# Database backups

The `backup` service dumps PostgreSQL to `/backups` (the `pgbackups` volume) on
boot and then every `BACKUP_INTERVAL_HOURS` (default 24), keeping
`BACKUP_KEEP_DAYS` days (default 7).

Dumps are written to a `.part` file and renamed on success, so a partial dump is
never mistaken for a good one, and a dump under 1 KB is quarantined as
`.suspect` rather than counted as a backup.

## List backups
```bash
docker compose -f infra/docker-compose.yml exec backup ls -lh /backups
```

## Restore
```bash
# copy the dump out of the volume, then replay it into the db container
docker compose -f infra/docker-compose.yml exec backup \
  sh -c 'gunzip -c /backups/motoshub-YYYYMMDD-HHMMSS.sql.gz' \
  | docker compose -f infra/docker-compose.yml exec -T db \
      psql -U motoshub -d motoshub_core
```

## Copy a dump to the host
```bash
docker compose -f infra/docker-compose.yml cp \
  backup:/backups/motoshub-YYYYMMDD-HHMMSS.sql.gz ./
```
