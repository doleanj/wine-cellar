"""Fill a wine from a La Compagnie des Bonnes Bouteilles product page (/produit/...).

WooCommerce shop: the title is an <h1>, the price sits in the ``.price`` block, the details in a
two-column attributes table (Producteur, Cuvée, Appellation, Cépages, ...), the sensory notes in the
product description. Personal use, one page per user action.
"""
import html as htmllib
import re
from urllib.parse import urlparse

from leclerc import _float, _int, _json_ld_product, pairing_keys, COLOURS

KEY = "lcdbb"
NAME = "La Compagnie des Bonnes Bouteilles"
HOSTS = ("lacompagniedesbonnesbouteilles.fr", "www.lacompagniedesbonnesbouteilles.fr")
PATH_PREFIX = "/produit/"
EXAMPLE = "https://lacompagniedesbonnesbouteilles.fr/produit/…"
FIELDS = ["name", "producer", "grape", "vintage", "type", "region", "country", "alcohol", "volume_ml",
          "sulphites", "pairings", "keep_until_years", "description", "price", "image_url", "url"]


class LcdbbError(Exception):
    pass


def canonical_url(url: str) -> str:
    """https URL of a /produit/ page on the bare domain, without query string or fragment, else ''."""
    try:
        p = urlparse((url or "").strip())
    except ValueError:
        return ""
    if p.scheme != "https" or (p.hostname or "").lower() not in HOSTS:
        return ""
    if not re.match(r"^/produit/[A-Za-z0-9._%-]+/?$", p.path):
        return ""
    path = p.path if p.path.endswith("/") else p.path + "/"
    return f"https://lacompagniedesbonnesbouteilles.fr{path}"


def _clean(fragment: str) -> str:
    return htmllib.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment))).strip()


def _attributes(page: str) -> dict:
    out = {}
    for th, td in re.findall(r"(?is)<tr[^>]*>\s*<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>", page):
        k, v = _clean(th), _clean(td)
        if k and v and k not in out:
            out[k] = v
    return out


def _section(description: str, label: str) -> str:
    """Text of '<strong>Label :</strong> ...' up to the next <strong> heading."""
    m = re.search(rf"(?is)<strong>\s*{label}\s*:?\s*</strong>(.*?)(?=<strong>|\Z)", description)
    return _clean(m.group(1)) if m else ""


def parse(page: str, url: str) -> dict:
    prod = _json_ld_product(page)
    attrs = _attributes(page)
    h1 = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", page)
    title = _clean(h1.group(1)) if h1 else _clean(str(prod.get("name") or ""))
    if not title and not attrs:
        raise LcdbbError("no product data on the page")

    description_html = htmllib.unescape(str(prod.get("description") or ""))
    tasting = _section(description_html, "Dégustation")
    pairing_text = attrs.get("Accompagnement") or _section(description_html, "Accompagnement")

    appellation = re.sub(r"^(AOP|AOC|IGP|IGT|Vin de France)\s+", "", attrs.get("Appellation", ""), flags=re.I).strip()
    bottling_region = attrs.get("Région d'embouteillage", "")
    cuvee = attrs.get("Cuvée", "")
    name = " ".join(x for x in (appellation, cuvee) if x) or title

    vintage = re.search(r"\b(19|20)\d\d\b", title)
    price = None
    pm = re.search(r'(?is)class="price"[^>]*>.*?<bdi>\s*([\d\s.,]+)', page)
    if pm:
        price = _float(pm.group(1).replace(" ", ""))
    if price is None:
        offers = prod.get("offers")
        offers = offers if isinstance(offers, list) else ([offers] if offers else [])
        price = next((_float(str(o.get("price"))) for o in offers if isinstance(o, dict) and o.get("price")), None)

    image = prod.get("image") or ""
    image = image[0] if isinstance(image, list) and image else image
    if not str(image).startswith("https://"):
        image = ""
    cl = _float(attrs.get("Contenance", ""))

    fields = {
        "name": name,
        "producer": attrs.get("Producteur", ""),
        "grape": attrs.get("Cépages", ""),
        "vintage": int(vintage.group()) if vintage else None,
        "type": COLOURS.get(attrs.get("Type de vin", "").lower(), ""),
        "region": ", ".join(x for x in (appellation, bottling_region) if x),
        "country": "France" if (appellation or bottling_region) else "",
        "alcohol": _float(attrs.get("Degré (% vol)", "")),
        "volume_ml": int(round(cl * 10)) if cl else None,
        "sulphites": "sulfit" in attrs.get("Infos allergènes", "").lower(),
        "pairings": pairing_keys(pairing_text),
        "keep_until_years": _int(attrs.get("Durée de garde", "")),
        "description": tasting,
        "price": price,
        "image_url": image,
        "url": url,
    }
    return {"fields": fields, "source": KEY}
