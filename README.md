  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-tachyon-main_visor_small.png "UFONet Botnet Control Panel")

----------

 + Web:  https://ufonet.03c8.net

----------

 + FAQ:  https://ufonet.03c8.net/FAQ.html

----------

  UFONet - is a tool designed to launch Layer 7 (HTTP/Web Abuse) DDoS & DoS attacks,
  using 'Open Redirect' vectors on third part web applications (a botnet).

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

  You can automatically get all required libraries using:

       python setup.py install

  For manual installation, on Debian-based systems (ex: Ubuntu), run: 

       sudo apt-get install python-pycurl python-geoip python-whois python-crypto python-requests

  On other systems such as: Kali, Ubuntu, ArchLinux, ParrotSec, Fedora, etc... also run:

       pip install geoip 
       pip install requests
       pip install pycrypto

####  Source libs:

   * Python: https://www.python.org/downloads/
   * PyCurl: http://pycurl.sourceforge.net/
   * PyGeoIP: https://pypi.python.org/pypi/GeoIP/
   * PyWhois: https://pypi.python.org/pypi/whois
   * PyCrypto: https://pypi.python.org/pypi/pycrypto
   * PyRequests: https://pypi.python.org/pypi/requests
   * Leaflet: http://leafletjs.com/ (provided)

----------

####  License:

  UFONet is released under the GPLv3. You can find the full license text
in the [LICENSE](./docs/LICENSE) file.

----------

####  Screenshots (current version!):

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-tachyon-shell-gui_small.png "UFONet Botnet GUI Shell")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-tachyon-grid_small.png "UFONet Botnet Grid")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-tachyon-grid-stats_small.png "UFONet Botnet Grid Stats")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-tachyon-stats_small.png "UFONet Botnet General Stats")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-tachyon-board_small.png "UFONet Botnet Board")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-gui3_small.png "UFONet Botnet GeoMap (deploying)")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-tachyon-attack_visor_small.png "UFONet Attack Visor")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-gui4_small.png "UFONet Botnet GeoMap (attacking)")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-tachyon-missions_small.png "UFONet Botnet Missions")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-tachyon-abduction_small.png "UFONet Botnet Abduction")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-tachyon-warp_small.png "UFONet Botnet Warp")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-tachyon-help_small.png "UFONet Botnet Help")
