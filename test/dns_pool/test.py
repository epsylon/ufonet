#!/usr/bin/env python3
"""DNS resolver pool: enough entries, randomness, valid IPs."""
import sys, re, ipaddress

err = []

from core._dns_pool import (PUBLIC_DNS_RESOLVERS, OPENDNS_RESOLVERS,
                            DUMMY_ROUTABLE_HOSTS, random_resolvers,
                            random_opendns, random_dummy_host)

if len(PUBLIC_DNS_RESOLVERS) < 50:
    err.append(f"PUBLIC_DNS_RESOLVERS has only {len(PUBLIC_DNS_RESOLVERS)} entries (expected >=50)")

for ip in PUBLIC_DNS_RESOLVERS + OPENDNS_RESOLVERS + DUMMY_ROUTABLE_HOSTS:
    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        err.append(f"invalid IPv4 in pool: {ip!r}")

samples = set()
for _ in range(200):
    samples.add(tuple(random_resolvers(2)))
if len(samples) < 30:
    err.append(f"random_resolvers seems non-random: only {len(samples)} unique pairs in 200 draws")

for _ in range(10):
    pair = random_resolvers(2)
    if len(pair) != 2:
        err.append(f"random_resolvers(2) returned {len(pair)} items")
    if pair[0] == pair[1]:
        err.append("random_resolvers(2) returned duplicates")

od = random_opendns()
for ip in od:
    if ip not in OPENDNS_RESOLVERS:
        err.append(f"random_opendns returned non-opendns IP: {ip}")

h = random_dummy_host()
if h not in DUMMY_ROUTABLE_HOSTS:
    err.append(f"random_dummy_host returned unknown: {h}")

print(f"pool size: {len(PUBLIC_DNS_RESOLVERS)}")
print(f"unique 2-tuples in 200 draws: {len(samples)}")
print(f"opendns pool: {len(OPENDNS_RESOLVERS)}")
print(f"dummy hosts: {len(DUMMY_ROUTABLE_HOSTS)}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
