# State — 2026-10-16

## Now
- In daily use. Merged: wishlist (PR #2), add from links, Leclerc producer/region, batch-edit fix (PR #3), browser-translate opt-out, footer changelog.
- Freeze exception shipped 2026-10-16: "Past" filter + `last_drunk` date (PR #6), real delete from the Past view (PR #8), `last_drunk` editable in the edit form (PR #10, 2026-10-16.3; also fixes a trap where saving a Past wine from the form put a bottle back in stock). Toodledo 658993235 completed; backfill of dates for wines emptied before 2026-10-16 dropped on purpose (edit by hand if wanted).
- Leclerc wave 1 (order 10HGLRMJE9-1) is in the app and completed from the product pages. Test entries deleted.
- `scripts/add_wines.py` takes `--cafile` / `KELLERLOG_CA_FILE`: the NAS cert is signed by NASHOME LAN CA = `nas-infra-assets/tls/ca.crt`.
- Quirk seen 2026-10-16 (not fixed): `GET /wines/{id}` answers 404 for a wine at quantity 0; the list with `include_past=true` returns it. The UI works because it uses the list.
- Local oddity: `frontend/` has no `.dockerignore`, so a local `docker compose build` copies the host `node_modules` into the image and the build fails (CI builds from a clean checkout and is fine). Workaround: build from a clean copy. `.venv-backend` is broken (points to a removed path); make a Python 3.12 venv as in CLAUDE.md.

## Next
- Feature freeze until after the Lisbon trip (4-9 Nov).
- After the freeze: daily price check of wishlist links with the app's own shop parsers, alert through the Chat bridge. Re-assess first: Groly step C (price watch) is on hold, and both should share one price-watch service.

## Waiting on the user
- "Bourgogne Gamay Noir" (Bonot Père & Fils 2024, stock 0, in Past): the shop is Lidl. Paste the Lidl product URL (not the gv9l.st4.ch short link, which the browser refused) and use "fill from link", or type the fields by hand.
- Drop the leftover stash: `git stash drop` (it only holds a `package-lock.json` version bump).
- Close the leftover Chrome tabs from the earlier browser session.

## Open decisions
- Off-NAS backup: parked for the cross-project backup review (Toodledo 658941367 has the current script's details).
- Later: Web-watcher monitors for site-wide promos (no code); optional one-way "add to Groly list" once Groly has an API.
