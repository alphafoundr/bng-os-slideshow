"""Build the public BNG OS page (Cloudflare Worker static assets, https://bng-os.alphafoundr.com).

usage:  python -P build_site.py            confirmed slides only (production)
        python -P build_site.py --all      confirmed + provisional slides (review build)
Then:   CLOUDFLARE_ACCOUNT_ID=555854df7c51db1f32a3e8d1b7dd0425 npx wrangler deploy

Source of truth for slide content is Figma (file 20hUXLgkPbzRYaJVOe6wNI, page 4:2): src/data/*.json hold the
node records read from it, src/deck.json the order and status, src/fr.json the French strings (written by hand).
The build FAILS when a visible string has no French entry, when a colour is not a known token, or when an
icon / image / logo is not mapped. Output goes to ./public (wrangler.jsonc points at it).
"""
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
OUT = os.path.join(HERE, "public")
sys.path.insert(0, SRC)
import render as R  # noqa: E402
from data.gen_connected_exports import schedule  # noqa: E402

ALL = "--all" in sys.argv


def load(name):
    with open(os.path.join(SRC, name), "r", encoding="utf-8") as f:
        return json.load(f)


def read(name):
    with open(os.path.join(SRC, name), "r", encoding="utf-8") as f:
        return f.read()


def ext(rel):
    """An input kept outside this folder (the brand kit, the deck's shared images). Where the outer folder exists it is the
    source and is mirrored into src/ext/; a clone of the repository has no outer folder and builds from src/ext/ alone."""
    outer, inner = os.path.join(HERE, "..", rel), os.path.join(SRC, "ext", rel)
    if os.path.exists(outer):
        with open(outer, "rb") as f:
            new = f.read()
        old = None
        if os.path.exists(inner):
            with open(inner, "rb") as f:
                old = f.read()
        if new != old:
            os.makedirs(os.path.dirname(inner), exist_ok=True)
            shutil.copy2(outer, inner)
    return inner


PARTS = [("The case", 4), ("The turn", 1), ("The product", 5), ("The gains", 1), ("Close", 2)]


def nav_html(chapter, ctx, in_footer, section):
    part_of = []
    for pi, (_, n) in enumerate(PARTS):
        part_of += [pi] * n
    cur_part = part_of[chapter - 1]
    label, fr = ctx.s.attrs(section)
    segs = []
    c = 0
    for pi, (_, n) in enumerate(PARTS):
        items = []
        for _ in range(n):
            c += 1
            state = "cur" if c == chapter else ("past" if c < chapter else "next")
            items.append('<i class="seg %s" data-ch="%d"></i>' % (state, c))
        segs.append('<span class="part">%s</span>' % "".join(items))
    # the label is the part of the current slide; the other parts' names stay in data for the JS to swap
    names = json.dumps([[p, ctx.s.fr.get(p, p)] for p, _ in PARTS], ensure_ascii=False)
    for p, _ in PARTS:
        ctx.s.attrs(p)
    # Khalid, 2026-11-17: the wordmark sits top left and the bottom left holds a title only. On a slide with a footer the part name is that
    # title (class ftitle, returned separately) and the chapter bar stands alone; a slide without a footer keeps the name beside the bar.
    lab = '<span class="%s s-eyebrow-sm"%s>%s</span>' % ("ftitle" if in_footer else "nav-label", fr, label)
    nav = ('<nav class="nav" aria-label="Chapters" data-parts=\'%s\'>%s<span class="segs">%s</span></nav>'
           % (names.replace("'", "&#39;"), "" if in_footer else lab, "".join(segs)))
    return nav, (lab if in_footer else "")


def lede_html(txt, ctx, cls):
    body, fr = ctx.s.attrs(txt)
    return '<p class="%s"%s>%s</p>' % (cls, fr, body)


# The reveal between the last problem and the system (Khalid, 2026-11-17: "should we do something like animate the O of the OS logo there
# with the dot?" ... "looks great, let's integrate it"): the seven tools of slide 03, as the same tool discs, are pulled into the O and become
# its one dot. Site-only (no Figma frame). Name and icon per tool are slide 03's; motion is src/reveal.js.
REVEAL_TOOLS = [("BNG Business", "coin"), ("Nexus Panthera", "users"), ("Fame", "megaphone"), ("Vertex", "building"),
                ("BNG Sales Monitor", "bar-chart"), ("my.bngimmo.com", "smartphone"), ("Synergy", "circle-ask")]
