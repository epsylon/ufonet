#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
UFONet - DDoS Botnet via Web Abuse - 2013/2014/2015/2016 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import socket, threading, re, base64, os, time, base64, traceback
import webbrowser, subprocess, urllib2, json, sys, shlex
from urlparse import urlparse
from main import UFONet

try:
    import pygeoip
except:
    print "\n[Error] [AI] Cannot import lib: pygeoip. \n\n To install it try:\n\n $ 'sudo apt-get install python-geoip' or 'pip install geoip'\n"
    sys.exit(2)

class AjaxMap(object):
    def __init__(self):
        self.geo_db_mirror1 = 'http://176.28.23.46/bordercheck/maps.tar.gz'  # Turina Server
        self.geo_db_mirror2 = 'http://83.163.232.95/bordercheck/maps.tar.gz' # Mirror
        self._geoip=None
        self._geoasn=None
        self._geoipstatus='nomap'
        self._err=''
        ufonet = UFONet()
        ufonet.create_options()
        try:
            self.zombies = ufonet.extract_zombies()
            aliens_army = ufonet.extract_aliens()
            droids_army = ufonet.extract_droids()
            ucavs_army = ufonet.extract_ucavs()
            rpcs_army = ufonet.extract_rpcs()
            self.zombies.extend(aliens_army)
            self.zombies.extend(droids_army)
            self.zombies.extend(ucavs_army)
            self.zombies.extend(rpcs_army)
        except:
            return

    def get_err(self):
        return self._err

    # check for geoip data status
    # basic lock file mechanism to avoid multiple downloads
    def get_status(self):
        if os.path.exists('maps.downloading'):
            if not os.path.exists('maps.downloadmsg'):
                f=open("maps.downloadmsg","wb")
                f.write("")
                f.close()
                print "[Info] [AI] [Control] GeoIP data download started! -> [OK!]\n"
            self._geoipstatus='downloading'
        elif os.path.isdir('maps'):
            if self._geoip == None :
                self._geoip = pygeoip.GeoIP('maps/GeoLiteCity.dat')
            if self._geoasn == None :
                self._geoasn = pygeoip.GeoIP('maps/GeoIPASNum.dat')
            if os.path.exists("maps.downloadmsg") :
                os.remove("maps.downloadmsg")
            self._geoipstatus='ok'
        return self._geoipstatus

    def retrieve(self,url,name):
	try:
	    handle = urllib2.urlopen(url)
            CHUNK = 16384
	    with open(name,'wb') as fp:
	        while True:
	            chunk = handle.read(CHUNK)
	            if not chunk:
	                break
	            fp.write(chunk)
	except:
	    traceback.print_exc()

    def download_maps(self):
        # generate geolocation values on a map
        if self.get_status() != 'nomap':
            return self._geoipstatus == 'ok'
        if os.path.exists("maps.downloadmsg"):
            os.remove("maps.downloadmsg")
        f=open("maps.downloading",'w')
        f.write("download started<script>$'('#ufomsg').load('/js/ajax.js?fetchmap=')")
        f.close()
        self._geoipstatus="downloading"
        try: # mirror 1
            print "\n[Info] [AI] Fetching maps from 'Mirror 1':", self.geo_db_mirror1 + "\n"
            response = self.retrieve(self.geo_db_mirror1, 'maps.tar.gz')
        except:
            try: # mirror 2
                print "[Error] [AI] Mirror 1':", self.geo_db_mirror1 + " Failed! -> [Discarding!]\n"
                print "[Info] [AI] Fetching maps from 'Mirror 2':", self.geo_db_mirror2 + "\n"
                response = self.retrieve(self.geo_db_mirror2, 'maps.tar.gz')
            except:
                print("[Error] [AI] Something wrong fetching maps from mirrors! -> [Aborting!]"), "\n"
		traceback.print_exc()
                return False #sys.exit(2)
        subprocess.call(shlex.split('tar zxfv maps.tar.gz'))
        print "\n[Info] [AI] [Control] GeoIP maps and databases -> [OK!]\n"
        # set pygeoip data sources
        self._geoip = pygeoip.GeoIP('maps/GeoLiteCity.dat')
        self._geoasn = pygeoip.GeoIP('maps/GeoIPASNum.dat')
        self._geoipstatus='ok'
        os.remove('maps.tar.gz')
        os.remove('maps.downloading')
        return True

    # fetches geoip data for specified zombie
    def geo_ip(self, zombie):
        # check for status, downloading is done by ajax() method
        if self.get_status() != 'ok':
            if self._geoipstatus =='downloading':
                print "\n[Info] [AI] [Control] GeoIP maps and databases -> [Downloading!]\n"
	        self._err= "ufomsg('[Info] [AI] Downloading maps... -> [Waiting!]')"
            elif not os.path.exists('maps/GeoIPASNum.dat') or not os.path.exists('maps/GeoLiteCity.dat'):
                print "\n[Info] [AI] GeoIP maps and databases -> [Starting!]\n"
                self._err= "ufomsg('[Info] [AI] Map download starting')\n$('#ufomsg').load('/js/ajax.js?fetchgeoip=')"
            else:
                print "\n[Error] [AI] GeoIP maps and databases: FAILED! -> [Discarding!]\n"
                self._err= "ufomsg('<font color='red'>[Info] [AI]</font> Maps: unknown error -> [Discarding!]')"
            return None
        if re.match(r'^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$', zombie) or re.match(r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$', zombie) or re.match(r'^192.168\.\d{1,3}\.\d{1,3}$', zombie) or re.match(r'^172.(1[6-9]|2[0-9]|3[0-1]).[0-9]{1,3}.[0-9]{1,3}$', zombie) or re.match('localhost', zombie):
            self._err= "ufomsg('<font color='red'>[Info] [AI] [Control]</font> Maps: invalid ip data -> [Discarding!]')"
            return None
        # create geoip data skeleton
        geo_zombie={}
        geo_zombie['qq']=zombie
        url = urlparse(zombie)
        geo_zombie['city'] = '-'
        geo_zombie['country'] = '-'
        geo_zombie['country_code'] = '-'
        geo_zombie['longitude'] = '-'
        geo_zombie['latitude'] = '-'
        geo_zombie['ip'] = '-'
        geo_zombie['host_name'] = '-'
        geo_zombie['asn'] = '-'
        geo_zombie['latitude'] = '-'
        # retrieve and allocate geoip data
        try:
            ip = socket.gethostbyname(url.netloc)
        except:
            try:
                import dns.resolver
                r = dns.resolver.Resolver()
                r.nameservers = ['8.8.8.8', '8.8.4.4'] # google DNS resolvers
                a = r.query(url.netloc, "A") # A record
                for rd in a:
                    ip = str(rd)
            except:
                self._err= "ufomsg('<font color='yellow'>[Error] [AI]</font> GeoIP: hostbyname failed for "+str(url.netloc)+"...')"
                return None
        if ip:
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",ip):
                geo_zombie['ip'] = ip
                try:
                    record = self._geoip.record_by_addr(ip)
                except:
                    self._err= "ufomsg('<font color='yellow'>[Error] [AI] </font> GeoIP: lookup failed for "+ip+", page reload required...')"
                    return None
                try:
                    asn = self._geoasn.org_by_addr(ip)
                    if asn is not None:
                        geo_zombie['asn'] = asn.encode('utf-8')
                except:
                    geo_zombie['asn'] = 'No ASN provided'
                try:
                    geo_zombie['host_name'] = socket.gethostbyaddr(ip)[0].encode('utf-8')
                except:
                    geo_zombie['host_name'] = 'No hostname'
                try:
                    longitude = str(float(record['longitude']))
                    geo_zombie['longitude'] = longitude
                    latitude = str(float(record['latitude']))
                    geo_zombie['latitude'] = latitude
                except:
                    pass
                try:
                    geo_zombie['country'] = record["country_name"].encode('utf-8')
                    geo_zombie['country_code'] = record["country_code"].lower().encode('utf-8')
                    if record['city'] is not None:
                        geo_zombie['city'] = record["city"].encode('utf-8')
                except:
                    pass
        else:
            geo_zombie = None
        return geo_zombie

    # generates javascript for adding a new zombie with geoip data
    def get_js(self,z):
        ret = ""
        gz = self.geo_ip(z)
        if gz is not None and gz['latitude']!= '-':
            ret = "Zombies.add('"+z+"',Array(new L.LatLng("+str(gz['latitude'])+","+str(gz['longitude'])+"),'"+gz['city']+"','"+gz['country']+"','"+gz['country_code']+"','"+gz['asn']+"','"+gz['ip']+"','"+gz['host_name']+"'))\n"
        else:
            url = urlparse(z)
            print '[Error] [AI] [Control] [GUI]',url.netloc, "isn't geolocated on [Map] -> [Discarding!]"
            ret += "dead_zombies.push('"+z+"')\n"
        ret += "last_zombie = '"+z+"'\n"
        return ret

    # fetches next zombie from list (using all types of zombies)
    def get_next_zombie(self,name):
        if name in self.zombies:
            for z in self.zombies:
                if name == None:
                    return z
                if z == name:
                    name = None
            return None
        else:
            return self.zombies[0]

    # ajax controller
    def ajax(self,pGet={}):
        if 'fetchgeoip' in pGet.keys():
            if self.get_status() == "nomap":
                self.download_maps()
                return "[Info] [AI] [Control] Geoip data download! -> [OK!]<br/>"
        if 'stats' in pGet.keys():
            stat='<script>$(".ufo_stat_div").show()</script>'
            if os.path.exists('/tmp/ufonet.html'):
                for x in open(r'/tmp/ufonet.html').readlines():
                    stat = stat + x
            else:
                stat="<i>[Info] [AI] [Control] Generating statistics... -> [Waiting!]</i>"
            return stat+"</div>"
        if self.get_status() != "ok":
            dljs=""
            if self.get_status() == "nomap":
                dljs+="$('#ufomsg').load('/js/ajax.js?fetchgeoip=')\n"
            if 'doll' in pGet.keys():
                dljs+="$('#ufomsg').load('/js/ajax.js?fetchdoll="+pGet['doll']+"')\n"
                dljs+="doll=new Doll('"+pGet["doll"]+"')\n"
            return "[Info] [AI] GeoIP data download in progress...<br><i>See console for errors</i>+<script>"+dljs+"</script>"
        if 'zombie' in pGet.keys():
            zn=base64.b64decode(pGet['zombie'])
            nzn=self.get_next_zombie(zn)
            if nzn is not None:
                zombie=self.get_js(nzn)
                return """ <script>
                """+zombie+"""
                ufomsg('[Info] [AI] [Control] Adding zombie: """+nzn+"""...')
                </script>"""
            else:
                return "<script>zdone=true\nufomsg('[Info] [AI] [Control] All zombies deployed! -> [OK!]')\n </script>\n"
        if 'fetchdoll' in pGet.keys():
            tn=pGet['fetchdoll']
            target = self.geo_ip(tn)
            if target is None:
                return "doll waiting for geoip data !"
            return """ doll up !<script>
doll.setData(Array(new L.LatLng("""+str(target['latitude'])+","+str(target['longitude'])+"),'"+target['city']+"','"+target['country']+"','"+target['country_code']+"','"+target['asn']+"','"+target['ip']+"','"+target['host_name']+"'))\nufomsg('[Info] Adding target: """+tn+"""...')\ndoll.show() </script>"""
        if 'doll' in pGet.keys():
            tn=pGet['doll']
            return """<script>
doll=new Doll('"""+tn+"""')\n</script>"""
        return "\n"
