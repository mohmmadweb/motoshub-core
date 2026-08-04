#!/bin/sh
# Take one dump at boot (so a fresh deploy always has a restore point), then
# repeat every BACKUP_INTERVAL_HOURS. No cron daemon needed in the image.
set -eu
INTERVAL_HOURS="${BACKUP_INTERVAL_HOURS:-24}"

/usr/local/bin/backup.sh || echo "[WARN] initial backup failed; will retry"
while true; do
  sleep "$((INTERVAL_HOURS * 3600))"
  /usr/local/bin/backup.sh || echo "[WARN] backup failed; will retry next cycle"
done
