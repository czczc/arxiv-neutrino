#!/usr/bin/env python3
"""One-off repair: apply normalize_collaboration() to every stored paper.

Run wherever the live database is (ARXIV_DB honoured). Prints each change;
pass --dry-run to only print.
"""

import sys

from arxivnu.db import DB_PATH, get_conn
from arxivnu.utils import normalize_collaboration


def main() -> None:
    dry = "--dry-run" in sys.argv
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT arxiv_id, title, collaboration FROM papers WHERE collaboration != ''"
        ).fetchall()
        changed = 0
        for r in rows:
            new = normalize_collaboration(r["collaboration"], r["title"])
            if new != r["collaboration"]:
                changed += 1
                print(f"{r['arxiv_id']}: {r['collaboration']!r} -> {new!r}")
                if not dry:
                    conn.execute("UPDATE papers SET collaboration = ? WHERE arxiv_id = ?", (new, r["arxiv_id"]))
    print(f"{'would change' if dry else 'changed'} {changed} of {len(rows)} rows in {DB_PATH}")


if __name__ == "__main__":
    main()
