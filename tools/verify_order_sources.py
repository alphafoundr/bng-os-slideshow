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
for path in (root / 'src/data').glob('*.json'):
    rel = path.relative_to(root).as_posix()
    old = json.loads(subprocess.check_output(['git', 'show', f'HEAD:{rel}'], cwd=root))
    new = json.loads(path.read_text(encoding='utf-8'))
    adjusted = copy.deepcopy(new)
    if old != new:
        assert old['name'].split(' · ', 2)[2] == new['name'].split(' · ', 2)[2]
        adjusted['name'] = old['name']
        adjusted['nav'] = old['nav']
        adjusted['props']['Number'] = old['props']['Number']
        count += 1
    assert adjusted == old, rel
print(f'PASS: {count} changed JSON files; only counters, chapters and name prefixes differ from HEAD')
