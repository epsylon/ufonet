#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import optparse, math

class UFONetOptions(optparse.OptionParser):
    def __init__(self, *args):
        self.zombies_file = "botnet/zombies.txt" # set source path to retrieve 'zombies'
        self.aliens_file = "botnet/aliens.txt" # set source path to retrieve 'aliens'
        self.droids_file = "botnet/droids.txt" # set source path to retrieve 'droids'
        self.ucavs_file = "botnet/ucavs.txt" # set source path to retrieve 'ucavs'
        self.rpcs_file = "botnet/rpcs.txt" # set source path to retrieve 'rpcs'
        self.dnss_file = "botnet/dns.txt" # set source path to retrieve 'dnss'
        self.ntps_file = "botnet/ntp.txt" # set source path to retrieve 'ntps'
        self.snmps_file = "botnet/snmp.txt" # set source path to retrieve 'snmp'
        self.dorks_file = "botnet/dorks.txt" # set source path to retrieve 'dorks'
        self.sengines = self.extract_sengines()
        self.zombies = int(self.extract_zombies())
        self.aliens = int(self.extract_aliens())
        self.droids = int(self.extract_droids())
        self.ucavs = int(self.extract_ucavs())
        self.rpcs = int(self.extract_rpcs())
        self.dnss = int(self.extract_dnss())
        self.ntps = int(self.extract_ntps())
        self.snmps = int(self.extract_snmps())
        self.dorks = int(self.extract_dorks())
        self.tools = self.extract_tools()
        self.etools = self.extra_tools()
        self.weapons = self.extract_weapons()
        self.ebotnet = self.electronic_botnet()
        self.eweapons = self.extra_weapons()
        self.total_botnet = str(self.zombies+self.aliens+self.droids+self.ucavs+self.rpcs+self.dnss+self.ntps+self.snmps)
        self.d_energy = self.extract_d_energy()
        self.y_energy = self.extract_y_energy()
        self.x_energy = self.extract_x_energy()
        self.formula = self.formula_x_energy()
        optparse.OptionParser.__init__(self, 
        description='\n{(D)enial(OFF)ensive(S)ervice[ToolKit]}-{by_(io=psy+/03c8.net)}',
        prog='./ufonet',
        version='\nCode: 1.6 '+"\u25BC "+'[MR3] [ M4RAuD3R ] '+"\u25BC"+'\n')
        self.add_option("-v", "--verbose", action="store_true", dest="verbose", help="active verbose on requests")
        self.add_option("--examples", action="store_true", dest="examples", help="print some examples")
        self.add_option("--timeline", action="store_true", dest="timeline", help="show program's code timeline")
        self.add_option("--update", action="store_true", dest="update", help="check for latest stable version")
        self.add_option("--check-tor", action="store_true", dest="checktor", help="check to see if Tor is used properly")
        self.add_option("--force-ssl", action="store_true", dest="forcessl", help="force usage of SSL/HTTPS requests")
        self.add_option("--force-yes", action="store_true", dest="forceyes", help="set 'YES' to all questions")
        self.add_option("--gui", action="store_true", dest="web", help="start GUI (UFONet Web Interface)")
        group9 = optparse.OptionGroup(self, "*Tools*")
        group9.add_option("--crypter", action="store_true", dest="cryptomsg", help="Crypt/Decrypt messages using AES256+HMAC-SHA1")
        group9.add_option("--network", action="store_true", dest="shownet", help="Show info about your network (MAC, IPs)")
        group9.add_option("--xray", action="store", dest="xray", help="Fast port scanner (ex: --xray 'http(s)://target.com')")
        group9.add_option("--xray-ps", action="store", dest="xrayps", help="Set range of ports to scan (ex: --xray-ps '1-1024')")
        self.add_option_group(group9)
        group1 = optparse.OptionGroup(self, "*Configure Request(s)*")
        group1.add_option("--proxy", action="store", dest="proxy", help="Use proxy server (ex: --proxy 'http://127.0.0.1:8118')")
        group1.add_option("--user-agent", action="store", dest="agent", help="Use another HTTP User-Agent header (default: SPOOFED)")
        group1.add_option("--referer", action="store", dest="referer", help="Use another HTTP Referer header (default: SPOOFED)")
        group1.add_option("--host", action="store", dest="host", help="Use another HTTP Host header (default: NONE)")
        group1.add_option("--xforw", action="store_true", dest="xforw", help="Set your HTTP X-Forwarded-For with random IP values")
        group1.add_option("--xclient", action="store_true", dest="xclient", help="Set your HTTP X-Client-IP with random IP values")
        group1.add_option("--timeout", action="store", dest="timeout", type="int", help="Select your timeout (default: 5)")
        group1.add_option("--retries", action="store", dest="retries", type="int", help="Retries when the connection timeouts (default: 0)")
        group1.add_option("--threads", action="store", dest="threads", type="int", help="Max number of concurrent HTTP requests (default: 5)") 
        group1.add_option("--delay", action="store", dest="delay", type="int", help="Delay between each HTTP request (default: 0)")
        self.add_option_group(group1)
        group2 = optparse.OptionGroup(self, "*Search for 'Zombies'*")
        group2.add_option("--auto-search", action="store_true", dest="autosearch", help="Search automatically for 'zombies' (may take time!)")
        group2.add_option("-s", action="store", dest="search", help="Search from a 'dork' (ex: -s 'proxy.php?url=')")
        group2.add_option("--sd", action="store", dest="dorks", help="Search from 'dorks' file (ex: --sd 'botnet/dorks.txt')")
        group2.add_option("--sn", action="store", dest="num_results", help="Set max number of results for engine (default: 10)")
        group2.add_option("--se", action="store", dest="engine", help="Search engine for 'dorking' (default: DuckDuckGo)")
        group2.add_option("--sa", action="store_true", dest="allengines", help="Search massively using all engines (may take time!)")
        group2.add_option("--sax", action="store", dest="ex_engine", help="Exclude engines when mass searching (ex: 'Bing,Yahoo')")
        self.add_option_group(group2)
        group3 = optparse.OptionGroup(self, "*Test Botnet*")
        group3.add_option("--test-offline", action="store_true", dest="testoffline", help="Fast check to discard offline bots")
        group3.add_option("--test-all", action="store_true", dest="testall", help="Update ALL botnet status (may take time!)")
        group3.add_option("-t", action="store", dest="test", help="Update 'zombies' status (ex: -t 'botnet/zombies.txt')")
        group3.add_option("--test-rpc", action="store_true", dest="testrpc", help="Update 'reflectors' status (ex: --test-rpc)")
        group3.add_option("--attack-me", action="store_true", dest="attackme", help="Order 'zombies' to attack you (NAT required!)")
        self.add_option_group(group3)
        group4 = optparse.OptionGroup(self, "*Community*")
        group4.add_option("--grider", action="store_true", dest="grider", help="Create a 'grider' to share 'stats/wargames/messages'")
        group4.add_option("--blackhole", action="store_true", dest="blackhole", help="Generate a 'blackhole' to share 'zombies'")
        group4.add_option("--up-to", action="store", dest="upip", help="Upload 'zombies' to IP (ex: --up-to '<IP>')")
        group4.add_option("--down-from", action="store", dest="dip", help="Download 'zombies' from IP (ex: --down-from '<IP>')")
        group4.add_option("--upload-zombies", action="store_true", dest="upload", help="Upload 'zombies' to Community")
        group4.add_option("--download-zombies", action="store_true", dest="download", help="Download 'zombies' from Community")
        group4.add_option("--upload-github", action="store_true", dest="upload_github", help="Upload 'zombies' to GitHub")
        group4.add_option("--download-github", action="store_true", dest="download_github", help="Download 'zombies' from GitHub")
        self.add_option_group(group4)
        group5 = optparse.OptionGroup(self, "*Research Target*")
        group5.add_option("-i", action="store", dest="inspect", help="Search biggest file (ex: -i 'http(s)://target.com')")
        group5.add_option("-x", action="store", dest="abduction", help="Examine webserver configuration (+CVE, +WAF detection)")
        self.add_option_group(group5)
        group6 = optparse.OptionGroup(self, "*Configure Attack(s)*")
        group6.add_option("-a", action="store", dest="target", help="[DDoS] attack a target (ex: -a 'http(s)://target.com')")
        group6.add_option("-f", action="store", dest="target_list", help="[DDoS] attack a list of targets (ex: -f 'targets.txt')")
        group6.add_option("-b", action="store", dest="place", help="Set place to attack (ex: -b '/path/big.jpg')")
        group6.add_option("-r", action="store", dest="rounds", help="Set number of rounds (ex: -r '1000') (default: 1)")
        self.add_option_group(group6)
        group7 = optparse.OptionGroup(self, "*Extra Configuration(s)*")
        group7.add_option("--no-droids", action="store_true", dest="disabledroids", help="Disable 'DROIDS' redirectors")
        group7.add_option("--no-ucavs", action="store_true", dest="disableucavs", help="Disable 'UCAVS' checkers")
        group7.add_option("--no-aliens", action="store_true", dest="disablealiens", help="Disable 'ALIENS' web abuse")
        group7.add_option("--no-rpcs", action="store_true", dest="disablerpcs", help="Disable 'XML-RPCs' reflectors")
        group7.add_option("--no-head", action="store_true", dest="disablehead", help="Disable 'Is target up?' starting check")
        group7.add_option("--no-scan", action="store_true", dest="disablescanner", help="Disable 'Scan shields' round check")
        group7.add_option("--no-purge", action="store_true", dest="disablepurge", help="Disable 'Zombies purge' round check")
        group7.add_option("--expire", action="store", dest="expire", help="Set expire time for 'Zombies purge' (default: 30)")
        self.add_option_group(group7)
        group8 = optparse.OptionGroup(self, "*Extra Attack(s)*")
        group8.add_option("--fraggle", action="store", dest="fraggle", help="[DDoS] 'UDP amplification' (ex: --fraggle 101)")
        group8.add_option("--tachyon", action="store", dest="tachyon", help="[DDoS] 'DNS amplification' (ex: --tachyon 101)")
        group8.add_option("--monlist", action="store", dest="monlist", help="[DDoS] 'NTP amplification' (ex: --monlist 101)")
        group8.add_option("--smurf", action="store", dest="smurf", help="[DDoS] 'ICMP amplification' (ex: --smurf 101)")
        group8.add_option("--sniper", action="store", dest="sniper", help="[DDoS] 'SNMP amplification' (ex: --sniper 101)")
        group8.add_option("--spray", action="store", dest="spray", help="[DDoS] 'TCP-SYN reflection' (ex: --spray 101)")
        group8.add_option("--db", action="store", dest="dbstress", help="[DDoS] 'HTTP-DB flood' (ex: --db 'search.php?q=')")
        group8.add_option("--loic", action="store", dest="loic", help="[ DoS] 'HTTP-FAST flood' (ex: --loic 101)")
        group8.add_option("--loris", action="store", dest="loris", help="[ DoS] 'HTTP-SLOW flood' (ex: --loris 101)")
        group8.add_option("--ufosyn", action="store", dest="ufosyn", help="[ DoS] 'TCP-SYN flood' (ex: --ufosyn 101)")
        group8.add_option("--xmas", action="store", dest="xmas", help="[ DoS] 'TCP-XMAS flood' (ex: --xmas 101)")
        group8.add_option("--nuke", action="store", dest="nuke", help="[ DoS] 'TCP-STARVATION flood' (ex: --nuke 101)")
        group8.add_option("--ufoack", action="store", dest="ufoack", help="[ DoS] 'TCP-ACK flood' (ex: --ufoack 101)")
        group8.add_option("--uforst", action="store", dest="uforst", help="[ DoS] 'TCP-RST flood' (ex: --uforst 101)")
        group8.add_option("--droper", action="store", dest="droper", help="[ DoS] 'IP-FRAGMENTATION flood' (ex: --droper 101)")
        group8.add_option("--overlap", action="store", dest="overlap", help="[ DoS] 'IP-OVERLAP flood' (ex: --overlap 101)")
        group8.add_option("--pinger", action="store", dest="pinger", help="[ DoS] 'ICMP flood' (ex: --pinger 101)")
        group8.add_option("--ufoudp", action="store", dest="ufoudp", help="[ DoS] 'UDP flood' (ex: --ufoudp 101)")
        self.add_option_group(group8)

    def extract_sengines(self):
        sengines = ["Yahoo", "Bing", "DuckDuckGo"]
        sengines = len(sengines)
        return sengines

    def extract_tools(self):
        tools = ["CYPTER", "NETWORK", "XRAY", "WARPER", "INSPECTOR", "ABDUCTOR", "AI.BOTNET", "AI.GUI", "AI.STATS", "AI.EVASIVE", "BLACKHOLE", "AI.LINKS", "AI.STREAMS", "AI.BROWSER", "AI.GLOBALNET", "AI.GAMES"]
        tools = len(tools)
        return tools

    def extra_tools(self):
        etools =  '\n     _> ABDUCTOR                   * Defensive Shield Detector'
        etools += '\n     _> AI.BOTNET                  * Intelligent Attack System'
        etools += '\n     _> AI.BROWSER                 * Private Sandbox Browser'
        etools += '\n     _> AI.EVASIVE                 * Automatic Evasion System'
        etools += '\n     _> AI.GAMES                   * Fun & Games Center'
        etools += '\n     _> AI.GEO                     * Geomapping System'
        etools += '\n     _> AI.GLOBAL_NET              * Global UFONET Network'
        etools += '\n     _> AI.LIBRARY                 * Public (data.Links) Library'
        etools += '\n     _> AI.STATS                   * Live Stats Reporter'
        etools += '\n     _> AI.STREAMING               * Video (data.Streams) Player'
        etools += '\n     _> AI.WEB                     * Graphical User Web-Interface'
        etools += '\n     _> BLACKHOLE                  * Warper (p2p.Botnet) Generator'
        etools += '\n     _> CRYPTER                    * Telegram (crypto.Community) System'
        etools += '\n     _> INSPECTOR                  * Objective Scanning Crawler'
        etools += '\n     _> AI.NETWORK                 * Network (MACs, IPs) Reporter'
        etools += '\n     _> XRAY                       * Ultra-Fast Ports Scanner'
        return etools

    def extract_weapons(self):
        weapons = ["SMURF", "TACHYON", "MONLIST", "SNIPER", "SPRAY", "DBSTRESS", "LOIC", "LORIS", "UFOSYN", "XMAS", "NUKE", "UFOACK", "UFORST", "DROPER", "OVERLAP", "PINGER", "UFOUPD", "FRAGGLE"]
        weapons = len(weapons)
        return weapons

    def extra_weapons(self):
        eweapons = '\n     _> FRAGGLE                    * [DDoS] UDP Amplificator'
        eweapons += '\n     _> TACHYON                    * [DDoS] DNS Amplificator'
        eweapons += '\n     _> MONLIST                    * [DDoS] NTP Amplificator'
        eweapons += '\n     _> SMURF                      * [DDoS] ICMP Amplificator'
        eweapons += '\n     _> SNIPER                     * [DDoS] SNMP Amplificator'
        eweapons += '\n     _> SPRAY                      * [DDoS] TCP SYN Reflector'
        eweapons += '\n     _> DBSTRESS                   * [DDoS] HTTP-DB Stresser'
        eweapons += '\n     _> LOIC                       * [ DoS] HTTP-FAST Requester'
        eweapons += '\n     _> LORIS                      * [ DoS] HTTP-SLOW Requester'
        eweapons += '\n     _> UFOSYN                     * [ DoS] TCP-SYN Flooder'
        eweapons += '\n     _> XMAS                       * [ DoS] TCP-XMAS Flooder'
        eweapons += '\n     _> NUKE                       * [ DoS] TCP-STARVATION Flooder'
        eweapons += '\n     _> UFOACK                     * [ DoS] TCP-ACK Flooder'
        eweapons += '\n     _> UFORST                     * [ DoS] TCP-RST Flooder'
        eweapons += '\n     _> DROPER                     * [ DoS] IP-FRAGMENTATION Flooder'
        eweapons += '\n     _> OVERLAP                    * [ DoS] IP-OVERLAP Flooder'
        eweapons += '\n     _> PINGER                     * [ DoS] ICMP Flooder'
        eweapons += '\n     _> UFOUDP                     * [ DoS] UDP Flooder'
        return eweapons

    def electronic_botnet(self):
        ebotnet = '\n     _> ZOMBIES       [ '+ format(int(self.zombies), '08d')+ ' ]   * HTTP GET (simple)'
        ebotnet += '\n     _> DROIDS        [ '+ format(int(self.droids), '08d')+ ' ]   * HTTP GET (complex)'
        ebotnet += '\n     _> UCAVs         [ '+ format(int(self.ucavs), '08d')+ ' ]   * WebAbuse (multiple)'
        ebotnet += '\n     _> ALIENS        [ '+ format(int(self.aliens), '08d')+ ' ]   * HTTP POST'
        ebotnet += '\n     _> X-RPCs        [ '+ format(int(self.rpcs), '08d')+ ' ]   * XML-RPC'
        ebotnet += '\n     _> DNSs          [ '+ format(int(self.dnss), '08d')+ ' ]   * DNS'
        ebotnet += '\n     _> NTPs          [ '+ format(int(self.ntps), '08d')+ ' ]   * NTP'
        ebotnet += '\n     _> SNMPs         [ '+ format(int(self.snmps), '08d')+ ' ]   * SNMP'
        return ebotnet

    def extract_zombies(self):
        try:
            f = open(self.zombies_file)
            zombies = len(f.readlines())
            f.close()
        except:
            zombies = "broken!"
        return zombies

    def extract_aliens(self):
        try:
            f = open(self.aliens_file)
            aliens = len(f.readlines())
            f.close()
        except:
            aliens = "broken!"
        return aliens

    def extract_droids(self):
        try:
            f = open(self.droids_file)
            droids = len(f.readlines())
            f.close()
        except:
            droids = "broken!"
        return droids

    def extract_ucavs(self):
        try:
            f = open(self.ucavs_file)
            ucavs = len(f.readlines())
            f.close()
        except:
            ucavs = "broken!"
        return ucavs

    def extract_rpcs(self):
        try:
            f = open(self.rpcs_file)
            rpcs = len(f.readlines())
            f.close()
        except:
            rpcs = "broken!"
        return rpcs

    def extract_dnss(self):
        try:
            f = open(self.dnss_file)
            dnss = len(f.readlines())
            f.close()
        except:
            dnss = "broken!"
        return dnss

    def extract_ntps(self):
        try:
            f = open(self.ntps_file)
            ntps = len(f.readlines())
            f.close()
        except:
            ntps = "broken!"
        return ntps

    def extract_snmps(self):
        try:
            f = open(self.snmps_file)
            snmps = len(f.readlines())
            f.close()
        except:
            snmps = "broken!"
        return snmps

    def extract_dorks(self):
        try:
            f = open(self.dorks_file)
            dorks = len(f.readlines())
            f.close()
        except:
            dorks = "broken!"
        return dorks

    def extract_d_energy(self): # Dark Energy Density = (Fluctuations)*(Baryon)*(Event horizont sphere)/(Age of the Universe)
        d_density = 0.8288*0.05
        d_sphere = d_density * 4 * math.pi * 16 **2
        d_energy = d_sphere/13.64**2
        return d_energy

    def extract_y_energy(self): # Y-Energy = (Momento Entropy)*(Energy of Invariability lost)  
        y_entropy = int(self.total_botnet)+int(self.dorks)+int(self.sengines)+int(self.tools)+int(self.weapons)
        y_energy = y_entropy * 0.49
        return y_energy

    def extract_x_energy(self): # X-Energy = (Y-Energy)*(Dark Energy Density)
        x_energy = self.y_energy / self.d_energy
        return x_energy

    def formula_x_energy(self): # X-Energy Final Formula
        formula = 'X'+"\u2091"+''+"\N{SUBSCRIPT EIGHT}"' = '+"\u03A8"+'/'+"\u03A9"+''+"\u028C"+' = ('+"\u03A3"+''+"\u2091"+')/('+"\u03C3"+''+"\N{SUBSCRIPT EIGHT}"+'*'+"\u03A9"+'b*A'+"\u2091"+''+"\u2095"+'/t'+"\N{SUPERSCRIPT TWO}"+')\n                                   '+ str(self.y_energy) + '*0.49/0.8288*0.05*4'+"\u03A0"+'16'+"\N{SUPERSCRIPT TWO}"+'/13.64'+"\N{SUPERSCRIPT TWO}"+''
        return formula

    def get_options(self, user_args=None):
        (options, args) = self.parse_args(user_args)
        if (not options.test and not options.testrpc and not options.target and not options.target_list and not options.checktor and not options.search and not options.dorks and not options.inspect and not options.abduction and not options.update and not options.download and not options.download_github and not options.upload and not options.upload_github and not options.web and not options.attackme and not options.upip and not options.dip and not options.blackhole and not options.grider and not options.cryptomsg and not options.shownet and not options.xray and not options.timeline and not options.examples and not options.autosearch and not options.testoffline and not options.testall):
            print('='*75, "\n")
            print("888     888 8888888888 .d88888b.  888b    888          888    ")   
            print("888     888 888        d88P" "Y888b  8888b   888          888    ")
            print("888     888 888       888     888 88888b  888          888    ")
            print("888     888 8888888   888     888 888Y88b 888  .d88b.  888888 ")
            print("888     888 888       888     888 888 Y88b888 d8P  Y8b 888    ")
            print("888     888 888       888     888 888  Y88888 88888888 888    ")
            print("Y88b. .d88P 888       Y88b. .d88P 888   Y8888 Y8b.     Y88b.  ")
            print(" 'Y88888P'  888        'Y88888P'  888    Y888  'Y8888   'Y8888")                                 
            print(self.description, "\n")
            print('='*75)
            self.version = self.version.replace("\n","")
            print('\n  '+"\u25BC "+self.version+'\n')
            print("-"*75+"\n")
            print(' -> _BOTNET [DDoS]:   [', format(int(self.total_botnet), '08d'),'] '+"\u25BC"+' Bots (Available)'+ self.ebotnet)
            print('\n -> _DORKS:           [', format(int(self.dorks), '08d'), '] '+"\u25BC"+' Open Redirect (CWE-601) patterns')
            print('     _> ENGINES       [', format(int(self.sengines), '08d'), ']   * Dorking providers (Working)')
            print('\n -> _TOOLS:           [', format(int(self.tools), '08d'),'] '+"\u25BC"+' Extra Tools (Misc)'+self.etools)
            print('\n -> _WEAPONS:         [', format(int(self.weapons), '08d'),'] '+"\u25BC"+' Extra Attacks (DDoS & DoS)'+ self.eweapons)
            print('\n -> _X-ENERGY [X'+"\u2091"+''+"\N{SUBSCRIPT EIGHT}"+']:  [', format(int(self.x_energy), '08d'),'] '+"\u25BC"+' '+self.formula+'\n')
            print("-"*75+"\n")
            print(" -> _HELP:            ./ufonet --help (or ./ufonet -h)")
            print(' -> _EXAMPLES:        ./ufonet --examples')
            print("\n -> _WEB_INTERFACE:   ./ufonet --gui\n")
            print('='*75, "\n")
            return False
        return options
