# Deploying to prod.shub.ir

This overlay runs the whole platform on **dedicated host ports** — 9080 (HTTP)
and 9443 (HTTPS). It publishes nothing else: Postgres, Redis, the Celery worker
and the Django API have no host bindings at all. Ports 80 and 443 are left
alone, so this stack can share a machine with unrelated services without ever
competing with them.

## 1. Configure

```bash
cp infra/.env.prod.shub.ir.example infra/.env
python -c "import secrets;print(secrets.token_urlsafe(64))"   # SECRET_KEY
python -c "import secrets;print(secrets.token_urlsafe(48))"   # OW_PASSWORD_PEPPER
```

`infra/.env` is gitignored — secrets never enter the repository.

`OW_PASSWORD_PEPPER` must be **identical** to the PHP backend's, otherwise
tokens issued by one side will not validate on the other.

## 2. DNS

```
prod.shub.ir.   A   <server public IP>
```

Because the site does not use port 443, the URL carries the port:
`http://prod.shub.ir:9080` (and `https://prod.shub.ir:9443` once TLS is on).

## 3. Deploy

```bash
docker compose -f infra/docker-compose.yml -f infra/prod/compose.prod.yml \
  --env-file infra/.env up -d --build
```

Migrations, RBAC seeding and `collectstatic` run automatically on API start.

Verify:

```bash
curl -H "Host: prod.shub.ir" http://127.0.0.1:9080/api/v1/health
# {"data":{"status":"ok","db":true},...}
```

## 4. TLS

Live: **https://prod.shub.ir:9443** — Let's Encrypt, renewed automatically.

Certificates are obtained over **DNS-01**, not HTTP-01. HTTP-01 validates on
port 80, which on this host belongs to another service that must not be
touched; DNS-01 needs no inbound port at all. The zone lives on cPanel and has
an API, so `infra/prod/dns-hooks/cpanel_dns.py` publishes the challenge record
itself — that is what makes renewal unattended rather than a manual chore every
ninety days.

Setup on a fresh deployment:

1. `cp infra/prod/dns-hooks/.env.example infra/prod/dns-hooks/.env` and fill in
   the panel credentials (gitignored).
2. Issue the certificate — see [dns-hooks/README.md](dns-hooks/README.md).
   Always `--dry-run` first; failures against the real endpoint count against a
   rate limit.
3. Set `SECURE_SSL_REDIRECT=True` in `infra/.env`. Secure cookies and HSTS
   follow the same switch, so leaving it off keeps the site usable over plain
   HTTP but unprotected.
4. `docker compose ... up -d --force-recreate web api`
5. Add the daily renewal to cron:

       17 3 * * * /path/to/infra/prod/renew-cert.sh >> .../renew.log 2>&1

nginx serves the config as a template so `${DOMAIN}` and `${HTTPS_PORT}` are
filled in at start. `NGINX_ENVSUBST_FILTER` restricts substitution to those
two — without it envsubst would also consume nginx's own `$host`, `$scheme`
and `$request_uri`.

Port 80 on the container redirects to HTTPS, carrying the port through, since
this deployment does not own 443 on the host. The ACME webroot path stays
reachable so a webroot challenge remains possible without editing config under
time pressure.

## Backups

The `backup` service dumps Postgres every `BACKUP_INTERVAL_HOURS` into the
`pgbackups` volume and prunes past `BACKUP_KEEP_DAYS`. See
[../backup/README.md](../backup/README.md) for restoring one.

## Notes

* nginx resolves the API container through Docker's embedded DNS on every
  request. A static `upstream` would be resolved once at startup, so recreating
  the API container would 502 every request until nginx restarted too.
* `ALLOWED_HOSTS` contains the domain, loopback (for health checks) and the
  server IP. Any other `Host` header gets a 400 — that is Django rejecting
  host-header spoofing, not a misconfiguration.
