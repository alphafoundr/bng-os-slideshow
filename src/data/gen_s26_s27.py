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
    image = {"x": x, "y": y, "t": "R", "w": w}
    if h is not None:
        image["h"] = h
    image.update({"n": "Photo · " + name, "f": [{"c": "background/neutral/subtle"}, {"im": im, "sm": mode, "tr": [[1, 0, 0], [0, 1, 0]]}],
                  "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 12, "k": 1})
    return image


# ---------------- 26 · Five stages, in this order ----------------
stages = [
    ("f845e811", "Contracts and collections", [
        "Contract requests, checked", "Contracts with e-signature", "Welcome email",
        "Instalment reminders that arrive", "Registered e-letters",
    ]),
    ("3650788b", "Leads and assignment", [
        "Leads arrive from Fame", "Assigned in BNG OS", "Adviser and back office in one tool",
        "No re-entry by hand",
    ]),
    ("38958e82", "Commissions and the 360° view", [
        "One true version of each client", "Commissions checked per sale", "Every sale in one view",
    ]),
    ("396b09ab", "Group finance", [
        "Cash per company", "Cash forecast", "Rent, commissions and advances between companies",
    ]),
    ("12ac5423", "Construction, after‑sales, client space", [
        "Monthly photo and video updates", "After-sales requests", "Client space through to the keys",
    ]),
]
stage_width, stage_gap = 206, 10
pitch = stage_width + stage_gap
track_width = pitch * len(stages) - stage_gap - 16
growth = 1 / len(stages)
stage_beats = 3
photos, labels, numbers = [], [], []
for i, (im, title, items) in enumerate(stages):
    name = f"Stage {i + 1}"
    x, step = pitch * i, stage_beats * i
    stretch = {"exl": -i * growth, "exw": growth}
    image = photo(name, x, 94, stage_width, None, im)  # CSS keeps the original ratio as the columns grow.
    image.update(stretch)
    photos.append(at(step, image))
    number = badge(name, x + stage_width / 2 - 12, 347, str(i + 1))
    number["exl"] = -(i + 0.5) * growth
    numbers.append(at(step + 0.5, number))
    heading = at(step + 1, T(title, "heading/md", "text/neutral/bold", sh="L", h=76))
    rows = [
        at(step + 1.5, {
            "n": f"{name} · Checklist item {j + 1}", "t": "F", "lm": "H", "gap": 6, "sh": "L",
            "ch": [icon("checkmark-20", 16, "icon/success/bold"), T(item, "body/lg", "text/neutral/subtle", sh="L")],
        }, motion="row", index=j)
        for j, item in enumerate(items)
    ]
    labels.append({"x": x, "y": 383, "t": "F", "w": stage_width, "lm": "V", "gap": 10, **stretch,
                   "ch": [heading, {"t": "F", "lm": "V", "gap": 4, "sh": "L", "ch": rows}]})

line = conn("Stage 1 → Stage 5", 8, 359, track_width, 0, f"M 0 0 L {track_width} 0")
line.update({"exl": 0, "exw": 1})
start = node("Stage 1 start", 0, 351)
end = node("Stage 5 end", track_width, 351)
end["exl"] = -1
draw(0, line, start, end, target=photos[-1], arrival=stage_beats * (len(stages) - 1),
     via=[(stage_beats * i, (pitch * i + stage_width / 2 - 8) / track_width, photos[i])
          for i in range(1, len(stages) - 1)])
chip = at(0, tag("Urgent request", 0, 60, "Your urgent request · we start here"))
ch = [*photos, {"t": "F", "n": "Roadmap details", "ch": [line, start, end, *labels, *numbers]}, chip]
s26 = slide("517:5998", "13 · Stages and start · Five stages, in this order", "26 / 27", "The plan", "Five stages,\nin this order.",
            "Each one is useful on its own\nand prepares the next.", "Illustrative images, generated", 13, ch)
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
s27 = slide("517:6133", "13 · Stages and start · Three things to begin", "27 / 27", "To begin", "Three things\nto begin.",
            "One access to open, one figure to agree. Then the first stage starts.", "Illustrative images, generated", 13, ch)
dump("s27", s27)
