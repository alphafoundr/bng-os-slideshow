"""Slide 15 from the Figma read of 2026-11-17 (307:3287). Run: PYTHONPATH=. python -P gen_s15.py"""
from dsl import *
from gen_s14 import fact, button, desktop, confirmation, vconn


def badge(src):
    return {"cn": "App / Data display / Source badge", "t": "F", "sh": "H", "sv": "H", "n": "Source", "f": [{"c": "background/neutral/subtle"}],
            "cr": 4, "lm": "H", "gap": 4, "pad": [2, 6, 2, 6], "ca": "c",
            "ch": [{"t": "E", "w": 6, "h": 6, "f": [{"c": "icon/neutral/subtle"}]}, T(src, "label/tag", "text/neutral/subtle", nw=1)]}


price = {"x": 16, "y": 254, "cn": "App / Data display / Fact row", "t": "F", "sv": "H", "w": 272, "n": "Fact · Price", "f": [{"c": "background/neutral/subtle"}],
         "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 8, "lm": "H", "gap": 12, "pad": [12, 12, 12, 12],
         "ch": [{"t": "F", "sh": "L", "sv": "H", "lm": "V", "gap": 2,
                 "ch": [T("Price", "body/xs", "text/neutral/subtlest", nw=1), T("MAD 1,235,000 in the contract", "label/md-strong", "text/neutral/bold", nw=1),
                        T("Nexus Panthera says MAD 1,250,000", "body/sm", "text/neutral/subtle", nw=1)]},
                icon("triangle-warning", 16, "icon/danger/bold"), badge("BNG Business")]}
sg = suggestion("Hold the file", 304, 104, "Hold the file until\nthe price is settled", "Two tools, MAD 15,000 apart")
sg["w"] = 272
inner = [{"x": 16, "y": 16, **T("Sales contract · lot B-214", "heading/sm", "text/neutral/bold", nw=1)},
         {"x": 16, "y": 40, **T("Read as the file arrived · 3 of 4 checks verified", "body/md", "text/neutral/subtlest", nw=1)},
         {"x": 16, "y": 80, **T("What Cortex checked", "label/md-strong", "text/neutral/subtlest", nw=1)},
         {"x": 304, "y": 80, **T("What Cortex proposes", "label/md-strong", "text/neutral/subtlest", nw=1)},
         fact("ID document", 16, 104, "ID document", "Name matches", "Uploaded documents"),
         fact("Proof of address", 16, 154, "Proof of address", "Received", "Uploaded documents"),
         fact("Transfer", 16, 204, "Transfer", "Amount matches the contract", "Bank"),
         price, sg,
         button("Decline", 417, 258, "Decline", False), button("Approve", 498, 258, "Approve", True),
         {"x": 304, "y": 304, **T("Nothing is sent until you approve.", "body/xs", "text/neutral/subtlest", nw=1)}]
ch = [desktop("Device · Desktop · Contract file", inner)]
for name, x, cx, ic, label in (("Uploaded documents", 143, 210, "file-document", "Uploaded documents"), ("BNG Business", 486, 530, "coin", "BNG Business"),
                               ("Bank", 662, 690, "bank", "Bank"), ("Nexus Panthera", 320, 370, "users", "Nexus Panthera")):
    ch += [tool(name, x, 8, ic, label), vconn(name + " → contract file", cx, 103, 53, True), ai_node(name, cx - 8, 95)]
ch += [persona_h("The back office", 130, 640, 256, "2a9ca040", "The back office", "Sees both values, then decides"),
       confirmation("File on hold", 426, 640, 344, "File on hold, price to settle", "Approved by the back office and logged in the file's history."),
       vconn("back office → contract file", 258, 556, 84, False), node("contract file · approves", 250, 548), node("back office", 250, 632),
       annotation("approves", 218, 592, "approves"),
       vconn("contract file → file on hold", 598, 556, 84, True), ai_node("Device · file on hold", 590, 548),
       annotation("after approval", 545, 592, "after approval")]
s15 = slide("307:3287", "08 · Cortex at work · The file checks itself", "19 / 27", "Cortex at work", "The file\nchecks itself.",
            "A file is read as it arrives. Each mismatch names its field and goes to the right person.",
            "Illustrative example · fictional people and figures", 8, ch)
dump("s15", s15)
