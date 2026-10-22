#!/usr/bin/env python3
"""Titelbild für die Facebook-Seite (1640×624, Inhalt mittig für Handy-Zuschnitt). Aufruf: python3 insta/fb_cover.py OUT.jpg"""
import sys
from playwright.sync_api import sync_playwright
HTML = """<html><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0;padding:0}
body{width:1640px;height:624px;background:#111418;color:#fff;font-family:Inter,'DejaVu Sans',Arial,sans-serif;overflow:hidden;position:relative}
.c{position:absolute;left:0;right:0;top:150px;display:flex;flex-direction:column;align-items:center}
.top{display:flex;align-items:center;gap:30px}
.fml{display:flex;gap:10px}
.fml span{width:92px;height:80px;background:#d71920;border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:54px}
.brand{font-size:84px;font-weight:900;letter-spacing:-2px}
.tag{margin-top:34px;font-size:40px;font-weight:700;color:#fff}
.tag em{font-style:normal;color:#d71920}
.ser{margin-top:26px;font-size:24px;color:#9aa2ad;font-weight:600;letter-spacing:.5px}
.redbar{position:absolute;left:0;right:0;bottom:30px;height:12px;background:#d71920}
.flag{position:absolute;left:0;right:0;bottom:0;height:30px;background:repeating-conic-gradient(#fff 0 25%,#111418 0 50%) 0 0/30px 30px}
</style></head><body><div class="c">
<div class="top"><div class="fml"><span>F</span><span>M</span><span>L</span></div><div class="brand">Rennkalender</div></div>
<div class="tag">Alle Rennen <em>·</em> deutsche Startzeit <em>·</em> wo's auf Deutsch läuft</div>
<div class="ser">F1 · MotoGP · WEC · DTM · NASCAR · IndyCar · Formel E · WorldSBK · IMSA · GT World · NLS</div>
</div><div class="redbar"></div><div class="flag"></div></body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1640, "height": 624})
    pg.set_content(HTML); pg.wait_for_timeout(200)
    pg.screenshot(path=sys.argv[1], type="jpeg", quality=95); b.close()
