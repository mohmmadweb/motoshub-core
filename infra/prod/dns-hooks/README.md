# DNS-01 hook for certbot

`cpanel_dns.py` publishes and withdraws the `_acme-challenge` TXT record that
Let's Encrypt asks for, through the cPanel API that hosts the zone.

## Why DNS-01 rather than HTTP-01

HTTP-01 is validated over port 80. Port 80 on this machine belongs to another
service that must not be disturbed, so that challenge is unavailable. DNS-01
needs no inbound port at all — and because the zone has an API, the record can
be published automatically, which is what makes renewal unattended.

## Configuration

Copy the example and fill it in; the file is gitignored because it holds a
panel password.

```
CPANEL_HOST=185.88.177.182     # address to dial
CPANEL_SNI=cpanel.7ho.st       # name the panel's certificate covers
CPANEL_USER=...
CPANEL_PASS=...
CPANEL_ZONE=shub.ir
DNS_PROPAGATION_SECONDS=45
```

`CPANEL_HOST` and `CPANEL_SNI` are separate on purpose. The panel answers on a
bare IP, which no certificate can cover, so the socket connects to the address
while SNI and hostname verification use the name the certificate is issued for.
The connection is therefore authenticated, not merely encrypted — verification
is never disabled.

## Manual use

```bash
docker run --rm \
  -v motoshub-core_letsencrypt:/etc/letsencrypt \
  -v "$PWD/infra/prod/dns-hooks:/hooks:ro" \
  --env-file infra/prod/dns-hooks/.env \
  certbot/certbot:latest certonly \
    --manual --preferred-challenges dns \
    --manual-auth-hook "python3 /hooks/cpanel_dns.py auth" \
    --manual-cleanup-hook "python3 /hooks/cpanel_dns.py cleanup" \
    -d prod.shub.ir --agree-tos --non-interactive \
    --register-unsafely-without-email --key-type ecdsa
```

Add `--dry-run` first. Let's Encrypt rate-limits failed attempts against the
real endpoint, and the staging run catches a broken hook for free — it is how
the missing `curl` in the certbot image was found.

## Renewal

`infra/prod/renew-cert.sh` runs daily from cron. Certbot does nothing until the
certificate is within thirty days of expiry, so a daily run is cheap and leaves
weeks of room for a failed attempt to be retried.

    17 3 * * * /path/to/infra/prod/renew-cert.sh >> .../renew.log 2>&1

nginx is reloaded only when a certificate was actually replaced, via certbot's
`--deploy-hook`.
