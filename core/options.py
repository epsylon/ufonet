#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - DDoS Botnet via Web Abuse - 2013/2014/2015/2016 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import optparse

class UFONetOptions(optparse.OptionParser):
    def __init__(self, *args):
        self.zombies_file = "botnet/zombies.txt" # set source path to retrieve 'zombies'
        self.aliens_file = "botnet/aliens.txt" # set source path to retrieve 'aliens'
        self.droids_file = "botnet/droids.txt" # set source path to retrieve 'droids'
        self.ucavs_file = "botnet/ucavs.txt" # set source path to retrieve 'ucavs'
        self.rpcs_file = "botnet/rpcs.txt" # set source path to retrieve 'rpcs'
        self.zombies = int(self.extract_zombies())
        self.aliens = int(self.extract_aliens())
        self.droids = int(self.extract_droids())
        self.ucavs = int(self.extract_ucavs())
        self.rpcs = int(self.extract_rpcs())
        self.total_botnet = str(self.zombies+self.aliens+self.droids+self.ucavs+self.rpcs)
        optparse.OptionParser.__init__(self, 
                           description='\nUFONet - DDoS Botnet via Web Abuse - by psy',
                           prog='UFONet.py',
                           version='\nVersion: v0.8 - U-NATi0n!\n')
        self.add_option("-v", "--verbose", action="store_true", dest="verbose", help="active verbose on requests")
        self.add_option("--update", action="store_true", dest="update", help="check for latest stable version")
        self.add_option("--check-tor", action="store_true", dest="checktor", help="check to see if Tor is used properly")
        #self.add_option("--force-ssl", action="store_true", dest="forcessl", help="force usage of SSL/HTTPS requests")
        self.add_option("--force-yes", action="store_true", dest="forceyes", help="set 'YES' to all questions")
        self.add_option("--gui", action="store_true", dest="web", help="run GUI (UFONet Web Interface)")
        group8 = optparse.OptionGroup(self, "*Tools*")
        group8.add_option("--crypter", action="store_true", dest="cryptomsg", help="Encrypt/Decrypt messages using AES256+HMAC-SHA1")
        self.add_option_group(group8)
        group1 = optparse.OptionGroup(self, "*Configure Request(s)*")
        group1.add_option("--proxy", action="store", dest="proxy", help="Use proxy server (tor: 'http://127.0.0.1:8118')")
        group1.add_option("--user-agent", action="store", dest="agent", help="Use another HTTP User-Agent header (default SPOOFED)")
        group1.add_option("--referer", action="store", dest="referer", help="Use another HTTP Referer header (default SPOOFED)")
        group1.add_option("--host", action="store", dest="host", help="Use another HTTP Host header (default NONE)")
        group1.add_option("--xforw", action="store_true", dest="xforw", help="Set your HTTP X-Forwarded-For with random IP values")
        group1.add_option("--xclient", action="store_true", dest="xclient", help="Set your HTTP X-Client-IP with random IP values")
        group1.add_option("--timeout", action="store", dest="timeout", type="int", help="Select your timeout (default 10)")
        group1.add_option("--retries", action="store", dest="retries", type="int", help="Retries when the connection timeouts (default 1)")
        group1.add_option("--threads", action="store", dest="threads", type="int", help="Maximum number of concurrent HTTP requests (default 5)") 
        group1.add_option("--delay", action="store", dest="delay", type="int", help="Delay in seconds between each HTTP request (default 0)")
        self.add_option_group(group1)
        group2 = optparse.OptionGroup(self, "*Search for 'Zombies'*")
        group2.add_option("-s", action="store", dest="search", help="Search from a 'dork' (ex: -s 'proxy.php?url=')")
        group2.add_option("--sd", action="store", dest="dorks", help="Search from 'dorks' file (ex: --sd 'botnet/dorks.txt')")
        group2.add_option("--sn", action="store", dest="num_results", help="Set max number of results for engine (default 10)")
        group2.add_option("--se", action="store", dest="engine", help="Search engine to use for 'dorking' (default: bing)")
        group2.add_option("--sa", action="store_true", dest="allengines", help="Search massively using all search engines")
        self.add_option_group(group2)
        group3 = optparse.OptionGroup(self, "*Test Botnet*")
        group3.add_option("-t", action="store", dest="test", help="Update 'zombies' status (ex: -t 'botnet/zombies.txt')")
        group3.add_option("--attack-me", action="store_true", dest="attackme", help="Order 'zombies' to attack you (NAT required!)")
        group3.add_option("--test-rpc", action="store_true", dest="testrpc", help="Update 'xml-rpc' reflectors status")
        self.add_option_group(group3)
        group4 = optparse.OptionGroup(self, "*Community*")
        group4.add_option("--download-zombies", action="store_true", dest="download", help="Download 'zombies' from Community 'blackhole'")
        group4.add_option("--upload-zombies", action="store_true", dest="upload", help="Upload your 'zombies' to Community 'blackhole'")
        group4.add_option("--blackhole", action="store_true", dest="blackhole", help="Create a 'blackhole' to share your 'zombies'")
        group4.add_option("--up-to", action="store", dest="upip", help="Upload your 'zombies' to a 'blackhole'")
        group4.add_option("--down-from", action="store", dest="dip", help="Download your 'zombies' from a 'blackhole'")
        self.add_option_group(group4)
        group5 = optparse.OptionGroup(self, "*Research Target*")
        group5.add_option("-i", action="store", dest="inspect", help="Search biggest file (ex: -i 'http(s)://target.com')")
        #group5.add_option("-c", action="store", dest="crawl", help="Search places to attack (ex: -c http(s)://target.com)")
        self.add_option_group(group5)
        group6 = optparse.OptionGroup(self, "*Configure Attack(s)*")
        group6.add_option("--no-head", action="store_true", dest="disablehead", help="Disable status check: 'Is target up?'")
        group6.add_option("--no-aliens", action="store_true", dest="disablealiens", help="Disable 'aliens' web abuse")
        group6.add_option("--no-droids", action="store_true", dest="disabledroids", help="Disable 'droids' redirectors")
        group6.add_option("--no-ucavs", action="store_true", dest="disableisup", help="Disable 'ucavs' checkers")
        group6.add_option("--no-rpcs", action="store_true", dest="disablerpcs", help="Disable 'xml-rpcs' reflectors")
        group6.add_option("-r", action="store", dest="rounds", help="Set number of rounds (default: 1)")
        group6.add_option("-b", action="store", dest="place", help="Set place to attack (ex: -b '/path/big.jpg')")
        group6.add_option("-a", action="store", dest="target", help="Start Web DDoS attack (ex: -a 'http(s)://target.com')")
        self.add_option_group(group6)
        group7 = optparse.OptionGroup(self, "*Special Attack(s)*")
        group7.add_option("--db", action="store", dest="dbstress", help="Set db stress input point (ex: --db 'search.php?q=')")
        self.add_option_group(group7)

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

    def get_options(self, user_args=None):
        (options, args) = self.parse_args(user_args)
        if (not options.test and not options.testrpc and not options.target and not options.checktor and not options.search and not options.dorks and not options.inspect and not options.update and not options.download and not options.upload and not options.web and not options.attackme and not options.upip and not options.dip and not options.blackhole and not options.cryptomsg):
            print '='*75, "\n"
            print "888     888 8888888888 .d88888b.  888b    888          888    "   
            print "888     888 888        d88P" "Y888b  8888b   888          888    "
            print "888     888 888       888     888 88888b  888          888    "
            print "888     888 8888888   888     888 888Y88b 888  .d88b.  888888 "
            print "888     888 888       888     888 888 Y88b888 d8P  Y8b 888    "
            print "888     888 888       888     888 888  Y88888 88888888 888    "
            print "Y88b. .d88P 888       Y88b. .d88P 888   Y8888 Y8b.     Y88b.  "
            print " 'Y88888P'  888        'Y88888P'  888    Y888  'Y8888   'Y8888"                                 
            print self.description, "\n"
            print '='*75, "\n"
            print 'Total bots:', self.total_botnet, "= [ Z:" + str(self.zombies) + " + A:" + str(self.aliens) + " + D:" + str(self.droids) + " + U:" + str(self.ucavs) + " + R:" + str(self.rpcs) + " ]" + "\n"
            print '='*75, "\n"
            print "-> For HELP use: -h or --help"
            print "\n-> For WEB interface use: --gui\n"
            print '='*75, "\n"
            return False
        return options
