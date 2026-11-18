"""Checks the screen film of one slide (the slide must have an entry in src/films.json; build with it first).

usage: python -P tools/check_film.py <port> [slide key, default s20] [--stills <folder>]

 1. the <video> box equals the screen box (within 1 px), at 1440 x 900 and at 1920 x 970
 2. preload: none until the slide is current or next
 3. it does not play during the slide transition or monitor entrance, then currentTime passes 1
 4. it pauses when the slide is left and restarts from 0 when the slide is entered again
 5. reduced motion: only the poster (never loads the film, never plays)
 6. the film request aborted: the screen gets film-failed and the static screen shows (same box, visible)
 7. when no French film is configured, French keeps playing the English film
 8. a non-looping film ends and holds its last frame
With --stills the playing slide is saved as <key>-film-1440.png and <key>-film-1920.png.
"""
import os
import sys

from playwright.sync_api import sync_playwright

PORT = sys.argv[1]
KEY = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "s20"
STILLS = sys.argv[sys.argv.index("--stills") + 1] if "--stills" in sys.argv else None
BASE = "http://localhost:%s/" % PORT
res = []


def ok(name, detail, cond):
    res.append((name, detail, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name, detail)


def vid(pg, key):
    return pg.evaluate("""k => { const v = document.querySelector('.slide[data-key=' + k + '] video.film'); if (!v) return null;
        return {paused: v.paused, t: v.currentTime, preload: v.preload, rs: v.readyState, ns: v.networkState, poster: v.getAttribute('poster'),
                cls: v.parentNode.className, shown: getComputedStyle(v).display !== 'none'}; }""", key)


def box(pg, sel):
    return pg.evaluate("""s => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect();
        return {x: r.x, y: r.y, w: r.width, h: r.height, vis: getComputedStyle(e).visibility}; }""", sel)


def near(a, b, tol=1.0):
    return a and b and all(abs(a[k] - b[k]) <= tol for k in ("x", "y", "w", "h"))


def neighbours(pg):
    return pg.evaluate("""k => { const s = Array.from(document.querySelectorAll('.slide')).map(x => x.getAttribute('data-key')); const i = s.indexOf(k);
        return [s[i - 1], s[i + 1]]; }""", KEY)


def check_last_frame(pg, selector, language):
    video = pg.locator(selector)
    if video.evaluate("v => v.loop"):
        return
    video.evaluate("v => v.playbackRate = 16")
    pg.wait_for_function("selector => document.querySelector(selector).ended", arg=selector, timeout=15000)
    end = video.evaluate("v => ({time: v.currentTime, duration: v.duration})")
    pg.wait_for_timeout(350)
    held = vid(pg, KEY)
    ok(f"non-looping {language} film holds the last frame", held["t"],
       held["paused"] and held["t"] == end["time"] and held["t"] >= end["duration"] - 0.1)
    video.evaluate("v => v.playbackRate = 1")


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    SCR = ".slide[data-key=%s] [data-name=Screen]" % KEY
    VID = ".slide[data-key=%s] video.film" % KEY

    # 1 + 2 + 3 + 4 at 1440 x 900
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "?nopreshow=1#" + KEY)
    pg.wait_for_function("window.BNG_DECK && window.BNG_DECK.index >= 0")
    prev, nxt = neighbours(pg)
    if vid(pg, KEY) is None:
        print("FAIL no <video> on slide %s: put an entry in src/films.json and rebuild" % KEY)
        sys.exit(1)
    # a slide two before: preload none
    two_before = pg.evaluate("k => { const s = Array.from(document.querySelectorAll('.slide')).map(x => x.getAttribute('data-key')); return s[s.indexOf(k) - 2]; }", KEY)
    pg.goto(BASE + "?nopreshow=1#" + two_before)
    pg.reload()
    pg.wait_for_function("window.BNG_DECK && window.BNG_DECK.index >= 0")
    pg.wait_for_function("!document.querySelector('.slide:not([hidden])[data-sequence=playing]')")
    v = vid(pg, KEY)
    ok("preload is none two slides before", v["preload"], v["preload"] == "none" and v["paused"])
    pg.keyboard.press("ArrowRight")           # now the slide before: the film's slide is NEXT
    pg.wait_for_function("k => document.body.dataset.slide === k && document.querySelector('[data-key=' + k + ']').dataset.sequence !== 'playing'", arg=prev)
    v = vid(pg, KEY)
    ok("preload auto when the slide is next, not playing", "preload=%s paused=%s" % (v["preload"], v["paused"]), v["preload"] == "auto" and v["paused"])
    pg.locator(VID).evaluate("""v => {
        v.addEventListener('play', () => {
            const monitor = v.closest('[data-c="Illo / Device · Desktop"]');
            window.firstFilmPlay = {opacity: +getComputedStyle(monitor).opacity, slide: document.body.dataset.slide};
        }, {once: true});
    }""")
    pg.keyboard.press("ArrowRight")           # enter the film's slide
    pg.wait_for_timeout(450)
    v = vid(pg, KEY)
    ok("not playing during the slide transition (0.45 s in)", "paused=%s" % v["paused"], v["paused"])
    pg.wait_for_function("window.firstFilmPlay", timeout=12000)
    first_play = pg.evaluate("window.firstFilmPlay")
    ok("starts once the monitor is visible", first_play, first_play == {"opacity": 1, "slide": KEY})
    pg.wait_for_function("k => { const v = document.querySelector('.slide[data-key=' + k + '] video.film'); return v && !v.paused && v.currentTime > 1; }", arg=KEY, timeout=12000)
    v = vid(pg, KEY)
    t_play = v["t"]
    ok("plays after the transition and currentTime > 1", "t=%.2f" % t_play, not v["paused"] and t_play > 1)
    pg.wait_for_timeout(300)
    bs, bv = box(pg, SCR), box(pg, VID)
    ok("1440: video box equals screen box (<=1 px)", "screen=%s video=%s" % ({k: round(x, 1) for k, x in bs.items() if k != "vis"}, {k: round(x, 1) for k, x in bv.items() if k != "vis"}), near(bs, bv))
    fallback = pg.locator(VID).evaluate("""v => {
        if (JSON.parse(v.dataset.film).fr) return null;
        const source = v.currentSrc, time = v.currentTime;
        BNG_DECK.setLang('fr');
        const kept = document.documentElement.lang === 'fr' && v.currentSrc === source &&
            v.currentTime >= time && !v.paused;
        BNG_DECK.setLang('en');
        return {kept, source};
    }""")
    if fallback is not None:
        ok("French keeps the English film when no French set is mapped", fallback["source"], fallback["kept"])
    else:
        sets = pg.locator(VID).evaluate("v => JSON.parse(v.dataset.film)")
        for language in ("fr", "en"):
            pg.evaluate("language => BNG_DECK.setLang(language)", language)
            pg.wait_for_function("""([selector, media]) => {
                const v = document.querySelector(selector);
                return v.currentTime > 0.1 && !v.paused && v.poster.endsWith(media.poster) &&
                    [media.mp4, media.webm].filter(Boolean).some(path => v.currentSrc.endsWith(path));
            }""", arg=[VID, sets[language]], timeout=12000)
            if language == "fr":
                check_last_frame(pg, VID, "French")
        ok("French selects the French set and English switches back", sets["fr"], True)
    if STILLS:
        os.makedirs(STILLS, exist_ok=True)
        pg.screenshot(path=os.path.join(STILLS, "%s-film-1440.png" % KEY))
    pg.keyboard.press("ArrowRight")           # complete the remaining card reveals
    if pg.locator("body").get_attribute("data-slide") == KEY:
        pg.keyboard.press("ArrowRight")       # leave
    pg.wait_for_timeout(250)
    v = vid(pg, KEY)
    ok("pauses when the slide is left", "paused=%s t=%.2f" % (v["paused"], v["t"]), v["paused"])
    pg.keyboard.press("ArrowLeft")            # come back
    pg.wait_for_timeout(1500)
    v = vid(pg, KEY)
    ok("restarts from 0 on re-entry and plays", "t=%.2f (was %.2f) paused=%s" % (v["t"], t_play, v["paused"]), not v["paused"] and v["t"] < min(1.0, t_play))
    check_last_frame(pg, VID, "English")
    ok("no page errors", errs, not errs)
    ctx.close()

    # 1 again at 1920 x 970
    ctx = b.new_context(viewport={"width": 1920, "height": 970})
    pg = ctx.new_page()
    pg.goto(BASE + "?nopreshow=1#" + KEY)
    pg.wait_for_function("window.BNG_DECK && window.BNG_DECK.index >= 0")
    pg.wait_for_function("k => { const v = document.querySelector('.slide[data-key=' + k + '] video.film'); return v && !v.paused && v.currentTime > 1; }", arg=KEY, timeout=12000)
    bs, bv = box(pg, SCR), box(pg, VID)
    ok("1920: video box equals screen box (<=1 px)", "screen=%s video=%s" % ({k: round(x, 1) for k, x in bs.items() if k != "vis"}, {k: round(x, 1) for k, x in bv.items() if k != "vis"}), near(bs, bv))
    if STILLS:
        pg.screenshot(path=os.path.join(STILLS, "%s-film-1920.png" % KEY))
    ctx.close()

    # 5 reduced motion: poster only
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    pg = ctx.new_page()
    reqs = []
    pg.on("response", lambda r: reqs.append((r.url, r.status)))
    pg.goto(BASE + "?nopreshow=1#" + KEY)
    pg.wait_for_function("window.BNG_DECK && window.BNG_DECK.index >= 0")
    pg.wait_for_timeout(3000)
    v = vid(pg, KEY)
    poster_ok = any(u.endswith(v["poster"]) and s == 200 for u, s in reqs)
    media = [u for u, s in reqs if u.split("?")[0].endswith((".mp4", ".webm"))]
    ok("reduced motion: paused at 0, preload none, no film request", "paused=%s t=%.2f preload=%s film requests=%s" % (v["paused"], v["t"], v["preload"], media),
       v["paused"] and v["t"] == 0 and v["preload"] == "none" and not media)
    ok("reduced motion: the poster is requested and served", v["poster"], poster_ok)
    ctx.close()

    # 6 film request aborted: static screen shows
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    ctx.route("**/*.mp4", lambda r: r.abort())
    ctx.route("**/*.webm", lambda r: r.abort())
    pg = ctx.new_page()
    pg.goto(BASE + "?nopreshow=1#" + KEY)
    pg.wait_for_function("window.BNG_DECK && window.BNG_DECK.index >= 0")
    pg.wait_for_timeout(3000)
    v = vid(pg, KEY)
    st, sc = box(pg, ".slide[data-key=%s] [data-name='Static screen']" % KEY), box(pg, SCR)
    ok("aborted request: screen is marked film-failed and the video is hidden", "class=%s video shown=%s" % (v["cls"], v["shown"]), "film-failed" in v["cls"] and not v["shown"])
    ok("aborted request: the static screen fills the screen and is visible", "static=%s screen=%s" % ({k: round(x, 1) for k, x in st.items() if k != "vis"}, {k: round(x, 1) for k, x in sc.items() if k != "vis"}),
       near(st, sc, 1.5) and st["vis"] == "visible")
    if STILLS:
        pg.screenshot(path=os.path.join(STILLS, "%s-film-failed-1440.png" % KEY))
    ctx.close()
    b.close()

fails = [r for r in res if not r[2]]
print("check_film: %d checks, failures: %d" % (len(res), len(fails)))
sys.exit(1 if fails else 0)
