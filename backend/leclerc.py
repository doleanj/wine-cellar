"""Fill a wine from an e.leclerc product page (/fp/...): personal use, one page per user action.

The page is server-rendered: a JSON-LD ``Product`` block (name, EAN, price, images) plus a list of
label/value text nodes ("Millésime", "Cépage", "Potentiel de garde", ...). We read both; nothing is
stored from the page except the fields the user confirms in the preview.
"""
import html as htmllib
import json
import re
from typing import Optional
from urllib.parse import urlparse

ALLOWED_HOSTS = ("www.e.leclerc", "e.leclerc")


class LeclercError(Exception):
    pass


def canonical_url(url: str) -> str:
    """https URL of an /fp/ product page without query string or fragment, else ''."""
    try:
        p = urlparse((url or "").strip())
    except ValueError:
        return ""
    if p.scheme != "https" or (p.hostname or "").lower() not in ALLOWED_HOSTS:
        return ""
    if not re.match(r"^/fp/[A-Za-z0-9._%-]+/?$", p.path):
        return ""
    return f"https://{p.hostname.lower()}{p.path}"


def _text_nodes(page: str) -> list:
    page = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", page)
    page = re.sub(r"<!--.*?-->", " ", page, flags=re.S)
    nodes = []
    for t in re.split(r"<[^>]+>", page):
        t = htmllib.unescape(re.sub(r"\s+", " ", t)).strip()
        if t:
            nodes.append(t)
    return nodes


def _pairs(nodes: list, labels: set) -> dict:
    out = {}
    for i, n in enumerate(nodes[:-1]):
        if n in labels and n not in out and nodes[i + 1] not in labels:
            out[n] = nodes[i + 1]
    return out


def _json_ld_product(page: str) -> dict:
    for m in re.finditer(r'(?is)<script[^>]*application/ld\+json[^>]*>(.*?)</script>', page):
        try:
            d = json.loads(m.group(1))
        except ValueError:
            continue
        for item in (d if isinstance(d, list) else [d]):
            if isinstance(item, dict) and item.get("@type") == "Product":
                return item
    return {}


def _int(s: str) -> Optional[int]:
    m = re.search(r"\d+", s or "")
    return int(m.group()) if m else None


def _float(s: str) -> Optional[float]:
    m = re.search(r"\d+(?:[.,]\d+)?", s or "")
    return float(m.group().replace(",", ".")) if m else None


COLOURS = {"rouge": "red", "blanc": "white", "rosé": "rosé", "rose": "rosé"}

# Leclerc "Accords Mets et Vins" words -> our pairing keys (see frontend wine-reference PAIRINGS)
PAIRING_WORDS = [
    ("apéritif", "aperitif"), ("aperitif", "aperitif"), ("canard", "canard"), ("charcuterie", "charcuterie"),
    ("exotique", "cuisine-exotique"), ("asiatique", "cuisine-exotique"), ("dessert", "desserts"),
    ("foie gras", "foie-gras"), ("fromage à pâte dure", "fromage-pate-dure"), ("pâte molle", "fromage-pate-molle"),
    ("persillé", "fromage-persille"), ("fromage", "fromage"), ("fruits de mer", "fruits-de-mer"),
    ("coquillage", "fruits-de-mer"), ("gibier", "gibiers"), ("grillade", "grillades"), ("barbecue", "grillades"),
    ("légume", "legumes-verts"), ("sauce", "plats-en-sauce"), ("poisson", "poisson"), ("rôti", "roti"),
    ("salade", "salade"), ("viande rouge", "viande-rouge"), ("viandes rouges", "viande-rouge"),
    ("viande blanche", "viande-blanche"), ("viandes blanches", "viande-blanche"), ("volaille", "volaille"),
]


def pairing_keys(text: str) -> str:
    low = (text or "").lower()
    keys = []
    for word, key in PAIRING_WORDS:
        if word in low and key not in keys:
            keys.append(key)
    return ",".join(keys)


LABELS = {
    "Millésime", "Couleur (Vin)", "Région viticole", "Appellation viticole", "Cépage", "Pays d'origine",
    "Contenu net", "Alcool", "Allergène(s)", "Accords Mets et Vins", "Arômes", "Dégustation bouche (bouche)",
    "Dégustation olfactive (Nez)", "Dégustation robe (Œil)", "Echelle de fruit", "Echelle de personnalité",
    "Potentiel de garde", "Température de service", "Dégustation", "Occasion (Vin et alcool)",
    "Type d'appellation", "Déclaration nutritionnelle", "Catégorie produits", "Libellé", "Vin millésimé",
}


def parse(page: str, url: str) -> dict:
    prod = _json_ld_product(page)
    attrs = _pairs(_text_nodes(page), LABELS)
    if not prod and not attrs:
        raise LeclercError("no product data on the page")

    title = htmllib.unescape(str(prod.get("name") or attrs.get("Libellé") or "")).strip()
    # "Les charmes, 2025 - Morgon AOP - Rouge - 75 cl" -> "Les charmes"
    name = re.split(r",\s*(?:19|20)\d\d\b| - ", title)[0].strip() or title

    offers = prod.get("offers") or []
    price = next((o.get("price") for o in offers if isinstance(o, dict) and o.get("price") is not None), None)
    images = prod.get("image") or []
    image = images[0] if isinstance(images, list) and images else (images if isinstance(images, str) else "")
    if not str(image).startswith("https://"):
        image = ""

    region, appellation = attrs.get("Région viticole", ""), attrs.get("Appellation viticole", "")
    region_text = ", ".join(x for x in (region, appellation) if x)
    colour = COLOURS.get(attrs.get("Couleur (Vin)", "").lower(), "")
    cl = _float(attrs.get("Contenu net", ""))

    tasting = []
    for label, tag in (("Dégustation robe (Œil)", "Œil"), ("Dégustation olfactive (Nez)", "Nez"),
                       ("Dégustation bouche (bouche)", "Bouche"), ("Dégustation", "Style"),
                       ("Arômes", "Arômes")):
        if attrs.get(label):
            tasting.append(f"{tag} : {attrs[label]}")

    def scale(label):
        v = _int(attrs.get(label, ""))
        return v if v and 1 <= v <= 5 else None

    fields = {
        "name": name,
        "grape": attrs.get("Cépage", ""),
        "vintage": _int(attrs.get("Millésime", "")),
        "type": colour,
        "region": region_text,
        "country": attrs.get("Pays d'origine", ""),
        "alcohol": _float(attrs.get("Alcool", "")),
        "volume_ml": int(round(cl * 10)) if cl else None,
        "sulphites": "sulfit" in attrs.get("Allergène(s)", "").lower(),
        "pairings": pairing_keys(attrs.get("Accords Mets et Vins", "")),
        "profile_fruit": scale("Echelle de fruit"),
        "profile_personality": scale("Echelle de personnalité"),
        "keep_until_years": _int(attrs.get("Potentiel de garde", "")),
        "serving_temp": _int(attrs.get("Température de service", "")),
        "tasting": "\n".join(tasting),
        "price": float(price) if price is not None else None,
        "barcode": str(prod.get("gtin13") or prod.get("sku") or ""),
        "image_url": image,
        "url": url,
    }
    return {"fields": fields, "source": "leclerc"}
