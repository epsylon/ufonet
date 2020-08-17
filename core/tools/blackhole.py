#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import socket, re, time, string, sys, os, traceback, gzip, shutil
from threading import *

class AI(Thread):
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
                    print("[Info] [AI] Found meat in "+str(f))
                    self.meats.append(f)
        except:
            print("[info] [AI] No meat in the fridge "+self.tmp_dir + "blackhole")
            traceback.print_exc()
        return self.meats != []

    def process( self ):
        zombies_incoming=[]
        aliens_incoming=[]
        droids_incoming=[]
        ucavs_incoming=[]
        rpcs_incoming=[]
        ntps_incoming=[]
        dnss_incoming=[]
        snmps_incoming=[]
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
            elif 'community_rpcs.txt.gz' in f_in: # rpcs found
                f_out = open(self.tmp_dir+'mirror.txt', 'wb')
                for line in f_in.readlines():
                    rpcs_incoming.append(line)
                    f_out.write(line.strip()+os.linesep)
                f_out.close()
            elif 'community_ntps.txt.gz' in f_in: # ntps found
                f_out = open(self.tmp_dir+'clock.txt', 'wb')
                for line in f_in.readlines():
                    ntps_incoming.append(line)
                    f_out.write(line.strip()+os.linesep)
                f_out.close()
            elif 'community_dnss.txt.gz' in f_in: # dnss found
                f_out = open(self.tmp_dir+'label.txt', 'wb')
                for line in f_in.readlines():
                    dnss_incoming.append(line)
                    f_out.write(line.strip()+os.linesep)
                f_out.close()
            elif 'community_snmps.txt.gz' in f_in: # snmps found
                f_out = open(self.tmp_dir+'glass.txt', 'wb')
                for line in f_in.readlines():
                    snmps_incoming.append(line)
                    f_out.write(line.strip()+os.linesep)
                f_out.close()
            f_in.close()
            os.remove(self.tmp_dir+"blackhole/"+meat)
        import subprocess
        f_tmp = open(self.tmp_dir + 'meat.tmp','wb')
        try:
            subprocess.call('../../ufonet --force-yes -t "'+self.tmp_dir+'meat.txt"', shell=True, stdout=f_tmp) # testing zombies (GET) (path: core/tools/blackhole.py)
        except:
            pass
        f_tmp.close()
        f_tmp = open(self.tmp_dir + 'meat.tmp')
        testoutput=f_tmp.read()
        f_tmp.close()
        if "Not any zombie active" in testoutput:
            if not aliens_incoming and not droids_incoming and not ucavs_incoming: # not any valid zombie (GET or POST)
                print("[Info] [AI] no valid zombies !")
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
            print("[info] [AI] Zombies tested : " +str(len(zombies_community)) + " / initial : " +str(initial) + " / final : " + str(len(zombies_army)))
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
            print("[Info] [AI] Aliens tested : " +str(len(aliens_community)) + " / initial : " +str(initial) + " / final : " + str(len(aliens_army)))
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
            print("[Info] [AI] Droids tested : " +str(len(droids_community)) + " / initial : " +str(initial) + " / final : " + str(len(droids_army)))
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
            print("[Info] [AI] UCAVs tested : " +str(len(ucavs_community)) + " / initial : " +str(initial) + " / final : " + str(len(ucavs_army)))
            f_tested = open(self.tmp_dir+'mirror.txt')
            rpcs_community = f_tested.readlines()
            f_tested.close()
            o_in = gzip.open(self.target_dir+'reflectors.txt.gz', 'rb')
            rpcs_army = o_in.readlines()
            initial = len(rpcs_army)
            o_in.close()
            for rpc in rpcs_community:
                if rpc.strip() not in rpcs_army:
                    rpcs_army.append(rpc)
                else:
                    pass
            fc = gzip.open(self.tmp_dir+'newrpcs.txt.gz', 'wb')
            for rpc in rpcs_army:
                fc.write(rpc.strip()+os.linesep)
            fc.close()
            shutil.move(self.tmp_dir+'newrpcs.txt.gz', self.target_dir+'reflectors.txt.gz')
            print("[Info] [AI] X-RPCs tested : " +str(len(rpcs_community)) + " / initial : " +str(initial) + " / final : " + str(len(rpcs_army)))
            f_tested = open(self.tmp_dir+'clock.txt')
            ntps_community = f_tested.readlines()
            f_tested.close()
            o_in = gzip.open(self.target_dir+'warps.txt.gz', 'rb')
            ntps_army = o_in.readlines()
            initial = len(ntps_army)
            o_in.close()
            for ntp in ntps_community:
                if ntp.strip() not in ntps_army:
                    ntps_army.append(ntp)
                else:
                    pass
            fc = gzip.open(self.tmp_dir+'newntps.txt.gz', 'wb')
            for ntp in ntps_army:
                fc.write(ntp.strip()+os.linesep)
            fc.close()
            shutil.move(self.tmp_dir+'newntps.txt.gz', self.target_dir+'warps.txt.gz')
            print("[Info] [AI] NTPs tested : " +str(len(ntps_community)) + " / initial : " +str(initial) + " / final : " + str(len(ntps_army)))
            f_tested = open(self.tmp_dir+'label.txt')
            dnss_community = f_tested.readlines()
            f_tested.close()
            o_in = gzip.open(self.target_dir+'crystals.txt.gz', 'rb')
            dnss_army = o_in.readlines()
            initial = len(dnss_army)
            o_in.close()
            for dns in dnss_community:
                if dns.strip() not in dnss_army:
                    dnss_army.append(dns)
                else:
                    pass
            fc = gzip.open(self.tmp_dir+'newdnss.txt.gz', 'wb')
            for dns in dnss_army:
                fc.write(dns.strip()+os.linesep)
            fc.close()
            shutil.move(self.tmp_dir+'newdnss.txt.gz', self.target_dir+'crystals.txt.gz')
            print("[Info] [AI] DNSs tested : " +str(len(dnss_community)) + " / initial : " +str(initial) + " / final : " + str(len(dnss_army)))
            f_tested = open(self.tmp_dir+'glass.txt')
            snmps_community = f_tested.readlines()
            f_tested.close()
            o_in = gzip.open(self.target_dir+'bosons.txt.gz', 'rb')
            snmps_army = o_in.readlines()
            initial = len(snmps_army)
            o_in.close()
            for snmp in snmps_community:
                if snmp.strip() not in snmps_army:
                    snmps_army.append(snmp)
                else:
                    pass
            fc = gzip.open(self.tmp_dir+'newsnmps.txt.gz', 'wb')
            for snmp in snmps_army:
                fc.write(snmp.strip()+os.linesep)
            fc.close()
            shutil.move(self.tmp_dir+'newsnmps.txt.gz', self.target_dir+'bosons.txt.gz')
            print("[Info] [AI] SNMPs tested : " +str(len(snmps_community)) + " / initial : " +str(initial) + " / final : " + str(len(snmps_army)))

    def run(self):
        self.power_on = True
        print("[Info] [AI] Power On")
        while self.power_on :
            # load list of files to process
            if self.find_meat():
                # if data -> process
                self.process()
            time.sleep(5)
        print("[Info] [AI] Power Off")

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
            print('[Info] [AI] [BlackRay] Emitting on port 9991')
            self.shining = True
        else:
            print('[Error] [AI] [BlackRay] Failed to emit on port 9991')
        while self.shining:
            try:
                conn,addr = self.sock.accept()
                print('[Info] [AI] [BlackRay] Got connection from', addr)
            except socket.timeout:
                pass
            except socket.error as e:
                if self.shining == False:
                    print("[Error] [AI] [BlackRay] Socket Error /return : "+str(e))
                    return
                else:
                    print("[Error] [AI] [BlackRay] Socket Error /break : "+str(e))
                    break
            else:
                data = conn.recv(1024)
                if data : 
                    if data[0:4] == "SEND" :
                        print("[Info] [AI] [BlackRay] Meat ready : "+data[5:])
                conn.close()
        print('[Info] [AI] [BlackRay] End of emission')
        self.sock.close()

