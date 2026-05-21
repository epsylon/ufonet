#!/usr/bin/env python3
"""core/_ensure: ensure() falls back to importlib.import_module + pip_install when missing."""
import sys

err = []

from core._ensure import ensure, pip_install, PIP_FLAGS

if "--break-system-packages" not in PIP_FLAGS:
    err.append("PIP_FLAGS should include --break-system-packages")

m = ensure("os")
if m is None or not hasattr(m, "path"):
    err.append("ensure('os') should return the os module (already installed)")

m = ensure("sys")
if m is None:
    err.append("ensure('sys') should return the sys module")

import importlib
m = ensure("Cryptodome.Cipher", "pycryptodomex")
if m is None:
    err.append("ensure('Cryptodome.Cipher') should succeed (already installed via setup.py)")

print(f"ensure('os'): {ensure('os') is not None}")
print(f"PIP_FLAGS: {PIP_FLAGS}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
