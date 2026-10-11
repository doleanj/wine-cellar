#!/usr/bin/env python3
"""Build frontend/static/geo/appellations.geojson: one simplified polygon per wine appellation.

Method: the INAO list "Aires géographiques des AOC/AOP" (commune -> appellation, data.gouv.fr,
Licence Ouverte) is joined with commune outlines from geo.api.gouv.fr (IGN Admin Express, open data)
and the communes of each appellation are dissolved into one shape. This is the delimited commune
area, not the exact parcel area, so borders are approximate.

    pip install shapely
    python3 scripts/build_appellation_geo.py <aoc-communes.csv> <cache-dir> frontend/static/geo/appellations.geojson
"""
import csv
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

from shapely.geometry import mapping, shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from regions_seed import REGIONS_SEED  # noqa: E402

# Seed appellation -> table-name prefixes, where the table splits or renames an appellation.
ALIASES = {
    "Chautagne": ["vin de savoie chautagne"],
    "Ayse": ["vin de savoie ayze"],
    "Chignin": ["vin de savoie chignin"],
    "Apremont": ["vin de savoie apremont"],
    "Abymes": ["vin de savoie abymes"],
    "Saumur": ["saumur"],
    "Pouilly-Fumé": ["pouilly fume ou blanc fume"],
    "Alsace": ["alsace"],
    "Alsace Grand Cru": ["alsace grand cru"],
}
EXCLUDE_PREFIX = {"Alsace": ["alsace grand cru"]}
TOLERANCE = 0.002  # degrees (~200 m): small enough to look right at region zoom, keeps the file light


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()).strip()


def dept(code):
    return code[:3] if code.startswith("97") else code[:2]


def fetch_dept(d, cache):
    f = cache / f"communes-{d}.json"
    if not f.exists():
        url = f"https://geo.api.gouv.fr/communes?codeDepartement={d}&fields=code&format=geojson&geometry=contour"
        print("fetching", d, flush=True)
        with urllib.request.urlopen(url, timeout=120) as r:
            f.write_bytes(r.read())
    return {ft["properties"]["code"]: shape(ft["geometry"]) for ft in json.loads(f.read_text())["features"]}


def main():
    csv_path, cache, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    cache.mkdir(parents=True, exist_ok=True)
    table = {}  # normalised appellation name -> set(INSEE codes)
    for ci, _dep, _com, _art, aire, _ida in list(csv.reader(csv_path.open(encoding="latin-1"), delimiter=";"))[1:]:
        table.setdefault(norm(aire), set()).add(ci)

    wanted = []  # (region key, appellation, commune codes)
    for region in REGIONS_SEED:
        for app in region["appellations"]:
            if app in ALIASES:
                skip = EXCLUDE_PREFIX.get(app, [])
                codes = set().union(*[c for n, c in table.items()
                                      if any(n == p or n.startswith(p + " ") for p in ALIASES[app])
                                      and not any(n.startswith(s) for s in skip)] or [set()])
            else:
                codes = table.get(norm(app), set())
            if codes:
                wanted.append((region["key"], app, codes))
            else:
                print("no commune data for", region["key"], app)

    communes = {}
    for d in sorted({dept(c) for _, _, codes in wanted for c in codes}):
        communes.update(fetch_dept(d, cache))

    features = []
    for key, app, codes in wanted:
        geoms = [communes[c] for c in codes if c in communes]
        if not geoms:
            continue
        geom = unary_union(geoms).simplify(TOLERANCE, preserve_topology=True)
        m = mapping(geom)

        def rnd(c):
            return [rnd(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], 4), round(c[1], 4)]

        m = {"type": m["type"], "coordinates": rnd(m["coordinates"])}
        features.append({"type": "Feature", "properties": {"region": key, "name": app, "communes": len(geoms)}, "geometry": m})

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, separators=(",", ":")))
    print(f"{len(features)} appellations, {out.stat().st_size // 1024} KB -> {out}")


if __name__ == "__main__":
    main()
