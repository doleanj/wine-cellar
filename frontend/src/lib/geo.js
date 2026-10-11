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
