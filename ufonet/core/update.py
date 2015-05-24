#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - DDoS attacks via Web Abuse - 2013/2014/2015 - by psy (epsylon@riseup.net)

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
        GIT_REPOSITORY = "https://github.com/epsylon/ufonet"
        rootDir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', ''))
        if not os.path.exists(os.path.join(rootDir, ".git")):
            print "Not any .git repository found!\n"
            print "="*30
            print "\nYou should clone UFONet manually with:\n"
            print "$ git clone %s" % GIT_REPOSITORY
        else:
            checkout = execute("git checkout .", shell=True, stdout=PIPE, stderr=PIPE).communicate()[0]
            if "fast-forwarded" in checkout:
                pull = execute("git pull %s HEAD" % GIT_REPOSITORY, shell=True, stdout=PIPE, stderr=PIPE).communicate()
                print "Congratulations!! UFONet has been updated to latest version ;-)\n"
            else:
                print "You are updated! ;-)\n"

