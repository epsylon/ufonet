#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2026 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys, subprocess, importlib

PIP_FLAGS = ["--no-warn-script-location", "--root-user-action=ignore", "--break-system-packages"]

def pip_install(pip_name):
    print("[Info] [AI] [AUTO-INSTALL] Trying to install missing lib: '" + pip_name + "' ... -> [WAIT!]")
    cmd = [sys.executable, "-m", "pip", "install", pip_name] + PIP_FLAGS
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except Exception as e:
        print("[Error] [AI] [AUTO-INSTALL] Could not run pip: " + str(e))
        return False
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip().splitlines()
        tail = "\n  ".join(err[-6:]) if err else "(no output)"
        print("[Error] [AI] [AUTO-INSTALL] pip install '" + pip_name + "' failed:")
        print("  " + tail)
        return False
    print("[Info] [AI] [AUTO-INSTALL] '" + pip_name + "' installed -> [OK!]")
    return True

def ensure(module_name, pip_name=None):
    pkg = pip_name or module_name
    try:
        return importlib.import_module(module_name)
    except ImportError:
        if not pip_install(pkg):
            print("[Error] [AI] You can install it manually with: python3 -m pip install " + pkg + " --break-system-packages")
            return None
        for cached in list(sys.modules):
            if cached == module_name or cached.startswith(module_name + "."):
                del sys.modules[cached]
        try:
            return importlib.import_module(module_name)
        except ImportError as e:
            print("[Error] [AI] Library still missing after install attempt: '" + module_name + "': " + str(e))
            print("[Error] [AI] You can install it manually with: python3 -m pip install " + pkg + " --break-system-packages")
            return None
