#!/usr/bin/env python3
"""Per-mod unit tests for the 18 v2.0 attack modules.

Each mod is invoked with target='127.0.0.1' (the localhost guard inside every
mod returns early without emitting traffic). Tests verify: clean import,
class exists with expected name, .attacking(target, rounds) runs to completion.
"""
import sys, os, io, contextlib

NEW_MODS = [
    ("memcached",  "MEMCACHED"),
    ("chargen",    "CHARGEN"),
    ("cldap",      "CLDAP"),
    ("ssdp",       "SSDP"),
    ("qotd",       "QOTD"),
    ("tftp",       "TFTP"),
    ("wsdisco",    "WSDISCO"),
    ("coap",       "COAP"),
    ("mssql",      "MSSQL"),
    ("arms",       "ARMS"),
    ("plex",       "PLEX"),
    ("netbios",    "NETBIOS"),
    ("ripv1",      "RIPV1"),
    ("middlebox",  "MIDDLEBOX"),
    ("rapidreset", "RAPIDRESET"),
    ("slowread",   "SLOWREAD"),
    ("goldeneye",  "GOLDENEYE"),
    ("finflood",   "FINFLOOD"),
]

err = []
ok = 0

for modname, classname in NEW_MODS:
    try:
        mod = __import__("core.mods." + modname, fromlist=[classname])
    except Exception as e:
        err.append(f"{modname}: import failed -> {type(e).__name__}: {e}")
        continue
    cls = getattr(mod, classname, None)
    if cls is None:
        err.append(f"{modname}: missing class {classname}")
        continue
    try:
        inst = cls()
    except Exception as e:
        err.append(f"{modname}: instantiation failed -> {type(e).__name__}: {e}")
        continue
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            if classname == "GOLDENEYE":
                inst.attacking("127.0.0.1", 1, None)
            else:
                inst.attacking("127.0.0.1", 1)
    except SystemExit:
        pass
    except Exception as e:
        err.append(f"{modname}: attacking() raised -> {type(e).__name__}: {e}")
        continue
    out = buf.getvalue()
    if "localhost" not in out.lower() and "Sending message" not in out and "ready to fire" not in out:
        if "[Aborting!]" not in out and "[Skipping!]" not in out and "placeholder" not in out.lower():
            err.append(f"{modname}: unexpected output (no localhost/placeholder guard hit) -> {out[:120]!r}")
            continue
    ok += 1
    print(f"[OK] {modname} ({classname})")

print(f"\n{ok}/{len(NEW_MODS)} mods passed")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
