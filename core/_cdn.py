#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2026 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import re, ssl, urllib.request, urllib.error
from urllib.parse import urlparse

CDN_HEADER_SIGNATURES = {
    'Cloudflare': [
        ('server', re.compile(r'cloudflare', re.I)),
        ('cf-ray', None),
        ('cf-cache-status', None),
        ('cf-connecting-ip', None),
    ],
    'Akamai': [
        ('server', re.compile(r'AkamaiGHost|AkamaiNetStorage', re.I)),
        ('x-akamai-request-id', None),
        ('x-akamai-transformed', None),
        ('x-akamai-staging', None),
    ],
    'AWS CloudFront': [
        ('via', re.compile(r'CloudFront', re.I)),
        ('x-amz-cf-id', None),
        ('x-amz-cf-pop', None),
    ],
    'Fastly': [
        ('via', re.compile(r'\bfastly\b', re.I)),
        ('x-served-by', re.compile(r'cache-', re.I)),
        ('x-fastly-request-id', None),
        ('fastly-debug-digest', None),
    ],
    'Sucuri': [
        ('server', re.compile(r'Sucuri', re.I)),
        ('x-sucuri-id', None),
        ('x-sucuri-cache', None),
    ],
    'Imperva (Incapsula)': [
        ('x-iinfo', None),
        ('x-cdn', re.compile(r'incapsula|imperva', re.I)),
        ('server', re.compile(r'incapsula', re.I)),
    ],
    'Google Cloud / GFE': [
        ('via', re.compile(r'\bGoogle\b', re.I)),
        ('server', re.compile(r'\bGFE/', re.I)),
    ],
    'Microsoft Azure': [
        ('x-azure-ref', None),
        ('x-msedge-ref', None),
    ],
    'KeyCDN': [
        ('server', re.compile(r'KeyCDN', re.I)),
        ('x-edge-location', None),
    ],
    'StackPath / MaxCDN': [
        ('server', re.compile(r'StackPath|MaxCDN|NetDNA', re.I)),
        ('x-hw', None),
    ],
    'Bunny.net': [
        ('server', re.compile(r'BunnyCDN', re.I)),
        ('cdn-pullzone', None),
    ],
    'CDN77': [
        ('server', re.compile(r'CDN77', re.I)),
    ],
    'OVH / EdgeCDN': [
        ('server', re.compile(r'OVH', re.I)),
        ('x-iplb-instance', None),
    ],
    'Section.io': [
        ('x-section-cache', None),
    ],
    'Reblaze': [
        ('server', re.compile(r'rbzid|reblaze', re.I)),
    ],
    'F5 BIG-IP': [
        ('server', re.compile(r'BigIP|BIG-IP', re.I)),
    ],
    'Varnish (front)': [
        ('via', re.compile(r'varnish', re.I)),
        ('x-varnish', None),
    ],
}

def detect_cdn(target, timeout=8, verify=False):
    """Return (cdn_name, evidence_header) if target appears behind a CDN/WAF; (None, None) otherwise."""
    if not target:
        return (None, None)
    if '://' not in target:
        target = 'http://' + target
    parsed = urlparse(target)
    url = parsed.scheme + '://' + parsed.netloc + '/'
    ctx = ssl.create_default_context()
    if not verify:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    headers = {}
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 UFONet-CDNcheck'}, method='HEAD')
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        for k, v in resp.headers.items():
            headers[k.lower()] = v
    except urllib.error.HTTPError as e:
        try:
            for k, v in e.headers.items():
                headers[k.lower()] = v
        except Exception:
            pass
    except Exception:
        return (None, None)
    for cdn, sigs in CDN_HEADER_SIGNATURES.items():
        for hname, pat in sigs:
            if hname in headers:
                val = headers[hname]
                if pat is None:
                    return (cdn, hname + ': ' + str(val)[:80])
                if pat.search(str(val)):
                    return (cdn, hname + ': ' + str(val)[:80])
    return (None, None)
