# Backlog

One line per item. Only the top 3 of the repo live in STATE.md "Next".
Line format: `title | (v:S/M/H, c:XS-XXL) | blocker | added YYYY-MM-DD | toodledo-id`
(v = value: S small, M medium, H high. c = cost, effort and context load: XS under 15 min, S under an hour, M a session, L several sessions or a design, XL a project, XXL several projects.)
Items with a date, or that need the user outside a session, also get a Toodledo task: put its id in the last field and let STATE cite the id, not the date.

## Quick wins (mobile-friendly)
Under about 15 minutes and doable from the phone: a decision, a note, a Toodledo edit, a read-only check, a reply.

- Review and merge PR #19 (stop tracking .env.prod) | (v:S, c:XS) | none | 2026-10-24 |

## Design
Needs an Opus design session (`/s.design`). Grouped by cost vs value; keep each item in the group that fits.

### High value, low cost
### High value, high cost
- Daily price check of wishlist links with the app's shop parsers, alert through the Chat bridge; share one price-watch service with Groly step C | (v:H, c:L) | freeze until after 9 Nov; Groly step C on hold | 2026-10-24 |
### Lower value

## Dev
Implementation items with a clear scope.

- "Open" button also in the wine detail view and on cards | (v:M, c:S) | freeze until after 9 Nov | 2026-10-24 | [659020964](https://www.toodledo.com/tasks/index.php#task_659020964)
- Auto target price from the buying price | (v:S, c:S) | freeze until after 9 Nov | 2026-10-24 | [659020964](https://www.toodledo.com/tasks/index.php#task_659020964)
- Auto-fill a wine from a link or barcode: decide what is left after the freeze | (v:M, c:M) | freeze until after 9 Nov | 2026-10-24 | [658932711](https://www.toodledo.com/tasks/index.php#task_658932711)
- `GET /wines/{id}` answers 404 for a wine at quantity 0 (the UI is unaffected: it uses the list) | (v:S, c:XS) | none | 2026-10-24 |
- Add `frontend/.dockerignore` so a local `docker compose build` stops copying the host `node_modules` | (v:S, c:XS) | none | 2026-10-24 |

## Other
- Off-NAS backup of `./data` (Mac pull, scripts built, not running) | (v:H, c:M) | NAS backup plan (nas-infra `docs/design-backups.md`) | 2026-10-24 | [658941367](https://www.toodledo.com/tasks/index.php#task_658941367)
- Web-watcher monitors for site-wide promos (no code) | (v:S, c:S) | none | 2026-10-24 |
- One-way "add to Groly list" | (v:S, c:M) | Groly needs an API | 2026-10-24 |
