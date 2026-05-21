#!/usr/bin/env python3
"""Inspector tool: ensure it crawls a local target without exceptions."""
import sys, os, ssl, time
sys.path.insert(0, os.path.abspath("test"))
from _lib.local_target import http_target
from core.tools.inspector import Inspector

err = []

class _UFOMin:
    def __init__(self):
        self.options = type("O", (), dict(proxy=None))()
        self.user_agent = "Mozilla/5.0 UFONet-test"
        self.referer = "https://example.com"
        self.agents = [self.user_agent]
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

ufo = _UFOMin()
ins = Inspector(ufo)

with http_target() as (port, counter):
    target = f"http://127.0.0.1:{port}/"
    try:
        ins.inspecting(target)
    except SystemExit:
        pass
    except Exception as e:
        err.append(f"inspector raised: {type(e).__name__}: {e}")
    _deadline = time.time() + 3
    while counter["get"] < 1 and time.time() < _deadline:
        time.sleep(0.1)
    if counter["get"] < 1:
        err.append(f"inspector didn't perform any GET (got {counter['get']})")

print(f"inspector_get_hits={counter['get']}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
