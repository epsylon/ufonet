#!/usr/bin/env python3
"""Static verification of /cmd_check_tool runtime path (without actually pulling)."""
import sys, re, os, subprocess

err = []

src_path = "core/webgui.py"
with open(src_path, encoding="utf-8") as f:
    src = f.read()

m = re.search(r'if page == "/cmd_check_tool":\s*\n\s+self\.pages\["/cmd_check_tool"\]\s*=\s*"([^"]+)"', src)
if not m:
    err.append("/cmd_check_tool handler not found in webgui.py")
else:
    placeholder = m.group(1)
    if "Waiting" not in placeholder:
        err.append("/cmd_check_tool placeholder missing 'Waiting': " + placeholder)

m2 = re.search(r'if page == "/cmd_check_tool":[\s\S]{0,600}', src)
if not m2:
    err.append("/cmd_check_tool runcmd not found near handler")
else:
    region = m2.group(0)
    if "ufonet --update" not in region:
        err.append("runcmd doesn't call 'ufonet --update'")
    if "/tmp/out" not in region:
        err.append("runcmd doesn't redirect to /tmp/out")

if not re.search(r'if page == "/cmd_check_tool_update":', src):
    err.append("/cmd_check_tool_update handler missing")

with open("core/update.py", encoding="utf-8") as f:
    upd = f.read()

if "git pull" not in upd:
    err.append("update.py doesn't invoke 'git pull'")
if "github.com/epsylon/ufonet" not in upd:
    err.append("update.py missing GitHub mirror URL")

r = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
if r.returncode != 0 or "true" not in r.stdout:
    err.append("Not inside a git working tree; --update would fail on this checkout")

print(f"webgui /cmd_check_tool handler: OK={m is not None}")
print(f"webgui runcmd build:           OK={m2 is not None}")
print(f"update.py git pull present:    OK={'git pull' in upd}")
print(f"inside git workdir:            OK={r.returncode == 0}")

for e in err:
    print("FAIL:", e)

sys.exit(0 if not err else 1)
