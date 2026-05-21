#!/usr/bin/env python3
"""Search engine helpers: registry, query builder, decoder."""
import sys, base64

err = []

from core.main import UFONet

app = UFONet()
try:
    app.start_ship_engine()
except SystemExit:
    pass
except Exception as e:
    err.append(f"start_ship_engine raised: {type(e).__name__}: {e}")

expected_engines = ['bing', 'duck', 'brave', 'mojeek', 'yahoo', 'startpage', 'ecosia']
for e in expected_engines:
    if e not in app.search_engines:
        err.append(f"search engine missing in registry: {e}")

target = "https://example.com/page.php"
b64 = base64.urlsafe_b64encode(target.encode("utf-8")).decode("ascii").rstrip("=")
sample_bing = f"https://www.bing.com/ck/a?!&&p=xyz&u=a1{b64}&ntb=1"
got = app._bing_decode(sample_bing)
if got != target:
    err.append(f"_bing_decode mismatch: expected {target!r}, got {got!r}")

raw_yahoo = "https://r.search.yahoo.com/_ylt=xxxx/RV=2/RE=00/RO=10/RU=https%3a%2f%2fexample.com%2fpage%3fa%3d1/RK=2/RS=zzz"
got2 = app._yahoo_decode(raw_yahoo)
if "example.com/page" not in got2:
    err.append(f"_yahoo_decode unexpected: {got2!r}")

class _O: pass
app.options = _O()
app.options.search = "page.php?url="
app.options.dorks = None
app.options.autosearch = None
sep, q = app._engine_query_string(None)
if sep != "page.php?url=" or "instreamset" not in q:
    err.append(f"query_string (search mode) wrong: sep={sep!r} q={q!r}")

app.options.search = None
app.options.dorks = "dorks.txt"
sep2, q2 = app._engine_query_string("redirect.php?url=")
if sep2 != "redirect.php?url=" or "redirect.php" not in q2:
    err.append(f"query_string (dork mode) wrong: sep={sep2!r} q={q2!r}")

print(f"registry: {app.search_engines}")
print(f"bing decode OK: {got == target}")
print(f"yahoo decode OK: {'example.com/page' in got2}")
print(f"query_string (search): {sep!r}, {q!r}")
print(f"query_string (dork):   {sep2!r}, {q2!r}")

for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
