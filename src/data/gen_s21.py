"""Slide 21 from the Figma read of 2026-11-17 (322:6839). Run: cd src/data && PYTHONPATH=. python -P gen_s21.py"""
from dsl import *
from gen_s14 import fact, vconn
from gen_s18 import desktop_full, rail, ucard, SIGN  # noqa: F401


def badge(name, text):
    return {"cn": "App / Data display / Source badge", "t": "F", "sh": "H", "sv": "H", "n": name, "f": [{"c": "background/neutral/subtle"}], "cr": 4,
            "lm": "H", "gap": 4, "pad": [2, 6, 2, 6], "ca": "c",
            "ch": [{"t": "E", "w": 6, "h": 6, "f": [{"c": "icon/neutral/subtle"}]}, T(text, "label/tag", "text/neutral/subtle", nw=1)]}


def srow(b, amount):
    return {"t": "F", "sh": "L", "sv": "H", "k": 1, "lm": "H", "gap": 8, "pa": "s", "ca": "c",
            "ch": [b, T(amount, "label/md-strong", "text/neutral/bold", nw=1)]}


conflict = {"x": 104, "y": 98, "cn": "App / Feedback / Conflict block", "t": "F", "sv": "H", "w": 244, "n": "Conflict · two late amounts",
            "f": [{"c": "background/neutral/subtle"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 8, "lm": "V", "gap": 8, "pad": [12, 12, 12, 12],
            "ch": [{"t": "F", "sh": "L", "sv": "H", "k": 1, "lm": "H", "gap": 6, "ca": "c",
                    "ch": [icon("triangle-warning", 16, "icon/danger/bold"), T("Two sources, two late amounts", "label/md-strong", "text/neutral/bold", sh="L")]},
                   srow(badge("Badge A", "BNG Business"), "MAD 48,000"),
                   srow(badge("Badge B", "Nexus Panthera"), "MAD 53,000"),
                   T("Difference MAD 5,000", "body/sm", "text/neutral/bold", sh="L")]}


def fact244(name, y, label, value, src):
    f = fact(name, 104, y, label, value, src)
    f["w"] = 244
    return f


sugg = suggestion("Cortex is holding this reminder", 364, 72, "Reminder on hold for Omar T.", "Two sources give two late amounts.", label="Cortex is holding this reminder")
sugg["w"] = 244
buttons = {"x": 364, "y": 228, "t": "F", "sv": "H", "w": 369.99, "k": 1, "lm": "H", "gap": 8, "ca": "c",
           "ch": [{"cn": "App / Actions / Button", "t": "F", "sh": "H", "h": 32, "n": "Button / Settle the amount", "f": [{"c": "background/action/bold"}], "cr": 8, "lm": "H",
                   "gap": 4, "pad": [0, 12, 0, 12], "pa": "c", "ca": "c", "ch": [T("Settle the amount", "label/md-strong", "text/on-action/bold", nw=1)]},
                  {"cn": "App / Actions / Button", "t": "F", "sh": "H", "h": 32, "n": "Button / Skip for now", "cr": 8, "lm": "H", "gap": 4, "pad": [0, 12, 0, 12],
                   "pa": "c", "ca": "c", "ch": [T("Skip for now", "label/md", "text/neutral/subtle", nw=1)]}]}

inner = [rail("Money", [44, 100, 156, 212, 268, 326]),
         {"x": 104, "y": 16, **T("Omar T.", "heading/sm", "text/neutral/bold", nw=1)},
         {"x": 104, "y": 40, **T("Lot C-031 · Instalment 2 of 6", "body/md", "text/neutral/subtlest", nw=1)},
         {"x": 104, "y": 72, **T("Checked against the contract", "heading/xs", "text/neutral/bold", w=288)},
         conflict, fact244("Schedule", 238, "Schedule", "Due 28 Oct", "BNG Business"), fact244("Paid so far", 288, "Paid so far", "MAD 96,000", "Bank"),
         sugg, buttons]

ch = [desktop_full("Device · Desktop · Collections", inner),
      ucard("Two sources, two amounts", 222, 8, "Two sources, two amounts", "Both shown, each with its source"),
      vconn("two sources → device", 350, 103, 53, False), node("two sources", 342, 95), node("Device · two sources", 342, 148),
      ucard("Cortex holds the message", 512, 8, "Cortex holds the message", "It never sends a wrong figure"),
      vconn("hold → device", 640, 103, 53, True), ai_node("hold", 632, 95),
      ucard("A person settles it", 494, 640, "A person settles it", "Nothing is sent before approval"),
      vconn("device → settle", 622, 556, 84, False), node("Device · settle", 614, 548), node("settle", 614, 632)]
s21 = slide("322:6839", "06 · The app · Money that agrees", "14 / 27", "The app", "Money that agrees\nbefore it moves.",
            "Cortex checks each reminder against the contract and the bank. When two sources differ, it holds the message and says why.",
            "Illustrative example · fictional people and figures", 6, ch)
dump("s21", s21)
