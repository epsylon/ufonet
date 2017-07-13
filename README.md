  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-gui6_small.png "UFONet Botnet Control Panel")

----------

 + Web:  http://ufonet.03c8.net

----------

 + FAQ:  http://ufonet.03c8.net/FAQ.html

----------

  UFONet - is a tool designed to launch DDoS attacks against a target, 
  using 'Open Redirect' vectors on third party web applications, like botnet.

  See this links for more info:

   - CWE-601:Open Redirect: 
     http://cwe.mitre.org/data/definitions/601.html

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

  On Debian-based systems (ex: Ubuntu), run: 

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

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-gui7_small.png "UFONet Botnet Grid")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-gui8_small.png "UFONet Botnet Stats")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-gui9_small.png "UFONet Botnet Board")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-gui3_small.png "UFONet Botnet GeoMap (deploying)")

  ![UFONet](https://ufonet.03c8.net/ufonet/ufonet-gui4_small.png "UFONet Botnet GeoMap (attacking)")

