"""The large desktop monitor of the app slides (s18-s21) and the three card slots around it.

Every number is the owner's Figma frame "example space gains" (artboard 1440 x 900, slide s20), measured 2026-11-18.
These slides use ARTBOARD coordinates: build_site gives their slot the origin (0,0) (class `desk`, deck.css), so a record's x,y is
the same number as in Figma. Slides 14-16 keep `desktop()` in gen_s14.py (640 x 440) and are not touched by this module.

The screen holds a <video> (render.py, key "film") and, under it, the old 624 x 384 screen content scaled to fit, which is what shows
when a slide has no film or the film fails to load.
"""
from dsl import *

# monitor, artboard px: bezel, screen, stand neck, stand foot (the foot ends at y 817, on the footer rule at 816)
BEZ = (509.7, 215.5, 875.1, 547.3)
SCR = (519.1, 224.9, 855.1, 526.0)
NECK = (903.6, 762.7, 87.3, 43.6)
FOOT = (793.9, 806.4, 306.7, 10.6)
R_BEZ, R_SCR = 16.4, 10.9      # the old radii 12 and 8 scaled by 875.1 / 640
SX, SY = SCR[2] / 624, SCR[3] / 384   # old screen content (624 x 384) -> new screen

CARD_W = 256
# slot: (card x, card y, card height, attach point on the card, kind). A and B sit above the monitor, C at the lower left.
SLOTS = {
    "A": dict(x=285, y=111, h=83),   # leaves the right side at y 146, runs right to x 794, then down to the bezel top
    "B": dict(x=1096, y=72, h=83),   # straight down at x 1124 to the bezel top
    "C": dict(x=195, y=700, h=84),   # straight right at y 745 to the bezel's left edge
}
A_Y, A_TURN, B_DX, C_Y = 146, 794, 28, 745


def desktop_big(name, inner):
    """Illo / Device · Desktop (large): bezel, stand and a screen frame that holds the film and the static screen content."""
    bx, by, bw, bh = BEZ
    return at(0, {"x": bx, "y": by, "cn": "Illo / Device · Desktop", "t": "F", "w": bw, "h": FOOT[1] + FOOT[3] - by, "n": name,
            "ch": [{"x": NECK[0] - bx, "y": NECK[1] - by, "t": "R", "w": NECK[2], "h": NECK[3], "f": [{"c": "background/neutral/strong"}]},
                   {"x": FOOT[0] - bx, "y": FOOT[1] - by, "t": "R", "w": FOOT[2], "h": FOOT[3], "f": [{"c": "background/neutral/strong"}], "cr": 999},
                   {"x": 0, "y": 0, "t": "R", "w": bw, "h": bh, "f": [{"c": "background/inverse/bold"}], "cr": R_BEZ},
                   {"x": SCR[0] - bx, "y": SCR[1] - by, "t": "F", "w": SCR[2], "h": SCR[3], "n": "Screen", "film": 1,
                    "f": [{"c": "background/neutral/raised"}], "cr": R_SCR, "k": 1,
                    "ch": [{"x": 0, "y": 0, "t": "F", "w": 624, "h": 384, "n": "Static screen", "k": 1, "m": [round(SX, 5), 0, 0, round(SY, 5)], "ch": inner}]}]})


def ring(name, cx, cy):
    return node(name, cx - 8, cy - 8)       # dsl.node adds 3: a 10 px ring centred on (cx, cy)


def dot(name, cx, cy):
    return ai_node(name, cx - 8, cy - 8)    # dsl.ai_node adds 4: an 8 px dot centred on (cx, cy)


def card(slot, name, title, sub):
    s = SLOTS[slot]
    return ucard_h(name, s["x"], s["y"], s["h"], title, sub)


def ucard_h(name, x, y, h, title, sub):
    return {"x": x, "y": y, "cn": "Illo / UI card", "t": "F", "w": CARD_W, "h": h, "n": "UI card · " + name, "f": [{"c": "background/neutral/raised"}],
            "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 12, "lm": "V", "gap": 12, "pad": [16, 16, 16, 16],
            "ch": [{"t": "F", "sh": "L", "sv": "H", "lm": "H", "gap": 8, "ca": "c", "ch": [T(title, "heading/xs", "text/neutral/bold", sh="L")]},
                   T(sub, "body/sm", "text/neutral/subtlest", sh="L")]}


def _f(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")


def link(slot, name, ai=False, source="card"):
    """The connector of a card slot, from the card's edge to the monitor's edge, with its end marks. Returns the list of records.

    Neutral: grey 2 px dashed line and a 10 px ring at each end. AI: green 2 px dashed line and ONE 8 px dot, at the source end
    ("card" when Cortex writes to the screen, "device" when the screen shows what Cortex proposes). Every end sits on the edge it touches."""
    s = SLOTS[slot]
    bx, by = BEZ[0], BEZ[1]
    if slot == "A":
        p0, p1 = (s["x"] + CARD_W, A_Y), (A_TURN, by)        # card edge -> bezel top
        w, h = A_TURN - p0[0], by - A_Y
        d = "M 0 0 L %s 0 L %s %s" % (_f(w), _f(w), _f(h))
        dr = "M %s %s L %s 0 L 0 0" % (_f(w), _f(h), _f(w))
    elif slot == "B":
        p0, p1 = (s["x"] + B_DX, s["y"] + s["h"]), (s["x"] + B_DX, by)
        w, h = 0, by - p0[1]
        d, dr = "M 0 0 L 0 %s" % _f(h), "M 0 %s L 0 0" % _f(h)
    else:
        p0, p1 = (s["x"] + CARD_W, C_Y), (bx, C_Y)
        w, h = bx - p0[0], 0
        d, dr = "M 0 0 L %s 0" % _f(w), "M %s 0 L 0 0" % _f(w)
    src = p0 if source == "card" else p1
    path = d if source == "card" else dr
    if ai:
        return [ai_conn(name, p0[0] - 4, p0[1] - 4, w, h, path), dot(name, src[0], src[1])]
    return [conn(name, p0[0], p0[1], w, h, path), ring(name + " · card", *p0), ring(name + " · device", *p1)]


def callout(step, slot, title, sub, route, *, ai=False, source="card"):
    """Schedule a card and its connector from the source toward the destination."""
    from_device = source == "device"
    panel = at(step + int(from_device), card(slot, title, title, sub))
    line, start, *end = link(slot, route, ai=ai, source=source if ai else "card")
    if from_device and not ai:
        start, end = end[0], [start]
    draw(step, line, start, *end, target=panel if from_device else None, reverse=from_device and not ai)
    return [panel, line, start, *end]
