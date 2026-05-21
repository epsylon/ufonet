#!/usr/bin/env python3
"""argparse migration: all expected flags present, --version exits with v2.0 codename."""
import sys, subprocess

EXPECTED_FLAGS = [
    "-h", "--help", "--version", "-v", "--verbose", "--examples", "--timeline",
    "--update", "--test-ufonet", "--check-tor", "--force-ssl", "--force-yes", "--gui",
    "--crypter", "--network", "--xray", "--xray-ps",
    "--proxy", "--user-agent", "--referer", "--host", "--xforw", "--xclient",
    "--timeout", "--retries", "--threads", "--delay",
    "--auto-search", "-s", "--sd", "--sn", "--se", "--sa", "--sax", "--sl",
    "--test-offline", "--test-all", "-t", "--test-rpc", "--attack-me",
    "--deploy", "--grider", "--blackhole", "--download-nodes",
    "--up-to", "--down-from",
    "-i", "-x", "-a", "-f", "-b", "-r", "-m",
    "--no-droids", "--no-ucavs", "--no-aliens", "--no-rpcs", "--no-head",
    "--no-scan", "--no-purge", "--expire",
    "--fraggle", "--tachyon", "--monlist", "--smurf", "--sniper", "--spray",
    "--db", "--loic", "--loris", "--ufosyn", "--xmas", "--nuke", "--ufoack",
    "--uforst", "--droper", "--overlap", "--pinger", "--ufoudp",
    "--memcached", "--chargen", "--cldap", "--ssdp", "--qotd", "--tftp",
    "--wsdisco", "--coap", "--mssql", "--arms", "--plex", "--netbios",
    "--ripv1", "--middlebox", "--rapidreset", "--slowread", "--goldeneye",
    "--finflood",
]

err = []

r = subprocess.run([sys.executable, "ufonet", "--help"], capture_output=True, text=True, timeout=10)
if r.returncode != 0:
    err.append(f"--help exited {r.returncode}")
help_text = r.stdout

missing = [f for f in EXPECTED_FLAGS if f not in help_text]
if missing:
    err.append(f"missing flags in --help: {missing}")

r = subprocess.run([sys.executable, "ufonet", "--version"], capture_output=True, text=True, timeout=10)
if r.returncode != 0:
    err.append(f"--version exited {r.returncode}")
if "2.0" not in r.stdout:
    err.append("--version output missing '2.0'")
if "R3DST4R" not in r.stdout:
    err.append("--version output missing 'R3DST4R'")

print(f"--help flags found: {len(EXPECTED_FLAGS) - len(missing)} / {len(EXPECTED_FLAGS)}")
print(f"--version output: {r.stdout.strip()}")

for e in err:
    print("FAIL:", e)

sys.exit(0 if not err else 1)
