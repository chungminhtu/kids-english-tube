#!/usr/bin/env python3
"""Local server for index.html - optional, only useful at home.

    python3 kids_yt.py            # http://127.0.0.1:8777
    python3 kids_yt.py --lan      # also reachable from phone/iPad on the same wifi
    python3 kids_yt.py --selftest

index.html works on its own (GitHub Pages) by pulling YouTube's RSS through a
public CORS proxy. Run this instead and the page uses /feed here: no proxy, and a
6-hour on-disk cache, so it is faster and does not depend on a free proxy staying up.
Serves only index.html / channels.js, and only fetches URLs of the exact shape
https://www.youtube.com/feeds/videos.xml?channel_id=UC... - it is not an open proxy.
"""
import argparse
import json
import os
import re
import socket
import sys
import threading
import time
import urllib.request
import webbrowser
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 8777
FEED = "https://www.youtube.com/feeds/videos.xml?channel_id={}"
NS = {"a": "http://www.w3.org/2005/Atom", "m": "http://search.yahoo.com/mrss/",
      "yt": "http://www.youtube.com/xml/schemas/2015"}
TTL = 6 * 3600
PER_CHANNEL = 10
CACHE_FILE = os.path.expanduser("~/Library/Caches/kids_yt_feeds.json")
STATIC = {"/": ("index.html", "text/html; charset=utf-8"),
          "/index.html": ("index.html", "text/html; charset=utf-8"),
          "/channels.js": ("channels.js", "application/javascript; charset=utf-8")}

_cache = {}
_lock = threading.Lock()
_last_call = [0.0]   # YouTube's RSS host answers 404/500 when hit in bursts


def channels():
    """The curated list, read straight out of channels.js (single source of truth)."""
    src = open(os.path.join(HERE, "channels.js"), encoding="utf-8").read()
    start = src.index("=", src.index("window.CHANNELS")) + 1   # skip the comment header
    return json.loads(src[start:src.rindex(";")])


def _load_cache():
    try:
        with open(CACHE_FILE) as f:
            _cache.update(json.load(f))
    except (OSError, ValueError):
        pass


def _save_cache():
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(_cache, f)
    except OSError:
        pass


def latest(cid, n=PER_CHANNEL):
    """Newest n videos of a channel from YouTube's public RSS, cached TTL seconds."""
    hit = _cache.get(cid)
    if hit and time.time() - hit["t"] < TTL:
        return hit["v"][:n]
    req = urllib.request.Request(FEED.format(cid), headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(4):
        with _lock:                       # one outbound request at a time, spaced out
            gap = 0.35 - (time.time() - _last_call[0])
            if gap > 0:
                time.sleep(gap)
            _last_call[0] = time.time()
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                root = ET.fromstring(r.read())
            break
        except Exception:
            if attempt == 3:
                if hit:
                    return hit["v"][:n]   # stale beats empty
                raise
            time.sleep(1.0 * (attempt + 1))
    vids = []
    for e in root.findall("a:entry", NS):
        vid = e.findtext("yt:videoId", "", NS)
        vids.append({"id": vid, "title": e.findtext("a:title", "", NS),
                     "published": (e.findtext("a:published", "", NS) or "")[:10],
                     "thumb": "https://i.ytimg.com/vi/%s/hqdefault.jpg" % vid})
    _cache[cid] = {"t": time.time(), "v": vids}
    _save_cache()
    return vids[:n]


def prefetch():
    """Warm every channel in the background so scrolling is instant."""
    for cid in [c[1] for cs in channels().values() for c in cs]:
        try:
            latest(cid)
        except Exception:
            pass


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/feed":
            m = re.search(r"cid=(UC[\w-]{22})", self.path)   # only real channel ids
            if not m:
                return self._send(400, b'{"error":"bad channel id"}', "application/json")
            try:
                body = json.dumps({"videos": latest(m.group(1))})
            except Exception as e:
                body = json.dumps({"error": str(e)})
            return self._send(200, body.encode(), "application/json")
        if path in STATIC:
            name, ctype = STATIC[path]
            with open(os.path.join(HERE, name), "rb") as f:
                return self._send(200, f.read(), ctype)
        self._send(404, b"not found", "text/plain")

    def log_message(self, *a):
        pass


def lan_ip():
    """This machine's address on the local network (no packet is actually sent)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("192.0.2.1", 9))   # reserved TEST-NET-1, just to pick the route
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def selftest():
    cats = channels()
    ids = [c[1] for cs in cats.values() for c in cs]
    assert len(ids) == len(set(ids)), "duplicate channel"
    assert all(re.fullmatch(r"UC[\w-]{22}", i) for i in ids), "bad channel id"
    html = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
    assert "<details" not in html, "nothing may be collapsed"
    assert "PER_CHANNEL = %d" % PER_CHANNEL in html, "page and server disagree on video count"
    v = latest("UC-3SbfTPJsL8fJAPKiVqBLg")            # Deep Look
    assert len(v) == PER_CHANNEL, v
    assert all(len(x["id"]) == 11 and x["title"] for x in v), v
    print("selftest ok - %d topics, %d channels, newest: %s"
          % (len(cats), len(ids), v[0]["title"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--lan", action="store_true",
                    help="serve on the local network too (phone/iPad, same wifi)")
    a = ap.parse_args()
    _load_cache()
    if a.selftest:
        selftest()
        sys.exit(0)
    threading.Thread(target=prefetch, daemon=True).start()
    url = "http://127.0.0.1:%d" % a.port
    print("serving " + url + "  (ctrl-c to stop)")
    if a.lan:
        print("LAN:     http://%s:%d" % (lan_ip(), a.port))
    webbrowser.open(url)
    ThreadingHTTPServer(("0.0.0.0" if a.lan else "127.0.0.1", a.port), Handler).serve_forever()
