"""Run local checks and captures, always stopping the owned HTTP server."""
import subprocess,sys,json,time,re
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'tools/_lines'
port='8793'
server=subprocess.Popen([sys.executable,'-m','http.server',port,'--directory','public'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    time.sleep(1)
    logs=[]
    for tool in ('check_deck','check_reveal','check_preshow'):
        r=subprocess.run([sys.executable,'-P',f'tools/{tool}.py',port],cwd=ROOT,capture_output=True,text=True)
        logs.append(tool+' exit '+str(r.returncode)+'\n'+r.stdout+r.stderr)
        print(logs[-1],flush=True)
    (OUT/'checks.txt').write_text('\n'.join(logs),encoding='utf8')
    keys=[]
    for path in sorted((ROOT/'src/data').glob('*.json')):
        def walk(r):
            yield r
            for c in r.get('ch',[]): yield from walk(c)
        if any('connector' in r.get('n','').lower() for r in walk(json.loads(path.read_text(encoding='utf8')))): keys.append(path.stem)
    with sync_playwright() as p:
        b=p.chromium.launch(channel='chrome',headless=True)
        page=b.new_page(viewport={'width':1440,'height':900})
        page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(('http://localhost:','data:','blob:')) else r.abort())
        for key in keys+['s12-wide','s12-wide-fr']:
            wide='wide' in key
            page.set_viewport_size({'width':1920 if wide else 1440,'height':970 if wide else 900})
            page.goto('about:blank'); page.goto(f'http://localhost:{port}/?nopreshow=1'+('&lang=fr' if key.endswith('-fr') else '')+'#'+('s12' if wide else key))
            page.wait_for_timeout(2200)
            page.screenshot(path=str(OUT/(key+'.png')))
            if wide:
                print(key,page.evaluate('''() => { const s=document.querySelector('.slide.active') || document.querySelector('#s12'); return {ex:getComputedStyle(document.documentElement).getPropertyValue('--ex')}; }'''),flush=True)
        b.close()
    print('PASS: screenshots '+str(len(keys)+2),flush=True)
finally:
    server.terminate();server.wait()
    print('Server stopped',flush=True)
