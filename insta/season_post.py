#!/usr/bin/env python3
"""Saisonkalender einer Serie als Karussell (zum Anpinnen/Nachschauen).
Aufruf: python3 insta/season_post.py nas 2027 [OUT]  → Bilder 1.jpg … + caption.txt"""
import os, sys, json, re
from datetime import date, datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_post import CSS, head, render, ROOT, APP_URL, WD, hashtags, mentions, TAG_SERIES
import make_post

BER = ZoneInfo("Europe/Berlin")
EXTRA = """
.ttl{font-size:76px;font-weight:900;line-height:1.02;margin-top:46px}
.ttl em{font-style:normal;color:var(--c)}
.cnt{font-size:34px;color:#c9ced6;margin:14px 0 30px}
.row{display:flex;align-items:center;gap:22px;padding:13px 0;border-bottom:2px solid #22272e}
.row .d{width:170px;flex:none;font-size:34px;font-weight:900}
.row .d span{display:block;font-size:22px;color:#9aa2ad;font-weight:700}
.row .t{flex:1;font-size:33px;font-weight:700;line-height:1.15}
.row .t i{font-style:normal;display:block;font-size:24px;color:#9aa2ad;font-weight:600;margin-top:2px}
.row.top .t{color:var(--c)}
.tag{flex:none;font-size:20px;font-weight:800;border:2px solid #9aa2ad;color:#c9ced6;border-radius:8px;padding:2px 10px}
.tag.po{border-color:var(--c);color:var(--c)}
.big{display:flex;flex-direction:column;gap:18px;margin-top:10px}
.big div{background:#1b1f25;border-radius:20px;padding:24px 30px;border-left:10px solid var(--c)}
.big b{display:block;font-size:42px;font-weight:900}
.big span{font-size:28px;color:#c9ced6}
.hint{margin-top:28px;font-size:28px;color:#9aa2ad;line-height:1.45}
.pgn{font-size:26px;color:#9aa2ad;font-weight:700;margin-top:30px}
"""
HL = ("Daytona 500", "Coca-Cola 600", "Brickyard 400", "Southern 500", "Championship Race")

def ishl(e):
    return bool(e.get("hl")) or any(h in e["name"] for h in HL)

def evdate(e):
    if e.get("start"): return datetime.fromisoformat(e["start"]).astimezone(BER).date()
    return date.fromisoformat(e.get("date") or e.get("to"))

