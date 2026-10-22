#!/usr/bin/env python3
"""Postet einen Ordner aus posts/ zusätzlich auf die Facebook-Seite „FML Rennkalender“.

story.jpg → Seiten-Story · reel.mp4 → Facebook-Reel · sonst 1.jpg … n.jpg → Beitrag mit mehreren Bildern.
Die Bildunterschrift wird für Facebook angepasst (Link anklickbar statt „Link in der Bio“, keine @-Erwähnungen,
nur 2 Hashtags). Benötigt FB_PAGE_TOKEN und FB_PAGE_ID (GitHub-Secrets).

Aufruf: python3 insta/fb_post.py posts/2026-10-19-weekreel
"""
import os, sys, re, time, json, glob, urllib.request, urllib.parse, urllib.error

API = "https://graph.facebook.com/v21.0"
BASE_URL = "https://raw.githubusercontent.com/langflo163/FML-Racekalender/main/"
APP = "https://langflo163.github.io/FML-Racekalender/"

def fail(msg):
    msg = msg.replace(os.environ.get("FB_PAGE_TOKEN", "") or "\0", "***")
    print(f"::error::Facebook: {msg}"); sys.exit(1)

def call(path, method="POST", headers=None, base=API, **params):
    if "access_token" not in params: params["access_token"] = os.environ["FB_PAGE_TOKEN"]
    if not params["access_token"]: params.pop("access_token")
    data = urllib.parse.urlencode(params).encode() if params else b""
    url = f"{base}/{path}"
    req = urllib.request.Request(url + ("?" + data.decode() if method == "GET" else ""),
                                 data=None if method == "GET" else data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        fail(f"{e.code} bei {path}: {e.read().decode(errors='replace')}")

def fb_caption(text):
    out = []
    for line in text.splitlines():
        if line.startswith("Mit dabei:"):
            continue
        if "Link in der Bio" in line:
            line = "📲 Alle Termine & Sender: " + APP
        if line.startswith("#"):
            line = " ".join(line.split()[:2])
        out.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()

def wait_public(url, tries=30):
    for _ in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                if r.status == 200: return
        except Exception:
            pass
        time.sleep(10)
    fail(f"Datei nicht öffentlich erreichbar: {url}")

def main(folder):
    for k in ("FB_PAGE_TOKEN", "FB_PAGE_ID"):
        if not os.environ.get(k): fail(f"Secret {k} fehlt")
    page = os.environ["FB_PAGE_ID"]
    url_of = lambda p: BASE_URL + os.path.relpath(p).replace(os.sep, "/")
    cap_file = os.path.join(folder, "caption.txt")
    caption = fb_caption(open(cap_file, encoding="utf-8").read()) if os.path.exists(cap_file) else ""
    story, reel = os.path.join(folder, "story.jpg"), os.path.join(folder, "reel.mp4")

    if os.path.exists(story):
        u = url_of(story); wait_public(u)
        pid = call(f"{page}/photos", url=u, published="false")["id"]
        r = call(f"{page}/photo_stories", photo_id=pid)
        print("Facebook-Story veröffentlicht:", r.get("post_id")); return

    if os.path.exists(reel):
        u = url_of(reel); wait_public(u)
        vid = call(f"{page}/video_reels", upload_phase="start")["video_id"]
        call(vid, base="https://rupload.facebook.com/video-upload/v21.0",
             headers={"Authorization": "OAuth " + os.environ["FB_PAGE_TOKEN"], "file_url": u}, access_token="")
        for _ in range(30):   # warten, bis Facebook die Datei geladen hat
            st = call(vid, method="GET", fields="status").get("status", {})
            if st.get("uploading_phase", {}).get("status") == "complete": break
            time.sleep(10)
        r = call(f"{page}/video_reels", video_id=vid, upload_phase="finish", video_state="PUBLISHED", description=caption)
        print("Facebook-Reel veröffentlicht:", vid, r.get("success")); return

    imgs = sorted(glob.glob(os.path.join(folder, "*.jpg")), key=lambda p: int(os.path.basename(p)[:-4]))[:10]
    if not imgs: fail("Keine Bilder gefunden")
    ids = []
    for p in imgs:
        u = url_of(p); wait_public(u)
        ids.append(call(f"{page}/photos", url=u, published="false")["id"])
    media = {f"attached_media[{i}]": json.dumps({"media_fbid": x}) for i, x in enumerate(ids)}
    r = call(f"{page}/feed", message=caption, **media)
    print("Facebook-Beitrag veröffentlicht:", r.get("id"))

if __name__ == "__main__":
    main(sys.argv[1])
