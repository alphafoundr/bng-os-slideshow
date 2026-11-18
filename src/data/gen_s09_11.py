"""Slides 09, 10, 11 from the Figma reads of 2026-11-17 (282:2212, 289:2470, 290:3066). Run: PYTHONPATH=. python -P src/data/gen_s09_11.py"""
from dsl import *
from desk import desktop_big

# ---------------- 09 · Buyer files with holes ----------------


def record_usage(x, ic, label):
    return {"x": x, "y": 19, "t": "F", "sh": "H", "h": 30, "n": "Used for · " + label,
            "f": [{"c": "background/neutral/subtle"}], "cr": 8,
            "lm": "H", "pad": [0, 10, 0, 10], "gap": 6, "ca": "c",
            "ch": [icon(ic, 16), T(label, "label/md", "text/neutral/bold", nw=1)]}


def record_finding(x, label, value):
    return {"x": x, "y": 68, "t": "F", "w": 142, "h": 58, "n": "Finding · " + label,
            "f": [{"c": "background/neutral/subtle"}], "cr": 8,
            "sk": {"c": "border/neutral/subtle"}, "sw": 1,
            "lm": "V", "pad": [7, 9, 7, 9], "gap": 2,
            "ch": [T(label, "label/tag", "text/neutral/subtle", nw=1),
                   T(value, "heading/xs", "text/neutral/bold", nw=1)]}


def field_status(x, present):
    label = "On file" if present else "Missing"
    fill = "background/neutral/subtle" if present else "background/danger/subtle"
    colour = "text/neutral/bold" if present else "text/danger/bold"
    return {"x": x, "y": 7, "t": "F", "sh": "H", "h": 23, "n": label, "cr": 4,
            "f": [{"c": fill}], "lm": "H", "pad": [0, 8, 0, 8], "ca": "c",
            "ch": [T(label, "label/tag", colour, nw=1)]}


def record_row(y, name, initials, image, fields, duplicate=False):
    avatar = portrait(image, size=28) if image else {
        "t": "F", "w": 28, "h": 28, "cr": 999, "f": [{"c": "background/neutral/subtle"}],
        "lm": "H", "pa": "c", "ca": "c",
        "ch": [T(initials, "label/sm", "text/neutral/bold", nw=1)]}
    children = [{"x": 8, "y": 4, **avatar},
                {"x": 45, "y": 8, **T(name, "label/md-strong", "text/neutral/bold", nw=1)}]
    children.extend(field_status(x, present) for x, present in zip((155, 270, 370), fields))
    if duplicate:
        children.append(tag("Duplicate", 474, 7, "Duplicate"))
    return {"x": 16, "y": y, "t": "F", "w": 592, "h": 37, "n": "Record · " + name,
            "sk": {"c": "border/neutral/subtle"}, "sw": [0, 0, 1, 0], "ch": children}


panel = [
    {"x": 16, "y": 12, **T("Client records", "heading/sm", "text/neutral/bold", nw=1)},
    {"x": 16, "y": 38, **T("975 in the finance app", "body/md", "text/neutral/subtle", nw=1)},
    record_usage(326, "file-text", "Every contract"),
    record_usage(467, "bell", "Every reminder"),
    record_finding(16, "ID number", "78% missing"),
    record_finding(166, "Email", "42% missing"),
    record_finding(316, "Phone", "38% missing"),
    record_finding(466, "Duplicate records", "at least 80"),
    {"x": 16, "y": 138, **T("Sample records", "heading/xs", "text/neutral/bold", nw=1)},
    *[{"x": x, "y": 165, **T(label, "label/sm", "text/neutral/subtle", nw=1)}
      for x, label in [(24, "Buyer"), (171, "ID no."), (286, "Email"), (386, "Phone"), (490, "Record status")]],
    record_row(186, "Amine A.", None, "e9061fc2", (False, True, False)),
    record_row(223, "Ilyas N.", None, "a4eba5b8", (True, False, True)),
    record_row(260, "Nabil R.", "NR", None, (False, True, True)),
    record_row(297, "Inès M.", "IM", None, (False, False, True), duplicate=True),
    record_row(334, "Inès M.", "IM", None, (False, False, True), duplicate=True),
]
at(1, *panel[:2])
for i, chip in enumerate(panel[2:8]):
    at(2, chip, motion="row", index=i)
