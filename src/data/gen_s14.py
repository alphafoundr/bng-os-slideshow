"""Slide 14 from the Figma read of 2026-11-17 (303:3128). Run: PYTHONPATH=. python -P gen_s14.py"""
from dsl import *


def fact(name, x, y, label, value, src):
    return {"x": x, "y": y, "cn": "App / Data display / Fact row", "t": "F", "sv": "H", "w": 272, "n": "Fact · " + name,
            "sk": {"c": "border/neutral/subtle"}, "sw": [0, 0, 1, 0], "lm": "H", "gap": 12, "pad": [6, 12, 6, 12], "ca": "c",
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


def desktop(name, inner):
    """Illo / Device · Desktop 640x440: black bezel 640x400, stand 288..352, foot 208..432, screen 624x384 at (8,8) with a 592x352 content frame."""
    return {"x": 130, "y": 156, "cn": "Illo / Device · Desktop", "t": "F", "w": 640, "h": 440, "n": name,
            "ch": [{"x": 0, "y": 0, "t": "R", "w": 640, "h": 400, "f": [{"c": "background/inverse/bold"}], "cr": 12},
                   {"x": 288, "y": 400, "t": "R", "w": 64, "h": 32, "f": [{"c": "background/neutral/strong"}]},
                   {"x": 208, "y": 432, "t": "R", "w": 224, "h": 8, "f": [{"c": "background/neutral/strong"}], "cr": 999},
                   {"x": 8, "y": 8, "t": "F", "w": 624, "h": 384, "f": [{"c": "background/neutral/raised"}], "cr": 8, "k": 1, "lm": "V", "gap": 12,
                    "pad": [16, 16, 16, 16], "ch": [{"t": "F", "w": 592, "h": 352, "k": 1, "ch": inner}]}]}


def confirmation(name, x, y, w, title, sub):
    return {"x": x, "y": y, "cn": "App / Feedback / Confirmation", "t": "F", "sv": "H", "w": w, "n": "Confirmation · " + name,
            "f": [{"c": "background/neutral/subtle"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 8, "lm": "H", "gap": 8, "pad": [12, 12, 12, 12],
            "ch": [icon("circle-checkmark", 20, "icon/success/bold"),
                   {"t": "F", "sh": "L", "sv": "H", "k": 1, "lm": "V", "gap": 2,
                    "ch": [T(title, "label/md-strong", "text/neutral/bold", sh="L"), T(sub, "body/sm", "text/neutral/subtlest", sh="L")]}]}


def vconn(name, x, y, h, ai):
    f = ai_conn if ai else conn
    r = f(name, x, y, 0, h, "M 0 0 L 0 %s" % h)
    return r


def sugg272(x, y):
    s = suggestion("Assign the adviser", x, y, "Assign the Dutch-speaking adviser who is free now", "Strong fit for Elyazia, 2-bed.")
    s["w"] = 272
    return s


inner = [{"x": 16, "y": 16, **T("New lead · Elyazia, 2-bed", "heading/sm", "text/neutral/bold", nw=1)},
         {"x": 16, "y": 40, **T("Came in through the website form", "body/md", "text/neutral/subtlest", nw=1)},
         {"x": 16, "y": 80, **T("What Cortex read", "label/md-strong", "text/neutral/subtlest", nw=1)},
         {"x": 304, "y": 80, **T("What Cortex proposes", "label/md-strong", "text/neutral/subtlest", nw=1)},
         fact("Project", 16, 104, "Project", "Elyazia, 2-bed", "Fame"),
         fact("Language", 16, 154, "Language", "Dutch", "Fame"),
         fact("Earlier record", 16, 204, "Earlier record", "None found", "Nexus Panthera"),
         sugg272(304, 104),
         button("Decline", 417, 258, "Decline", False), button("Approve", 498, 258, "Approve", True),
         {"x": 304, "y": 304, **T("Nothing is sent until you approve.", "body/xs", "text/neutral/subtlest", nw=1)},
         fact("Who is free", 16, 254, "Availability", "Two advisers free", "Fame")]
ch = [desktop("Device · Desktop · Decisions inbox", inner)]
for name, x, ic, label in (("Website form", 208, "globe", "Website form"), ("Fame's CRM", 411, "megaphone", "Fame"), ("Nexus Panthera", 600, "users", "Nexus Panthera")):
    cx = x + 42 if name == "Website form" else (x + 39 if name == "Fame's CRM" else x + 50)
    ch += [tool(name, x, 8, ic, label), vconn(name + " → decisions inbox", cx, 103, 53, True),
           ai_node(name, cx - 8, 95)]
ch += [persona_h("The sales manager", 130, 640, 256, "5755e103", "The sales manager", "Sees the reason, then decides"),
       confirmation("Lead assigned", 426, 640, 344, "Lead assigned to the adviser", "Approved by the sales manager and logged in the lead's history."),
       vconn("sales manager → decisions inbox", 258, 556, 84, False), node("decisions inbox · approves", 250, 548), node("sales manager", 250, 632),
       annotation("approves", 218, 592, "approves"),
       vconn("decisions inbox → lead assigned", 598, 556, 84, True), ai_node("Device · lead assigned", 590, 548),
       annotation("after approval", 545, 592, "after approval")]
# the persona uses the sales director portrait (5755e103) with the Figma crop; persona_h passes the hash to portrait()
s14 = slide("303:3128", "08 · Cortex at work · From the form to the right adviser", "18 / 27", "Cortex at work", "From the form\nto the right adviser.",
            "Cortex reads a new lead, checks who is free and who speaks the language, and proposes an adviser. A person confirms.",
            "Illustrative example · fictional people and figures", 8, ch)
dump("s14", s14)
