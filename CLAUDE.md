# Wine Cellar (fork) — working notes for Claude

Fork of KrapfalAT/kellerlog: FastAPI backend (`backend/`, Python 3.12) + SvelteKit frontend (`frontend/`, nginx in prod). `origin` = doleanj/wine-cellar, `upstream` = KrapfalAT/kellerlog.
Current state and next steps: `docs/STATE.md` (read first). House rules: `~/.claude/CLAUDE.md`.

## Commands
- Backend: uv venv with **Python 3.12** (pinned deps do not build on 3.13), `pip install -r backend/requirements-dev.txt`, then `cd backend && pytest` (~7 s).
- Frontend: `cd frontend && npm install && npm run build` (or `npm run dev`).
- Local stack: `docker-compose.dev.yml`.

## Fork rules
- gh: **always `-R doleanj/wine-cellar`**. `gh pr create` once opened a PR on upstream by mistake.
- Changelog: every behaviour-changing PR adds an entry at the top of `frontend/src/lib/changelog.js` (UI `ChangelogModal.svelte`). Build info comes from CI args `APP_SHA`/`APP_BUILD_DATE` → `VITE_APP_*`.
- Region screenshots and texts live in `~/workspace/wine-cellar-assets/regions`, outside git on purpose (retailer content, personal use). Never commit them; load them with `scripts/load_region_assets.py`.
- Shop parsers: `backend/leclerc.py`, `lcdbb.py`, `elabel.py`, fallback `generic.py` (JSON-LD, then OpenGraph).

## Release and NAS
- Push to main → `.github/workflows/publish.yml` builds `ghcr.io/doleanj/wine-cellar-{backend,frontend}:edge` + a pre-release → Watchtower (host port 8095) redeploys.
- NAS: Container Manager project `wine-cellar`, data in `./data`, portal https://wine-cellar.nashome.
- Watchtower → Chat notifications for wine-cellar are deliberately off; don't propose them unprompted.
- Off-NAS backup: `scripts/backup_pull_from_nas.sh` + `install_backup_agent.sh` are built but not running; backups for all projects are parked for a dedicated review.
