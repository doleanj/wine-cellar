from pathlib import Path

import httpx
import pytest

import generic
from tests.webmock import patch_web

FIX = Path(__file__).parent / "fixtures"
PAGE = (FIX / "generic_sample.html").read_text(encoding="utf8")
OG = (FIX / "generic_og_only.html").read_text(encoding="utf8")
HTML = {"content-type": "text/html; charset=utf-8"}


def test_canonical_url_strips_tracking_keeps_other_params():
    assert generic.canonical_url("https://shop.example.test/p/abc?id=7&utm_source=x&gclid=1#frag") == \
        "https://shop.example.test/p/abc?id=7"


@pytest.mark.parametrize("u", [
    "http://shop.example.test/p", "https://user:pw@shop.example.test/p", "https://shop.example.test:8443/p",
    "https://localhost/p", "ftp://shop.example.test/p", "javascript:alert(1)", "",
])
def test_canonical_url_rejects(u):
    assert generic.canonical_url(u) == ""


def test_parse_json_ld_product():
    f = generic.parse(PAGE, "https://shop.example.test/p")["fields"]
    assert f["name"] == "Domaine Exemple Rouge 2021" and f["producer"] == "Domaine Exemple"
    assert (f["vintage"], f["type"], f["alcohol"], f["price"]) == (2021, "red", 13.5, 14.5)
    assert f["barcode"] == "3000000000017" and f["image_url"] == "https://img.example.test/p1.jpg"
    assert f["description"] == "Un vin rouge de test, 13,5% vol." and "<" not in f["description"]


def test_parse_opengraph_fallback_and_empty_page():
    f = generic.parse(OG, "https://shop.example.test/p")["fields"]
    assert (f["name"], f["vintage"], f["type"], f["description"]) == ("Blanc Test 2020", 2020, "white", "Description meta de test.")
    assert f["price"] is None and f["barcode"] == ""
    with pytest.raises(generic.GenericError):
        generic.parse("<html><body>nothing</body></html>", "https://shop.example.test/p")


def _public(monkeypatch, *private):
    import main
    monkeypatch.setattr(main, "_is_public_host", lambda h: h not in private and h != "localhost")


def test_endpoint_generic_page(client, admin_headers, monkeypatch):
    _public(monkeypatch)
    seen = []

    def handler(request):
        seen.append(str(request.url))
        return httpx.Response(200, text=PAGE, headers=HTML)

    patch_web(monkeypatch, handler)
    r = client.post("/fill-from-url", json={"url": "https://shop.example.test/p/abc?utm_source=x"}, headers=admin_headers)
    assert r.status_code == 200 and r.json()["source"] == "generic"
    assert seen == ["https://shop.example.test/p/abc"] and r.json()["fields"]["barcode"] == "3000000000017"


def test_endpoint_rejects_private_hosts_and_non_https(client, admin_headers, monkeypatch):
    _public(monkeypatch, "intranet.example.test", "127.0.0.1")
    patch_web(monkeypatch, lambda request: pytest.fail("no request must be made"))
    for u in ("https://intranet.example.test/p", "https://127.0.0.1/p", "http://shop.example.test/p",
              "https://shop.example.test:8443/p", "https://user:pw@shop.example.test/p"):
        assert client.post("/fill-from-url", json={"url": u}, headers=admin_headers).status_code == 400, u


def test_endpoint_validates_redirect_targets(client, admin_headers, monkeypatch):
    _public(monkeypatch, "intranet.example.test")
    calls = []

    def handler(request):
        calls.append(request.url.host)
        if request.url.host == "shop.example.test":
            return httpx.Response(302, headers={"location": "https://intranet.example.test/secret"})
        pytest.fail("the private redirect target must not be requested")

    patch_web(monkeypatch, handler)
    r = client.post("/fill-from-url", json={"url": "https://shop.example.test/p"}, headers=admin_headers)
    assert r.status_code == 400 and calls == ["shop.example.test"]


def test_endpoint_rejects_non_html_and_caps_size(client, admin_headers, monkeypatch):
    import main
    _public(monkeypatch)
    patch_web(monkeypatch, lambda request: httpx.Response(200, content=b"%PDF", headers={"content-type": "application/pdf"}))
    assert client.post("/fill-from-url", json={"url": "https://shop.example.test/a.pdf"}, headers=admin_headers).status_code == 400
    monkeypatch.setattr(main, "FILL_MAX_BYTES", 200)
    big = "<html><head><title>Big Page 2020</title></head><body>" + "x" * 5000 + "</body></html>"
    patch_web(monkeypatch, lambda request: httpx.Response(200, text=big, headers=HTML))
    r = client.post("/fill-from-url", json={"url": "https://shop.example.test/big"}, headers=admin_headers)
    assert r.status_code == 200, r.text
    assert r.json()["fields"]["name"] == "Big Page 2020"
