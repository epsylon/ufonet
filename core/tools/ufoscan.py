#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - Denial of Service Toolkit - 2018 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys, time, urlparse

try:
    from scapy.all import *
except:
    print "\nError importing: scapy lib. \n\n To install it on Debian based systems:\n\n $ 'sudo apt-get install python-scapy' or 'pip install scapy'\n"
    sys.exit(2)

# UFONet port scanner (UFOSCAN) class
def randInt():
    x = random.randint(1,65535) # TCP ports
    return x
 
def scan(self, ip, port, openp, closed):
    src_port = RandShort()
    seq = randInt()
    window = randInt()
    p = IP(dst=ip)/TCP(sport=src_port, dport=port, seq=seq, window=window, flags='S')
    resp = sr1(p, timeout=2)
    if str(type(resp)) == "<type 'NoneType'>":
        closed = closed + 1
    elif resp.haslayer(TCP):
        if resp.getlayer(TCP).flags == 0x12:
            send_rst = sr(IP(dst=ip)/TCP(sport=src_port, dport=port, flags='AR'), timeout=1)
            openp.append(port) # open port found!
            print "\n" + "="*54
            print "[Info] [AI] [UFOSCAN] OPEN port found! [ " + str(port) + " ]"
            print "="*54 + "\n"
        elif resp.getlayer(TCP).flags == 0x14:
            closed = closed + 1
    return openp, closed

def is_up(ip):
    p = IP(dst=ip)/ICMP()
    resp = sr1(p, timeout=10)
    if resp == None:
        return False
    elif resp.haslayer(ICMP):
        return True

class UFOSCAN(object):
    def scanning(self, target, portX, portY):
        print "[Info] [AI] [UFOSCAN] Emitting X-Ray into range: [ "+str(portX)+"-"+str(portY)+" ]\n"
        print "="*74, "\n"
        if target.startswith('http://'):
            target = target.replace('http://','')
        elif target.startswith('https://'):
            target = target.replace('https://','')
        else:
            print "[Error] [AI] [UFOSCAN] Target url not valid ("+target+")! -> It should starts with 'http(s)://'\n"
            return
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
            print "[Info] [AI] [UFOSCAN] Sending message '1/0 %====D 2 Ur ;-0' to 'localhost' -> [OK!]\n"
            return
        start_time = time.time()
        try:
            ports = range(int(portX), int(portY+1))
        except:
            portX = 1
            portY = 1024 # 1024
            print "[Info] [AI] [UFOSCAN] Not any range of ports selected. Using by default: [ 1-1024 ]\n"
            ports = range(int(portX), int(portY+1))
        portX = str(portX)
        portY = str(portY+1)
        if is_up(ip):
            openp = []
            closed = 0
            print "\n" + "="*44
            print "[Info] [AI] [UFOSCAN] Host %s is UP!" % ip
            print "="*44
            print "-"*22
            for port in ports:
                openp, closed = scan(self, ip, port, openp, closed)
            duration = time.time()-start_time
            print "-"*22
            print "="*44, "\n"
            print "[Info] [AI] [UFOSCAN] Scan completed in: [ %s ]" % duration
            if closed == len(ports):
                print "\n[Info] [AI] [UFOSCAN] [ %s/%d ] CLOSED ports. -> [Exiting!]\n" % (closed, len(ports)-1)
            else:
                print "\n[Info] [AI] [UFOSCAN] [ %s/%d ] OPEN ports FOUND!\n" % (len(openp), len(ports)-1)
                print "    [-] Target: [ " + str(ip) + " ]\n"
                for o in openp:
                    print "      [+] OPEN PORT: [ " + str(o) + " ]"
                print ""
        else:
            duration = time.time()-start_time
            print "-"*22
            print "="*44, "\n"
            print "[Info] [AI] [UFOSCAN] Host %s is DOWN!" % ip
            print "\n[Info] [AI] [UFOSCAN] Scan completed in: [ %s ]" % duration + "\n"
