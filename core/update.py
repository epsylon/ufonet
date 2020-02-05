#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

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
        if not os.path.exists(".git"):
            print("Not any .git repository found!\n")
            print("="*30)
            print("\nTo have working this feature, you should clone UFONet with:\n")
            print("$ git clone %s" % GIT_REPOSITORY)
            print("\nAlso you can try this other mirror:\n")
            print("$ git clone %s" % GIT_REPOSITORY2 + "\n")
        else:
            checkout = execute("git checkout . && git pull", shell=True, stdout=PIPE, stderr=PIPE).communicate()[0]
            print("[Info] [GitHub] Reply:\n\n"+checkout.decode('utf-8'))
            if not b"Already up-to-date" in checkout:
                print("[Info] [AI] Congratulations!! UFONet has been updated... ;-)\n")
            else:
                print("[Info] [AI] Your UFONet doesn't need to be updated... ;-)\n")
