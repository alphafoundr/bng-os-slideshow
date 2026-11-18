"""Sample the deck's timed entrances in Chrome. Usage: python tools/check_sequence.py <port>."""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{sys.argv[1]}/?nopreshow=1"
OUT = Path(__file__).parent / "_sequence"
FRAMES = {
    "s12": (0.4, 1.3, 2.6, 3.8, 4.8, 5.55, 6.15, None),
    "s14": (0.4, 1.25, 2.5, 3.3, 4.45, 5.35, 6.4, None),
    "s15": (0.4, 1.25, 3.1, 3.9, 5.05, 5.95, 7.0, None),
    "s16": (0.4, 1.25, 2.2, 2.7, 3.85, 4.75, 5.8, None),
}

PROBE = """
window.sequenceRuns = {};
window.sequenceSnapshot = slide => [...slide.querySelectorAll('[data-seq]')].map(el => {
  const path = el.querySelector(':scope > mask path');
  let opacity = 1;
  for (let node = el; node !== slide; node = node.parentElement) opacity *= +getComputedStyle(node).opacity;
  return [opacity, path ? +parseFloat(getComputedStyle(path).strokeDashoffset).toFixed(3) : null];
});
new MutationObserver(changes => {
  for (const {target: slide} of changes) {
    const key = slide.dataset.key;
    if (slide.dataset.sequence !== 'playing' || sequenceRuns[key]) continue;
    const elements = [...slide.querySelectorAll('[data-seq]')];
    const info = elements.map(el => ({...JSON.parse(el.dataset.seq), name: el.dataset.name || el.textContent}));
    const run = sequenceRuns[key] = {info, samples: [], start: performance.now()};
    function sample() {
      const t = performance.now() - run.start;
      run.samples.push({t, values: sequenceSnapshot(slide)});
      if (slide.dataset.sequence === 'complete' || t >= 10000) {
        run.done = true;
        run.complete = slide.dataset.sequence === 'complete';
      } else setTimeout(sample, Math.max(0, run.samples.length * 100 - t));
    }
    sample();
  }
}).observe(document, {subtree: true, attributes: true, attributeFilter: ['data-sequence']});
"""


def check_samples(key, run):
    info, samples = run["info"], run["samples"]
    assert run["complete"] and samples[-1]["t"] < 10000, (key, samples[-1]["t"])
    first, last = samples[0]["values"], samples[-1]["values"]
    names = {part["name"]: i for i, part in enumerate(info)}
    starts, strokes = {}, {}
    for i, part in enumerate(info):
        assert last[i] == [1, None] or (part["motion"] == "draw" and last[i][1] is None and last[i][0] > 0), (key, part, last[i])
        if part["motion"] == "draw":
            original = abs(first[i][1])
            assert original > 0, (key, part)
            offsets = [(s["t"], abs(s["values"][i][1] or 0)) for s in samples]
            assert all(a[1] >= b[1] - 0.02 for a, b in zip(offsets, offsets[1:])), (key, part, offsets)
            strokes[i] = next(t for t, offset in offsets if offset < original - 0.02)
            for name in [part["target"], *(stop[2] for stop in part["via"])]:
                if name:
                    target = names[name]
                    assert all(s["values"][target][0] < 0.02 for s in samples if s["t"] < strokes[i]), (key, part, name)
            if part["target"]:
                arrival = next(t for t, offset in offsets if offset < 0.1)
                visible = next(s["t"] for s in samples if s["values"][names[part["target"]]][0] >= 0.02)
                assert arrival <= visible, (key, part, arrival, visible)
        else:
            assert first[i][0] < 0.02, (key, part)
            starts[i] = next(s["t"] for s in samples if s["values"][i][0] >= 0.02)

    def ordered(indices, times, order):
        groups = {}
        for i in indices:
            groups.setdefault(order(info[i]), []).append(times[i])
        for a, b in zip(sorted(groups), sorted(groups)[1:]):
            assert max(groups[a]) <= min(groups[b]), (key, a, b, groups)

    ordered((i for i in starts if info[i]["motion"] == "part"), starts, lambda part: part["step"])
    ordered((i for i in starts if info[i]["motion"] == "row"), starts, lambda part: (part["step"], part["index"]))
    ordered(strokes, strokes, lambda part: part["step"])
    return samples[-1]["t"] / 1000


