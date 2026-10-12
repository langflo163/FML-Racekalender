#!/usr/bin/env python3
"""Postet einen Ordner aus posts/ (1.jpg … n.jpg + caption.txt) als Instagram-Karussell.

Benötigt Umgebungsvariablen IG_TOKEN und IG_USER_ID (GitHub-Secrets).
Die Bilder müssen öffentlich erreichbar sein – sie werden vorher ins Repo gepusht
und über raw.githubusercontent.com ausgeliefert (BASE_URL).

Aufruf: python3 insta/post.py posts/2026-10-12-week
"""
import os, sys, time, json, glob, urllib.request, urllib.parse, urllib.error

def fail(msg):
    # als GitHub-Annotation sichtbar (ohne Token)
    msg = msg.replace(os.environ.get("IG_TOKEN", "") or "\0", "***")
    print(f"::error::{msg}"); sys.exit(1)

API = "https://graph.instagram.com"
BASE_URL = "https://raw.githubusercontent.com/langflo163/FML-Racekalender/main/"  # sofort nach Push verfügbar

def call(method, path, **params):
    params["access_token"] = os.environ["IG_TOKEN"]
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    if method == "GET":
        req = urllib.request.Request(url + "?" + data.decode())
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        body = body.replace(os.environ["IG_TOKEN"], "***")
        fail(f"API-Fehler {e.code} bei {path}: {body}")

def wait_public(url, tries=30):
    for _ in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                if r.status == 200: return
        except Exception:
            pass
        time.sleep(10)
    fail(f"Datei nicht öffentlich erreichbar: {url}")

def wait_ready(cid, tries=60):
    for _ in range(tries):
        st = call("GET", cid, fields="status_code").get("status_code")
        if st == "FINISHED": return
        if st in ("ERROR", "EXPIRED"): fail(f"Container {cid}: {st} " + json.dumps(call("GET", cid, fields="status")))
        time.sleep(10)
    fail(f"Container {cid} nicht fertig")

def main(folder):
    uid = os.environ.get("IG_USER_ID", "").strip()
    if not os.environ.get("IG_TOKEN") or not uid: fail("Secret IG_TOKEN oder IG_USER_ID fehlt")
    url_of = lambda p: BASE_URL + os.path.relpath(p).replace(os.sep, "/")
    cap_file = os.path.join(folder, "caption.txt")
    caption = open(cap_file, encoding="utf-8").read() if os.path.exists(cap_file) else ""
    reel, story = os.path.join(folder, "reel.mp4"), os.path.join(folder, "story.jpg")
    if os.path.exists(story):
        u = url_of(story); wait_public(u)
        cid = call("POST", f"{uid}/media", image_url=u, media_type="STORIES")["id"]
        wait_ready(cid)
        print("Story veröffentlicht, Media-ID:", call("POST", f"{uid}/media_publish", creation_id=cid).get("id")); return
    if os.path.exists(reel):
        u = url_of(reel); wait_public(u)
        cid = call("POST", f"{uid}/media", video_url=u, media_type="REELS", caption=caption, share_to_feed="true")["id"]
        wait_ready(cid)
        print("Reel veröffentlicht, Media-ID:", call("POST", f"{uid}/media_publish", creation_id=cid).get("id")); return
    imgs = sorted(glob.glob(os.path.join(folder, "*.jpg")), key=lambda p: int(os.path.basename(p)[:-4]))[:10]
    if not imgs: fail("Keine Bilder gefunden")
    urls = [url_of(p) for p in imgs]
    for u in urls: wait_public(u)

    if len(urls) == 1:
        cid = call("POST", f"{uid}/media", image_url=urls[0], caption=caption)["id"]
    else:
        kids = []
        for u in urls:
            kids.append(call("POST", f"{uid}/media", image_url=u, is_carousel_item="true")["id"])
        for k in kids: wait_ready(k)
        cid = call("POST", f"{uid}/media", media_type="CAROUSEL", children=",".join(kids), caption=caption)["id"]
    wait_ready(cid)
    res = call("POST", f"{uid}/media_publish", creation_id=cid)
    print("Veröffentlicht, Media-ID:", res.get("id"))

if __name__ == "__main__":
    main(sys.argv[1])
