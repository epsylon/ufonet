
  ![Alt_text](http://ufonet.03c8.net/ufonet/ufonet-gui4_small.png "UFONet Botnet Attacking Map")


  UFONet - is a tool designed to launch DDoS attacks against a target, 
  using 'Open Redirect' vectors on third party web applications, like botnet.

  See this links for more info:

   - CWE-601:Open Redirect: 
     http://cwe.mitre.org/data/definitions/601.html

   - OWASP:URL Redirector Abuse: 
     https://www.owasp.org/index.php/OWASP_Periodic_Table_of_Vulnerabilities_-_URL_Redirector_Abuse2

  ![Alt text](http://ufonet.03c8.net/ufonet/ufonet-schema.png "UFONet Schema")

----------

 UFONet is released under the GPLv3+. You can find the full license text
in the [LICENSE](./LICENSE) file.

----------

 + Web:  http://ufonet.03c8.net

----------

#### Installing:

  UFONet runs on many platforms.  It requires Python (>2.7.9) and the following libraries:

       python-pycurl - Python bindings to libcurl
       python-geoip  - Python bindings for the GeoIP IP-to-country resolver library
       python-crypto - Cryptographic algorithms and protocols for Python

  On Debian-based systems (ex: Ubuntu), run: 

       sudo apt-get install python-pycurl python-geoip python-crypto

  On other systems such as: Kali, Ubuntu, ArchLinux, ParrotSec, Fedora, etc... also run:

    pip install geoip 
    pip install requests
    pip install pycrypto

####  Source libs:

 * Python: https://www.python.org/downloads/
 * PyCurl: http://pycurl.sourceforge.net/
 * PyGeoIP: https://pypi.python.org/pypi/GeoIP/
 * PyCrypto: https://pypi.python.org/pypi/pycrypto
 * Leaflet: http://leafletjs.com/

----------
