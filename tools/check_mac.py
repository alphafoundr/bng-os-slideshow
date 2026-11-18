"""Local GPU pilot acceptance checks. One Chrome process; no external services."""
import json
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright

out = Path(__file__).parent / '_mac'
out.mkdir(exist_ok=True)
base = 'http://localhost:%s/' % sys.argv[1]
results = {}
with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome', headless=True, args=['--use-angle=default','--enable-gpu','--ignore-gpu-blocklist'])
    ctx = b.new_context(viewport={'width':1440,'height':900})
    pg = ctx.new_page()
    requests, errors, off = [], [], []
    pg.on('request', lambda r: requests.append(r.url))
    pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    pg.on('request', lambda r: off.append(r.url) if not r.url.startswith((base, 'data:', 'blob:')) else None)
    pg.goto(base+'?nopreshow=1#s15')
    pg.wait_for_function('BNG_DECK.index>=0')
    assert not any('/mac/' in u for u in requests)
    assert pg.locator('.mac-canvas').count()==0
    results['flag_off_no_mac_requests']=True
    requests.clear()
    pg.goto(base+'?nopreshow=1&mac=1#op')
    pg.wait_for_function('window.BNG_MAC && window.BNG_DECK.index===0')
    assert not any('three.' in u or 'laptop.glb' in u or '.mp4' in u for u in requests)
    results['distant_no_heavy_load']=True
    for w,h in [(1440,900),(1920,970)]:
        pg.set_viewport_size({'width':w,'height':h})
        pg.goto('about:blank')
        pg.goto(base+'?nopreshow=1&mac=1#s14')
        pg.wait_for_function("['ready','fallback'].includes(window.BNG_MAC?.state.status)",timeout=30000)
        assert pg.evaluate('BNG_MAC.state.status')=='ready', pg.evaluate('BNG_MAC.state')
        pg.wait_for_function("document.body.dataset.slide==='s14'")
        pg.evaluate("BNG_DECK.show([...document.querySelectorAll('.slide')].findIndex(s=>s.dataset.key==='s15'),1)")
        pg.wait_for_function('BNG_MAC.state.active && BNG_MAC.state.open===0')
        pg.wait_for_timeout(180)
        pg.screenshot(path=str(out/f'{w}-closed.png'))
        pg.wait_for_function('BNG_MAC.state.open>.3 && BNG_MAC.state.open<.98')
        pg.screenshot(path=str(out/f'{w}-mid.png'))
        pg.wait_for_function('BNG_MAC.state.open===1')
        pg.wait_for_function("document.querySelector('video').currentTime>.4")
        pg.screenshot(path=str(out/f'{w}-open.png'))
        rect=pg.evaluate("""(()=>{const c=document.querySelector('.mac-canvas').getBoundingClientRect(),d=document.querySelector('[data-key=s15] [data-name="Device · Desktop · Contract file"]').getBoundingClientRect();return {canvas:[c.x,c.y,c.width,c.height],device:[d.x,d.y,d.width,d.height],scale:d.width/640}})()""")
        # the laptop is the whole illustration: centred between the title column and the right margin, inside the deck, clear of the title text
        box=pg.evaluate("""(()=>{const r=e=>e.getBoundingClientRect(),d=r(document.getElementById('deck')),t=r(document.querySelector('[data-key=s15] .tblock')),f=r(document.querySelector('[data-key=s15] .frule'));return {deck:[d.left,d.right,d.top],k:d.height/900,textRight:Math.max(...[...document.querySelectorAll('[data-key=s15] .tblock>*')].map(e=>{const g=document.createRange();g.selectNodeContents(e);return g.getBoundingClientRect().right})),rule:f.top}})()""")
        c=rect['canvas']; k=box['k']
        assert c[0]>=box['textRight'] and c[0]+c[2]<=box['deck'][1]-11*k, (c,box)
        # the sources and the two cards stay on the slide, in the title column: visible, left of the canvas, clear of the text and of each other
        g=pg.evaluate("""(()=>{const s=document.querySelector('[data-key=s15] .slot'),r=e=>{const b=e.getBoundingClientRect();return [b.left,b.top,b.right,b.bottom]};
          const kept=[...s.children].filter(e=>!e.classList.contains('mac-hide')&&!e.matches('.mac-canvas,video'));
          return {boxes:kept.map(r),visible:kept.every(e=>getComputedStyle(e).visibility==='visible'),text:r(document.querySelector('[data-key=s15] .tblock')),hidden:s.querySelectorAll(':scope>.mac-hide').length}})()""")
        # 16 hidden slot children after removing five panel-end AI nodes.
        assert len(g['boxes'])==6 and g['visible'] and g['hidden']>=16, g
        hit=lambda a,b: a[0]<b[2]-1 and b[0]<a[2]-1 and a[1]<b[3]-1 and b[1]<a[3]-1
        for i,a in enumerate(g['boxes']):
            assert a[2]<=c[0]+1 and a[0]>=box['deck'][0]+35*k and a[1]>=box['deck'][2]+56*k and a[3]<=box['rule'], (a,c,box)
            assert not hit(a,g['text']), (a,g['text'])
            assert not any(hit(a,o) for o in g['boxes'][i+1:]), (a,g['boxes'])
        assert c[1]>=box['deck'][2]+40*k and c[1]+c[3]<=box['rule']+40*k, (c,box)   # the canvas may pass the area by its own empty margin; the laptop is what is centred
        pg.wait_for_function('BNG_MAC.state.frames.playing.length>60')
        results[str(w)]={'rect':rect,'frames':pg.evaluate('BNG_MAC.state.frames'),'state':pg.evaluate('BNG_MAC.state')}
        assert pg.evaluate("getComputedStyle(document.querySelector('[data-key=s15] [data-name=\"Device · Desktop · Contract file\"]')).visibility")=='hidden'
        pg.evaluate('BNG_DECK.go(1)')
        pg.wait_for_function("document.querySelector('video').paused")
        pg.wait_for_function('BNG_MAC.state.open===0')
        pg.evaluate('BNG_DECK.go(1)')
        pg.wait_for_function('BNG_MAC.state.disposed')
        assert pg.locator('.mac-canvas').count()==0
        pg.evaluate("BNG_DECK.goKey('s15')")
        pg.wait_for_function('BNG_MAC.state.open===1 && !BNG_MAC.state.disposed')
        assert pg.evaluate("location.search.includes('mac=1')")
    assert any('laptop.glb' in u for u in requests)
    assert any('.mp4' in u for u in requests)
    pg.emulate_media(reduced_motion='reduce')
    pg.goto('about:blank')
    pg.goto(base+'?nopreshow=1&mac=1#s15')
    pg.wait_for_function('window.BNG_MAC?.state.open===1')
    assert pg.evaluate("document.querySelector('video').paused && document.querySelector('video').currentTime===0")
    results['reduced_motion']=True
    # A failed model fetch and a lost context both restore the original drawing.
    pg.route('**/laptop.glb', lambda r:r.abort())
    pg.reload()
    pg.wait_for_function("window.BNG_MAC?.state.status==='fallback'")
    assert pg.evaluate("getComputedStyle(document.querySelector('[data-key=s15] [data-name=\"Device · Desktop · Contract file\"]')).visibility")=='visible'
    pg.unroute('**/laptop.glb')
    # Network errors generated by this deliberate failure are expected.
    errors=[e for e in errors if 'net::ERR_FAILED' not in e]
    pg.reload()
    pg.wait_for_function('window.BNG_MAC?.state.open===1')
    pg.evaluate("document.querySelector('.mac-canvas').getContext('webgl2').getExtension('WEBGL_lose_context').loseContext()")
    pg.wait_for_function("BNG_MAC.state.status==='fallback'")
    assert pg.locator('.mac-canvas').count()==0
    results['fallbacks']=True
    results['errors']=errors
    results['off_origin']=off
    ctx.close()
    b.close()
assert not errors, errors
assert not off, off
for size in ['1440','1920']:
    for phase, intervals in results[size]['frames'].items():
        results[size][phase]={'average_ms':sum(intervals)/len(intervals),'worst_ms':max(intervals),'samples':len(intervals)}
(out/'results.json').write_text(json.dumps(results,indent=2),encoding='utf8')
print(json.dumps({k:{p:v[p] for p in ['opening','playing']} for k,v in results.items() if k in ['1440','1920']},indent=2))
print('PASS: flag, lifecycle, local requests, video, projection box, reduced motion, fallbacks')
