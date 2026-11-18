"""Slide 18 from the Figma read of 2026-11-17 (321:4137). Run: PYTHONPATH=. python -P gen_s18.py
Also holds the app-shell helpers slide 19 and 20 import (rail, full-bleed desktop, UI cards)."""
from dsl import *
from gen_s14 import fact

SIGN = {"x": 38, "y": 12, "cn": "Brand / Sign", "w": 24, "h": 24, "lg": 1, "vp": {"Product": "OS", "Size": "24", "Ink": "Full colour"}}


def desktop_full(name, inner):
    """Illo / Device · Desktop with the screen content filling 624x384 (an app shell)."""
    return {"x": 130, "y": 156, "cn": "Illo / Device · Desktop", "t": "F", "w": 640, "h": 440, "n": name,
            "ch": [{"x": 0, "y": 0, "t": "R", "w": 640, "h": 400, "f": [{"c": "background/inverse/bold"}], "cr": 12},
                   {"x": 288, "y": 400, "t": "R", "w": 64, "h": 32, "f": [{"c": "background/neutral/strong"}]},
                   {"x": 208, "y": 432, "t": "R", "w": 224, "h": 8, "f": [{"c": "background/neutral/strong"}], "cr": 999},
                   {"x": 8, "y": 8, "t": "F", "w": 624, "h": 384, "f": [{"c": "background/neutral/raised"}], "cr": 8, "k": 1, "lm": "V", "gap": 12,
                    "ch": [{"t": "F", "w": 624, "h": 384, "k": 1, "ch": inner}]}]}


