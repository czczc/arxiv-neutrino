import os
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    db = tmp_path_factory.mktemp("db") / "test.db"
    os.environ["ARXIV_DB"] = str(db)
    # arxivnu.db reads the env at import time, so import only after setting it.
    for mod in [m for m in sys.modules if m.startswith("arxivnu")]:
        del sys.modules[mod]
    from fastapi.testclient import TestClient

    from arxivnu.api import app
    from arxivnu.db import get_conn, init_db

    init_db()
    with get_conn() as conn:
        conn.executemany(
            """INSERT INTO papers (arxiv_id, title, authors, abstract, submitted_date, summary,
                                   kept, collaboration) VALUES (?,?,?,?,?,?,?,?)""",
            [
                ("2609.00001", "Neutron modeling in NOvA", '["A. One", "B. Two"]', "abs1", "2026-09-09", "sum1", 1, "NOvA"),
                ("2609.00002", "Sterile search", '["C. Three"]', "abs2", "2026-09-09", "sum2", 1, ""),
                ("2609.00003", "Earth interior", '["D. Four"]', "abs3", "2026-09-07", "sum3", 1, ""),
                ("2609.00004", "Dropped paper", '["E. Five"]', "abs4", "2026-09-07", "", 0, ""),
            ],
        )
        conn.executemany(
            "INSERT INTO paper_tags (arxiv_id, tag) VALUES (?,?)",
            [
                ("2609.00001", "accelerator"), ("2609.00001", "experiment"),
                ("2609.00002", "sterile-neutrino"), ("2609.00002", "experiment"),
                ("2609.00003", "theory"),
            ],
        )
    with TestClient(app) as c:
        yield c
