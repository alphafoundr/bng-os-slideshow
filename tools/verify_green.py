"""Run requested checks serially; always stop the local server."""
from pathlib import Path
import subprocess
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'tools/_green'
def run(args, log):
    r = subprocess.run([sys.executable,'-P']+args,cwd=ROOT,capture_output=True,text=True,encoding='utf8')
    (OUT/log).write_text(r.stdout+r.stderr,encoding='utf8')
    print(r.stdout[-2500:]+r.stderr[-1000:], flush=True)
    assert r.returncode==0, args

if '--shots' not in sys.argv:
    run(['tools/census_ai.py'],'census-after.txt')
    run(['build_site.py'],'build.txt')
server = ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT/'public')))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
    port = str(server.server_port)
    for script in (['shot_green'] if '--shots' in sys.argv else ['check_deck','check_reveal','shot_green']):
        run(['tools/'+script+'.py',port],script+'.txt')
finally:
    server.shutdown()
    server.server_close()
