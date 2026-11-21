#!/usr/bin/env python3
"""Einmaliger Nachtrag-Post: FIA GT World Cup Macau 22.11.2026 (Flo 21.11.). Ausgabe: posts/nachtrag-macau-2026/1.jpg + caption.txt"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_post import CSS, head, render, ROOT
import make_post

EXTRA = """
.tag0{display:inline-block;margin-top:46px;font-size:28px;font-weight:800;letter-spacing:2px;color:#d71920;border:3px solid #d71920;border-radius:10px;padding:4px 16px}
.big{font-size:86px;font-weight:900;line-height:1.02;margin-top:22px}
.big em{font-style:normal;color:#d71920}
.sub2{font-size:34px;color:#c9ced6;margin-top:16px}
.mc{background:#1b1f25;border-radius:22px;padding:30px 36px;margin-top:40px;border-left:12px solid #00897b}
.mc .md{font-size:30px;color:#9aa2ad;font-weight:700}
.mc .mt{font-size:74px;font-weight:900;margin-top:4px}
.mc .mr{font-size:32px;font-weight:700;margin-top:6px}
.mtv{margin-top:26px;display:flex;flex-direction:column;gap:14px}
.mtv div{background:#1b1f25;border-radius:18px;padding:20px 30px;font-size:30px}
.mtv b{display:block;font-size:36px;color:#fff}
.mtv span{color:#9aa2ad;font-size:26px}
"""
slide = f'''<div class="pg">{head()}
<div class="tag0">NACHTRAG</div>
<div class="big">Fast vergessen: <em>GT3 in Macau</em> 🙈</div>
<div class="sub2">FIA GT World Cup – der GT3-Klassiker auf dem Guia Circuit</div>
<div class="mc"><div class="md">SONNTAG, 22. NOVEMBER</div><div class="mt">5:35 Uhr</div><div class="mr">Hauptrennen · 16 Runden · deutsche Zeit</div></div>
<div class="mtv">
<div><b>▶ YouTube-Livestream</b><span>Motorsport Television Deutschland – kostenlos, auf Deutsch</span></div>
<div><b>📺 ORF Sport+</b><span>Live ab 5:30 Uhr mit deutschem Kommentar</span></div>
</div>
<div class="foot"><span>FML Rennkalender</span><span>@fmlrennkalender</span></div>
<div class="redbar"></div><div class="flag"></div></div>'''

caption = """🙈 Nachtrag: Den FIA GT World Cup in Macau hatten wir nicht im Kalender – sorry!
Stehst du dafür um 5:30 Uhr auf? ⏰👇

🏁 Macau GT Cup – FIA GT World Cup (GT3)
📅 Sonntag, 22. November, 5:35 Uhr (deutsche Zeit), 16 Runden auf dem Guia Circuit

▶ Kostenlos im YouTube-Livestream von Motorsport Television Deutschland – auf Deutsch
📺 Außerdem live auf ORF Sport+ ab 5:30 Uhr

Ab sofort ist Macau fest im Kalender. Ohne Gewähr.

#motorsport #racing #gt3 #macau #fiagtworldcup"""

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "posts", "nachtrag-macau-2026")
    make_post.CSS = CSS + EXTRA
    render([slide], out)
    open(os.path.join(out, "caption.txt"), "w", encoding="utf-8").write(caption)
    print(out)
