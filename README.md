=================================================================== 

  UFONet - is a tool designed to launch DDoS attacks against a target, 
  using 'Open Redirect' vectors on third party web applications, like botnet.

  See this links for more info:

   - CWE-601:Open Redirect: 
     http://cwe.mitre.org/data/definitions/601.html

   - OWASP:URL Redirector Abuse: 
     https://www.owasp.org/index.php/OWASP_Periodic_Table_of_Vulnerabilities_-_URL_Redirector_Abuse2

----------

 + Web:  http://ufonet.sf.net

----------

    Main features:

  --version             show program's version number and exit
  -v, --verbose         active verbose on requests
  --check-tor           check to see if Tor is used properly
  --force-yes           Set 'YES' to all questions
  --update              check for latest stable version
  --gui                 launch GUI/Web Interface

  *Configure Request(s)*:
    --proxy=PROXY       Use proxy server (tor: http://localhost:8118)
    --user-agent=AGENT  Use another HTTP User-Agent header (default SPOOFED)
    --referer=REFERER   Use another HTTP Referer header (default SPOOFED)
    --host=HOST         Use another HTTP Host header (default NONE)
    --xforw             Set your HTTP X-Forwarded-For with random IP values
    --xclient           Set your HTTP X-Client-IP with random IP values
    --timeout=TIMEOUT   Select your timeout (default 30)
    --retries=RETRIES   Retries when the connection timeouts (default 1)
    --delay=DELAY       Delay in seconds between each HTTP request (default 0)

  *Manage Botnet*:
    -s SEARCH           Search 'zombies' on google (ex: -s 'proxy.php?url=')
    --sd=DORKS          Search from a list of 'dorks' (ex: --sd dorks.txt)
    --sn=NUM_RESULTS    Set max number of result to search (default 10)
    -t TEST             Test list of web 'zombie' servers (ex: -t zombies.txt)

  *Community Botnet*:
    --download-zombies  Download list of 'zombies' from Community
    --upload-zombies    Share your 'zombies' with Commmunity

  *Research Target*:
    -i INSPECT          Inspect object's sizes (ex: -i http(s)://target.com)

  *Configure Attack(s)*:
    -r ROUNDS           Set number of 'rounds' for the attack (default: 1)
    -b PLACE            Set a place to 'bit' on target (ex: -b /path/big.jpg)
    -a TARGET           Start a Web DDoS attack (ex: -a http(s)://target.com)

----------

    Installing:

  UFONet runs on many platforms.  It requires Python (2.x.y) and the following library:

       python-pycurl - Python bindings to libcurl

  On Debian-based systems (ex: Ubuntu), run: 

       sudo apt-get install python-pycurl

  Source libs:

       * Python: https://www.python.org/downloads/
       * PyCurl: http://pycurl.sourceforge.net/

----------
