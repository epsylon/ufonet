#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
"""
UFONet - DDoS attacks via Web Abuse (XSS/CSRF) - 2013 - by psy

You should have received a copy of the GNU General Public License along
with masxssive; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import optparse

class UFONetOptions(optparse.OptionParser):
    def __init__(self, *args):
        optparse.OptionParser.__init__(self, 
                           description='\nUFONet - DDoS attacks via Web Abuse (XSS/CSRF) - 2013 - by psy',
                           prog='UFONet.py',
                           version='\nUFONet v0.1\n')

        group1 = optparse.OptionGroup(self, "Connections")
        group1.add_option("-v", "--verbose", action="store_true", dest="verbose", help="Active verbose on connections")
        group1.add_option("--proxy", action="store", dest="proxy", help="Use proxy server (tor: http://localhost:8118)")
        group1.add_option("--user-agent", action="store", dest="agent", help="Change your HTTP User-Agent header (default SPOOFED)")
        group1.add_option("--referer", action="store", dest="referer", help="Use another HTTP Referer header (default NONE)")                         
        #group1.add_option("--timeout", action="store", dest="timeout", type="int", help="Select your timeout (default 30)")
        #group1.add_option("--retries", action="store", dest="retries", type="int", help="Retries when the connection timeouts (default 1)")
        #group1.add_option("--threads", action="store", dest="threads", type="int", help="Maximum number of concurrent HTTP requests (default 5)") 
        #group1.add_option("--delay", action="store", dest="delay", type="int", help="Delay in seconds between each HTTP request (default 0)")
        self.add_option_group(group1)

        group2 = optparse.OptionGroup(self, "Botnet")
        group2.add_option("-t", action="store", dest="test", help="Test list of web 'zombie' servers (ex: -t zombies.txt)")
        self.add_option_group(group2)

        group3 = optparse.OptionGroup(self, "Attacks")
        group3.add_option("-a", action="store", dest="target", help="Start a Web DDoS attack (ex: -u http(s)://target.com)")
        group3.add_option("-r", action="store", dest="rounds", help="Set number of 'rounds' for the attack (default: 1)")
        self.add_option_group(group3)

    def get_options(self, user_args=None):
        (options, args) = self.parse_args(user_args)
        if (not options.test and not options.target):
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

