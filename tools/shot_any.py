"""Screenshots of chosen slides. usage: python -P tools/shot_any.py <port> <out dir> <WxH> <lang> key [key ...]"""
import os
import sys

from playwright.sync_api import sync_playwright

port, out, size, lang, keys = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:]
w, h = (int(v) for v in size.split("x"))
os.makedirs(out, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    pg = b.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce").new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    for k in keys:
        pg.goto("about:blank")
        pg.goto("http://127.0.0.1:%s/?lang=%s&nopreshow=1#%s" % (port, lang, k))
        pg.wait_for_function("window.BNG_DECK && window.BNG_DECK.index >= 0")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(out, "%s-%s-%s.png" % (k, size, lang)))
    b.close()
print("errors:", errs)
