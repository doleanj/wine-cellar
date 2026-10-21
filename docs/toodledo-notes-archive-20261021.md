# Toodledo notes archive, 2026-10-21

Verbatim copies of Toodledo task notes moved here when each note was reduced to purpose + repo + next action (house rule of 2026-10-21: no design, state or history in Toodledo notes).

## 658932711 · Wine Cellar: auto-fill from a link / barcode
```
2026-10-12 UPDATE 2 (commits e3961e9, 4c64047).
BUILT SINCE: (a) generic fallback reader backend/generic.py for any https product page (JSON-LD Product, then OpenGraph: name, brand, description, photo, price, EAN, guessed vintage/alcohol/colour); network safety in one helper main._fetch_page: generic sources only https port 443, no credentials, public hosts only, every redirect re-validated (max 3), HTML only, 4 MB cap, 1 request per click; tests with a mock transport. (b) Regions: new columns regions.extra + extra_source (migrated), shown as "More about this region" in the regions panel and wine detail. scripts/fetch_leclerc_region_texts.py (one-off, polite, texts saved OUTSIDE git in ~/workspace/wine-cellar-assets/leclerc-regions/regions_extra.json): 9 of 10 regions (all except savoie-jura: Leclerc's own Savoie pages show the Alsace paragraph, the script rejects it). scripts/load_region_extra.py uploads them (needs the admin password in the user's own terminal). (c) Branding: the old default title "KellerLog" in the NAS DB is renamed to "Wine Cellar" at startup (only the exact old default).
USER STEP: after the new image is live run on the Mac: KELLERLOG_ADMIN_USER=... KELLERLOG_ADMIN_PASSWORD=... python3 scripts/load_region_extra.py https://wine-cellar.nashome ../wine-cellar-assets/leclerc-regions   (CA: SSL_CERT_FILE=<ca.crt> if the private CA is not trusted by Python).
LEFT: purchases history table; barcode chain (local -> Leclerc by EAN -> Open Food Facts); optional Claude API extractor; Savoie/Jura text from another source; per-site parsers for more shops on demand.

==> what remaining todo ?
```

## 658941367 · Wine Cellar: off-NAS backup of the data folder (Mac pull, daily)
```
2026-10-13 BUILT (commit 3634116), NOT YET RUNNING. scripts/backup_pull_from_nas.sh pulls /volume1/docker/wine-cellar/data over SSH+rsync into ~/Backups/wine-cellar/<date>/ (dated snapshots, hard links, newest 30 kept). It skips the live wines.db (a SQLite file copied while the app writes can be corrupt); the database source is the app's own consistent copies in data/backups (startup/daily/manual; freshest <= 1 day old). Each run opens the newest wines-*.db with sqlite3 (integrity_check + wine count) and refuses/moves aside a bad snapshot; --check re-verifies. scripts/install_backup_agent.sh = launchd agent (daily 03:30, runs at wake, log ~/Library/Logs/wine-cellar-backup.log, notification on failure). Tested on a fake NAS folder (hard links, exclusion, pruning, corrupt/missing db refused, SSH failure message).
USER STEPS: 1) ssh-copy-id dolean_j@nashome (password typed once; key login did not work yet: Permission denied publickey). If DSM still refuses: home dir permissions (chmod 755 ~ on the NAS), ~/.ssh 700, authorized_keys 600. 2) scripts/backup_pull_from_nas.sh (first snapshot; check the 'integrity ok, N wines' line). 3) scripts/install_backup_agent.sh install, then launchctl kickstart to test. 4) RESTORE TEST once on a copy (README section 'Off-NAS backup'). 5) Optional: DEST in a Time Machine / cloud folder so the copy leaves the house; later Hyper Backup to USB/cloud as a second route.
Limits: Mac must be on at some point per day; copy is off the NAS but still at home unless DEST syncs elsewhere; app data only (not Container Manager config, secrets files or compose folders: see the infra design task 658935137).
```
Note 2026-10-21: the NAS-wide three-tier backup (nas-infra `docs/design-backups.md`, Toodledo 658970706) covers `/volume1/docker` snapshots and an encrypted cloud copy; whether this Mac pull is still needed is decided there.
