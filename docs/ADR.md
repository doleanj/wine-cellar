# ADR

Append-only record of decisions and lessons. Newest last, numbered. Two kinds of entry.

## ADR-NNNN · YYYY-MM-DD · decision · <title>
What was decided, by whom, why, what it replaces. Status: accepted / superseded by ADR-NNNN.

## ADR-NNNN · YYYY-MM-DD · lesson · <title>
- Incident: what happened (facts only, no secret values).
- Cause: why.
- Rule changed: what we do differently now.
- Promoted to: the CLAUDE.md line it became, or "none (ADR only)".

## ADR-0001 · 2026-10-20 · decision · Feature freeze until after the Lisbon trip
No new features until after the trip (4-9 Nov); only small exceptions asked for by the user (2026-10-20: price on pairing rows, "Open" button, Past / To rate filters). Recorded from STATE.md. Status: accepted.

## ADR-0002 · 2026-10-20 · decision · Off-NAS backup is parked for the NAS backup plan
The Mac-pull scripts (`scripts/backup_pull_from_nas.sh`, `install_backup_agent.sh`) are built but not running; backups for all projects are reviewed together in nas-infra `docs/design-backups.md`. Details moved from Toodledo [658941367](https://www.toodledo.com/tasks/index.php#task_658941367) to `docs/toodledo-notes-archive-20261021.md`. Status: accepted.
