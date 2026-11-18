"""Slides 26 (517:5998) and 27 (517:6133), the photo versions, from the Figma reads of 2026-11-17 (they replace 321:5386 and 321:5647, the icon versions, which are not ported).
Image hashes: f845e811 scene-signing, 3650788b scene-visit, 38958e82 scene-office, 396b09ab scene-aerial, 12ac5423 scene-handover, b5362d92 obj-keys (see ../images.json).
Run: cd src/data && PYTHONPATH=. python -P gen_s26_s27.py"""
from dsl import *


def badge(name, x, y, text):
    return {"x": x, "y": y, "cn": "Illo / Badge", "t": "F", "w": 24, "h": 24, "n": "Badge · " + name, "f": [{"c": "background/action/bold"}],
            "sk": {"c": "background/neutral/canvas"}, "sw": 2, "sa": "OUTSIDE", "cr": 999, "lm": "H", "pa": "c", "ca": "c",
            "ch": [T(text, "label/tag", "text/on-action/bold", nw=1)]}


def photo(name, x, y, w, h, im, mode="FILL"):
    """Rectangle with a subtle fill, the image on top (FILL = cover, FIT = contain), radius 12, 1 px inside hairline, no shadow."""
    return {"x": x, "y": y, "t": "R", "w": w, "h": h, "n": "Photo · " + name, "f": [{"c": "background/neutral/subtle"}, {"im": im, "sm": mode, "tr": [[1, 0, 0], [0, 1, 0]]}],
            "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 12, "k": 1}


# ---------------- 26 · Five stages, in this order ----------------
stages = [("Stage 1", "f845e811", "Contracts and\ncollections", "Urgent collections, verified client data"),
          ("Stage 2", "3650788b", "Leads and\nassignment", "Leads no longer depend on one tool"),
          ("Stage 3", "38958e82", "Commissions and\nthe 360° view", "Management sees every sale in one view"),
          ("Stage 4", "396b09ab", "Group finance", "Cash per company, consolidated"),
          ("Stage 5", "12ac5423", "Construction,\nafter-sales,\nclient space", "Follow-up through\nto the keys")]
ch = []
for i, (name, im, title, sub) in enumerate(stages):
    ch.append(photo(name, 182 * i, 190, 172, 200, im))
ch += [conn("Stage 1 → Stage 5", 8, 418, 884, 0, "M 0 0 L 884 0"), node("Stage 1 start", 0, 410), node("Stage 5 end", 884, 410)]
for i, (name, im, title, sub) in enumerate(stages):
    ch.append({"x": 182 * i - 2, "y": 442, **T(title, "heading/md", "text/neutral/bold", w=176, al="C")})
    ch.append({"x": 182 * i - 2, "y": 534, **T(sub, "body/md", "text/neutral/subtlest", w=176, al="C")})
ch.append(tag("We start here", 0, 156, "We start here"))
for i, (name, im, title, sub) in enumerate(stages):
    ch.append(badge(name, 182 * i + 74, 406, str(i + 1)))
s26 = slide("517:5998", "12 · Stages and start · Five stages, in this order", "26 / 27", "The plan", "Five stages,\nin this order.",
            "Each one is useful on its own and prepares the next.", "Illustrative images, generated", 12, ch)
dump("s26", s26)

# ---------------- 27 · Three things to begin ----------------
steps = [("Step 1", 102, "b5362d92", "FIT", "Read access to Fame", "Agreed, still to be opened", ("BNG · Fame", 819, 165)),
         ("Step 2", 290, "38958e82", "FILL", "One session with finance", "To agree a single overdue figure", ("Finance · us", 817, 353)),
         ("Step 3", 478, "f845e811", "FILL", "Contracts and collections", "The first stage starts", ("We start here", 809, 541))]
ch = [photo(n, 0, y, 220, 148, im, m) for (n, y, im, m, _, _, _) in reversed(steps)]
ch += [{"x": 248, "y": 270, "t": "R", "w": 652, "h": 1, "f": [{"c": "border/neutral/subtle"}]},
       {"x": 248, "y": 458, "t": "R", "w": 652, "h": 1, "f": [{"c": "border/neutral/subtle"}]}]
for (n, y, im, m, title, sub, (tt, tx, ty)) in steps:
    ch.append({"x": 248, "y": y + 41, **T(title, "heading/lg", "text/neutral/bold", nw=1)})
    ch.append({"x": 248, "y": y + 81, **T(sub, "body/lg", "text/neutral/subtlest", nw=1)})
    ch.append(tag(tt, tx, ty, tt))
for i, (n, y, *_r) in enumerate(steps, 1):
    ch.append(badge(n, 8, y + 8, str(i)))
s27 = slide("517:6133", "12 · Stages and start · Three things to begin", "27 / 27", "To begin", "Three things\nto begin.",
            "One access to open, one figure to agree. Then the first stage starts.", "Illustrative images, generated", 12, ch)
dump("s27", s27)
