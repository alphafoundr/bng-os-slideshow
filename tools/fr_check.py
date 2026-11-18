"""French fit check: for every text on every slide, compare the French rendering with the English one.

usage: python -P tools/fr_check.py <port> [key ...]

Flags, per text element (same DOM in both languages):
  more-lines   the French text wraps onto more lines than the English one (a layout that was drawn for English)
  overflow     the text sticks out of its parent box by more than 1 px (right/bottom) or out of the 1440x900 artboard
  orphan       the last line of a wrapped French text is a single short word (<= 3 characters)
Writes nothing; prints one line per finding.
"""
import sys

JS = """
() => {
  const s = document.querySelector('.slide:not([hidden])');
  const art = s.getBoundingClientRect();
  const out = [];
  s.querySelectorAll('.tx').forEach((t, i) => {
    const r = t.getBoundingClientRect();
    if (!r.width && !r.height) return;
    const cs = getComputedStyle(t);
    const lh = parseFloat(cs.lineHeight) || (parseFloat(cs.fontSize) * 1.2);
    const rg = document.createRange(); rg.selectNodeContents(t);
    const rects = Array.from(rg.getClientRects()).filter(x => x.width > 0.5);
    const lines = new Set(rects.map(x => Math.round(x.top / 4))).size;
    const last = rects.length ? rects[rects.length - 1] : r;
    const p = t.parentElement;
    const pr = p ? p.getBoundingClientRect() : null;
    let ov = null;
    const right = Math.max(...rects.map(x => x.right), r.right), bottom = Math.max(...rects.map(x => x.bottom), r.bottom);
    if (pr && p.classList.contains('b') && (right > pr.right + 1.5 || bottom > pr.bottom + 1.5)) ov = ['parent', Math.round(right - pr.right), Math.round(bottom - pr.bottom)];
    if (right > art.right + 1 || r.left < art.left - 1) ov = ['artboard', Math.round(right - art.right), 0];
    const words = t.textContent.trim().split(/\\s+/);
    out.push({ i, text: t.textContent.replace(/\\s+/g, ' ').trim(), lines, ov, lastw: words[words.length - 1] || '', lastLine: rects.length ? Math.round(last.width) : 0 });
  });
  return out;
}
"""


def main():
    from playwright.sync_api import sync_playwright
    port = sys.argv[1]
    only = sys.argv[2:]
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        pg = ctx.new_page()
        pg.goto("http://127.0.0.1:%s/?nopreshow=1&lang=en" % port)
        pg.wait_for_function("window.BNG_DECK && window.BNG_DECK.index >= 0")
        pg.evaluate("document.fonts.ready")
        keys = pg.evaluate("Array.from(document.querySelectorAll('.slide')).map(s => s.getAttribute('data-key'))")
        total = 0
        for k in keys:
            if only and k not in only:
                continue
            pg.evaluate("l => BNG_DECK.setLang(l, false)", "en")
            pg.evaluate("k => BNG_DECK.goKey(k)", k)
            pg.wait_for_timeout(120)
            en = pg.evaluate(JS)
            pg.evaluate("l => BNG_DECK.setLang(l, false)", "fr")
            pg.wait_for_timeout(120)
            fr = pg.evaluate(JS)
            for a, f in zip(en, fr):
                msgs = []
                if f["lines"] > a["lines"]:
                    msgs.append("more-lines %d>%d" % (f["lines"], a["lines"]))
                if f["ov"] and not a["ov"]:
                    msgs.append("overflow %s" % (f["ov"],))
                if f["lines"] > 1 and len(f["lastw"]) <= 3 and f["lastLine"] < 60:
                    msgs.append("orphan '%s'" % f["lastw"])
                if msgs:
                    total += 1
                    print("%s #%d  %s  |  %s  ->  %s" % (k, f["i"], "; ".join(msgs), a["text"][:60], f["text"][:70]))
        print("findings:", total)
        b.close()


main()
