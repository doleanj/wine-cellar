# State — 2026-10-16

## Now
- In daily use. Merged: wishlist (PR #2), add from links, Leclerc producer/region, batch-edit fix (PR #3), browser-translate opt-out, footer changelog.
- Freeze exception shipped 2026-10-16: "Past" filter + `last_drunk` date (PR #6), real delete from the Past view (PR #8). Delete of a stocked wine only empties the stock (it moves to Past). Live on the NAS (build 223a736).
- Leclerc wave 1 (order 10HGLRMJE9-1) is in the app and completed from the product pages (link, photo, barcode, tasting). Test entries (Morgon, Moulin a vent, Gris Pays d'Oc) deleted.
- `scripts/add_wines.py` takes `--cafile` / `KELLERLOG_CA_FILE`: the NAS cert is signed by NASHOME LAN CA = `nas-infra-assets/tls/ca.crt` (not the old CA in wine-cellar-assets/tls).

## Next
- Feature freeze until after the Lisbon trip (4-9 Nov).
- After the freeze: daily price check of wishlist links with the app's own shop parsers, alert through the Chat bridge. Re-assess first: Groly step C (price watch) is on hold, and both should share one price-watch service.
- Small leftovers (Toodledo 658993235): edit `last_drunk` in the edit form (API only today); wines emptied before 2026-10-16 have no date.

## Waiting on the user
- "Bourgogne Gamay Noir" (Bonot Père & Fils 2024, stock 0, in Past) has no data: not on e.leclerc, and its barcode field holds a short link (gv9l.st4.ch/orxPNvptCWaT) that the browser safety check refused to open. Give the shop or paste what that link shows, then fill it with "fill from link".
- `git stash` in this repo holds one leftover entry from a mistaken stash (probably the package-lock.json change): check with `git stash show`, then drop.
- Close the leftover Chrome tabs from the browser session.
- Toodledo 658993235 can be completed once the user is happy with the Past view.

## Open decisions
- Off-NAS backup: parked for the cross-project backup review (Toodledo 658941367 has the current script's details).
- Later: Web-watcher monitors for site-wide promos (no code); optional one-way "add to Groly list" once Groly has an API.
