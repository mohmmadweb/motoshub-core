#!/bin/sh
# Renew the TLS certificate and reload nginx if it changed.
#
# Run from cron (see infra/prod/README.md). Certbot only acts when the
# certificate is within thirty days of expiry, so running this daily is both
# safe and the recommended cadence — it leaves room for a failed attempt to be
# retried long before anything expires.
#
# DNS-01 is used because Let's Encrypt validates HTTP-01 over port 80, and port
# 80 on this host belongs to another service that must not be touched.
set -eu

HERE=$(cd "$(dirname "$0")" && pwd)
CORE=$(cd "$HERE/../.." && pwd)
COMPOSE="docker compose -f $CORE/infra/docker-compose.yml -f $CORE/infra/prod/compose.prod.yml --env-file $CORE/infra/.env"

if [ ! -f "$HERE/dns-hooks/.env" ]; then
  echo "missing $HERE/dns-hooks/.env — the DNS hook cannot authenticate." >&2
  exit 1
fi

echo "── $(date '+%Y-%m-%d %H:%M:%S') renewal check ──"

# --deploy-hook runs only when a certificate was actually replaced, so nginx is
# reloaded on renewal and left alone on the ordinary no-op days.
docker run --rm \
  -v motoshub-core_letsencrypt:/etc/letsencrypt \
  -v "$HERE/dns-hooks:/hooks:ro" \
  --env-file "$HERE/dns-hooks/.env" \
  certbot/certbot:latest renew \
    --manual --preferred-challenges dns \
    --manual-auth-hook "python3 /hooks/cpanel_dns.py auth" \
    --manual-cleanup-hook "python3 /hooks/cpanel_dns.py cleanup" \
    --deploy-hook "touch /etc/letsencrypt/RENEWED" \
    --non-interactive

# The marker lives on the shared volume, which is how this script learns what
# happened inside the throwaway certbot container.
if docker run --rm -v motoshub-core_letsencrypt:/etc/letsencrypt \
     certbot/certbot:latest sh -c 'test -f /etc/letsencrypt/RENEWED && rm -f /etc/letsencrypt/RENEWED'; then
  echo "certificate renewed — reloading nginx"
  $COMPOSE exec -T web nginx -s reload
else
  echo "nothing to renew"
fi
