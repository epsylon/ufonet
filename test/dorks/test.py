#!/usr/bin/env python3
"""botnet/dorks.txt sanity checks."""
import sys, os

err = []
path = "botnet/dorks.txt"
if not os.path.exists(path):
    print("FAIL: botnet/dorks.txt missing")
    sys.exit(1)

with open(path, encoding="utf-8", errors="replace") as f:
    lines = f.read().splitlines()

raw = len(lines)
non_empty = [l for l in lines if l.strip()]
unique = sorted(set(l.strip() for l in non_empty))

if raw < 100:
    err.append(f"dorks.txt has only {raw} lines (expected > 100)")
if len(non_empty) != raw:
    err.append(f"{raw - len(non_empty)} blank lines found")
if len(unique) != len(non_empty):
    err.append(f"{len(non_empty) - len(unique)} duplicate dorks")

malformed = 0
for ln, line in enumerate(non_empty, start=1):
    if not any(tok in line for tok in ("=", "?", "/")):
        malformed += 1
        if malformed <= 5:
            err.append(f"line {ln} doesn't look like a dork: {line!r}")

print(f"total={raw} non_empty={len(non_empty)} unique={len(unique)}")
for e in err:
    print("FAIL:", e)

sys.exit(0 if not err else 1)
