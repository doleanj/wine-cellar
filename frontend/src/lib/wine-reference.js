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
