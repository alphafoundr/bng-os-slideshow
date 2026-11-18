"""Neutral census, count preservation, AI regression and generator reproducibility."""
import json, sys, subprocess, os, re
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from thin_neutral import walk
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tools/_lines'
def census(data):
    rs=list(walk(data))
    nc=[r for r in rs if r.get('n','').startswith('Connector') and r.get('sk',{}).get('c','').startswith('border/neutral/')]
    nn=[r for r in rs if r.get('cn')=='Illo / Node']
    ai=[r for r in rs if r.get('n','').startswith('AI connector /') or r.get('cn')=='Illo / AI node']
    return nc,nn,ai
before=json.loads((OUT/'before.json').read_text(encoding='utf8'))
lines=[]
for name,old in sorted(before.items()):
    if not re.fullmatch(r'(s\d+|op|p1|p2)\.json',name): continue
    now=json.loads((ROOT/'src/data'/name).read_text(encoding='utf8'))
    a,b,ai=census(old); c,d,aj=census(now)
    assert (len(a),len(b),len(ai))==(len(c),len(d),len(aj)),name
    assert all(not(r.get('sw')==4 and r.get('da')==[10,10]) for r in c),name
    assert all(r['w']!=16 for r in d),name
    assert [(r.get('sw'),r.get('da'),r.get('w') if r.get('cn') else None,r.get('h') if r.get('cn') else None) for r in ai]==[(r.get('sw'),r.get('da'),r.get('w') if r.get('cn') else None,r.get('h') if r.get('cn') else None) for r in aj],name
    def summary(cs,ns):
        return str(dict(Counter((r['sw'],tuple(r.get('da',[]))) for r in cs)))+' / '+str(dict(Counter((r['w'],r['sw']) for r in ns)))
    lines.append(name+': '+summary(a,b)+' -> '+summary(c,d))
print('\n'.join(lines))
(OUT/'census.txt').write_text('\n'.join(lines),encoding='utf8')
def snapshot(): return {p.name:p.read_bytes() for p in (ROOT/'src/data').glob('*.json')}
for i in range(2):
    snap=snapshot()
    env=dict(os.environ,PYTHONPATH=str(ROOT/'src/data')+os.pathsep+str(ROOT))
    for p in sorted((ROOT/'src/data').glob('gen_*.py')):
        subprocess.run([sys.executable,'-P',str(p)],cwd=ROOT,env=env,check=True,stdout=subprocess.DEVNULL)
    assert snapshot()==snap, 'generator drift'
print('PASS: counts preserved; AI unchanged; neutral rules; two generator reruns byte-identical')
