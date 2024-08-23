#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2024 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys, time

if sys.version_info[0] != 3:
    sys.exit("Sorry, UFONet requires Python >= 3")

libs = ("GeoIP", "python-geoip", "pygeoip", "requests", "whois", "scapy", "pycryptodomex", "duckduckgo-search")
    
import subprocess, os

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
        sys.exit(2) # return
    return euid


def install(package):
    subprocess.run(["python3", "-m", "pip", "install", "--upgrade", "pip", "--no-warn-script-location", "--root-user-action=ignore"])
    subprocess.run(["python3", "-m", "pip", "install", "pycurl", "--upgrade", "--no-warn-script-location", "--root-user-action=ignore"])
    for lib in libs:
        subprocess.run(["python3", "-m", "pip", "install", lib, "--no-warn-script-location", "--ignore-installed", "--root-user-action=ignore"])

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
    os.system("sudo apt-get install -y --no-install-recommends libpython3.11-dev python3-pycurl python3-geoip python3-whois python3-requests libgeoip1 libgeoip-dev")
    install(libs)
    print("\n[UFONET] Setup has been completed!. You can now try to run: ./ufonet\n")
