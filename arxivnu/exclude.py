#!/usr/bin/env python3
"""Exclude papers permanently (curation; runs on the server, not in the UI)."""

import argparse

from arxivnu.db import get_conn


def main() -> None:
    parser = argparse.ArgumentParser(description="Hide papers and block them from re-fetch")
    parser.add_argument("arxiv_ids", nargs="+", metavar="ARXIV_ID")
    parser.add_argument("--undo", action="store_true", help="Restore instead of exclude")
    args = parser.parse_args()

    with get_conn() as conn:
        for arxiv_id in args.arxiv_ids:
            if args.undo:
                conn.execute("UPDATE papers SET kept = 1 WHERE arxiv_id = ?", (arxiv_id,))
                conn.execute("DELETE FROM excluded_papers WHERE arxiv_id = ?", (arxiv_id,))
                print(f"restored {arxiv_id}")
            else:
                conn.execute("UPDATE papers SET kept = 0 WHERE arxiv_id = ?", (arxiv_id,))
                conn.execute("INSERT OR IGNORE INTO excluded_papers (arxiv_id) VALUES (?)", (arxiv_id,))
                print(f"excluded {arxiv_id}")


if __name__ == "__main__":
    main()
