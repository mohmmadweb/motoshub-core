#!/usr/bin/env python3
"""certbot DNS-01 hook: publish and withdraw _acme-challenge TXT via cPanel.

Let's Encrypt's HTTP-01 challenge validates over port 80, which on this machine
belongs to another service that must not be touched. DNS-01 avoids port 80
entirely, and because the zone is hosted on cPanel with an API, the record can
be published automatically — which is what makes renewal unattended rather
than a manual chore every ninety days.

Written against the standard library alone: the certbot image ships Python but
no curl, and adding packages to it would make renewal depend on a build step.

TLS is verified properly. The panel's certificate covers a wildcard host rather
than the bare IP, so the socket connects to the IP while SNI and hostname
verification both use that covered name — the connection is authenticated, not
merely encrypted.

Environment:
    CPANEL_HOST  IP or hostname to connect to
    CPANEL_SNI   name the panel's certificate is issued for
    CPANEL_USER, CPANEL_PASS
    CPANEL_ZONE  e.g. shub.ir
    DNS_PROPAGATION_SECONDS  wait after publishing (default 45)
"""
import base64
import http.client
import json
import os
import socket
import ssl
import sys
import time
import urllib.parse

HOST = os.environ["CPANEL_HOST"]
SNI = os.environ["CPANEL_SNI"]
USER = os.environ["CPANEL_USER"]
PASS = os.environ["CPANEL_PASS"]
ZONE = os.environ["CPANEL_ZONE"]
WAIT = int(os.environ.get("DNS_PROPAGATION_SECONDS", "45"))
PORT = int(os.environ.get("CPANEL_PORT", "2083"))


def _call(path: str, params: dict) -> dict:
    ctx = ssl.create_default_context()          # verification stays on
    # Dial the address we were given, but complete the handshake under the name
    # the certificate is issued for: SNI and hostname verification both use it,
    # so the connection is authenticated even though CPANEL_HOST is a bare IP
    # that no certificate could ever cover.
    raw = socket.create_connection((HOST, PORT), timeout=60)
    tls = ctx.wrap_socket(raw, server_hostname=SNI)

    conn = http.client.HTTPSConnection(SNI, PORT, context=ctx, timeout=60)
    conn.sock = tls                             # hand over the verified socket
    token = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
    query = urllib.parse.urlencode(params)
    conn.request(
        "GET", f"{path}?{query}",
        headers={"Authorization": f"Basic {token}", "Host": SNI},
    )
    body = conn.getresponse().read().decode("utf-8", "replace")
    conn.close()
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise SystemExit(f"cPanel returned a non-JSON response: {body[:200]}")


def _zone() -> dict:
    res = _call("/execute/DNS/parse_zone", {"zone": ZONE})
    if res.get("status") != 1:
        raise SystemExit(f"reading the zone failed: {res.get('errors')}")
    return res


def _serial(zone: dict) -> str:
    """The zone's current serial, which mass_edit_zone requires.

    It is the third field of the SOA's data (primary, admin, serial, ...) and is
    base64-encoded like every other value cPanel returns. Sending back the
    serial we just read is what stops one edit silently overwriting another.
    """
    for row in zone["data"]:
        if row.get("record_type") == "SOA":
            parts = [base64.b64decode(x).decode("utf-8", "replace") for x in row["data_b64"]]
            if len(parts) < 3:
                raise SystemExit(f"unexpected SOA layout: {parts}")
            return parts[2]
    raise SystemExit("the zone has no SOA record")


def _record_name(domain: str) -> str:
    """prod.shub.ir → _acme-challenge.prod ; shub.ir → _acme-challenge"""
    sub = domain[: -len(ZONE)].rstrip(".") if domain.endswith(ZONE) else domain
    return f"_acme-challenge.{sub}" if sub else "_acme-challenge"


def publish(domain: str, value: str) -> None:
    name = _record_name(domain)
    add = json.dumps({"dname": name, "ttl": 60, "record_type": "TXT", "data": [value]})
    res = _call("/execute/DNS/mass_edit_zone", {"zone": ZONE, "serial": _serial(_zone()), "add": add})
    if res.get("status") != 1:
        raise SystemExit(f"publishing {name} failed: {res.get('errors')}")
    print(f"published TXT {name}.{ZONE}", flush=True)
    # certbot asks the CA to validate the moment this returns, so the zone
    # reload has to reach both authoritative servers first.
    print(f"waiting {WAIT}s for propagation…", flush=True)
    time.sleep(WAIT)


def withdraw(domain: str) -> None:
    """Remove every challenge TXT for this name.

    Line numbers shift as records are deleted, so the zone is re-read for each
    removal instead of deleting from one stale snapshot.
    """
    name = _record_name(domain)
    wanted = {name, f"{name}.{ZONE}"}
    removed = 0
    while True:
        zone = _zone()
        target = None
        for row in zone["data"]:
            if row.get("record_type") != "TXT":
                continue
            dname = base64.b64decode(row["dname_b64"]).decode("utf-8", "replace").rstrip(".")
            if dname in wanted:
                target = row["line_index"]
                break
        if target is None:
            break
        res = _call("/execute/DNS/mass_edit_zone",
                    {"zone": ZONE, "serial": _serial(zone), "remove": str(target)})
        if res.get("status") != 1:
            print(f"could not remove line {target}: {res.get('errors')}", file=sys.stderr)
            break
        removed += 1
    print(f"withdrew {removed} TXT record(s) for {name}.{ZONE}", flush=True)


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "auth"
    domain = os.environ.get("CERTBOT_DOMAIN")
    if not domain:
        raise SystemExit("CERTBOT_DOMAIN is unset — this runs as a certbot hook")
    if action == "auth":
        publish(domain, os.environ["CERTBOT_VALIDATION"])
    elif action == "cleanup":
        withdraw(domain)
    else:
        raise SystemExit("usage: cpanel_dns.py auth|cleanup")
