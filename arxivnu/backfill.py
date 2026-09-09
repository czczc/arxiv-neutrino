#!/usr/bin/env python3
"""Backfill papers for a range of missing dates."""

import argparse
import subprocess
import sys
from datetime import date, timedelta

from arxivnu.db import get_conn, init_db


def date_range(start: str, end: str) -> list[str]:
    d = date.fromisoformat(start)
    end_d = date.fromisoformat(end)
    dates = []
    while d <= end_d:
        dates.append(d.isoformat())
        d += timedelta(days=1)
    return dates


def already_fetched(d: str) -> bool:
    with get_conn() as conn:
        return bool(conn.execute(
            "SELECT 1 FROM fetched_dates WHERE date = ?", (d,)
        ).fetchone())


def main():
    parser = argparse.ArgumentParser(description="Backfill ArXiv papers for missing dates")
    parser.add_argument("--from", dest="from_date", required=True, metavar="YYYY-MM-DD")
    parser.add_argument("--to", dest="to_date", required=True, metavar="YYYY-MM-DD")
    parser.add_argument("--force", action="store_true", help="Re-fetch even if already in DB")
    args = parser.parse_args()

    init_db()

    dates = date_range(args.from_date, args.to_date)
    print(f"Checking {len(dates)} date(s): {args.from_date} to {args.to_date}\n")

    skipped = []
    to_fetch = []
    for d in dates:
        if not args.force and already_fetched(d):
            skipped.append(d)
        else:
            to_fetch.append(d)

    if skipped:
        print(f"Already fetched ({len(skipped)}): {', '.join(skipped)}")
    if not to_fetch:
        print("Nothing to fetch.")
        return

    print(f"Fetching {len(to_fetch)} date(s): {', '.join(to_fetch)}\n")

    failed = []
    for d in to_fetch:
        print(f"── {d} ──")
        result = subprocess.run(
            ["uv", "run", "arxiv-fetch", "--date", d],
            capture_output=False,
        )
        if result.returncode != 0:
            print(f"  FAILED for {d}", file=sys.stderr)
            failed.append(d)
        print()

    if failed:
        print(f"\nFailed dates: {', '.join(failed)}", file=sys.stderr)
        print("Re-run with the same range to retry failed dates.")
        sys.exit(1)

    print(f"Backfill complete. Run: claude -p \"/arxiv-summarize\" && uv run arxiv-apply")


if __name__ == "__main__":
    main()
