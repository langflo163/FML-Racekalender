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
    mode = t["mode"]
    d = date.fromisoformat(t["date"]) if t.get("date") else now.date()
    publish = "true" if t.get("publish") else "false"
    out = t["folder"] if mode == "existing" else f"posts/test-{now:%Y%m%d-%H%M}-{mode}"
elif force in ("week", "weekend", "story", "bonus"):
    mode = force
    publish = os.environ.get("FORCE_PUBLISH", "false")
elif cfg.get("enabled"):
    hm = (now.hour, now.minute)
    done = lambda m: os.path.exists(os.path.join(root, "posts", f"{now.date()}-{m}"))
    for m in ("week", "weekend", "story", "bonus"):
        c = cfg.get(m)
        if not isinstance(c, dict):
            continue
        if c.get("weekday") is not None and now.weekday() != c["weekday"]:
            continue
        if hm < (c["hour"], c.get("minute", 0)) or ("until" in c and hm >= tuple(c["until"])):
            continue
        if m == "bonus" and done("story"):   # Renntag: schon „Heute live“ gepostet
            continue
        if not done(m):
            mode = m; break
out = out or f"posts/{d}-{mode}"
print(f"mode={mode}")
print(f"date={d}")
print(f"out={out}")
print(f"publish={publish}")
