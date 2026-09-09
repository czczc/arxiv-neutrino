def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_list_hides_dropped_and_omits_abstract(client):
    body = client.get("/api/papers").json()
    ids = [p["arxiv_id"] for p in body["papers"]]
    assert ids == ["2609.00002", "2609.00001", "2609.00003"] or set(ids) == {"2609.00001", "2609.00002", "2609.00003"}
    assert "2609.00004" not in ids
    assert "abstract" not in body["papers"][0]
    assert body["papers"][0]["tags"]
    assert body["next_before"] is None


def test_pagination_never_splits_a_day(client):
    page1 = client.get("/api/papers?limit=1").json()
    assert {p["submitted_date"] for p in page1["papers"]} == {"2026-09-09"}
    assert len(page1["papers"]) == 2
    assert page1["next_before"] == "2026-09-09"
    page2 = client.get("/api/papers?limit=1&before=2026-09-09").json()
    assert [p["arxiv_id"] for p in page2["papers"]] == ["2609.00003"]
    assert page2["next_before"] is None


def test_tag_filter_is_and(client):
    both = client.get("/api/papers?tags=experiment,accelerator").json()["papers"]
    assert [p["arxiv_id"] for p in both] == ["2609.00001"]
    exp = client.get("/api/papers?tags=experiment").json()["papers"]
    assert len(exp) == 2


def test_collab_query_ids_date(client):
    assert len(client.get("/api/papers?collab=NOvA").json()["papers"]) == 1
    assert len(client.get("/api/papers?q=earth").json()["papers"]) == 1
    assert len(client.get("/api/papers?ids=2609.00001,2609.00003").json()["papers"]) == 2
    assert len(client.get("/api/papers?date=2026-09-07").json()["papers"]) == 1


def test_detail_has_abstract_and_404(client):
    p = client.get("/api/papers/2609.00001").json()
    assert p["abstract"] == "abs1" and p["authors"] == ["A. One", "B. Two"]
    assert client.get("/api/papers/nope").status_code == 404


def test_facets_and_dates(client):
    f = client.get("/api/facets").json()
    assert f["total"] == 3
    assert f["tags"][0] == {"tag": "experiment", "count": 2}
    assert f["collaborations"] == [{"collaboration": "NOvA", "count": 1}]
    assert client.get("/api/dates").json() == [
        {"date": "2026-09-09", "count": 2}, {"date": "2026-09-07", "count": 1}]


def test_detail_strips_rss_prefix(client):
    from arxivnu.db import get_conn
    with get_conn() as conn:
        conn.execute("UPDATE papers SET abstract = 'arXiv:2609.00002v1 Announce Type: new Abstract: Real text.' WHERE arxiv_id = '2609.00002'")
    assert client.get("/api/papers/2609.00002").json()["abstract"] == "Real text."
