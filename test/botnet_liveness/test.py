#!/usr/bin/env python3
"""Liveness check for every entry in every botnet/*.txt (HTTP, DNS, NTP, SNMP, UDP-amp).

Iterates the whole botnet/ folder, routes by filename to the right probe.
Informational test: PASS unless every populated category has zero alive entries
(which would indicate a systemic network failure or code regression).
"""
import socket, ssl, struct, time, os, sys
import urllib.request, urllib.error, urllib.parse

BOTNET_DIR = "botnet"
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0"
TIMEOUT = 6

HTTP_CATEGORIES = {"zombies", "aliens", "droids", "ucavs", "rpcs"}
UDP_AMP_PROBES = {
    "dns":       (53,    b'\x00' * 12 + b'\x06google\x03com\x00\x00\x01\x00\x01',
                  lambda d: d[2] & 0x80),
    "ntp":       (123,   b'\x1b' + 47 * b'\0',  lambda d: len(d) == 48),
    "snmp":      (161,
                  bytes([0x30, 0x26, 0x02, 0x01, 0x01, 0x04, 0x06]) + b'public' + bytes([
                      0xa0, 0x19, 0x02, 0x04, 0x71, 0x44, 0x12, 0x34,
                      0x02, 0x01, 0x00, 0x02, 0x01, 0x00, 0x30, 0x0b,
                      0x30, 0x09, 0x06, 0x05, 0x2b, 0x06, 0x01, 0x02,
                      0x01, 0x05, 0x00]),
                  lambda d: len(d) > 10),
    "memcached": (11211, b'\x00\x01\x00\x00\x00\x01\x00\x00stats\r\n', lambda d: len(d) > 0),
    "chargen":   (19,    b'\x00',                                       lambda d: len(d) > 0),
    "cldap":     (389,
                  (b'\x30\x84\x00\x00\x00\x2d\x02\x01\x01\x63\x84\x00\x00\x00\x24'
                   b'\x04\x00\x0a\x01\x00\x0a\x01\x00\x02\x01\x00\x02\x01\x00\x01'
                   b'\x01\x00\x87\x0b\x6f\x62\x6a\x65\x63\x74\x43\x6c\x61\x73\x73'
                   b'\x30\x00'),
                  lambda d: len(d) > 0),
    "ssdp":      (1900,
                  (b'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\n'
                   b'MAN: "ssdp:discover"\r\nMX: 1\r\nST: ssdp:all\r\n\r\n'),
                  lambda d: len(d) > 0),
    "qotd":      (17,    b'\x00',                                       lambda d: len(d) > 0),
    "tftp":      (69,    b'\x00\x01startup-config\x00netascii\x00',     lambda d: len(d) > 0),
    "wsdisco":   (3702,  b'',                                           lambda d: len(d) > 0),
    "coap":      (5683,  b'\x40\x01\x12\x34\xbb.well-known\x04core',    lambda d: len(d) > 0),
    "mssql":     (1434,  b'\x02',                                       lambda d: len(d) > 0),
    "arms":      (3283,  b'\x00\x14\x00\x01\x00\x03',                   lambda d: len(d) > 0),
    "plex":      (32414, b'M-SEARCH * HTTP/1.1\r\n\r\n',                lambda d: len(d) > 0),
    "netbios":   (137,
                  (b'\xab\xcd\x00\x10\x00\x01\x00\x00\x00\x00\x00\x00'
                   b'\x20\x43\x4b\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41'
                   b'\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x00'
                   b'\x00\x21\x00\x01'),
                  lambda d: len(d) > 0),
    "ripv1":     (520,
                  (b'\x01\x01\x00\x00' + b'\x00' * 16 + b'\x00\x00\x00\x10'),
                  lambda d: len(d) > 0),
}
TCP_PROBES = {
    "middlebox": 80,
}
SKIP = {"dorks", "humans"}

