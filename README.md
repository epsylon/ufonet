  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-singularity-welcome_small.png "UFONet Welcome")

----------

 + Web:  https://ufonet.03c8.net

----------

 + FAQ:  https://ufonet.03c8.net/FAQ.html

----------

  UFONet - is a toolkit designed to launch DDoS and DoS attacks.

  See these links for more info:

   - CWE-601:Open Redirect: 
     https://cwe.mitre.org/data/definitions/601.html

   - OWASP:URL Redirector Abuse: 
     https://www.owasp.org/index.php/OWASP_Periodic_Table_of_Vulnerabilities_-_URL_Redirector_Abuse2

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-schema.png "UFONet Schema")

----------

#### Installing:

  UFONet runs on many platforms.  It requires Python (>2.7.9) and the following libraries:

       python-pycurl - Python bindings to libcurl
       python-geoip  - Python bindings for the GeoIP IP-to-country resolver library
       python-whois  - Python module for retrieving WHOIS information - Python 2
       python-crypto - Cryptographic algorithms and protocols for Python
       python-requests - elegant and simple HTTP library for Python2, built for human beings
       python-scapy - Packet generator/sniffer and network scanner/discovery

  You can automatically get all required libraries using (as root):

       sudo python setup.py install

  For manual installation, on Debian-based systems (ex: Ubuntu), run: 

       sudo apt-get install python-pycurl python-geoip python-whois python-crypto python-requests python-scapy

  On other systems such as: Kali, Ubuntu, ArchLinux, ParrotSec, Fedora, etc... also run:

       pip install geoip 
       pip install requests
       pip install pycrypto
       pip install scapy

####  Source libs:

   * Python: https://www.python.org/downloads/
   * PyCurl: http://pycurl.sourceforge.net/
   * PyGeoIP: https://pypi.python.org/pypi/GeoIP/
   * PyWhois: https://pypi.python.org/pypi/whois
   * PyCrypto: https://pypi.python.org/pypi/pycrypto
   * PyRequests: https://pypi.python.org/pypi/requests
   * PyScapy: https://pypi.org/project/scapy/
   * Leaflet: http://leafletjs.com/ (provided)

----------

####  License:

  UFONet is released under the GPLv3. You can find the full license text
in the [LICENSE](./docs/LICENSE) file.

----------

####  Screenshots (current version!):

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-singularity-shell1_small.png "UFONet Shell")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-singularity-shell2_small.png "UFONet Shell Board")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-singularity-shell3_small.png "UFONet GUI Shell")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-singularity-welcome_small.png "UFONet GUI Welcome")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-singularity-main_small.png "UFONet GUI Main Panel")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-hydra-botnet_small.png "UFONet GUI Botnet")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-singularity-stats_small.png "UFONet GUI General Stats")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-singularity-ranking_small.png "UFONet GUI Ranking")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-hydra-board_small.png "UFONet GUI Board/Forum")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-singularity-grid_small.png "UFONet GUI Crypto Grid Board")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-singularity-grid2_small.png "UFONet GUI Grid Stats")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-singularity-wargames_small.png "UFONet GUI Wargames")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-singularity-attack_small.png "UFONet GUI Attack")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-gui3_small.png "UFONet GeoMap /deploying/")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-gui4_small.png "UFONet GeoMap /attacking/")

