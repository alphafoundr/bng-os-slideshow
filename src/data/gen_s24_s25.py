"""Slides 24 (395:5162, final) and 25 (397:5247, version A, final) from the Figma reads of 2026-11-17.
Run: cd src/data && PYTHONPATH=. python -P gen_s24_s25.py"""
from dsl import *
from math import sqrt


def sign(prod):
    if prod == "Cortex":
        return {"t": "F", "w": 48, "h": 48, "n": "Sign", "ch": [marker(48, 0, 0)]}
    return {"cn": "Brand / Sign", "w": 48, "h": 48, "lg": 1, "vp": {"Product": prod, "Size": "48", "Ink": "Full colour"}}


def lockup(prod, w, label):
    """Brand / Product lockup, Size Deck: the 48 sign, 12 gap and the name in heading/xl."""
    return {"cn": "Brand / Product lockup", "t": "F", "w": w, "h": 48, "n": "Lockup · " + prod, "lm": "H", "gap": 12, "ca": "c",
            "ch": [sign(prod), T(label, "heading/xl", "text/neutral/bold", nw=1)]}


def tag_neutral(name, text, **kw):
    t = {"cn": "Illo / Tag", "t": "F", "sh": "H", "sv": "H", "n": "Tag · " + name, "f": [{"c": "background/neutral/tag"}], "cr": 4, "lm": "H",
         "pad": [2, 8, 2, 8], "pa": "c", "ca": "c", "ch": [T(text, "label/tag", "text/neutral/bold", nw=1)]}
    t.update(kw)
    return t


# ---------------- 24 · Three products, one system ----------------
def diagram_sign(product):
    if product != "Cortex":
        return {"cn": "Brand / Sign", "w": 24, "h": 24, "lg": 1,
                "vp": {"Product": product, "Size": "24", "Ink": "Full colour"}}
    sign24 = marker(48)
    glyph, dot = sign24["ch"]
    sign24.update(w=24, h=24)
    glyph.update(x=glyph["x"] / 2, m=[0.5, 0, 0, 0.5])
    for dimension in ("x", "y", "w", "h"):
        dot[dimension] /= 2
    return sign24


def diagram_label(product, label, role, copy, x, y, w, stretch, centered=False):
    return {"x": x, "y": y, "exl": stretch, "t": "F", "w": w, "n": label + " label",
            "lm": "V", "gap": 6, "ca": "c" if centered else "s",
            "ch": [{"t": "F", "lm": "H", "h": 32, "gap": 8, "ca": "c",
                    "ch": [diagram_sign(product), T(label, "heading/sm", "text/neutral/bold", nw=1),
                           tag_neutral(role, role)]},
                   T(copy, "body/md", "text/neutral/subtle", sh="L",
                     **({"al": "C", "nw": 1} if centered else {}))]}


# The OS sign's 48-unit proportions set the ring's weight, opening and core.
# The opening doubles as the path out of the core.
cx, cy, diameter = 417, 360, 320
radius = diameter / 2
# A diagram ring, not the sign at poster size: a 40 px stroke keeps it light. The core and the opening keep the sign's
# proportions to that stroke (dot 1.848 x stroke, opening 0.742 x stroke).
stroke = 40
inner = radius - stroke
half_slit = stroke * 0.371
core_d = stroke * 1.848
outer_x = sqrt(radius ** 2 - half_slit ** 2)
inner_x = sqrt(inner ** 2 - half_slit ** 2)
ring_paths = []
for side, sweep in [(-1, 1), (1, 0)]:
    slit_y = radius + side * half_slit
    ring_paths.append(
        f"M {radius - outer_x:.3f} {slit_y:.3f} "
        f"A {radius} {radius} 0 0 {sweep} {radius + outer_x:.3f} {slit_y:.3f} "
        f"H {radius + inner_x:.3f} A {inner} {inner} 0 0 {1 - sweep} "
        f"{radius - inner_x:.3f} {slit_y:.3f} Z")
ring = at(7.25, {"x": cx - radius, "y": cy - radius, "exl": 0.5, "t": "V", "n": "BNG OS ring",
                 "w": diameter, "h": diameter, "f": {"c": "icon/neutral/bold"}, "d": ring_paths})
os_label = at(7.25, diagram_label("OS", "BNG OS", "Centralises",
                                 "Holds every client, lot and payment in one place.",
                                 cx - 210, 105, 420, 0.5, centered=True))
caption = at(0, {"x": 0, "y": 104, "exl": 1, **T("The tools you already have", "label/md-strong",
                                                  "text/neutral/subtle", w=211, al="R", nw=1)})
