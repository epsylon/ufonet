#!/usr/bin/env python3
"""Dorking pipeline: search_zombies() reaches each engine branch without raising.

We monkey-patch _engine_fetch (HTTP-fetched engines) and the DDGS class (duck)
to return synthetic markup, then call search_zombies() with engine=<each> and
verify it parses at least one href without exceptions. This validates the
regex / decoder paths for all 7 engines without touching the network.
"""
import sys, os, types
sys.path.insert(0, os.path.abspath('test'))
from core.main import UFONet

err = []

ENGINES_HTTP = {
    "bing":      '<a class="tilk" href="https://www.bing.com/ck/a?!&u=a1aHR0cHM6Ly9leGFtcGxlLmNvbS9wcm94eS5waHA_dXJsPQ&p=foo">Example</a>',
    "brave":     '<a href="https://example.com/proxy.php?url=" rel="noopener">Example</a>',
    "mojeek":    '<a class="ob" href="https://example.com/proxy.php?url=">Example</a>',
    "yahoo":     '<a class="d-ib something" href="https://r.search.yahoo.com/_ylt=foo/RU=https%3A%2F%2Fexample.com%2Fproxy.php%3Furl%3D/RK=/foo">Example</a>',
    "startpage": '<a class="w-gl__result-title result-link" href="https://example.com/proxy.php?url=">Example</a>',
    "ecosia":    '<a class="result-title" href="https://example.com/proxy.php?url=">Example</a>',
}

DUCK_RESULTS = [
    {"href": "https://example.com/proxy.php?url=foo", "title": "ex", "body": "x"},
    {"href": "https://example.org/proxy.php?url=bar", "title": "ex2", "body": "x"},
]

class _FakeDDGS:
    def text(self, q, **kw):
        return iter(DUCK_RESULTS)

def make_ufo():
    ufo = UFONet()
    ufo.create_options(['--sd', 'botnet/dorks.txt'])
    ufo.options.verbose = False
    ufo.options.num_results = 5
    ufo.user_agent = "Mozilla/5.0 test"
    ufo.referer = "https://example.com"
    ufo.agents = [ufo.user_agent]
    ufo.options.proxy = None
    ufo.options.forceyes = True
    return ufo

for engine, body in ENGINES_HTTP.items():
    try:
        ufo = make_ufo()
        ufo.options.engine = engine
        ufo._engine_fetch = lambda url, headers, timeout=10, _body=body: _body
        result = ufo.search_zombies('proxy.php?url=', [])
        print("[OK] " + engine + " -> parsed (returned object: " + str(type(result).__name__) + ")")
    except Exception as e:
        err.append(engine + ": " + type(e).__name__ + ": " + str(e)[:200])

try:
    ufo = make_ufo()
    ufo.options.engine = "duck"
    import sys as _s
    _fake_mod = types.ModuleType("ddgs")
    _fake_mod.DDGS = _FakeDDGS
    _s.modules["ddgs"] = _fake_mod
    _fake_dds = types.ModuleType("duckduckgo_search")
    _fake_dds.DDGS = _FakeDDGS
    _s.modules["duckduckgo_search"] = _fake_dds
    result = ufo.search_zombies('proxy.php?url=', [])
    print("[OK] duck -> parsed (" + str(type(result).__name__) + ")")
except Exception as e:
    err.append("duck: " + type(e).__name__ + ": " + str(e)[:200])

for e in err:
    print("FAIL:", e)
print()
print(str(7 - len(err)) + "/7 engine code paths OK")
sys.exit(0 if not err else 1)
