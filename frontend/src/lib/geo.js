// Appellation polygons (frontend/static/geo/appellations.geojson, built by scripts/build_appellation_geo.py)
// and the matching of wines to them.
import { matchRegion } from '$lib/regions.js';

let cache = null;

export function loadGeo() {
  if (!cache) {
    cache = fetch('/geo/appellations.geojson')
      .then(r => (r.ok ? r.json() : { features: [] }))
      .then(j => j.features || [])
      .catch(() => { cache = null; return []; });
  }
  return cache;
}

const norm = s => (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();

/**
 * Group wines by the polygons they belong to.
 * - appellation level: the wine's region text contains the appellation name (longest name wins);
 * - region level: only the region is known, so all polygons of that region are listed (lighter style).
 * Returns Map<feature, { level: 'appellation' | 'region', label, wines }>.
 */
export function groupWinesByGeo(wines, features, regionList) {
  const byName = features.map(f => ({ f, n: ` ${norm(f.properties.name)} ` })).filter(x => x.n.trim().length >= 4);
  const out = new Map();
  const add = (f, level, label, wine) => {
    const cur = out.get(f);
    if (cur) { if (level === 'appellation' && cur.level === 'region') { cur.level = level; cur.label = label; } cur.wines.push(wine); }
    else out.set(f, { level, label, wines: [wine] });
  };
  for (const wine of wines) {
    const text = ` ${norm(wine.region)} `;
    if (text.trim() === '') continue;
    const hits = byName.filter(x => text.includes(x.n));
    if (hits.length) {
      const longest = Math.max(...hits.map(x => x.n.length));
      for (const { f } of hits.filter(x => x.n.length === longest)) add(f, 'appellation', f.properties.name, wine);
      continue;
    }
    const m = matchRegion(wine, regionList);
    if (m) for (const f of features.filter(x => x.properties.region === m.region.key)) add(f, 'region', m.region.name, wine);
  }
  return out;
}

// ── Geometry helpers (used by the map to find every zone under a click) ─────────────────────────────

function rings(geom) {
  if (!geom) return [];
  if (geom.type === 'Polygon') return [geom.coordinates];
  if (geom.type === 'MultiPolygon') return geom.coordinates;
  return [];
}

function ringContains(ring, x, y) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i], [xj, yj] = ring[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}

/** Ray-casting point-in-polygon for a GeoJSON feature (Polygon or MultiPolygon, holes respected). */
export function featureContains(feature, lng, lat) {
  return rings(feature.geometry).some(poly => {
    if (!ringContains(poly[0], lng, lat)) return false;
    for (let k = 1; k < poly.length; k++) if (ringContains(poly[k], lng, lat)) return false;
    return true;
  });
}

/** [west, south, east, north] */
export function featureBBox(feature) {
  let w = Infinity, s = Infinity, e = -Infinity, n = -Infinity;
  for (const poly of rings(feature.geometry)) for (const [x, y] of poly[0]) {
    if (x < w) w = x; if (x > e) e = x; if (y < s) s = y; if (y > n) n = y;
  }
  return [w, s, e, n];
}

/** Approximate area (square degrees, shoelace on outer rings) - only used to order zones big -> small. */
export function featureArea(feature) {
  let total = 0;
  for (const poly of rings(feature.geometry)) {
    const r = poly[0];
    let a = 0;
    for (let i = 0, j = r.length - 1; i < r.length; j = i++) a += r[j][0] * r[i][1] - r[i][0] * r[j][1];
    total += Math.abs(a) / 2;
  }
  return total;
}
