// Reference data for food pairings and taste profile.
// Pairings are stored on the wine as a comma-separated string of keys (see PAIRINGS);
// any token that is not a known key is kept as free text, so older entries still work.

// Categories follow the "Accords parfaits" table; icons are generic emoji (own choice).
export const PAIRINGS = [
  { key: 'aperitif',          icon: '🥂', fr: 'Apéritif',            en: 'Aperitif',            de: 'Aperitif' },
  { key: 'canard',            icon: '🦆', fr: 'Canard',              en: 'Duck',                de: 'Ente' },
  { key: 'charcuterie',       icon: '🥓', fr: 'Charcuterie',         en: 'Charcuterie',         de: 'Aufschnitt' },
  { key: 'cuisine-exotique',  icon: '🍛', fr: 'Cuisine exotique',    en: 'Exotic cuisine',      de: 'Exotische Küche' },
  { key: 'desserts',          icon: '🍰', fr: 'Desserts',            en: 'Desserts',            de: 'Desserts' },
  { key: 'foie-gras',         icon: '🪿', fr: 'Foie gras',           en: 'Foie gras',           de: 'Foie gras' },
  { key: 'fromage-pate-dure', icon: '🧀', fr: 'Fromage pâte dure',   en: 'Hard cheese',         de: 'Hartkäse' },
  { key: 'fromage-pate-molle',icon: '🧀', fr: 'Fromage pâte molle',  en: 'Soft cheese',         de: 'Weichkäse' },
  { key: 'fromage-persille',  icon: '🧀', fr: 'Fromage persillé',    en: 'Blue cheese',         de: 'Blauschimmelkäse' },
  { key: 'fromage',           icon: '🧀', fr: 'Fromage',             en: 'Cheese',              de: 'Käse' },
  { key: 'fruits-de-mer',     icon: '🦞', fr: 'Fruits de mer',       en: 'Seafood',             de: 'Meeresfrüchte' },
  { key: 'gibiers',           icon: '🦌', fr: 'Gibiers',             en: 'Game',                de: 'Wild' },
  { key: 'grillades',         icon: '🍢', fr: 'Grillades',           en: 'Grilled dishes',      de: 'Gegrilltes' },
  { key: 'legumes-verts',     icon: '🥦', fr: 'Légumes verts',       en: 'Green vegetables',    de: 'Grünes Gemüse' },
  { key: 'plats-en-sauce',    icon: '🍲', fr: 'Plats en sauce',      en: 'Dishes in sauce',     de: 'Gerichte mit Sauce' },
  { key: 'poisson',           icon: '🐟', fr: 'Poisson',             en: 'Fish',                de: 'Fisch' },
  { key: 'roti',              icon: '🍖', fr: 'Rôti',                en: 'Roast',               de: 'Braten' },
  { key: 'salade',            icon: '🥗', fr: 'Salade',              en: 'Salad',               de: 'Salat' },
  { key: 'viande-rouge',      icon: '🥩', fr: 'Viande rouge',        en: 'Red meat',            de: 'Rotes Fleisch' },
  { key: 'viande-blanche',    icon: '🍗', fr: 'Viande blanche',      en: 'White meat',          de: 'Helles Fleisch' },
  { key: 'volaille',          icon: '🐔', fr: 'Volaille',            en: 'Poultry',             de: 'Geflügel' },
];

const BY_KEY = Object.fromEntries(PAIRINGS.map(p => [p.key, p]));

export function splitPairings(str) {
  return (str || '').split(',').map(s => s.trim()).filter(Boolean);
}

export function joinPairings(tokens) {
  return tokens.join(',');
}

/** Tokens of a pairings string as display items: known keys get icon + label, free text a generic icon. */
export function pairingItems(str, language = 'en') {
  return splitPairings(str).map(tok => {
    const p = BY_KEY[tok];
    if (!p) return { token: tok, known: false, icon: '🍽', label: tok, title: tok };
    const label = p[language] || p.en;
    return { token: tok, known: true, icon: p.icon, label, title: p.fr };
  });
}

// "Macaron du goût": two axes scored 1..5, plus sweetness.
export const PROFILE_MIN = 1;
export const PROFILE_MAX = 5;
export const SWEETNESS = ['sec', 'doux', 'moelleux'];

// ── Pairing finder ────────────────────────────────────────────────────────────────────────────────
// Wine types that usually go with each category: used when a bottle has no pairing data yet.
export const PAIRING_TYPES = {
  'aperitif': ['sparkling', 'white', 'rosé'], 'canard': ['red'], 'charcuterie': ['red', 'rosé'],
  'cuisine-exotique': ['white', 'rosé'], 'desserts': ['dessert', 'sparkling'], 'foie-gras': ['dessert', 'white'],
  'fromage-pate-dure': ['red', 'white'], 'fromage-pate-molle': ['white', 'red', 'sparkling'],
  'fromage-persille': ['dessert', 'red'], 'fromage': ['red', 'white'], 'fruits-de-mer': ['white', 'sparkling'],
  'gibiers': ['red'], 'grillades': ['red', 'rosé'], 'legumes-verts': ['white', 'rosé'],
  'plats-en-sauce': ['red', 'white'], 'poisson': ['white', 'sparkling', 'rosé'], 'roti': ['red'],
  'salade': ['white', 'rosé'], 'viande-rouge': ['red'], 'viande-blanche': ['white', 'rosé', 'red'],
  'volaille': ['white', 'red'],
};

/** 'young' | 'ready' | 'late' | 'past' | null - same rule as the wine card (vintage + rule offsets). */
export function drinkStatus(wine, rules, year = new Date().getFullYear()) {
  if (!wine.vintage || !wine.type || !rules?.length) return null;
  const rule = rules.find(r =>
    (!r.wine_type || r.wine_type === wine.type) &&
    (!r.grape || r.grape.toLowerCase() === (wine.grape || '').toLowerCase()));
  if (!rule) return null;
  const from = wine.vintage + rule.from_offset, to = wine.vintage + rule.to_offset;
  if (year < from) return 'young';
  if (year <= to) return 'ready';
  if (year <= to + 3) return 'late';
  return 'past';
}

/**
 * Rank a wine for the selected dish categories. Returns null when it does not fit at all.
 * explicit pairing match: +10 each; wine type fits a selected dish: +2 (alone: +3 "suggested by type");
 * drink window: ready +2, young/late -1, past -3; favorite +1.
 */
export function scoreWine(wine, selected, rules) {
  const have = new Set(splitPairings(wine.pairings));
  const matched = selected.filter(k => have.has(k));
  const typeHit = selected.some(k => (PAIRING_TYPES[k] || []).includes(wine.type));
  const status = drinkStatus(wine, rules);
  let score;
  if (matched.length) score = matched.length * 10 + (typeHit ? 2 : 0);
  else if (typeHit) score = 3;
  else return null;
  if (status === 'ready') score += 2;
  else if (status === 'young' || status === 'late') score -= 1;
  else if (status === 'past') score -= 3;
  if (wine.favorite) score += 1;
  return { wine, score, matched, status, fallback: matched.length === 0 };
}
