"""AI geometry census. --before saves the baseline; default verifies it."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'tools' / '_green' / 'before.json'

def walk(r):
    if isinstance(r, dict):
        yield r
        for c in r.get('ch', []):
            yield from walk(c)

def census():
    result = {}
    for p in sorted((ROOT / 'src/data').glob('*.json')):
        records = list(walk(json.loads(p.read_text(encoding='utf8'))))
        ac = [r for r in records if r.get('n', '').startswith('AI connector / ')]
        an = [r for r in records if r.get('cn') == 'Illo / AI node']
        nc = [r for r in records if r.get('n', '').startswith('Connector')]
        nn = [r for r in records if r.get('cn') == 'Illo / Node']
        if p.stem.startswith('_'):
            continue
        result[p.stem] = [len(ac), sorted(set(r['sw'] for r in ac)), sorted(set(tuple(r['da']) for r in ac)), len(an), sorted(set((r['w'], r['h']) for r in an)), len(nc), len(nn)]
    return result

def table(rows):
    return '\n'.join(['|Slide|AI lines|Widths|Dashes|AI dots|Sizes|Neutral lines|Rings|', '|---|---:|---|---|---:|---|---:|---:|'] + ['|'+'|'.join(str(v) for v in [k]+r)+'|' for k,r in rows.items()])

if __name__ == '__main__':
    rows = census()
    if '--before' in sys.argv:
        BASE.parent.mkdir(exist_ok=True)
        BASE.write_text(json.dumps(rows), encoding='utf8')
        for key in ('s09', 's11'):
            (BASE.parent / (key+'.before.json')).write_bytes((ROOT/'src/data'/ (key+'.json')).read_bytes())
    else:
        before = json.loads(BASE.read_text())
        for k,r in rows.items():
            assert not r[0] or (r[1] == [2] and r[2] == [(6,6)]), (k,r)
            assert not r[3] or r[4] == [(8,8)], (k,r)
            if k != 's10':
                assert r[5:] == before[k][5:], (k,r)
            if k in ['s12','s13','s14','s15','s16','s19','s20','s21']:
                assert r[3] <= r[0] + max(0,before[k][3]-2*before[k][0]), (k,r)
        for key in ('s09','s11'):
            assert (BASE.parent/(key+'.before.json')).read_bytes() == (ROOT/'src/data'/(key+'.json')).read_bytes(), key
        print('PASS: AI geometry, node counts, neutral counts, byte-identical s09/s11')
    print(table(rows))
