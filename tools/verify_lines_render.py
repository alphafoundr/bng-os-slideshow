"""Isolate renderer compatibility from the intentional neutral record changes."""
import json,subprocess,sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tools/_lines'
paths={p.name:p.read_bytes() for p in (ROOT/'src/data').glob('*.json')}
before=json.loads((OUT/'before.json').read_text(encoding='utf8'))
try:
    for name,data in before.items():
        (ROOT/'src/data'/name).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
    subprocess.run([sys.executable,'-P','build_site.py'],cwd=ROOT,check=True)
    def exclude(s): return re.sub(r'<section class="slide[^>]*data-key="s12".*?</section>','',s,flags=re.S)
    assert exclude((OUT/'before.html').read_text(encoding='utf8'))==exclude((ROOT/'public/index.html').read_text(encoding='utf8'))
    print('PASS: renderer index.html byte-identical with s12 excluded and neutral data held constant')
finally:
    for name,content in paths.items(): (ROOT/'src/data'/name).write_bytes(content)
    subprocess.run([sys.executable,'-P','build_site.py'],cwd=ROOT,check=True)
