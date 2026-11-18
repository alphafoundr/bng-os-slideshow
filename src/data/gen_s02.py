"""Slide 02's finance-app inventory. Run from src/data with PYTHONPATH=."""
from dsl import T, at, dump, icon, slide
from desk import desktop_big


PROGRAMMES = [
    ("M-Resort", 244),
    ("Elyazia", 172),
    ("Ayline Garden", 108),
    ("Jardins d'Alma", 88),
    ("Naïa Hills", 76),
    ("Petit Ambassadeur", 46),
    ("Jardin d'Eden", 28),
]
STATUSES = [
    ("sold", 572, "chart/neutral/primary"),
    ("still to sell", 185, "chart/neutral/track"),
    ("reserved", 5, "chart/neutral/secondary"),
]
TOTAL = sum(count for _, count in PROGRAMMES)


def stat_chip(x, title, count, role):
    return {"x": x, "y": 49, "t": "F", "w": 192, "h": 43, "n": "Inventory status · " + title,
            "cr": 8, "f": [{"c": "background/neutral/subtle"}],
            "sk": {"c": "border/neutral/subtle"}, "sw": 1,
            "lm": "H", "pad": [0, 12, 0, 12], "gap": 8, "ca": "c",
            "ch": [{"t": "R", "w": 12, "h": 8, "cr": 4, "f": [{"c": role}]},
                   T(str(count), "heading/md", "text/neutral/bold", nw=1),
                   T(title, "body/sm", "text/neutral/bold", nw=1)]}


def status_bar():
    segments = []
    offset = 0
    for label, count, role in STATUSES:
        width = 592 * count / TOTAL
        segments.append({"x": offset, "y": 0, "t": "R", "w": width, "h": 8, "n": label,
                         "f": [{"c": role}]})
        offset += width
    return {"x": 16, "y": 102, "t": "F", "w": 592, "h": 8, "cr": 4, "k": 1,
            "n": "Overall inventory by status", "ch": segments}


def programme_row(y, name, count):
    tile = {"t": "F", "w": 24, "h": 24, "cr": 4, "f": [{"c": "background/neutral/subtle"}],
            "lm": "H", "pa": "c", "ca": "c", "ch": [icon("building", 16)]}
    bar = {"t": "F", "w": 352, "h": 8, "cr": 4, "k": 1,
           "f": [{"c": "chart/neutral/track"}],
           "ch": [{"x": 0, "y": 0, "t": "R", "w": 352 * count / PROGRAMMES[0][1], "h": 8,
                   "f": [{"c": "chart/neutral/primary"}], "cr": 4}]}
    return {"x": 16, "y": y, "t": "F", "w": 592, "h": 31, "n": "Programme · " + name,
            "sk": {"c": "border/neutral/subtle"}, "sw": [0, 0, 1, 0],
            "lm": "H", "gap": 8, "ca": "c",
            "ch": [tile, T(name, "label/md-strong", "text/neutral/bold", w=156, nw=1), bar,
                   T(str(count), "label/md-strong", "text/neutral/bold", w=36, nw=1, al="R")]}


assert TOTAL == sum(count for _, count, _ in STATUSES)
header = [
    {"x": 16, "y": 14, **T("Lots by programme", "heading/sm", "text/neutral/bold", nw=1)},
    {"x": 492, "y": 15, **T("762 lots", "label/md-strong", "text/neutral/bold", w=116, nw=1, al="R")},
]
screen = [
    *at(1, *header),
    *[at(2, stat_chip(16 + i * 200, *status), motion="row", index=i) for i, status in enumerate(STATUSES)],
    at(3, status_bar()),
    at(3, {"x": 212, "y": 115, **T("Programme size", "label/sm", "text/neutral/subtle", nw=1)}),
    *[at(4, programme_row(135 + i * 31, *programme), motion="row", index=i)
      for i, programme in enumerate(PROGRAMMES)],
    at(6, {"x": 16, "y": 360, **T("Source · BNG Business, the finance app", "label/tag", "text/neutral/subtle", nw=1)}),
]
s02 = slide("266:6269", "01 · The group · 762 lots, seven programmes", "02 / 27", "The group",
            "762 lots,\nseven programmes.",
            "Seven programmes in the finance app today: 762 lots, three quarters of them sold.",
            "Figures read from the finance app on 13 November 2026", 1,
            [desktop_big("Device · Desktop · Finance app", screen)])
s02["props"]["Big desktop"] = True
s02["props"]["Title width"] = 444  # Same exception as s19, so "seven programmes" stays together.
s02["props"]["Monochrome wordmark"] = True
dump("s02", s02)
