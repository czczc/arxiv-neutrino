#!/usr/bin/env python3
"""Read results.json and write summaries + tags into the DB."""

import json
import sys
from pathlib import Path

from arxivnu.db import WORK_DIR, get_conn

RESULTS_PATH = WORK_DIR / "results.json"


def main():
    if not RESULTS_PATH.exists():
        print("results.json not found. Run: claude -p \"/arxiv-summarize\" first.", file=sys.stderr)
        sys.exit(1)

    results = json.loads(RESULTS_PATH.read_text())
    if not isinstance(results, list):
        print("results.json must be a JSON array.", file=sys.stderr)
        sys.exit(1)
    if not results:
        print("Nothing to apply.")
        RESULTS_PATH.unlink()
        sys.exit(0)

    kept = 0
    dropped = 0
    tagged = 0

    with get_conn() as conn:
        for item in results:
            arxiv_id = item.get("arxiv_id")
            if not arxiv_id:
                continue

            keep = bool(item.get("keep", True))
            summary = item.get("summary", "").strip()
            tags = [t.strip() for t in item.get("tags", []) if t.strip()]

            conn.execute(
                "UPDATE papers SET summary = ?, kept = ? WHERE arxiv_id = ?",
                (summary, 1 if keep else 0, arxiv_id),
            )

            if keep:
                kept += 1
                for tag in tags:
                    conn.execute(
                        "INSERT OR IGNORE INTO paper_tags (arxiv_id, tag) VALUES (?, ?)",
                        (arxiv_id, tag),
                    )
                    tagged += 1
            else:
                dropped += 1

    print(f"Applied results: {kept} kept, {dropped} dropped, {tagged} tags written.")

    # Archive results.json so it's not accidentally re-applied
    archive_path = RESULTS_PATH.with_suffix(".applied.json")
    RESULTS_PATH.rename(archive_path)
    print(f"results.json archived to {archive_path.name}")


if __name__ == "__main__":
    main()
