#!/usr/bin/env python3
"""LOIC against a local http.server: verify N requests reach the target."""
import sys, os, time
sys.path.insert(0, os.path.abspath("test"))
from _lib.local_target import http_target
from core.mods.loic import ionize, LOIC

err = []

class Holder:
    def __init__(self, agents):
        self.agents = agents
        self.user_agent = agents[0]
        self.payload = ""
        self.attack_mode = "loic"

h = Holder(["Mozilla/5.0 (UFONet-test)"])
rounds = 7

with http_target() as (port, counter):
    target = f"http://127.0.0.1:{port}/test"
    ionize(h, target, rounds, None)
    _deadline = time.time() + 3
    while counter["get"] < rounds and time.time() < _deadline:
        time.sleep(0.1)
    hits = counter["get"]

if hits != rounds:
    err.append(f"expected {rounds} GET hits, got {hits}")

print(f"loic_rounds={rounds} hits={hits}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
