#!/usr/bin/env bash
# Pull an off-NAS copy of the Wine Cellar data folder to this machine (versioned, verified).
#
#   scripts/backup_pull_from_nas.sh            # take a snapshot now
#   scripts/backup_pull_from_nas.sh --check    # only verify the newest snapshot
#
# What is copied: <REMOTE_DIR>/ (photos, the app's consistent database copies in backups/, ...) over SSH with
# rsync, EXCEPT the live wines.db (+ -wal/-shm): copying a SQLite file while the app writes can give a corrupt
# copy, so the app's own backups (startup, daily, manual: consistent by construction) are the database source.
# Each run makes a dated snapshot in DEST (unchanged files are hard links, so a snapshot costs only what
# changed), opens the newest database copy to check it, and keeps the newest KEEP snapshots.
#
# Needs key-based SSH to the NAS once:  ssh-copy-id dolean_j@nashome   (password typed by you, never stored).
# Settings (environment or ~/.config/wine-cellar-backup.env, KEY=value lines):
#   NAS_USER=dolean_j  NAS_HOST=nashome  REMOTE_DIR=/volume1/docker/wine-cellar/data
#   DEST=$HOME/Backups/wine-cellar  KEEP=30  MAX_DB_AGE_HOURS=36
# For tests: NAS_HOST="" makes REMOTE_DIR a local folder.
set -euo pipefail

CONF="${WINE_CELLAR_BACKUP_CONF:-$HOME/.config/wine-cellar-backup.env}"
[ -f "$CONF" ] && set -a && . "$CONF" && set +a
NAS_USER="${NAS_USER:-dolean_j}"
NAS_HOST="${NAS_HOST-nashome}"
REMOTE_DIR="${REMOTE_DIR:-/volume1/docker/wine-cellar/data}"
DEST="${DEST:-$HOME/Backups/wine-cellar}"
KEEP="${KEEP:-30}"
MAX_DB_AGE_HOURS="${MAX_DB_AGE_HOURS:-36}"
STAMP_RE='^[0-9]{8}-[0-9]{6}$'

log() { printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }
fail() { log "FAILED: $*"; command -v osascript >/dev/null 2>&1 && osascript -e "display notification \"$*\" with title \"Wine Cellar backup failed\"" >/dev/null 2>&1 || true; exit 1; }

snapshots() { { ls -1 "$DEST" 2>/dev/null || true; } | { grep -E "$STAMP_RE" || true; } | sort; }
newest_snapshot() { snapshots | tail -1; }

# Opens the newest consistent database copy inside a snapshot and reports what it holds.
verify_snapshot() {
  local snap="$1" db age_h result wines
  db="$(ls -1 "$snap"/backups/wines-*.db 2>/dev/null | sort | tail -1 || true)"
  [ -n "$db" ] || fail "no database copy (backups/wines-*.db) in $snap - has the app made a backup yet?"
  result="$(sqlite3 "file:$db?mode=ro" 'PRAGMA integrity_check;' 2>&1 | head -1)"
  [ "$result" = "ok" ] || fail "database copy $(basename "$db") is not intact: $result"
  wines="$(sqlite3 "file:$db?mode=ro" 'SELECT COUNT(*) FROM wine_library;' 2>&1)" || fail "cannot read wines from $(basename "$db")"
  age_h=$(( ( $(date +%s) - $(stat -f %m "$db" 2>/dev/null || stat -c %Y "$db") ) / 3600 ))
  log "database copy $(basename "$db"): integrity ok, $wines wines, ${age_h} h old"
  [ "$age_h" -le "$MAX_DB_AGE_HOURS" ] || log "WARNING: newest database copy is older than ${MAX_DB_AGE_HOURS} h - is the app's daily backup running?"
  log "photos: $(ls -1 "$snap"/images 2>/dev/null | wc -l | tr -d ' ') files, snapshot size: $(du -sh "$snap" | cut -f1)"
}

if [ "${1:-}" = "--check" ]; then
  snap="$(newest_snapshot)"; [ -n "$snap" ] || fail "no snapshot in $DEST"
  log "checking $DEST/$snap"; verify_snapshot "$DEST/$snap"; exit 0
fi

mkdir -p "$DEST"
LOCK="$DEST/.lock"
mkdir "$LOCK" 2>/dev/null || fail "another backup is running (remove $LOCK if it is stale)"
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

STAMP="$(date +%Y%m%d-%H%M%S)"
PARTIAL="$DEST/.partial-$STAMP"
PREV="$(newest_snapshot)"
if [ -n "$NAS_HOST" ]; then SRC="$NAS_USER@$NAS_HOST:$REMOTE_DIR/"; else SRC="$REMOTE_DIR/"; fi
RSYNC=(rsync -a --delete --exclude='/wines.db' --exclude='/wines.db-*' --exclude='/tmp/')
[ -n "$PREV" ] && RSYNC+=(--link-dest="$DEST/$PREV")
[ -n "$NAS_HOST" ] && RSYNC+=(-e "ssh -o BatchMode=yes -o ConnectTimeout=15")

log "pulling $SRC -> $DEST/$STAMP${PREV:+ (links to $PREV)}"
if ! "${RSYNC[@]}" "$SRC" "$PARTIAL/" 2>"$DEST/.rsync-error.log"; then
  mv "$PARTIAL" "$DEST/.failed-$STAMP" 2>/dev/null || true
  fail "rsync failed: $(tail -2 "$DEST/.rsync-error.log" | tr '\n' ' ') (SSH key set up? see the header of this script)"
fi
if ! (verify_snapshot "$PARTIAL"); then     # subshell: fail() exits it, the snapshot is kept aside as .failed-*
  mv "$PARTIAL" "$DEST/.failed-$STAMP" 2>/dev/null || true
  exit 1
fi
mv "$PARTIAL" "$DEST/$STAMP"
rm -f "$DEST/.rsync-error.log"

# keep the newest KEEP snapshots, drop failed leftovers older than a week
snapshots | awk -v keep="$KEEP" '{ a[NR] = $0 } END { for (i = 1; i <= NR - keep; i++) print a[i] }' | while read -r old; do rm -rf "${DEST:?}/$old"; log "pruned $old"; done
find "$DEST" -maxdepth 1 -name '.failed-*' -mtime +7 -exec rm -rf {} + 2>/dev/null || true
log "done: $DEST/$STAMP ($(snapshots | wc -l | tr -d ' ') snapshots kept)"
