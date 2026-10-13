#!/usr/bin/env python3
"""Erzeugt Instagram-Grafiken (JPEG, 1080x1350) + Bildtext aus data/races.json.

Aufruf:  python3 insta/make_post.py week|weekend [YYYY-MM-DD] [--out DIR]
  week     Montag bis Sonntag der Woche, in der das Datum liegt
  weekend  Freitag bis Sonntag dieser Woche
Ausgabe: DIR/1.jpg, 2.jpg … und DIR/caption.txt
"""
import json, sys, os, html, re
from datetime import datetime, date, timedelta, time
from zoneinfo import ZoneInfo

BER = ZoneInfo("Europe/Berlin")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WD = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
WDS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
MON = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
       "September", "Oktober", "November", "Dezember"]
APP_URL = "langflo163.github.io/FML-Racekalender"
MAX_ROWS = 7          # Termine pro Bild
MAX_SLIDES = 10       # Instagram-Limit Karussell

def load():
    with open(os.path.join(ROOT, "data", "races.json"), encoding="utf-8") as f:
        return json.load(f)

def span(e):
    """(start_date, end_date, start_dt|None) in Berlin-Zeit."""
    if e.get("start"):
        t = datetime.fromisoformat(e["start"]).astimezone(BER)
        return t.date(), t.date(), t
    if e.get("date"):
        d = date.fromisoformat(e["date"]); return d, d, None
    a = date.fromisoformat(e["from"]); b = date.fromisoformat(e.get("to") or e["from"])
    return a, b, None

def kind(e):
    return {"quali": "Qualifying", "sq": "Sprint-Quali", "sprint": "Sprint"}.get(e.get("type"), "")

def tv_names(e, ser):
    order = {"mine": 0, "free": 1, "pay": 2, "open": 3}
    tv = sorted(e.get("tv") or ser.get("tv") or [], key=lambda t: order.get(t.get("k"), 9))
    return [t["n"] for t in tv if t.get("k") != "open"][:2]

def collect(data, d0, d1):
    ser = {s["id"]: s for s in data["series"]}
    days = {}
    for e in data["events"]:
        s = ser.get(e["s"])
        if not s: continue
        a, b, t = span(e)
        if b < d0 or a > d1: continue
        item = dict(e=e, s=s, t=t, multi=(a != b), a=a, b=b)
        if t:
            days.setdefault(a, []).append(item)
        elif a == b:
            days.setdefault(a, []).append(item)
        else:  # mehrtägig ohne Zeit: am letzten Tag im Zeitraum (Renntag) zeigen
            days.setdefault(min(b, d1), []).append(item)
    for k in days:
        days[k].sort(key=lambda x: (x["t"] is None, x["t"] or datetime.min.replace(tzinfo=BER), x["s"]["name"]))
    return dict(sorted(days.items()))

