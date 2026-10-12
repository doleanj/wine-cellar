#!/usr/bin/env bash
# Run the Wine Cellar off-NAS backup every day on this Mac (launchd user agent, no sudo).
#
#   scripts/install_backup_agent.sh install     # writes the agent and loads it (daily 03:30; runs at wake if the Mac slept)
#   scripts/install_backup_agent.sh status      # shows the agent and the last log lines
#   scripts/install_backup_agent.sh uninstall
#   scripts/install_backup_agent.sh plist       # only prints the agent file
#
# Log: ~/Library/Logs/wine-cellar-backup.log. Needs the SSH key login to the NAS first (see backup_pull_from_nas.sh).
set -euo pipefail
LABEL="com.doleanj.wine-cellar-backup"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG="$HOME/Library/Logs/wine-cellar-backup.log"
SCRIPT="$(cd "$(dirname "$0")" && pwd)/backup_pull_from_nas.sh"
HOUR="${BACKUP_HOUR:-3}"; MINUTE="${BACKUP_MINUTE:-30}"

plist() {
cat <<XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array><string>/bin/bash</string><string>$SCRIPT</string></array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>$HOUR</integer><key>Minute</key><integer>$MINUTE</integer></dict>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string></dict>
</dict>
</plist>
XML
}

case "${1:-}" in
  plist) plist ;;
  install)
    [ -x "$SCRIPT" ] || { echo "missing $SCRIPT" >&2; exit 1; }
    mkdir -p "$(dirname "$PLIST")" "$(dirname "$LOG")"
    plist > "$PLIST"; plutil -lint "$PLIST" >/dev/null
    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$PLIST"
    echo "installed: daily at $(printf '%02d:%02d' "$HOUR" "$MINUTE") (runs at wake if the Mac was asleep). Log: $LOG"
    echo "try it now:  launchctl kickstart -k gui/$(id -u)/$LABEL   (then: tail $LOG)"
    ;;
  status)
    launchctl print "gui/$(id -u)/$LABEL" 2>/dev/null | grep -E "state|last exit code|run interval|path" | head -5 || echo "not installed"
    echo "--- last log lines:"; tail -8 "$LOG" 2>/dev/null || echo "(no log yet)"
    ;;
  uninstall)
    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true; rm -f "$PLIST"; echo "removed (the backups in the destination folder are kept)" ;;
  *) sed -n '2,10p' "$0"; exit 1 ;;
esac
