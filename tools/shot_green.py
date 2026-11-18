"""Capture the nine affected slides from a running local build."""
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright

KEYS = ['s10','s12','s13','s14','s15','s16','s19','s20','s21']
OUT = Path(__file__).parent/'_green'
OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome', headless=True)
    page = b.new_page(viewport={'width':1440,'height':900})
    page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(('http://localhost:', 'data:', 'blob:')) else route.abort())
    for key in KEYS:
        page.goto('about:blank')
        page.goto('http://localhost:%s/?nopreshow=1#%s' % (sys.argv[1], key))
        page.wait_for_function("document.body.dataset.slide === '%s'" % key)
        page.wait_for_timeout(2200)
        page.screenshot(path=str(OUT/(key+'.png')))
    b.close()
print('PASS: nine 1440x900 green screenshots')
