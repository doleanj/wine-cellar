import json
from pathlib import Path

import httpx
import pytest

import elabel
import main

SAMPLE = json.loads((Path(__file__).parent / "fixtures" / "elabel_sample.json").read_text())
SHORT = "https://gv9l.st4.ch/orxPNvptCWaT"
UID = "3742869a-c492-4680-b36b-f9086d1574a6"
LOCATION = f"https://elabel.scantrust.com/default/#/?uid={UID}&api_key=abc%3Adef%3Aghi&qr=orxPNvptCWaT"


@pytest.mark.parametrize("url,ok", [
    (SHORT, True),
    ("https://elabel.scantrust.com/default/#/?uid=x", True),
    ("http://gv9l.st4.ch/x", False),
    ("https://evil.example.com/x", False),
    ("https://st4.ch.evil.com/x", False),
    ("https://notst4.ch/x", False),
    ("3017620422003", False),
    ("", False),
])
def test_is_elabel_url(url, ok):
    assert elabel.is_elabel_url(url) is ok


def test_parse_location():
    assert elabel.parse_elabel_location(LOCATION) == (UID, "abc:def:ghi")


@pytest.mark.parametrize("loc", [
    "https://evil.example.com/#/?uid=%s&api_key=k" % UID,
    "http://elabel.scantrust.com/#/?uid=%s&api_key=k" % UID,
    "https://elabel.scantrust.com/#/?uid=../x&api_key=k",
    "https://elabel.scantrust.com/#/?uid=%s" % UID,
])
def test_parse_location_rejects(loc):
    with pytest.raises(elabel.ElabelError):
        elabel.parse_elabel_location(loc)


def test_normalize_sample():
    f = elabel.normalize(SAMPLE, SHORT)["fields"]
    assert f["name"] == "BOURGOGNE GAMAY 2024"
    assert (f["grape"], f["vintage"], f["alcohol"]) == ("Gamay", 2024, 12.5)
    assert (f["type"], f["sweetness"], f["volume_ml"]) == ("red", "sec", 750)
    assert f["sulphites"] is True and "metatartaric acid" in f["ingredients"]
    assert (f["energy_kcal_100ml"], f["sugar_g_100ml"], f["carbs_g_100ml"]) == (72.0, 0.1, 0.8)
    assert f["elabel_url"] == SHORT and f["description"].startswith("Au nez")


def test_normalize_sparse_data_does_not_crash():
    r = elabel.normalize({"code": {"product": {"name": "X"}}, "elabel": {"published": {
        "product-infos": {"vintage_year": "", "alcohol_volume": "n/a", "wine_colour": "wine_colour_rose"}}}})
    f = r["fields"]
    assert f["name"] == "X" and f["type"] == "rosé"
    assert f["vintage"] is None and f["alcohol"] is None and f["sulphites"] is False


def _mock_client(calls):
    def handler(request: httpx.Request):
        calls.append(request)
        if request.url.host == "gv9l.st4.ch":
            return httpx.Response(302, headers={"location": LOCATION})
        assert request.url.host == "api.scantrust.com"
        assert request.headers["X-ScanTrust-Consumer-Api-Key"] == "abc:def:ghi"
        return httpx.Response(200, json=SAMPLE)
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


@pytest.mark.anyio
async def test_resolve_makes_exactly_two_allowlisted_calls():
    calls = []
    async with _mock_client(calls) as c:
        r = await elabel.resolve(SHORT, c)
    assert [x.url.host for x in calls] == ["gv9l.st4.ch", "api.scantrust.com"]
    assert r["fields"]["grape"] == "Gamay"


@pytest.mark.anyio
async def test_resolve_rejects_foreign_url_without_network():
    calls = []
    async with _mock_client(calls) as c:
        with pytest.raises(elabel.ElabelError):
            await elabel.resolve("https://evil.example.com/x", c)
    assert calls == []


def test_endpoint_requires_login(client):
    assert client.post("/elabel/resolve", json={"url": SHORT}).status_code == 401


def test_endpoint_rejects_foreign_url(client, admin_headers):
    r = client.post("/elabel/resolve", json={"url": "https://evil.example.com/x"}, headers=admin_headers)
    assert r.status_code == 400


def test_endpoint_returns_fields_and_existing_wine(client, admin_headers, monkeypatch):
    async def fake_resolve(url, c):
        return elabel.normalize(SAMPLE, url)
    monkeypatch.setattr(elabel, "resolve", fake_resolve)
    r = client.post("/elabel/resolve", json={"url": SHORT}, headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["fields"]["name"] == "BOURGOGNE GAMAY 2024" and body["existing_wine_id"] is None
    # save the wine with the e-label fields, then the same QR is recognised
    w = client.post("/wines", json={**body["fields"], "name": "Gamay", "type": "red"}, headers=admin_headers)
    assert w.status_code in (200, 201), w.text
    assert w.json()["elabel_url"] == SHORT and w.json()["sulphites"] is True
    r2 = client.post("/elabel/resolve", json={"url": SHORT}, headers=admin_headers)
    assert r2.json()["existing_wine_id"] == w.json()["id"]


def test_endpoint_upstream_failure_is_502(client, admin_headers, monkeypatch):
    async def boom(url, c):
        raise elabel.ElabelError("down")
    monkeypatch.setattr(elabel, "resolve", boom)
    r = client.post("/elabel/resolve", json={"url": SHORT}, headers=admin_headers)
    assert r.status_code == 502
