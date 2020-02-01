=================================================================
How to set up a 'grider' - eg a P2P/Community stats/board server
=================================================================

* Setup web server (apache, nginx...) with a folder "ufonet", this folder should be:
  - Located in: /var/www/ufonet
  - Owned by the user running the blackhole
  - Accessible with: http(s)://<your ip>/ufonet/

* Start the grider with: 
  ./ufonet --grider (or python3 ufonet --grider &)

* Anyone wanting to connect to your server needs to set the 'grider' origin
  at main.py (self.blackhole = <IP-grider>)

===============================================================

WARNING: this *ADVANCED* function is *NOT* secure, proceed if you really want to.

===============================================================
