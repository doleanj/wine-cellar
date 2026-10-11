import io
import json

BASE = {"name": "Chinon Test", "producer": "Domaine X", "vintage": 2020}


def _create(client, admin_headers, **extra):
    return client.post("/wines", json={**BASE, **extra}, headers=admin_headers)


def test_defaults_for_new_fields(client, admin_headers):
    r = _create(client, admin_headers, name="Defaults Wine")
    assert r.status_code == 200
    d = r.json()
    assert d["url"] == ""
    assert d["profile_fruit"] is None
    assert d["profile_personality"] is None
    assert d["sweetness"] == ""


def test_create_with_profile_url_and_pairings(client, admin_headers):
    r = _create(
        client, admin_headers, name="Full Wine",
        url="https://example.org/wine", profile_fruit=4, profile_personality=2,
        sweetness="sec", pairings="viande-rouge,fromage-pate-dure",
    )
    assert r.status_code == 200
    d = r.json()
    assert d["url"] == "https://example.org/wine"
    assert (d["profile_fruit"], d["profile_personality"]) == (4, 2)
    assert d["sweetness"] == "sec"
    assert d["pairings"] == "viande-rouge,fromage-pate-dure"


def test_update_new_fields(client, admin_headers):
    wid = _create(client, admin_headers, name="Update Wine").json()["id"]
    r = client.put(f"/wines/{wid}", json={"profile_fruit": 5, "sweetness": "moelleux", "url": "http://a.b/c"},
                   headers=admin_headers)
    assert r.status_code == 200
    d = r.json()
    assert d["profile_fruit"] == 5 and d["sweetness"] == "moelleux" and d["url"] == "http://a.b/c"


def test_rejects_bad_url_score_and_sweetness(client, admin_headers):
    assert _create(client, admin_headers, name="Bad1", url="javascript:alert(1)").status_code == 422
    assert _create(client, admin_headers, name="Bad2", url="ftp://x.y/z").status_code == 422
    assert _create(client, admin_headers, name="Bad3", profile_fruit=0).status_code == 422
    assert _create(client, admin_headers, name="Bad4", profile_personality=6).status_code == 422
    assert _create(client, admin_headers, name="Bad5", sweetness="brut").status_code == 422


def test_json_export_import_roundtrip(client, admin_headers):
    _create(client, admin_headers, name="Roundtrip Wine", url="https://example.org/r",
            profile_fruit=3, profile_personality=4, sweetness="doux")
    exported = client.get("/export/json", headers=admin_headers).json()
    row = next(w for w in exported if w["name"] == "Roundtrip Wine")
    assert row["url"] == "https://example.org/r"
    assert row["profile_fruit"] == 3 and row["sweetness"] == "doux"


def test_import_sanitizes_unsafe_values(client, admin_headers):
    payload = [{"name": "Imported Evil", "producer": "P", "url": "javascript:alert(1)",
                "profile_fruit": 9, "profile_personality": 2, "sweetness": "brut"}]
    r = client.post("/import", files={"file": ("w.json", io.BytesIO(json.dumps(payload).encode()), "application/json")},
                    headers=admin_headers)
    assert r.status_code == 200 and r.json()["created"] == 1
    wines = client.get("/wines").json()
    w = next(w for w in wines if w["name"] == "Imported Evil") if any(w["name"] == "Imported Evil" for w in wines) else None
    lib = client.get("/export/json", headers=admin_headers).json()
    row = next(x for x in lib if x["name"] == "Imported Evil")
    assert row["url"] == "" and row["profile_fruit"] is None
    assert row["profile_personality"] == 2 and row["sweetness"] == ""
