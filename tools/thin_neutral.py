"""Apply the fixed neutral geometry rule to records without generators."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def walk(r):
    yield r
    for c in r.get('ch', []):
        yield from walk(c)

def thin(data):
    lines = nodes = 0
    for r in walk(data):
        if r.get('n', '').startswith('Connector') and r.get('sk', {}).get('c', '').startswith('border/neutral/') and r.get('sw') == 4 and r.get('da') == [10, 10]:
            r.update(sw=2, da=[6, 6]); lines += 1
        if r.get('cn') == 'Illo / Node' and r.get('w') == r.get('h') == 16 and r.get('sw') == 2:
            r.update(x=r.get('x', 0)+3, y=r.get('y', 0)+3, w=10, h=10, sw=1.5); nodes += 1
    return lines, nodes

if __name__ == '__main__':
    expected = {'s01': (6, 9), 's02': (0, 0), 's03': (6, 3), 's05': (3, 4)}
    for key, counts in expected.items():
        p = ROOT/'src/data'/f'{key}.json'
        data = json.loads(p.read_text(encoding='utf8'))
        actual = thin(data)
        assert actual == counts or actual == (0, 0), (key, actual, counts)
        if actual != (0, 0):
            p.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf8')
        print(key, actual)
