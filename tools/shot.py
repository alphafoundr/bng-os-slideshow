"""Screenshot slides of the built page at 1440x900 and compare with the Figma export.

usage: python -P tools/shot.py web  <port> <lang> key [key ...]     -> proof/web-<key>[-fr].png
       python -P tools/shot.py diff <key> [<key> ...]                 -> proof/pair-<key>.png (figma | web | diff) + score
Figma exports are saved by hand as proof/figma-<key>.png (get_screenshot, 1440 wide).
"""
import os
import sys

import numpy as np
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
PROOF = os.path.join(os.path.dirname(HERE), "proof")
os.makedirs(PROOF, exist_ok=True)


def web(port, lang, keys, w=1440, h=900):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        ctx = b.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce", device_scale_factor=1)
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        reqs = []
        pg.on("request", lambda r: reqs.append(r.url))
        for k in keys:
            pg.goto("about:blank")
            pg.goto("http://127.0.0.1:%s/?lang=%s&nopreshow=1#%s" % (port, lang, k))
            pg.wait_for_function("window.BNG_DECK && window.BNG_DECK.index >= 0")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_function("Array.from(document.querySelectorAll('.slide:not([hidden]) img')).every(i => i.complete && i.naturalWidth > 0)")  # lazy photos
            pg.wait_for_timeout(250)
            name = "web-%s%s.png" % (k, "-fr" if lang == "fr" else "")
            pg.screenshot(path=os.path.join(PROOF, name))
            print("shot", name)
        off = [u for u in reqs if not u.startswith("http://127.0.0.1:%s" % port) and not u.startswith("data:")]
        print("errors:", errs, "| off-origin requests:", off)
        b.close()


def diff(keys):
    for k in keys:
        a = Image.open(os.path.join(PROOF, "figma-%s.png" % k)).convert("RGB")
        b = Image.open(os.path.join(PROOF, "web-%s.png" % k)).convert("RGB")
        if a.size != b.size:
            a = a.resize(b.size)
        d = ImageChops.difference(a, b)
        arr = np.asarray(d).astype(np.int16).max(axis=2)
        bad = (arr > 24)
        print("%s: %.3f%% pixels differ by >24 (mean %.2f)" % (k, bad.mean() * 100, arr.mean()))
        vis = Image.fromarray(np.where(bad, 0, 255).astype(np.uint8)).convert("RGB")
        sheet = Image.new("RGB", (a.width * 3 // 2, a.height // 2 * 2 // 1), (255, 255, 255))
        half = (a.width // 2, a.height // 2)
        sheet = Image.new("RGB", (half[0] * 3, half[1]), (255, 255, 255))
        sheet.paste(a.resize(half), (0, 0))
        sheet.paste(b.resize(half), (half[0], 0))
        sheet.paste(vis.resize(half), (half[0] * 2, 0))
        sheet.save(os.path.join(PROOF, "pair-%s.png" % k))


if __name__ == "__main__":
    if sys.argv[1] == "web":
        web(sys.argv[2], sys.argv[3], sys.argv[4:])
    else:
        diff(sys.argv[2:])
