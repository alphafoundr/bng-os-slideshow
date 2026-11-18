"""Pause 'Meet Cortex' and slides 12, 13 from the Figma reads of 2026-11-17 (332:5105, 291:2752, 293:3342). Run: PYTHONPATH=. python -P src/data/gen_p1_s13.py"""
from dsl import *

# ---------------- pause · Meet Cortex. ----------------
p1 = {"id": "332:5105", "name": "06 · Cortex decides · Meet Cortex (pause)",
      "props": {"Note": "Illustrative · fictional people and figures", "Lede": "A lede in one or two short lines.", "Show lede": False,
                "Eyebrow": "06 · Cortex: what it decides", "Title": "Meet Cortex.", "Show footer": False, "Show nav": True, "Show note": False,
                "Show title column": False, "Number": "01 / 27"},
      "nav": {"Chapter": "6"},
      "ch": [{"x": -468, "y": 557, **T("Meet Cortex.", "display/xl", "text/neutral/bold", w=1368)},
             {"x": -468, "y": 717, **T("One engine, built and tuned only for BNG.", "body/lede-lg", "text/neutral/subtle", w=900)},
             cortex_lockup(-468, -36)]}
dump("p1", p1)

# ---------------- 12 · One engine, tuned for BNG ----------------
ch = [hub("Cortex", 240, 264, 180, "Built for BNG")]
# name, disc x, disc y, icon, label, connector (x,y,w,h,d), node at the tool, node at the hub
tools = [("Fame's CRM", 32, 14, "megaphone", "Fame", (88, 42, 112, 250, "M 0 0 C 56 0 56 250 112 250"), (80, 34), (192, 284)),
         ("Nexus Panthera", 10, 114, "users", "Nexus Panthera", (88, 142, 112, 174, "M 0 0 C 56 0 56 174 112 174"), (80, 134), (192, 308)),
         ("BNG Business", 16, 214, "coin", "BNG Business", (88, 242, 112, 98, "M 0 0 C 56 0 56 98 112 98"), (80, 234), (192, 332)),
         ("Vertex", 32, 314, "building", "Vertex", (88, 342, 112, 22, "M 0 0 C 56 0 56 22 112 22"), (80, 334), (192, 356)),
         ("BNG Sales Monitor", 1, 414, "bar-chart", "BNG Sales Monitor", (88, 388, 112, 54, "M 0 54 C 56 54 56 0 112 0"), (80, 434), (192, 380)),
         ("Synergy", 32, 514, "circle-ask", "Synergy", (88, 412, 112, 130, "M 0 130 C 56 130 56 0 112 0"), (80, 534), (192, 404)),
         ("my.bngimmo.com", 4, 614, "smartphone", "my.bngimmo.com", (88, 436, 112, 206, "M 0 206 C 56 206 56 0 112 0"), (80, 634), (192, 428))]
for name, x, y, ic, label, (cx, cy, cw, chh, d), n1, n2 in tools:
    # Keep the output edge fixed; spread the incoming curves over the wider gap.
    d = d.replace("56", "76").replace("112", "152")
    td = tool(name, x, y, ic, label)
    line = ai_conn_plain(name + " → Cortex", cx, cy, cw + 40, chh, d)
    # ai_conn_plain adds 4 to x; cancel it so the far end is exactly x=240.
    line["x"] -= 4
    # Correct the inherited 4px start offset while retaining the hub arrival y.
    import re
    d = re.sub(r"M 0 (\d+) C 76 (\d+)", lambda m: "M 0 %s C 76 %s" % (int(m[1])-4, int(m[2])-4), d)
    line["d"] = [d]
    # Tool dot centre is 88; the incoming line starts there.
    td["exl"] = line["exw"] = 0.6
    dot = ai_node(name, *n1)
    dot["exl"] = 0.6
    ch += [td, line, dot]
ch += [suggestion("Assign the lead to the right adviser", 540, 120, "Assign the lead to the right adviser", "Speaks Dutch, free now"),
       ai_conn_plain("Cortex → Assign the lead to the right adviser", 420, 182, 120, 122, "M 0 122 C 60 122 60 0 120 0", True),
       ai_node("Cortex → 0", 412, 296),
       suggestion("Price differs from the contract", 540, 302, "Price differs from the contract", "Two tools give two prices"),
       ai_conn_plain("Cortex → Price differs from the contract", 420, 364, 120, 0, "M 0 0 L 120 0", True),
       ai_node("Cortex → 1", 412, 356),
       suggestion("Call the buyer who stopped answering", 540, 484, "Call the buyer who stopped answering", "No reply to two reminders"),
       ai_conn_plain("Cortex → Send the payment reminder", 420, 424, 120, 122, "M 0 0 C 60 0 60 122 120 122", True),
       ai_node("Cortex → 2", 412, 416),
       tag("Sales manager confirms", 728, 140, "Sales manager confirms"), tag("Back office confirms", 749, 322, "Back office confirms"),
       tag("Collections confirms", 749, 504, "Collections confirms")]
s12 = slide("291:2752", "06 · Cortex decides · One engine, tuned for BNG · A", "12 / 27", "Cortex: what it decides", "One engine,\ntuned for BNG.",
            "Cortex reads every tool, checks them against each other and proposes the next best action. A person confirms what matters.",
            "Illustrative example", 6, ch)
dump("s12", s12)

# ---------------- 13 · Sure, it acts. Unsure, it asks. ----------------
ch = [hub("Cortex", 40, 264, 200, "Every event"),
      tag("Clear: done automatically", 480, 54, "Clear: done automatically", "success"),
      suggestion("Reminder sent", 480, 88, "Reminder sent", "By WhatsApp, on the right day", label="Done by Cortex", dashed=False),
      ai_conn_plain("Cortex → acts alone", 240, 150, 240, 174, "M 0 174 C 120 174 120 0 240 0", True),
      ai_node("Cortex lane 0", 232, 316),
      tag("Doubtful: a person decides", 480, 268, "Doubtful: a person decides", "dashed"),
      suggestion("Two buyers, same phone", 480, 302, "Two buyers share one phone", "Possible duplicate record"),
      ai_conn_plain("Cortex → asks a person", 240, 364, 240, 0, "M 0 0 L 240 0", True),
      ai_node("Cortex lane 1", 232, 356),
      tag("Legal or money: always confirmed", 480, 482, "Legal or money: always confirmed"),
      suggestion("Registered letter", 480, 516, "Send the registered letter", "60 days late, two reminders unanswered"),
      ai_conn_plain("Cortex → always confirmed", 240, 404, 240, 174, "M 0 0 C 120 0 120 174 240 174", True),
      ai_node("Cortex lane 2", 232, 396)]
s13 = slide("293:3342", "06 · Cortex decides · Sure it acts, unsure it asks", "13 / 27", "Cortex: what it decides", "Sure, it acts.\nUnsure, it asks.",
            "Clear cases run on their own. Anything doubtful goes to the right person, and money or legal steps always wait for one.",
            "Illustrative example", 6, ch)
dump("s13", s13)
