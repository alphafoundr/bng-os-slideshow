"""Slide 14 (303:3128), free-standing cards, no desktop device (2026-11-18; layout in cortex_flow.py).
fact, button, confirmation and vconn stay importable from here (gen_s18, gen_s21 and gen_p2_s22_s23 use them).
Run: PYTHONPATH=. python -P gen_s14.py"""
from dsl import *
from cortex_flow import *

H_LEAD, H_READ = 188, 372
H_SUGG, H_APPR, H_CONF = 232, 204, 96
geo = GeoA([H_LEAD, H_READ], 1, [H_SUGG, H_APPR, H_CONF], 3)
yl, yr = geo.yl, geo.yr


def row(*a):
    return stretch(fact(*a, py=ROW_PY))


lead = subject_card("New lead", X2, yl[0], W2, H_LEAD, "construction", "Jan V.", "The lead", "New lead · Elyazia, 2-bed", "Came in through the website form")
read = read_card("What Cortex read", X2, yl[1], W2, H_READ, "What Cortex read",
                 [row("Project", 0, 0, "Project", "Elyazia, 2-bed", "Fame"), row("Language", 0, 0, "Language", "Dutch", "Fame"),
                  row("Earlier record", 0, 0, "Earlier record", "None found", "Nexus Panthera"),
                  row("Who is free", 0, 0, "Availability", "Two advisers free", "Fame")])
sugg = suggestion_card("Assign the adviser", X3, yr[0], W3, H_SUGG, "Assign the Dutch-speaking adviser who is free now", "Strong fit for Elyazia, 2-bed.",
                       who("backoffice", "Reda M.", "Adviser · free now", None, PORTRAIT_SM))
appr = approval_card("The sales manager", X3, yr[1], W3, H_APPR, "director", "Omar T.", "The sales manager", "Sees the reason, then decides")
done = result_card("Lead assigned", X3C, yr[2], W3C, H_CONF, "Lead assigned to the adviser", "Approved by the sales manager and logged in the lead's history.")

ch = [lead, read, sugg, appr, done]
for i, (name, ic, label) in enumerate((("Website form", "globe", "Website form"), ("Fame's CRM", "megaphone", "Fame"), ("Nexus Panthera", "users", "Nexus Panthera"))):
    ch.append(source(name, X1, geo.ys[i] - 28, ic, label))
ch += geo.build_lines({"recv": "what Cortex read", "chain": [("new lead", "what Cortex read")], "propose": "suggestion", "approve": "sales manager",
                       "result": "lead assigned"}, ["Website form", "Fame's CRM", "Nexus Panthera"])
s14 = slide("303:3128", "07 · Cortex at work · From the form to the right adviser", "14 / 27", "Cortex at work", "From the form\nto the right adviser.",
            "Cortex reads a new lead, checks who is free and who speaks the language, and proposes an adviser. A person confirms.",
            "Illustrative example · fictional people and figures", 7, ch)
dump("s14", s14)
