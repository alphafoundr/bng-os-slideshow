"""The reveal between slides 09 and 10. Usage: python -P tools/check_reveal.py <port>"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path(__file__).parent / '_reveal'
out.mkdir(exist_ok=True)
base = 'http://localhost:%s/' % sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome', headless=True)
    for w, h, lang in [(1440, 900, 'en'), (1920, 970, 'fr')]:
        pg = b.new_context(viewport={'width': w, 'height': h}).new_page()
        errors, off = [], []
        pg.on('pageerror', lambda e: errors.append(str(e)))
        pg.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        pg.on('request', lambda r: off.append(r.url) if not r.url.startswith((base, 'data:', 'blob:')) else None)
        pg.goto(base + '?nopreshow=1&lang=%s#s09' % lang)
        pg.wait_for_function('window.BNG_DECK && BNG_DECK.index>=0 && window.BNG_REVEAL')
        keys = pg.evaluate("[...document.querySelectorAll('.slide')].map(s=>s.dataset.key)")
        i = keys.index('rv')
        assert keys[i - 1] == 's09' and keys[i + 1] == 's10', keys
        # forward: it plays, and stills are taken along the way
        pg.keyboard.press('ArrowRight')
        pg.wait_for_function("document.body.dataset.slide==='rv' && BNG_REVEAL.state.mode==='play'")
        for stop in [1.2, 3.0, 4.0, 4.9]:
            pg.wait_for_function('BNG_REVEAL.state.t>=%s' % stop)
            pg.screenshot(path=str(out / f'{w}-t{int(stop*10):02d}.png'))
        pg.wait_for_function("BNG_REVEAL.state.mode==='rest'", timeout=15000)
        pg.screenshot(path=str(out / f'{w}-rest.png'))
        g = pg.evaluate("""(()=>{const r=e=>{const b=e.getBoundingClientRect();return [b.left,b.top,b.right,b.bottom]},d=r(document.getElementById('deck'));
          return {deck:d,wm:r(document.querySelector('.rv-wm')),line:r(document.querySelector('.rv-line')),text:document.querySelector('.rv-line').textContent,
                  core:getComputedStyle(document.querySelector('.rv-core')).fill,tools:[...document.querySelectorAll('.rv-tool')].map(e=>+e.getAttribute('opacity')),
                  nav:document.querySelectorAll('.slide:not([hidden]) .pager').length}})()""")
        mid = (g['deck'][0] + g['deck'][2]) / 2
        assert abs((g['wm'][0] + g['wm'][2]) / 2 - mid) < 2 and abs((g['line'][0] + g['line'][2]) / 2 - mid) < 2, g   # lockup and line centred on the artboard
        assert g['line'][0] > g['deck'][0] and g['line'][2] < g['deck'][2] and g['line'][1] > g['wm'][3], g
        assert g['core'] == 'rgb(16, 185, 129)' and max(g['tools']) == 0, g
        assert ('Un système' in g['text']) == (lang == 'fr'), g['text']
        # hand-over: the wordmark lands on slide 10's own wordmark
        pg.keyboard.press('ArrowRight')
        pg.wait_for_function("BNG_REVEAL.state.t2>=0.45")
        pg.screenshot(path=str(out / f'{w}-exit.png'))
        assert pg.evaluate("getComputedStyle(document.querySelector('[data-key=s10] .wm')).visibility") == 'hidden'   # one wordmark on screen while it travels
        pg.wait_for_function("BNG_REVEAL.state.t2>=BNG_REVEAL.T2 || document.querySelector('.kind-reveal').hidden")
        land = pg.evaluate("""(()=>{const s=document.querySelector('.kind-reveal'),h=s.hidden;s.hidden=false;BNG_REVEAL.render(BNG_REVEAL.T1,BNG_REVEAL.T2);
          const r=e=>{const b=e.getBoundingClientRect();return [b.left,b.top,b.right,b.bottom]},a=r(document.querySelector('.rv-wm')),b=r(document.querySelector('[data-key=s10] .wm svg'));s.hidden=h;return [a,b]})()""")
        assert all(abs(x - y) < 1.5 for x, y in zip(*land)), land
        pg.wait_for_timeout(1300)
        assert pg.evaluate("document.body.dataset.slide") == 's10' and pg.evaluate("document.querySelector('.kind-reveal').hidden")
        pg.screenshot(path=str(out / f'{w}-s10.png'))
        assert pg.evaluate("getComputedStyle(document.querySelector('[data-key=s10] .wm')).visibility") == 'visible'
        # back from slide 10: the finished lockup, no replay; back again: slide 09
        pg.keyboard.press('ArrowLeft'); pg.wait_for_timeout(1300)
        assert pg.evaluate("BNG_REVEAL.state.mode") == 'rest' and pg.evaluate("BNG_REVEAL.state.t") == pg.evaluate("BNG_REVEAL.T1")
        pg.keyboard.press('ArrowLeft'); pg.wait_for_timeout(1300)
        assert pg.evaluate("document.body.dataset.slide") == 's09'
        # a key during the reveal goes straight on
        pg.keyboard.press('ArrowRight'); pg.wait_for_function('BNG_REVEAL.state.t>1'); pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(1300)
        assert pg.evaluate("document.body.dataset.slide") == 's10'
        assert not errors and not off, (errors, off)
        pg.context.close()
    # reduced motion: the finished lockup at once
    ctx = b.new_context(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
    pg = ctx.new_page()
    pg.goto(base + '?nopreshow=1#rv')
    pg.wait_for_function("window.BNG_REVEAL && BNG_REVEAL.state.mode==='rest'")
    assert pg.evaluate("BNG_REVEAL.state.t") == pg.evaluate("BNG_REVEAL.T1")
    b.close()
print('PASS: order, play, centred lockup, green core, French line, hand-over onto slide 10 wordmark, back, skip, reduced motion')
