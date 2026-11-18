"""Opener from the Figma read of 2026-11-17 (318:3774, "BNG OS · A"). Run: PYTHONPATH=. python -P gen_op.py"""
from dsl import *

op = {"id": "318:3774", "name": "00 · Opener · BNG OS · A",
      "props": {"Note": "Illustrative · fictional people and figures", "Lede": "A lede in one or two short lines.", "Show lede": False, "Eyebrow": "01 · The group",
                "Title": "One group,\nmany companies.", "Show footer": False, "Show title column": False, "Number": "01 / 27", "Show note": True, "Show nav": False},
      "nav": {},
      "ch": [{"x": -127, "y": 268, "cn": "Brand / Logo / primary / full-colour", "w": 685.24, "h": 121.88, "lg": 1, "vp": {}},
             {"x": -234, "y": 446, **T("One system above the tools BNG already has.", "body/lede-lg", "text/neutral/subtle", w=900, al="C")}]}
dump("op", op)
