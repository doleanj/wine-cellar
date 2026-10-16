# State — 2026-10-16

## Now
- In daily use. Merged: wishlist (`wishlist`/`target_price`, "Bought" flow, PR #2), add from links, Leclerc producer/region, batch-edit fix, README tags (PR #3), browser-translate opt-out, footer changelog.

## Next
- Feature freeze until after the Lisbon trip (4-9 Nov), except the "Past" view + `last_drunk` date (user exception 2026-10-16, PR feature/last-drunk, not merged yet).
- Roadmap after the freeze: daily price check of wishlist links with the app's own shop parsers, alert through the Chat bridge. Re-assess first: Groly step C (price watch) is on hold, and both should share one price-watch service.

## Waiting on the user
- Run the Leclerc order load on the NAS app (order 10HGLRMJE9-1, 6 bottles, file in wine-cellar-assets/orders/): dry-run first, then real. Wave 2 is already on the wishlist.
- Review/merge the last-drunk PR.

## Open decisions
- Off-NAS backup: parked for the cross-project backup review (Toodledo 658941367 has the current script's details).
- Later: Web-watcher monitors for site-wide promos (no code); optional one-way "add to Groly list" once Groly has an API.
