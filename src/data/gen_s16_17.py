"""Slides 16 and 17 from the Figma reads of 2026-11-17 (308:3460, 310:3676). Slide 16 is rebuilt as free-standing cards, no desktop
device (2026-11-18; layout in cortex_flow.py); slide 17 is unchanged. Run: PYTHONPATH=. python -P gen_s16_17.py"""
from dsl import *
from cortex_flow import *

QW = W2                        # queue card width


def qrow(name, n, hkey, ini, who_, late, amt, selected=False):
    """App / Data display / Queue row, with the debtor's portrait (initials when the pool has no face left)."""
    if hkey:
        h, crop = POOL[hkey]
        face = portrait(h, "Portrait · " + who_, 44, crop=crop)
    else:
        face = {"t": "F", "w": 44, "h": 44, "f": [{"c": "background/neutral/muted"}], "cr": 999, "k": 1, "lm": "H", "pa": "c", "ca": "c",
                "ch": [T(ini, "label/sm", "text/neutral/bold", nw=1)]}
    return {"cn": "App / Data display / Queue row", "t": "F", "sh": "L", "sv": "H", "h": 76, "n": "Queue row · " + name,
            "f": [{"c": "background/neutral/selected" if selected else "background/neutral/raised"}], "sk": {"c": "border/neutral/subtle"}, "sw": [0, 0, 1, 0],
            "lm": "H", "gap": 6, "pad": [0, 8, 0, 8], "ca": "c",
            "ch": [T(str(n), "label/md-strong", "text/neutral/subtlest", w=20, al="C"),
                   {"t": "F", "sh": "L", "sv": "H", "k": 1, "lm": "H", "gap": 12, "ca": "c",
                    "ch": [face,
                           {"t": "F", "sh": "H", "sv": "H", "k": 1, "lm": "V",
                            "ch": [T(who_, "label/md-strong", "text/neutral/bold", nw=1), T(late, "body/sm", "text/neutral/subtlest", nw=1)]}]},
                   {"t": "F", "sv": "H", "w": 84, "k": 1, "lm": "V", "ca": "x", "ch": [T(amt, "label/md-strong", "text/neutral/bold", sh="L", al="R")]},
                   {"t": "F", "w": 20, "h": 20, "k": 1, "lm": "H", "pa": "c", "ca": "c", "ch": [marker(14)]}]}


H_Q = 434
H_SUGG, H_APPR, H_CONF = 232, 204, 96
geo = GeoA([H_Q], 0, [H_SUGG, H_APPR, H_CONF], 3)
yl, yr = geo.yl, geo.yr
rows = {"t": "F", "sh": "L", "sv": "H", "lm": "V", "gap": 0,
        "ch": [qrow("Nadia S.", 1, "partner", "NS", "Nadia S.", "47 days late", "MAD 74,000", True),
               qrow("Meryem A.", 2, None, "MA", "Meryem A.", "31 days late", "MAD 55,500"),
               qrow("Youssef B.", 3, "buyer", "YB", "Youssef B.", "26 days late", "MAD 92,500"),
               qrow("Yassine K.", 4, "construction", "YK", "Yassine K.", "14 days late", "MAD 41,000")]}
queue = card("Today · 4 actions", X2, yl[0], QW, H_Q,
             [head("Today · 4 actions", "Ranked, with the reason for each"),
              T("Most urgent first", "label/md-strong", "text/neutral/subtlest", nw=1), rows], COL2, gap=14)
sugg = suggestion_card("Send the reminder", X3, yr[0], W3, H_SUGG, "Send Nadia S.\nthe registered letter", "47 days late, no reply",
                       who("partner", "Nadia S.", "The buyer", None, PORTRAIT_SM))
appr = approval_card("Collections", X3, yr[1], W3, H_APPR, "rep", "Salma R.", "Collections", "Sees the reason, then decides")
done = result_card("Reminder sent", X3C, yr[2], W3C, H_CONF, "Registered letter sent", "Approved by collections, with the proof saved in the file.")

