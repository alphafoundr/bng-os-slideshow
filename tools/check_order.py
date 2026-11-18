"""Usage: python tools/check_order.py <port>. Walk every slide with ArrowRight."""
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright

ORDER = 'op s01 s02 s03 s04 s05 s06 s07 s08 s09 rv s10 s11 p1 s12 s13 s14 s15 s16 s18 s19 s20 s21 p2 s22 s24 s25 s17 s23 s26 s27'.split()
NUMBERS = {k: f'{i:02d} / 27' for i, k in enumerate(k for k in ORDER if k not in ('rv', 'p1', 'p2'))}
CHAPTERS = [1, 1, 1, 2, 3, 4, 4, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 8, 8, 9, 9, 10, 10, 11, 12, 13, 13]
out = Path(__file__).parent / '_order'
out.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
    page.goto(f'http://localhost:{sys.argv[1]}/?nopreshow=1')
    page.wait_for_function('window.BNG_DECK && BNG_DECK.index >= 0')
    seen = []
    for i, key in enumerate(ORDER):
        page.wait_for_function('(k) => document.body.dataset.slide === k', arg=key)
        seen.append(page.locator('body').get_attribute('data-slide'))
        slide = page.locator(f'.slide[data-key="{key}"]')
        assert slide.get_attribute('data-ch') == str(CHAPTERS[i]), key
        assert slide.locator('.seg').count() == (0 if key in ('op', 'rv') else 13), key
        if key not in ('op', 'rv'):
            assert slide.locator('.seg.cur').get_attribute('data-ch') == str(CHAPTERS[i]), key
            expected = ('The case' if key in ORDER[1:10] else
                        'The turn' if key in ('s10', 's11') else
                        'Close' if key in ('s23', 's26', 's27') else
                        'The gains' if key == 's17' else 'The product')
            assert slide.locator('.ftitle, .nav-label').inner_text().lower() == expected.lower(), key
        if key in NUMBERS and key != 'op':
            assert slide.locator('.num').is_visible(), key
            assert slide.locator('.num').inner_text() == NUMBERS[key], key
        else:
            assert slide.locator('.num:visible').count() == 0, key
        if key in ('s12', 's14', 's18', 's17', 's23'):
            page.screenshot(path=str(out / (key + '.png')))
        if i < len(ORDER) - 1:
            page.keyboard.press('ArrowRight')
    assert seen == ORDER, seen
    page.keyboard.press('ArrowRight')
    assert page.locator('body').get_attribute('data-slide') == ORDER[-1]
    browser.close()
print('PASS: 31 keys in order, 27 visible counters, unnumbered opener/pauses/reveal, 13 progress segments; five screenshots')
