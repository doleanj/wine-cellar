"""EU e-label (ScanTrust "U-label") resolver for scanned wine QR codes.

The QR on the bottle is a short link (*.st4.ch) that redirects to elabel.scantrust.com with a
per-scan uid and a consumer api_key in the URL fragment. The e-label page reads its data from
api.scantrust.com using that key. We do the same two steps server-side, strictly allow-listed.
"""
import re
from typing import Optional
from urllib.parse import urlparse, parse_qs, unquote

import httpx

SHORT_SUFFIX = ".st4.ch"
ELABEL_HOST = "elabel.scantrust.com"
API_URL = "https://api.scantrust.com/api/v2/consumer/scan/{uid}/combined-info/"
UID_RE = re.compile(r"^[0-9a-fA-F-]{16,64}$")


class ElabelError(Exception):
    pass


def is_elabel_url(url: str) -> bool:
    try:
        p = urlparse((url or "").strip())
    except ValueError:
        return False
    host = (p.hostname or "").lower()
    return p.scheme == "https" and (host.endswith(SHORT_SUFFIX) or host == ELABEL_HOST)


def parse_elabel_location(location: str) -> tuple[str, str]:
    """(uid, api_key) from the elabel.scantrust.com redirect target (values live in the fragment)."""
    p = urlparse(location)
    if p.scheme != "https" or (p.hostname or "").lower() != ELABEL_HOST:
        raise ElabelError("unexpected redirect target")
    frag = p.fragment.split("?", 1)[1] if "?" in p.fragment else p.query
    q = parse_qs(frag)
    uid = (q.get("uid") or [""])[0]
    key = unquote((q.get("api_key") or [""])[0])
    if not UID_RE.match(uid) or not key:
        raise ElabelError("uid/api_key missing")
    return uid, key


def _text(v) -> str:
    return str(v).strip() if v not in (None, "") else ""


def _num(v) -> Optional[float]:
    try:
        return float(str(v).replace(",", ".").strip().split()[0])
    except (ValueError, IndexError):
        return None


def _pick_lang(d, prefer=("fr", "en", "de")) -> tuple[str, str]:
    if not isinstance(d, dict) or not d:
        return "", ""
    for lang in prefer:
        if _text(d.get(lang)):
            return _text(d[lang]), lang
    k = next((k for k, v in d.items() if _text(v)), None)
    return (_text(d[k]), k) if k else ("", "")


COLOURS = {"red": "red", "white": "white", "rose": "rosé", "rosé": "rosé"}
SWEETNESS = {"dry": "sec", "sec": "sec", "medium": "doux", "sweet": "moelleux"}


def normalize(data: dict, elabel_url: str = "") -> dict:
    """Map the combined-info JSON to our wine fields. Missing data stays empty/None."""
    code = data.get("code") or {}
    product = code.get("product") or {}
    brand = (code.get("brand") or {}).get("name") or ""
    company = (data.get("company") or {}).get("name") or ""
    el = ((data.get("elabel") or {}).get("published")) or {}
    info = el.get("product-infos") or {}
    op = el.get("business-operator") or {}
    gi = el.get("geographical-indications") or {}
    ing = el.get("ingredients") or {}
    nut = el.get("nutrition") or {}

    colour_key = _text(info.get("wine_colour")).replace("wine_colour_", "").lower()
    sweet_key = _text(info.get("wine_sweetness"))
    sweet = ""
    for k, v in SWEETNESS.items():
        if k in sweet_key.lower() or f"_{k}" in sweet_key.lower():
            sweet = v
            break
    if not sweet and re.search(r"_b_dry|_dry", sweet_key.lower()):
        sweet = "sec"

    description, desc_lang = _pick_lang(info.get("sales_description"))
    indications = [_text(i.get("description")) for i in (gi.get("list") or []) if isinstance(i, dict)]
    ingredients, sulphites = [], False
    for i in ing.get("list") or []:
        if not isinstance(i, dict):
            continue
        name = _text(i.get("description")).replace("ingredient_", "").replace("_", " ")
        if name:
            ingredients.append(name)
        if i.get("is_allergen") and "sulph" in name.lower():
            sulphites = True

    nutrition = {}

    def walk(rows):
        for row in rows or []:
            if not isinstance(row, dict):
                continue
            key, unit = _text(row.get("key")), _text(row.get("unit")).lower()
            val = _num(row.get("per_100ml"))
            if unit == "kcal":
                nutrition["energy_kcal"] = val
            elif key == "sugar":
                nutrition["sugar_g"] = val
            elif key == "carbohydrate":
                nutrition["carbs_g"] = val
            walk(row.get("children"))
    walk(nut.get("table"))

    bottled_by = ""
    for role in ("bottled_by", "produced_by"):
        entry = op.get(role)
        if isinstance(entry, dict):
            bottled_by = next((_text(v) for v in entry.values() if _text(v)), "")
        elif entry:
            bottled_by = _text(entry)
        if bottled_by:
            break

    name = _pick_lang(info.get("product_name"))[0] if isinstance(info.get("product_name"), dict) \
        else _text(info.get("product_name"))
    name = name or _text(product.get("name"))
    vol = info.get("volumes")
    vol = vol[0] if isinstance(vol, list) and vol else vol
    return {
        "fields": {
            "name": name,
            "producer": _text(brand) or _text(company),
            "grape": _text(info.get("vine_variety")),
            "vintage": int(_num(info.get("vintage_year"))) if _num(info.get("vintage_year")) else None,
            "alcohol": _num(info.get("alcohol_volume")),
            "type": COLOURS.get(colour_key, ""),
            "sweetness": sweet,
            "description": description,
            "region": indications[0] if indications else "",
            "country": "France" if "FR" in (info.get("origin") or []) else "",
            "elabel_url": elabel_url,
            "ingredients": ", ".join(ingredients),
            "sulphites": sulphites,
            "energy_kcal_100ml": nutrition.get("energy_kcal"),
            "sugar_g_100ml": nutrition.get("sugar_g"),
            "carbs_g_100ml": nutrition.get("carbs_g"),
            "bottled_by": bottled_by,
            "volume_ml": int(_num(vol)) if _num(vol) else None,
        },
        "description_lang": desc_lang,
        "qr": _text((code.get("qrcode") or {}).get("message")),
    }


async def resolve(url: str, client: httpx.AsyncClient) -> dict:
    """Two requests: short link (no redirect following) then combined-info. One scan = one call."""
    if not is_elabel_url(url):
        raise ElabelError("not an e-label link")
    r = await client.get(url.strip(), follow_redirects=False)
    loc = r.headers.get("location")
    if not loc:
        raise ElabelError("no redirect from short link")
    uid, key = parse_elabel_location(loc)
    r2 = await client.get(API_URL.format(uid=uid), params={"show_elabel": "true"},
                          headers={"X-ScanTrust-Consumer-Api-Key": key})
    if r2.status_code != 200:
        raise ElabelError(f"e-label service answered {r2.status_code}")
    return normalize(r2.json(), url.strip())
