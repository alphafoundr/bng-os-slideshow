"""Prove body preservation against HEAD and preserve generator newline conventions."""
import copy
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
for path in (root / 'src/data').glob('gen_*.py'):
    rel = path.relative_to(root).as_posix()
    old = subprocess.check_output(['git', 'show', f'HEAD:{rel}'], cwd=root)
    data = path.read_bytes().replace(b'\r\n', b'\n')
    if b'\r\n' in old:
        data = data.replace(b'\n', b'\r\n')
    path.write_bytes(data)
count = 0
expected = {
    'p1': (6, None), 's12': (6, 12), 's13': (6, 13),
    's14': (7, 14), 's15': (7, 15), 's16': (7, 16),
    's18': (8, 17), 's19': (8, 18), 's20': (8, 19), 's21': (8, 20),
}
for path in (root / 'src/data').glob('*.json'):
    rel = path.relative_to(root).as_posix()
    old = json.loads(subprocess.check_output(['git', 'show', f'HEAD:{rel}'], cwd=root))
    new = json.loads(path.read_text(encoding='utf-8'))
    adjusted = copy.deepcopy(new)
    if old != new:
        assert path.stem in expected, rel
        chapter, number = expected[path.stem]
        assert new['name'].split(' · ', 2)[0] == f'{chapter:02d}', rel
        assert new['nav'] == {**old['nav'], 'Chapter': str(chapter)}, rel
        assert new['props']['Number'] == (old['props']['Number'] if number is None else f'{number:02d} / 27'), rel
        assert old['name'].split(' · ', 2)[2] == new['name'].split(' · ', 2)[2]
        adjusted['name'] = old['name']
        adjusted['nav'] = old['nav']
        adjusted['props']['Number'] = old['props']['Number']
        count += 1
    assert adjusted == old, rel
assert count == len(expected), count
print(f'PASS: {count} changed JSON files; only counters, chapters and name prefixes differ from HEAD')
