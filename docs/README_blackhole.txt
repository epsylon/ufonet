=================================================================
How to set up a 'blackhole' - eg a P2P/Community 'zombies' server
=================================================================

* Setup web server (apache, nginx...) with a folder "ufonet", this folder should be:
  - Located in: /var/www/ufonet
  - Owned by the user running the blackhole
  - Accessible with: http(s)://<your ip>/ufonet/

* Start the blackhole with:
  ./ufonet --blackhole (or python3 ufonet --blackhole &)

* Anyone wanting to connect to your server needs to set the --up-to/--down-from 
  to the ip address of your webserver.

===============================================================

WARNING: this *ADVANCED* function is *NOT* secure, proceed if you really want to.

===============================================================
