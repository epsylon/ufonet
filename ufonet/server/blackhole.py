#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - DDoS Botnet via Web Abuse - 2013/2014/2015 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import socket
import time
import string
import sys
import urlparse
import os
import traceback
import gzip
import shutil
import tempfile
from threading import *

class Computer(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.power_on = False
        self.parent = parent
        self.tmp_dir = parent.tmp_dir
        self.target_dir = parent.target_dir

    def find_meat(self):
        self.meats = []
        try:
            for f in os.listdir(self.tmp_dir + "blackhole"):
                if f[-3:] == '.gz':
                    print "[Computer] found meat in "+str(f)
                    self.meats.append(f)
        except:
            print "[Computer] No meat in the fridge "+self.tmp_dir + "blackhole"
            traceback.print_exc()
        return self.meats != []

    def process( self ):
        f_out = open(self.tmp_dir+'meat.txt', 'wb')
        zombies_incoming=[]
        for meat in self.meats:
            f_in = gzip.open(self.tmp_dir+"blackhole/"+meat)
            for line in f_in.readlines() : 
                zombies_incoming.append(line)
                f_out.write(line.strip()+os.linesep)
            f_in.close()
            os.remove(self.tmp_dir+"blackhole/"+meat)
        f_out.close()
        import subprocess
        f_tmp = open(self.tmp_dir + 'meat.tmp','wb')
        subprocess.call('../ufonet --force-yes -t "'+self.tmp_dir+'meat.txt"', shell=True, stdout=f_tmp)
        f_tmp.close()
        f_tmp = open(self.tmp_dir + 'meat.tmp')
        testoutput=f_tmp.read()
        f_tmp.close()
        if "Not any zombie active" in testoutput:
            print "[Computer] no valid zombies !"
            return
        f_tested = open(self.tmp_dir+'meat.txt')
        zombies_community = f_tested.readlines()
        f_tested.close()
        o_in = gzip.open(self.target_dir+'abductions.txt.gz', 'rb')
        zombies_army = o_in.readlines()
        initial = len(zombies_army)
        o_in.close()
        for zombie in zombies_community:
            if zombie.strip() not in zombies_army:
                zombies_army.append(zombie)
            else:
                pass
        fc = gzip.open(self.tmp_dir+'newzombies.txt.gz', 'wb')
        for zombie in zombies_army:
            fc.write(zombie.strip()+os.linesep)
        fc.close()
        shutil.move(self.tmp_dir+'newzombies.txt.gz', self.target_dir+'abductions.txt.gz')
        print "[Computer] Zombies tested : " +str(len(zombies_community)) + " / initial : " +str(initial) + " / final : " + str(len(zombies_army))

    def run(self):
        self.power_on = True
        print "[Computer] Power On"
        while self.power_on :
            # load list of files to process
            if self.find_meat():
                # if data -> process
                self.process()
            time.sleep(5)
        print "[Computer] Power Off"

class BlackRay(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.parent = parent
        self.active = False
        self.sock = None
        self.shining = False

    def run( self ):
        conn = None
        addr = None
        self.sock = self.parent.try_bind(9991)
        if self.sock is not None:
            self.sock.listen(1)
            print '[BlackRay] Emitting on port 9991'
            self.shining = True
        else:
            print '[BlackRay ERROR] Failed to emit on port 9991'
        while self.shining:
            try:
                conn,addr = self.sock.accept()
                print '[BlackRay] Got connection from', addr
            except socket.timeout:
                pass
            except socket.error, e:
                if self.shining == False:
                    print "[BlackRay] Socket Error /return : "+str(e)
                    return
                else:
                    print "[BlackRay] Socket Error /break : "+str(e)
                    break
            else:
                data = conn.recv(1024)
                if data : 
                    if data[0:4] == "SEND" :
                        print "[BlackRay] Meat ready : "+data[5:]
                conn.close()
        print '[BlackRay] End of emission'
        self.sock.close()

class Eater(Thread):
    def __init__(self, client, parent):
        Thread.__init__(self)
        self.client = client
        self.parent = parent

    def run(self):
        print '[Eater] Yum... got meat'
        f = open(self.parent.tmp_dir+"blackhole/"+str(time.time())+".gz","wb")
        while 1:
            data = self.client.recv(1024)
            if not data: break
            f.write(data)
        f.close()
        print '[Eater] Got "%s Closing media transfer"' % f.name
        self.client.close()
        self.parent.eater_full(self)

class Absorber(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.parent = parent
        self.overflow = True
        self._eaters = []
        self.tmp_dir = parent.tmp_dir
        self.sock = False

    def run( self ):
        self.sock = self.parent.try_bind(9990)
        if self.sock is not None:
            self.sock.listen(1)
            print '[Absorber] Ready to feed on port 9990'
            self.overflow = False
        else:
            print '[Absorber ERROR] Failed to listen on port 9990'
        while not self.overflow:
            try:
                conn,addr = self.sock.accept()
                print '[Absorber] Got connection from', addr
            except socket.timeout:
                pass
            except socket.error, e:
                if self.hungry == False:
                    print "[Absorber] Socket Error /return : "+str(e)
                    return
                else:
                    print "[Absorber] Socket Error /break : "+str(e)
                    break
            else:
                t = Eater(conn, self)
                t.start()
                self._eaters.append(t)
        self.sock.close()
        print '[Absorber] Dinner time is over'

    def eater_full(self, _thread):
        self._eaters.remove(_thread)

class BlackHole ( Thread ):
    def __init__(self):
        Thread.__init__( self )
        self.daemon = True
        self.awake = True
        self.tmp_dir = "/tmp/"
        self.target_dir = '/var/www/ufonet/' 
        self.blackray = None
        self.absorber = None
        self.computer = None

    def dream(self):
        if not os.path.exists(self.target_dir+"abductions.txt.gz"):
            try:
                fc = gzip.open(self.target_dir+'abductions.txt.gz', 'wb')
                fc.close()
            except:
                print "[Error] unable to create empty abductions file in "+self.target_dir
                sys.exit(2)
        if not os.access(self.target_dir+"abductions.txt.gz",os.W_OK):
            print "[Error] write acces denied to abductions file in "+self.target_dir
            sys.exit(2)
        if self.consume():
            os.mkdir(self.tmp_dir + "blackhole")
        else:
            print "[Blackhole Error] unable to consume in "+self.tmp_dir+"blackhole..."
            sys.exit(2)
        if not os.path.isdir(self.tmp_dir + "blackhole"):
            print "[Blackhole Error] unable to create "+self.tmp_dir+"blackhole..."
            sys.exit(2)
        self.blackray = BlackRay(self)
        self.absorber = Absorber(self)
        self.computer = Computer(self)
        self.awake = False
        print "[Blackhole] Having sweet dreams..."

    def consume(self):
        if os.path.isdir(self.tmp_dir + "blackhole"):
            try:
                shutil.rmtree(self.tmp_dir + "blackhole")
            except OSError, e:
                print "[Blackhole Error] unable to consume : " + str(e)
                return False
        return True

    def try_bind(self, port):
        s=None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.bind(('', port))
        except socket.error as e:
            if e.errno == 98: # if is in use wait a bit and retry
                time.sleep(3)
                return self.try_bind(port)
            print("[Blackhole Warning] socket busy, connection failed on port " + str(port))
        return s

    def run(self):
        self.dream()
        try:
            self.blackray.start()
            self.absorber.start()
            self.computer.start()
            if not self.blackray.shining or self.absorber.overflow or not self.computer.power_on:
                print "[BlackHole] Advancing time in another space (waiting for server)"+os.linesep
                time.sleep(1)
            while not self.blackray.shining or self.absorber.overflow or not self.computer.power_on:
                time.sleep(1)
            print "\n[BlackHole] all up and running"
            while self.blackray.shining and not self.absorber.overflow and self.computer.power_on:
                time.sleep(1)
        except:
            traceback.print_exc()
        self.awaken()
        print "[Blackhole] Lifespan is up..."

    def collapse(self):
        self.blackray.shining = False
        self.absorber.overflow = True
        self.computer.power_on = False
        self.computer.join()
        self.blackray.join()
        self.absorber.join()

    def awaken(self):
        self.consume()
        self.collapse()
        self.awake = True

if __name__ == "__main__":
    try:
        print("\nInitiating void generation sequence...\n")
        print '='*22 + '\n'
        app = BlackHole()
        app.start()
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\nTerminating void generation sequence...\n")
        app.collapse()
    except Exception, e:
        traceback.print_exc()
        print ("\n[Error] - Something wrong creating blackhole...!\n")
