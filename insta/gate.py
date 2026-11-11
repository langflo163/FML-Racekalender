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

def story_left():
    """Gibt es heute noch nicht beendete Sessions? (billig, ohne Playwright)
    Verspätete GitHub-Läufe holen die Story so bis fallback_until nach (Flo 11.11.)."""
    try:
        import sys
        sys.path.insert(0, os.path.join(root, "insta"))
        import make_post
        return bool(make_post.build_story(now.date())[0])
    except Exception as e:   # im Zweifel wie früher versuchen
        import sys
        print(f"story_left: {e}", file=sys.stderr)
        return True
ev = os.environ.get("EVENT", "")
force = os.environ.get("FORCE_MODE", "")
if ev == "push":
    t = json.load(open(os.path.join(root, "insta", "test.json")))
    mode = t["mode"]
    d = date.fromisoformat(t["date"]) if t.get("date") else now.date()
    publish = "true" if t.get("publish") else "false"
    out = t["folder"] if mode == "existing" else f"posts/test-{now:%Y%m%d-%H%M}-{mode}"
elif force in ("week", "weekreel", "weekend", "story", "season", "bonus"):
    mode = force
    publish = os.environ.get("FORCE_PUBLISH", "false")
elif cfg.get("enabled"):
    hm = (now.hour, now.minute)
    done = lambda m: os.path.exists(os.path.join(root, "posts", f"{now.date()}-{m}"))
    for m in ("week", "weekreel", "weekend", "story", "season", "bonus"):
        c = cfg.get(m)
        if not isinstance(c, dict):
            continue
        if c.get("weekday") is not None and now.weekday() != c["weekday"]:
            continue
        if hm < (c["hour"], c.get("minute", 0)):
            continue
        late = "until" in c and hm >= tuple(c["until"])
        if late and not ("fallback_until" in c and hm < tuple(c["fallback_until"])):
            continue
        if m == "story" and not done(m) and not story_left():
            continue   # kein Renntag bzw. alle Sessions heute schon vorbei → nichts nachzuholen
        if m == "bonus" and done("story"):   # Renntag: schon „Heute live“ gepostet
            continue
        if not done(m):
            mode = m; break
out = out or f"posts/{d}-{mode}"
print(f"mode={mode}")
print(f"date={d}")
print(f"out={out}")
print(f"publish={publish}")
