#!/usr/bin/env python3
"""One-off: dump read/starred marks from a local arxiv.db into the JSON the
web app's Import button accepts (the localStorage `arxivnu:v1` shape)."""

import json
import sys
from datetime import datetime, timezone

from arxivnu.db import DB_PATH, get_conn


def main() -> None:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT arxiv_id, read_at, starred FROM papers WHERE read_at IS NOT NULL OR starred = 1"
        ).fetchall()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    state = {"version": 1, "stars": {}, "read": {}, "readBefore": None}
    for r in rows:
        if r["read_at"]:
            state["read"][r["arxiv_id"]] = r["read_at"].replace(" ", "T") + "Z"
        if r["starred"]:
            state["stars"][r["arxiv_id"]] = now
    json.dump(state, sys.stdout, indent=2)
    print(file=sys.stderr)
    print(f"from {DB_PATH}: {len(state['read'])} read, {len(state['stars'])} starred", file=sys.stderr)


if __name__ == "__main__":
    main()
