"""Decode the pre-show sound from slideshow/preshow/audio/c.js (base64 mp3: the loop bed and the transition effect) into two plain
mp3 files in src/audio/. Bytes are copied, not re-encoded. Reads the pre-show folder, never writes into it.

    python -P tools/extract_audio.py
"""
import base64
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
SRC_JS = os.path.join(SITE, "..", "slideshow", "preshow", "audio", "c.js")
OUT = os.path.join(SITE, "src", "audio")

with open(SRC_JS, "r", encoding="utf-8") as f:
    js = f.read()
m = re.search(r'window\.PRESHOW_AUDIO=\{bed:"([A-Za-z0-9+/=]+)",bedW:([0-9.]+),bedX:([0-9.]+),sfx:"([A-Za-z0-9+/=]+)",sfxGain:([0-9.]+)', js)
assert m, "c.js layout changed"
bed, sfx = base64.b64decode(m.group(1)), base64.b64decode(m.group(4))
os.makedirs(OUT, exist_ok=True)
for name in os.listdir(OUT):
    os.remove(os.path.join(OUT, name))
for name, data in (("bed.mp3", bed), ("sfx.mp3", sfx)):
    with open(os.path.join(OUT, name), "wb") as f:
        f.write(data)
with open(os.path.join(SITE, "src", "audio.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(["bed.mp3", "sfx.mp3"], f)
print("bed %d bytes (loop %.1f s + %.1f s crossfade), sfx %d bytes, gain %s" % (len(bed), float(m.group(2)), float(m.group(3)), len(sfx), m.group(5)))
