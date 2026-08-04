# HTTPS with Let's Encrypt

The stack serves plain HTTP by default so it runs anywhere. To enable TLS you
need a domain whose A record points at this host.

## 1. Point the domain here, then issue a certificate

```bash
export DOMAIN=motoshub.example.ir
export EMAIL=you@example.ir

docker run --rm \
  -v motoshub-core_letsencrypt:/etc/letsencrypt \
  -p 80:80 \
  certbot/certbot certonly --standalone \
    -d "$DOMAIN" --email "$EMAIL" --agree-tos --no-eff-email
```

Port 80 must be free while certbot runs (stop the `web` service first if it is
bound there).

## 2. Bring the stack up with the TLS overlay

```bash
DOMAIN=$DOMAIN docker compose \
  -f infra/docker-compose.yml \
  -f infra/tls/compose.tls.yml up -d
```

The overlay mounts the certificates into the `web` container and swaps in an
nginx config that redirects HTTP→HTTPS, enables HTTP/2, and keeps the existing
`/api`, `/ws`, `/static`, `/media` proxying.

## 3. Renewal

Certificates last 90 days. Renew from cron on the host:

```cron
0 3 * * 1 docker run --rm -v motoshub-core_letsencrypt:/etc/letsencrypt \
  certbot/certbot renew --quiet && \
  docker compose -f /path/to/infra/docker-compose.yml \
  -f /path/to/infra/tls/compose.tls.yml exec web nginx -s reload
```

## Also set for production

`SECURE_SSL_REDIRECT` and HSTS are already on in `config.settings.production`.
Point the API at that settings module and give it real secrets — it refuses to
boot with the development ones.
