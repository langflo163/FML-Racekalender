#!/usr/bin/env python3
"""Storys für rennfreie Tage. Aufruf: python3 insta/free_story.py <vorlage> --out DIR
Vorlagen: serie_fehlt"""
import os, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_post
from make_post import CSS, head, ROOT

EXTRA = """
.big{font-size:118px;font-weight:900;line-height:1.02;letter-spacing:-2px;margin-top:150px}
.big em{font-style:normal;color:#d71920}
.txt{font-size:44px;color:#c9ced6;margin-top:50px;line-height:1.35;font-weight:600}
.cta{margin-top:70px;background:#d71920;border-radius:24px;padding:38px 40px;font-size:46px;font-weight:800;line-height:1.3}
.cta small{display:block;font-size:30px;font-weight:600;opacity:.9;margin-top:10px}
.chips{display:flex;flex-wrap:wrap;gap:12px;margin-top:70px}
.chips span{font-size:24px;font-weight:700;color:#c9ced6;border:2px solid #2a2f37;border-radius:999px;padding:8px 18px;display:flex;align-items:center;gap:10px}
.chips i{width:14px;height:14px;border-radius:50%;display:inline-block}
.lbl{font-size:28px;color:#9aa2ad;margin-top:60px;font-weight:700;text-transform:uppercase;letter-spacing:1px}
"""

def foot():
    return ('<div class="foot"><span>FML Rennkalender</span><span>@fmlrennkalender</span></div>'
            '<div class="redbar"></div><div class="flag"></div>')

def serie_fehlt():
    data = json.load(open(os.path.join(ROOT, "data", "races.json"), encoding="utf-8"))
    chips = "".join(f'<span><i style="background:{s["color"]}"></i>{html.escape(s["name"])}</span>' for s in data["series"])
    return (f'<div class="pg">{head()}'
            '<div class="big">Fehlt dir eine <em>Rennserie?</em></div>'
            '<div class="txt">Wir nehmen alles auf, was live mit deutschem Kommentar läuft – im TV, im Stream oder auf YouTube.</div>'
            '<div class="cta">💬 Antworte einfach auf diese Story!<small>Serie + wo sie auf Deutsch läuft</small></div>'
            f'<div class="lbl">Schon dabei</div><div class="chips">{chips}</div>'
            f'{foot()}</div>')

TEMPLATES = {"serie_fehlt": serie_fehlt}

if __name__ == "__main__":
    argv = sys.argv[1:]
    out = argv[argv.index("--out") + 1] if "--out" in argv else None
    name = argv[0]
    out = out or os.path.join(ROOT, "posts", f"frei-{name}")
    make_post.CSS = CSS + EXTRA
    make_post.render([TEMPLATES[name]()], out, story=True)
    print(out)