SRC = (("BNG Business", "coin", "BNG Business"), ("Bank", "bank", "Bank"), ("Nexus Panthera", "users", "Nexus Panthera"))
sources = [source(name, X1, y - 28, ic, label) for y, (name, ic, label) in zip(geo.ys, SRC)]
ch = geo.build_flow([queue, sugg, appr, done], sources, {
    "recv": "today's list", "chain": [], "propose": "suggestion", "approve": "collections", "result": "reminder sent"}, recv_y=148)
s16 = slide("308:3460", "07 · Cortex at work · Today's actions, already ranked", "16 / 27", "Cortex at work", "Today's actions,\nalready ranked.",
            "Every morning the day's collection actions arrive ranked, with the reason for each. Nothing legal leaves without a person.",
            "Illustrative example · fictional people and figures", 7, ch)
dump("s16", s16)

# ---------------- 17 · What changes, in numbers ----------------
ch = [tag("Today", 330, 30, "Today"), tag("Low end estimate", 480, 30, "Low end · estimate", "dashed"), tag("High end estimate", 690, 30, "High end · estimate", "dashed")]


def row(y, title, sub, today, low, high, lw=190, hw=210, vy=None, vs="heading/sm", ty=None):
    vy = y - 2 if vy is None else vy
    out = [{"x": 0, "y": y, **T(title, "heading/xs", "text/neutral/bold", w=296)},
           {"x": 0, "y": y + 22, **T(sub, "body/xs", "text/neutral/subtlest", w=296)},
           {"x": 330, "y": ty if ty is not None else vy, **T(today, "heading/sm", "text/neutral/bold", w=130)},
           {"x": 480, "y": vy, **T(low, vs, "text/neutral/bold", w=lw)}]
    if high is not None:
        out.append({"x": 690, "y": vy, **T(high, vs, "text/neutral/bold", w=hw)})
    out.append({"x": 0, "y": y + 65, "t": "V", "n": "Divider · " + title, "w": 900, "h": 0, "sk": {"c": "border/neutral/subtle"}, "sw": 1, "ln": 1})
    return out


ch += row(84, "Reminders that reach the buyer", "Low: buyers with a usable email or phone. High: after a contact-recovery pass.", "0 of 800", "about 65%", "about 95%")
ch += row(164, "Late sales with a recorded follow-up", "Every late sale gets a ranked action each day; the low end allows for cases paused by finance.", "64 of 348", "90%", "100%")
ch += row(244, "Days from due date to payment, median", "Reminders pull late payers forward by 20% (low) to 40% (high).", "27 days", "22 days", "16 days")
ch += row(324, "Payments that match no sale", "A payment cannot be saved without a sale; the old ones are cleared once.", "80", "under 10", "0")
ch += row(404, "Adviser line-ups deciding who gets a lead", "One assignment engine, with one history.", "21", "1, in both cases", None, lw=420)
ch += [{"x": 0, "y": 506, **T("In dirhams · scenarios", "label/md-strong", "text/neutral/subtlest", w=300)}]
ch += row(536, "Overdue cash collected a quarter sooner", "10% of the low overdue reading to 25% of the high one. A scenario.", "not measured", "MAD 9M", "MAD 37M", vy=531, vs="heading/md", ty=534)
ch += row(616, "Sales kept, not cancelled, per 8 months", "Earlier reminders save 10% to 30% of 34 cancellations. A scenario.", "not measured", "3 sales · MAD 5M", "10 sales · MAD 17M", vy=611, vs="heading/md", ty=614)
s17 = slide("310:3676", "11 · In numbers · What changes, in numbers", "24 / 27", "The gains", "What changes,\nin numbers.",
            "Every gain is a range. Today's figures come from BNG's own systems; the low and high ends are our estimates, with what each rests on.",
            "Today: read from BNG's systems on 13 November 2026 · Low and high end: our estimates", 11, ch)
dump("s17", s17)
