def test_regions_seeded_and_ordered(client, admin_headers):
    r = client.get("/regions", headers=admin_headers)
    assert r.status_code == 200
    keys = [x["key"] for x in r.json()]
    assert keys[:3] == ["bordelais", "sud-ouest", "languedoc-roussillon"]
    assert len(keys) == 10 and "champagne" in keys
    bordeaux = r.json()[0]
    assert "Pauillac" in bordeaux["appellations"]
    assert bordeaux["intro"] == "" and bordeaux["image_url"] == ""


def test_update_region_requires_admin(client):
    assert client.put("/regions/alsace", json={"intro": "x"}).status_code == 401


def test_update_region(client, admin_headers):
    r = client.put("/regions/alsace", headers=admin_headers, json={
        "intro": "Bande étroite entre Vosges et Rhin.",
        "appellations": ["Alsace Grand Cru", " Riesling ", ""],
        "image_url": "/api/images/abc.png",
    })
    assert r.status_code == 200
    d = r.json()
    assert d["intro"].startswith("Bande")
    assert d["appellations"] == ["Alsace Grand Cru", "Riesling"]
    assert d["image_url"] == "/api/images/abc.png"
    again = [x for x in client.get("/regions", headers=admin_headers).json() if x["key"] == "alsace"][0]
    assert again["image_url"] == "/api/images/abc.png"


def test_update_region_rejects_foreign_image_url(client, admin_headers):
    r = client.put("/regions/alsace", headers=admin_headers, json={"image_url": "https://evil.example/x.png"})
    assert r.status_code == 422


def test_update_unknown_region(client, admin_headers):
    assert client.put("/regions/atlantis", headers=admin_headers, json={"intro": "x"}).status_code == 404
