#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - DDoS Botnet via Web Abuse - 2013/2014/2015 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import optparse

class UFONetOptions(optparse.OptionParser):
    def __init__(self, *args):
        optparse.OptionParser.__init__(self, 
                           description='\nUFONet - DDoS Botnet via Web Abuse - by psy',
                           prog='UFONet.py',
                           version='\nVersion: v0.6 - Galactic Offensive!\n')
        self.add_option("-v", "--verbose", action="store_true", dest="verbose", help="active verbose on requests")
        self.add_option("--update", action="store_true", dest="update", help="check for latest stable version")
        self.add_option("--check-tor", action="store_true", dest="checktor", help="check to see if Tor is used properly")
        #self.add_option("--force-ssl", action="store_true", dest="forcessl", help="force usage of SSL/HTTPS requests")
        self.add_option("--force-yes", action="store_true", dest="forceyes", help="set 'YES' to all questions")
        self.add_option("--disableisup", action="store_true", dest="disableisup", help="disable external check of target's status")
        self.add_option("--gui", action="store_true", dest="web", help="run GUI (UFONet Web Interface)")
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
        group2.add_option("--sd", action="store", dest="dorks", help="Search from a list of 'dorks' (ex: --sd 'dorks.txt')")
        group2.add_option("--sn", action="store", dest="num_results", help="Set max number of results for engine (default 10)")
        group2.add_option("--se", action="store", dest="engine", help="Search engine to use for 'dorking' (default: duck)")
        group2.add_option("--sa", action="store_true", dest="allengines", help="Search massively using all search engines")
        self.add_option_group(group2)
        group3 = optparse.OptionGroup(self, "*Test Botnet*")
        group3.add_option("-t", action="store", dest="test", help="Update 'zombies' status (ex: -t 'zombies.txt')")
        group3.add_option("--attack-me", action="store_true", dest="attackme", help="Order 'zombies' to attack you (NAT required!)")
        self.add_option_group(group3)
        group4 = optparse.OptionGroup(self, "*Community*")
        group4.add_option("--download-zombies", action="store_true", dest="download", help="Download 'zombies' from Community server: Turina")
        group4.add_option("--upload-zombies", action="store_true", dest="upload", help="Upload your 'zombies' to Community server: Turina")
        group4.add_option("--blackhole", action="store_true", dest="blackhole", help="Create a 'blackhole' to share your 'zombies'")
        group4.add_option("--up-to", action="store", dest="upip", help="Upload your 'zombies' to a 'blackhole'")
        group4.add_option("--down-from", action="store", dest="dip", help="Download your 'zombies' from a 'blackhole'")
        self.add_option_group(group4)
        group5 = optparse.OptionGroup(self, "*Research Target*")
        group5.add_option("-i", action="store", dest="inspect", help="Search for biggest file (ex: -i 'http://target.com')")
        #group5.add_option("-c", action="store", dest="crawl", help="Search places to attack (ex: -c http(s)://target.com)")
        self.add_option_group(group5)
        group6 = optparse.OptionGroup(self, "*Configure Attack(s)*")
        group6.add_option("--disable-aliens", action="store_true", dest="disablealiens", help="Disable 'aliens' web abuse of test services")
        group6.add_option("--disable-isup", action="store_true", dest="disableisup", help="Disable check status 'is target up?'")
        group6.add_option("-r", action="store", dest="rounds", help="Set number of rounds (default: 1)")
        group6.add_option("-b", action="store", dest="place", help="Set place to attack (ex: -b '/path/big.jpg')")
        group6.add_option("-a", action="store", dest="target", help="Start Web DDoS attack (ex: -a 'http(s)://target.com')")
        self.add_option_group(group6)

    def get_options(self, user_args=None):
        (options, args) = self.parse_args(user_args)
        if (not options.test and not options.target and not options.checktor and not options.search and not options.dorks and not options.inspect and not options.update and not options.download and not options.upload and not options.web and not options.attackme and not options.upip and not options.dip and not options.blackhole):
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
            return False
        return options
