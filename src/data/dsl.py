"""Helpers that write the compact Figma-record JSON (see render.py) for repeated structures.
Every value comes from a Figma read taken the day the slide was built (2026-11-17); the slide scripts gen_sNN.py hold them."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CROP = [[0.74, 0, 0.13], [0, 0.74, 0.02]]


def T(c, s, col, **kw):
    d = {"t": "T", "c": c, "f": {"c": col}, "s": s}
    d.update(kw)
    return d


def node(name, x, y):
    return {"x": x + 3, "y": y + 3, "cn": "Illo / Node", "t": "F", "w": 10, "h": 10, "n": "Node · " + name,
            "f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/bold"}, "sw": 1.5, "cr": 999, "kg": 1}


def at(step, *parts, motion="part", **options):
    """Schedule parts without changing their layout or stacking order."""
    for part in parts:
        part["seq"] = {"step": step, "motion": motion, **options}
    return parts[0] if len(parts) == 1 else list(parts)


def draw(step, line, start=None, end=None, *, target=None, arrival=None, reverse=False, via=()):
    """Schedule a connector, its endpoint marks and an optional shared arrival."""
    arrival = step + 1 if arrival is None else arrival
    at(step, line, motion="draw", arrival=arrival, reverse=reverse,
       target=target["n"] if target else "", via=[(beat, fraction, part["n"]) for beat, fraction, part in via])
    if start:
        at(step, start, motion="dot")
    if end:
        at(arrival, end, motion="end")
    return line


def conn(name, x, y, w, h, d, rounded=True):
    r = {"x": x, "y": y, "t": "V", "n": "Connector / " + name, "w": w, "h": h, "sk": {"c": "border/neutral/default"}, "sw": 2, "da": [6, 6]}
    if rounded:
        r.update({"cap": "ROUND", "jn": "ROUND"})
    r["d"] = [d]
    return r


def annotation(name, x, y, text):
    return {"x": x, "y": y, "cn": "Illo / Annotation", "t": "F", "sh": "H", "sv": "H", "n": "Annotation · " + name,
            "f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 8, "lm": "H",
            "pad": [4, 12, 4, 12], "pa": "c", "ca": "c", "kg": 1, "ch": [T(text, "label/tag", "text/neutral/bold", nw=1)]}


def stat(name, x, y, w, fig, label):
    """Illo / Stat card, 218 wide, figure/md over body/md."""
    return {"x": x, "y": y, "cn": "Illo / Stat", "t": "F", "sv": "H", "w": w, "n": "Stat · " + name,
            "f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 12, "lm": "V", "gap": 6,
            "pad": [24, 24, 24, 24],
            "ch": [T(fig, "figure/md", "text/neutral/bold", nw=1), T(label, "body/md", "text/neutral/subtlest", nw=1)]}


def stat_bare(name, x, y, fig, label, fs="figure/xl", ls="body/lg"):
    return {"x": x, "y": y, "cn": "Illo / Stat", "t": "F", "sh": "H", "sv": "H", "n": "Stat · " + name, "lm": "V", "gap": 6,
            "ch": [T(fig, fs, "text/neutral/bold", nw=1), T(label, ls, "text/neutral/subtlest", nw=1)]}


def kv(label, value, vcol="text/neutral/bold"):
    return {"t": "F", "sh": "L", "sv": "H", "f": [{"c": "background/neutral/subtle"}], "cr": 8, "lm": "H", "gap": 8, "pad": [6, 8, 6, 8],
            "pa": "s", "ca": "c",
            "ch": [T(label, "body/sm", "text/neutral/subtlest", nw=1), T(value, "label/md-strong", vcol, nw=1)]}


def icon(name, size, col="icon/neutral/bold"):
    return {"cn": name, "ic": name, "w": size, "h": size, "f": {"c": col}}


def ui_card(name, x, y, w, ic, title, sub, rows, ic_col="icon/neutral/bold"):
    return {"x": x, "y": y, "cn": "Illo / UI card", "t": "F", "sv": "H", "w": w, "n": "UI card · " + name,
            "f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 12, "lm": "V", "gap": 12,
            "pad": [16, 16, 16, 16],
            "ch": [{"t": "F", "sh": "L", "sv": "H", "lm": "H", "gap": 8, "ca": "c",
                    "ch": [icon(ic, 20, ic_col), T(title, "heading/xs", "text/neutral/bold", sh="L")]},
                   T(sub, "body/sm", "text/neutral/subtlest", sh="L"),
                   {"t": "F", "sh": "L", "sv": "H", "lm": "V", "gap": 6, "ch": rows}]}


def portrait(h, name="Portrait", size=48, sw=1, crop=CROP):
    return {"cn": "Illo / Portrait", "t": "F", "w": size, "h": size, "n": name, "f": [{"im": h, "sm": "CROP", "tr": crop}],
            "sk": {"c": "border/neutral/subtle"}, "sw": sw, "cr": 999, "k": 1}


def persona_h(name, x, y, w, h, title, sub):
    return {"x": x, "y": y, "cn": "Illo / Persona card", "t": "F", "sv": "H", "w": w, "n": "Persona · " + name,
            "f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 12, "lm": "H", "gap": 12,
            "pad": [12, 12, 12, 12], "ca": "c",
            "ch": [portrait(h), {"t": "F", "sh": "L", "sv": "H", "lm": "V", "gap": 2,
                                 "ch": [T(title, "heading/xs", "text/neutral/bold", sh="L"), T(sub, "body/xs", "text/neutral/subtlest", sh="L")]}]}


def persona_v(name, x, y, h, title, sub, crop=CROP):
    """Vertical persona card, 168 wide."""
    return {"x": x, "y": y, "cn": "Illo / Persona card", "t": "F", "sv": "H", "w": 168, "n": "Persona · " + name,
            "f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 12, "lm": "V", "gap": 12,
            "pad": [16, 12, 16, 12], "ca": "c",
            "ch": [portrait(h, crop=crop), {"t": "F", "sh": "L", "sv": "H", "lm": "V", "gap": 2, "ca": "c",
                                            "ch": [T(title, "heading/xs", "text/neutral/bold", sh="L", al="C"),
                                                   T(sub, "body/xs", "text/neutral/subtlest", sh="L", al="C")]}]}


def disc(name, size, ic, ic_size):
    return {"cn": "Illo / Tool disc", "t": "F", "sh": "H", "sv": "H", "n": "Tool disc · " + name, "lm": "V", "gap": 8, "ca": "c",
            "ch": [{"t": "F", "w": size, "h": size, "f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1,
                    "cr": 999, "lm": "H", "pa": "c", "ca": "c", "ch": [icon(ic, ic_size)]}]}


def ai_node(name, x, y):
    return {"x": x + 4, "y": y + 4, "cn": "Illo / AI node", "t": "F", "w": 8, "h": 8, "n": "AI node · " + name,
            "f": [{"c": "background/signature/bold"}], "cr": 999, "kg": 1}


def ai_conn(name, x, y, w, h, d):
    return {"x": x + 4, "y": y + 4, "t": "V", "n": "AI connector / " + name, "w": w, "h": h, "sk": {"c": "border/signature/bold"}, "sw": 2,
            "da": [6, 6], "cap": "ROUND", "jn": "ROUND", "d": [d]}


def phone_shell(name, inner):
    """Illo / Device · Phone 280x574 with status bar; inner is the 264x558 screen content list."""
    return {"x": 310, "y": 77, "cn": "Illo / Device · Phone", "t": "F", "w": 280, "h": 574, "n": name, "f": [{"c": "background/inverse/bold"}], "cr": 40,
            "ch": [{"x": 8, "y": 8, "t": "F", "w": 264, "h": 558, "f": [{"c": "background/neutral/raised"}], "cr": 40, "k": 1, "lm": "V", "gap": 12,
                    "pad": [48, 16, 24, 16], "ch": inner},
                   {"x": 100, "y": 16, "t": "R", "w": 80, "h": 22, "f": [{"c": "background/inverse/bold"}], "cr": 999},
                   {"x": 32, "y": 16, **T("9:41", "label/md-strong", "text/neutral/bold", nw=1)},
                   {"x": 226, "y": 20, "t": "F", "w": 22, "h": 11, "sk": {"c": "border/inverse/bold"}, "sw": 1, "cr": 4, "k": 1,
                    "ch": [{"x": 2, "y": 2, "t": "R", "w": 14, "h": 7, "f": [{"c": "background/inverse/bold"}], "cr": 4}]},
                   {"x": 92, "y": 552, "t": "R", "w": 96, "h": 4, "f": [{"c": "background/inverse/bold"}], "cr": 999}]}


def marker(size, x=None, y=None):
    """App / Cortex / Marker: the corner glyph and the green dot (explicit numbers from Figma for 14 and 16, scaled from 16 for 48)."""
    if size == 14:
        gx, gw, gh, gp, dx, dy, dd = 1.5, 9.5, 7.01, "NONZERO M 0 0 L 9.5 0 L 9.5 2.7 L 2.7 2.7 L 2.7 7.01 L 0 7.01 L 0 0 Z", 1.5, 9.01, 4.99
    elif size == 16:
        gx, gw, gh, gp, dx, dy, dd = 2, 10, 8.23, "NONZERO M 0 0 L 10 0 L 10 3 L 3 3 L 3 8.23 L 0 8.23 L 0 0 Z", 2, 10.46, 5.54
    else:  # 48, as in the Deck lockup
        gx, gw, gh, gp, dx, dy, dd = 6, 30, 24.7, "NONZERO M 0 0 L 30 0 L 30 9 L 9 9 L 9 24.7 L 0 24.7 L 0 0 Z", 6, 31.37, 16.63
    m = {"cn": "App / Cortex / Marker", "t": "F", "w": size, "h": size, "n": "Marker",
         "ch": [{"x": gx, "y": 0, "t": "V", "n": "Glyph / corner", "w": gw, "h": gh, "f": {"c": "icon/neutral/bold"}, "d": [gp]},
                {"x": dx, "y": dy, "t": "E", "w": dd, "h": dd, "f": [{"c": "icon/signature/bold"}]}]}
    if x is not None:
        m["x"], m["y"] = x, y
    return m


def cortex_lockup(x, y):
    return {"x": x, "y": y, "cn": "Brand / Product lockup", "t": "F", "w": 177, "h": 48, "n": "Lockup · Cortex", "lm": "H", "gap": 12, "ca": "c",
            "ch": [{"t": "F", "w": 48, "h": 48, "n": "Sign", "ch": [marker(48, 0, 0)]},
                   T("Cortex", "heading/xl", "text/neutral/bold", nw=1)]}


def hub(name, x, y, w, sub):
    return {"x": x, "y": y, "cn": "Illo / Hub panel", "t": "F", "w": w, "h": 200, "n": "Hub panel · " + name, "f": [{"c": "background/neutral/subtle"}],
            "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 12, "lm": "V", "gap": 8, "pad": [20, 20, 20, 20], "pa": "c", "ca": "c",
            "ch": [marker(16), T(name, "heading/md", "text/neutral/bold", sh="L", al="C"), T(sub, "body/md", "text/neutral/subtlest", sh="L", al="C")]}


def suggestion(name, x, y, title, sub, label="Suggested by Cortex", dashed=True):
    c = {"x": x, "y": y, "cn": "App / Cortex / Suggestion card", "t": "F", "sv": "H", "w": 360, "n": "Suggestion · " + name,
         "f": [{"c": "background/neutral/suggested"}], "sk": {"c": "border/neutral/suggested"}, "sw": 1}
    if dashed:
        c["da"] = [6, 4]
    c.update({"cr": 12, "lm": "V", "gap": 12, "pad": [16, 16, 16, 16], "ch": [
        {"cn": "App / Cortex / Suggestion label", "t": "F", "sh": "H", "sv": "H", "n": "App / Cortex / Suggestion label",
         "f": [{"c": "background/neutral/subtle"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 4, "lm": "H", "gap": 4,
         "pad": [4, 8, 4, 6], "ca": "c", "ch": [marker(14), T(label, "label/tag", "text/neutral/subtle", nw=1)]},
        T(title, "heading/xs", "text/neutral/bold", sh="L"), T(sub, "body/md", "text/neutral/subtle", sh="L")]})
    return c


def tag(name, x, y, text, kind="tag"):
    t = {"x": x, "y": y, "cn": "Illo / Tag", "t": "F", "sh": "H", "sv": "H", "n": "Tag · " + name}
    if kind == "dashed":
        t.update({"sk": {"c": "border/neutral/bold"}, "sw": 1, "da": [4, 3]})
        col = "text/neutral/subtlest"
    elif kind == "success":
        t["f"] = [{"c": "background/success/subtle"}]
        col = "text/success/bold"
    elif kind == "bold":    # the one tag that must be read first, e.g. the tool BNG OS replaces
        t["f"] = [{"c": "background/action/bold"}]
        col = "text/on-action/bold"
    else:
        t["f"] = [{"c": "background/neutral/tag"}]
        col = "text/neutral/bold"
    t.update({"cr": 4, "lm": "H", "pad": [2, 8, 2, 8], "pa": "c", "ca": "c", "ch": [T(text, "label/tag", col, nw=1)]})
    return t


# What BNG OS does with each existing tool (Khalid, 2026-11-18: "make it clear we're replacing Nexus Panthera in the links to BNG OS";
# "replaces" and "integrates"). Only Nexus Panthera is marked replaced; the others are the orchestrating session's default, his to change.
REPLACED = {"Nexus Panthera"}


def relation_tag(tool_name):
    replaced = tool_name in REPLACED
    t = tag("Relation · " + tool_name, 0, 0, "Replaces" if replaced else "Integrates", "bold" if replaced else "tag")
    del t["x"], t["y"]
    return t


def tool(name, x, y, ic, label):
    td = disc(name, 56, ic, 24)
    td["n"] = "Tool · " + name
    td["ch"].append(T(label, "label/md-strong", "text/neutral/bold", al="C", nw=1))
    td["x"], td["y"] = x, y
    return td


def ai_conn_plain(name, x, y, w, h, d, rounded=False):
    c = ai_conn(name, x, y, w, h, d)
    if not rounded:
        del c["cap"], c["jn"]
    return c


def slide(sid, name, num, eyebrow, title, lede, note, chapter, ch):
    return {"id": sid, "name": name,
            "props": {"Show title column": True, "Number": num, "Show nav": True, "Show note": True, "Note": note, "Lede": lede,
                      "Show lede": True, "Show footer": True, "Title": title, "Eyebrow": eyebrow},
            "nav": {"Chapter": str(chapter)}, "ch": ch}


def dump(key, data):
    with open(os.path.join(HERE, key + ".json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(key + ".json", len(data["ch"]), "records")
