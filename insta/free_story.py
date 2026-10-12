#!/usr/bin/env python3
"""Bonus-Storys für rennfreie Tage.

pick(day)   -> (slide_html, key) oder (None, None); wählt nach Priorität und Regeln.
Regeln: max. 1 Story pro Tag (an Renntagen nur „Heute live“), max. 2 Bonus-Storys pro Woche
(Ausnahme: „Titel entschieden“, nur am ersten Werktag nach der Entscheidung).
Zustand (bekannte Saisons, Warteschlange, Verlauf) in insta/state.json.

Entwürfe:  python3 insta/free_story.py draft <art> YYYY-MM-DD --out DIR
Arten: titel kalender finale start zeit heim doppel neu winter countdown serie_fehlt
"""
import os, sys, json, html, re
from datetime import date, datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_post
from make_post import CSS, head, ROOT, load, span, dm, WD, WDS, MON, tv_names, BER

STATE = os.path.join(ROOT, "insta", "state.json")
HOME_COUNTRIES = ("Deutschland", "Österreich")
WEEK_CAP = 2

EXTRA = """
.big{font-size:112px;font-weight:900;line-height:1.02;letter-spacing:-2px;margin-top:130px}
.big em{font-style:normal;color:#d71920}
.mid{font-size:76px;font-weight:900;line-height:1.05;letter-spacing:-1px;margin-top:40px}
.txt{font-size:42px;color:#c9ced6;margin-top:44px;line-height:1.35;font-weight:600}
.cta{margin-top:60px;background:#d71920;border-radius:24px;padding:36px 40px;font-size:44px;font-weight:800;line-height:1.3}
.cta small{display:block;font-size:30px;font-weight:600;opacity:.9;margin-top:10px}
.chips{display:flex;flex-wrap:wrap;gap:12px;margin-top:30px}
.chips span{font-size:24px;font-weight:700;color:#c9ced6;border:2px solid #2a2f37;border-radius:999px;padding:8px 18px;display:flex;align-items:center;gap:10px}
.chips i,.dot2{width:14px;height:14px;border-radius:50%;display:inline-block;flex:none}
.lbl{font-size:28px;color:#9aa2ad;margin-top:60px;font-weight:700;text-transform:uppercase;letter-spacing:1px}
.tag2{display:inline-block;background:#d71920;color:#fff;font-weight:900;font-size:36px;border-radius:12px;padding:6px 20px;margin-top:70px;letter-spacing:1px}
.ser2{display:flex;align-items:center;gap:16px;font-size:40px;font-weight:800;margin-top:40px;color:#c9ced6}
.ser2 i{width:22px;height:22px;border-radius:50%}
.cd{font-size:300px;font-weight:900;line-height:.9;letter-spacing:-8px;margin-top:60px;color:#d71920}
.cdl{font-size:60px;font-weight:800;margin-top:10px}
.card{background:#1b1f25;border-radius:22px;padding:30px 34px;margin-top:40px;font-size:36px;line-height:1.4}
.card b{font-weight:800}
.card .tvl{color:#7fd3a0;font-size:30px;margin-top:8px}
.pod{margin-top:30px}
.pod div{display:flex;align-items:center;gap:24px;background:#1b1f25;border-radius:18px;padding:22px 28px;margin-bottom:14px;font-size:36px;font-weight:700}
.pod b{font-size:44px;width:60px;color:#d71920}
.pod span{margin-left:auto;color:#c9ced6;font-variant-numeric:tabular-nums}
.cols{columns:2;column-gap:36px;margin-top:30px}
.cols div{break-inside:avoid;font-size:27px;line-height:1.5;color:#e6e9ee;display:flex;gap:14px}
.cols div b{width:96px;flex:none;color:#9aa2ad;font-weight:700;font-variant-numeric:tabular-nums}
.cols .nw{color:#ff5a52;font-weight:800;font-size:20px;margin-left:6px}
.lst div{display:flex;align-items:center;justify-content:flex-start;gap:18px;font-size:34px;padding:16px 0;border-bottom:1px solid #2a2f37}
.lst div b{font-weight:700}
.lst div span{margin-left:auto;color:#c9ced6;font-variant-numeric:tabular-nums}
"""

def foot():
    return ('<div class="foot"><span>FML Rennkalender</span><span>@fmlrennkalender</span></div>'
            '<div class="redbar"></div><div class="flag"></div>')

