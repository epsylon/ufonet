#!/usr/bin/env python3
"""GUI /attack Extra(s) panel contains all attack input fields (matches CLI)."""
import sys, subprocess, time, socket, os, signal

err = []

EXPECTED_INPUTS = [
    "loic", "loris", "ufosyn", "fraggle", "uforst", "spray", "smurf", "xmas",
    "droper", "sniper", "tachyon", "pinger", "monlist", "ufoack", "overlap",
    "ufoudp", "nuke",
    "memcached", "chargen", "cldap", "ssdp", "qotd", "tftp", "wsdisco", "coap",
    "mssql", "arms", "plex", "netbios", "ripv1", "middlebox",
    "rapidreset", "slowread", "goldeneye", "finflood",
    "dbstress",
]

proc = subprocess.Popen(
    [sys.executable, "ufonet", "--gui"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    preexec_fn=os.setsid,
)

def http_get(path, port=9999, timeout=8):
    s = socket.socket(); s.settimeout(timeout)
    s.connect(("127.0.0.1", port))
    s.sendall(("GET " + path + " HTTP/1.0\r\n\r\n").encode())
    chunks = []
    while True:
        try:
            data = s.recv(65536)
            if not data: break
            chunks.append(data)
        except socket.timeout: break
    s.close()
    return b"".join(chunks).decode("utf-8", errors="replace")

try:
    for _ in range(30):
        try:
            s = socket.socket(); s.settimeout(0.5); s.connect(("127.0.0.1", 9999)); s.close()
            break
        except Exception:
            time.sleep(0.5)
    page = http_get("/attack")
    for name in EXPECTED_INPUTS:
        if f'name="{name}"' not in page:
            err.append(f"input name=\"{name}\" missing in /attack Extra(s) panel")
finally:
    try: os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except Exception: pass
    proc.wait(timeout=5)

print(f"Expected {len(EXPECTED_INPUTS)} inputs; missing: {len(err)}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