def dm(d): return f"{d.day}.{d.month}."

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1350px;background:#111418;color:#fff;font-family:Inter,'DejaVu Sans',Arial,sans-serif;overflow:hidden}
.pg{position:relative;width:1080px;height:1350px;padding:70px 70px 0}
.top{display:flex;align-items:center;gap:22px}
.fml{display:flex;gap:8px}
.fml span{width:62px;height:54px;background:#d71920;border-radius:9px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:36px}
.brand{font-size:40px;font-weight:800;letter-spacing:-.5px}
.flag{position:absolute;left:0;right:0;bottom:0;height:22px;background:repeating-conic-gradient(#fff 0 25%,#111418 0 50%) 0 0/22px 22px}
.redbar{position:absolute;left:0;right:0;bottom:22px;height:10px;background:#d71920}
.foot{position:absolute;left:70px;right:70px;bottom:62px;display:flex;justify-content:space-between;color:#9aa2ad;font-size:24px}
h1{font-size:96px;line-height:1;font-weight:900;margin-top:120px;letter-spacing:-2px}
h1 em{font-style:normal;color:#d71920}
.sub{font-size:44px;color:#c9ced6;margin-top:28px;font-weight:600}
.hl{margin-top:70px}
.hl div{font-size:34px;margin:16px 0;display:flex;gap:18px;align-items:center}
.dot{width:18px;height:18px;border-radius:50%;flex:none}
.cnt{margin-top:60px;font-size:30px;color:#9aa2ad}
.day{margin-top:46px;display:flex;align-items:baseline;gap:20px}
.day b{font-size:64px;font-weight:900;letter-spacing:-1px}
.day span{font-size:36px;color:#9aa2ad;font-weight:600}
.rows{margin-top:30px}
.r{display:flex;gap:24px;align-items:stretch;background:#1b1f25;border-radius:18px;padding:20px 24px;margin-bottom:16px}
.tm{width:130px;flex:none;font-size:42px;font-weight:800;font-variant-numeric:tabular-nums;line-height:1.05}
.tm.na{font-size:26px;color:#9aa2ad;font-weight:600;line-height:1.25}
.bar{width:8px;border-radius:4px;flex:none}
.bd{flex:1;min-width:0}
.sn{font-size:24px;font-weight:700;color:#c9ced6;text-transform:uppercase;letter-spacing:.5px}
.en{font-size:36px;font-weight:800;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.k{display:inline-block;font-size:22px;font-weight:800;border:2px solid #9aa2ad;color:#c9ced6;border-radius:8px;padding:1px 10px;margin-left:10px;vertical-align:6px}
.k.sp{border-color:#d71920;color:#ff5a52}
.tv{font-size:24px;color:#7fd3a0;margin-top:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.more{font-size:28px;color:#9aa2ad;margin-top:6px}
body.st{height:1920px}
.st .pg{height:1920px;padding-top:120px}
.st h1{margin-top:90px;font-size:110px}
.st .live{display:inline-block;background:#d71920;color:#fff;font-weight:900;font-size:40px;border-radius:12px;padding:6px 20px;margin-top:40px;letter-spacing:1px}
.st .rows{margin-top:50px}
"""

def head():
    return ('<div class="top"><div class="fml"><span>F</span><span>M</span><span>L</span></div>'
            '<div class="brand">Rennkalender</div></div>')

def foot(i, n):
    return (f'<div class="foot"><span>Alle Zeiten deutsche Zeit · ohne Gewähr</span><span>{i}/{n}</span></div>'
            '<div class="redbar"></div><div class="flag"></div>')

def row(it):
    e, s, t = it["e"], it["s"], it["t"]
    k = kind(e)
    kb = f'<span class="k{" sp" if e.get("type")=="sprint" else ""}">{k}</span>' if k else ""
    name = re.sub(r"\s+–\s+(Qualifying|Rennen\s*\d?|Superpole-Rennen)$", lambda m: "" if k else " – " + m.group(1), e["name"])
    night = (f'<div style="font-size:20px;color:#9aa2ad;font-weight:600;margin-top:4px">Nacht auf {WDS[t.weekday()]}</div>'
             if it.get("night") else "")
    tm = f'<div class="tm">{t:%H:%M}{night}</div>' if t else (
        f'<div class="tm na">{dm(it["a"])}–{dm(it["b"])}<br>Zeit folgt</div>' if it["multi"] else '<div class="tm na">Zeit<br>folgt</div>')
    tv = " · ".join(tv_names(e, s))
    star = "★ " if e.get("hl") else ""
    return (f'<div class="r">{tm}<div class="bar" style="background:{s["color"]}"></div><div class="bd">'
            f'<div class="sn">{html.escape(s["name"])}</div>'
            f'<div class="en">{star}{html.escape(name)}{kb}</div>'
            + (f'<div class="tv">📺 {html.escape(tv)}</div>' if tv else "") + '</div></div>')

def build(mode, ref):
    data = load()
    monday = ref - timedelta(days=ref.weekday())
    if mode == "week":
        d0, d1 = monday, monday + timedelta(days=6)
        title = 'Die <em>Rennwoche</em>'
    else:
        d0, d1 = monday + timedelta(days=4), monday + timedelta(days=6)
        title = 'Das <em>Renn&shy;wochenende</em>'
    days = collect(data, d0, d1)
    sub = f"{dm(d0)} – {d1.day}. {MON[d1.month-1]} {d1.year}"

    # Seiten pro Tag (lange Tage werden geteilt)
    pages = []
    for d, items in days.items():
        chunks = [items[i:i+MAX_ROWS] for i in range(0, len(items), MAX_ROWS)]
        for ci, ch in enumerate(chunks):
            pages.append((d, ch, ci > 0))
    if len(pages) > MAX_SLIDES - 1:   # zu viel: Rest kürzen, Hinweis auf letzter Seite
        pages = pages[:MAX_SLIDES - 1]
        pages[-1] = (pages[-1][0], pages[-1][1], pages[-1][2], True)
    total = 1 + len(pages)

    allitems = [it for v in days.values() for it in v]
    races = [it for it in allitems if not it["e"].get("type")]
    hls = []
    seen = set()
    for it in sorted(allitems, key=lambda x: (not x["e"].get("hl"), x["a"])):
        if it["e"].get("type") or it["s"]["id"] in seen: continue
        seen.add(it["s"]["id"]); hls.append(it)
    cover_list = "".join(
        f'<div><span class="dot" style="background:{it["s"]["color"]}"></span>'
        f'<b>{html.escape(it["s"]["name"])}</b>&nbsp;·&nbsp;{html.escape(re.sub(r" – .*$","",it["e"]["name"]))}</div>'
        for it in hls[:8])
    slides = [f'<div class="pg">{head()}<h1>{title}</h1><div class="sub">{sub}</div>'
              f'<div class="hl">{cover_list or "<div>Keine Rennen in diesem Zeitraum.</div>"}</div>'
              f'<div class="cnt">{len(races)} Rennen · {len(allitems)-len(races)} Quali/Sprints · {len(days)} Tage · Details in der App</div>'
              f'{foot(1,total)}</div>']
    for i, p in enumerate(pages, start=2):
        d, ch, cont = p[0], p[1], p[2]
        more = len(p) > 3
        slides.append(f'<div class="pg">{head()}<div class="day"><b>{WD[d.weekday()]}</b><span>{d.day}. {MON[d.month-1]}{" (Forts.)" if cont else ""}</span></div>'
                      f'<div class="rows">{"".join(row(it) for it in ch)}</div>'
                      + ('<div class="more">… weitere Termine in der App</div>' if more else "") + f'{foot(i,total)}</div>')

    # Bildtext
    lines = [("🏁 Die Rennwoche " if mode == "week" else "🏁 Das Rennwochenende ") + sub, ""]
    for d, items in days.items():
        lines.append(f"📅 {WDS[d.weekday()]} {dm(d)}")
        for it in items:
            e, s, t = it["e"], it["s"], it["t"]
            k = kind(e); tv = tv_names(e, s)
            nm = re.sub(r"\s+–\s+(Qualifying)$", "", e["name"])
            lines.append(f"{t:%H:%M}" if t else "–:–" )
            lines[-1] += f" {s['name']}: {nm}{' (' + k + ')' if k else ''}{' – ' + tv[0] if tv else ''}"
        lines.append("")
    tail = ["Alle Zeiten in deutscher Zeit, ohne Gewähr.", f"📲 Alle Termine & Sender: Link in der Bio ({APP_URL})", "",
            hashtags({it["s"]["id"] for it in allitems})]
    cap = "\n".join(lines)
    while len(cap) + len("\n".join(tail)) > 2150 and len(lines) > 3:
        lines = lines[:-2] + ["…", ""]
        cap = "\n".join(lines)
    caption = cap + "\n" + "\n".join(tail)
    global LAST_ALT
    LAST_ALT = alt_texts([("cover", None, allitems)] + [("day", p[0], p[1]) for p in pages], re.sub(r"<[^>]+>|&shy;", "", title) + " " + sub)
    return slides, caption

LAST_ALT = []
STORY_HOUR = 8   # Uhrzeit der Story (deutsche Zeit)

# Instagram erlaubt seit Dez. 2025 max. 5 Hashtags: 2 große allgemeine + die 3 größten Serien im Post
TAG_BASE = ["#motorsport", "#racing"]
TAG_SERIES = [("f1", "#f1"), ("mgp", "#motogp"), ("nas", "#nascar"), ("wec", "#wec"), ("indy", "#indycar"),
              ("sbk", "#worldsbk"), ("dtm", "#dtm"), ("fe", "#formulae"), ("imsa", "#imsa"), ("gtwc", "#gtworldchallenge"),
              ("m2", "#moto2"), ("m3", "#moto3"), ("n24", "#nordschleife"), ("nls", "#nordschleife"), ("elms", "#elms"),
              ("igtc", "#igtc"), ("h24", "#24hseries"), ("etrc", "#truckracing"), ("enas", "#iracing")]
TAG_FILL = ["#racecar", "#motorsports", "#formula"]

def hashtags(sids):
    tags = []
    for sid, t in TAG_SERIES:
        if sid in sids and t not in tags: tags.append(t)
    tags = tags[:3]
    tags += [t for t in TAG_FILL if t not in tags][:3 - len(tags)]
    return " ".join(TAG_BASE + tags)

def alt_texts(slides_items, title):
    """Bildbeschreibung je Karussell-Bild (max. 1000 Zeichen)."""
    out = []
    for kind_, d, items in slides_items:
        if kind_ == "cover":
            txt = f"FML Rennkalender – {title}: " + ", ".join(dict.fromkeys(it["s"]["name"] for it in items))
        else:
            txt = f"Motorsport live am {WD[d.weekday()]}, {dm(d)} (deutsche Zeit): " + "; ".join(
                f'{it["t"]:%H:%M} ' * bool(it["t"]) + f'{it["s"]["name"]} {it["e"]["name"]}' + (f' ({kind(it["e"])})' if kind(it["e"]) else "") for it in items)
        out.append(txt[:1000])
    return out

def build_story(day, drop_ended=True):
    data = load()
    days = collect(data, day, day + timedelta(days=1))
    items = days.get(day, [])
    # Nachtrennen des Folgetags (vor der nächsten Story) schon heute zeigen
    for it in days.get(day + timedelta(days=1), []):
        if it["t"] and it["t"].hour < STORY_HOUR:
            items.append(dict(it, night=True))
    now = datetime.now(BER)
    if drop_ended and day == now.date():   # bereits beendete Sessions (z. B. Nachtrennen) weglassen
        items = [it for it in items if not it["t"] or it["t"] + timedelta(hours=2) > now]
    if not items:
        return None, None
    rows = "".join(row(it) for it in items[:10])
    more = '<div class="more">… weitere Termine in der App</div>' if len(items) > 10 else ""
    slide = (f'<div class="pg">{head()}<div class="live">● {"HEUTE NACHT LIVE" if all(i.get("night") for i in items) else "HEUTE LIVE"}</div>'
             f'<h1>{WD[day.weekday()]}</h1><div class="sub">{day.day}. {MON[day.month-1]} {day.year}</div>'
             f'<div class="rows">{rows}</div>{more}'
             f'<div class="foot"><span>Alle Zeiten deutsche Zeit · ohne Gewähr</span><span>Link in Bio</span></div>'
             '<div class="redbar"></div><div class="flag"></div></div>')
    return [slide], f"Heute live – {WD[day.weekday()]}, {dm(day)}"

def make_reel(out, n, sec=3.5, fade=0.5):
    """Baut aus 1.jpg … n.jpg ein 9:16-Video (reel.mp4) ohne Ton."""
    import subprocess
    inputs, filt = [], []
    for i in range(1, n + 1):
        inputs += ["-loop", "1", "-t", str(sec), "-i", os.path.join(out, f"{i}.jpg")]
        filt.append(f"[{i-1}:v]scale=1080:1350,pad=1080:1920:0:285:color=#111418,setsar=1,fps=30,format=yuv420p[v{i}]")
    last = "v1"
    for i in range(2, n + 1):
        off = (i - 1) * (sec - fade)
        filt.append(f"[{last}][v{i}]xfade=transition=slideleft:duration={fade}:offset={off:.2f}[x{i}]")
        last = f"x{i}"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt), "-map", f"[{last}]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           os.path.join(out, "reel.mp4")]
    subprocess.run(cmd, check=True)

def render(slides, out, story=False):
    from playwright.sync_api import sync_playwright
    os.makedirs(out, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920 if story else 1350})
        for i, s in enumerate(slides, start=1):
            pg.set_content(f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body class='{'st' if story else ''}'>{s}</body></html>")
            pg.wait_for_timeout(150)
            pg.screenshot(path=os.path.join(out, "story.jpg" if story else f"{i}.jpg"), type="jpeg", quality=92)
        b.close()

if __name__ == "__main__":
    argv = sys.argv[1:]
    out = None
    if "--out" in argv:
        i = argv.index("--out"); out = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    mode = argv[0] if argv else "week"
    ref = date.fromisoformat(argv[1]) if len(argv) > 1 else datetime.now(BER).date()
    out = out or os.path.join(ROOT, "posts", f"{ref}-{mode}")
    if mode == "bonus":   # Bonus-Story nur an rennfreien Tagen
        if build_story(ref, drop_ended=False)[0]:
            print("Renntag – keine Bonus-Story"); sys.exit(0)
        import free_story
        slide, key = free_story.pick(ref)
        if not slide:
            print("Keine Bonus-Story fällig"); sys.exit(0)
        print("Bonus-Story:", key)
        free_story.render_story(slide, out)
        sys.exit(0)
    if mode == "story":
        slides, caption = build_story(ref)
        if not slides:
            print("Keine Termine heute – keine Story"); sys.exit(0)
        render(slides, out, story=True)
    else:
        slides, caption = build(mode, ref)
        render(slides, out)
        if LAST_ALT:
            with open(os.path.join(out, "alt.json"), "w", encoding="utf-8") as f:
                json.dump(LAST_ALT, f, ensure_ascii=False, indent=1)
        if mode == "weekend":
            make_reel(out, len(slides))
    with open(os.path.join(out, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(caption)
    print(out, len(slides), "Bilder")
