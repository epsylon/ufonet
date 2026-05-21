#!/usr/bin/env python3
"""Verify -m TARGET is wired and triggers standalone mod-only dispatch."""
import sys, subprocess

err = []

r = subprocess.run([sys.executable, "ufonet", "--help"], capture_output=True, text=True, timeout=10)
if r.returncode != 0:
    err.append(f"--help exited {r.returncode}")
help_text = r.stdout

if "-m TARGET" not in help_text:
    err.append("-m TARGET flag missing in --help")
if "mod-only" not in help_text.lower():
    err.append("'mod-only' label missing in --help for -m")

import sys as _sys
_sys.argv = ["ufonet", "-m", "http://example.com", "--memcached", "5"]
from core.main import UFONet
app = UFONet()
opts = app.create_options()

if not getattr(opts, 'mod_target', None):
    err.append("options.mod_target not populated when -m used")
if getattr(opts, 'mod_target', None) != "http://example.com":
    err.append(f"options.mod_target wrong: {opts.mod_target!r}")
if getattr(opts, 'memcached', None) != "5":
    err.append(f"options.memcached wrong: {opts.memcached!r}")
if opts.target is not None:
    err.append(f"options.target should be None, got {opts.target!r}")

print(f"-m flag wired correctly: mod_target={opts.mod_target!r}, memcached={opts.memcached!r}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
