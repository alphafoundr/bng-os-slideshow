"""Deck-wide behaviour checks: keys, pager, chapter nav, ?lang=fr, reduced motion, phone width, console errors, off-origin requests.

usage: python -P tools/check_deck.py <port>
"""
import sys


def main():
    from playwright.sync_api import sync_playwright
    port = sys.argv[1]
    base = "http://127.0.0.1:%s/" % port
    res = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)

        def new(vw, vh, reduce, mobile=False):
            ctx = b.new_context(viewport={"width": vw, "height": vh}, reduced_motion="reduce" if reduce else "no-preference", has_touch=mobile, is_mobile=mobile)
            pg = ctx.new_page()
            pg.errors, pg.off = [], []
            pg.on("console", lambda m: pg.errors.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: pg.errors.append(str(e)))
            pg.on("request", lambda r: pg.off.append(r.url) if not r.url.startswith(base) and not r.url.startswith("data:") and not r.url.startswith("blob:") else None)
            return ctx, pg

        # 1 keys, pager, hash, lang
        ctx, pg = new(1440, 900, False)
        pg.goto(base + "?nopreshow=1")
        pg.wait_for_function("window.BNG_DECK && window.BNG_DECK.index >= 0")
        i0 = pg.evaluate("BNG_DECK.index")
        pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(1300)
        i1 = pg.evaluate("BNG_DECK.index")
        # This check walks between slides. The sequence check exercises skipping a running entrance.
        pg.wait_for_function("document.querySelector('[data-key=s01]').dataset.sequence === 'complete'")
        pg.keyboard.press("Space"); pg.wait_for_timeout(1300)
        i2 = pg.evaluate("BNG_DECK.index")
        pg.keyboard.press("ArrowLeft"); pg.wait_for_timeout(1300)
        i3 = pg.evaluate("BNG_DECK.index")
        res.append(("keys ->,Space,<-", [i0, i1, i2, i3], i1 == i0 + 1 and i2 == i0 + 2 and i3 == i0 + 1))
        pg.locator(".slide:not([hidden]) .pager.next").click(); pg.wait_for_timeout(1300)
        i4 = pg.evaluate("BNG_DECK.index")
        pg.locator(".slide:not([hidden]) .pager.prev").click(); pg.wait_for_timeout(1300)
        i5 = pg.evaluate("BNG_DECK.index")
        res.append(("pager next/prev", [i3, i4, i5], i4 == i3 + 1 and i5 == i3))
        segs = pg.evaluate("document.querySelectorAll('.slide:not([hidden]) .seg').length")
        pg.locator(".slide:not([hidden]) .seg").nth(0).click(); pg.wait_for_timeout(1300)
        res.append(("chapter nav click jumps to first chapter", pg.evaluate("BNG_DECK.index"), pg.evaluate("BNG_DECK.index") <= 1 and segs > 0))
        n = pg.evaluate("Array.from(document.querySelectorAll('.slide')).length")
        pg2 = ctx.new_page()
        pg2.goto(base + "?nopreshow=1#s05"); pg2.wait_for_timeout(700)
        k5 = pg2.evaluate("document.querySelector('.slide:not([hidden])').getAttribute('data-key')")
        res.append(("hash #s05 opens slide 05", k5, k5 == "s05"))
        res.append(("slides in deck", n, n >= 26))
        res.append(("errors/off-origin (desktop)", (pg.errors, pg.off), not pg.errors and not pg.off))
        ctx.close()

        # 2 ?lang=fr and last-choice memory
        ctx, pg = new(1440, 900, False)
        pg.goto(base + "?nopreshow=1&lang=fr#s03")
        pg.wait_for_function("window.BNG_DECK && window.BNG_DECK.index >= 0")
        res.append(("?lang=fr html lang", pg.evaluate("document.documentElement.lang"), pg.evaluate("document.documentElement.lang") == "fr"))
        pg.locator(".ui [data-lang=en]").click(); pg.locator(".ui [data-lang=fr]").click()
        pg.goto(base + "?nopreshow=1#s03"); pg.wait_for_timeout(500)
        res.append(("last choice kept (fr)", pg.evaluate("document.documentElement.lang"), pg.evaluate("document.documentElement.lang") == "fr"))
        pg.goto(base + "?nopreshow=1&lang=en#s03"); pg.wait_for_timeout(500)
        res.append(("?lang=en wins", pg.evaluate("document.documentElement.lang"), pg.evaluate("document.documentElement.lang") == "en"))
        ctx.close()

        # 3 reduced motion
        ctx, pg = new(1440, 900, True)
        pg.goto(base + "?nopreshow=1#s14"); pg.wait_for_timeout(800)
        anims = pg.evaluate("document.getAnimations().length")
        tw = pg.evaluate("window.gsap ? gsap.globalTimeline.getChildren(true, true, false).filter(t => t.isActive && t.isActive()).length : -1")
        op = pg.evaluate("Array.from(document.querySelectorAll('.slide:not([hidden]) *')).filter(e => getComputedStyle(e).opacity === '0').length")
        res.append(("reduced motion: running animations / active tweens / hidden elements", (anims, tw, op), anims == 0 and tw <= 0 and op == 0))
        ctx.close()

        # 4 phone width
        for vw, vh in ((390, 844), (844, 390)):
            ctx, pg = new(vw, vh, False, mobile=True)
            pg.goto(base + "?nopreshow=1#s14"); pg.wait_for_timeout(1300)
            r = pg.evaluate("(() => { const d = document.getElementById('deck').getBoundingClientRect(); return [Math.round(d.left), Math.round(d.top), Math.round(d.width), Math.round(d.height), document.documentElement.scrollWidth, window.innerWidth]; })()")
            ok = r[0] >= -1 and r[1] >= -1 and r[2] <= vw + 1 and r[3] <= vh + 1 and r[4] <= vw + 1
            res.append(("phone %dx%d deck rect+scrollWidth" % (vw, vh), r, ok))
            pg.touchscreen.tap(vw // 2, vh // 2)
            res.append(("phone errors", (pg.errors, pg.off), not pg.errors and not pg.off))
            ctx.close()
        b.close()
    bad = 0
    for name, val, ok in res:
        print(("PASS " if ok else "FAIL ") + name + "  " + str(val))
        bad += 0 if ok else 1
    print("failures:", bad)


main()
