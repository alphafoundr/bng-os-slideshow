"""usage: python -P tools/check_flow.py <port> [slide ...]   (default s14 s15 s16, at 1440x900 and 1920x970, EN and FR)
Checks, from the rendered DOM: every connector end lies on the edge of a card / suggestion / result / source disc it joins (0.6 px),
each AI dot is 8 px and centred on its line's start, each ring is 10 px and centred on its line end, no card overflows its fixed height,
no card overlaps another card, no empty band wider than 125 artboard px between the columns, and nothing in the flow enters
the title column (x < 480 on the page)."""
import re
import sys

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
port = sys.argv[1]
slides = sys.argv[2:] or ["s14", "s15", "s16"]
JS = open(__file__.replace("check_flow.py", "measure_flow.py"), encoding="utf-8").read().split('JS = r"""')[1].split('"""')[0]
TOL = 0.7
fails = 0


def edges(b):
    return {"l": b["x"], "r": b["x"] + b["w"], "t": b["y"], "b": b["y"] + b["h"]}


def on_edge(pt, b, tol=TOL):
    e = edges(b)
    x, y = pt
    inx, iny = e["l"] - tol <= x <= e["r"] + tol, e["t"] - tol <= y <= e["b"] + tol
    return ((abs(x - e["l"]) <= tol or abs(x - e["r"]) <= tol) and iny) or ((abs(y - e["t"]) <= tol or abs(y - e["b"]) <= tol) and inx)


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    for size in ((1440, 900), (1920, 970)):
        for fr in (False, True):
            for s in slides:
                ctx = b.new_context(viewport={"width": size[0], "height": size[1]})
                pg = ctx.new_page()
                pg.goto("http://localhost:%s/?nopreshow=1%s#%s" % (port, "&lang=fr" if fr else "", s))
                pg.wait_for_timeout(2200)
                res = pg.evaluate(JS, s)
                ex = pg.evaluate("parseFloat(getComputedStyle(document.getElementById('deck')).getPropertyValue('--ex'))")
                tag = "%s %dx%d %s" % (s, size[0], size[1], "FR" if fr else "EN")
                boxes = []
                for bx in res["boxes"]:
                    n = bx["n"]
                    if n.startswith(("Card ·", "Suggestion ·", "Confirmation ·")):
                        boxes.append(bx)
                    elif n.startswith("Tool ·"):       # the disc: 56 px, centred in the 140 px block, at its top
                        boxes.append({"n": n + " (disc)", "x": bx["x"] + 42, "y": bx["y"], "w": 56, "h": 56})
                problems = []
                for o in res["overflow"]:
                    problems.append("overflow " + o)
                cards = [x for x in boxes if x["n"].startswith(("Card ·", "Suggestion ·", "Confirmation ·"))]
                for i, a in enumerate(cards):
                    for c in cards[i + 1:]:
                        M = 20   # nothing closer than 20 px
                        if a["x"] - M < c["x"] + c["w"] and c["x"] - M < a["x"] + a["w"] and a["y"] - M < c["y"] + c["h"] and c["y"] - M < a["y"] + a["h"]:
                            problems.append("overlap or closer than 20 px: %s / %s" % (a["n"], c["n"]))
                # no empty band wider than 125 artboard px between the columns (source discs, cards): union of the boxes' x ranges
                spans = sorted((bx["x"], bx["x"] + bx["w"]) for bx in boxes)
                reach = spans[0][1]
                for lo, hi in spans[1:]:
                    if lo - reach > 125:
                        problems.append("empty band %.0f px wide between x %.0f and %.0f (slot px)" % (lo - reach, reach, lo))
                    reach = max(reach, hi)
                for l in res["lines"]:
                    ai = l["n"].startswith("AI")
                    # the dot for this line = node with the same tail name
                    tail = l["n"].split(" / ", 1)[1]
                    dots = [d for d in res["dots"] if d["n"].endswith(" · " + tail) or d["n"].endswith(" · " + tail + " (end)")]
                    start, end = l["from"], l["to"]
                    if not any(on_edge(end, bx) for bx in boxes):
                        problems.append("line end off any card edge: %s %s" % (l["n"], end))
                    if ai:
                        d = [d for d in dots if d["d"] == 8]
                        if len(d) != 1:
                            problems.append("AI line without exactly one 8px dot: " + l["n"])
                        else:
                            d = d[0]
                            if abs(d["cx"] - start[0]) > TOL or abs(d["cy"] - start[1]) > TOL:
                                problems.append("dot not on line start: %s dot %s start %s" % (l["n"], (d["cx"], d["cy"]), start))
                            # the dot touches (4 px outside) the source edge
                            if not any(on_edge((d["cx"] + dx, d["cy"] + dy), bx, 1.0) for bx in boxes for dx, dy in ((4, 0), (-4, 0), (0, 4), (0, -4))):
                                problems.append("dot does not touch a source edge: " + l["n"])
                    else:
                        rings = [d for d in dots if d["d"] == 10]
                        for pt in (start, end):
                            if not any(abs(r["cx"] - pt[0]) <= TOL and abs(r["cy"] - pt[1]) <= TOL for r in rings):
                                problems.append("ring missing on %s end %s" % (l["n"], pt))
                # title column clearance: leftmost point of the illustration on the page
                k = size[0] / (1440 + ex) if size[0] / size[1] > 1.6 else size[0] / 1440
                k = min(size[0] / (1440 + ex), size[1] / 900) if ex else min(size[0] / 1440, size[1] / 900)
                slot_left = 504 + ex
                xs = [bx["x"] for bx in res["boxes"] if not bx["n"].startswith("Portrait")]
                xs += [l["from"][0] for l in res["lines"]] + [l["to"][0] for l in res["lines"]]
                left_page = slot_left + min(xs)
                clear = left_page - 480
                if clear < 16:
                    problems.append("illustration starts %.0f px from the title column edge (480), nothing may be closer than 16" % clear)
                print("%-22s ex=%-5s clearance %-4.0f %s" % (tag, ex, clear, "OK" if not problems else "FAIL"))
                for pr in problems:
                    print("    -", pr)
                fails += len(problems)
                ctx.close()
    b.close()
print("problems:", fails)
