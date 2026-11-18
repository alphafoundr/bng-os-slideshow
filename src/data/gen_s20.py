"""Slide 20 from the Figma read of 2026-11-17 (321:5889). Run: PYTHONPATH=. python -P gen_s20.py"""
from dsl import *
from gen_s18 import rail
from desk import desktop_big, callout


def event(title_key, y, ic, title, sub, date, src):
    # Figma gives the dot a 2px OUTSIDE stroke in the page colour (white on white): not drawn
    return {"x": 104, "y": y, "cn": "App / Data display / Timeline event", "t": "F", "sv": "H", "w": 504, "n": "Event / " + title_key, "lm": "H", "gap": 12, "pad": [12, 0, 12, 0],
            "ch": [{"t": "F", "w": 28, "h": 28, "f": [{"c": "background/neutral/subtle"}], "cr": 999, "lm": "H", "pa": "c", "ca": "c", "ch": [icon(ic, 14)]},
                   {"t": "F", "sh": "L", "sv": "H", "lm": "V", "gap": 2, "ch": [T(title, "label/md-strong", "text/neutral/bold", nw=1), T(sub, "body/sm", "text/neutral/subtle", nw=1)]},
                   {"t": "F", "sh": "H", "sv": "H", "lm": "V", "gap": 4, "ca": "x",
                    "ch": [T(date, "body/xs", "text/neutral/subtlest", nw=1),
                           {"cn": "App / Data display / Source badge", "t": "F", "sh": "H", "sv": "H", "n": "Source", "f": [{"c": "background/neutral/subtle"}], "cr": 4, "lm": "H",
                            "gap": 4, "pad": [2, 6, 2, 6], "ca": "c",
                            "ch": [{"t": "E", "w": 6, "h": 6, "f": [{"c": "icon/neutral/subtle"}]}, T(src, "label/tag", "text/neutral/subtle", nw=1)]}]}]}


status = {"x": 196, "y": 17, "cn": "App / Data display / Status tag", "t": "F", "sh": "H", "sv": "H", "n": "App / Data display / Status tag", "f": [{"c": "background/success/subtle"}],
          "cr": 4, "lm": "H", "gap": 4, "pad": [2, 8, 2, 8], "ca": "c", "ch": [icon("circle-checkmark", 12, "icon/success/bold"), T("Identity verified", "label/tag", "text/success/bold", nw=1)]}
inner = [rail("Clients", [44, 100, 156, 214, 270, 326]),
         {"x": 104, "y": 16, **T("Hicham L.", "heading/sm", "text/neutral/bold", nw=1)},
         {"x": 104, "y": 40, **T("Buyer · Lot B-214", "body/md", "text/neutral/subtlest", nw=1)},
         event("Reminder delivered and opened twice", 76, "envelope", "Reminder delivered and opened twice", "15 days before the due date", "28 Oct", "Cortex"),
         event("First payment received, 30%", 144, "coin", "First payment received, 30%", "Matched to the bank statement", "14 Mar", "Bank"),
         event("Video visit, 34 minutes", 212, "smartphone", "Video visit, 34 minutes", "Asked about the payment schedule", "08 Mar", "my.bngimmo.com"),
         event("Saw an ad and filled the form", 280, "megaphone", "Saw an ad and filled the form", "Interested in a 2-bedroom, budget stated", "02 Mar", "Fame"),
         status]
ch = [desktop_big("Device · Desktop · Client record", inner),
      *callout(1, "A", "Cortex writes to it too", "Its reminders are logged here", "cortex event → device", ai=True),
      *callout(3, "B", "One timeline", "Every tool, in date order", "timeline → device"),
      *callout(5, "C", "Where it comes from", "The source on every event", "device → sources", source="device")]
s20 = slide("321:5889", "08 · The app · One client, one record", "19 / 27", "The app", "One client,\none record.",
            "Every fact with where it comes from, on one timeline across the tools.",
            "Illustrative example · fictional people and figures", 8, ch)
s20["props"]["Big desktop"] = True
dump("s20", s20)