def check_rest(page, key, expected):
    slide = page.locator(f'.slide[data-key="{key}"]')
    assert page.locator("body").get_attribute("data-slide") == key, key
    assert slide.get_attribute("data-sequence") == "complete", key
    assert slide.evaluate("el => sequenceSnapshot(el)") == expected, key


def advance(page, key, control):
    if control == "pager":
        page.locator(f'[data-key="{key}"] .pager.next').click()
    else:
        page.keyboard.press(control)


def main():
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="no-preference")
        page.add_init_script(PROBE)
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(BASE)
        keys = page.locator(".slide").evaluate_all("els => els.map(el => el.dataset.key)")
        sequenced = page.locator(".slide:has([data-seq])").evaluate_all("els => els.map(el => el.dataset.key)")
        assert set(sequenced) == set("s01 s02 s03 s04 s05 s06 s08 s09 s10 s11 s12 s13 s14 s15 s16 s18 s19 s20 s21 s22 s23 s24 s25 s26".split()), sequenced
        priority = ("s14", "s15", "s16", "s12")
        sequenced = sys.argv[2:] or [*priority, *(key for key in sequenced if key not in priority)]
        expected = {}
        for i, key in enumerate(sequenced):
            # The longest sequence also exercises the full slide transition.
            if key == "s04":
                page.goto(f"{BASE}&run={i}-play#s03")
                page.keyboard.press("ArrowRight")
                page.keyboard.press("ArrowRight")
            else:
                page.goto(f"{BASE}&run={i}-play#{key}")
            for frame, t in enumerate(FRAMES.get(key, ()), 1):
                page.wait_for_function(
                    "([k, t]) => sequenceRuns[k] && (t === null ? sequenceRuns[k].done : performance.now() - sequenceRuns[k].start >= t * 1000)",
                    arg=[key, t],
                )
                page.screenshot(path=str(OUT / f"{key}-{frame}.png"))
            page.wait_for_function("k => sequenceRuns[k]?.done", arg=key, timeout=11000)
            run = page.evaluate("k => sequenceRuns[k]", key)
            duration = check_samples(key, run)
            expected[key] = run["samples"][-1]["values"]

            page.goto(f"{BASE}&run={i}-skip#{key}")
            page.wait_for_function("k => sequenceRuns[k]?.samples.length >= 12", arg=key)
            assert page.locator(f'[data-key="{key}"]').get_attribute("data-sequence") == "playing", key
            control = ("ArrowRight", "Space", "pager")[i % 3]
            advance(page, key, control)
            check_rest(page, key, expected[key])
            successor = keys[keys.index(key) + 1]
            advance(page, key, control)
            assert page.locator("body").get_attribute("data-slide") == successor, key
            page.keyboard.press("ArrowLeft")
            check_rest(page, key, expected[key])
            print(f"PASS {key}: {duration:.2f} s sampled, {control} completes then advances, back stays complete", flush=True)

        reduced = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        reduced.add_init_script(PROBE)
        reduced.goto(BASE)
        for key in sequenced:
            reduced.evaluate("key => BNG_DECK.goKey(key)", key)
            check_rest(reduced, key, expected[key])
        assert reduced.evaluate("Object.keys(sequenceRuns).length") == 0
        assert not errors, errors
        browser.close()
    print(f"PASS: {len(sequenced)} sequences, reduced motion, {sum(len(FRAMES.get(key, ())) for key in sequenced)} filmstrip frames")


if __name__ == "__main__":
    main()
