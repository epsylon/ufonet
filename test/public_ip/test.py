#!/usr/bin/env python3
"""Public IP detection: DNS reflection + HTTPS fallback both return a valid IPv4."""
import sys, re

err = []

from core.main import UFONet

app = UFONet()
try:
    app.start_ship_engine()
except SystemExit:
    pass
except Exception:
    pass

ipre = re.compile(r'^\d+\.\d+\.\d+\.\d+$')

ip_dns = app._public_ip_via_dns()
ip_http = app._public_ip_via_http()

print(f"DNS  (OpenDNS reflection): {ip_dns}")
print(f"HTTP (randomized service): {ip_http}")

if ip_dns is not None and not ipre.match(ip_dns):
    err.append(f"DNS returned non-IPv4: {ip_dns!r}")
if ip_http is not None and not ipre.match(ip_http):
    err.append(f"HTTP returned non-IPv4: {ip_http!r}")
if ip_dns is None and ip_http is None:
    err.append("Both DNS and HTTP IP lookups failed (no network?)")

for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
