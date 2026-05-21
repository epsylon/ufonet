#!/usr/bin/env python3
"""scapy-based modules: ensure packet builders construct expected layers (no send)."""
import sys, os

err = []
try:
    from scapy.all import IP, TCP, UDP, ICMP, RandShort
except Exception as e:
    print("scapy import FAILED:", e)
    sys.exit(1)

dst = "127.0.0.1"

def assert_pkt(name, pkt, *layers):
    for L in layers:
        if not pkt.haslayer(L):
            err.append(f"{name}: missing layer {L.__name__}")

p_syn = IP(dst=dst, flags='MF', ttl=64) / TCP(sport=RandShort(), dport=80, flags='S')
assert_pkt("ufosyn-style", p_syn, IP, TCP)
if str(p_syn[TCP].flags) != 'S':
    err.append(f"ufosyn: flags expected S, got {p_syn[TCP].flags}")

p_xmas = IP(dst=dst, flags='MF') / TCP(sport=RandShort(), dport=80, flags='FPU')
assert_pkt("xmas-style", p_xmas, IP, TCP)
if not all(c in str(p_xmas[TCP].flags) for c in 'FPU'):
    err.append(f"xmas: missing FPU flags, got {p_xmas[TCP].flags}")

p_ack = IP(dst=dst) / TCP(sport=RandShort(), dport=80, flags='A')
assert_pkt("ufoack-style", p_ack, IP, TCP)

p_rst = IP(dst=dst) / TCP(sport=RandShort(), dport=80, flags='R')
assert_pkt("uforst-style", p_rst, IP, TCP)

p_udp = IP(dst=dst) / UDP(sport=RandShort(), dport=53) / (b"\x00" * 32)
assert_pkt("ufoudp-style", p_udp, IP, UDP)

p_ping = IP(dst=dst) / ICMP()
assert_pkt("pinger-style", p_ping, IP, ICMP)

p_frag = IP(dst=dst, frag=1, flags='MF') / TCP(sport=RandShort(), dport=80) / (b"A" * 64)
assert_pkt("droper-style", p_frag, IP, TCP)

print("packet builders OK" if not err else "packet builders FAILED")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
