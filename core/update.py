#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - Denial of Service Toolkit - 2013/2018 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import os
from subprocess import PIPE
from subprocess import Popen as execute
        
class Updater(object):
    """     
    Update UFONet automatically from a .git repository
    """     
    def __init__(self):
        GIT_REPOSITORY = "https://code.03c8.net/epsylon/ufonet"
        GIT_REPOSITORY2 = "https://github.com/epsylon/ufonet"
        rootDir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', ''))
        if not os.path.exists(os.path.join(rootDir, ".git")):
            print "Not any .git repository found!\n"
            print "="*30
            print "\nTo have working this feature, you should clone UFONet with:\n"
            print "$ git clone %s" % GIT_REPOSITORY
            print "\nAlso you can try this other mirror:\n"
            print "$ git clone %s" % GIT_REPOSITORY2 + "\n"
        else:
            checkout = execute("git checkout . && git pull", shell=True, stdout=PIPE, stderr=PIPE).communicate()[0]
            print checkout
            if not "Already up-to-date" in checkout:
                print "Congratulations!! UFONet has been updated... ;-)\n"
            else:
                print "Your UFONet doesn't need to be updated... ;-)\n"