ch24 = [caption]
tools = [
    ("Fame", "megaphone", -126),
    ("Nexus Panthera", "users", -92),
    ("BNG Business", "coin", -58),
    ("Vertex", "building", -30),
    ("BNG Sales Monitor", "bar-chart", 40),
    ("Synergy", "circle-ask", 85),
    ("my.bngimmo.com", "smartphone", 126),
]
for i, (label, glyph, y_offset) in enumerate(tools):
    source_y = 168 + 64 * i
    destination_y = cy + y_offset
    destination_x = cx - sqrt(radius ** 2 - y_offset ** 2)
    top = min(source_y, destination_y)
    width = destination_x - 212
    start, end = source_y - top, destination_y - top
    line = conn(label + " → BNG OS", 212, top, width, abs(end - start),
                f"M 0 {start} C {width * 0.52:.3f} {start} {width * 0.70:.3f} {end} {width:.3f} {end}")
    line.update(exl=1, exw=0.5)
    tool_row = {"x": 0, "y": source_y - 28, "exl": 1, "t": "F", "n": "Tool · " + label,
                "w": 212, "h": 56, "lm": "H", "gap": 12, "ca": "c",
                "ch": [T(label, "label/md-strong", "text/neutral/bold", w=144, al="R", nw=1),
                       disc(label, 56, glyph, 24)]}
    step = i + 0.25
    ch24.extend([draw(step, line, target=ring, arrival=7.25), at(step, tool_row)])

core = at(8, {"x": cx - core_d / 2, "y": cy - core_d / 2, "exl": 0.5, "t": "E", "n": "Cortex core",
              "w": core_d, "h": core_d, "f": [{"c": "background/signature/bold"}]}, motion="end")
cortex = at(9, diagram_label("Cortex", "Cortex", "Guides decisions",
                             "Reads every tool and proposes the next step. A person confirms.",
                             654, 433, 246, 0))
core_edge = cx + core_d / 2
ai_width = cortex["x"] + 3 - core_edge
ai_height = cortex["y"] + 8 - cy
ai_line = ai_conn("Core → Cortex", core_edge - 4, cy - 4, ai_width, ai_height,
                  f"M 0 0 H 109 C 149 0 127 {ai_height} {ai_width:.3f} {ai_height}")
ai_line.update(exl=0.5, exw=0.5)
ai_dot = ai_node("Cortex callout", core_edge - 8, cy - 8)
ai_dot["exl"] = 0.5

studio = at(9.65, diagram_label("Studio", "Studio", "Extends it",
                                "Builds what BNG asks for, tested before it goes live.",
                                654, 170, 246, 0))
# One curve from Studio into the ring, the same shape as the tools' lines on the left. The modules Studio adds sit under it.
studio_top, studio_bottom = studio["y"] + 16, cy - 110
studio_height = studio_bottom - studio_top
entry_x = cx + sqrt(radius ** 2 - (studio_bottom - cy) ** 2)
studio_width = 646 - entry_x
studio_line = conn("Studio → BNG OS", entry_x, studio_top, studio_width, studio_height,
                   f"M {studio_width:.3f} 0 C {studio_width * 0.48:.3f} 0 {studio_width * 0.30:.3f} {studio_height} 0 {studio_height}")
studio_line.update(exl=0.5, exw=0.5)
chips = []
for i, label in enumerate(["Weekly report", "New alert"]):
    chip = annotation(label, 654 + i * 126, studio["y"] + 96, label)
    del chip["sh"]
    chip.update(w=120, h=26, exl=0)
    chips.append(at(10.4 + i * 0.6, chip, motion="end"))
draw(11.4, studio_line, arrival=12.3)
ownership = at(12.6, {"x": cx - 200, "y": 559, "exl": 0.5,
                      **T("Accounts, code and data belong to BNG.", "body/sm", "text/neutral/subtlest",
                          w=400, al="C", nw=1)})
ch24 += [ring, os_label, draw(8, ai_line, ai_dot, target=cortex), core, ai_dot, cortex,
         studio_line, studio, *chips, ownership]
s24 = slide("395:5162", "10 · Three products · Three products, one system", "22 / 27", "Recap", "Three products,\none system.", "One system BNG owns. Each part has one job.",
            "Illustrative · fictional people and figures", 10, ch24)
s24["props"]["Show note"] = False
dump("s24", s24)

# Variant "nostudio" (Khalid, 2026-11-18: a second file with Studio removed; build with BNG_VARIANT=nostudio): the same drawing without Studio.
import copy  # noqa: E402

own_ns = copy.deepcopy(ownership)
own_ns["seq"]["step"] = 10
ch24_ns = [own_ns if c is ownership else c for c in ch24 if c is not studio_line and c is not studio and not any(c is k for k in chips)]
s24_ns = slide("395:5162", "10 · Two products · Two products, one system (no Studio)", "22 / 27", "Recap", "Two products,\none system.",
               "One system BNG owns. Each part has one job.", "Illustrative · fictional people and figures", 10, ch24_ns)
