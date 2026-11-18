"""Builds public/preshow.js from the pre-show prototype C2 (slideshow/preshow/src/geometry.js + c2.js, read only) plus the site's
own audio module (src/preshow_audio.js). c2.js is not copied by hand: this script applies a fixed list of exact replacements
and FAILS when one does not match exactly once, so a changed prototype is noticed instead of silently half-ported.

What changes against c2.js (everything else, physics and GSAP timeline included, is the prototype's own):
  - element ids get a ps- prefix (the deck has its own #stage); colours come from the deck's CSS variables, not hex;
  - the sound hint, the S gate and the S/M keys are gone; sound lives in preshow_audio.js (on by default, M mutes);
  - "press space" is a button (touch has no space bar) and stays until the show starts; EN/FR text;
  - when the transition lands on the opener, the deck takes over (window.BNG_PRESHOW_REST) and the overlay is dropped;
  - nothing runs when the page is opened on a slide (#sNN) or with ?nopreshow=1.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
PRE = os.path.join(SITE, "..", "slideshow", "preshow", "src")
EXT = os.path.join(SITE, "src", "ext", "slideshow", "preshow", "src")


def pre(name):
    """The prototype file: the outer design folder where it exists (mirrored into src/ext/), else the mirror, so a clone builds alone."""
    outer, inner = os.path.join(PRE, name), os.path.join(EXT, name)
    if os.path.exists(outer):
        src = read(outer)
        if not os.path.exists(inner) or read(inner) != src:
            os.makedirs(EXT, exist_ok=True)
            with open(inner, "w", encoding="utf-8", newline="") as f:
                f.write(src)
        return src
    return read(inner)


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def once(src, old, new, label):
    n = src.count(old)
    if n != 1:
        raise SystemExit("build_preshow: %s matched %d times (expected 1)" % (label, n))
    return src.replace(old, new)


def patch_c2(js):
    # 1. nothing runs when the pre-show is skipped
    js = once(js, "(function () {\n  'use strict';\n  const G = window.PS_G",
              "(function () {\n  'use strict';\n  if (window.BNG_NOPRESHOW) return;\n  const G = window.PS_G", "guard")
    # 2. colours from the deck's variables, no dark stage
    js = once(js, "const DARK = Q.get('stage') === 'dark';", "const DARK = false;", "DARK")
    js = once(js, "const COL = { canvas: '#FAFAF8', ink: '#0B0B0B', white: '#FFFFFF', green: '#10B981' };",
              "const COL = { canvas: 'var(--color-background-neutral-canvas)', ink: 'var(--color-text-neutral-bold)', white: 'var(--color-text-on-action-bold)', green: 'var(--color-background-signature-bold)' };\n"
              "  const LANG = (window.BNG_DECK && window.BNG_DECK.lang) || 'en', UI = window.BNG_FR_UI || {};", "COL")
    # 3. ids
    ids = set(re.findall(r"getElementById\('([A-Za-z-]+)'\)", js))
    want = {"stage", "scene", "parts", "wmSwap", "dotG", "lightLayer", "floodC", "opener", "line", "rmLayer", "veil", "hint-sound", "hint-go", "lightUse"}
    if ids != want:
        raise SystemExit("build_preshow: element ids changed: %s" % sorted(ids ^ want))
    js = re.sub(r"getElementById\('([A-Za-z-]+)'\)", r"getElementById('ps-\1')", js)
    # 4. sound: the module in preshow_audio.js replaces the prototype's Snd (the block from "const Snd = {" to "const SPEC")
    a, b = js.index("  let hintEl, goEl, hintTimer, goTimer;"), js.index("  const SPEC = {")
    js = js[:a] + "  let hintEl, goEl, hintTimer, goTimer, done = false;\n  function setHint() {}\n  function showHint() {}\n  function hideGo() { document.body.classList.remove('go-on'); }\n  const Snd = window.BNG_AUDIO;\n" + js[b:]
    js = once(js, "hintEl = document.getElementById('ps-hint-sound'); goEl = document.getElementById('ps-hint-go');",
              "goEl = document.getElementById('ps-hint-go');\n"
              "  goEl.textContent = (window.matchMedia && matchMedia('(pointer: coarse)').matches) ? (LANG === 'fr' ? UI.preshow_tap : 'Tap to start') : (LANG === 'fr' ? UI.preshow_start : 'Press space to start');", "hints")
    js = once(js, "lineEl.textContent = G.OPENER.text;", "lineEl.textContent = LANG === 'fr' ? UI.preshow_line : G.OPENER.text;", "line text")
    # 5. keys: Space / Enter / right arrow start the show; S and M belong to the audio module; nothing after the hand-over
    js = once(js, "window.addEventListener('keydown', (e) => {\n    if (e.repeat) return;", "window.addEventListener('keydown', (e) => {\n    if (e.repeat || done) return;", "keydown guard")
    js = once(js, "\n    else if (e.code === 'KeyS') { hideGo(); Snd.enable(); if (Snd.ctx && !Snd.on) Snd.on = true; }\n    else if (e.code === 'KeyM') { Snd.mute(); }", "", "S and M keys")
    js = once(js, "hintEl.addEventListener('click', (e) => { e.stopPropagation(); Snd.enable(); });",
              "goEl.addEventListener('click', (e) => { e.stopPropagation(); if (done) return; hideGo(); advance(); });", "go button")
    js = once(js, "document.body.classList.add('go-on'); goTimer = setTimeout(() => document.body.classList.remove('go-on'), 14000);\n  showHint(8000);",
              "document.body.classList.add('go-on');", "go hint")
    # 6. hand-over to the deck
    js = once(js, "document.body.classList.remove('dark'); veil.style.opacity = 0; svg.style.setProperty('--ink', COL.ink);\n  }",
              "document.body.classList.remove('dark'); veil.style.opacity = 0; svg.style.setProperty('--ink', COL.ink);\n"
              "    done = true; if (window.BNG_PRESHOW_REST) window.BNG_PRESHOW_REST();\n  }", "enterRest")
    return js


BOOT = """/* hand-over: the transition has landed on the opener; the deck shows the same opener underneath, then the overlay goes */
window.BNG_PRESHOW = !window.BNG_NOPRESHOW;
window.BNG_PRESHOW_REST = function () {
  if (window.BNG_PRESHOW_REST.done) return; window.BNG_PRESHOW_REST.done = true;
  var ps = document.getElementById('preshow');
  if (window.BNG_DECK) window.BNG_DECK.start({ quiet: true });
  if (window.BNG_AUDIO) window.BNG_AUDIO.deck();
  requestAnimationFrame(function () { requestAnimationFrame(function () { if (ps) ps.hidden = true; }); });
};
"""


def build(out_dir):
    audio = read(os.path.join(SITE, "src", "preshow_audio.js"))
    geo = pre("geometry.js")
    c2 = patch_c2(pre("c2.js"))
    js = audio + "\n" + BOOT + "\n" + geo + "\n" + c2
    with open(os.path.join(out_dir, "preshow.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write(js)
    return len(js)


if __name__ == "__main__":
    out = os.path.join(SITE, "public")
    print("preshow.js", build(out), "bytes")