def main(sid, year, out):
    data = json.load(open(os.path.join(ROOT, "data", "races.json"), encoding="utf-8"))
    ser = next(s for s in data["series"] if s["id"] == sid)
    evs = sorted([e for e in data["events"] if e["s"] == sid and not e.get("type") and str(evdate(e).year) == year], key=evdate)
    pts = [e for e in evs if "Einladungsrennen" not in (e.get("note") or "")]
    po_start = next((i for i, e in enumerate(evs) if evdate(e) >= date(int(year), 9, 1) and "Darlington" not in (e.get("track") or e["name"])), None) if sid == "nas" else None
    color = ser.get("color", "#d71920")
    foot = '<div class="foot"><span>FML Rennkalender</span><span>@fmlrennkalender</span></div><div class="redbar"></div><div class="flag"></div>'
    def row(i, e):
        d = evdate(e); name, track = e["name"], e.get("track") or ""
        sub = track if track and track not in name else ""
        tag = ""
        if "Einladungsrennen" in (e.get("note") or ""): tag = '<span class="tag">Einladung</span>'
        elif po_start is not None and i >= po_start: tag = '<span class="tag po">Playoffs</span>'
        if "Championship" in name: name, sub = "Titelentscheidung", track
        hl = " top" if ishl(e) else ""
        return f'<div class="row{hl}"><div class="d">{d:%d.%m.}<span>{WD[d.weekday()]}</span></div><div class="t">{name}{f"<i>{sub}</i>" if sub else ""}</div>{tag}</div>'
    first, last = evdate(evs[0]), evdate(evs[-1])
    hls = [e for e in evs if ishl(e)][:5]
    cover = f'''<div class="pg" style="--c:{color}">{head()}
<div class="ttl">{ser["name"]}<br><em>Kalender {year}</em></div>
<div class="cnt">{len(pts)} Rennen · {first:%d.%m.} – {last:%d.%m.%Y}</div>
<div class="big">''' + "".join(
        f'<div><b>{("Titelentscheidung" if "Championship" in e["name"] else e["name"])}</b><span>{WD[evdate(e).weekday()]}, {evdate(e):%d.%m.%Y} · {e.get("track") or ""}</span></div>'
        for e in (hls or [evs[0], evs[-1]])) + f'''</div>
<div class="hint">👉 Wischen für alle Termine · Startzeiten &amp; Sender in deutscher Zeit kurz vorher in der App &amp; Story</div>
{foot}</div>'''
    per = 10
    chunks = [evs[i:i + per] for i in range(0, len(evs), per)]
    slides = [cover]
    for n, ch in enumerate(chunks, 1):
        rows = "".join(row(evs.index(e), e) for e in ch)
        slides.append(f'<div class="pg" style="--c:{color}">{head()}<div class="pgn">{ser["name"]} {year} · Teil {n}/{len(chunks)}</div><div style="margin-top:14px">{rows}</div>{foot}</div>')
    make_post.CSS = CSS + EXTRA
    render(slides, out)
    sids = {sid}
    ment = mentions(sids)
    cap = f"""🏁 {ser['name']} – der komplette Kalender {year}
Speichern 🔖 und jederzeit nachschauen! Auf welches Rennen freust du dich am meisten? 👇

{len(pts)} Rennen von {first:%d.%m.} bis {last:%d.%m.%Y}""" + ((" – Highlights:\n" + "\n".join(f"• {evdate(e):%d.%m.} {('Titelentscheidung ' + (e.get('track') or '')) if 'Championship' in e['name'] else e['name']}" for e in hls)) if hls else "") + f"""

Startzeiten in deutscher Zeit und Sender mit deutschem Kommentar gibt's kurz vor jedem Rennen hier und in der App (Link in der Bio). Ohne Gewähr.
""" + (f"\nMit dabei: {' · '.join(ment)}\n" if ment else "") + "\n" + hashtags(sids)
    open(os.path.join(out, "caption.txt"), "w", encoding="utf-8").write(cap)
    print(out, len(slides), "Bilder")

ORDER = [sid for sid, _ in TAG_SERIES]

def pick(today):
    """Nächste Serie für den Sonntags-Kalenderpost: Saison laut races.json als komplett markiert ("complete": [Jahr]),
    noch nicht gepostet (state.json "season_posted"), Saison noch nicht vorbei. Reihenfolge = Größe der Serie."""
    data = json.load(open(os.path.join(ROOT, "data", "races.json"), encoding="utf-8"))
    sp = os.path.join(ROOT, "insta", "state.json")
    st = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {}
    done = set(st.get("season_posted", []))
    cands = []
    for s_ in data["series"]:
        for y in s_.get("complete", []):
            key = f"{s_['id']}:{y}"
            if key in done or y < today.year: continue
            evs = [e for e in data["events"] if e["s"] == s_["id"] and not e.get("type") and evdate(e).year == y]
            if not evs or max(map(evdate, evs)) < today: continue
            rank = ORDER.index(s_["id"]) if s_["id"] in ORDER else 99
            cands.append((y, rank, s_["id"], key))
    if not cands: return None
    y, _, sid, key = sorted(cands)[0]
    return sid, str(y), key

def mark(key):
    sp = os.path.join(ROOT, "insta", "state.json")
    st = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {}
    st.setdefault("season_posted", [])
    if key not in st["season_posted"]: st["season_posted"].append(key)
    json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    sid, year = sys.argv[1], sys.argv[2]
    main(sid, year, sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, "posts", f"saison-{sid}-{year}"))
