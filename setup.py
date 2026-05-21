#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2026 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys, time

if sys.version_info[0] != 3:
    sys.exit("Sorry, UFONet requires Python >= 3")

libs = ("pygeoip", "requests", "urllib3", "whois", "scapy", "pycryptodomex", "ddgs", "dnspython", "certifi")

import subprocess, os

PY_TAG = "python{}.{}".format(sys.version_info[0], sys.version_info[1])
LIBPYTHON_DEV = "libpython{}.{}-dev".format(sys.version_info[0], sys.version_info[1])
PIP_FLAGS = ["--no-warn-script-location", "--root-user-action=ignore", "--break-system-packages"]

def speech():
    print("[MASTER] Connecting UFONET [AI] system, remotely...\n")
    time.sleep(5)
    print("\n[AI] Hello Master!... ;-)\n")
    print("\n[AI] Launching self-deployment protocols...\n")
    time.sleep(2)
    print(r"      _______")
    print(r"    |.-----.|")
    print(r"    ||x . x||")
    print(r"    ||_.-._||")
    print(r"    `--)-(--`")
    print(r"   __[=== o]___")
    print(r"  |:::::::::::|")

def checkeuid():
    try:
        euid = os.geteuid()
    except:
        sys.exit(2)
    return euid

def install(packages):
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"] + PIP_FLAGS)
    subprocess.run([sys.executable, "-m", "pip", "install", "pycurl", "--upgrade"] + PIP_FLAGS)
    for lib in packages:
        subprocess.run([sys.executable, "-m", "pip", "install", lib, "--ignore-installed"] + PIP_FLAGS)

if __name__ == '__main__':
    euid = checkeuid()
    if euid != 0:
        try:
            args = ['sudo', sys.executable] + sys.argv + [os.environ]
            os.execlpe('sudo', *args)
        except:
            sys.exit()
        sys.exit()
    speech()
    apt_cmd = "sudo apt-get install -y --no-install-recommends {libdev} python3-pycurl python3-geoip python3-whois python3-requests libgeoip1 libgeoip-dev".format(libdev=LIBPYTHON_DEV)
    os.system(apt_cmd)
    install(libs)
    print("\n[UFONET] Setup has been completed!. You can now try to run: ./ufonet\n")