def page(inner):
    return f'<div class="pg">{head()}{inner}{foot()}</div>'

# ---------- Daten ----------
def events(data):
    ser = {s["id"]: s for s in data["series"]}
    out = []
    for e in data["events"]:
        if e["s"] not in ser: continue
        a, b, t = span(e)
        out.append(dict(e=e, s=ser[e["s"]], a=a, b=b, t=t))
    return sorted(out, key=lambda x: (x["a"], x["t"] or datetime.min.replace(tzinfo=BER)))

def races(evs, sid=None):
    return [x for x in evs if not x["e"].get("type") and (sid is None or x["s"]["id"] == sid)]

def when(x):
    if x["t"]: return f'{WD[x["t"].weekday()]}, {dm(x["a"])} · {x["t"]:%H:%M} Uhr'
    if x["a"] != x["b"]: return f'{dm(x["a"])}–{dm(x["b"])}{x["b"].year}'
    return f'{WD[x["a"].weekday()]}, {dm(x["a"])}{x["a"].year}'

def tvline(x):
    tv = tv_names(x["e"], x["s"])
    return f'<div class="tvl">📺 {html.escape(" · ".join(tv))}</div>' if tv else ""

def evcard(x):
    place = " · ".join(html.escape(p) for p in (x["e"].get("track"), x["e"].get("country")) if p)
    return (f'<div class="card"><b>{html.escape(x["e"]["name"])}</b><br>{place}<br>{when(x)}{tvline(x)}</div>')

def sertag(s):
    return f'<div class="ser2"><i style="background:{s["color"]}"></i>{html.escape(s["name"])}</div>'

def last_sunday(y, m):
    d = date(y, m + 1, 1) - timedelta(days=1) if m < 12 else date(y, 12, 31)
    return d - timedelta(days=(d.weekday() - 6) % 7)

def nth_sunday(y, m, n):
    d = date(y, m, 1); d += timedelta(days=(6 - d.weekday()) % 7)
    return d + timedelta(days=7 * (n - 1))

def next_workday(d):
    d += timedelta(days=1)
    while d.weekday() > 4: d += timedelta(days=1)
    return d

# ---------- Zustand ----------
def load_state():
    try: return json.load(open(STATE, encoding="utf-8"))
    except Exception: return {"known": {}, "queue": [], "history": []}

def save_state(st):
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def update_known(st, evs):
    """Neue Saisons erkennen -> Warteschlange „Neu im Kalender“."""
    years = {}
    for x in races(evs): years.setdefault(x["s"]["id"], set()).add(x["a"].year)
    first_run = not st["known"]
    for sid, ys in years.items():
        known = set(st["known"].get(sid, []))
        for y in sorted(ys - known):
            if not first_run and known:
                st["queue"].append({"s": sid, "year": y})
        st["known"][sid] = sorted(known | ys)

# ---------- Vorlagen ----------
def t_titel(data, stand, day, sid):
    s = {x["id"]: x for x in data["series"]}[sid]; ch = stand[sid]["champion"]
    return page(f'<div class="tag2">🏆 TITEL ENTSCHIEDEN</div>{sertag(s)}'
                f'<div class="big" style="margin-top:50px">{html.escape(ch["name"])}</div>'
                f'<div class="txt">{html.escape(ch.get("title") or ("Meister " + s["name"]))}'
                + (f'<br>{html.escape(ch["team"])}' if ch.get("team") else "") + '</div>'
                '<div class="txt" style="font-size:34px;color:#9aa2ad">Glückwunsch! 🏁</div>')

def t_kalender(data, evs, sid, year):
    s = {x["id"]: x for x in data["series"]}[sid]
    rs = [x for x in races(evs, sid) if x["a"].year == year]
    rows = "".join(f'<div><b>{dm(x["b"])}</b>{html.escape(x["e"].get("track") or x["e"]["name"])}'
                   + ('<span class="nw">NEU</span>' if x["e"].get("new") else "") + '</div>' for x in rs[:40])
    return page(f'<div class="tag2">📅 NEU IM KALENDER</div>{sertag(s)}'
                f'<div class="mid">Saison {year}</div><div class="txt" style="margin-top:16px;font-size:34px">{len(rs)} Rennen · alle Termine in der App</div>'
                f'<div class="cols">{rows}</div>')