def rail_item(label, y, ic, selected=False):
    c = "bold" if selected else "subtle"
    r = {"x": 8, "y": y, "cn": "App / Navigation / Rail item", "t": "F", "sv": "H", "w": 72, "n": "Rail item / " + label}
    if selected:
        r.update({"f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1})
    r.update({"cr": 8, "lm": "V", "gap": 4, "pad": [4, 4, 4, 4], "pa": "c", "ca": "c",
              "ch": [icon(ic, 24, "icon/neutral/" + c), T(label, "label/sm", "text/neutral/" + c, al="C", nw=1)]})
    return r


def rail(sel, ys):
    items = [("Home", "home"), ("Inbox", "inbox"), ("Clients", "group"), ("Properties", "building"), ("Money", "coin"), ("Reports", "bar-chart")]
    return {"x": 0, "y": 0, "t": "F", "w": 88, "h": 384, "f": [{"c": "background/neutral/rail"}],
            "ch": [{"x": 87, "y": 0, "t": "R", "w": 1, "h": 384, "f": [{"c": "border/neutral/subtle"}]}] +
                  [rail_item(lbl, ys[i], ic, lbl == sel) for i, (lbl, ic) in enumerate(items)] + [SIGN]}


def ucard(name, x, y, title, sub):
    return {"x": x, "y": y, "cn": "Illo / UI card", "t": "F", "sv": "H", "w": 256, "n": "UI card · " + name, "f": [{"c": "background/neutral/raised"}],
            "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 12, "lm": "V", "gap": 12, "pad": [16, 16, 16, 16],
            "ch": [{"t": "F", "sh": "L", "sv": "H", "lm": "H", "gap": 8, "ca": "c", "ch": [T(title, "heading/xs", "text/neutral/bold", sh="L")]},
                   T(sub, "body/sm", "text/neutral/subtlest", sh="L")]}


def prow(name, text, count, selected=False):
    r = {"cn": "App / Navigation / Panel row", "t": "F", "sh": "L", "h": 32, "n": name}
    if selected:
        r["f"] = [{"c": "background/neutral/muted"}]
    r.update({"cr": 8, "lm": "H", "gap": 8, "pad": [0, 12, 0, 12], "ca": "c"})
    if selected:
        r["ch"] = [T(text, "label/md-strong", "text/neutral/bold", sh="L")]
    else:
        r["ch"] = [T(text, "body/sm", "text/neutral/subtle", sh="L")]
    if count:
        r["ch"].append(T(count, "label/sm", "text/neutral/subtlest", nw=1))
    return r


panel = {"x": 88, "y": 0, "t": "F", "w": 248, "h": 384, "n": "Level 2 panel", "f": [{"c": "background/neutral/canvas"}],
         "ch": [{"x": 247, "y": 0, "t": "R", "w": 1, "h": 384, "n": "Hairline · panel", "f": [{"c": "border/neutral/subtle"}]},
                {"x": 8, "y": 64, "cn": "App / Navigation / Panel group", "t": "F", "sv": "H", "w": 232, "n": "Group / Clients", "lm": "V", "gap": 4,
                 "ch": [{"t": "F", "sh": "L", "h": 28, "lm": "H", "gap": 8, "pad": [0, 8, 0, 12], "ca": "c",
                         "ch": [T("Clients", "label/sm", "text/neutral/subtlest", sh="L"), icon("chevron-down", 16, "icon/neutral/subtlest")]},
                        {"t": "F", "sh": "L", "sv": "H", "lm": "V", "gap": 2,
                         "ch": [prow("Row 1", "Leads", "48"), prow("Row 2", "Buyers", "126", True), prow("Row 3", "All people", "174"), prow("Row 4", "Segments", None)]}]},
                {"x": 0, "y": 0, "t": "F", "w": 248, "h": 56, "n": "Panel header", "lm": "H", "pad": [0, 8, 0, 20], "ca": "c",
                 "ch": [T("Clients", "heading/sm", "text/neutral/bold", nw=1), {"t": "F", "sh": "L", "sv": "H", "lm": "H"},
                        {"t": "F", "w": 32, "h": 32, "n": "Collapse panel", "cr": 8, "lm": "H", "pa": "c", "ca": "c", "ch": [icon("sidebar-left", 20, "icon/neutral/subtle")]}]},
                {"x": 0, "y": 335, "t": "F", "sv": "H", "w": 248, "n": "Panel footer", "sk": {"c": "border/neutral/subtle"}, "sw": [1, 0, 0, 0], "lm": "V", "pad": [8, 8, 8, 8],
                 "ch": [{"cn": "App / Navigation / Panel row", "t": "F", "sh": "L", "h": 32, "n": "Pin panel", "cr": 8, "lm": "H", "gap": 8, "pad": [0, 12, 0, 12], "ca": "c",
                         "ch": [icon("push-pin", 16, "icon/neutral/subtle"), T("Pin panel", "body/sm", "text/neutral/subtle", sh="L")]}]}]}

if __name__ == "__main__":
    inner = [rail("Clients", [44, 100, 156, 214, 270, 326]), panel,
             {"x": 344, "y": 16, **T("Hicham L.", "heading/sm", "text/neutral/bold", nw=1)},
             {"x": 344, "y": 40, **T("Buyer · Lot B-214", "body/md", "text/neutral/subtlest", nw=1)},
             fact("Adviser", 344, 68, "Adviser", "Salma K.", "Nexus Panthera"), fact("Last visit", 344, 118, "Last visit", "Video visit, 34 min", "my.bngimmo.com"),
             fact("Paid so far", 344, 168, "Paid so far", "MAD 741,000", "Bank"), fact("Next instalment", 344, 218, "Next instalment", "MAD 370,500 · 12 Nov", "BNG Business"),
             fact("Last reminder", 344, 268, "Last reminder", "Delivered, opened twice", "Cortex")]
    for f in inner[-5:]:
        f["n"] = f["n"].replace("Fact · ", "Fact / ")
    ch = [desktop_full("Device · Desktop · Shell", inner),
          ucard("Six areas", 54, 8, "Six areas", "Named for what people work on"),
          conn("rail → device", 182, 103, 0, 53, "M 0 0 L 0 53"), node("rail", 174, 95), node("Device · rail", 174, 148),
          ucard("Tools are badges", 572, 8, "Tools are badges", "Shown on each fact only"),
          conn("badges → device", 700, 103, 0.01, 53, "M 0 0 L 0 53"), node("badges", 692, 95), node("Device · badges", 692, 148),
          ucard("A second level", 162, 640, "A second level", "Each area opens its own lists"),
          conn("device → second level", 290, 556, 0, 84, "M 0 0 L 0 84"), node("Device · second level", 282, 548), node("second level", 282, 632)]
    s18 = slide("321:4137", "08 · The app · One place for everything", "17 / 27", "The app", "One place\nfor everything.",
                "Six areas, named for what people work on, not for the tool behind them. The tools show only as small badges.",
                "Illustrative example · fictional people and figures", 8, ch)
    dump("s18", s18)
