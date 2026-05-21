#!/usr/bin/env python3
"""CDN/WAF detection: registry has the expected providers and detect_cdn returns expected shapes."""
import sys

err = []

from core._cdn import detect_cdn, CDN_HEADER_SIGNATURES

EXPECTED = ['Cloudflare', 'Akamai', 'AWS CloudFront', 'Fastly', 'Sucuri',
            'Imperva (Incapsula)', 'Google Cloud / GFE', 'Microsoft Azure',
            'KeyCDN', 'StackPath / MaxCDN', 'Bunny.net', 'CDN77',
            'OVH / EdgeCDN', 'Section.io', 'Reblaze', 'F5 BIG-IP',
            'Varnish (front)']
for name in EXPECTED:
    if name not in CDN_HEADER_SIGNATURES:
        err.append(f"missing CDN signature: {name}")

cdn, evidence = detect_cdn(None)
if cdn is not None:
    err.append(f"detect_cdn(None) should return (None, None), got ({cdn}, {evidence})")

try:
    cdn, evidence = detect_cdn("https://example.com/")
    print(f"example.com -> {cdn} ({evidence})")
except Exception as e:
    err.append(f"detect_cdn raised on real URL: {type(e).__name__}: {e}")

print(f"registry size: {len(CDN_HEADER_SIGNATURES)}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
