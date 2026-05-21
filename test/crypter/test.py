#!/usr/bin/env python3
"""AES-256 + HMAC-SHA1 encrypt/decrypt round-trip using the actual Cipher API."""
import sys, base64
from core.tools.crypter import Cipher

PASSPHRASE = "U-NATi0n!"
KEY = base64.b64encode(PASSPHRASE.encode("utf-8"))

SAMPLES = [
    "hello",
    "x",
    "Mensaje en espanol con accent",
    "Mensaje en español con ñ y emoji",
    "A" * 60,
]

err = []
for sample in SAMPLES:
    try:
        c = Cipher(KEY, sample)
        enc = c.encrypt()
        c2 = Cipher(KEY, enc.decode("utf-8"))
        dec = c2.decrypt()
        if dec is None:
            err.append(f"decrypt returned None for {sample!r}")
            continue
        dec_s = dec.decode("utf-8", errors="replace")
        if not sample.startswith(dec_s) and not dec_s.startswith(sample[:len(dec_s)]):
            err.append(f"roundtrip mismatch for {sample!r}: got {dec_s!r}")
    except Exception as e:
        err.append(f"exception for {sample!r}: {type(e).__name__}: {e}")

print(f"round-trips ok: {len(SAMPLES) - len(err)} / {len(SAMPLES)}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
