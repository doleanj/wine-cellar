#!/usr/bin/env python3
"""One-off: read the region paragraph that e.leclerc shows on wine pages ("Partez à la découverte du ...").

For each region of the app, open its e.leclerc wine category page, take the first listed product and read the
region block from that product page. Personal use, polite: about 20 requests in total, 3 s apart, only /cat/
and /fp/ pages. The texts are third-party material, so they are written OUTSIDE the repository:

    python3 scripts/fetch_leclerc_region_texts.py ../wine-cellar-assets/leclerc-regions

Output: <folder>/regions_extra.json  {"<region key>": {"title", "text", "source_url", "category"}}
Then upload with scripts/load_region_extra.py.
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from leclerc import _text_nodes  # noqa: E402

BASE = "https://www.e.leclerc"
UA = "Mozilla/5.0 (personal wine-cellar app)"
DELAY = 3

# region key (backend/regions_seed.py) -> e.leclerc category slug. Savoie has no category of its own.
CATEGORIES = {
    "bordelais": "vins-de-bordeaux",
    "sud-ouest": "vins-du-sud-ouest",
    "languedoc-roussillon": "vins-du-languedoc-roussillon",
    "vallee-du-rhone": "vins-de-la-vallee-du-rhone",
    "savoie-jura": "vins-du-jura",
    "beaujolais": "vins-du-beaujolais",
    "bourgogne": "vins-de-bourgogne",
    "vallee-de-la-loire": "vins-de-loire",
    "alsace": "vins-d-alsace",
    "champagne": "champagnes",
}


def get(url: str) -> str:
    time.sleep(DELAY)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


# words that give away another region's text (Leclerc reuses the Alsace paragraph on its Savoie pages)
FOREIGN_MARKERS = {"alsace": (), "default": ("Alsacien",)}


def plausible(key: str, text: str) -> bool:
    markers = FOREIGN_MARKERS.get(key, FOREIGN_MARKERS["default"])
    return not any(m.lower() in text.lower() for m in markers)


def region_block(page: str):
    """(title, text) of the 'Partez à la découverte ...' block, else None."""
    nodes = _text_nodes(page)
    for i, n in enumerate(nodes):
        if n.lower().startswith("partez à la découverte"):
            paras = []
            for m in nodes[i + 1:i + 12]:
                if m.lower().startswith(("cliquez ici", "a voir aussi", "à voir aussi", "-->")):
                    break
                paras.append(m)
            if paras:
                return n, "\n\n".join(paras)
    return None


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {}
    for key, slug in CATEGORIES.items():
        cat_url = f"{BASE}/cat/{slug}"
        try:
            products = list(dict.fromkeys(re.findall(r'(/fp/[a-z0-9-]+)', get(cat_url))))[:3]
        except Exception as exc:  # noqa: BLE001
            print(f"{key}: category failed: {exc}")
            continue
        found = None
        for path in products:
            try:
                found = region_block(get(BASE + path))
            except Exception as exc:  # noqa: BLE001
                print(f"{key}: {path} failed: {exc}")
                continue
            if found and not plausible(key, found[1]):
                print(f"{key}: skipped {path}: the text does not look like this region")
                found = None
                continue
            if found:
                result[key] = {"title": found[0], "text": found[1], "source_url": BASE + path, "category": cat_url}
                print(f"{key}: ok ({len(found[1])} chars) <- {path}")
                break
        if not found:
            print(f"{key}: no region block found on the first {len(products)} products")
    (out_dir / "regions_extra.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(result)}/{len(CATEGORIES)} regions to {out_dir / 'regions_extra.json'}")


if __name__ == "__main__":
    main()
