# State — 2026-10-24

## Now
- In daily use. Merged: wishlist (PR #2), add from links, Leclerc producer/region, batch-edit fix (PR #3), browser-translate opt-out, footer changelog. "Past" filter + `last_drunk` date (PR #6, #8, #10; 2026-10-16). Leclerc wave 1 is in the app.
- Freeze exception 2026-10-20 (small, asked by the user), merged and deployed: price on each pairing-menu row (PR #12) and an "Open" button on each row with confirm sheet, 10 s Undo and optional rating/tag/note (PR #13, version 2026-10-20). It uses the existing `PUT /wines/{id}`; the backend sets `last_drunk` when stock goes down. Follow-ups, tested on the phone and deployed: single-select Open tags with a "Saved as:" preview (PR #15); "Past" = every wine ever drunk, Past + Wishlist combine, new "To rate" filter, more header padding under 600 px (PR #16, version 2026-10-20.3).
- 2026-10-24: `docs/BACKLOG.md` and `docs/ADR.md` created from the dev-system templates (PR #20, open, docs only). This file is the last commit of that PR. PR #19 (stop tracking `.env.prod`) is still open.
- `scripts/add_wines.py` takes `--cafile` / `KELLERLOG_CA_FILE`: the NAS cert is signed by NASHOME LAN CA = `nas-infra-assets/tls/ca.crt`.
- Quirks (not fixed, both in BACKLOG Dev): `GET /wines/{id}` answers 404 for a wine at quantity 0 (the UI uses the list, so it works); `frontend/` has no `.dockerignore`, so a local `docker compose build` fails on the host `node_modules` (CI is fine; build from a clean copy). `.venv-backend` is broken: make a Python 3.12 venv as in CLAUDE.md.
- Browser testing quirk 2026-10-20: the Chrome extension session showed blank pages for a local dev instance (cause unknown, not the app); verify on the phone.

## Next
1. Feature freeze until after the Lisbon trip (4-9 Nov), apart from the exception above.
2. [659020964](https://www.toodledo.com/tasks/index.php#task_659020964) leftovers: "Open" button also in the detail view and on cards; auto target price from the buying price.
3. After the freeze [opus]: daily price check of wishlist links with the app's own shop parsers, alert through the Chat bridge. Re-assess first: Groly step C (price watch) is on hold, and both should share one price-watch service.
Everything else: `docs/BACKLOG.md`.

## Waiting on the user
- Review and merge PR #19 and PR #20 (a merge to main redeploys the app through Watchtower).

## Open decisions
- Off-NAS backup: parked for the NAS backup plan (nas-infra `docs/design-backups.md`); the Mac-pull script's details are in `docs/toodledo-notes-archive-20261021.md` (Toodledo [658941367](https://www.toodledo.com/tasks/index.php#task_658941367)). ADR-0002.
- Later: Web-watcher monitors for site-wide promos (no code); optional one-way "add to Groly list" once Groly has an API.
