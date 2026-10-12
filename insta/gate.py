#!/usr/bin/env python3
"""Entscheidet, ob jetzt gepostet wird. Gibt 'mode=week|weekend|none' für GitHub Actions aus.
Zeitplan in deutscher Zeit (insta/config.json); GitHub-cron läuft in UTC, daher zwei Läufe je Termin."""
import json, os, sys
from datetime import datetime
from zoneinfo import ZoneInfo
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = json.load(open(os.path.join(root, "insta", "config.json")))
now = datetime.now(ZoneInfo("Europe/Berlin"))
mode = "none"
force = os.environ.get("FORCE_MODE", "")
if force in ("week", "weekend"):
    mode = force
elif cfg.get("enabled"):
    for m in ("week", "weekend"):
        c = cfg[m]
        if now.weekday() == c["weekday"] and now.hour >= c["hour"]:
            folder = os.path.join(root, "posts", f"{now.date()}-{m}")
            if not os.path.exists(folder):
                mode = m
print(f"mode={mode}")
print(f"date={now.date()}")
