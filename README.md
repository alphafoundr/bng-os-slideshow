# BNG OS slideshow

The presentation served at https://bng-os.alphafoundr.com (English and French, no login, not indexed).
It is a static page built by one Python script. People and figures on the slides are fictional and labelled so.

## Look at it locally

Needs Python 3.11+ (no packages for the build).

```powershell
python -P build_site.py
python -m http.server 8800 --directory public
```

Open http://localhost:8800. Add `?nopreshow=1` to skip the opening sequence, and `#s12` to land on a slide.
The build recreates `public/` each time, so start the server after building.

## Change something

| To change | Edit | Then |
|---|---|---|
| English text or layout of a slide | the slide's generator, `src/data/gen_*.py` | run it from `src/data` (see below), then build |
| French text | `src/fr/<slide>.json` (English string on the left, French on the right) | build |
| Slide order, or hiding a slide | `src/deck.json` | build |
| Styling, motion | `src/deck.css`, `src/deck.js`, `src/reveal.js` | build |

`src/data/<slide>.json` files are written by the generators: do not edit them by hand, the next generator run
overwrites them.

```powershell
cd src/data
$env:PYTHONPATH = "."
python -P gen_s15.py
cd ../..
python -P build_site.py
```

The build stops with a list when an English string has no French line. Add the missing lines to the slide's
file in `src/fr/` and build again.

## Checks

Need `pip install playwright` and Google Chrome. With the local server running on port 8800:

```powershell
python tools/check_deck.py 8800
python tools/check_reveal.py 8800
```

## Publishing

The live page is a Cloudflare Worker (`wrangler.jsonc`). Publishing is done from the owner's Cloudflare
account; pushing to this repository does not change the live page.

## Layout

- `build_site.py`: the build. `src/render.py`: turns slide records into HTML.
- `src/data/`: slide generators (`gen_*.py`, helpers in `dsl.py`) and their output.
- `src/fr/`: French strings. `src/deck.json`: order and chapters.
- `src/ext/`: the logo files and four portraits the build needs, mirrored from the design folders.
- `src/img/`, `src/fonts/`, `src/audio/`, `src/vendor/`: assets and third-party libraries (licences beside them).
- `tools/`: checks and screenshot helpers.
