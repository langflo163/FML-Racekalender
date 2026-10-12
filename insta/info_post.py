#!/usr/bin/env python3
"""Einmaliger Info-Post: Wann wird was gepostet. Ausgabe: posts/info-zeiten/1.jpg + caption.txt"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_post import CSS, head, render, ROOT, APP_URL

EXTRA = """
.blk{display:flex;gap:30px;align-items:center;background:#1b1f25;border-radius:22px;padding:30px 36px;margin-bottom:20px}
.when{width:210px;flex:none}
.when b{display:block;font-size:46px;font-weight:900;line-height:1.05}
.when span{display:block;font-size:30px;color:#d71920;font-weight:800;margin-top:6px}
.what{flex:1}
.what b{display:block;font-size:38px;font-weight:800}
.what span{display:block;font-size:27px;color:#c9ced6;margin-top:6px;line-height:1.3}
.what i.ty{font-style:normal;display:inline-block;font-size:22px;font-weight:800;border:2px solid #9aa2ad;color:#c9ced6;border-radius:8px;padding:1px 10px;margin-left:10px;vertical-align:6px}
.note2{margin-top:22px;font-size:28px;color:#9aa2ad;line-height:1.45}
"""
slide = f'''<div class="pg">{head()}
<h1 style="margin-top:56px;font-size:84px">So läuft's <em>hier</em></h1>
<div class="sub" style="font-size:36px;margin-bottom:40px">Alle Rennen mit deutscher Übertragung – automatisch.</div>
<div class="blk"><div class="when"><b>Montag</b><span>9:00 Uhr</span></div>
 <div class="what"><b>Die Rennwoche<i class="ty">Beitrag</i></b><span>Alle Rennen, Qualis &amp; Sprints von Montag bis Sonntag</span></div></div>
<div class="blk"><div class="when"><b>Freitag</b><span>12:00 Uhr</span></div>
 <div class="what"><b>Das Wochenende<i class="ty">Reel</i></b><span>Freitag bis Sonntag auf einen Blick</span></div></div>
<div class="blk"><div class="when"><b>Renntage</b><span>8:00 Uhr</span></div>
 <div class="what"><b>Heute live<i class="ty">Story</i></b><span>Startzeiten &amp; Sender des Tages – Nachtrennen schon am Vortag</span></div></div>
<div class="note2">Alle Zeiten in deutscher Zeit · Sender mit deutschem Kommentar<br>📲 Alle Termine jederzeit in der App – Link in der Bio</div>
<div class="foot"><span>FML Rennkalender</span><span>@fmlrennkalender</span></div>
<div class="redbar"></div><div class="flag"></div></div>'''

caption = f"""🏁 Willkommen beim FML Rennkalender!

Hier findest du alle Motorsport-Termine mit deutscher Übertragung – automatisch und pünktlich:

📅 Montag, 9:00 Uhr – Die Rennwoche (Mo–So)
🎬 Freitag, 12:00 Uhr – Das Wochenende als Reel
🔴 An Renntagen, 8:00 Uhr – Story „Heute live“ mit Startzeiten & Sendern

Alle Zeiten in deutscher Zeit, ohne Gewähr.
📲 Alle Termine, Sender & Tabellen in der App: Link in der Bio ({APP_URL})

#motorsport #rennkalender #formel1 #motogp #dtm #wec #nascar #indycar #racing #motorsportdeutschland"""

if __name__ == "__main__":
    import make_post
    make_post.CSS = CSS + EXTRA
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "posts", "info-zeiten")
    make_post.render([slide], out)
    open(os.path.join(out, "caption.txt"), "w", encoding="utf-8").write(caption)
    print(out)
