from datetime import datetime


def _create(client, headers, **kw):
    body = {"name": "Drunk Wine", "quantity": 3, **kw}
    return client.post("/wines", json=body, headers=headers).json()["id"]


def _today():
    return datetime.utcnow().strftime("%Y-%m-%d")


def test_default_is_empty(client, admin_headers):
    wid = _create(client, admin_headers)
    assert client.get(f"/wines/{wid}", headers=admin_headers).json()["last_drunk"] == ""


def test_stock_going_down_sets_last_drunk(client, admin_headers):
    wid = _create(client, admin_headers)
    d = client.put(f"/wines/{wid}", json={"quantity": 2}, headers=admin_headers).json()
    assert d["last_drunk"] == _today()


def test_stock_going_up_or_other_edit_keeps_it(client, admin_headers):
    wid = _create(client, admin_headers)
    client.put(f"/wines/{wid}", json={"last_drunk": "2026-01-02"}, headers=admin_headers)
    client.put(f"/wines/{wid}", json={"quantity": 5, "notes": "x"}, headers=admin_headers)
    assert client.get(f"/wines/{wid}", headers=admin_headers).json()["last_drunk"] == "2026-01-02"


def test_explicit_date_wins_over_decrement(client, admin_headers):
    wid = _create(client, admin_headers)
    d = client.put(f"/wines/{wid}", json={"quantity": 1, "last_drunk": "2026-03-04"}, headers=admin_headers).json()
    assert d["last_drunk"] == "2026-03-04"


def test_bad_date_rejected(client, admin_headers):
    wid = _create(client, admin_headers)
    assert client.put(f"/wines/{wid}", json={"last_drunk": "yesterday"}, headers=admin_headers).status_code == 422


def test_include_past_lists_empty_wines_for_logged_in_only(client, admin_headers):
    wid = _create(client, admin_headers, quantity=1)
    client.put(f"/wines/{wid}", json={"quantity": 0}, headers=admin_headers)
    assert wid not in {w["id"] for w in client.get("/wines", headers=admin_headers).json()}
    past = {w["id"]: w for w in client.get("/wines?include_past=true", headers=admin_headers).json()}
    assert past[wid]["last_drunk"] == _today()
