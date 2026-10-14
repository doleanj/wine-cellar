from pathlib import Path

import pytest

import leclerc

PAGE = (Path(__file__).parent / "fixtures" / "leclerc_sample.html").read_text(encoding="utf8")
URL = "https://www.e.leclerc/fp/cuvee-test-2023-exemple-aop-rouge-75-cl-1234567890123"


def test_canonical_url_strips_tracking_and_checks_host():
    assert leclerc.canonical_url(URL + "?et_keyword=x&utm_source=y#frag") == URL
    assert leclerc.canonical_url("https://e.leclerc/fp/abc-123") == "https://e.leclerc/fp/abc-123"


@pytest.mark.parametrize("u", [
    "http://www.e.leclerc/fp/abc", "https://evil.example.com/fp/abc", "https://www.e.leclerc.evil.com/fp/abc",
    "https://www.e.leclerc/recherche?q=x", "https://www.e.leclerc/fp/", "https://www.e.leclerc/cat/ma-cave", "",
])
def test_canonical_url_rejects(u):
    assert leclerc.canonical_url(u) == ""


def test_parse_sample_page():
    f = leclerc.parse(PAGE, URL)["fields"]
    assert f["name"] == "Cuvee Test"
    assert (f["vintage"], f["type"], f["grape"], f["country"]) == (2023, "red", "Cépage test", "France")
    assert f["region"] == "Testland, Exemple"
    assert (f["alcohol"], f["volume_ml"], f["sulphites"]) == (13.5, 750, True)
    assert f["pairings"] == "fromage,plats-en-sauce,viande-rouge"
    assert (f["profile_fruit"], f["profile_personality"]) == (3, 5)
    assert (f["keep_until_years"], f["serving_temp"]) == (7, 16)
    assert f["tasting"].splitlines()[:3] == ["Œil : Rouge test", "Nez : Nez de test.", "Bouche : Bouche de test."]
    assert (f["price"], f["barcode"], f["url"]) == (9.5, "1234567890123", URL)
    assert f["image_url"] == "https://media.example.test/img_1"


def test_parse_page_without_data_raises():
    with pytest.raises(leclerc.LeclercError):
        leclerc.parse("<html><body>nothing here</body></html>", URL)


def test_parse_sparse_page_does_not_crash():
    page = '<script type="application/ld+json">{"@type":"Product","name":"Only A Name"}</script>'
    f = leclerc.parse(page, URL)["fields"]
    assert f["name"] == "Only A Name" and f["vintage"] is None and f["pairings"] == "" and f["price"] is None


def test_endpoint_requires_login(client):
    assert client.post("/fill-from-url", json={"url": URL}).status_code == 401


def test_endpoint_rejects_other_urls(client, admin_headers):
    r = client.post("/fill-from-url", json={"url": "https://evil.example.com/fp/x"}, headers=admin_headers)
    assert r.status_code == 400


def test_endpoint_parses_and_wine_keeps_the_new_fields(client, admin_headers, monkeypatch):
    import httpx
    from tests.webmock import patch_web

    def handler(request):
        assert str(request.url) == URL  # tracking params were stripped before the request
        return httpx.Response(200, text=PAGE, headers={"content-type": "text/html; charset=utf-8"})

    patch_web(monkeypatch, handler)
    r = client.post("/fill-from-url", json={"url": URL + "?et_keyword=abc"}, headers=admin_headers)
    assert r.status_code == 200
    fields = r.json()["fields"]
    w = client.post("/wines", json={**fields, "purchase_date": "2026-10-12"}, headers=admin_headers)
    assert w.status_code in (200, 201), w.text
    d = w.json()
    assert (d["keep_until_years"], d["serving_temp"], d["purchase_date"]) == (7, 16, "2026-10-12")
    assert d["tasting"].startswith("Œil")
    bad = client.post("/wines", json={"name": "X", "purchase_date": "12/10/2026"}, headers=admin_headers)
    assert bad.status_code == 422


@pytest.mark.parametrize("region, appellation, expected", [
    ("Bordeaux", "Fronton", "Sud-Ouest"),                          # Leclerc files Fronton under Bordeaux
    ("Bordeaux", "Saint-Emilion Grand Cru", "Bordeaux"),           # same region: Leclerc wording kept
    ("Languedoc-Roussillon", "Pic-Saint-Loup", "Languedoc-Roussillon"),
    ("Sud-Ouest", "Gaillac", "Sud-Ouest"),
    ("Vallée du Rhône", "Crozes-Hermitage", "Vallée du Rhône"),
    ("Testland", "Exemple", "Testland"),                           # unknown appellation: unchanged
    ("", "Fronton", ""),                                           # no region given: nothing invented
])
def test_fix_region(region, appellation, expected):
    assert leclerc.fix_region(region, appellation) == expected


@pytest.mark.parametrize("name, producer", [
    ("Château Tour De Pressac 2022", "Château Tour De Pressac"),
    ("Domaine du mas amiel BIO", "Domaine du mas amiel"),
    ("Clos Maginiai BIO", "Clos Maginiai"),
    ("Domaine Barreau", "Domaine Barreau"),
    ("Les charmes", ""),
    ("Laurent Brotte", ""),
    ("Plaimont Les vieilles vignes", ""),
])
def test_producer_from_name(name, producer):
    assert leclerc.producer_from_name(name) == producer


def test_parse_sample_has_no_producer_for_a_cuvee_name():
    assert leclerc.parse(PAGE, URL)["fields"]["producer"] == ""


def test_endpoint_reports_a_known_bottle(client, admin_headers, monkeypatch):
    import httpx
    from tests.webmock import patch_web

    patch_web(monkeypatch, lambda request: httpx.Response(200, text=PAGE, headers={"content-type": "text/html"}))
    fields = client.post("/fill-from-url", json={"url": URL}, headers=admin_headers).json()["fields"]
    client.post("/wines", json={**fields, "quantity": 0, "wishlist": True}, headers=admin_headers)
    found = client.post("/fill-from-url", json={"url": URL}, headers=admin_headers).json()["existing_wine_id"]
    rows = client.get("/export/json", headers=admin_headers).json()
    assert found is not None
    assert fields["barcode"] in {r["barcode"] for r in rows}
    assert client.get(f"/wines/{found}", headers=admin_headers).json()["barcode"] == fields["barcode"]


def test_endpoint_reports_no_match_for_an_unknown_bottle(client, admin_headers, monkeypatch):
    import httpx
    from tests.webmock import patch_web

    page = PAGE.replace("1234567890123", "9999999999994")
    patch_web(monkeypatch, lambda request: httpx.Response(200, text=page, headers={"content-type": "text/html"}))
    other = "https://www.e.leclerc/fp/another-wine-9999999999994"
    assert client.post("/fill-from-url", json={"url": other}, headers=admin_headers).json()["existing_wine_id"] is None