def podium(stand, sid, n=3):
    st = stand.get(sid)
    if not st or not st.get("tables"): return ""
    rows = st["tables"][0]["rows"][:n]
    return '<div class="pod">' + "".join(f'<div><b>{r[0]}</b>{html.escape(str(r[1]))}<span>{html.escape(str(r[3]))}</span></div>' for r in rows) + '</div>'

def t_finale(data, stand, x):
    return page(f'<div class="tag2">🏁 SAISONFINALE</div>{sertag(x["s"])}'
                f'<div class="mid">Am Wochenende fällt die Entscheidung</div>{evcard(x)}'
                + (f'<div class="lbl">Stand der Meisterschaft</div>{podium(stand, x["s"]["id"])}' if podium(stand, x["s"]["id"]) else ""))

def t_start(x, days):
    return page(f'<div class="tag2">🚦 SAISONSTART</div>{sertag(x["s"])}'
                f'<div class="cd">{days}</div><div class="cdl">{"Tag" if days == 1 else "Tage"} bis zum ersten Rennen</div>{evcard(x)}')

def t_zeit(change, us_change):
    back = change.month == 10
    gap_txt = ""
    if us_change and us_change != change:
        a, b = sorted([change, us_change])
        gap_txt = (f'<div class="card">⚠️ <b>USA-Rennen:</b> Vom {dm(a)} bis {dm(b - timedelta(days=1))} ist der Zeitunterschied '
                   f'zur US-Ostküste nur <b>5 statt 6 Stunden</b>.</div>')
    return page(f'<div class="tag2">⏰ ZEITUMSTELLUNG</div>'
                f'<div class="big" style="margin-top:60px">Uhren {"zurück" if back else "vor"}!</div>'
                f'<div class="txt">In der Nacht auf <b>Sonntag, {dm(change)}</b> werden die Uhren '
                f'{"eine Stunde zurück" if back else "eine Stunde vor"}gestellt.</div>'
                f'<div class="txt" style="font-size:36px">Alle Startzeiten bei uns sind automatisch in deutscher Zeit – du musst nichts umrechnen.</div>{gap_txt}')

def t_heim(xs):
    cards = "".join(f'<div class="card"><span class="dot2" style="background:{x["s"]["color"]}"></span> <b>{html.escape(x["s"]["name"])}</b> · '
                    f'{html.escape(x["e"]["name"])}<br>{html.escape(x["e"].get("track") or x["e"].get("country",""))} · {when(x)}{tvline(x)}</div>' for x in xs[:4])
    return page(f'<div class="tag2">🇩🇪 HEIMRENNEN</div><div class="mid">Motorsport vor der Haustür</div>{cards}')

def t_doppel(x1, x2):
    return page(f'<div class="tag2">⏩ DOPPEL-WOCHENENDE</div>{sertag(x1["s"])}'
                f'<div class="mid">Zwei Wochenenden in Folge</div>{evcard(x1)}{evcard(x2)}')

def t_neu(x):
    return page(f'<div class="tag2">✨ NEUE STRECKE</div>{sertag(x["s"])}'
                f'<div class="mid">Premiere: {html.escape(x["e"].get("track") or x["e"]["name"])}</div>{evcard(x)}')

def t_winter(data, evs, day):
    nxt = []
    for s in data["series"]:
        rs = [x for x in races(evs, s["id"]) if x["a"] > day]
        if rs: nxt.append((rs[0]["a"], s))
    nxt.sort(key=lambda t: t[0])
    rows = "".join(f'<div><span class="dot2" style="background:{s["color"]}"></span><b>{html.escape(s["name"])}</b><span>{dm(d)}{d.year}</span></div>' for d, s in nxt[:18])
    return page(f'<div class="tag2">❄️ WINTERPAUSE</div><div class="mid">Wann geht\'s weiter?</div><div class="lst" style="margin-top:40px">{rows}</div>')

def t_countdown(x, label, days):
    return page(f'<div class="tag2">⏳ COUNTDOWN</div>{sertag(x["s"])}'
                f'<div class="cd">{days}</div><div class="cdl">{"Tag" if days == 1 else "Tage"} bis {html.escape(label)}</div>{evcard(x)}')

def t_serie_fehlt(data):
    chips = "".join(f'<span><i style="background:{s["color"]}"></i>{html.escape(s["name"])}</span>' for s in data["series"])
    return page('<div class="big" style="margin-top:150px">Fehlt dir eine <em>Rennserie?</em></div>'
                '<div class="txt">Wir nehmen alles auf, was live mit deutschem Kommentar läuft – im TV, im Stream oder auf YouTube.</div>'
                '<div class="cta">💬 Antworte einfach auf diese Story!<small>Serie + wo sie auf Deutsch läuft</small></div>'
                f'<div class="lbl">Schon dabei</div><div class="chips">{chips}</div>')