s24_ns["props"]["Show note"] = False
dump("s24_ns", s24_ns)


# ---------------- 25 · What each one does (A) ----------------
def mock(inner, gap=8):
    return {"t": "F", "sh": "L", "h": 272, "f": [{"c": "background/neutral/subtle"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 8, "k": 1, "lm": "H", "gap": gap,
            "pad": [16, 16, 16, 16], "pa": "c", "ca": "c", "ch": inner}


def rail_item25(label, ic, col):
    return {"cn": "App / Navigation / Rail item", "t": "F", "sv": "H", "w": 72, "n": "Rail item · " + label, "cr": 8, "lm": "V", "gap": 4, "pad": [8, 4, 8, 4],
            "pa": "c", "ca": "c", "ch": [icon(ic, 24, "icon/neutral/" + col), T(label, "label/sm", "text/neutral/subtle", al="C", nw=1)]}


def fact25(name, label, value):
    return {"cn": "App / Data display / Fact row", "t": "F", "sv": "H", "w": 272, "n": "Fact · " + name, "sk": {"c": "border/neutral/subtle"}, "sw": [0, 0, 1, 0],
            "lm": "H", "gap": 12, "pad": [6, 12, 6, 12], "ca": "c",
            "ch": [{"t": "F", "sh": "L", "sv": "H", "lm": "V", "ch": [T(label, "body/xs", "text/neutral/subtlest", nw=1), T(value, "label/md-strong", "text/neutral/bold", nw=1)]}]}


def checks(lines):
    return {"t": "F", "sh": "L", "sv": "H", "k": 1, "lm": "V", "gap": 8,
            "ch": [{"t": "F", "sh": "L", "sv": "H", "k": 1, "lm": "H", "gap": 8,
                    "ch": [icon("checkmark-20", 20), T(s, "body/md", "text/neutral/subtle", sh="L")]} for s in lines]}


def card25(name, x, mockup, lk, head, lines):
    return {"x": x, "y": 96, "t": "F", "w": 440, "h": 600, "n": "Card · " + name, "f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1,
            "cr": 12, "k": 1, "lm": "V", "gap": 20, "pad": [24, 24, 24, 24],
            "ch": [mockup, lk, T(head, "heading/md", "text/neutral/bold", sh="L"), checks(lines)]}


mock_os = mock([{"t": "F", "sh": "H", "sv": "H", "k": 1, "lm": "V", "gap": 4,
                 "ch": [rail_item25("Home", "home", "bold"), rail_item25("Clients", "group", "subtle"), rail_item25("Money", "coin", "subtle")]},
                {"t": "F", "sh": "H", "sv": "H", "k": 1, "lm": "V", "gap": 8,
                 "ch": [fact25("Due", "Due", "MAD 12.4M"), fact25("Received", "Received", "MAD 9.2M"), fact25("Late", "Late", "MAD 1.9M")]}])

sugg25 = suggestion("Assign the adviser", 0, 0, "Assign the Dutch-speaking adviser who is free now", "Strong fit for Elyazia, 2-bed.")
for k in ("x", "y"):
    del sugg25[k]
sugg25["w"] = 360
btns = {"t": "F", "sh": "L", "sv": "H", "k": 1, "lm": "H", "gap": 8, "pa": "x",
        "ch": [{"cn": "App / Actions / Button", "t": "F", "sh": "H", "h": 32, "n": "Button · Decline", "f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"},
                "sw": 1, "cr": 8, "lm": "H", "gap": 4, "pad": [0, 12, 0, 12], "pa": "c", "ca": "c", "ch": [T("Decline", "label/md", "text/neutral/bold", nw=1)]},
               {"cn": "App / Actions / Button", "t": "F", "sh": "H", "h": 32, "n": "Button · Approve", "f": [{"c": "background/action/bold"}], "cr": 8, "lm": "H", "gap": 4,
                "pad": [0, 12, 0, 12], "pa": "c", "ca": "c", "ch": [T("Approve", "label/md-strong", "text/on-action/bold", nw=1)]}]}
confirms = tag_neutral("Sales manager confirms", "Sales manager confirms", x=188, y=20, ab=1)
mock_cx = mock([{"t": "F", "sh": "H", "sv": "H", "k": 1, "lm": "V", "gap": 8, "ch": [sugg25, btns, confirms]}])


def list_row25(name, ic, title, sub, tail=None):
    d = disc("Tool disc", 56, ic, 24)
    d["n"] = "Tool disc"
    r = {"cn": "Illo / List row", "t": "F", "w": 360, "h": 56, "n": "List row · " + name, "lm": "H", "gap": 12, "ca": "c",
         "ch": [d, {"t": "F", "sh": "L", "sv": "H", "lm": "V", "gap": 2, "ch": [T(title, "heading/xs", "text/neutral/bold", sh="L"), T(sub, "body/xs", "text/neutral/subtlest", sh="L")]}]}
    if tail:
        r["ch"].append(tag_neutral("Tag", tail))
        r["ch"][-1]["n"] = "Tag"
    return r


def gap_conn(a, b):
    return {"t": "F", "w": 360, "h": 16, "n": "Connector gap",
            "ch": [{"x": 28, "y": 0, "t": "V", "n": "Connector · %s to %s" % (a, b), "w": 0, "h": 16, "sk": {"c": "border/neutral/default"}, "sw": 4, "da": [4, 4], "cap": "ROUND",
                    "d": ["M 0 0 L 0 16"]}]}


mock_st = mock([{"t": "F", "sh": "H", "sv": "H", "k": 1, "lm": "V",
                 "ch": [list_row25("Asked", "pen", "Asked", "In plain words"), gap_conn("Asked", "Built"),
                        list_row25("Built", "code", "Built", "Ready for testing"), gap_conn("Built", "Live"),
                        list_row25("Live", "server", "Live", "In use", "Yours to keep")]}])

ch25 = [{"x": -468, "y": 0, **T("Recap", "eyebrow/md", "text/neutral/subtlest", tc="UPPER", nw=1)},
        {"x": -468, "y": 26, **T("What each one does.", "heading/xl", "text/neutral/bold", nw=1)},
        card25("BNG OS", -468, mock_os, lockup("OS", 196, "BNG OS"), "Holds every client, lot and payment in one place.",
               ["One login for the whole group", "Each role sees its own part", "The group’s cash on one screen", "Every change is logged"]),
        card25("Cortex", -4, mock_cx, lockup("Cortex", 177, "Cortex"), "Reads every tool and proposes the next step.",
               ["Checks every tool against the others", "Clear cases run on their own", "Doubtful cases go to a person", "Money and legal steps wait for a yes"]),
        card25("Studio", 460, mock_st, lockup("Studio", 173, "Studio"), "Builds what BNG asks for, tested before it goes live.",
               ["Asked for in plain words", "Planned, built and tested for you", "Live only after every check", "Code and data stay with BNG"])]
at(0, *ch25[:2])
at(1, ch25[2])
at(2, ch25[3])
at(3, ch25[4])
asked, to_built, built, to_live, live = mock_st["ch"][0]["ch"]
at(4, asked)
at(5, built)
at(6, live)
draw(4, to_built["ch"][0], target=built)
draw(5, to_live["ch"][0], target=live)
s25 = {"id": "397:5247", "name": "10 · Three products · What each one does · A",
       "props": {"Lede": "A lede in one or two short lines.", "Show lede": False, "Eyebrow": "11 · It is yours", "Title": "What each\none does.", "Show footer": True, "Show note": True,
                 "Show nav": True, "Number": "23 / 27", "Show title column": False, "Note": "Illustrative example · fictional people and figures"},
       "nav": {"Chapter": "10"}, "ch": ch25}
dump("s25", s25)


# Variants: "nostudio" keeps the OS and Cortex cards, wider; "studio" keeps the Studio card alone, centred, with its own heading.
def recard(card, x, w, shift=0):
    c = copy.deepcopy(card)
    c.update(x=x, w=w)

    def walk(n):
        if "seq" in n:
            n["seq"]["step"] -= shift
            if "arrival" in n["seq"]:
                n["seq"]["arrival"] -= shift
        for k in n.get("ch", []):
            walk(k)
    walk(c)
    return c


s25_ns = copy.deepcopy(s25)
s25_ns["name"] = "10 · Two products · What each one does (no Studio)"
s25_ns["ch"] = [*copy.deepcopy(ch25[:2]), recard(ch25[2], -468, 676), recard(ch25[3], 224, 676)]
dump("s25_ns", s25_ns)

s25_st = copy.deepcopy(s25)
s25_st["name"] = "09 · Studio · What Studio does (Studio only)"
head_st = copy.deepcopy(ch25[:2])
head_st[0] = {"x": -468, "y": 0, **T("Studio", "eyebrow/md", "text/neutral/subtlest", tc="UPPER", nw=1), "seq": head_st[0]["seq"]}
head_st[1] = {"x": -468, "y": 26, **T("What Studio does.", "heading/xl", "text/neutral/bold", nw=1), "seq": head_st[1]["seq"]}
s25_st["ch"] = [*head_st, recard(ch25[4], -122, 676, shift=2)]
dump("s25_st", s25_st)
