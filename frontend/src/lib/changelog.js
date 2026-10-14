// What changed in Wine Cellar, shown from the version link in the footer (newest first).
// Convention: every PR that changes behaviour adds an entry here in the same PR, at the top.
// `version` is the release date (add ".2", ".3" for further entries the same day). Use status
// 'planned' or 'in-progress' to track something that spans several PRs; drop it once shipped.
export const CHANGELOG = [
  {
    version: '2026-10-14',
    items: ['Footer shows the current version and build; click it to open this changelog']
  },
  {
    version: '2026-10-13',
    items: ['Off-NAS backup: daily pull of the data folder to a Mac (versioned, verified)']
  },
  {
    version: '2026-10-12.3',
    items: [
      'Fill a wine from a product link: e.leclerc, La Compagnie des Bonnes Bouteilles, and basic data from any other shop',
      'Compare current and new values before taking over e-label or product page data; info overlay lists supported sites',
      'New fields: keep until, serving temperature, purchase date, tasting notes',
      'Region extra texts; fix a startup crash on existing databases'
    ]
  },
  {
    version: '2026-10-12.2',
    items: [
      'Scan a bottle\'s EU e-label (QR) to fill its details',
      'Pairing finder: pick dishes, get your in-stock bottles ranked',
      'Automatic database backups (at startup and daily) with list, back up now and download'
    ]
  },
  {
    version: '2026-10-12',
    items: [
      'Origin map: larger, select overlapping zones, stays open when opening a wine',
      'Barcode scanner no longer hidden behind the quick-add sheet; HTTPS requirement explained',
      'Each new build publishes a GitHub release with its notes',
      'English UI strings and a readable logout button'
    ]
  },
  {
    version: '2026-10-11',
    items: [
      'Rebranded from KellerLog to Wine Cellar (personal fork)',
      'French wine regions with map and text linking, appellation outlines and a regions panel',
      'Per-wine link, taste profile and sweetness; pairing picker and taste badge',
      'Favorite heart button and Favorites filter',
      'Bulk-add wines from a JSON file (script)',
      'Fix edit form and detail panel clipping on small screens'
    ]
  },
  {
    version: '2026-07-06',
    items: ['Based on KellerLog v1.5.0 (dashboard views, accessibility overhaul, backend hardening); earlier versions are on GitHub releases']
  }
];

// Newest entry that has shipped: the version shown in the footer.
export const currentEntry = CHANGELOG.find(e => !e.status || e.status === 'released');
