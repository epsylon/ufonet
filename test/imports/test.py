#!/usr/bin/env python3
"""All UFONet modules must import without error."""
import sys, importlib, traceback

MODULES = [
    "core.main", "core.options", "core.webgui", "core.zombie", "core.herd",
    "core.doll", "core.ajaxmap", "core.randomip", "core.update", "core._ensure",
    "core.tools.abductor", "core.tools.inspector", "core.tools.ufoscan",
    "core.tools.crypter", "core.tools.blackhole", "core.tools.grider",
    "core.mods.loic", "core.mods.loris", "core.mods.ufosyn", "core.mods.spray",
    "core.mods.smurf", "core.mods.xmas", "core.mods.nuke", "core.mods.tachyon",
    "core.mods.monlist", "core.mods.sniper", "core.mods.ufoack", "core.mods.uforst",
    "core.mods.droper", "core.mods.overlap", "core.mods.pinger", "core.mods.ufoudp",
    "core.mods.fraggle",
]

ok = []
fail = []
for name in MODULES:
    try:
        importlib.import_module(name)
        ok.append(name)
    except Exception as e:
        fail.append((name, type(e).__name__, str(e)))
        traceback.print_exc()

print(f"imported_ok={len(ok)} / {len(MODULES)}")
for n, ty, msg in fail:
    print(f"  FAIL {n}: {ty}: {msg}")

sys.exit(0 if not fail else 1)
