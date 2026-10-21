# State — 2026-10-20

## Now
- In daily use. Merged: wishlist (PR #2), add from links, Leclerc producer/region, batch-edit fix (PR #3), browser-translate opt-out, footer changelog.
- "Past" filter + `last_drunk` date (PR #6, #8, #10; 2026-10-16). Leclerc wave 1 is in the app.
- Freeze exception 2026-10-20 (small, asked by the user), merged and deployed: price on each pairing-menu row (PR #12) and an "Open" button on each row with confirm sheet, 10 s Undo and optional rating/tag/note (PR #13, version 2026-10-20). It uses the existing `PUT /wines/{id}`; the backend sets `last_drunk` when stock goes down. Follow-ups, all tested on the phone by the user and deployed: Open rate sheet tags are single-select with a "Saved as:" preview (PR #15, 2026-10-20.2); "Past" = every wine ever drunk (`last_drunk` set or no bottle left), so a restocked or re-wished wine stays in it, and Past + Wishlist now combine; new "To rate" filter = drunk with no star rating (notes do not count); more top padding under 600 px so the header no longer hides the first filter row (PR #16, 2026-10-20.3).
- `scripts/add_wines.py` takes `--cafile` / `KELLERLOG_CA_FILE`: the NAS cert is signed by NASHOME LAN CA = `nas-infra-assets/tls/ca.crt`.
- Quirk (not fixed): `GET /wines/{id}` answers 404 for a wine at quantity 0; the list with `include_past=true` returns it. The UI works because it uses the list.
- Browser testing quirk 2026-10-20: the Chrome extension session showed blank pages for a local dev instance (cause unknown, not the app); #15 and #16 were verified on the phone instead.
- Local oddity: `frontend/` has no `.dockerignore`, so a local `docker compose build` copies the host `node_modules` into the image and the build fails (CI builds from a clean checkout and is fine). Workaround: build from a clean copy. `.venv-backend` is broken; make a Python 3.12 venv as in CLAUDE.md.

## Next
- Feature freeze until after the Lisbon trip (4-9 Nov), apart from the exception above.
- [659020964](https://www.toodledo.com/tasks/index.php#task_659020964) leftovers: "Open" button also in the detail view and on cards; auto target price from the buying price.
- After the freeze: daily price check of wishlist links with the app's own shop parsers, alert through the Chat bridge. Re-assess first: Groly step C (price watch) is on hold, and both should share one price-watch service.

## Waiting on the user
- Nothing.

## Open decisions
- Off-NAS backup: parked for the NAS backup plan (nas-infra `docs/design-backups.md`); the Mac-pull script's details moved from Toodledo [658941367](https://www.toodledo.com/tasks/index.php#task_658941367) to `docs/toodledo-notes-archive-20261021.md`.
- Later: Web-watcher monitors for site-wide promos (no code); optional one-way "add to Groly list" once Groly has an API.
