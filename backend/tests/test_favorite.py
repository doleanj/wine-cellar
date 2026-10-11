import io
import json


def _create(client, admin_headers, **extra):
    return client.post("/wines", json={"name": "Fav Wine", "producer": "P", "quantity": 1, **extra}, headers=admin_headers)


def test_favorite_defaults_to_false(client, admin_headers):
    d = _create(client, admin_headers, name="Not Fav").json()
    assert d["favorite"] is False


def test_toggle_favorite(client, admin_headers):
    wid = _create(client, admin_headers, name="Toggle Wine").json()["id"]
    r = client.put(f"/wines/{wid}", json={"favorite": True}, headers=admin_headers)
    assert r.status_code == 200 and r.json()["favorite"] is True
    r = client.put(f"/wines/{wid}", json={"favorite": False}, headers=admin_headers)
    assert r.json()["favorite"] is False


def test_toggle_requires_admin(client, admin_headers):
    wid = _create(client, admin_headers, name="Locked Wine").json()["id"]
    assert client.put(f"/wines/{wid}", json={"favorite": True}).status_code == 401


def test_filter_by_favorite(client, admin_headers):
    fav = _create(client, admin_headers, name="Filter Fav", favorite=True).json()["id"]
    other = _create(client, admin_headers, name="Filter Other").json()["id"]
    favs = [w["id"] for w in client.get("/wines?favorite=true").json()]
    assert fav in favs and other not in favs
    nonfavs = [w["id"] for w in client.get("/wines?favorite=false").json()]
    assert other in nonfavs and fav not in nonfavs
    assert {fav, other} <= {w["id"] for w in client.get("/wines").json()}


def test_favorite_export_and_import(client, admin_headers):
    _create(client, admin_headers, name="Export Fav", favorite=True)
    rows = client.get("/export/json", headers=admin_headers).json()
    assert next(w for w in rows if w["name"] == "Export Fav")["favorite"] is True
    payload = [{"name": "Imported Fav", "producer": "P", "favorite": "true"}]
    r = client.post("/import", files={"file": ("w.json", io.BytesIO(json.dumps(payload).encode()), "application/json")},
                    headers=admin_headers)
    assert r.json()["created"] == 1
    rows = client.get("/export/json", headers=admin_headers).json()
    assert next(w for w in rows if w["name"] == "Imported Fav")["favorite"] is True