REVEAL_LINE = "One system, above the tools you already have."


def reveal_html(ctx):
    import re
    wm = ctx.logos["Wordmark"]
    vb = re.search(r'viewBox="([^"]+)"', wm).group(1)
    paths = re.findall(r'<path d="([^"]+)"/>', wm)
    core = re.search(r'<circle[^>]*cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"', wm)
    # the wordmark's own geometry, never redrawn: B, N, G, the O (two halves) and S, plus the core
    assert len(paths) == 5 and core and paths[3].count("ZM") == 1, "wordmark-full-light.svg changed shape: update reveal_html"
    top, bot = paths[3].split("ZM")
    parts = ['<path class="rv-l" data-k="%s" d="%s"/>' % (k, paths[i]) for k, i in (("B", 0), ("N", 1), ("G", 2), ("S", 4))]
    parts += ['<path class="rv-ot" d="%sZ"/>' % top, '<path class="rv-ob" d="M%s"/>' % bot,
              '<circle class="rv-core" cx="%s" cy="%s" r="0" data-r="%s"/>' % core.groups()]
    tools = []
    for name, icon in REVEAL_TOOLS:
        body, fr = ctx.s.attrs(name)
        ctx.used_icons.add(icon)
        ico = ctx.icons[icon].replace("<svg ", '<svg class="rv-ico" x="-15" y="-15" width="30" height="30" ', 1)
        tools.append('<g class="rv-tool"><circle class="rv-disc" r="35"/>%s<text class="rv-label s-body-lg" y="63" text-anchor="middle"%s>%s</text></g>'
                     % (ico, fr, body))
    line, lfr = ctx.s.attrs(REVEAL_LINE)
    return ('<svg class="rv" role="img" aria-label="BNG OS" data-vb="%s"><g class="rv-tools">%s</g><g class="rv-wm">%s</g>'
            '<text class="rv-line s-body-lede-lg" text-anchor="middle"%s>%s</text></svg>' % (vb, "".join(tools), "".join(parts), lfr, line))


def chrome(slide, ctx, idx, total_label):
    p = slide["props"]
    out = []
    if slide["kind"] == "reveal":
        out.append(reveal_html(ctx))
    show_nav = p.get("Show nav", True)
    show_title = p.get("Show title column", True)
    show_footer = p.get("Show footer", True)
    ftitle = ""
    if show_nav:
        nav, ftitle = nav_html(slide["chapter"], ctx, show_footer, slide["section"])
        out.append(nav)
    if show_footer:
        out.append('<span class="wm">%s</span>' % ctx.logos["Wordmark"])
    if show_title:
        eb, ebfr = ctx.s.attrs(p["Eyebrow"])
        # titles are translated as a whole, line breaks included
        tbody, tfr = ctx.s.attrs(p["Title"])
        lede = ""
        if p.get("Show lede"):
            lede = lede_html(p["Lede"], ctx, "lede s-body-lg")
        out.append('<div class="titlecol"><div class="tblock"><p class="eyebrow s-eyebrow-md"%s>%s</p>'
                   '<h1 class="title s-heading-title"%s>%s</h1>%s</div></div>' % (ebfr, eb, tfr, tbody, lede))
    out.append('<div class="slot">%s</div>' % "".join(R.render_node(c, ctx, None) for c in slide["ch"]))
    if show_footer:
        note = ""
        if p.get("Show note"):
            nb, nfr = ctx.s.attrs(p["Note"])
            note = '<span class="note s-body-xs"%s>%s</span>' % (nfr, nb)
        num = p.get("Number", "")
        out.append('<div class="frule"></div><footer class="foot"><div class="fl">%s%s</div>'
                   '<div class="fr"><span class="num s-body-sm">%s</span>'
                   '<button class="pager prev" aria-label="Previous slide">%s</button>'
                   '<button class="pager next" aria-label="Next slide">%s</button></div></footer>'
                   % (ftitle, note, num, ctx.icons["left-arrow"], ctx.icons["right-arrow"]))
        ctx.used_icons.update(["left-arrow", "right-arrow"])
    return "".join(out)


