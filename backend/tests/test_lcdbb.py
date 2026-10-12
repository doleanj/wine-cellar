from pathlib import Path

import pytest

import lcdbb
import sources

PAGE = (Path(__file__).parent / "fixtures" / "lcdbb_sample.html").read_text(encoding="utf8")
URL = "https://lacompagniedesbonnesbouteilles.fr/produit/vin-rouge-domaine-test-cuvee-exemple-2022-75-cl/"


def test_canonical_url():
    assert lcdbb.canonical_url(URL + "?utm_source=x#y") == URL
    assert lcdbb.canonical_url(URL.rstrip("/").replace("https://", "https://www.")) == URL


@pytest.mark.parametrize("u", [
    "http://lacompagniedesbonnesbouteilles.fr/produit/abc/", "https://evil.example.com/produit/abc/",
    "https://lacompagniedesbonnesbouteilles.fr.evil.com/produit/abc/", "https://lacompagniedesbonnesbouteilles.fr/vente/vins/",
    "https://lacompagniedesbonnesbouteilles.fr/produit/", "",
])
def test_canonical_url_rejects(u):
    assert lcdbb.canonical_url(u) == ""


def test_parse_sample_page():
    f = lcdbb.parse(PAGE, URL)["fields"]
    assert f["name"] == "Exemple Cuvée Exemple"      # appellation (without AOP) + cuvée
    assert (f["producer"], f["grape"], f["vintage"], f["type"]) == ("Domaine Test", "Cépage test", 2022, "red")
    assert f["region"] == "Exemple, Testland" and f["country"] == "France"
    assert (f["alcohol"], f["volume_ml"], f["sulphites"], f["keep_until_years"]) == (13.0, 750, True, 3)
    assert f["pairings"] == "aperitif,charcuterie,grillades"
    assert f["description"] == "Texte de test fruité et poivré."
    assert (f["price"], f["image_url"], f["url"]) == (22.9, "https://img.example.test/a.jpg", URL)


def test_parse_empty_page_raises():
    with pytest.raises(lcdbb.LcdbbError):
        lcdbb.parse("<html><body>nothing</body></html>", URL)


def test_sources_dispatch_and_description():
    mod, canon = sources.match(URL + "?x=1")
    assert mod is lcdbb and canon == URL
    assert sources.match("https://www.e.leclerc/fp/abc-123")[0].KEY == "leclerc"
    assert sources.match("https://example.com/x")[0].KEY == "generic"
    assert sources.match("http://example.com/x")[0] is None
    keys = [s["key"] for s in sources.describe()]
    assert keys == ["leclerc", "lcdbb", "generic"]


def test_endpoints(client, admin_headers, monkeypatch):
    import httpx
    assert client.get("/fill-sources").status_code == 401
    r = client.get("/fill-sources", headers=admin_headers)
    assert r.status_code == 200 and [s["key"] for s in r.json()] == ["leclerc", "lcdbb", "generic"]

    from tests.webmock import patch_web

    def handler(request):
        assert str(request.url) == URL
        return httpx.Response(200, text=PAGE, headers={"content-type": "text/html; charset=utf-8"})

    patch_web(monkeypatch, handler)
    r = client.post("/fill-from-url", json={"url": URL + "?utm=1"}, headers=admin_headers)
    assert r.status_code == 200 and r.json()["source"] == "lcdbb" and r.json()["source_name"] == lcdbb.NAME
    assert client.post("/fill-from-url", json={"url": "http://example.com/x"}, headers=admin_headers).status_code == 400
