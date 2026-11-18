"""Slide 19 from the Figma read of 2026-11-17 (321:5013). Run: PYTHONPATH=. python -P gen_s19.py"""
from dsl import *
from gen_s18 import desktop_full, rail, ucard


def tile(name, x, label, value):
    return {"x": x, "y": 68, "cn": "App / Data display / Figure tile", "t": "F", "sv": "H", "w": 160, "n": "Figure tile · " + name,
            "f": [{"c": "background/neutral/subtle"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 8, "lm": "V", "gap": 2, "pad": [12, 16, 12, 16],
            "ch": [T(label, "body/sm", "text/neutral/subtlest", nw=1), T(value, "heading/md", "text/neutral/bold", sh="L")]}


def drow(name, y, title, sub, amt, cap, selected=False):
    r = {"x": 104, "y": y, "cn": "App / Cortex / Decision row", "t": "F", "w": 504, "h": 56, "n": "Decision row · " + name}
    if selected:
        r["f"] = [{"c": "background/neutral/selected"}]
    else:
        r.update({"sk": {"c": "border/neutral/subtle"}, "sw": [0, 0, 1, 0]})
    r.update({"cr": 8, "lm": "H", "gap": 16, "pad": [0, 16, 0, 16], "ca": "c"} if selected else {"lm": "H", "gap": 16, "pad": [0, 16, 0, 16], "ca": "c"})
    r["ch"] = [marker(16),
               {"t": "F", "sh": "L", "sv": "H", "k": 1, "lm": "V", "gap": 2, "pa": "c",
                "ch": [T(title, "heading/xs", "text/neutral/bold", sh="L"), T(sub, "body/sm", "text/neutral/subtle", sh="L")]},
               {"t": "F", "sv": "H", "w": 112, "k": 1, "lm": "V", "pa": "c", "ch": [T(amt, "label/md-strong", "text/neutral/bold", nw=1), T(cap, "body/sm", "text/neutral/subtlest", nw=1)]}]
    return r


label = {"x": 304, "y": 156, "cn": "App / Cortex / Suggestion label", "t": "F", "sh": "H", "sv": "H", "n": "Suggestion label · Suggested by Cortex",
         "f": [{"c": "background/neutral/subtle"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 4, "lm": "H", "gap": 4, "pad": [4, 8, 4, 6], "ca": "c",
         "ch": [marker(14), T("Suggested by Cortex", "label/tag", "text/neutral/subtle", nw=1)]}
inner = [rail("Home", [44, 102, 158, 214, 270, 326]),
         {"x": 104, "y": 16, **T("Good morning", "heading/sm", "text/neutral/bold", nw=1)},
         {"x": 104, "y": 40, **T("3 decisions are waiting", "body/md", "text/neutral/subtlest", nw=1)},
         tile("Due", 104, "Due this month", "MAD 12.4M"), tile("Received", 276, "Received this month", "MAD 9.2M"), tile("Late", 448, "Late this month", "MAD 1.9M"),
         {"x": 104, "y": 160, **T("Decisions waiting for you", "heading/xs", "text/neutral/bold", nw=1)},
         label,
         drow("Call Youssef B. before Friday", 188, "Call Youssef B. before Friday", "Last payment 26 days late", "MAD 92,500", "overdue", True),
         drow("Match MAD 120,000 to lot A-102", 244, "Match MAD 120,000 to lot A-102", "Amount and reference match", "MAD 120,000", "to match"),
         drow("Fix the price of lot B-214", 300, "Fix the price of lot B-214", "Contract and Nexus Panthera differ", "MAD 15,000", "price gap")]
# the Home rail item is the selected one on this slide
ch = [desktop_full("Device · Desktop · Cockpit", inner),
      ucard("The whole group", 366, 8, "The whole group", "Cash due, received and late"),
      conn("figures → device", 494, 103, 0, 53, "M 0 0 L 0 53"), node("figures", 486, 95), node("Device · figures", 486, 148),
      ucard("Cortex proposes", 162, 640, "Cortex proposes", "Each decision, with its reason"),
      ai_conn("device → proposal", 290, 556, 0, 84, "M 0 0 L 0 84"), ai_node("Device · proposal", 282, 548),
      ucard("A stake on each row", 494, 640, "A stake on each row", "The amount behind each one"),
      conn("device → stake", 622, 556, 0, 84, "M 0 0 L 0 84"), node("Device · stake", 614, 548), node("stake", 614, 632)]
s19 = slide("321:5013", "08 · The app · The day starts with decisions", "18 / 27", "The app", "The day starts\nwith decisions.",
            "The group's cash on top, then the decisions Cortex proposes, each with its reason. A person approves every one.",
            "Illustrative example · fictional people and figures", 8, ch)
dump("s19", s19)
