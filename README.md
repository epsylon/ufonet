  ![UFONet](https://ufonet.03c8.net/ufonet/r3dst4r/ufonet-gui.png "UFONet Welcome")

----------

 + Website:   https://ufonet.03c8.net

----------

#### Description:

  UFONet - is a free software, P2P and cryptographic -disruptive toolkit- that allows to perform DoS and DDoS attacks; 
on the Layer 7 (APP/HTTP) through the exploitation of Open Redirect vectors on third-party websites to act as a botnet 
and on the Layer3 (Network) abusing the protocol.

  It also works as an encrypted DarkNET to publish and receive content by creating a global client/server network based 
on a direct-connect P2P architecture.

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
     https://en.wikipedia.org/wiki/TCP_reset_attack

   - SPRAY: 
     https://en.wikipedia.org/wiki/Denial-of-service_attack#Reflected_attack

   - SMURF: 
     https://en.wikipedia.org/wiki/Smurf_attack

   - XMAS: 
     https://en.wikipedia.org/wiki/Christmas_tree_packet

   - DROPER: 
     https://en.wikipedia.org/wiki/IP_fragmentation_attack

   - SNIPER: 
     https://en.wikipedia.org/wiki/Simple_Network_Management_Protocol

   - TACHYON: 
     https://en.wikipedia.org/wiki/DNS_amplification_attack

   - PINGER: 
     https://en.wikipedia.org/wiki/Ping_flood

   - MONLIST: 
     https://en.wikipedia.org/wiki/NTP_server_misuse_and_abuse

   - UFOACK: 
     https://en.wikipedia.org/wiki/Denial-of-service_attack

   - OVERLAP: 
     https://en.wikipedia.org/wiki/IP_fragmentation_attack#Overlapping_fragment_attack

   - UFOUDP: 
     https://en.wikipedia.org/wiki/UDP_flood_attack

   - NUKE: 
     https://en.wikipedia.org/wiki/Sockstress

   - MEMCACHED:
     https://en.wikipedia.org/wiki/Memcached

   - CHARGEN:
     https://en.wikipedia.org/wiki/Character_Generator_Protocol

   - CLDAP:
     https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol

   - SSDP:
     https://en.wikipedia.org/wiki/Simple_Service_Discovery_Protocol

   - QOTD:
     https://en.wikipedia.org/wiki/QOTD

   - TFTP:
     https://en.wikipedia.org/wiki/Trivial_File_Transfer_Protocol

   - WSDISCO:
     https://en.wikipedia.org/wiki/WS-Discovery

   - COAP:
     https://en.wikipedia.org/wiki/Constrained_Application_Protocol

   - MSSQL:
     https://en.wikipedia.org/wiki/Microsoft_SQL_Server

   - ARMS:
     https://en.wikipedia.org/wiki/Apple_Remote_Desktop

   - PLEX:
     https://en.wikipedia.org/wiki/Plex_(software)

   - NETBIOS:
     https://en.wikipedia.org/wiki/NetBIOS

   - RIPV1:
     https://en.wikipedia.org/wiki/Routing_Information_Protocol

   - MIDDLEBOX:
     https://en.wikipedia.org/wiki/Network_middlebox

   - RAPIDRESET:
     https://en.wikipedia.org/wiki/HTTP/2

   - SLOWREAD:
     https://en.wikipedia.org/wiki/Slowloris_(software)

   - GOLDENEYE:
     https://en.wikipedia.org/wiki/Denial-of-service_attack#Application-layer_attacks

   - FINFLOOD:
     https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Connection_termination

#### Installing:

  UFONet runs on many platforms:

  You can try to automatically get all required libraries using (as root):

       python3 setup.py

  For manual installation, run:

       sudo apt-get install -y --no-install-recommends libpython3.12-dev python3-pycurl python3-geoip python3-whois python3-requests libgeoip1 libgeoip-dev
       python3 -m pip install --upgrade pip --no-warn-script-location --root-user-action=ignore --break-system-packages
       python3 -m pip install pycurl --upgrade --root-user-action=ignore --break-system-packages
       python3 -m pip install pygeoip requests urllib3 whois scapy pycryptodomex duckduckgo-search dnspython certifi --ignore-installed --root-user-action=ignore --break-system-packages

  If any lib is missing at runtime, UFONet 2.0 will try to auto-install it using pip.

  To run the test suite at any time:

       python3 ufonet --test-ufonet

----------

####  License:

  UFONet is released under the GPLv3. You can find the full license text
in the [LICENSE](./docs/LICENSE) file.

----------

####  Screenshots (current version!):

  ![UFONet](https://ufonet.03c8.net/ufonet/r3dst4r/ufonet-tools-1.png "UFONet Tools 1")

  ![UFONet](https://ufonet.03c8.net/ufonet/r3dst4r/ufonet-tools-2.png "UFONet Tools 2")
  
  ![UFONet](https://ufonet.03c8.net/ufonet/r3dst4r/ufonet-gui-shell.png "UFONet GUI Shell")   
      
  ![UFONet](https://ufonet.03c8.net/ufonet/r3dst4r/ufonet-available-engines.png "UFONet Engines")
  
  ![UFONet](https://ufonet.03c8.net/ufonet/r3dst4r/ufonet-gui-init.png "UFONet GUI Init")
  
  ![UFONet](https://ufonet.03c8.net/ufonet/r3dst4r/ufonet-gui-help.png "UFONet GUI Help")
  
  ![UFONet](https://ufonet.03c8.net/ufonet/r3dst4r/ufonet-gui-board.png "UFONet GUI Board")
  
  ![UFONet](https://ufonet.03c8.net/ufonet/r3dst4r/ufonet-gui-botnet.png "UFONet GUI Botnet")
               
  ![UFONet](https://ufonet.03c8.net/ufonet/r3dst4r/ufonet-gui-stats.png "UFONet GUI Stats")

  ![UFONet](https://ufonet.03c8.net/ufonet/r3dst4r/ufonet-gui-attack.png "UFONet GUI Attack")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-kraken-board_small.png "UFONet GUI Board")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-kraken-wargames_small.png "UFONet GUI Wargames")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-gui3_small.png "UFONet GeoMap /deploying/")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-gui4_small.png "UFONet GeoMap /attacking/")

