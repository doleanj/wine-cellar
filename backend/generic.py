"""Basic fallback for any other shop: standard product data (JSON-LD Product), then OpenGraph tags.

Best effort: name, brand, description, photo, price, EAN, plus a few guesses from the text (vintage,
alcohol, colour). Anything the page does not state stays empty. The caller (main.py) is responsible for
the network side: public hosts only, https on port 443, validated redirects, size cap.
"""
import html as htmllib
import re
from urllib.parse import parse_qsl, urlencode, urlparse

from leclerc import _float, _json_ld_product

KEY = "generic"
NAME = "Any other shop (basic data)"
HOSTS = ("*",)
PATH_PREFIX = "/"
EXAMPLE = "https://…"
FIELDS = ["name", "producer", "description", "vintage", "type", "alcohol", "price", "barcode", "image_url", "url"]
GENERIC = True  # main.py applies the public-host / redirect / size checks to these sources

TRACKING = re.compile(r"^(utm_|gclid|fbclid|msclkid|mc_|et_|_ga|igshid|ref$|ref_|srsltid)", re.I)


class GenericError(Exception):
    pass


def canonical_url(url: str) -> str:
    """https URL on the default port, no credentials, tracking parameters and fragment removed, else ''."""
    try:
        p = urlparse((url or "").strip())
        port = p.port
    except ValueError:
        return ""
    if p.scheme != "https" or not p.hostname or p.username or p.password or port not in (None, 443):
        return ""
    if "." not in p.hostname and ":" not in p.hostname:
        return ""
    query = urlencode([(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if not TRACKING.match(k)])
    host = p.hostname.lower()
    host = f"[{host}]" if ":" in host else host
    return f"https://{host}{p.path or '/'}" + (f"?{query}" if query else "")


def _meta(page: str) -> dict:
    out = {}
    for tag in re.findall(r"(?is)<meta\b[^>]*>", page):
        key = re.search(r'(?is)\b(?:property|name)\s*=\s*["\']([^"\']+)["\']', tag)
        val = re.search(r'(?is)\bcontent\s*=\s*["\']([^"\']*)["\']', tag)
        if key and val and key.group(1).lower() not in out:
            out[key.group(1).lower()] = htmllib.unescape(val.group(1)).strip()
    return out


def _clean(text: str, limit: int = 1500) -> str:
    text = htmllib.unescape(re.sub(r"<[^>]+>", " ", htmllib.unescape(text or "")))
    return re.sub(r"\s+", " ", text).strip()[:limit]


def _first(v):
    return v[0] if isinstance(v, list) and v else v


def _price(prod: dict, meta: dict):
    offers = prod.get("offers")
    offers = offers if isinstance(offers, list) else ([offers] if isinstance(offers, dict) else [])
    for o in offers:
        for k in ("price", "lowPrice"):
            if isinstance(o, dict) and o.get(k) not in (None, ""):
                p = _float(str(o[k]))
                if p is not None:
                    return p
    return _float(meta.get("product:price:amount") or meta.get("og:price:amount") or "")


def _gtin(prod: dict) -> str:
    for k in ("gtin13", "gtin", "gtin14", "gtin12", "gtin8"):
        digits = re.sub(r"\D", "", str(prod.get(k) or ""))
        if len(digits) in (8, 12, 13, 14):
            return digits
    return ""


def parse(page: str, url: str) -> dict:
    prod = _json_ld_product(page)
    meta = _meta(page)
    name = _clean(str(prod.get("name") or meta.get("og:title") or ""), 200)
    if not name:
        m = re.search(r"(?is)<title[^>]*>(.*?)</title>", page)
        name = _clean(m.group(1), 200) if m else ""
    if not name and not prod:
        raise GenericError("no product data on the page")

    brand = prod.get("brand")
    brand = brand.get("name") if isinstance(brand, dict) else brand
    description = _clean(str(prod.get("description") or meta.get("og:description") or meta.get("description") or ""))
    image = _first(prod.get("image"))
    image = image.get("url") if isinstance(image, dict) else image
    image = image or meta.get("og:image") or ""
    if not str(image).startswith("https://"):
        image = ""

    text = f"{name} {description}"
    vintage = re.search(r"\b(19[6-9]\d|20[0-4]\d)\b", name)
    alc = re.search(r"(\d{1,2}(?:[.,]\d)?)\s*%\s*(?:vol|alc)", text, re.I)
    low = text.lower()
    wine_type = ""
    if re.search(r"champagne|cr[ée]mant|prosecco|cava|p[ée]tillant|effervescent", low):
        wine_type = "sparkling"
    elif re.search(r"\bros[ée]\b", low):
        wine_type = "rosé"
    elif re.search(r"\brouge\b", low):
        wine_type = "red"
    elif re.search(r"\bblanc\b", low):
        wine_type = "white"

    fields = {
        "name": name,
        "producer": _clean(str(brand or ""), 120),
        "description": description,
        "vintage": int(vintage.group()) if vintage else None,
        "type": wine_type,
        "alcohol": _float(alc.group(1)) if alc else None,
        "price": _price(prod, meta),
        "barcode": _gtin(prod),
        "image_url": image,
        "url": url,
    }
    return {"fields": fields, "source": KEY}
