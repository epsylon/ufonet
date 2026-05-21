#!/usr/bin/env python3
"""Placeholder helpers: detect TEST-NET, load_botnet_file flags, warn_placeholders per kind."""
import sys, os, tempfile

err = []

from core._botnet import is_placeholder, load_botnet_file, warn_placeholders, GUIDANCE, PLACEHOLDER_NETS

if not (str(PLACEHOLDER_NETS[0]) == "203.0.113.0/24"):
    err.append("PLACEHOLDER_NETS missing TEST-NET-3")

cases = [
    ("203.0.113.5", True),
    ("192.0.2.1", True),
    ("198.51.100.99", True),
    ("8.8.8.8", False),
    ("https://example.com/", False),
    ("https://203.0.113.1/path", True),
    ("203.0.113.1:11211", True),
    ("", True),
]
for entry, expected in cases:
    got = is_placeholder(entry)
    if got != expected:
        err.append(f"is_placeholder({entry!r}) = {got}, expected {expected}")

with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write("")
    empty_path = f.name
entries, empty, all_ph = load_botnet_file(empty_path)
if not empty or entries:
    err.append(f"empty file: empty={empty}, entries={entries}")

with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write("203.0.113.10\n203.0.113.11\n")
    ph_path = f.name
entries, empty, all_ph = load_botnet_file(ph_path)
if empty or not all_ph or len(entries) != 2:
    err.append(f"all-placeholders: empty={empty}, all_ph={all_ph}, entries={entries}")

with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write("8.8.8.8\n203.0.113.99\n")
    mix_path = f.name
entries, empty, all_ph = load_botnet_file(mix_path)
if empty or all_ph or len(entries) != 2:
    err.append(f"mixed: empty={empty}, all_ph={all_ph}, entries={entries}")

for kind in ["open-redirect", "dns", "ntp", "snmp", "memcached", "cldap",
             "ssdp", "qotd", "tftp", "wsdisco", "coap", "mssql",
             "arms", "plex", "netbios", "ripv1", "middlebox", "chargen", "reflector"]:
    if kind not in GUIDANCE:
        err.append(f"missing GUIDANCE for kind: {kind}")

os.unlink(empty_path); os.unlink(ph_path); os.unlink(mix_path)

print(f"placeholder cases: {len(cases) - len(err)} / {len(cases)}")
print(f"GUIDANCE entries: {len(GUIDANCE)}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
