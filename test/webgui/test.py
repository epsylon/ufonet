#!/usr/bin/env python3
"""Start GUI, hit /cmd_list_army and /cmd_list_nodes, validate anchors."""
import sys, subprocess, time, socket, signal, os

err = []

proc = subprocess.Popen(
    [sys.executable, "ufonet", "--gui"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    preexec_fn=os.setsid,
)

def http_get(path, port=9999, timeout=5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect(("127.0.0.1", port))
    s.sendall(("GET " + path + " HTTP/1.0\r\n\r\n").encode())
    chunks = []
    while True:
        try:
            data = s.recv(65536)
            if not data: break
            chunks.append(data)
        except socket.timeout:
            break
    s.close()
    return b"".join(chunks).decode("utf-8", errors="replace")

try:
    ready = False
    for _ in range(30):
        try:
            s = socket.socket()
            s.settimeout(0.5)
            s.connect(("127.0.0.1", 9999))
            s.close()
            ready = True
            break
        except Exception:
            time.sleep(0.5)
    if not ready:
        err.append("GUI didn't open port 9999 within ~15s")
    else:
        army = http_get("/cmd_list_army")
        nodes = http_get("/cmd_list_nodes")
        sections = ["UCAVs", "Aliens", "Droids", "Zombies", "XML-RPCs", "NTPs", "DNSs", "SNMPs"]
        for s in sections:
            if f"<u>{s}:</u>" not in army:
                err.append(f"army: section {s} missing")
        if army.count("<a href=") < len(sections):
            err.append(f"army: too few anchors ({army.count('<a href=')})")
        if "Total Nodes" not in nodes:
            err.append("nodes: 'Total Nodes' header missing")
finally:
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except Exception:
        pass
    proc.wait(timeout=5)

print(f"army_anchors={army.count('<a href=') if 'army' in dir() else 'n/a'}")
print(f"nodes_anchors={nodes.count('<a href=') if 'nodes' in dir() else 'n/a'}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
