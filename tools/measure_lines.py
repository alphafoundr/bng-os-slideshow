import subprocess,sys,time,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
s=subprocess.Popen([sys.executable,'-m','http.server','8793','--directory','public'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    time.sleep(1)
    with sync_playwright() as p:
        b=p.chromium.launch(channel='chrome',headless=True)
        page=b.new_page(viewport={'width':1920,'height':970})
        page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(('http://localhost:','data:','blob:')) else r.abort())
        for lang in ('en','fr'):
            page.goto(f'http://localhost:8793/?nopreshow=1&lang={lang}#s12');page.wait_for_timeout(2200)
            r=page.evaluate('''() => {let s=document.querySelector('[data-key="s12"]'),t=s.querySelector('.titlecol').getBoundingClientRect();let tools=[...s.querySelectorAll('[data-c="Illo / Tool disc"]')].map(e=>e.getBoundingClientRect());return {gap:Math.min(...tools.map(r=>r.left))-t.right,ex:getComputedStyle(document.querySelector('#deck')).getPropertyValue('--ex'),count:tools.length};}''')
            assert r['gap']>=40,r
            print(lang,r)
        b.close()
finally:s.terminate();s.wait()
