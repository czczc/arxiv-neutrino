#!/usr/bin/env python3
"""Fetch new ArXiv papers and store raw records to DB, writing pending.json for LLM step."""

import argparse
import json
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path

import feedparser
import httpx

from arxivnu.db import WORK_DIR, get_conn, init_db
from arxivnu.utils import pick_collaboration, split_author_string

RSS_FEEDS = {
    "hep-ex": "https://rss.arxiv.org/rss/hep-ex",
    "nucl-ex": "https://rss.arxiv.org/rss/nucl-ex",
    "physics.ins-det": "https://rss.arxiv.org/rss/physics.ins-det",
    "physics.data-an": "https://rss.arxiv.org/rss/physics.data-an",
}

ARXIV_API_URL = "https://export.arxiv.org/api/query"
INSPIREHEP_API = "https://inspirehep.net/api/literature"

ARXIV_ID_RE = re.compile(r"(\d{4}\.\d{4,5}(?:v\d+)?)")

# Neutrino keyword pre-filter (title + abstract)
NEUTRINO_KEYWORDS = [
    "neutrino", "antineutrino", r"\bnu_", r"\bnu\b",
    "oscillat", "mass ordering", "mass hierarchy",
    "sterile neutrino", "majorana", "dirac mass",
    "double beta", "neutrinoless",
    "dune", "super-k", "superkamiokande", "icecube", "t2k", "nova",
    "microbooNE", "microboone", "miniboone",
    "sno", "kamland", "juno", "reactor antineutrino", "reactor neutrino",
    "solar neutrino", "atmospheric neutrino", "supernova neutrino",
    "liquid argon tpc", "lartpc", "water cherenkov",
    "numi", "bnb", "nue", "numu", "nutau",
]
NEUTRINO_RE_CERTAIN = re.compile(
    "|".join(NEUTRINO_KEYWORDS), re.IGNORECASE
)
# Weaker signal — needs more context; these go into ambiguous bucket
NEUTRINO_RE_WEAK = re.compile(
    r"\b(detector|scintillator|photomultiplier|pmt|sipm|dark matter)\b",
    re.IGNORECASE,
)

# Collider experiments with no neutrino physics relevance — drop regardless of abstract
EXCLUDED_COLLABORATIONS = {
    "ATLAS", "CMS", "LHCb", "ALICE",
    "BESIII", "Belle", "Belle II", "BaBar", "CLEO",
    "CDF", "D0", "NA61/SHINE", "COMPASS", "NA62",
}

# Proceedings heuristic on ArXiv comment field
PROCEEDINGS_RE = re.compile(
    r"(proceedings|talk\s+given|contribution\s+to|PoS\s*\(|conference\s+paper"
    r"|submitted\s+to\s+.*\s+proceedings|ICHEP|NuFact|TAUP|WIN\s+\d)",
    re.IGNORECASE,
)


def extract_arxiv_id(text: str) -> str | None:
    m = ARXIV_ID_RE.search(text)
    if m:
        return re.sub(r"v\d+$", "", m.group(1))
    return None


def parse_authors(entry) -> list[str]:
    if hasattr(entry, "authors"):
        names = [a.get("name", "") for a in entry.authors]
        if len(names) == 1 and ', ' in names[0]:
            return split_author_string(names[0])
        return names
    if hasattr(entry, "author"):
        s = entry.author
        if ', ' in s:
            return split_author_string(s)
        return [s]
    return []


def classify_relevance(title: str, abstract: str) -> str:
    """Return 'certain', 'ambiguous', or 'skip'."""
    text = f"{title} {abstract}"
    if NEUTRINO_RE_CERTAIN.search(text):
        return "certain"
    if NEUTRINO_RE_WEAK.search(text):
        return "ambiguous"
    return "skip"


def is_proceedings(comment: str) -> bool:
    return bool(comment and PROCEEDINGS_RE.search(comment))


def fetch_rss(url: str) -> list[dict]:
    feed = feedparser.parse(url)
    # feedparser does NOT raise on a connection failure — it returns an empty
    # feed with bozo set. Surface that as an error so it isn't mistaken for a
    # legitimately empty (e.g. weekend) feed.
    if feed.bozo and not feed.entries:
        raise RuntimeError(f"feed fetch/parse failed: {feed.bozo_exception!r}")
    papers = []
    for entry in feed.entries:
        arxiv_id = extract_arxiv_id(getattr(entry, "id", "") or getattr(entry, "link", ""))
        if not arxiv_id:
            continue
        papers.append({
            "arxiv_id": arxiv_id,
            "title": entry.get("title", "").replace("\n", " ").strip(),
            "authors": parse_authors(entry),
            "abstract": entry.get("summary", "").strip(),
            "comment": entry.get("arxiv_comment", "") or "",
        })
    return papers


