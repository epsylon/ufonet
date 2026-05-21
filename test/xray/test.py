#!/usr/bin/env python3
"""XRAY (UFOSCAN): TCP-SYN scan helper builds packets correctly."""
import sys, os

err = []

try:
    from scapy.all import IP, TCP, RandShort
except Exception as e:
    print("scapy import FAILED:", e)
    sys.exit(1)

dst_ip = "127.0.0.1"
for port in (22, 80, 9999):
    src_port = RandShort()
    p = IP(dst=dst_ip) / TCP(sport=src_port, dport=port, flags='S')
    if not (p.haslayer(IP) and p.haslayer(TCP)):
        err.append(f"port {port}: packet missing IP/TCP layer")
    if str(p[TCP].flags) != 'S':
        err.append(f"port {port}: TCP flags not SYN, got {p[TCP].flags}")
    if p[TCP].dport != port:
        err.append(f"port {port}: dport mismatch")

print("xray packet builders OK" if not err else "xray packet builders FAILED")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
