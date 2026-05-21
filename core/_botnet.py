#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2026 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import ipaddress, os

PLACEHOLDER_NETS = [
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("198.51.100.0/24"),
]

def is_placeholder(entry):
    s = entry.strip()
    if not s:
        return True
    if s.startswith('<TBD:') and s.endswith('>'):
        return True
    if s.startswith(('http://', 'https://')):
        from urllib.parse import urlparse
        host = urlparse(s).hostname or ''
    else:
        host = s.split(':', 1)[0].split('/', 1)[0]
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    for net in PLACEHOLDER_NETS:
        if ip in net:
            return True
    return False

def load_botnet_file(path):
    if not os.path.exists(path):
        return [], False, False
    with open(path, encoding='utf-8', errors='replace') as f:
        entries = [l.strip() for l in f.readlines() if l.strip()]
    if not entries:
        return [], True, False
    all_placeholder = all(is_placeholder(e) for e in entries)
    return entries, False, all_placeholder

GUIDANCE = {
    "open-redirect": "Find real 'zombies' via dorking: ./ufonet -s 'page.php?url='  (or --auto-search / --sd botnet/dorks.txt)",
    "dns":           "Use any public open DNS resolver (1.1.1.1, 8.8.8.8) or a known recursive server in your scope.",
    "ntp":           "Use pool.ntp.org, time.cloudflare.com, time.google.com, or a misconfigured NTPv2 server in your scope.",
    "snmp":          "Scan UDP/161 in your authorized scope (community='public'). Dorking will NOT find these.",
    "memcached":     "Scan UDP/11211 in your authorized scope (e.g. masscan/zmap). Dorking will NOT find these.",
    "cldap":         "Scan UDP/389 in your authorized scope (Active Directory hosts replying to anonymous searchRequest). Dorking will NOT find these.",
    "ssdp":          "Scan UDP/1900 in your authorized scope (UPnP-exposed routers). Dorking will NOT find these.",
    "chargen":       "Extremely rare today. Scan UDP/19 in your authorized scope. Dorking will NOT find these.",
    "qotd":          "Extremely rare today. Scan UDP/17 in your scope. Dorking will NOT find these.",
    "tftp":          "Scan UDP/69 in your authorized scope. Dorking will NOT find these.",
    "wsdisco":       "Scan UDP/3702 in your scope (printers, IP cameras). Dorking will NOT find these.",
    "coap":          "Scan UDP/5683 in your scope (IoT). Dorking will NOT find these.",
    "mssql":         "Scan UDP/1434 in your scope (SQL Server browser). Dorking will NOT find these.",
    "arms":          "Scan UDP/3283 in your scope (Apple Remote Desktop). Dorking will NOT find these.",
    "plex":          "Scan UDP/32414 in your scope (Plex GDM). Dorking will NOT find these.",
    "netbios":       "Scan UDP/137 in your scope. Dorking will NOT find these.",
    "ripv1":         "Scan UDP/520 in your scope (legacy router). Dorking will NOT find these.",
    "middlebox":     "Identify censorship middleboxes via probing (CN/IR/RU/etc.). See the Geneva paper. Dorking will NOT find these.",
    "reflector":     "Populate with real reflectors from your authorized scope. Dorking does NOT usually find these protocols.",
}

def warn_placeholders(label, file_path, kind="reflector"):
    print("[Info] [AI] [" + label + "] No real entries in botnet/" + os.path.basename(file_path) + " -> [Skipping]")
