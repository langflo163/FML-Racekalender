#!/usr/bin/env python3
"""Entscheidet, ob jetzt gepostet wird. Gibt mode=…, date=…, out=…, publish=… für GitHub Actions aus.
Zeitplan in deutscher Zeit (insta/config.json); GitHub-cron läuft in UTC, daher zwei Läufe je Termin.
Testposts: Push einer geänderten insta/test.json ({"mode": "...", "date": "YYYY-MM-DD", "publish": true})."""
import json, os
from datetime import datetime, date
from zoneinfo import ZoneInfo
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = json.load(open(os.path.join(root, "insta", "config.json")))
now = datetime.now(ZoneInfo("Europe/Berlin"))
mode, d, publish, out = "none", now.date(), "true", ""
ev = os.environ.get("EVENT", "")
force = os.environ.get("FORCE_MODE", "")
if ev == "push":
    t = json.load(open(os.path.join(root, "insta", "test.json")))
    mode, d = t["mode"], date.fromisoformat(t["date"])
    publish = "true" if t.get("publish") else "false"
    out = f"posts/test-{now:%Y%m%d-%H%M}-{mode}"
elif force in ("week", "weekend", "story"):
    mode = force
    publish = os.environ.get("FORCE_PUBLISH", "false")
elif cfg.get("enabled"):
    for m in ("week", "weekend", "story"):
        c = cfg[m]
        if (c.get("weekday") is None or now.weekday() == c["weekday"]) and now.hour >= c["hour"]:
            if not os.path.exists(os.path.join(root, "posts", f"{now.date()}-{m}")):
                mode = m; break
out = out or f"posts/{d}-{mode}"
print(f"mode={mode}")
print(f"date={d}")
print(f"out={out}")
print(f"publish={publish}")
