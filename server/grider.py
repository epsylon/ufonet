#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - Denial of Service Toolkit - 2017/2018 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import socket, re, time, string, sys, urlparse, os, traceback
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
            print '[Paster] clean on port 9992'
            self.clean = True
        else:
            print '[Paster ERROR] no paste on port 9992'
        while self.clean:
            try:
                conn,addr = self.sock.accept()
                print '[Paster] Got copy from', addr
            except socket.timeout:
                pass
            except socket.error, e:
                if self.clean == False:
                    print "[Paster] Socket Error /return : "+str(e)
                    return
                else:
                    print "[Paster] Socket Error /break : "+str(e)
                    break
            else:
                data = conn.recv(4096)
                if data :
                    l=len(data)
                    print "[DEBUG] received data : "+data+"/"+str(l)+"/"+str(data.find("\n"))
                    if data.find('\n')==-1 and data.find('\r')==-1:
                        if data.find("#?#")!=-1:
                            print "[DEBUG] adding to grid"
                            fc=open(self.parent.target_dir+"grid.txt","a")
                            fc.write(data+"\n")
                            fc.close()
                        elif data.find("#!#")!=-1:
                            print "[DEBUG] adding to board"
                            fc=open(self.parent.target_dir+"board.txt","a")
                            fc.write(data+"\n")
                            fc.close()
                        elif data.find("#-#")!=-1:
                            print "[DEBUG] adding to wargames"
                            fc=open(self.parent.target_dir+"wargames.txt","a")
                            fc.write(data+"\n")
                            fc.close()
                    conn.close()
        print '[Paster] done'
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
                print "[Error] no grid.txt file in "+self.target_dir
                grid_fail = grid_fail + 1
        else:
            grid_fail = 0
        if not os.path.exists(self.target_dir+"board.txt"):
            board_fail = 0
            try:
                fc = open(self.target_dir+'board.txt', 'wb')
                fc.close()
            except:
                print "[Error] no board.txt file in "+self.target_dir
                board_fail = board_fail + 1
        else:
            board_fail = 0
        if not os.path.exists(self.target_dir+"wargames.txt"):
            wargames_fail = 0
            try:
                fc = open(self.target_dir+'wargames.txt', 'wb')
                fc.close()
            except:
                print "[Error] no wargames.txt file in "+self.target_dir
                wargames_fail = wargames_fail + 1
        else:
            wargames_fail = 0
        if not os.access(self.target_dir+"grid.txt",os.W_OK):
            print "[Error] write access denied for grid file in "+self.target_dir
            grid_fail = grid_fail + 1
        if not os.access(self.target_dir+"board.txt",os.W_OK):
            print "[Error] write access denied for board file in "+self.target_dir
            board_fail = board_fail + 1
        if not os.access(self.target_dir+"wargames.txt",os.W_OK):
            print "[Error] write access denied for wargames file in "+self.target_dir
            wargames_fail = wargames_fail + 1
        if grid_fail > 0 and board_fail > 0 and wargames_fail > 0:
            print "[Error] grid, board and wargames are unuseable. Aborting..."
            sys.exit(2)
        self.paster = Paster(self)
        self.awake = False
        print "[Grider] Having sweet dreams..."

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
            print("[Grider Warning] socket busy, connection failed on port " + str(port))
        return s

    def run(self):
        self.dream()
        try:
            self.paster.start()
            if self.paster.clean:
                print "[Grider] Advancing time in another space (waiting for server)"+os.linesep
                time.sleep(1)
            while self.paster.clean:
                print "[Grider] Advancing time in another space (waiting for server)"+os.linesep
                time.sleep(1)
            print "\n[Grider] sheets are all up and ready"
            while self.paster.clean:
                time.sleep(1)
        except:
            traceback.print_exc()
        self.cut()
        print "[Grider] finished"
        
    def cut(self):
        self.paster.clean=False
        self.paster.join()

if __name__ == "__main__":
    try:
        print("\nInitiating copy/paste functions ...\n")
        print '='*22 + '\n'
        app = Grider()
        app.start()
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\nTerminating copy/paste functions...\n")
        app.cut()
    except Exception, e:
        traceback.print_exc()
        print ("\n[Error] - Something wrong trying to copy/paste to the grid...!\n")
