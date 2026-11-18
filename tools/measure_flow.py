"""usage: python -P tools/measure_flow.py <port> <slide> [WxH] [fr]
Per fixed-height box of the flow (cards, suggestion, confirmation, source): declared height vs natural content height, and the
exact end points of every connector / dot against the box edges they should touch. Positions in slot coordinates (artboard px)."""
import json
import sys

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
port, slide = sys.argv[1], sys.argv[2]
size = sys.argv[3] if len(sys.argv) > 3 and "x" in sys.argv[3] else "1440x900"
fr = "fr" in sys.argv[3:]
w, h = [int(v) for v in size.split("x")]
JS = r"""
(slide) => {
  const sec = document.querySelector('section[data-key="' + slide + '"]');
  const slot = sec.querySelector('.slot');
  const k = document.getElementById('deck').getBoundingClientRect().width / (1440 + parseFloat(getComputedStyle(document.getElementById('deck')).getPropertyValue('--ex')));
  const o = slot.getBoundingClientRect();
  const rel = (r) => ({x: +((r.left - o.left) / k).toFixed(1), y: +((r.top - o.top) / k).toFixed(1), w: +(r.width / k).toFixed(1), h: +(r.height / k).toFixed(1)});
  const out = {boxes: [], lines: [], dots: [], overflow: []};
  sec.querySelectorAll('[data-name]').forEach(e => {
    const n = e.getAttribute('data-name');
    if (/^(Card ·|Suggestion ·|Confirmation ·|Tool ·|Queue row ·|Portrait ·|Tool disc)/.test(n) || e.getAttribute('data-c') === 'Illo / Annotation') {
      const r = rel(e.getBoundingClientRect());
      const o2 = {n, ...r};
      if (/^(Card ·|Suggestion ·|Confirmation ·)/.test(n)) {
        const st = e.style.height; e.style.height = 'auto';
        o2.natural = +(e.getBoundingClientRect().height / k).toFixed(1);
        e.style.height = st;
        if (e.scrollHeight > e.clientHeight + 1) out.overflow.push(n);
      }
      if (e.getAttribute('data-c') === 'Illo / Annotation') o2.n = 'Annotation · ' + e.textContent;
      out.boxes.push(o2);
    }
    if (e.tagName.toLowerCase() === 'svg' && /^(AI connector|Connector) /.test(n)) {
      const r = rel(e.getBoundingClientRect());
      const p = e.querySelector('path');
      const len = p.getTotalLength();
      const a = p.getPointAtLength(0), b = p.getPointAtLength(len);
      // end points in slot px: svg origin + point (scaled by the svg's rendered/declared ratio)
      const vb = (e.getAttribute('viewBox') || '').split(' ').map(Number);
      const sx = vb.length === 4 ? r.w / vb[2] : 1, sy = vb.length === 4 ? r.h / Math.max(vb[3], 1) : 1;
      out.lines.push({n, from: [+(r.x + a.x * sx).toFixed(1), +(r.y + a.y * sy).toFixed(1)], to: [+(r.x + b.x * sx).toFixed(1), +(r.y + b.y * sy).toFixed(1)]});
    }
    if (/^(AI node|Node) /.test(n)) {
      const r = rel(e.getBoundingClientRect());
      out.dots.push({n, cx: +(r.x + r.w / 2).toFixed(1), cy: +(r.y + r.h / 2).toFixed(1), d: r.w});
    }
  });
  return out;
}
"""
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    ctx = b.new_context(viewport={"width": w, "height": h})
    pg = ctx.new_page()
    pg.goto("http://localhost:%s/?nopreshow=1%s#%s" % (port, "&lang=fr" if fr else "", slide))
    pg.wait_for_timeout(2200)
    res = pg.evaluate(JS, slide)
    for bx in res["boxes"]:
        nat = " natural %s" % bx["natural"] if "natural" in bx else ""
        print("BOX  %-34s x%-7s y%-7s w%-7s h%-7s%s" % (bx["n"][:34], bx["x"], bx["y"], bx["w"], bx["h"], nat))
    for l in res["lines"]:
        print("LINE %-44s %s -> %s" % (l["n"][:44], l["from"], l["to"]))
    for d in res["dots"]:
        print("DOT  %-44s (%s, %s) d=%s" % (d["n"][:44], d["cx"], d["cy"], d["d"]))
    print("OVERFLOW:", res["overflow"])
    b.close()
