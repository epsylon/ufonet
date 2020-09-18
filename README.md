  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-multiverse-welcome_small.png "UFONet Welcome")

----------

 + Website:   https://ufonet.03c8.net

----------

#### Description:

  UFONet - is a free software, P2P and cryptographic -disruptive toolkit- that allows to perform DoS and DDoS attacks; 
on the Layer 7 (APP/HTTP) through the exploitation of Open Redirect vectors on third-party websites to act as a botnet 
and on the Layer3 (Network) abusing the protocol.

  See these links for more info:

   - FAQ:
     https://ufonet.03c8.net/FAQ.html

   - CWE-601:Open Redirect: 
     https://cwe.mitre.org/data/definitions/601.html

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-schema.png "UFONet Schema")

   - LOIC: 
     https://en.wikipedia.org/wiki/Low_Orbit_Ion_Cannon

   - LORIS: 
     https://en.wikipedia.org/wiki/Slowloris_(software)

   - UFOSYN: 
     https://en.wikipedia.org/wiki/SYN_flood

   - FRAGGLE: 
     https://en.wikipedia.org/wiki/Fraggle_attack

   - UFORST: 
     https://ddos-guard.net/en/terminology/attack_type/rst-or-fin-flood

   - SPRAY: 
     https://en.wikipedia.org/wiki/DRDOS

   - SMURF: 
     https://en.wikipedia.org/wiki/Smurf_attack

   - XMAS: 
     https://en.wikipedia.org/wiki/Christmas_tree_packet

   - DROPER: 
     https://en.wikipedia.org/wiki/IP_fragmentation_attack

   - SNIPER: 
     https://www.imperva.com/learn/application-security/snmp-reflection/

   - TACHYON: 
     https://www.us-cert.gov/ncas/alerts/TA13-088A

   - PINGER: 
     https://www.cloudflare.com/learning/ddos/ping-icmp-flood-ddos-attack/

   - MONLIST: 
     https://www.us-cert.gov/ncas/alerts/TA14-013A

   - UFOACK: 
     https://www.f5.com/services/resources/glossary/push-and-ack-flood

   - OVERLAP: 
     https://cyberhoot.com/cybrary/fragment-overlap-attack/

   - UFOUDP: 
     https://en.wikipedia.org/wiki/UDP_flood_attack

   - NUKE: 
     https://dl.packetstormsecurity.net/papers/general/tcp-starvation.pdf

----------

#### Installing:

  UFONet runs on many platforms. It requires Python (>=3) and the following libraries:

       python3-pycurl - Python bindings to libcurl (Python 3)
       python3-geoip - Python3 bindings for the GeoIP IP-to-country resolver library
       python3-whois - Python module for retrieving WHOIS information - Python 3
       python3-crypto - cryptographic algorithms and protocols for Python 3
       python3-requests - elegant and simple HTTP library for Python3, built for human beings
       python3-scapy - Packet crafting/sniffing/manipulation/visualization security tool

  You can automatically get all required libraries using (as root):

       python3 setup.py install

  For manual installation, on Debian-based systems (ex: Ubuntu), run: 

       sudo apt-get install python3-pycurl python3-geoip python3-whois python3-crypto python3-requests python3-scapy

  On other systems such as: Kali, Ubuntu, ArchLinux, ParrotSec, Fedora, etc... also run:

       pip3 install GeoIP
       pip3 install python-geoip
       pip3 install pygeoip
       pip3 install requests
       pip3 install pycrypto
       pip3 install pycurl
       pip3 install whois
       pip3 install scapy-python3

####  Source libs:

   * Python: https://www.python.org/downloads/
   * PyCurl: http://pycurl.sourceforge.net/
   * GeoIP: https://pypi.python.org/pypi/GeoIP/
   * Python-geoip: https://pypi.org/project/python-geoip/
   * Pygeoip: https://pypi.org/project/pygeoip/
   * Whois: https://pypi.python.org/pypi/whois
   * PyCrypto: https://pypi.python.org/pypi/pycrypto
   * PyRequests: https://pypi.python.org/pypi/requests
   * Scapy-Python3: https://pypi.org/project/scapy-python3/
   * Leaflet: http://leafletjs.com/ (provided)

----------

####  License:

  UFONet is released under the GPLv3. You can find the full license text
in the [LICENSE](./docs/LICENSE) file.

----------

####  Screenshots (current version!):

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-marauder-shell-1.png "UFONet Shell")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-marauder-shell-2.png "UFONet Shell Board")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-marauder-shell-3.png "UFONet GUI Shell")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-multiverse-main_small.png "UFONet GUI Main Panel")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-marauder-botnet.png "UFONet GUI Botnet")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-marauder-stats.png "UFONet GUI General Stats")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-multiverse-ranking_small.png "UFONet GUI Ranking")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-marauder-attack.png "UFONet GUI Attack")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-gui3_small.png "UFONet GeoMap /deploying/")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-gui4_small.png "UFONet GeoMap /attacking/")