at(4, *panel[8:14])
for i, row in enumerate(panel[14:]):
    at(5, row, motion="row", index=i)
s09 = slide("282:2212", "04 · What it costs · Buyer files with holes", "09 / 27", "What it costs", "Buyer files\nwith holes.",
            "The file is the base of every contract and of every reminder. Today most are incomplete.",
            "Figures read from the 975 client records on 13 November 2026. Illustration · fictional people", 4,
            [desktop_big("Device · Desktop · Buyer file", panel)])
s09["props"]["Big desktop"] = True
s09["props"]["Title width"] = 444  # Keeps the French title's second line together.
s09["props"]["Monochrome wordmark"] = True
dump("s09", s09)

# ---------------- 10 · One system, in BNG's name ----------------
CARD_W, CARD_H, CARD_X, CARD_Y = 248, 176, 326, 290
PERSONAS = [("Management", 112), ("Back office", 337), ("Sales advisers", 562), ("Buyers", 787)]
TOOLS = [(38, "Fame's CRM", "megaphone", "Fame", 66), (144, "Nexus Panthera", "users", "Nexus Panthera", 194),
         (278, "BNG Business", "coin", "BNG Business", 322), (422, "Vertex", "building", "Vertex", 450),
         (519, "BNG Sales Monitor", "bar-chart", "BNG Sales Monitor", 578), (678, "Synergy", "circle-ask", "Synergy", 706),
         (778, "my.bngimmo.com", "smartphone", "my.bngimmo.com", 834)]


def curve(name, x0, y0, x1, y1, colour, sw, dash, op=None, prefix="AI connector / "):
    """An S-curve from (x0,y0) to (x1,y1), leaving and arriving vertically."""
    x, y, w, h = min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0)
    ax, ay, bx, by = x0 - x, y0 - y, x1 - x, y1 - y
    my = (ay + by) / 2
    r = {"x": x, "y": y, "t": "V", "n": prefix + name, "w": w, "h": h, "sk": {"c": colour}, "sw": sw, "da": dash, "cap": "ROUND", "jn": "ROUND",
         "d": ["M %s %s C %s %s %s %s %s %s" % (ax, ay, ax, my, bx, my, bx, by)]}
    if op is not None:
        r["op"] = op
    return r


def dot(name, cx, cy, size, colour="background/signature/bold"):
    return {"x": cx - size / 2, "y": cy - size / 2, "cn": "Illo / AI node", "t": "F", "w": size, "h": size, "n": "AI node · " + name,
            "f": [{"c": colour}], "cr": 999, "kg": 1}