def main():
    deck = load("deck.json")
    styles = load("data/_styles.json")
    fr = {}
    for fn in sorted(os.listdir(os.path.join(SRC, "fr"))):  # one French table per slide plus common.json
        if fn.endswith(".json"):
            for k, v in load("fr/" + fn).items():
                if k in fr and fr[k] != v:
                    print("note: '%s' translated twice differently (%s / %s); the later file wins" % (k[:40], fr[k][:30], v[:30]))
                fr[k] = v
    icons = load("icons.json")
    images = load("images.json")
    with open(ext("brand-kit/svg/wordmark-full-light.svg"), encoding="utf-8") as lf:
        logos = {"Wordmark": lf.read().replace("<svg ", '<svg class="wmk" ', 1)}
    for k, path in load("logos.json").items():
        with open(ext(path), encoding="utf-8") as lf:
            logos[k] = lf.read()
    strings = R.Strings(fr)
    ctx = R.Ctx(strings, styles, icons, images, logos)

    slides_html = []
    nav_index = []
    img_used = set()
    i = 0
    for entry in deck:
        if entry["status"] == "provisional" and not ALL:
            continue
        strings.slide = entry["key"]
        slide = load("data/%s.json" % entry["file"])
        schedule(entry["file"], slide["ch"])
        slide["chapter"] = entry["chapter"]
        slide["section"] = entry["section"]
        slide["kind"] = entry.get("kind", "slide")
        body = chrome(slide, ctx, i, "")
        slides_html.append('<section class="slide kind-%s" data-key="%s" data-ch="%d" data-status="%s" hidden>'
                           '<div class="art">%s</div></section>' % (slide["kind"], entry["key"], entry["chapter"], entry["status"], body))
        nav_index.append({"key": entry["key"], "ch": entry["chapter"]})
        i += 1

    if strings.missing:
        print("FAIL: %d visible strings have no French entry:" % len(set(strings.missing)))
        for s in sorted(set(strings.missing)):
            print("  -", repr(s))
        sys.exit(1)

    # ---- assemble ----
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    for d in ("fonts", "vendor", "audio", "img"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    for f in os.listdir(os.path.join(SRC, "fonts")):
        shutil.copy2(os.path.join(SRC, "fonts", f), os.path.join(OUT, "fonts", f))
    for f in ("gsap-3.15.1.min.js", "gsap-LICENSE.txt", "matter-0.20.0.min.js", "matter-LICENSE.txt"):
        shutil.copy2(os.path.join(SRC, "vendor", f), os.path.join(OUT, "vendor", f))
    for f in load("audio.json"):
        shutil.copy2(os.path.join(SRC, "audio", f), os.path.join(OUT, "audio", f))
    for f in sorted(set(images.values())):
        # raster art: the generated, labelled-fictional images of the deck (slideshow/img), same files the Figma file uses
        s = os.path.join(SRC, f)
        if not os.path.exists(s):
            s = ext("slideshow/" + f)
        shutil.copy2(s, os.path.join(OUT, f))


    css = R.css_vars() + "\n" + R.style_classes(styles) + "\n" + read("deck.css")
    tmpl = read("index.tmpl.html")
    page = (tmpl.replace("/*CSS*/", css)
            .replace("<!--SLIDES-->", "\n".join(slides_html))
            .replace("/*FR_UI*/", json.dumps(load("fr_ui.json"), ensure_ascii=False)))
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    shutil.copy2(os.path.join(SRC, "deck.js"), os.path.join(OUT, "deck.js"))
    shutil.copy2(os.path.join(SRC, "reveal.js"), os.path.join(OUT, "reveal.js"))
    sys.path.insert(0, os.path.join(HERE, "tools"))
    import build_preshow  # noqa: E402  (preshow.js is generated from the prototype, see its docstring)
    build_preshow.build(OUT)
    with open(os.path.join(OUT, "_headers"), "w", encoding="utf-8", newline="\n") as f:
        f.write("/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n  Referrer-Policy: no-referrer\n"
                "  X-Content-Type-Options: nosniff\n/audio/*\n  Cache-Control: public, max-age=86400\n")
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("User-agent: *\nDisallow: /\n")
    total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs)
    print("built %d slides (%s), %d strings, %d icons, %.1f MB -> public/" % (
        len(slides_html), "all" if ALL else "confirmed only", len(strings.used), len(ctx.used_icons), total / 1048576))


if __name__ == "__main__":
    main()
