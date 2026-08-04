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

The stack starts with `SECURE_SSL_REDIRECT=False` — plain HTTP, so the site is
reachable the moment it boots. Turn HTTPS on as soon as a certificate exists;
until then, logins travel unencrypted.

Let's Encrypt's HTTP-01 challenge validates over port **80**, which this stack
deliberately does not own. Two ways forward:

**DNS-01 (no port 80 needed).** Works regardless of what else runs on the box:

```bash
certbot certonly --manual --preferred-challenges dns -d prod.shub.ir
# add the _acme-challenge TXT record it prints, then:
docker cp /etc/letsencrypt/live/prod.shub.ir/. motoshub-core-web-1:/etc/letsencrypt/live/prod.shub.ir/
```

Renewal is manual unless your DNS provider has a certbot plugin
(`--dns-cloudflare`, `--dns-route53`, …), in which case renewal is automatic.

**HTTP-01**, if and only if port 80 on this host is free or already terminated
by a proxy you control: point that proxy's `/.well-known/acme-challenge/` at
`http://127.0.0.1:9080` — nginx here already serves that path from
`/var/www/certbot`.

Once the certificate is in place:

1. Set `SECURE_SSL_REDIRECT=True` in `infra/.env`.
2. Add a `listen 443 ssl;` server block to `nginx.prod.conf` pointing at
   `/etc/letsencrypt/live/${DOMAIN}/fullchain.pem` and `privkey.pem`
   (`infra/tls/nginx.tls.conf` has a ready-made one to copy).
3. `docker compose ... up -d --force-recreate web api`.

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