def build(variant):
    sign = {"cn": "Brand / Sign", "w": 48, "h": 48, "lg": 1, "vp": {"Product": "OS", "Size": "48", "Ink": "Full colour"}}
    card = {"x": CARD_X, "y": CARD_Y, "cn": "Illo / Hub panel", "t": "F", "w": CARD_W, "h": CARD_H, "n": "Hub panel · BNG OS",
            "f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 12, "lm": "V", "gap": 4,
            "pad": [28, 24, 28, 24], "pa": "c", "ca": "c",
            "ch": [sign, {"t": "F", "w": 8, "h": 8}, T("BNG OS", "heading/lg", "text/neutral/bold", sh="L", al="C"),
                   T("One system, one login", "body/md", "text/neutral/subtlest", sh="L", al="C")]}
    ch = [persona_v("Management", 28, 50, "e9061fc2", "Management", "Sees the whole group"),
          persona_v("Back office", 253, 50, "2a9ca040", "Back office", "Verifies and validates"),
          persona_v("Sales advisers", 478, 50, "5755e103", "Sales advisers", "Their leads and sales"),
          persona_v("Buyers", 703, 50, "4cad20ba", "Buyers", "Their own file")]
    lines, nodes = [], []
    hub_step = 4
    at(hub_step, card)
    top, bottom, mid = CARD_Y, CARD_Y + CARD_H, CARD_X + CARD_W / 2
    for i, (name, cx) in enumerate(PERSONAS):
        lx = mid + (i - 1.5) * 44
        lines.append(curve("BNG OS → " + name, cx, 182, lx, top, "border/neutral/default", 2, [6, 6], prefix="Connector / "))
        nodes.append(node(name, cx - 8, 174))
        step = hub_step + i
        at(step + 1, ch[i])
        draw(step, lines[-1], end=nodes[-1], target=ch[i], reverse=True)
    for i, (x, name, ic, label, cx) in enumerate(TOOLS):
        td = disc(name, 56, ic, 24)
        td["n"] = "Tool · " + name
        td["ch"] = [{"t": "F", "w": 56, "h": 56, "f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 999,
                     "lm": "H", "pa": "c", "ca": "c", "ch": [icon(ic, 24)]}, T(label, "label/md-strong", "text/neutral/bold", al="C", nw=1), relation_tag(label)]
        td["x"], td["y"] = x, 586
        ch.append(td)
        lx = mid + (i - 3) * 30
        if variant == "A":      # green 2 px, one 8 px dot at the tool
            lines.append(curve(name + " → BNG OS", cx, 586, lx, bottom, "border/signature/bold", 2, [6, 6]))
            nodes.append(dot(name, cx, 586, 8))
        elif variant == "B":    # the same green at half strength, one 8 px dot where it enters the card
            lines.append(curve(name + " → BNG OS", cx, 586, lx, bottom, "border/signature/bold", 2, [6, 6], op=0.5))
            nodes.append(dot("BNG OS · " + name, lx, bottom, 8))
        else:                   # C: grey lines like the ones above, green only as the dot at the card
            lines.append(curve(name + " → BNG OS", cx, 586, lx, bottom, "border/neutral/default", 2, [6, 6], prefix="Connector / "))
            nodes.append(dot("BNG OS · " + name, lx, bottom, 8))
        step = i // 2
        at(step, td)
        if variant == "A":
            draw(step, lines[-1], nodes[-1], target=card, arrival=hub_step)
        else:
            draw(step, lines[-1], end=nodes[-1], target=card, arrival=hub_step)
    ch += lines + [card] + nodes
    return slide("289:2470", "05 · One system · One system, in BNG's name · B", "10 / 27", "One system above the tools",
                 "One system,\nin BNG's name.", "One system that connects your tools and replaces Nexus Panthera. Accounts, code and data belong to BNG.",
                 "Illustrative · fictional people", 5, ch)


s10 = build("C")
dump("s10", s10)

# ---------------- 11 · One login, six views ----------------


def field(label, placeholder, eye=False):
    """Labelled input: label/md above a 40 px box (input fill, 1 px strong border, radius 8)."""
    box = {"t": "F", "sh": "L", "h": 40, "f": [{"c": "background/neutral/input"}], "sk": {"c": "border/neutral/bold"}, "sw": 1, "cr": 8, "k": 1,
           "lm": "H", "gap": 8, "pad": [0, 12, 0, 12], "ca": "c",
           "ch": [T(placeholder, "body/md", "text/neutral/placeholder", sh="L", nw=1)] + ([icon("eye", 20, "icon/neutral/subtlest")] if eye else [])}
    return {"t": "F", "sh": "L", "lm": "V", "gap": 6, "ch": [T(label, "label/md", "text/neutral/bold", sh="L"), box]}


