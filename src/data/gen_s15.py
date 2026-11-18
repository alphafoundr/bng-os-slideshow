"""Slide 15 (307:3287), free-standing cards, no desktop device (2026-11-18; layout A in cortex_flow.py).
Run: PYTHONPATH=. python -P gen_s15.py"""
from dsl import *
from cortex_flow import *


def badge(src):
    return {"cn": "App / Data display / Source badge", "t": "F", "sh": "H", "sv": "H", "n": "Source", "f": [{"c": "background/neutral/subtle"}],
            "cr": 4, "lm": "H", "gap": 4, "pad": [2, 6, 2, 6], "ca": "c",
            "ch": [{"t": "E", "w": 6, "h": 6, "f": [{"c": "icon/neutral/subtle"}]}, T(src, "label/tag", "text/neutral/subtle", nw=1)]}


def price_box():
    return {"x": 0, "y": 0, "cn": "App / Data display / Fact row", "t": "F", "sh": "L", "sv": "H", "n": "Fact · Price", "f": [{"c": "background/neutral/subtle"}],
            "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 8, "lm": "H", "gap": 12, "pad": [16, 16, 16, 16],
            "ch": [{"t": "F", "sh": "L", "sv": "H", "lm": "V", "gap": 2,
                    "ch": [T("Price", "body/xs", "text/neutral/subtlest", nw=1), T("MAD 1,235,000 in the contract", "label/md-strong", "text/neutral/bold", nw=1),
                           T("Nexus Panthera says MAD 1,250,000", "body/sm", "text/neutral/subtle", nw=1)]},
                   icon("triangle-warning", 16, "icon/danger/bold"), badge("BNG Business")]}


def facts():
    return [stretch(fact("ID document", 0, 0, "ID document", "Name matches", "Uploaded documents", py=ROW_PY - 2)),
            stretch(fact("Proof of address", 0, 0, "Proof of address", "Received", "Uploaded documents", py=ROW_PY - 2)),
            stretch(fact("Transfer", 0, 0, "Transfer", "Amount matches the contract", "Bank", py=ROW_PY - 2)), price_box()]


SOURCES = (("Uploaded documents", "file-document", "Uploaded documents"), ("Nexus Panthera", "users", "Nexus Panthera"),
           ("BNG Business", "coin", "BNG Business"), ("Bank", "bank", "Bank"))
H_FILE, H_READ = 196, 392
H_SUGG, H_APPR, H_CONF = 180, 204, 96
geo = GeoA([H_FILE, H_READ], 1, [H_SUGG, H_APPR, H_CONF], 4)
yl, yr = geo.yl, geo.yr
ch = [subject_card("Sales contract", X2, yl[0], W2, H_FILE, "buyer4", "Hind B.", "The buyer", "Sales contract · lot B-214",
                   "Read as the file arrived · 3 of 4 checks verified"),
      read_card("What Cortex checked", X2, yl[1], W2, H_READ, "What Cortex checked", facts()),
      suggestion_card("Hold the file", X3, yr[0], W3, H_SUGG, "Hold the file until\nthe price is settled", "Two tools, MAD 15,000 apart"),
      approval_card("The back office", X3, yr[1], W3, H_APPR, "rep", "Salma R.", "The back office", "Sees both values, then decides"),
      result_card("File on hold", X3C, yr[2], W3C, H_CONF, "File on hold, price to settle", "Approved by the back office and logged in the file's history.")]
sources = [source(name, X1, y - 28, ic, label) for y, (name, ic, label) in zip(geo.ys, SOURCES)]
ch = geo.build_flow(ch, sources, {"recv": "what Cortex checked", "chain": [("contract file", "what Cortex checked")],
                                 "propose": "suggestion", "approve": "back office", "result": "file on hold"})
s15 = slide("307:3287", "07 · Cortex at work · The file checks itself", "15 / 27", "Cortex at work", "The file\nchecks itself.",
            "A file is read as it arrives. Each mismatch names its field and goes to the right person.",
            "Illustrative example · fictional people and figures", 7, ch)
dump("s15", s15)
