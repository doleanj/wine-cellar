// EU e-label (ScanTrust) QR links: recognised in the scanner and resolved by the backend.
export function isElabelUrl(text) {
  try {
    const u = new URL((text || '').trim());
    return u.protocol === 'https:' && (u.hostname.endsWith('.st4.ch') || u.hostname === 'elabel.scantrust.com');
  } catch {
    return false;
  }
}

// Fields shown in the preview (label key suffix = elabel_f_<key>); elabel_url is always kept.
export const ELABEL_FIELDS = [
  'name', 'producer', 'grape', 'vintage', 'alcohol', 'type', 'sweetness', 'region', 'country',
  'volume_ml', 'bottled_by', 'description', 'ingredients', 'sulphites',
  'energy_kcal_100ml', 'sugar_g_100ml', 'carbs_g_100ml',
];

export const isFilled = v => v !== null && v !== undefined && v !== '' && v !== false;

// "Fill from link": e.leclerc product pages (/fp/...), read by the backend.
export function isLeclercUrl(text) {
  try {
    const u = new URL((text || '').trim());
    return u.protocol === 'https:' && (u.hostname === 'www.e.leclerc' || u.hostname === 'e.leclerc') && u.pathname.startsWith('/fp/');
  } catch {
    return false;
  }
}

// Fields a product page can fill in addition to the e-label ones.
export const LINK_FIELDS = [
  'pairings', 'profile_fruit', 'profile_personality', 'keep_until_years', 'serving_temp',
  'tasting', 'price', 'barcode', 'image_url',
];
export const PREVIEW_FIELDS = [...ELABEL_FIELDS, ...LINK_FIELDS];
