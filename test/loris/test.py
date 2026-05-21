#!/usr/bin/env python3
"""LORIS: verify setupSocket connects to a local server (no DoS, just connection)."""
import sys, os, socket, threading, time
sys.path.insert(0, os.path.abspath("test"))
from _lib.local_target import http_target
from core.mods.loris import setupSocket, LORIS

err = []

with http_target() as (port, counter):
    target = f"127.0.0.1:{port}"
    l = LORIS()
    try:
        sock, ip = setupSocket(l, "http://" + target)
    except Exception as e:
        err.append(f"setupSocket raised: {type(e).__name__}: {e}")
        sock = None
    if sock is None:
        err.append("setupSocket returned no socket")
    else:
        try:
            sock.close()
        except Exception:
            pass

print("setupSocket OK" if not err else "setupSocket FAILED")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
