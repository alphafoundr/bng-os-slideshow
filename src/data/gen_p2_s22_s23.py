"""Pause 'And when BNG needs something new?' and slides 22, 23 from the Figma reads of 2026-11-17 (332:5182, 498:5853, 321:4745).
Run: cd src/data && PYTHONPATH=. python -P gen_p2_s22_s23.py"""
from dsl import *
from desk import callout, desktop_big

# ---------------- pause · And when BNG needs something new? ----------------
studio_lockup = {"x": -468, "y": -36, "cn": "Brand / Product lockup", "t": "F", "w": 173, "h": 48, "n": "Lockup · Studio", "lm": "H", "gap": 12, "ca": "c",
                 "ch": [{"cn": "Brand / Sign", "w": 48, "h": 48, "lg": 1, "vp": {"Product": "Studio", "Size": "48", "Ink": "Full colour"}},
                        T("Studio", "heading/xl", "text/neutral/bold", nw=1)]}
p2 = {"id": "332:5182", "name": "09 · Studio · And when BNG needs something new (pause)",
      "props": {"Note": "Illustrative · fictional people and figures", "Lede": "A lede in one or two short lines.", "Show lede": False,
                "Eyebrow": "10 · Studio", "Title": "And when BNG needs\nsomething new?", "Show footer": False, "Show nav": True, "Show note": False,
                "Show title column": False, "Number": "01 / 27"},
      "nav": {"Chapter": "9"},
      "ch": [{"x": -468, "y": 421, **T("And when BNG needs\nsomething new?", "display/xl", "text/neutral/bold", w=1368)},
             {"x": -468, "y": 717, **T("You should not have to call us.", "body/lede-lg", "text/neutral/subtle", w=900)},
             studio_lockup]}
dump("p2", p2)

# ---------------- 22 · You ask. It gets built. ----------------


