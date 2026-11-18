"""Writes s04.json from the compact Figma read of slide 277:1810 (2026-11-17). Run: python -P src/data/gen_s04.py"""
import json
import os
from dsl import at, draw

HERE = os.path.dirname(os.path.abspath(__file__))
SUBTLE = [{"c": "border/neutral/subtle"}]
guides_h = [(148, 678, 684), (77, 635, 675), (81, 592, 591), (105, 549, 567), (100, 506, 482), (96, 463, 396), (78, 420, 504),
            (74, 377, 418), (83, 334, 409), (132, 291, 360), (43, 248, 154), (120, 205, 257), (97, 162, 100), (102, 119, 185), (46, 76, 151)]
guides_v = [(850, 626), (770, 583), (690, 540), (600, 454), (510, 411), (395, 153), (305, 67), (215, 196)]
ch = []
for x, y, w in guides_h:
    ch.append({"x": x, "y": y, "t": "R", "w": w, "h": 1, "f": SUBTLE})
for x, h in guides_v:
    ch.append({"x": x, "y": 52, "t": "R", "w": 1, "h": h, "f": SUBTLE})

# (name, x, y, w, h, path)
conns = [
    ("step 1 → step 2", 227, 76, 66, 43, "M 0 0 C 33 0 33 43 66 43"),
    ("step 2 → step 3", 227, 119, 66, 43, "M 66 0 C 33 0 33 43 0 43"),
    ("step 3 → step 4", 227, 162, 156, 43, "M 0 0 C 78 0 78 43 156 43"),
    ("step 4 → step 5", 227, 205, 156, 43, "M 156 0 C 78 0 78 43 0 43"),
    ("step 5 → step 6", 227, 248, 271, 43, "M 0 0 C 135.5 0 135.5 43 271 43"),
    ("step 6 → step 7", 510, 303, 0, 19, "M 0 0 L 0 19"),
    ("step 7 → step 8", 510, 346, 0, 19, "M 0 0 L 0 19"),
    ("step 8 → step 9", 522, 377, 66, 43, "M 0 0 C 33 0 33 43 66 43"),
    ("step 9 → step 10", 522, 420, 66, 43, "M 66 0 C 33 0 33 43 0 43"),
    ("step 10 → step 11", 522, 463, 66, 43, "M 0 0 C 33 0 33 43 66 43"),
    ("step 11 → step 12", 612, 506, 66, 43, "M 0 0 C 33 0 33 43 66 43"),
    ("step 12 → step 13", 690, 561, 0, 19, "M 0 0 L 0 19"),
    ("step 13 → step 14", 702, 592, 56, 43, "M 0 0 C 28 0 28 43 56 43"),
    ("step 14 → step 15", 782, 635, 56, 43, "M 0 0 C 28 0 28 43 56 43"),
]
for n, x, y, w, h, d in conns:
    ch.append({"x": x, "y": y, "t": "V", "n": "Connector / " + n, "w": w, "h": h, "sk": {"c": "border/neutral/default"}, "sw": 2,
               "da": [6, 6], "cap": "ROUND", "jn": "ROUND", "d": [d]})


def annotation(name, x, y):
    return {"x": x, "y": y, "cn": "Illo / Annotation", "t": "F", "sh": "H", "sv": "H", "n": name, "f": [{"c": "background/neutral/raised"}],
            "sk": {"c": "border/neutral/subtle"}, "sw": 1, "cr": 8, "lm": "H", "pad": [4, 12, 4, 12], "pa": "c", "ca": "c", "kg": 1,
            "ch": [{"t": "T", "c": "Typed again", "f": {"c": "text/neutral/bold"}, "s": "label/tag", "nw": 1}]}


ch.append(annotation("Annotation · typed again · 11 to 12", 575, 535))

tags = [("Nexus Panthera", 162.5, 0), ("Fame", 281.5, 0), ("my.bngimmo.com", 337, 0), ("BNG Business", 463, 0), ("By hand", 569.5, 0),
        ("To confirm", 651, 1), ("Notary", 743, 0), ("Palmease", 815, 0)]
for label, x, dashed in tags:
    t = {"x": x, "y": 24, "cn": "Illo / Tag", "t": "F", "sh": "H", "sv": "H", "n": "Tag · " + label}
    if dashed:
        t.update({"sk": {"c": "border/neutral/bold"}, "sw": 1, "da": [4, 3]})
        txt = {"t": "T", "c": label, "f": {"c": "text/neutral/subtlest"}, "s": "label/tag", "nw": 1}
    else:
        t["f"] = [{"c": "background/neutral/tag"}]
        txt = {"t": "T", "c": label, "f": {"c": "text/neutral/bold"}, "s": "label/tag", "nw": 1}
    t.update({"cr": 4, "lm": "H", "pad": [2, 8, 2, 8], "pa": "c", "ca": "c", "ch": [txt]})
    ch.append(t)

# (number, name, badge x, badge y, label y)
steps = [(1, "Lead", 203, 64, 67), (2, "Qualification", 293, 107, 110), (3, "Assignment", 203, 150, 153), (4, "Sales follow-up", 383, 193, 196),
         (5, "Sale", 203, 236, 239), (6, "Contract request", 498, 279, 282), (7, "Validation", 498, 322, 325), (8, "Contract", 498, 365, 368),
         (9, "Welcome", 588, 408, 411), (10, "Instalments", 498, 451, 454), (11, "Commission", 588, 494, 497), (12, "Construction", 678, 537, 540),
         (13, "Handover", 678, 580, 583), (14, "Land title", 758, 623, 626), (15, "Life of the property", 838, 666, 669)]
for num, name, bx, by, ly in steps:
    ch.append({"x": bx, "y": by, "cn": "Illo / Badge", "t": "F", "w": 24, "h": 24, "n": "Badge · %d · %s" % (num, name),
               "f": [{"c": "background/action/bold"}], "sk": {"c": "background/neutral/canvas"}, "sw": 2, "sa": "OUTSIDE", "cr": 999,
               "lm": "H", "pa": "c", "ca": "c",
               "ch": [{"t": "T", "c": str(num), "f": {"c": "text/on-action/bold"}, "s": "label/tag", "nw": 1}]})
    ch.append({"x": 0, "y": ly, "t": "T", "c": name, "f": {"c": "text/neutral/bold"}, "s": "heading/xs", "nw": 1})
ch.append(annotation("Annotation · typed again", 314, 255.5))
paths = ch[len(guides_h) + len(guides_v):][:len(conns)]
badges = [part for part in ch if part.get("cn") == "Illo / Badge"]
for i, badge in enumerate(badges):
    at(i, badge, ch[ch.index(badge) + 1])
    if i:
        draw(i - 1, paths[i - 1], target=badge)
at(10, ch[len(guides_h) + len(guides_v) + len(conns)], motion="label")
at(4, ch[-1], motion="label")

data = {
    "id": "277:1810", "name": "03 · The journey · Fifteen steps, one client · B",
    "props": {"Show title column": True, "Number": "04 / 27", "Show nav": True, "Show note": True,
              "Note": "Steps and tools as BNG described them; dashed tags are to confirm.",
              "Lede": "From a first message to the life of the property, the file changes hands 11 times between tools and people.",
              "Show lede": True, "Show footer": True, "Title": "Fifteen steps,\none client.", "Eyebrow": "The journey"},
    "nav": {"Chapter": "3"}, "ch": ch,
}
with open(os.path.join(HERE, "s04.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
print("s04.json", len(ch), "records")
