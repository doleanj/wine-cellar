import io
import json


def _create(client, admin_headers, **extra):
    return client.post("/wines", json={"name": "Wish Wine", "producer": "P", "quantity": 1, **extra}, headers=admin_headers)


def test_wishlist_defaults(client, admin_headers):
    d = _create(client, admin_headers, name="Plain Wine").json()
    assert d["wishlist"] is False and d["target_price"] is None


def test_wished_wine_without_stock_only_listed_on_request(client, admin_headers):
    wid = _create(client, admin_headers, name="Wanted Wine", quantity=0, wishlist=True, target_price=12.5).json()["id"]
    assert wid not in {w["id"] for w in client.get("/wines").json()}
    listed = {w["id"]: w for w in client.get("/wines?include_wishlist=true").json()}
    assert listed[wid]["quantity"] == 0 and listed[wid]["target_price"] == 12.5
    assert client.get(f"/wines/{wid}").status_code == 200


def test_out_of_stock_wine_not_on_wishlist_stays_hidden(client, admin_headers):
    wid = _create(client, admin_headers, name="Finished Wine", quantity=0).json()["id"]
    assert wid not in {w["id"] for w in client.get("/wines?include_wishlist=true").json()}
    assert client.get(f"/wines/{wid}").status_code == 404


def test_wished_wine_not_counted_in_stats(client, admin_headers):
    before = client.get("/stats", headers=admin_headers).json()
    _create(client, admin_headers, name="Stats Wish", quantity=0, wishlist=True)
    after = client.get("/stats", headers=admin_headers).json()
    assert after["total_wines"] == before["total_wines"]
    assert after["total_bottles"] == before["total_bottles"]


def test_bought_moves_wine_into_stock(client, admin_headers):
    wid = _create(client, admin_headers, name="Bought Wine", quantity=0, wishlist=True).json()["id"]
    r = client.put(f"/wines/{wid}", json={"wishlist": False, "quantity": 3, "purchase_date": "2026-10-14"}, headers=admin_headers)
    assert r.status_code == 200
    d = r.json()
    assert d["wishlist"] is False and d["quantity"] == 3
    assert wid in {w["id"] for w in client.get("/wines").json()}


def test_negative_target_price_rejected(client, admin_headers):
    assert _create(client, admin_headers, name="Bad Target", wishlist=True, target_price=-1).status_code == 422


def test_wishlist_export_and_import(client, admin_headers):
    _create(client, admin_headers, name="Export Wish", quantity=0, wishlist=True, target_price=20)
    rows = client.get("/export/json", headers=admin_headers).json()
    row = next(w for w in rows if w["name"] == "Export Wish")
    assert row["wishlist"] is True and row["target_price"] == 20
    payload = [{"name": "Imported Wish", "producer": "P", "quantity": 0, "wishlist": "true", "target_price": "9.9"},
               {"name": "Imported Zero", "producer": "P", "quantity": 0}]
    r = client.post("/import", files={"file": ("w.json", io.BytesIO(json.dumps(payload).encode()), "application/json")},
                    headers=admin_headers)
    assert r.json()["created"] == 2
    rows = {w["name"]: w for w in client.get("/export/json", headers=admin_headers).json()}
    assert rows["Imported Wish"]["quantity"] == 0 and rows["Imported Wish"]["target_price"] == 9.9
    assert rows["Imported Zero"]["quantity"] == 1  # unchanged rule for non-wishlist rows
