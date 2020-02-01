#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
from threading import Thread
import socket, time, os, base64, re
try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse
class Needle(Thread):
    def __init__(self, client, addr, parent):
        Thread.__init__(self)
        self.daemon = True
        self.client = client
        self.parent = parent

    def run(self):
        data = self.client.recv(1024)
        if data:
            if data.startswith("HEAD"):
                self.parent.data_arrived(data)
                self.client.send("""HTTP/1.1 200 OK
Server: UFONet Galactic Cyber Warfare
Date: Wed, 05 Nov 2042 16:21:23 GMT
Content-Type: text/html
Content-Length: """+str(len('thanks for coming!'))+"""
Connection: close

""")
                self.client.close()
            else:
                self.parent.data_arrived(data)
                self.client.send('Welcome to UFONet mothership! ;-)\n')
                self.client.send('='*40)
                self.client.send("\n\nStream:\n")
                self.client.send('-'*15 + "\n\n")
                f = open("mothership", 'r') # read mothership stream
                self.client.send(str(f.read()))
                f.close()
                self.client.close()
        self.parent.client_finished(self)

class Doll(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.daemon = True
        self._clients = []
        self._armed = True
        self.ready = False
        self.running =False
        self.parent = parent
        self.real_zombies = [] # 100% vulnerable zombies
        if os.path.exists('mothership') == True:
            os.remove('mothership') # remove mothership stream 
        with open('alien') as f: # call alien to verify vulnerability
            self.alien = f.read().splitlines()
        f.close()

    def data_arrived(self, data):
        data.split("\n")[0]
        self.check_zombie(data)
        f = open("mothership", 'a') # append data mothership stream
        f.write(data)
        f.close()

    def check_zombie(self, data): # check for requests received by a zombie
        if str(''.join(self.alien)) in data: # hash check
            if "%7C" in data: # %7C -> |
                regex_zmb = re.compile('{}(.*){}'.format(re.escape('%7C'), re.escape(' HTTP'))) # regex magics
            else:
                regex_zmb = re.compile('{}(.*){}'.format(re.escape('|'), re.escape(' HTTP'))) # regex magics
            pattern_zmb = re.compile(regex_zmb)
            zombie_vul = re.findall(pattern_zmb, data)
            if zombie_vul not in self.real_zombies: # add zombies only one time
                self.real_zombies.append(zombie_vul)

    def client_finished(self, _thread):
        self._clients.remove(_thread)

    def shutdown(self):
        if self.ready:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        self.running = False
        self._armed = False
        self.ready = False

    def run(self):
        while not self.running and self._armed:
            try:
                s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                s.bind(('', 8080))
                self.running = True
            except socket.error as e:
                print("\n[Warning] Doll socket busy, retry opening")
                if e.errno == 98: # if is in use wait a bit and retry
                    time.sleep(3)
                else:
                    return
        if not self._armed:
            print("\n[Error] Doll not armed")
            return
        self.socket = s
        self.ready = True
        s.listen(1)
        while self.running and self._armed:
            try:
                conn, addr = s.accept()
            except socket.timeout:
                print("\n[Warning] Socket is giving timeout...")
                pass
            except socket.error as e:
                if self.ready == False:
                    return
                else:
                    break
            else:
                t = Needle(conn, addr, self)
                t.start()
                self._clients.append(t)
        if self.ready:
            s.close()
            self.ready = False
