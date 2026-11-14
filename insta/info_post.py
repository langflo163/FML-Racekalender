#!/usr/bin/env python3
"""Info-Post: Wann wird was gepostet (Stand 14.11.2026, ohne App-Hinweis). Ausgabe: posts/info-zeiten-2/1.jpg + caption.txt"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_post import CSS, head, render, ROOT

EXTRA = """
.blk{display:flex;gap:28px;align-items:center;background:#1b1f25;border-radius:20px;padding:20px 32px;margin-bottom:14px}
.when{width:210px;flex:none}
.when b{display:block;font-size:40px;font-weight:900;line-height:1.05}
.when span{display:block;font-size:30px;color:#d71920;font-weight:800;margin-top:6px}
.what{flex:1}
.what b{display:block;font-size:34px;font-weight:800}
.what span{display:block;font-size:24px;color:#c9ced6;margin-top:6px;line-height:1.3}
.what i.ty{font-style:normal;display:inline-block;font-size:22px;font-weight:800;border:2px solid #9aa2ad;color:#c9ced6;border-radius:8px;padding:1px 10px;margin-left:10px;vertical-align:6px}
.note2{margin-top:22px;font-size:28px;color:#9aa2ad;line-height:1.45}
"""
def blk(when, at, what, ty, txt):
    return (f'<div class="blk"><div class="when"><b>{when}</b><span>{at}</span></div>'
            f'<div class="what"><b>{what}<i class="ty">{ty}</i></b><span>{txt}</span></div></div>')

slide = f'''<div class="pg">{head()}
<h1 style="margin-top:44px;font-size:80px">So läuft's <em>hier</em></h1>
<div class="sub" style="font-size:34px;margin-bottom:30px">Alle Rennen mit deutscher Übertragung – automatisch.</div>
{blk("Montag", "9:00 Uhr", "Die Rennwoche", "Beitrag", "Alle Rennen, Qualis &amp; Sprints von Montag bis Sonntag")}
{blk("Montag", "18:00 Uhr", "Die Rennwoche", "Reel", "Die Woche als kurzes Video")}
{blk("Freitag", "12:00 Uhr", "Das Wochenende", "Reel", "Freitag bis Sonntag auf einen Blick")}
{blk("Renntage", "8:00 Uhr", "Heute live", "Story", "Startzeiten &amp; Sender des Tages – Nachtrennen schon am Vortag")}
{blk("Sonntag", "20:00 Uhr", "Saisonkalender", "Beitrag", "Der komplette Kalender einer Serie, sobald er feststeht")}
<div class="note2">An rennfreien Tagen gibt's ab und zu eine Bonus-Story: Weltmeister, Saisonstart, Highlights …<br>Alle Zeiten in deutscher Zeit · Sender mit deutschem Kommentar</div>
<div class="foot"><span>FML Rennkalender</span><span>@fmlrennkalender</span></div>
<div class="redbar"></div><div class="flag"></div></div>'''

caption = """🏁 Willkommen beim FML Rennkalender!
Folgen und nichts mehr verpassen 🔔 – welche Serie schaust du am liebsten? 👇

Hier findest du alle Motorsport-Termine mit deutscher Übertragung – automatisch und pünktlich:

📅 Montag, 9:00 Uhr – Die Rennwoche (Mo–So)
🎬 Montag, 18:00 Uhr – Die Rennwoche als Reel
🎬 Freitag, 12:00 Uhr – Das Wochenende als Reel
🔴 An Renntagen, 8:00 Uhr – Story „Heute live“ mit Startzeiten & Sendern
🗓️ Sonntag, 20:00 Uhr – Der komplette Saisonkalender einer Serie (sobald er feststeht)
✨ An rennfreien Tagen ab und zu eine Bonus-Story

Alle Zeiten in deutscher Zeit, ohne Gewähr.

#motorsport #racing #f1 #motogp #nascar"""

if __name__ == "__main__":
    import make_post
    make_post.CSS = CSS + EXTRA
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "posts", "info-zeiten-2")
    make_post.render([slide], out)
    open(os.path.join(out, "caption.txt"), "w", encoding="utf-8").write(caption)
    print(out)
