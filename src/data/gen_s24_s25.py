"""Slides 24 (395:5162, final) and 25 (397:5247, version A, final) from the Figma reads of 2026-11-17.
Run: cd src/data && PYTHONPATH=. python -P gen_s24_s25.py"""
from dsl import *


def sign(prod):
    if prod == "Cortex":
        return {"t": "F", "w": 48, "h": 48, "n": "Sign", "ch": [marker(48, 0, 0)]}
    return {"cn": "Brand / Sign", "w": 48, "h": 48, "lg": 1, "vp": {"Product": prod, "Size": "48", "Ink": "Full colour"}}


def lockup(prod, w, label):
    """Brand / Product lockup, Size Deck: the 48 sign, 12 gap and the name in heading/xl."""
    return {"cn": "Brand / Product lockup", "t": "F", "w": w, "h": 48, "n": "Lockup · " + prod, "lm": "H", "gap": 12, "ca": "c",
            "ch": [sign(prod), T(label, "heading/xl", "text/neutral/bold", nw=1)]}


def tag_inverse(name, text):
    return {"cn": "Illo / Tag", "t": "F", "sh": "H", "sv": "H", "n": "Tag · " + name, "f": [{"c": "background/inverse/bold"}], "cr": 4, "lm": "H",
            "pad": [2, 8, 2, 8], "pa": "c", "ca": "c", "ch": [T(text, "label/tag", "text/inverse/bold", nw=1)]}


def tag_neutral(name, text, **kw):
    t = {"cn": "Illo / Tag", "t": "F", "sh": "H", "sv": "H", "n": "Tag · " + name, "f": [{"c": "background/neutral/tag"}], "cr": 4, "lm": "H",
         "pad": [2, 8, 2, 8], "pa": "c", "ca": "c", "ch": [T(text, "label/tag", "text/neutral/bold", nw=1)]}
    t.update(kw)
    return t


# ---------------- 24 · Three products, one system ----------------
def prod_card(name, x, y, w, prod, lw, label, sentence, tagtext):
    return {"x": x, "y": y, "t": "F", "w": w, "h": 108, "n": "Card · " + name, "f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"},
            "sw": 1, "cr": 12, "k": 1, "lm": "H", "gap": 16, "pad": [24, 24, 24, 24], "ca": "c",
            "ch": [lockup(prod, lw, label),
                   {"t": "F", "sh": "L", "sv": "H", "k": 1, "lm": "V", "gap": 8,
                    "ch": [T(sentence, "body/md", "text/neutral/subtle", sh="L"), tag_neutral(tagtext, tagtext)]}]}


panel = {"x": 0, "y": 125, "t": "F", "w": 900, "h": 270, "n": "Panel · BNG OS", "f": [{"c": "background/neutral/subtle"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 12,
         "ch": [{"x": 24, "y": 24, "t": "F", "sh": "H", "sv": "H", "k": 1, "lm": "H", "gap": 16, "ca": "c",
                 "ch": [lockup("OS", 196, "BNG OS"), tag_inverse("Holds everything", "Holds everything")]},
                prod_card("Cortex", 24, 120, 852, "Cortex", 177, "Cortex", "Reads the tools, checks them against each other, proposes. A person approves.", "Decides, inside it"),
                {"x": 24, "y": 84, **T("One place for clients, properties and money, above the seven tools.", "body/md", "text/neutral/subtle", nw=1)}]}
studio = prod_card("Studio", 0, 495, 900, "Studio", 173, "Studio", "Builds what BNG asks for, tested before it goes live. It stays BNG’s.", "Extends it")
c24 = conn("BNG OS to Studio", 450, 395, 0, 100, "M 0 0 L 0 100")
c24["n"] = "Connector · BNG OS to Studio"
ch24 = [panel, studio, c24, node("BNG OS end", 442, 387), node("Studio end", 442, 487)]
at(0, panel)
at(1, panel["ch"][1])
at(3, studio)
draw(2, *ch24[2:], target=studio)
s24 = slide("395:5162", "10 · Three products · Three products, one system", "22 / 27", "Recap", "Three products,\none system.", "One system BNG owns. Each part has one job.",
            "Illustrative · fictional people and figures", 10, ch24)
s24["props"]["Show note"] = False
dump("s24", s24)


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