class Eater(Thread):
    def __init__(self, client, parent):
        Thread.__init__(self)
        self.client = client
        self.parent = parent

    def run(self):
        print('[Info] [AI] Yum... got meat')
        zombie_meat = "community_zombies.txt.gz"
        alien_meat = "community_aliens.txt.gz"
        droid_meat = "community_droids.txt.gz"
        ucav_meat = "community_ucavs.txt.gz"
        rpc_meat = "community_rpcs.txt.gz"
        ntp_meat = "community_ntps.txt.gz"
        dns_meat = "community_dnss.txt.gz"
        snmp_meat = "community_snmps.txt.gz"
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
            print('\n[Info] [AI] Got "%s Closing media transfer"' % f.name)
            f.close()
        elif alien_meat in data: # get aliens
            r = re.compile(".*("+alien_meat+").*") # regex magics
            meat_type = r.search(data)
            m = meat_type.group(1)
            f = open(self.parent.tmp_dir+"blackhole/"+m,"wb")
            f.write(data)
            print('\n[Info] [AI] Got "%s Closing media transfer"' % f.name)
            f.close()
        elif droid_meat in data: # get zombies
            r = re.compile(".*("+droid_meat+").*") # regex magics
            meat_type = r.search(data)
            m = meat_type.group(1)
            f = open(self.parent.tmp_dir+"blackhole/"+m,"wb")
            f.write(data)
            print('\n[Info] [AI] Got "%s Closing media transfer"' % f.name)
            f.close()
        elif ucav_meat in data: # get ucavs
            r = re.compile(".*("+ucav_meat+").*") # regex magics
            meat_type = r.search(data)
            m = meat_type.group(1)
            f = open(self.parent.tmp_dir+"blackhole/"+m,"wb")
            f.write(data)
            print('\n[Info] [AI] Got "%s Closing media transfer"' % f.name)
            f.close()
        elif rpc_meat in data: # get rpcs
            r = re.compile(".*("+rpc_meat+").*") # regex magics
            meat_type = r.search(data)
            m = meat_type.group(1)
            f = open(self.parent.tmp_dir+"blackhole/"+m,"wb")
            f.write(data)
            print('\n[Info] [AI] Got "%s Closing media transfer"' % f.name)
            f.close()
        elif ntp_meat in data: # get ntps
            r = re.compile(".*("+ntp_meat+").*") # regex magics
            meat_type = r.search(data)
            m = meat_type.group(1)
            f = open(self.parent.tmp_dir+"blackhole/"+m,"wb")
            f.write(data)
            print('\n[Info] [AI] Got "%s Closing media transfer"' % f.name)
            f.close()
        elif dns_meat in data: # get dnss
            r = re.compile(".*("+dns_meat+").*") # regex magics
            meat_type = r.search(data)
            m = meat_type.group(1)
            f = open(self.parent.tmp_dir+"blackhole/"+m,"wb")
            f.write(data)
            print('\n[Info] [AI] Got "%s Closing media transfer"' % f.name)
            f.close()
        elif snmp_meat in data: # get snmps
            r = re.compile(".*("+snmp_meat+").*") # regex magics
            meat_type = r.search(data)
            m = meat_type.group(1)
            f = open(self.parent.tmp_dir+"blackhole/"+m,"wb")
            f.write(data)
            print('\n[Info] [AI] Got "%s Closing media transfer"' % f.name)
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
            print('[Info] [AI] Ready to feed on port 9990')
            self.overflow = False
        else:
            print('[Error] [AI] Failed to listen on port 9990')
        while not self.overflow:
            try:
                conn,addr = self.sock.accept()
                print('[Info] [AI] Got connection from', addr)
            except socket.timeout:
                pass
            except socket.error as e:
                if self.hungry == False:
                    print("[Error] [AI] Socket Error /return : "+str(e))
                    return
                else:
                    print("[Error] [AI] Socket Error /break : "+str(e))
                    break
            else:
                t = Eater(conn, self)
                t.start()
                self._eaters.append(t)
        self.sock.close()
        print('[Info] [AI] Dinner time is over')

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
                print("[Error] [AI] Not 'abductions.txt.gz' file in "+self.target_dir)
                abductions_fail = abductions_fail + 1
        else:
            abductions_fail = 0
        if not os.path.exists(self.target_dir+"troops.txt.gz"):
            troops_fail = 0
            try:
                fc = gzip.open(self.target_dir+'troops.txt.gz', 'wb')
                fc.close()
            except:
                print("[Error] [AI] Not 'troops.txt.gz' file in "+self.target_dir)
                troops_fail = troops_fail + 1
        else:
            troops_fail = 0
        if not os.path.exists(self.target_dir+"robots.txt.gz"):
            robots_fail = 0
            try:
                fc = gzip.open(self.target_dir+'robots.txt.gz', 'wb')
                fc.close()
            except:
                print("[Error] [AI] Not 'robots.txt.gz' file in "+self.target_dir)
                robots_fail = robots_fail + 1
        else:
            robots_fail = 0
        if not os.path.exists(self.target_dir+"drones.txt.gz"):
            drones_fail = 0
            try:
                fc = gzip.open(self.target_dir+'drones.txt.gz', 'wb')
                fc.close()
            except:
                print("[Error] [AI] Not 'drones.txt.gz' file in "+self.target_dir)
                drones_fail = drones_fail + 1
        else:
            drones_fail = 0
        if not os.path.exists(self.target_dir+"reflectors.txt.gz"):
            reflectors_fail = 0
            try:
                fc = gzip.open(self.target_dir+'reflectors.txt.gz', 'wb')
                fc.close()
            except:
                print("[Error] [AI] Not 'reflectors.txt.gz' file in "+self.target_dir)
                reflectors_fail = reflectors_fail + 1
        else:
            reflectors_fail = 0
        if not os.path.exists(self.target_dir+"warps.txt.gz"):
            ntps_fail = 0
            try:
                fc = gzip.open(self.target_dir+'warps.txt.gz', 'wb')
                fc.close()
            except:
                print("[Error] [AI] Not 'warps.txt.gz' file in "+self.target_dir)
                ntps_fail = ntps_fail + 1
        else:
            ntps_fail = 0
        if not os.path.exists(self.target_dir+"crystals.txt.gz"):
            dnss_fail = 0
            try:
                fc = gzip.open(self.target_dir+'crystals.txt.gz', 'wb')
                fc.close()
            except:
                print("[Error] [AI] Not 'crystals.txt.gz' file in "+self.target_dir)
                dnss_fail = dnss_fail + 1
        else:
            dnss_fail = 0
        if not os.path.exists(self.target_dir+"bosons.txt.gz"):
            snmps_fail = 0
            try:
                fc = gzip.open(self.target_dir+'bosons.txt.gz', 'wb')
                fc.close()
            except:
                print("[Error] [AI] Not 'bosons.txt.gz' file in "+self.target_dir)
                snmps_fail = snmps_fail + 1
        else:
            snmps_fail = 0
        if not os.access(self.target_dir+"abductions.txt.gz",os.W_OK):
            print("[Error] [AI] Write access denied for 'abductions' file in "+self.target_dir)
            abductions_fail = abductions_fail + 1
        if not os.access(self.target_dir+"troops.txt.gz",os.W_OK):
            print("[Error] [AI] Write access denied for 'troops' file in "+self.target_dir)
            troops_fail = troops_fail + 1
        if not os.access(self.target_dir+"robots.txt.gz",os.W_OK):
            print("[Error] [AI] Write access denied for 'robots' file in "+self.target_dir)
            robots_fail = robots_fail + 1
        if not os.access(self.target_dir+"drones.txt.gz",os.W_OK):
            print("[Error] [AI] Write access denied for 'drones' file in "+self.target_dir)
            drones_fail = drones_fail + 1
        if not os.access(self.target_dir+"reflectors.txt.gz",os.W_OK):
            print("[Error] [AI] Write access denied for 'reflectors' file in "+self.target_dir)
            reflectors_fail = reflectors_fail + 1
        if not os.access(self.target_dir+"warps.txt.gz",os.W_OK):
            print("[Error] [AI] Write access denied for 'warps' file in "+self.target_dir)
            ntps_fail = ntps_fail + 1
        if not os.access(self.target_dir+"crystals.txt.gz",os.W_OK):
            print("[Error] [AI] Write access denied for 'crystals' file in "+self.target_dir)
            dnss_fail = dnss_fail + 1
        if not os.access(self.target_dir+"bosons.txt.gz",os.W_OK):
            print("[Error] [AI] Write access denied for 'bosons' file in "+self.target_dir)
            snmps_fail = snmps_fail + 1
        if abductions_fail > 0 and troops_fail > 0 and robots_fail > 0 and drones_fail > 0 and reflectors_fail > 0 and ntps_fail > 0 and dnss_fail > 0 and snmps_fail > 0:
            print("\n[Error] [AI] Cannot found any container... -> [Aborting!]")
            print("\n[Info] [AI] Suspend [Blackhole] with: Ctrl+z")
            sys.exit(2)
        if self.consume():
            os.mkdir(self.tmp_dir + "blackhole")
        else:
            print("[Error] [AI] [Blackhol] Unable to consume in "+self.tmp_dir+"blackhole...")
            sys.exit(2)
        if not os.path.isdir(self.tmp_dir + "blackhole"):
            print("[Error] [AI] [Blackhole] Unable to create "+self.tmp_dir+"blackhole...")
            sys.exit(2)
        self.blackray = BlackRay(self)
        self.absorber = Absorber(self)
        self.computer = AI(self)
        self.awake = False
        print("[Info] [AI] [Blackhole] Having sweet dreams...")

    def consume(self):
        if os.path.isdir(self.tmp_dir + "blackhole"):
            try:
                shutil.rmtree(self.tmp_dir + "blackhole")
            except OSError as e:
                print("[Error] [AI] [Blackhole] Unable to consume : " + str(e))
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
            print(("[Error] [AI] [Blackhole] Socket busy, connection failed on port " + str(port)))
        return s

    def run(self):
        self.dream()
        try:
            self.blackray.start()
            self.absorber.start()
            self.computer.start()
            if not self.blackray.shining or self.absorber.overflow or not self.computer.power_on:
                print("[Info] [AI] Advancing time in another space (waiting for server)"+os.linesep)
                time.sleep(1)
            while not self.blackray.shining or self.absorber.overflow or not self.computer.power_on:
                time.sleep(1)
            print("\n[Info] [AI] [BlackHole] All up and running...")
            while self.blackray.shining and not self.absorber.overflow and self.computer.power_on:
                time.sleep(1)
        except:
            traceback.print_exc()
        self.awaken()
        print("[Info] [AI] [Blackhole] Lifespan is up...")

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
        print("\n[Info] [AI] Initiating void generation sequence...\n")
        print('='*22 + '\n')
        app = BlackHole()
        app.start()
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Info] [AI] Terminating void generation sequence...\n")
        app.collapse()
    except Exception as e:
        traceback.print_exc()
        print ("\n[Error] [AI] Something wrong creating [Blackhole] -> [Passing!]\n")
