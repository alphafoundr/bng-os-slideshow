"""Shared pieces of the free-standing 'Cortex at work' flow (slides 14, 15, 16), built without the desktop device.

The owner's words: keep the illustration with cards designed as they are on the desktop, but without the desktop, with more
images of leads and people, and the approval card with a person to verify it. Layout A (left to right) approved 2026-11-18.

Geometry (slot 900 x 728 artboard px, left edge of the slot at x = 504 + --ex; the illustration is centred on slot y = 348 so it spans
about page y 80 to 760 at 1440 x 900):
  * three columns: sources (x 0..140), the subject and 'what Cortex read' cards (col 2, x 196..556), the proposal, the approval and the
    result (col 3, right edge on the margin).
  * on a screen wider than 16:10 (--ex up to 480) the columns spread instead of leaving a band: each edge has a move factor, in units of
    --ex, to the left. FA sources 0.85, FB col-2 left edge 0.85, FC col-2 right edge 0.35, FD col-3 left edge 0.25 (its right edge stays on
    the margin). So col 2 grows by (FB - FC) x ex, col 3 by FD x ex, the gap col 2 -> col 3 by (FC - FD) x ex = 0.1 x ex, and the
    title-column gap by (1 - FA) x ex. A box carries exl (left move) and exw (width growth); a line carries exl (its left end) and exw
    (width growth), see render.py.
  * Cortex / AI lines: green 2 px dashed [6,6], ONE 8 px dot at the source end (ai_conn / ai_node), the dot sits just outside
    the source edge; the line ends exactly on the edge of the card it reaches.
  * other lines: neutral 2 px dashed, 10 px rings centred on the edges they join (conn / node).
Run via gen_s14.py, gen_s15.py, gen_s16_17.py (this file has no output of its own).
"""
from dsl import *

FA, FB, FC, FD = 0.85, 0.85, 0.35, 0.25
COL2 = (FB, round(FB - FC, 3))          # (exl, exw) of a col-2 card
COL3 = (FD, FD)                         # (exl, exw) of a col-3 card
C1 = [[0.68, 0, 0.16], [0, 0.68, 0.13]]
C2 = [[0.72, 0, 0.14], [0, 0.72, 0.265]]
# the site's portrait pool: six generated, labelled-fictional portraits (images.json): (hash, crop)
POOL = {"buyer": ("e9061fc2", CROP), "director": ("5755e103", CROP), "rep": ("2a9ca040", CROP), "backoffice": ("4cad20ba", CROP),
        "construction": ("dc262b77", C1), "partner": ("f0ed4c75", C2)}

# columns (artboard px, slot origin)
SRC_W, SRC_H = 140, 82          # one source: 56 px disc, 8 gap, label
X1 = 0
X2, W2 = 196, 360
X3, W3 = 612, 288
X3C, W3C = 580, 320              # the result card, right edge on the margin; 320 keeps 26 px free of the col-2 cards
GAP = 72                        # vertical space between stacked cards (room for a line, its dot and a pill)
CY = 348                        # the illustration is centred on this slot y (page y 420)
PAD = 20                        # card padding
PORTRAIT, PORTRAIT_BIG, PORTRAIT_SM = 56, 64, 48
ROW_PY = 18                     # vertical padding of a fact row in a read card


# ---------------------------------------------------------------- pieces moved out of gen_s14 (unchanged; fact has one added option)
def fact(name, x, y, label, value, src, py=6):
    return {"x": x, "y": y, "cn": "App / Data display / Fact row", "t": "F", "sv": "H", "w": 272, "n": "Fact · " + name,
            "sk": {"c": "border/neutral/subtle"}, "sw": [0, 0, 1, 0], "lm": "H", "gap": 12, "pad": [py, 12, py, 12], "ca": "c",
            "ch": [{"t": "F", "sh": "L", "sv": "H", "lm": "V", "ch": [T(label, "body/xs", "text/neutral/subtlest", nw=1),
                                                                   T(value, "label/md-strong", "text/neutral/bold", nw=1)]},
                   {"cn": "App / Data display / Source badge", "t": "F", "sh": "H", "sv": "H", "n": "Source", "f": [{"c": "background/neutral/subtle"}],
                    "cr": 4, "lm": "H", "gap": 4, "pad": [2, 6, 2, 6], "ca": "c",
                    "ch": [{"t": "E", "w": 6, "h": 6, "f": [{"c": "icon/neutral/subtle"}]}, T(src, "label/tag", "text/neutral/subtle", nw=1)]}]}