# ---------- Auswahl ----------
def candidates(day, data, stand, evs, st):
    """Liefert Kandidaten (prio, key, slide_fn) – kleinere prio = wichtiger."""
    c = []
    done = {h["key"] for h in st["history"]}
    # Titel entschieden: nur am ersten Werktag nach der Entscheidung
    for sid, sd in stand.items():
        ch = sd.get("champion")
        if ch and ch.get("date") and next_workday(date.fromisoformat(ch["date"])) == day:
            c.append((0, f"titel:{sid}:{ch['date'][:4]}", lambda sid=sid: t_titel(data, stand, day, sid)))
    # Neu im Kalender
    for q in st["queue"]:
        c.append((1, f"kalender:{q['s']}:{q['year']}", lambda q=q: t_kalender(data, evs, q["s"], q["year"])))
    rs = races(evs)
    for s in data["series"]:
        sr = [x for x in rs if x["s"]["id"] == s["id"]]
        fut = [x for x in sr if x["a"] > day]
        if not fut: continue
        nx = fut[0]; dd = (nx["a"] - day).days
        prev = [x for x in sr if x["b"] < nx["a"]]
        after = [x for x in sr if x["a"] > nx["b"]]
        gap = (after[0]["a"] - nx["b"]).days if after else 999
        if dd <= 7 and s["id"] in stand and gap > 60 and (gap > 120 or after[0]["a"].year != nx["a"].year):  # echte Saisonpause, nur Serien mit Meisterschaft
            c.append((2, f"finale:{s['id']}:{nx['a']}", lambda nx=nx: t_finale(data, stand, nx)))
        if 1 <= dd <= 7 and prev and (nx["a"] - prev[-1]["b"]).days > 40:  # nur mit bekannter Vorsaison
            c.append((2, f"event:{s['id']}:{nx['a']}", lambda nx=nx, dd=dd: t_start(nx, dd)))  # je Veranstaltung nur 1x (Start ODER Countdown)
        if dd <= 7 and after and 5 <= (after[0]["a"] - nx["a"]).days <= 9 and nx["a"].weekday() >= 4:
            c.append((3, f"doppel:{s['id']}:{nx['a']}", lambda nx=nx, a=after[0]: t_doppel(nx, a)))
    # Zeitumstellung (Mo–Fr vor dem Umstellungs-Sonntag)
    for m, usn in ((3, 2), (10, None)):
        ch = last_sunday(day.year, m)
        us = nth_sunday(day.year, 3, 2) if m == 3 else nth_sunday(day.year, 11, 1)
        if 1 <= (ch - day).days <= 6:
            c.append((2, f"zeit:{ch}", lambda ch=ch, us=us: t_zeit(ch, us)))
    # Heimrennen in den nächsten 7 Tagen
    home = [x for x in rs if 1 <= (x["a"] - day).days <= 7 and x["e"].get("country") in HOME_COUNTRIES]
    if home:
        c.append((3, f"heim:{home[0]['a']}", lambda home=home: t_heim(home)))
    # Neue Strecke (Datenfeld "new": true) in den nächsten 14 Tagen
    for x in rs:
        if x["e"].get("new") and 1 <= (x["a"] - day).days <= 14:
            c.append((3, f"neu:{x['s']['id']}:{x['a']}", lambda x=x: t_neu(x)))
    # Winterpause: mind. 10 Serien ohne Rennen in den nächsten 30 Tagen, höchstens alle 21 Tage
    idle = [s for s in data["series"] if not [x for x in rs if x["s"]["id"] == s["id"] and 0 <= (x["a"] - day).days <= 30]]
    last_w = [h["date"] for h in st["history"] if h["key"].startswith("winter")]
    if len(idle) >= 10 and (not last_w or (day - date.fromisoformat(max(last_w))).days >= 21):
        c.append((3, f"winter:{day}", lambda: t_winter(data, evs, day)))
    # Countdown zu Highlights (2 Wochen / 1 Woche vorher je einmal)
    try: hls = json.load(open(os.path.join(ROOT, "insta", "highlights.json"), encoding="utf-8"))
    except Exception: hls = []
    for h in hls:
        cand = [x for x in rs if x["s"]["id"] == h["s"] and 1 <= (x["a"] - day).days <= 14]
        if h.get("match"): cand = [x for x in cand if re.search(h["match"], x["e"]["name"])]
        if h.get("first"):
            cand = [x for x in cand if not [y for y in rs if y["s"]["id"] == h["s"] and 0 < (x["a"] - y["b"]).days <= 40]]
        if cand:
            x = cand[0]; dd = (x["a"] - day).days
            c.append((4, f"event:{x['s']['id']}:{x['a']}", lambda x=x, dd=dd, h=h: t_countdown(x, h["label"], dd)))  # max. 1x, max. 14 Tage vorher
    # Serie fehlt? alle 14 Tage
    last_s = [h["date"] for h in st["history"] if h["key"].startswith("seriefehlt")]
    if not last_s or (day - date.fromisoformat(max(last_s))).days >= 14:
        c.append((5, f"seriefehlt:{day}", lambda: t_serie_fehlt(data)))
    return [x for x in c if x[1] not in done]

