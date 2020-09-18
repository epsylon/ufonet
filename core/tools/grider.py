#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import socket, re, time, string, sys, os, traceback
from threading import *

class Paster(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.parent = parent
        self.active = False
        self.sock = None
        self.clean = False

    def run( self ):
        conn = None
        addr = None
        self.sock = self.parent.try_bind(9992)
        if self.sock is not None:
            self.sock.listen(1)
            print('[Info] [AI] Clean on port 9992')
            self.clean = True
        else:
            print('[Error] [AI] No paste on port 9992')
        while self.clean:
            try:
                conn,addr = self.sock.accept()
                print('[Info] [AI] Got copy from', addr)
                data = conn.recv(4096).decode()
                print ("[Info] [AI] Stream received:", repr(data))
            except socket.timeout:
                print("[Info] [AI] Socket listening...")
                pass
            except socket.error as e:
                if self.clean == False:
                    print("[Error] [AI] Socket Error /return : "+str(e))
                    return
                else:
                    print("[Error] [AI] Socket Error /break : "+str(e))
                    break
            else:
                if data:
                    l=len(data)
                    print("[Info] [AI] Received data...\n")
                    if data.find('\n')==-1 and data.find('\r')==-1:
                        if data.find("#?#")!=-1:
                            print("[Info] [AI] Adding to grid")
                            fc=open(self.parent.target_dir+"grid.txt","a")
                            fc.write(data+"\n")
                            fc.close()
                        elif data.find("#!#")!=-1:
                            print("[Info] [AI] Adding to board")
                            fc=open(self.parent.target_dir+"board.txt","a")
                            fc.write(data+"\n")
                            fc.close()
                        elif data.find("#-#")!=-1:
                            print("[Info] [AI] Adding to wargames")
                            fc=open(self.parent.target_dir+"wargames.txt","a")
                            fc.write(data+"\n")
                            fc.close()
                        elif data.find("#L#")!=-1:
                            print("[Info] [AI] Adding to links")
                            fc=open(self.parent.target_dir+"links.txt","a")
                            fc.write(data+"\n")
                            fc.close()
                        elif data.find("#S#")!=-1:
                            print("[Info] [AI] Adding to streams")
                            fc=open(self.parent.target_dir+"streams.txt","a")
                            fc.write(data+"\n")
                            fc.close()
                        elif data.find("#$#")!=-1:
                            print("[Info] [AI] Adding to globalnet")
                            fc=open(self.parent.target_dir+"globalnet.txt","a")
                            fc.write(data+"\n")
                            fc.close()
                        else:
                            print("[Error] [AI] Unknown data...")
                    conn.close()
        print('[Info] [AI] Done!!!')
        self.sock.close()
        
class Grider ( Thread ):
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
        if not os.path.exists(self.target_dir+"grid.txt"):
            grid_fail = 0
            try:
                fc = open(self.target_dir+'grid.txt', 'wb')
                fc.close()
            except:
                print("[Error] [AI] No 'grid.txt' file in "+self.target_dir)
                grid_fail = grid_fail + 1
        else:
            grid_fail = 0
        if not os.path.exists(self.target_dir+"board.txt"):
            board_fail = 0
            try:
                fc = open(self.target_dir+'board.txt', 'wb')
                fc.close()
            except:
                print("[Error] [AI] No 'board.txt' file in "+self.target_dir)
                board_fail = board_fail + 1
        else:
            board_fail = 0
        if not os.path.exists(self.target_dir+"wargames.txt"):
            wargames_fail = 0
            try:
                fc = open(self.target_dir+'wargames.txt', 'wb')
                fc.close()
            except:
                print("[Error] [AI] No 'wargames.txt' file in "+self.target_dir)
                wargames_fail = wargames_fail + 1
        else:
            wargames_fail = 0
        if not os.path.exists(self.target_dir+"links.txt"):
            links_fail = 0
            try:
                fc = open(self.target_dir+'links.txt', 'wb')
                fc.close()
            except:
                print("[Error] [AI] No 'links.txt' file in "+self.target_dir)
                links_fail = links_fail + 1
        else:
            links_fail = 0
        if not os.path.exists(self.target_dir+"streams.txt"):
            streams_fail = 0
            try:
                fc = open(self.target_dir+'streams.txt', 'wb')
                fc.close()
            except:
                print("[Error] [AI] No 'streams.txt' file in "+self.target_dir)
                streams_fail = streams_fail + 1
        else:
            streams_fail = 0
        if not os.path.exists(self.target_dir+"globalnet.txt"):
            globalnet_fail = 0
            try:
                fc = open(self.target_dir+'globalnet.txt', 'wb')
                fc.close()
            except:
                print("[Error] [AI] No 'globalnet.txt' file in "+self.target_dir)
                globalnet_fail = globalnet_fail + 1
        else:
            globalnet_fail = 0
        if not os.access(self.target_dir+"grid.txt",os.W_OK):
            print("[Error] [AI] Write access denied for grid file in "+self.target_dir)
            grid_fail = grid_fail + 1
        if not os.access(self.target_dir+"board.txt",os.W_OK):
            print("[Error] [AI] Write access denied for board file in "+self.target_dir)
            board_fail = board_fail + 1
        if not os.access(self.target_dir+"wargames.txt",os.W_OK):
            print("[Error] [AI] Write access denied for wargames file in "+self.target_dir)
            wargames_fail = wargames_fail + 1
        if not os.access(self.target_dir+"links.txt",os.W_OK):
            print("[Error] [AI] Write access denied for links file in "+self.target_dir)
            links_fail = links_fail + 1
        if not os.access(self.target_dir+"streams.txt",os.W_OK):
            print("[Error] [AI] Write access denied for streams file in "+self.target_dir)
            streams_fail = streams_fail + 1
        if not os.access(self.target_dir+"globalnet.txt",os.W_OK):
            print("[Error] [AI] Write access denied for globalnet file in "+self.target_dir)
            globalnet_fail = globalnet_fail + 1
        if grid_fail > 0 and board_fail > 0 and wargames_fail > 0 and links_fail > 0 and streams_fail > 0 and globalnet_fail > 0:
            print("\n[Error] [AI] 'Grid', 'board', 'wargames', 'links', 'streams' and 'globalnet' are unuseable... -> [Aborting!]")
            print("\n[Info] [AI] Suspend [Grider] with: Ctrl+z")
            sys.exit(2)
        self.paster = Paster(self)
        self.awake = False
        print("[Info] [AI] [Grider] Having sweet dreams...")

    def try_bind(self, port):
        s=None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(30)
            s.bind(('', port))
        except socket.error as e:
            if e.errno == 98: # if is in use wait a bit and retry
                time.sleep(3)
                return self.try_bind(port)
            print("[Error] [AI] [Grider] Socket busy, connection failed on port " + str(port))
        return s

    def run(self):
        self.dream()
        try:
            self.paster.start()
            if self.paster.clean:
                print("[Info] [AI] [Grider] Advancing time in another space (waiting for server)"+os.linesep)
                time.sleep(1)
            while self.paster.clean:
                print("[Info] [AI] [Grider] Advancing time in another space (waiting for server)"+os.linesep)
                time.sleep(1)
            print("\n[Info] [AI] [Grider] Sheets are all up and ready...")
            while self.paster.clean:
                time.sleep(1)
        except:
            traceback.print_exc()
        self.cut()
        print("[Info] [AI] [Grider] Finished!!!")
        
    def cut(self):
        self.paster.clean=False
        self.paster.join()

if __name__ == "__main__":
    try:
        print("\n[Info] [AI] Initiating copy/paste functions ...\n")
        print('='*22 + '\n')
        app = Grider()
        app.start()
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Info] [AI] Terminating copy/paste functions...\n")
        app.cut()
    except Exception as e:
        traceback.print_exc()
        print ("\n[Error] [AI] Something wrong trying to copy/paste to the 'grid'... -> [Passing!]\n")
