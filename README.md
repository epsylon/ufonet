=================================================================== 

  UFONet - is a tool designed to launch DDoS attacks against a target, 
  using 'Open Redirect' vectors on third party web applications, like botnet.

  See this links for more info:

   - CWE-601:Open Redirect: 
     http://cwe.mitre.org/data/definitions/601.html

   - OWASP:URL Redirector Abuse: 
     https://www.owasp.org/index.php/OWASP_Periodic_Table_of_Vulnerabilities_-_URL_Redirector_Abuse2

----------

 + Web:  http://ufonet.03c8.net

----------

    Installing:

  UFONet runs on many platforms.  It requires Python (2.x.y) and the following libraries:

       python-pycurl - Python bindings to libcurl
       python-geoip  - Python bindings for the GeoIP IP-to-country resolver library

  On Debian-based systems (ex: Ubuntu), run: 

       sudo apt-get install python-pycurl python-geoip

  Source libs:

       * Python: https://www.python.org/downloads/
       * PyCurl: http://pycurl.sourceforge.net/
       * PyGeoIP: https://pypi.python.org/pypi/GeoIP/

----------
