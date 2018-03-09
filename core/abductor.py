#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - DDoS Botnet via Web Abuse - 2017 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import urllib, urllib2, ssl, random, socket, time, re
from urlparse import urlparse

# UFONet recognizance (abduction) class
class Abductor(object):
    def __init__(self,ufonet):
        self.ufonet=ufonet
        self.start = None
        self.stop = None 
        self.port = None
        self.ctx = ssl.create_default_context() # creating context to bypass SSL cert validation (black magic)
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

    def proxy_transport(self, proxy):
        proxy_url = self.ufonet.extract_proxy(proxy)
        proxy = urllib2.ProxyHandler({'https': proxy_url})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)

    def establish_connection(self, target):
        if target.endswith(""):
            target.replace("", "/")
        self.ufonet.user_agent = random.choice(self.ufonet.agents).strip() # suffle user-agent
        headers = {'User-Agent' : self.ufonet.user_agent, 'Referer' : self.ufonet.referer} # set fake user-agent and referer
        try:
            req = urllib2.Request(target, None, headers)
            if self.ufonet.options.proxy: # set proxy
                self.proxy_transport(self.ufonet.options.proxy)
                self.start = time.time()
                target_reply = urllib2.urlopen(req).read()
                header = urllib2.urlopen(req).info()
                self.stop = time.time()
            else:
                self.start = time.time()
                target_reply = urllib2.urlopen(req, context=self.ctx).read()
                header = urllib2.urlopen(req).info()
                self.stop = time.time()
        except: 
            print('[Error] - Unable to connect...\n')
            return #sys.exit(2)
        return target_reply, header

    def convert_size(self, size):
        import math
        if (size == 0):
            return '0B'
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size,1024)))
        p = math.pow(1024,i)
        s = round(size/p,2)
        return '%s %s' % (s,size_name[i])

    def convert_time(self, time):    
        return '%.2f' % time

    def extract_banner(self, header): # extract webserver banner
        try:
            banner = header["server"]
        except:
            banner = "NOT found!"
        try:
            via = header["via"]
        except: # return when fails performing query
            via = "NOT found!"
        return banner, via

    def extract_whois(self, domain): # extract whois data from target domain
        try:
            import whois
            d = whois.query(domain, ignore_returncode=True) # ignore return code
            if d.creation_date is None: # return when no creation date
                return
            else:
                print " -Registrant   : " + str(d.registrar)
                print " -Creation date: " + str(d.creation_date)
                print " -Expiration   : " + str(d.expiration_date)
                print " -Last update  : " + str(d.last_updated)
        except: # return when fails performing query
            return

    def extract_cve(self, banner): # extract Denial of Service vulnerabilities related with webserver banner from CVE database
        url = 'https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword'
        q = str(banner)
        query_string = { '':q}
        data = urllib.urlencode(query_string)
        target = url + data
        try:
            self.ufonet.user_agent = random.choice(self.ufonet.agents).strip() # suffle user-agent
            headers = {'User-Agent' : self.ufonet.user_agent, 'Referer' : self.ufonet.referer} # set fake user-agent and referer
            req = urllib2.Request(target, None, headers)
            if self.ufonet.options.proxy: # set proxy
                self.proxy_transport(self.ufonet.options.proxy)
                target_reply = urllib2.urlopen(req).read()
            else:
                target_reply = urllib2.urlopen(req, context=self.ctx).read()
        except: 
            return #sys.exit(2)
        if target_reply == "": # no records found
            return
        if "<b>0</b> CVE entries" in target_reply: # regex for: no CVE records found
            cve = "NOT found!"
        else:
            regex_s = '<td valign="top" nowrap="nowrap"><a href="(.+?)">' # regex magics
            pattern_s = re.compile(regex_s)
            cve = re.findall(pattern_s, target_reply)
        return cve

    def waf_detection(self, banner, target_reply):
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
        if signature in target_reply or signature in banner:
            waf = "VENDOR -> " + str(t) 
        else:
            waf = "FIREWALL NOT PRESENT (or not discovered yet)! ;-)\n"
        return waf
                  
    def abducting(self, target):
        try:
            target_reply, header = self.establish_connection(target)
        except:
            print "[Error] - Something wrong connecting to your target. Aborting...\n"
            return #sys.exit(2)
        if not target_reply:
            print "[Error] - Something wrong connecting to your target. Aborting...\n"
            return #sys.exit(2)
        print ' -Target URL:', target, "\n"
        try:
            if target.startswith("http://"):
                self.port = "80"
            if target.startswith("https://"):
                self.port = "443"
        except:
            self.port = "Error!"
        try:
            domain = urlparse(target)
            domain = domain.netloc
            if domain.startswith("www."):
                domain = domain.replace("www.", "")
        except:
            domain = "OFF"
        try:       
            ipv4 = socket.gethostbyname(domain)
        except:
            ipv4 = "OFF"
        try:
            ipv6 = socket.getaddrinfo(domain, port, socket.AF_INET6)
            ftpca = ipv6[0]
            ipv6 = ftpca[4][0]
        except:
            ipv6 = "OFF"
        print ' -IP    :', ipv4
        print ' -IPv6  :', ipv6
        print ' -Port  :', self.port
        print ' \n -Domain:', domain
        try:
            whois = self.extract_whois(domain)
        except:
            pass
        try:
            size = self.convert_size(len(target_reply))
        except:
            size = "Error!"
        try:
            time_required = self.stop - self.start
            load = self.convert_time(time_required)
        except:
            load = "Error!"
        try:
            banner, via = self.extract_banner(header)
        except:
            pass
        print '\n---------'
        print "\nTrying single visit broadband test (using GET)...\n"
        print ' -Bytes in :', size
        print ' -Load time:', load, "seconds\n"
        print '---------'
        print "\nDetermining webserver fingerprint (note that this value can be a fake)...\n"
        print ' -Banner:', banner 
        print ' -Vía   :', via , "\n"
        print '---------'
        print "\nSearching for extra Anti-DDoS protections...\n"
        waf = self.waf_detection(banner, target_reply)
        print ' -WAF/IDS: ' +  waf
        if 'VENDOR' in waf:
            print ' -NOTICE : This FIREWALL probably is using Anti-(D)DoS measures!', "\n"
        print '---------'
        if banner == "NOT found!":
            pass
        else:
            print "\nSearching at CVE (https://cve.mitre.org) for vulnerabilities...\n"
            try:
                cve = self.extract_cve(banner)
                if cve == None:
                    print ' -Reports: NOT found!', "\n"
                elif cve == "NOT found!":
                    print ' -Reports:', cve
                else:
                    print ' -Reports:'
                    for c in cve:
                        cve_info = c.replace("/cgi-bin/cvename.cgi?name=","")
                        print "\n        +", cve_info, "->", "https://cve.mitre.org" + c # 8 tab for zen
                print '\n---------'
            except:
                pass
        print "\n[Info] Abduction finished... ;-)\n"
