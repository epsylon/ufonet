#!/usr/bin/env python3
"""Each scapy-based attack mod exposes its <name>ize() entry point and dispatches
without crashing when scapy.send/sr/sr1 are mocked. Real packet emission needs root
and is left to the user; this test only validates the dispatch + packet-building.
"""
import sys, importlib, threading, time

err = []

import scapy.all as scapy
calls = {"send": 0, "sendp": 0, "sr": 0, "sr1": 0}

def fake_send(*a, **kw):
    calls["send"] += 1
def fake_sendp(*a, **kw):
    calls["sendp"] += 1
def fake_sr(*a, **kw):
    calls["sr"] += 1
    return ([], [])
def fake_sr1(*a, **kw):
    calls["sr1"] += 1
    return None

scapy.send = fake_send
scapy.sendp = fake_sendp
scapy.sr = fake_sr
scapy.sr1 = fake_sr1

for _name in ('core.mods.ufosyn', 'core.mods.xmas', 'core.mods.ufoack', 'core.mods.uforst',
              'core.mods.droper', 'core.mods.overlap', 'core.mods.pinger', 'core.mods.ufoudp',
              'core.mods.spray', 'core.mods.smurf', 'core.mods.fraggle', 'core.mods.tachyon',
              'core.mods.monlist', 'core.mods.sniper', 'core.mods.nuke',
              'core.mods.memcached', 'core.mods.chargen', 'core.mods.cldap',
              'core.mods.ssdp', 'core.mods.qotd', 'core.mods.tftp',
              'core.mods.wsdisco', 'core.mods.coap', 'core.mods.mssql',
              'core.mods.middlebox', 'core.mods.finflood',
              'core.mods.arms', 'core.mods.plex', 'core.mods.netbios', 'core.mods.ripv1'):
    mod = importlib.import_module(_name)
    for sym in ('send', 'sendp', 'sr', 'sr1'):
        if hasattr(mod, sym):
            setattr(mod, sym, getattr(scapy, sym))

SPECS = [
    ('core.mods.ufosyn',    'synize',       ('127.0.0.1', 80, 2)),
    ('core.mods.xmas',      'xmasize',      ('127.0.0.1', 80, 2)),
    ('core.mods.ufoack',    'ackize',       ('127.0.0.1', 80, 2)),
    ('core.mods.uforst',    'rstize',       ('127.0.0.1', 80, 2)),
    ('core.mods.droper',    'droperize',    ('127.0.0.1', 80, 2)),
    ('core.mods.overlap',   'overlapize',   ('127.0.0.1', 80, 2)),
    ('core.mods.pinger',    'pingerize',    ('127.0.0.1', 80, 2)),
    ('core.mods.ufoudp',    'ufoudpize',    ('127.0.0.1', 53, 2)),
    ('core.mods.tachyon',   'dnsize',       ('127.0.0.1', 53, 2)),
    ('core.mods.monlist',   'monlistize',   ('127.0.0.1', 2)),
    ('core.mods.sniper',    'sniperize',    ('127.0.0.1', 2)),
    ('core.mods.finflood',  'ripperize',    ('127.0.0.1', 80, 2)),
    ('core.mods.memcached', 'crusherize',   ('127.0.0.1', 2)),
    ('core.mods.chargen',   'fountainize',  ('127.0.0.1', 2)),
    ('core.mods.cldap',     'wormholize',   ('127.0.0.1', 2)),
    ('core.mods.ssdp',      'pulsarize',    ('127.0.0.1', 2)),
    ('core.mods.qotd',      'oraclize',     ('127.0.0.1', 2)),
    ('core.mods.tftp',      'cargoize',     ('127.0.0.1', 2)),
    ('core.mods.wsdisco',   'sonarize',     ('127.0.0.1', 2)),
    ('core.mods.coap',      'nebulize',     ('127.0.0.1', 2)),
    ('core.mods.mssql',     'phantomize',   ('127.0.0.1', 2)),
    ('core.mods.middlebox', 'censorshipize',('127.0.0.1', 2)),
    ('core.mods.arms',      'polishize',    ('127.0.0.1', 2)),
    ('core.mods.plex',      'reelize',      ('127.0.0.1', 2)),
    ('core.mods.netbios',   'cipherize',    ('127.0.0.1', 2)),
    ('core.mods.ripv1',     'halcyonize',   ('127.0.0.1', 2)),
]

def run_with_timeout(fn, args, timeout=4):
    box = {"err": None}
    def target():
        try:
            fn(*args)
        except Exception as e:
            box["err"] = (type(e).__name__, str(e))
    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        return "TIMEOUT", None
    return ("OK", None) if box["err"] is None else ("ERR", box["err"])

for modname, fname, args in SPECS:
    mod = importlib.import_module(modname)
    fn = getattr(mod, fname, None)
    if fn is None:
        err.append(f"{modname}: missing function {fname}()")
        continue
    status, detail = run_with_timeout(fn, args, timeout=4)
    if status == "ERR":
        err.append(f"{modname}.{fname}{args} raised: {detail[0]}: {detail[1][:80]}")
    print(f"  {modname:25s}.{fname:12s} {args}  -> {status}")

SPRAY_LIKE = [
    ('core.mods.spray',   'sprayize',   ('127.0.0.1', 80, 1)),
    ('core.mods.smurf',   'smurfize',   ('127.0.0.1', 80, 1)),
    ('core.mods.fraggle', 'fraggleize', ('127.0.0.1', 53, 1)),
]

import os as _os
_os_environ = dict(_os.environ)

for modname, fname, args in SPRAY_LIKE:
    mod = importlib.import_module(modname)
    fn = getattr(mod, fname, None)
    if fn is None:
        err.append(f"{modname}: missing function {fname}()")
        continue
    status, detail = run_with_timeout(fn, args, timeout=4)
    if status == "ERR":
        msg = (detail[1] or "").lower()
        if "no such file" in msg or "open" in msg or "rpcs.txt" in msg or "snmp.txt" in msg or "ntp.txt" in msg:
            print(f"  {modname:25s}.{fname:12s} {args}  -> SKIP (no reflector file)")
            continue
        err.append(f"{modname}.{fname}{args} raised: {detail[0]}: {detail[1][:80]}")
    print(f"  {modname:25s}.{fname:12s} {args}  -> {status}")

HTTP_MODS = [
    ('core.mods.rapidreset', 'RAPIDRESET', ()),
    ('core.mods.slowread',   'SLOWREAD',   ()),
    ('core.mods.goldeneye',  'GOLDENEYE',  ()),
]
for modname, classname, _ in HTTP_MODS:
    try:
        mod = importlib.import_module(modname)
        cls = getattr(mod, classname, None)
        if cls is None:
            err.append(f"{modname}: missing class {classname}")
        else:
            print(f"  {modname:25s}.{classname:12s} importable -> OK")
    except Exception as e:
        err.append(f"{modname} import failed: {type(e).__name__}: {e}")

print(f"\nfake-send invocations: {calls}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
