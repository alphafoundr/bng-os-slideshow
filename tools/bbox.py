"""Print the bounding box of dark pixels in a region for figma-<key>.png and web-<key>.png: python -P tools/bbox.py key x0 y0 x1 y1"""
import os
import sys

import numpy as np
from PIL import Image

PROOF = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "proof")
key = sys.argv[1]
x0, y0, x1, y1 = map(int, sys.argv[2:6])
thr = int(sys.argv[6]) if len(sys.argv) > 6 else 120
for kind in ("figma", "web"):
    im = np.asarray(Image.open(os.path.join(PROOF, "%s-%s.png" % (kind, key))).convert("L"))[y0:y1, x0:x1]
    ys, xs = np.where(im < thr)
    if len(ys) == 0:
        print(kind, "nothing")
        continue
    rows = sorted(set(ys.tolist()))
    print(kind, "x %d-%d y %d-%d" % (xs.min() + x0, xs.max() + x0, ys.min() + y0, ys.max() + y0), "rows", len(rows))