screen = {"t": "F", "sh": "L", "sv": "L", "n": "Device screen / Sign in", "k": 1, "lm": "V", "gap": 28, "pad": [0, 0, 8, 0], "pa": "c", "ca": "c", "ch": [
    {"t": "F", "sh": "L", "lm": "V", "gap": 16, "ca": "c", "n": "Header", "ch": [
        {"cn": "Brand / Sign", "w": 48, "h": 48, "lg": 1, "vp": {"Product": "OS", "Size": "48", "Ink": "Full colour"}},
        {"t": "F", "sh": "L", "lm": "V", "gap": 4, "ch": [
            T("Sign in", "heading/md", "text/neutral/bold", sh="L", al="C"),
            T("One login for the whole group", "body/sm", "text/neutral/subtlest", sh="L", al="C")]}]},
    {"t": "F", "sh": "L", "lm": "V", "gap": 16, "n": "Form", "ch": [
        {"t": "F", "sh": "L", "lm": "V", "gap": 14, "ch": [field("Work email", "name@bngimmo.com"), field("Password", "••••••••", eye=True)]},
        {"t": "F", "sh": "L", "h": 40, "n": "Button · Sign in", "f": [{"c": "background/action/bold"}], "cr": 8, "lm": "H", "gap": 4,
         "pad": [0, 12, 0, 12], "pa": "c", "ca": "c", "ch": [T("Sign in", "label/md-strong", "text/on-action/bold", nw=1)]},
        T("Forgot password?", "label/md-strong", "text/neutral/bold", sh="L", al="C", td="UNDERLINE")]}]}
C1 = [[0.68, 0, 0.16], [0, 0.68, 0.13]]
C2 = [[0.72, 0, 0.14], [0, 0.72, 0.265]]
ch = [phone_shell("Device / Phone · Sign in", [screen]),
      persona_v("Management", 16, 64, "e9061fc2", "Management", "Sees the whole group"),
      persona_v("Sales advisers", 16, 298, "5755e103", "Sales advisers", "Their leads and sales"),
      persona_v("Construction", 16, 532, "dc262b77", "Construction", "Sites and snags", crop=C1),
      persona_v("Back office", 716, 64, "2a9ca040", "Back office", "Verifies and validates"),
      persona_v("Partners", 716, 298, "f0ed4c75", "Partners", "Only what concerns them", crop=C2),
      persona_v("Buyers", 716, 532, "4cad20ba", "Buyers", "Their own file"),
      conn("Management → login", 184, 130, 126, 120, "M 0 0 C 63 0 63 120 126 120"), node("Management", 176, 122), node("login · Management", 302, 242),
      conn("Sales advisers → login", 184, 364, 126, 0, "M 0 0 L 126 0", rounded=False), node("Sales advisers", 176, 356), node("login · Sales advisers", 302, 356),
      conn("Construction → login", 184, 478, 126, 120, "M 0 120 C 63 120 63 0 126 0"), node("Construction", 176, 590), node("login · Construction", 302, 470),
      conn("Back office → login", 590, 130, 126, 120, "M 0 120 C 63 120 63 0 126 0"), node("Back office", 708, 122), node("login · Back office", 582, 242),
      conn("Partners → login", 590, 364, 126, 0, "M 0 0 L 126 0", rounded=False), node("Partners", 708, 356), node("login · Partners", 582, 356),
      conn("Buyers → login", 590, 478, 126, 120, "M 0 0 C 63 0 63 120 126 120"), node("Buyers", 708, 590), node("login · Buyers", 582, 470)]
at(3, ch[0])
for i in range(6):
    step = i % 3
    at(step, ch[1 + i])
    draw(step, *ch[7 + 3 * i:10 + 3 * i], target=ch[0], arrival=3, reverse=i >= 3)
s11 = slide("290:3066", "05 · One system · One login, six views", "11 / 27", "One system above the tools", "One login.\nSix views.",
            "Each role sees its own part of the system.", "Illustrative · fictional people", 5, ch)
dump("s11", s11)
