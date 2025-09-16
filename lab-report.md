# Malware C2 Beacon Lab — Detailed Lab Report

## Summary
This lab simulates a simple Command & Control (C2) beacon over HTTP and demonstrates how to:
- Generate periodic beacon traffic (victim → C2 server).
- Capture beacon traffic using `tcpdump`.
- Analyze traffic in **Wireshark** to identify beaconing behavior and extract Indicators of Compromise (IOCs).
- Export evidence (PCAP & screenshots) for SOC analysis or portfolio demonstration.

**Environment**
- Host: macOS (used for running Wireshark and controlling Multipass)
- Multipass VMs:
  - **attacker** (Ubuntu) — acts as the C2 server (HTTP)
  - **victim** (Ubuntu) — runs a Python beacon script
- Example IPs used in this report:
  - Attacker VM: `192.168.64.8`
  - Victim VM: `192.168.64.2`

---

## Repository structure
c2-beacon-lab/
├── README.md            # Project summary and instructions
├── lab-report.md        # This detailed report (you are reading now)
├── http_beacon.py       # Beacon script run on victim VM
├── beacon.pcap          # Packet capture (optional saved result)
└── screenshots/
├── io-graph.png
├── packet-list.png
└── http-stream.png
---

## 1 — Prepare attacker (C2) VM
We will run a very simple HTTP server on the attacker VM to accept beacon requests.

**Command (on host macOS):**
```bash
# start a background HTTP server on attacker VM (port 8080)
multipass exec attacker -- nohup python3 -m http.server 8080 >/tmp/http.log 2>&1 &
What this does
	•	Runs a basic Python HTTP server bound to all interfaces in the attacker VM, logging stdout/stderr to /tmp/http.log.
	•	The server will respond with standard HTTP responses. For beacon GET paths that don’t exist, it will return 404.

Verify server is running:
multipass exec attacker -- ss -ltnp | grep 8080 || true
# or
multipass exec attacker -- ps aux | grep http.server | grep -v grep || true
2 — Prepare victim: tcpdump capture

Capture packets on the victim VM, filtering to the attacker host so the PCAP contains only relevant traffic.

Command (on host macOS):
# Start packet capture on victim VM and write to /tmp/beacon.pcap
multipass exec victim -- sudo tcpdump -i any host 192.168.64.8 -w /tmp/beacon.pcap &
Notes
	•	-i any captures on all interfaces (works well in virtualized environment).
	•	Use sudo because raw packet capture usually requires root.
	•	The & runs tcpdump in the background (so you can run other commands locally).
	•	Record start time for documentation.

To stop capture:
multipass exec victim -- sudo pkill -f tcpdump || true
Copy capture from VM to host:
multipass transfer victim:/tmp/beacon.pcap ./beacon.pcap
If multipass transfer fails because the file does not exist or tcpdump is still running, stop tcpdump first as above, then retry.
3 — Beacon script (victim)

Create http_beacon.py on the victim (or on your host and transfer it to the victim).
Code (http_beacon.py):
#!/usr/bin/env python3
import time
import requests

ATTACKER = "http://192.168.64.8:8080/heartbeat"
INTERVAL = 20  # seconds between beacons
BEACONS = 6     # how many beacons to send

for i in range(BEACONS):
    try:
        r = requests.get(ATTACKER, params={'id': 'victim1', 'i': i}, timeout=5)
        print("beacon", i, r.status_code)
    except Exception as e:
        print("error", e)
    time.sleep(INTERVAL)
How to place and run it from your host:
# place file in your local repo, then transfer to victim
multipass transfer http_beacon.py victim:/home/ubuntu/http_beacon.py
multipass exec victim -- ls -l /home/ubuntu/http_beacon.py
Install dependencies on victim (if needed):
# Use Debian packaged requests to avoid pip issues in managed environment
multipass exec victim -- sudo apt update
multipass exec victim -- sudo apt install -y python3-requests
Run the beacon (interactive):
multipass exec victim -- python3 /home/ubuntu/http_beacon.py
Run in background (log to file):
multipass exec victim -- nohup python3 /home/ubuntu/http_beacon.py >/tmp/beacon.log 2>&1 &
multipass exec victim -- tail -f /tmp/beacon.log
What to expect
	•	The victim will send HTTP GET requests to http://192.168.64.8:8080/heartbeat?id=victim1&i=N roughly every 20 seconds.
	•	The attacker’s Python HTTP server will typically respond with 404 Not Found for /heartbeat because it has no matching file; this is expected in this simulation.











