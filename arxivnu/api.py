"""Read-only JSON API + SPA host.

Visitors never write to the database: stars and read marks live in the
browser (localStorage). Curation (exclude) is a CLI on the server.
"""

import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from arxivnu.db import ROOT, get_conn, init_db
from arxivnu.utils import normalize_authors



@asynccontextmanager
async def _lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="ArXiv Neutrino", docs_url=None, redoc_url=None, lifespan=_lifespan)

MAX_AUTHORS_IN_LIST = 6
# RSS abstracts arrive as "arXiv:2609.06956v1 Announce Type: new Abstract: ..."
_RSS_PREFIX = re.compile(r"^arXiv:\S+\s+Announce Type:\s*\S+\s+Abstract:\s*", re.IGNORECASE)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def _split_csv(value: str | None) -> list[str]:
    return [v for v in (value or "").split(",") if v]


def _row_to_paper(row, *, full: bool) -> dict:
    p = dict(row)
    p["tags"] = [t for t in (p.pop("tags_csv") or "").split(",") if t]
    authors = normalize_authors(p["authors"] or "[]")
    p["author_count"] = len(authors)
    p["authors"] = authors if full else authors[:MAX_AUTHORS_IN_LIST]
    for k in ("kept", "read_at", "starred", "rating", "fetched_date", "inspire_id", "created_at"):
        p.pop(k, None)
    if full:
        p["abstract"] = _RSS_PREFIX.sub("", p.get("abstract") or "")
    else:
        p.pop("abstract", None)
    return p


_SELECT = """
    SELECT p.*, GROUP_CONCAT(pt.tag, ',') AS tags_csv
    FROM papers p
    LEFT JOIN paper_tags pt ON pt.arxiv_id = p.arxiv_id
    WHERE p.kept = 1 {where}
    GROUP BY p.arxiv_id
    {having}
    ORDER BY p.submitted_date DESC, p.created_at DESC, p.arxiv_id DESC
"""


@app.get("/api/papers")
def list_papers(
    tags: str | None = None,
    collab: str | None = None,
    q: str | None = None,
    ids: str | None = None,
    date: str | None = None,
    before: str | None = Query(None, description="Only days strictly before this YYYY-MM-DD"),
    limit: int = Query(100, ge=1, le=1000),
) -> dict:
    """Papers newest first, paginated by whole days.

    Days are never split across pages: the response includes every paper of
    each day it touches, stopping once at least `limit` papers are
    collected. `next_before` is the last day included (pass it back as
    `before` to continue) or null when exhausted.
    """
    where, having, params = [], [], []
    if collab:
        where.append("p.collaboration = ?")
        params.append(collab)
    if q:
        like = f"%{q}%"
        where.append("(p.title LIKE ? OR p.authors LIKE ? OR p.summary LIKE ? OR p.arxiv_id LIKE ?)")
        params += [like, like, like, like]
    if ids:
        id_list = _split_csv(ids)
        where.append(f"p.arxiv_id IN ({','.join('?' * len(id_list))})")
        params += id_list
    if date:
        where.append("p.submitted_date = ?")
        params.append(date)
    if before:
        where.append("p.submitted_date < ?")
        params.append(before)
    tag_list = _split_csv(tags)
    for t in tag_list:
        # AND across tags: each requested tag must appear in the aggregate
        having.append("SUM(pt.tag = ?) > 0")
        params.append(t)

    sql = _SELECT.format(
        where=("AND " + " AND ".join(where)) if where else "",
        having=("HAVING " + " AND ".join(having)) if having else "",
    )
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()

    papers, next_before = [], None
    if ids:
        # Explicit id lookups (the Starred view) are not paginated.
        papers = [_row_to_paper(r, full=False) for r in rows]
    else:
        current_day = None
        for r in rows:
            day = r["submitted_date"]
            if len(papers) >= limit and day != current_day:
                next_before = current_day
                break
            current_day = day
            papers.append(_row_to_paper(r, full=False))
    return {"papers": papers, "next_before": next_before}


@app.get("/api/papers/{arxiv_id}")
def get_paper(arxiv_id: str) -> dict:
    sql = _SELECT.format(where="AND p.arxiv_id = ?", having="")
    with get_conn() as conn:
        row = conn.execute(sql, (arxiv_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return _row_to_paper(row, full=True)


@app.get("/api/facets")
def facets() -> dict:
    with get_conn() as conn:
        tags = conn.execute("""
            SELECT pt.tag, COUNT(*) AS count
            FROM paper_tags pt JOIN papers p ON p.arxiv_id = pt.arxiv_id
            WHERE p.kept = 1
            GROUP BY pt.tag ORDER BY count DESC, pt.tag
        """).fetchall()
        collabs = conn.execute("""
            SELECT collaboration, COUNT(*) AS count
            FROM papers WHERE kept = 1 AND collaboration != ''
            GROUP BY collaboration ORDER BY count DESC, collaboration
        """).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM papers WHERE kept = 1").fetchone()[0]
    return {
        "tags": [dict(r) for r in tags],
        "collaborations": [dict(r) for r in collabs],
        "total": total,
    }


@app.get("/api/dates")
def dates() -> list[dict]:
    """Every day with kept papers and its count, newest first (archive nav)."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT submitted_date AS date, COUNT(*) AS count
            FROM papers WHERE kept = 1 AND submitted_date IS NOT NULL
            GROUP BY submitted_date ORDER BY submitted_date DESC
        """).fetchall()
    return [dict(r) for r in rows]


# --- SPA bundle -----------------------------------------------------------
# Same shape as dunecat's hub: mount known asset dirs explicitly so an unknown
# /api/* path still 404s as JSON, then a catch-all serves index.html for
# history-mode routes.
_SPA_DIR = ROOT / "frontend" / "dist"
_SPA_INDEX = _SPA_DIR / "index.html"

if (_SPA_DIR / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=_SPA_DIR / "assets"), name="spa-assets")

if _SPA_INDEX.exists():

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str) -> FileResponse:
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
        candidate = _SPA_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_SPA_INDEX)
