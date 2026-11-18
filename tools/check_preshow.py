"""Global checks of the pre-show and the hand-over to the opener, in real Chrome.

usage: python -P tools/check_preshow.py <port> [lang]

Runs: pre-show loads and idles -> pointer scatter -> Space -> transition -> hand-over; compares the last pre-show frame with the
deck's opener (pixels), reports audio state before and after a gesture, M mute and its persistence over a reload, console errors
and requests that leave the origin. Writes proof/preshow-*.png.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
PROOF = os.path.join(os.path.dirname(HERE), "proof")
port = sys.argv[1]
lang = sys.argv[2] if len(sys.argv) > 2 else "en"
BASE = "http://127.0.0.1:%s/" % port


def main():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True, args=["--autoplay-policy=document-user-activation-required"])
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        pg = ctx.new_page()
        errs, reqs = [], []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("request", lambda r: reqs.append(r.url))

        pg.goto(BASE + "?lang=" + lang)
        pg.wait_for_function("window.__c2 && window.BNG_AUDIO")
        pg.wait_for_timeout(2500)
        print("idle: phase", pg.evaluate("__c2.phase()"), "| body", pg.evaluate("document.body.className"),
              "| audio before gesture:", pg.evaluate("BNG_AUDIO.state"), "playing", pg.evaluate("BNG_AUDIO.playing"))
        pg.screenshot(path=os.path.join(PROOF, "preshow-idle.png"))
        print("hint text:", pg.evaluate("document.getElementById('ps-hint-go').textContent"), "| hint opacity", pg.evaluate("getComputedStyle(document.getElementById('ps-hint-go')).opacity"))
        # pointer scatter
        for i in range(30):
            pg.mouse.move(300 + i * 20, 300 + i * 6)
        pg.wait_for_timeout(400)
        pg.mouse.click(720, 450)
        pg.wait_for_timeout(600)
        pg.wait_for_function("BNG_AUDIO.playing", timeout=8000)
        print("after first click: audio", pg.evaluate("BNG_AUDIO.state"), "playing", pg.evaluate("BNG_AUDIO.playing"), "muted", pg.evaluate("BNG_AUDIO.muted"))
        # Space starts the show
        pg.keyboard.press("Space")
        pg.wait_for_timeout(1700)
        pg.screenshot(path=os.path.join(PROOF, "preshow-mid.png"))
        pg.wait_for_function("document.body.classList.contains('deck-on')", timeout=8000)
        pg.wait_for_timeout(500)
        print("after transition: body", pg.evaluate("document.body.className"), "| preshow hidden", pg.evaluate("document.getElementById('preshow').hidden"),
              "| slide", pg.evaluate("document.body.getAttribute('data-slide')"), "| url", pg.url)
        pg.screenshot(path=os.path.join(PROOF, "preshow-handover.png"))
        # the same opener, straight from the deck
        pg2 = ctx.new_page()
        pg2.goto(BASE + "?lang=" + lang + "&nopreshow=1#op")
        pg2.wait_for_function("window.BNG_DECK && window.BNG_DECK.index >= 0")
        pg2.evaluate("document.fonts.ready")
        pg2.wait_for_timeout(600)
        pg2.screenshot(path=os.path.join(PROOF, "preshow-opener-deck.png"))
        a = Image.open(os.path.join(PROOF, "preshow-handover.png")).convert("RGB")
        c = Image.open(os.path.join(PROOF, "preshow-opener-deck.png")).convert("RGB")
        d = np.asarray(ImageChops.difference(a, c)).astype(np.int16).max(axis=2)
        ys, xs = np.nonzero(d > 24)
        print("hand-over vs deck opener: %.3f%% pixels differ by >24" % ((d > 24).mean() * 100), ("bbox x %d-%d y %d-%d" % (xs.min(), xs.max(), ys.min(), ys.max())) if len(xs) else "")
        # M mutes, survives a reload
        pg.keyboard.press("KeyM")
        pg.wait_for_timeout(200)
        print("M: muted", pg.evaluate("BNG_AUDIO.muted"), "| stored", pg.evaluate("localStorage.getItem('bng-os-muted')"), "| label", pg.evaluate("document.getElementById('snd').textContent"))
        pg.reload()
        pg.wait_for_function("window.BNG_AUDIO")
        print("after reload: muted", pg.evaluate("BNG_AUDIO.muted"))
        pg.keyboard.press("KeyM")
        pg.wait_for_timeout(200)
        print("M again: muted", pg.evaluate("BNG_AUDIO.muted"), "| stored", pg.evaluate("localStorage.getItem('bng-os-muted')"))
        # space after the hand-over moves the deck (use a fresh run so the opener is current)
        off = [u for u in reqs if not u.startswith(BASE.rstrip("/")) and not u.startswith("data:") and not u.startswith("blob:")]
        print("errors:", errs, "| off-origin requests:", off)
        b.close()


main()