def pick(day, dry=False):
    data = load()
    try: stand = json.load(open(os.path.join(ROOT, "data", "standings.json"), encoding="utf-8"))
    except Exception: stand = {}
    evs = events(data)
    st = load_state()
    update_known(st, evs)
    week0 = day - timedelta(days=day.weekday())
    used = len([h for h in st["history"] if date.fromisoformat(h["date"]) >= week0 and not h["key"].startswith("titel")])
    cands = sorted(candidates(day, data, stand, evs, st), key=lambda t: t[0])
    if used >= WEEK_CAP:
        cands = [x for x in cands if x[1].startswith("titel")]
    if not cands:
        if not dry: save_state(st)
        return None, None
    prio, key, fn = cands[0]
    slide = fn()
    if not dry:
        st["history"].append({"date": str(day), "key": key})
        if key.startswith("kalender:"):
            _, sid, y = key.split(":"); st["queue"] = [q for q in st["queue"] if not (q["s"] == sid and str(q["year"]) == y)]
        save_state(st)
    return slide, key

# ---------- Entwürfe ----------
def draft(kind, day):
    data = load(); evs = events(data)
    stand = json.load(open(os.path.join(ROOT, "data", "standings.json"), encoding="utf-8"))
    rs = races(evs)
    fut = lambda sid: [x for x in rs if x["s"]["id"] == sid and x["a"] > day]
    if kind == "titel":
        stand = dict(stand); sd = dict(stand["sbk"]); sd["champion"] = {"name": "Nicolò Bulega", "title": "Superbike-Weltmeister 2026", "date": "2026-10-11"}; stand["sbk"] = sd
        return t_titel(data, stand, day, "sbk")
    if kind == "kalender": return t_kalender(data, evs, "mgp", 2027)
    if kind == "finale": return t_finale(data, stand, fut("sbk")[0])
    if kind == "start":
        x = fut("fe")[0]; return t_start(x, (x["a"] - day).days)
    if kind == "zeit": return t_zeit(last_sunday(day.year, 10), nth_sunday(day.year, 11, 1))
    if kind == "heim": return t_heim([x for x in rs if x["e"].get("country") in HOME_COUNTRIES and x["a"] > day][:3])
    if kind == "doppel": f = fut("mgp"); return t_doppel(f[0], f[1])
    if kind == "neu": return t_neu([x for x in rs if x["s"]["id"] == "mgp" and "Argentin" in x["e"]["name"]][0])
    if kind == "winter": return t_winter(data, evs, date(2026, 12, 14))
    if kind == "countdown":
        x = [x for x in rs if x["s"]["id"] == "imsa" and "Rolex" in x["e"]["name"]][0]; return t_countdown(x, "Rolex 24 Daytona", 14)
    if kind == "serie_fehlt": return t_serie_fehlt(data)

def render_story(slide, out):
    make_post.CSS = CSS + EXTRA
    make_post.render([slide], out, story=True)

if __name__ == "__main__":
    a = sys.argv[1:]
    out = a[a.index("--out") + 1] if "--out" in a else None
    if a[0] == "draft":
        render_story(draft(a[1], date.fromisoformat(a[2])), out); print(out)
    elif a[0] == "pick":
        day = date.fromisoformat(a[1]); s, k = pick(day, dry=True); print(k)
        if s and out: render_story(s, out)