def http_probe(url):
    parsed = urllib.parse.urlparse(url.rstrip(';').split(';')[0])
    if not parsed.scheme:
        parsed = urllib.parse.urlparse("http://" + url)
    base = parsed.scheme + "://" + parsed.netloc + parsed.path
    if parsed.query:
        base += "?" + parsed.query
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    headers = {"User-Agent": UA, "Accept": "*/*"}
    is_xmlrpc = 'xmlrpc' in base.lower()
    if is_xmlrpc:
        body = b'<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName><params/></methodCall>'
        req = urllib.request.Request(base, data=body, headers={**headers, "Content-Type": "text/xml"}, method='POST')
    else:
        req = urllib.request.Request(base, headers=headers, method='HEAD')
    try:
        r = urllib.request.urlopen(req, context=ctx, timeout=TIMEOUT)
        return ("UP", r.status, "")
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):
            return ("HTTP-ERR", e.code, "")
        return ("HTTP-ERR", e.code, str(e)[:80])
    except urllib.error.URLError as e:
        return ("URL-ERR", 0, str(e.reason)[:80])
    except Exception as e:
        return ("ERR", 0, f"{type(e).__name__}: {e}"[:80])

def udp_probe(ip, port, payload, success_fn):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.settimeout(TIMEOUT)
    try:
        s.sendto(payload, (ip, port))
        data, _ = s.recvfrom(4096)
        if success_fn(data):
            return ("UP", port, f"{len(data)}B")
        return ("MALFORMED", port, repr(data[:20]))
    except socket.timeout:
        return ("TIMEOUT", port, "")
    except Exception as e:
        return ("ERR", port, f"{type(e).__name__}: {e}"[:80])
    finally:
        s.close()

def tcp_probe(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=TIMEOUT):
            return ("UP", port, "")
    except socket.timeout:
        return ("TIMEOUT", port, "")
    except Exception as e:
        return ("ERR", port, f"{type(e).__name__}: {e}"[:80])

def load(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8', errors='replace') as f:
        return [l.strip() for l in f if l.strip()]

total = alive_total = 0
dead_per_cat = {}
all_results = []

print(f"{'category':12s} | {'entry':50s} | result")
print("-" * 110)

files = sorted(os.listdir(BOTNET_DIR))
for fname in files:
    if not fname.endswith(".txt"):
        continue
    cat = fname[:-4]
    if cat in SKIP:
        continue
    entries = load(os.path.join(BOTNET_DIR, fname))
    if not entries:
        print(f"{cat:12s} | (empty)")
        continue
    if all(e.startswith('<TBD:') and e.endswith('>') for e in entries):
        print(f"{cat:12s} | (placeholders only)")
        continue
    entries = [e for e in entries if not (e.startswith('<TBD:') and e.endswith('>'))]
    if not entries:
        print(f"{cat:12s} | (placeholders only)")
        continue
    if len(entries) > 5:
        entries = entries[:5]
        print(f"{cat:12s} | sampling first 5 of {len(load(os.path.join(BOTNET_DIR, fname)))}")
    dead_per_cat[cat] = 0
    for entry in entries:
        total += 1
        if cat in HTTP_CATEGORIES:
            status, code, detail = http_probe(entry)
            ok = (status == "UP") or (status == "HTTP-ERR" and code in (403, 405) and 'xmlrpc' in entry.lower())
        elif cat in UDP_AMP_PROBES:
            port, payload, success_fn = UDP_AMP_PROBES[cat]
            status, code, detail = udp_probe(entry, port, payload, success_fn)
            ok = (status == "UP")
        elif cat in TCP_PROBES:
            port = TCP_PROBES[cat]
            status, code, detail = tcp_probe(entry, port)
            ok = (status == "UP")
        else:
            status, code, detail = ("SKIPPED", 0, "unknown category")
            ok = True
            continue
        mark = "OK " if ok else "DEAD"
        if not ok:
            dead_per_cat[cat] += 1
            all_results.append((cat, entry, status, code, detail))
        else:
            alive_total += 1
        print(f"{cat:12s} | {entry[:50]:50s} | {mark} {status:9s} {code:<5} {detail[:50]}")

print("-" * 110)
print(f"Tested entries: {total}, Alive: {alive_total}, Dead: {total - alive_total}")
print()
print("Per-category dead:")
for cat in sorted(dead_per_cat):
    if dead_per_cat[cat] > 0:
        print(f"  {cat}: {dead_per_cat[cat]} dead")
    else:
        print(f"  {cat}: 0 dead")
print()
print("DEAD entries:")
for cat, entry, status, code, detail in all_results:
    print(f"  {cat}: {entry}  ({status} {code} {detail})")

if total == 0:
    print("No entries tested (all categories empty or only placeholders).")
    sys.exit(0)
if alive_total == 0:
    print("All entries dead - probable network issue or code regression.")
    sys.exit(1)
sys.exit(0)
