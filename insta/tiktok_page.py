#!/usr/bin/env python3
"""Legt das neueste Reel für TikTok bereit: posts/neu/reel.mp4 + posts/neu/index.html (Video sichern + Text kopieren).
Feste Adresse für Flo: https://langflo163.github.io/FML-Racekalender/posts/neu/
Aufruf: python3 insta/tiktok_page.py posts/2026-10-23-weekend"""
import os, sys, re, shutil, html

def tiktok_caption(text):
    lines = text.splitlines()
    tags = next((l for l in reversed(lines) if l.startswith("#")), "")
    head = [l for l in lines[:2] if l.strip()]                     # Titel + Frage
    races, day = [], ""
    for l in lines:   # nur Rennen (keine Quali/Sprint), mit Wochentag
        m = re.match(r"^📅 (\w\w) ", l)
        if m: day = m.group(1)
        elif re.match(r"^\d\d:\d\d ", l) and "(" not in l: races.append(f"{day} {l}")
    races = races[:6]
    extra = ["#motorsportdeutschland", "#rennkalender"]
    t = " ".join(dict.fromkeys(tags.split() + extra))
    return "\n".join(head + [""] + races + ["", "Alle Zeiten deutsche Zeit · Sender in der App (Link im Profil)", "", t]).strip()

def main(folder):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "posts", "neu")
    os.makedirs(out, exist_ok=True)
    shutil.copy(os.path.join(folder, "reel.mp4"), os.path.join(out, "reel.mp4"))
    cap = tiktok_caption(open(os.path.join(folder, "caption.txt"), encoding="utf-8").read())
    with open(os.path.join(out, "tiktok.txt"), "w", encoding="utf-8") as f:
        f.write(cap)
    page = f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>FML – neues Reel</title><style>
:root{{color-scheme:light dark}}body{{margin:0;font-family:-apple-system,Segoe UI,Arial,sans-serif;background:#111418;color:#fff;padding:16px;max-width:520px;margin:auto}}
h1{{font-size:20px}}h1 b{{background:#d71920;padding:2px 6px;border-radius:5px;margin-right:4px}}video{{width:100%;border-radius:10px;background:#000}}
a.btn,button{{display:block;width:100%;box-sizing:border-box;margin:10px 0;padding:14px;border:0;border-radius:10px;background:#d71920;color:#fff;font-size:17px;font-weight:700;text-align:center;text-decoration:none}}
pre{{white-space:pre-wrap;background:#1e232a;padding:12px;border-radius:10px;font-size:14px}}small{{color:#9aa2ad}}</style></head><body>
<h1><b>FML</b> Neues Reel – {html.escape(os.path.basename(folder))}</h1>
<video src="reel.mp4" controls playsinline></video>
<a class="btn" href="reel.mp4" download>1. Video öffnen → Teilen → Video sichern</a>
<button onclick="navigator.clipboard.writeText(document.getElementById('t').innerText).then(()=>this.textContent='✓ Text kopiert')">2. TikTok-Text kopieren</button>
<pre id="t">{html.escape(cap)}</pre>
<small>3. In TikTok: + → Video wählen → Sound aussuchen → Text einfügen → Posten</small>
</body></html>"""
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("TikTok-Seite bereit:", out)

if __name__ == "__main__":
    main(sys.argv[1])
