// Region reference data: loaded once, matched to a wine by its free-text "region" field.
import { writable } from 'svelte/store';
import { getRegions } from '$lib/api.js';

export const regions = writable([]);
let loading = null;

export function loadRegions() {
  if (!loading) {
    loading = getRegions().then(list => { regions.set(list); return list; }).catch(() => { loading = null; return []; });
  }
  return loading;
}

const norm = s => (s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();

/** Find the region a wine belongs to and the appellation that matched (if any). */
export function matchRegion(wine, list) {
  const text = ` ${norm(wine?.region)} `;
  if (text.trim() === '') return null;
  for (const r of list) {
    if (text.includes(` ${norm(r.name)} `)) return { region: r, appellation: '' };
  }
  for (const r of list) {
    const app = r.appellations.find(a => norm(a).length >= 4 && text.includes(` ${norm(a)} `));
    if (app) return { region: r, appellation: app };
  }
  return null;
}