def button(name, x, y, text, primary):
    b = {"x": x, "y": y, "cn": "App / Actions / Button", "t": "F", "sh": "H", "h": 32, "n": "Button · " + name, "cr": 8, "lm": "H", "gap": 4,
         "pad": [0, 12, 0, 12], "pa": "c", "ca": "c"}
    if primary:
        b["f"] = [{"c": "background/action/bold"}]
        b["ch"] = [T(text, "label/md-strong", "text/on-action/bold", nw=1)]
    else:
        b.update({"f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1})
        b["ch"] = [T(text, "label/md", "text/neutral/bold", nw=1)]
    return b


def confirmation(name, x, y, w, title, sub):
    return {"x": x, "y": y, "cn": "App / Feedback / Confirmation", "t": "F", "sv": "H", "w": w, "n": "Confirmation · " + name,
            "f": [{"c": "background/neutral/subtle"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 8, "lm": "H", "gap": 8, "pad": [12, 12, 12, 12],
            "ch": [icon("circle-checkmark", 20, "icon/success/bold"),
                   {"t": "F", "sh": "L", "sv": "H", "k": 1, "lm": "V", "gap": 2,
                    "ch": [T(title, "label/md-strong", "text/neutral/bold", sh="L"), T(sub, "body/sm", "text/neutral/subtlest", sh="L")]}]}


def vconn(name, x, y, h, ai):
    f = ai_conn if ai else conn
    return f(name, x, y, 0, h, "M 0 0 L 0 %s" % h)


# ---------------------------------------------------------------- free-standing cards
def stretch(rec):
    """Make a record fill the width of its card (a fact row, the price box)."""
    rec.pop("w", None)
    rec["sh"] = "L"
    return rec


def mover(rec, mv):
    """mv: a move factor (exl) or a pair (exl, exw); 0 / None leaves the record fixed."""
    if isinstance(mv, (tuple, list)):
        mv, grow = mv
    else:
        grow = 0
    if mv:
        rec["exl"] = mv
    if grow:
        rec["exw"] = grow
    return rec


def card(name, x, y, w, h, ch, mv=0.0, gap=12, pad=PAD):
    """Illo / UI card, fixed height: raised fill, 1 px subtle hairline, radius 12."""
    return mover({"x": x, "y": y, "cn": "Illo / UI card", "t": "F", "w": w, "h": h, "n": "Card · " + name,
                  "f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 12, "lm": "V", "gap": gap,
                  "pad": [pad] * 4, "ch": ch}, mv)


def who(hkey, name, role, line=None, size=PORTRAIT):
    """A person row: portrait, name, role, optionally one more line."""
    h, crop = POOL[hkey]
    col = [T(name, "heading/xs", "text/neutral/bold", nw=1), T(role, "body/xs", "text/neutral/subtlest", nw=1)]
    if line:
        col.append(T(line, "body/xs", "text/neutral/subtlest", nw=1))
    return {"t": "F", "sh": "L", "sv": "H", "lm": "H", "gap": 14, "ca": "c",
            "ch": [portrait(h, "Portrait · " + name, size, crop=crop),
                   {"t": "F", "sh": "L", "sv": "H", "lm": "V", "gap": 2, "ch": col}]}


def head(title, sub):
    return {"t": "F", "sh": "L", "sv": "H", "lm": "V", "gap": 2,
            "ch": [T(title, "heading/sm", "text/neutral/bold", sh="L"), T(sub, "body/md", "text/neutral/subtlest", sh="L")]}


def subject_card(name, x, y, w, h, hkey, pname, prole, title, sub, mv=COL2):
    """The subject of the case: the person (lead, buyer) with the file's title under them."""
    c = card(name, x, y, w, h, [who(hkey, pname, prole, None, PORTRAIT_BIG), head(title, sub)], mv, gap=16)
    c["pa"] = "s"       # sized for the longer of the two languages: the spare height opens the gap between the person and the title
    return c


def read_card(name, x, y, w, h, title, facts, mv=COL2):
    """'What Cortex read / checked': the fact rows (source badges) in one card."""
    rows = {"t": "F", "sh": "L", "sv": "H", "lm": "V", "gap": 0, "ch": facts}
    return card(name, x, y, w, h, [T(title, "label/md-strong", "text/neutral/subtlest", nw=1), rows], mv, gap=16)


def suggestion_card(name, x, y, w, h, title, sub, person=None, mv=COL3):
    """App / Cortex / Suggestion card, fixed size, with the person Cortex proposes inside it (when the story has one)."""
    s = suggestion(name, x, y, title, sub)
    s["w"], s["h"] = w, h
    s["pad"] = [PAD + 4] * 4        # the suggestion's own padding is 16; the cards of the flow use 20, plus the 1 px hairline
    s["gap"] = 14
    s.pop("sv", None)
    if person:
        s["ch"].append(person)
    return mover(s, mv)


def approval_card(name, x, y, w, h, hkey, pname, role, line, mv=COL3):
    """One visible unit: the approver's portrait, name, role and one line, holding Decline / Approve and the note."""
    btn = {"t": "F", "sh": "L", "sv": "H", "lm": "H", "gap": 8, "pa": "x", "ca": "c",
           "ch": [button("Decline", 0, 0, "Decline", False), button("Approve", 0, 0, "Approve", True)]}
    return card(name, x, y, w, h, [who(hkey, pname, role, line, PORTRAIT_BIG), btn,
                                   T("Nothing is sent until you approve.", "body/xs", "text/neutral/subtlest", nw=1)], mv, gap=16)


def result_card(name, x, y, w, h, title, sub, mv=COL3):
    c = confirmation(name, x, y, w, title, sub)
    c["h"] = h
    c["pad"] = [16, 16, 16, 16]
    c["gap"] = 12
    c.pop("sv", None)
    return mover(c, mv)


def source(name, x, y, ic, label, mv=FA):
    td = tool(name, x, y, ic, label)
    td.pop("sh", None)
    td.pop("sv", None)
    td["w"], td["h"] = SRC_W, SRC_H
    return mover(td, mv)


# ---------------------------------------------------------------- lines
def link(name, p1, p2, kind, f1=0.0, f2=0.0, z=False):
    """A connector from p1 to p2 (exact points). kind 'ai': green, one 8 px dot centred on p1. kind 'plain': grey, rings on both ends.
    f1 / f2: the move factors (to the left, in units of --ex) of the two ends. Equal -> the whole line moves (exl); different -> the line
    is stretched: its left end moves by the left end's factor (exl) and its width grows by the difference (exw; the left end must
    move at least as far as the right end). z: a bend instead of a straight line: True / 'h' = horizontal-vertical-horizontal,
    'v' = vertical-horizontal-vertical, 'vh' = vertical then horizontal (an L)."""
    (x1, y1), (x2, y2) = p1, p2
    x0, y0 = min(x1, x2), min(y1, y2)
    w, h = abs(x2 - x1), abs(y2 - y1)
    sx, sy = x1 - x0, y1 - y0
    ex, ey = x2 - x0, y2 - y0
    if z and x1 != x2 and y1 != y2:
        mx, my = round(w / 2, 2), round(h / 2, 2)
        if z == "v":
            d = "M %s %s L %s %s L %s %s L %s %s" % (sx, sy, sx, my, ex, my, ex, ey)
        elif z == "vh":
            d = "M %s %s L %s %s L %s %s" % (sx, sy, sx, ey, ex, ey)
        else:
            d = "M %s %s L %s %s L %s %s L %s %s" % (sx, sy, mx, sy, mx, ey, ex, ey)
    else:
        assert x1 == x2 or y1 == y2, (name, p1, p2)
        d = "M %s %s L %s %s" % (sx, sy, ex, ey)
    if kind == "ai":
        line = ai_conn(name, x0 - 4, y0 - 4, w, h, d)
        extra = [mover(ai_node(name, x1 - 8, y1 - 8), f1)]
    else:
        line = conn(name, x0, y0, w, h, d)
        extra = [mover(node(name, x1 - 8, y1 - 8), f1), mover(node(name + " (end)", x2 - 8, y2 - 8), f2)]
    if f1 == f2:
        mover(line, f1)
    else:
        left_f, right_f = (f1, f2) if x1 < x2 else (f2, f1)
        assert left_f >= right_f > -1 and x1 != x2, (name, f1, f2)
        line["exl"] = left_f
        line["exw"] = round(left_f - right_f, 3)
    return [line] + extra


ANN_W = {"approves": 79.3, "after approval": 105.5}


def ann(name, cx, cy, text, f=0.0):
    """Annotation centred on a line (its canvas ring masks the line behind it)."""
    w = ANN_W[text]
    a = annotation(name, round(cx - w / 2, 2), round(cy - 13.65, 2), text)
    return mover(a, f)


# ---------------------------------------------------------------- layout A: columns, left to right
class GeoA:
    """Coordinates of layout A. left: heights of the stacked col-2 cards; recv: index of the card the sources feed and that proposes;
    right: heights (suggestion, approval, result). Both stacks are centred on slot y CY unless a top is given."""

    def __init__(self, left, recv, right, n_src, left_top=None, right_top=None, src_dy=None, pitch=None, x2=X2, w2=W2):
        self.left, self.recv, self.right, self.n_src = left, recv, right, n_src
        self.x2, self.w2 = x2, w2
        span_l = sum(left) + GAP * (len(left) - 1)
        span_r = sum(right) + 2 * GAP
        self.right_top = right_top if right_top is not None else (2 * CY - span_r) // 2
        self.left_top = left_top if left_top is not None else (2 * CY - span_l) // 2
        self.yl, y = [], self.left_top
        for h in left:
            self.yl.append(y)
            y += h + GAP
        self.yr, y = [], self.right_top
        for h in right:
            self.yr.append(y)
            y += h + GAP
        # sources: discs spread over the receiving card, lines horizontal at the disc centres
        ry, rh = self.yl[recv], left[recv]
        self.pitch = pitch if pitch is not None else (112 if n_src > 3 else 128)
        span = (n_src - 1) * self.pitch
        top = ry + (rh - span) // 2 if src_dy is None else ry + src_dy
        self.ys = [top + i * self.pitch for i in range(n_src)]  # disc centre y of each source
        self.disc_x = X1 + SRC_W // 2 + 28                      # right edge of a disc

    def build_lines(self, names, src_labels, recv_y=None, send_y=None):
        """names: dict of the line names. Returns the connector, dot and annotation records."""
        out = []
        recv_card_x = self.x2
        for i, y in enumerate(self.ys):
            out += link("%s → %s" % (src_labels[i], names["recv"]), (self.disc_x + 4, y), (recv_card_x, y), "ai", FA, FB)
        cx = self.x2 + self.w2 // 2
        fcol2 = round((FB + FC) / 2, 3)             # the centre of a col-2 card moves by the mean of its two edges
        for i in range(len(self.left) - 1):
            out += link("%s → %s" % (names["chain"][i][0], names["chain"][i][1]), (cx, self.yl[i] + self.left[i] + 4), (cx, self.yl[i + 1]), "ai", fcol2, fcol2)
        ry = self.yl[self.recv]
        y_from = ry + (recv_y if recv_y is not None else 44)
        sy = self.yr[0]
        y_to = sy + (send_y if send_y is not None else self.right[0] - 40)
        out += link("%s → %s" % (names["recv"], names["propose"]), (self.x2 + self.w2 + 4, y_from), (X3, y_to), "ai", FC, FD, z=True)
        cx3 = X3 + W3 // 2
        f3 = round(FD / 2, 3)                       # the centre of a col-3 card
        a_top, a_bot = self.yr[1], self.yr[1] + self.right[1]
        s_bot = self.yr[0] + self.right[0]
        out += link("%s → %s" % (names["propose"], names["approve"]), (cx3, s_bot), (cx3, a_top), "plain", f3, f3)
        out += link("%s → %s" % (names["approve"], names["result"]), (cx3, a_bot + 4), (cx3, self.yr[2]), "ai", f3, f3)
        out.append(ann("approves", cx3, (s_bot + a_top) // 2, "approves", f3))
        out.append(ann("after approval", cx3, (a_bot + self.yr[2]) // 2, "after approval", f3))
        return out