def fetch_arxiv_api(fetch_date: str, categories: list[str]) -> list[dict]:
    """Fetch papers for a specific date using the ArXiv API."""
    d = datetime.strptime(fetch_date, "%Y-%m-%d")
    date_str = d.strftime("%Y%m%d")
    query = " OR ".join(f"cat:{c}" for c in categories)
    # ArXiv API date range for submitted date
    search = f"({query}) AND submittedDate:[{date_str}0000 TO {date_str}2359]"
    params = {
        "search_query": search,
        "start": 0,
        "max_results": 200,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    papers = []
    with httpx.Client(timeout=30) as client:
        resp = client.get(ARXIV_API_URL, params=params)
        resp.raise_for_status()
    feed = feedparser.parse(resp.text)
    for entry in feed.entries:
        arxiv_id = extract_arxiv_id(getattr(entry, "id", "") or getattr(entry, "link", ""))
        if not arxiv_id:
            continue
        papers.append({
            "arxiv_id": arxiv_id,
            "title": entry.get("title", "").replace("\n", " ").strip(),
            "authors": parse_authors(entry),
            "abstract": entry.get("summary", "").strip(),
            "comment": entry.get("arxiv_comment", "") or "",
        })
    return papers


def fetch_inspirehep(arxiv_id: str, title: str = "") -> dict | None:
    """Fetch metadata from InspireHEP for a single arxiv ID."""
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(INSPIREHEP_API, params={"q": f"arxiv:{arxiv_id}", "fields": "arxiv_eprints,document_type,collaborations,journal_title,publication_info"})
            resp.raise_for_status()
        hits = resp.json().get("hits", {}).get("hits", [])
        if not hits:
            return None
        rec = hits[0]
        meta = rec.get("metadata", {})
        collab = pick_collaboration(meta.get("collaborations", []), title)
        doc_types = meta.get("document_type", [])
        doc_type = doc_types[0] if doc_types else ""
        pub_info = meta.get("publication_info", [{}])
        journal = pub_info[0].get("journal_title", "") if pub_info else ""
        return {
            "inspire_id": str(rec.get("id", "")),
            "collaboration": collab,
            "document_type": doc_type,
            "journal_ref": journal,
        }
    except Exception as e:
        print(f"  InspireHEP error for {arxiv_id}: {e}", file=sys.stderr)
        return None


def store_paper(conn, paper: dict, fetch_date: str) -> bool:
    """Insert paper if not already present and not excluded. Returns True if new."""
    excluded = conn.execute(
        "SELECT 1 FROM excluded_papers WHERE arxiv_id = ?", (paper["arxiv_id"],)
    ).fetchone()
    if excluded:
        return False
    existing = conn.execute(
        "SELECT arxiv_id FROM papers WHERE arxiv_id = ?", (paper["arxiv_id"],)
    ).fetchone()
    if existing:
        return False
    conn.execute(
        """INSERT INTO papers
           (arxiv_id, title, authors, abstract, fetched_date, submitted_date,
            collaboration, document_type, journal_ref, inspire_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            paper["arxiv_id"], paper["title"],
            json.dumps(paper.get("authors", [])),
            paper.get("abstract", ""),
            fetch_date, fetch_date,
            paper.get("collaboration", ""),
            paper.get("document_type", ""),
            paper.get("journal_ref", ""),
            paper.get("inspire_id", ""),
        ),
    )
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat(),
                        help="Date to fetch (YYYY-MM-DD), defaults to today")
    args = parser.parse_args()
    fetch_date = args.date

    init_db()

    # Check if already fetched
    with get_conn() as conn:
        already = conn.execute(
            "SELECT date FROM fetched_dates WHERE date = ?", (fetch_date,)
        ).fetchone()
    if already:
        print(f"Already fetched {fetch_date}. Nothing to do.")
        pending_path = WORK_DIR / "pending.json"
        pending_path.write_text(json.dumps({"fetch_date": fetch_date, "certain": [], "ambiguous": []}))
        sys.exit(0)

    # Collect raw papers
    raw: list[dict] = []
    today = date.today().isoformat()
    if fetch_date == today:
        feed_errors = 0
        for category, url in RSS_FEEDS.items():
            print(f"  RSS {category}...", end=" ", flush=True)
            try:
                papers = fetch_rss(url)
                print(f"{len(papers)} entries")
                raw.extend(papers)
            except Exception as e:
                print(f"ERROR: {e}", file=sys.stderr)
                feed_errors += 1
        if feed_errors == len(RSS_FEEDS):
            # All feeds failed — almost certainly no network (e.g. laptop just
            # woke). Do NOT mark this date as fetched, so a later run today can
            # still pick up the papers. Exit non-zero so it shows up as a failure.
            print("All RSS feeds failed (likely no network); not marking date "
                  "fetched. Will retry on next run.", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"  ArXiv API for {fetch_date}...", end=" ", flush=True)
        papers = fetch_arxiv_api(fetch_date, list(RSS_FEEDS.keys()))
        print(f"{len(papers)} entries")
        raw.extend(papers)

    # Deduplicate by arxiv_id
    seen: set[str] = set()
    unique: list[dict] = []
    for p in raw:
        if p["arxiv_id"] not in seen:
            seen.add(p["arxiv_id"])
            unique.append(p)
    print(f"\n{len(unique)} unique papers after dedup")

    # Filter pipeline
    certain: list[dict] = []
    ambiguous: list[dict] = []
    skipped_keyword = 0
    skipped_proceedings = 0

    for p in unique:
        if is_proceedings(p["comment"]):
            skipped_proceedings += 1
            continue
        relevance = classify_relevance(p["title"], p["abstract"])
        if relevance == "skip":
            skipped_keyword += 1
            continue
        if relevance == "certain":
            certain.append(p)
        else:
            ambiguous.append(p)

    print(f"Skipped {skipped_keyword} (keyword/collider), {skipped_proceedings} (proceedings)")
    print(f"Certain: {len(certain)}, Ambiguous: {len(ambiguous)}")

    # InspireHEP enrichment for survivors
    survivors = certain + ambiguous
    print(f"\nFetching InspireHEP for {len(survivors)} papers...")
    enriched: list[dict] = []
    for i, p in enumerate(survivors):
        print(f"  [{i+1}/{len(survivors)}] {p['arxiv_id']}...", end=" ", flush=True)
        inspire = fetch_inspirehep(p["arxiv_id"], p["title"])
        time.sleep(0.3)  # be polite to InspireHEP
        if inspire:
            p.update(inspire)
            # Drop conference papers/proceedings
            if inspire["document_type"] in ("proceedings", "conference paper"):
                print(f"dropped (InspireHEP: {inspire['document_type']})")
                skipped_proceedings += 1
                continue
            # Drop known collider experiments unrelated to neutrino physics
            if inspire["collaboration"] in EXCLUDED_COLLABORATIONS:
                print(f"dropped (collider experiment: {inspire['collaboration']})")
                skipped_keyword += 1
                continue
            print(f"ok ({inspire['document_type'] or 'unknown type'}, collab={inspire['collaboration'] or 'none'})")
        else:
            print("no InspireHEP record")
        enriched.append(p)

    # Store to DB
    print(f"\nStoring {len(enriched)} papers...")
    new_count = 0
    with get_conn() as conn:
        for p in enriched:
            if store_paper(conn, p, fetch_date):
                new_count += 1
        conn.execute(
            "INSERT OR REPLACE INTO fetched_dates (date) VALUES (?)", (fetch_date,)
        )

    print(f"{new_count} new papers stored ({len(enriched) - new_count} already existed)")

    # Write pending.json for LLM step — re-split after InspireHEP filtering
    enriched_ids = {p["arxiv_id"] for p in enriched}
    final_certain = [p for p in certain if p["arxiv_id"] in enriched_ids]
    final_ambiguous = [p for p in ambiguous if p["arxiv_id"] in enriched_ids]

    pending = {
        "fetch_date": fetch_date,
        "certain": [
            {"arxiv_id": p["arxiv_id"], "title": p["title"],
             "abstract": p["abstract"], "collaboration": p.get("collaboration", "")}
            for p in final_certain
        ],
        "ambiguous": [
            {"arxiv_id": p["arxiv_id"], "title": p["title"],
             "abstract": p["abstract"], "collaboration": p.get("collaboration", "")}
            for p in final_ambiguous
        ],
    }

    pending_path = WORK_DIR / "pending.json"
    pending_path.write_text(json.dumps(pending, indent=2))
    print(f"\npending.json written: {len(final_certain)} certain, {len(final_ambiguous)} ambiguous")
    print("\nNext step: claude -p \"/arxiv-summarize\" && uv run arxiv-apply")


if __name__ == "__main__":
    main()