def rail_sel(label, ic, selected):
    c = "bold" if selected else "subtle"
    r = {"cn": "App / Navigation / Rail item", "t": "F", "sh": "L", "sv": "H", "n": "Rail item / " + label}
    if selected:
        r.update({"f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1})
    r.update({"cr": 8, "lm": "V", "gap": 4, "pad": [8, 4, 8, 4], "pa": "c", "ca": "c",
              "ch": [icon(ic, 24, "icon/neutral/" + c), T(label, "label/sm", "text/neutral/" + c, al="C", nw=1)]})
    return r


def check(text):
    return {"cn": "App / Studio / Check row", "t": "F", "sh": "L", "sv": "H", "n": "Check / " + text, "sk": {"c": "border/neutral/subtle"}, "sw": [0, 0, 1, 0],
            "lm": "H", "gap": 12, "pad": [12, 0, 12, 0],
            "ch": [{"t": "F", "w": 24, "h": 24, "f": [{"c": "background/success/subtle"}], "cr": 999, "k": 1, "lm": "H", "pa": "c", "ca": "c",
                    "ch": [icon("checkmark", 14, "icon/success/bold")]},
                   {"t": "F", "sh": "L", "sv": "H", "k": 1, "lm": "V", "gap": 2, "ch": [T(text, "label/md-strong", "text/neutral/bold", sh="L")]}]}


def prow(name, text, selected=False, tail=None):
    r = {"cn": "App / Navigation / Panel row", "t": "F", "sh": "L", "h": 32, "n": name}
    if selected:
        r["f"] = [{"c": "background/neutral/muted"}]
    r.update({"cr": 8, "lm": "H", "gap": 8, "pad": [0, 12, 0, 12], "ca": "c"})
    r["ch"] = [T(text, "label/md-strong" if selected else "body/sm", "text/neutral/bold" if selected else "text/neutral/subtle", sh="L")]
    if tail:
        r["ch"].append(T(tail, "label/sm", "text/neutral/subtlest", nw=1))
    return r


rail = {"t": "F", "sv": "L", "w": 88, "f": [{"c": "background/neutral/rail"}], "sk": {"c": "border/neutral/subtle"}, "sw": [0, 1, 0, 0], "k": 1, "lm": "V", "gap": 4,
        "pad": [12, 8, 12, 8], "ca": "c",
        "ch": [{"t": "F", "sh": "L", "h": 40, "k": 1, "lm": "H", "pa": "c", "ca": "c",
                "ch": [{"cn": "Brand / Sign", "w": 24, "h": 24, "lg": 1, "vp": {"Product": "Studio", "Size": "24", "Ink": "Full colour"}}]},
               rail_sel("Requests", "document", True), rail_sel("Live", "circle-checkmark", False)]}
status = {"cn": "App / Data display / Status tag", "t": "F", "sh": "H", "sv": "H", "n": "Status tag · All passed", "f": [{"c": "background/success/subtle"}], "cr": 4,
          "lm": "H", "gap": 4, "pad": [2, 8, 2, 8], "ca": "c",
          "ch": [icon("circle-checkmark", 12, "icon/success/bold"), T("All passed", "label/tag", "text/success/bold", nw=1)]}
checks_col = {"t": "F", "sv": "H", "w": 252, "k": 1, "lm": "V", "gap": 4,
              "ch": [{"t": "F", "sh": "L", "sv": "H", "k": 1, "lm": "H", "gap": 8, "ca": "c", "ch": [T("Checks", "label/md-strong", "text/neutral/subtlest", nw=1), status]},
                     check("Source tools stay read-only"), check("Only sales managers can open it"), check("Test run on last Monday’s data"),
                     check("Matches what you asked for")]}
where_col = {"t": "F", "sh": "L", "sv": "H", "k": 1, "lm": "V", "gap": 8,
             "ch": [{"t": "F", "sh": "L", "sv": "H", "k": 1, "lm": "H", "ca": "c", "ch": [T("Where it appears in BNG OS", "label/md-strong", "text/neutral/subtlest", nw=1)]},
                    {"t": "F", "sh": "L", "sv": "H", "f": [{"c": "background/neutral/subtle"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 8, "k": 1, "lm": "V",
                     "gap": 2, "pad": [8, 8, 8, 8],
                     "ch": [T("Reports", "body/xs", "text/neutral/subtlest", nw=1), prow("Row / Sales", "Sales"), prow("Row / Cash", "Cash"),
                            prow("Row / Unsold lots", "Unsold lots", True, "New")]}]}
main = {"t": "F", "sh": "L", "sv": "L", "k": 1, "lm": "V", "gap": 16, "pad": [16, 16, 16, 0],
        "ch": [{"t": "F", "sh": "L", "sv": "H", "k": 1, "lm": "V", "gap": 4,
                "ch": [T("Unsold-lots report", "heading/sm", "text/neutral/bold", nw=1),
                       T("Weekly, by project · every check has passed", "body/md", "text/neutral/subtlest", nw=1)]},
               {"t": "F", "sh": "L", "sv": "L", "k": 1, "lm": "H", "gap": 24, "ch": [checks_col, where_col]},
               {"t": "F", "sh": "L", "sv": "H", "k": 1, "lm": "H", "gap": 12, "ca": "c",
                "ch": [T("Nothing goes live until you approve.", "body/xs", "text/neutral/subtlest", sh="L"),
                       {"cn": "App / Actions / Button", "t": "F", "sh": "H", "h": 32, "n": "Send back", "f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"},
                        "sw": 1, "cr": 8, "lm": "H", "gap": 4, "pad": [0, 12, 0, 12], "pa": "c", "ca": "c", "ch": [T("Send back", "label/md", "text/neutral/bold", nw=1)]},
                       {"cn": "App / Actions / Button", "t": "F", "sh": "H", "h": 32, "n": "Go live", "f": [{"c": "background/action/bold"}], "cr": 8, "lm": "H", "gap": 4,
                        "pad": [0, 12, 0, 12], "pa": "c", "ca": "c", "ch": [T("Go live", "label/md-strong", "text/on-action/bold", nw=1)]}]}]}
fallback = {"x": 0, "y": 0, "t": "F", "w": 624, "h": 384, "k": 1, "lm": "H", "gap": 16, "ch": [rail, main]}
device = desktop_big("Device · Desktop · Studio go live", [fallback])
asked = callout(1, "A", "Asked in plain words", "“A weekly report of unsold lots, by project.”", "Asked in plain words → device")
live = callout(3, "C", "Live in BNG OS", "Under Reports, for the sales managers. Code and data stay with BNG.",
               "device → Live in BNG OS", source="device")
# Keep the existing FR sentences inside the two side-attached cards.
asked[0].update(h=98, gap=8, pad=[12, 16, 12, 16])
live[0].update(h=108, gap=8, pad=[12, 16, 12, 16])
s22 = slide("498:5853", "09 · Studio · You ask, it gets built (22 B)", "21 / 27", "Studio", "You ask.\nIt gets built.",
            "BNG describes the need in plain words. The system plans it, builds it and tests it. BNG puts it live.",
            "Illustrative example · fictional people and figures", 9, [device, *asked, *live])
s22["props"]["Big desktop"] = True
dump("s22", s22)

# ---------------- 23 · It stays yours. It keeps growing. ----------------


def own_card(name, x, ic, title, tag_text):
    return {"x": x, "y": 32, "cn": "Illo / UI card", "t": "F", "sv": "H", "w": 256, "n": "UI card · " + name, "f": [{"c": "background/neutral/raised"}],
            "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 12, "lm": "V", "gap": 12, "pad": [16, 16, 16, 16],
            "ch": [{"t": "F", "sh": "L", "sv": "H", "lm": "H", "gap": 8, "ca": "c", "ch": [icon(ic, 20), T(title, "heading/xs", "text/neutral/bold", sh="L")]},
                   {"cn": "Illo / Tag", "t": "F", "sh": "H", "sv": "H", "n": "Tag", "f": [{"c": "background/neutral/tag"}], "cr": 4, "lm": "H", "pad": [2, 8, 2, 8], "pa": "c",
                    "ca": "c", "ch": [T(tag_text, "label/tag", "text/neutral/bold", nw=1)]}]}


hub23 = {"x": 318, "y": 232, "cn": "Illo / Hub panel", "t": "F", "sv": "H", "w": 264, "n": "Hub panel · BNG OS", "f": [{"c": "background/neutral/subtle"}],
         "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 12, "lm": "V", "gap": 8, "pad": [20, 20, 20, 20], "pa": "c", "ca": "c",
         "ch": [T("BNG OS", "heading/md", "text/neutral/bold", sh="L", al="C"), T("In BNG's name", "body/md", "text/neutral/subtlest", sh="L", al="C")]}
tools = [("Fame's CRM", 32, "megaphone", "Fame"), ("Nexus Panthera", 140, "users", "Nexus Panthera"), ("BNG Business", 275.5, "coin", "BNG Business"),
         ("Vertex", 422, "building", "Vertex"), ("BNG Sales Monitor", 521, "bar-chart", "BNG Sales Monitor"), ("Synergy", 682, "circle-ask", "Synergy"),
         ("my.bngimmo.com", 784, "smartphone", "my.bngimmo.com")]
fans = [(60, 282, "M 282 0 C 282 48 0 48 0 96"), (190, 188, "M 188 0 C 188 48 0 48 0 96"), (320, 94, "M 94 0 C 94 48 0 48 0 96"), (450, 0, "M 0 0 L 0 96"),
        (486, 94, "M 0 0 C 0 48 94 48 94 96"), (522, 188, "M 0 0 C 0 48 188 48 188 96"), (558, 282, "M 0 0 C 0 48 282 48 282 96")]
list_row = {"x": 270, "y": 596, "cn": "Illo / List row", "t": "F", "w": 360, "h": 56, "n": "List row · Every correction makes it sharper", "lm": "H", "gap": 12, "ca": "c",
            "ch": [disc("Tool disc", 56, "pen", 24),
                   {"t": "F", "sh": "L", "sv": "H", "lm": "V", "gap": 2, "ch": [T("Every correction makes it sharper", "heading/xs", "text/neutral/bold", sh="L")]}]}
list_row["ch"][0]["n"] = "Tool disc"
ch = [{"x": 0, "y": 0, **T("Owned by BNG", "eyebrow/md", "text/neutral/subtlest", tc="UPPER", nw=1)},
      own_card("Code", 0, "code", "Code", "In BNG's repository"), own_card("Accounts", 322, "user", "Accounts", "Opened in BNG's name"),
      own_card("Data", 644, "database", "Data", "In BNG's database"), hub23]
for name, x, ic, label in tools:
    t = tool(name, x, 424, ic, label)
    ch.append(t)
ch += [conn("Code → BNG OS", 128, 120, 232, 112, "M 0 0 C 0 56 232 56 232 112"), node("Code", 120, 112), node("BNG OS · Code", 352, 224),
       conn("Accounts → BNG OS", 450, 120, 0, 112, "M 0 0 L 0 112"), node("Accounts", 442, 112), node("BNG OS · Accounts", 442, 224),
       conn("Data → BNG OS", 540, 120, 232, 112, "M 232 0 C 232 56 0 56 0 112"), node("Data", 764, 112), node("BNG OS · Data", 532, 224)]
for (x, w, d), (name, _, _, _) in zip(fans, tools):
    ch.append(conn("BNG OS → " + name, x, 328, w, 96, d, rounded=False))
ch.append({"x": 330, "y": 527, **T("The tools BNG already has", "eyebrow/md", "text/neutral/subtlest", tc="UPPER", nw=1)})
ch.append(list_row)
for i, (name, _, _, _) in enumerate(tools):
    ch.append(node("BNG OS · " + name, 334 + 36 * i, 320))
for (name, x, _, _), nx in zip(tools, (52, 182, 312, 442, 572, 702, 832)):
    ch.append(node(name, nx, 416))
ch.append({"x": 381, "y": 254, "cn": "Brand / Sign", "w": 24, "h": 24, "lg": 1, "vp": {"Product": "OS", "Size": "24", "Ink": "Full colour"}})
at(0, ch[0])
at(3, hub23, ch[-1])
for i in range(3):
    at(i, ch[1 + i])
    start = 12 + i * 3
    draw(i, *ch[start:start + 3], target=hub23, arrival=3)
at(4, ch[28])
for i in range(7):
    step = 4 + i // 2
    at(step + 1, ch[5 + i])
    draw(step, ch[21 + i], ch[30 + i], ch[37 + i], target=ch[5 + i])
at(9, list_row)
s23 = slide("321:4745", "12 · It is yours · It stays yours, it keeps growing", "25 / 27", "Ownership", "It stays yours.\nIt keeps growing.",
            "Accounts, code and data belong to BNG. It keeps growing with every request and every correction.", "Illustrative · fictional people and figures", 12, ch)
s23["props"]["Show note"] = False
dump("s23", s23)
