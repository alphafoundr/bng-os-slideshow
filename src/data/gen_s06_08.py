"""Slides 06, 07, 08 from the Figma reads of 2026-11-17 (279:1890, 279:2074, 281:2072). Run: python -P src/data/gen_s06_08.py"""
from dsl import *

# ---------------- 06 · 800 reminders. None arrived. ----------------
muted = {"c": "background/neutral/muted"}


def bar(x, y, w, h, fill, cr):
    return {"x": x, "y": y, "t": "R", "w": w, "h": h, "f": [{"c": fill}], "cr": cr}


inbox = {"t": "F", "w": 232, "h": 480, "ch": [
    {"x": 0, "y": 0, **portrait("4cad20ba", "Portrait · The buyer", 32)},
    {"x": 44, "y": 0, **T("Inbox", "heading/sm", "text/neutral/bold", nw=1)},
    {"x": 44, "y": 18, **T("The buyer's email", "body/xs", "text/neutral/subtlest", nw=1)},
    bar(0, 52, 232, 52, "background/neutral/subtle", 8), bar(12, 65, 64, 6, "background/neutral/muted", 999), bar(12, 83, 148, 6, "background/neutral/muted", 999),
    bar(0, 116, 232, 52, "background/neutral/subtle", 8), bar(12, 129, 64, 6, "background/neutral/muted", 999), bar(12, 147, 148, 6, "background/neutral/muted", 999),
    {"x": 88, "y": 236, "cn": "Illo / Tool disc", "t": "F", "sh": "H", "sv": "H", "n": "Tool disc · Empty inbox", "lm": "V", "gap": 8, "ca": "c",
     "ch": [{"t": "F", "w": 56, "h": 56, "f": [{"c": "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 999,
             "lm": "H", "pa": "c", "ca": "c", "ch": [icon("mail", 24)]}]},
    {"x": 128, "y": 228, "cn": "Illo / Badge", "t": "F", "w": 24, "h": 24, "n": "Badge · Nothing arrived", "cr": 999, "lm": "H", "pa": "c", "ca": "c",
     "ch": [icon("triangle-warning", 16, "icon/danger/bold")]},
    {"x": 0, "y": 306, **T("Nothing from BNG", "heading/xs", "text/neutral/bold", w=232, al="C")},
    {"x": 0, "y": 327, **T("No reminder received", "body/xs", "text/neutral/subtlest", w=232, al="C")},
]}
phone = {"x": 310, "y": 77, "cn": "Illo / Device · Phone", "t": "F", "w": 280, "h": 574, "n": "Device · Phone · Buyer inbox",
         "f": [{"c": "background/inverse/bold"}], "cr": 40, "ch": [
    {"x": 8, "y": 8, "t": "F", "w": 264, "h": 558, "f": [{"c": "background/neutral/raised"}], "cr": 40, "k": 1, "lm": "V", "gap": 12,
     "pad": [48, 16, 24, 16], "ch": [inbox]},
    {"x": 100, "y": 16, "t": "R", "w": 80, "h": 22, "f": [{"c": "background/inverse/bold"}], "cr": 999},
    {"x": 32, "y": 16, **T("9:41", "label/md-strong", "text/neutral/bold", nw=1)},
    {"x": 226, "y": 20, "t": "F", "w": 22, "h": 11, "sk": {"c": "border/inverse/bold"}, "sw": 1, "cr": 4, "k": 1,
     "ch": [{"x": 2, "y": 2, "t": "R", "w": 14, "h": 7, "f": [{"c": "background/inverse/bold"}], "cr": 4}]},
    {"x": 92, "y": 552, "t": "R", "w": 96, "h": 4, "f": [{"c": "background/inverse/bold"}], "cr": 999},
]}
s06 = slide("279:1890", "04 · What it costs · 800 reminders, none arrived", "06 / 27", "What it costs", "800 reminders.\nNone arrived.",
            "Prepared on 13 November: 0 of 800 reminders reached a buyer. The team chases by hand, late.",
            "Illustrative · fictional buyer. Figures read from the finance app on 13 November 2026.", 4, [
    conn("800 → phone", 238, 300, 72, 0, "M 0 0 L 72 0"),
    conn("phone → 0 reached", 590, 181, 72, 49, "M 0 49 C 36 49 36 0 72 0"),
    conn("phone → 77 follow-ups", 590, 430, 72, 71, "M 0 0 C 36 0 36 71 72 71"),
    phone,
    stat("800 reminders prepared", 20, 219, 218, "800", "reminders prepared\non 13 November"),
    stat("0 reached a buyer", 662, 110, 218, "0", "reached a buyer"),
    stat("77 follow-ups typed by hand", 662, 420, 218, "77", "follow-ups typed by hand\nsince October"),
    node("800", 230, 292), node("phone left", 302, 292), node("phone right top", 582, 222), node("0 reached", 654, 173),
    node("phone right bottom", 582, 422), node("77 follow-ups", 654, 493),
])
dump("s06", s06)

# ---------------- 07 · What is owed? It depends who counts. ----------------
s07 = slide("279:2074", "04 · What it costs · What is owed, it depends who counts", "07 / 27", "What it costs", "What is owed?\nIt depends\nwho counts.",
            "Two ways of counting, two answers. And 80 payments match no lot: no single figure management can trust.",
            "Overdue amount on 13 November 2026, by two methods found in the same tool.", 4, [
    conn("gap → 80 payments", 442, 230, 0, 189, "M 0 0 L 0 189"),
    stat_bare("93M by recorded stage", 0, 161, "93M", "MAD, by the stage recorded on each sale"),
    stat_bare("147M by payment schedule", 620, 161, "147M", "MAD, by the payment schedule"),
    conn("93M ↔ 147M", 275, 230, 333, 0, "M 0 0 L 333 0"),
    node("93M edge", 267, 222), node("147M edge", 600, 222),
    ui_card("80 payments not linked", 314, 419, 256, "money", "80 payments", "not linked to any sale", [kv("Amount", "MAD 10.8M")]),
    annotation("54M apart", 384, 216, "MAD 54M apart"),
    node("80 payments top", 434, 411),
])
dump("s07", s07)

# ---------------- 08 · One sale, typed twice. ----------------
s08 = slide("281:2072", "04 · What it costs · One sale, typed twice", "08 / 27", "What it costs", "One sale,\ntyped twice.",
            "The same sale is typed twice, and the two versions drift apart. Nobody knows which one is right.",
            "Illustrative example · fictional people and figures", 4, [
    conn("adviser → CRM card", 128, 114, 0, 36, "M 0 0 L 0 36"),
    conn("back office → finance card", 772, 114, 0, 36, "M 0 0 L 0 36"),
    conn("CRM card → finance card", 256, 251, 388, 0, "M 0 0 L 388 0"),
    ui_card("Nexus Panthera · Sale", 0, 150, 256, "users", "Nexus Panthera", "Sale · Lot B-214",
            [kv("Agreed price", "1,250,000 MAD"), kv("Second buyer", "not filled"), kv("ID document", "photo")]),
    ui_card("BNG Business · Sale", 644, 150, 256, "coin", "BNG Business", "Sale · Lot B-214",
            [kv("Agreed price", "1,235,000 MAD"), kv("Second buyer", "filled"), kv("ID document", "checked scan")]),
    ui_card("Which one is right", 322, 470, 256, "warning", "Which one is right?", "15,000 MAD apart",
            [kv("CRM", "1,250,000 MAD"), kv("Finance app", "1,235,000 MAD")], ic_col="icon/danger/bold"),
    conn("CRM card → answer", 128, 352, 194, 200.5, "M 0 0 C 0 150.38 48.5 200.5 194 200.5"),
    conn("finance card → answer", 578, 352, 194, 200.5, "M 194 0 C 194 150.38 145.5 200.5 0 200.5"),
    persona_h("The sales adviser", 0, 40, 256, "5755e103", "The sales adviser", "Types it in the CRM"),
    persona_h("The back office", 644, 40, 256, "2a9ca040", "The back office", "Types it in the finance app"),
    node("adviser", 120, 106), node("CRM card top", 120, 142), node("back office", 764, 106), node("finance card top", 764, 142),
    node("CRM card right", 248, 243), node("finance card left", 636, 243), node("CRM card bottom", 120, 344),
    node("answer left", 314, 544.5), node("finance card bottom", 764, 344), node("answer right", 570, 544.5),
    annotation("typed again", 402, 237, "Typed again"),
])
dump("s08", s08)
