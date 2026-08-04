#!/bin/sh
# Nightly PostgreSQL dump with retention. Runs inside the `backup` container.
set -eu

STAMP=$(date +%Y%m%d-%H%M%S)
OUT="/backups/motoshub-${STAMP}.sql.gz"
KEEP_DAYS="${BACKUP_KEEP_DAYS:-7}"

echo "[$(date -Iseconds)] dumping ${POSTGRES_DB} → ${OUT}"
pg_dump --host="${POSTGRES_HOST:-db}" --username="${POSTGRES_USER}" \
        --dbname="${POSTGRES_DB}" --no-owner --no-acl \
  | gzip -9 > "${OUT}.part"
mv "${OUT}.part" "${OUT}"          # atomic: a partial dump never looks complete

# Fail loudly if the dump is suspiciously small (empty/failed dump).
SIZE=$(stat -c %s "${OUT}")
if [ "${SIZE}" -lt 1024 ]; then
  echo "[ERROR] dump is only ${SIZE} bytes — treating as failed" >&2
  mv "${OUT}" "${OUT}.suspect"
  exit 1
fi

echo "[$(date -Iseconds)] ok (${SIZE} bytes); pruning older than ${KEEP_DAYS}d"
find /backups -name 'motoshub-*.sql.gz' -mtime "+${KEEP_DAYS}" -print -delete
