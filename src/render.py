"""Figma-data -> HTML renderer for the BNG OS deck.

Input: the compact node records saved in src/data/*.json (read from Figma, node by node).
Output: HTML strings. Every colour is a CSS variable, every text style a class, every
visible string goes through Strings so the build can refuse a missing French entry.
"""
import html
import json
import re

# ---- colour tokens (Light mode of the Figma Color collection; mirror of DESIGN.md Colors) ----
COLORS = {
    "background/neutral/canvas": "#FAFAF8", "background/neutral/raised": "#FFFFFF",
    "background/neutral/subtle": "#F5F5F1", "background/neutral/muted": "#E8E8E4",
    "background/neutral/track": "#E8E8E4", "background/neutral/placeholder": "#E0E0DC",
    "background/neutral/rail": "#F5F5F1", "background/neutral/input": "#FFFFFF",
    "background/neutral/hover": "#EFEFEB", "background/neutral/selected": "#E8E8E4",
    "background/neutral/pressed": "#E0E0DC", "background/neutral/disabled": "#EFEFEB",
    "background/neutral/tag": "#E0E0DC", "background/neutral/strong": "#D4D4D0",
    "background/neutral/suggested": "#EFEFEB", "background/neutral/progress": "#74746F",
    "background/neutral/done": "#565552",
    "background/inverse/bold": "#0B0B0B", "background/action/bold": "#0B0B0B",
    "background/action/hovered": "#393937", "background/action/pressed": "#565552",
    "background/action/disabled": "#E0E0DC",
    "background/success/bold": "#447202", "background/success/subtle": "#E3F9D3",
    "background/signature/bold": "#10B981", "background/danger/bold": "#DC2626",
    "background/danger/subtle": "#FEE2E2",
    "chart/neutral/primary": "#0B0B0B", "chart/neutral/secondary": "#74746F",
    "chart/neutral/track": "#E8E8E4", "chart/danger/bold": "#DC2626",
    "text/neutral/bold": "#0B0B0B", "text/neutral/subtle": "#393937",
    "text/neutral/subtlest": "#565552", "text/neutral/faint": "#A3A39E",
    "text/neutral/placeholder": "#74746F", "text/neutral/disabled": "#A3A39E",
    "text/on-done/bold": "#FFFFFF", "text/inverse/bold": "#FFFFFF", "text/inverse/subtle": "#A3A39E",
    "text/on-action/bold": "#FFFFFF", "text/on-action/disabled": "#74746F",
    "text/on-danger/bold": "#FFFFFF", "text/success/bold": "#32520F",
    "text/danger/bold": "#991B1B", "text/danger/subtle": "#DC2626",
    "icon/neutral/bold": "#0B0B0B", "icon/neutral/subtle": "#565552", "icon/neutral/subtlest": "#74746F",
    "icon/neutral/disabled": "#A3A39E", "icon/inverse/bold": "#FFFFFF",
    "icon/on-action/bold": "#FFFFFF", "icon/success/bold": "#447202", "icon/signature/bold": "#10B981",
    "icon/danger/bold": "#DC2626", "icon/on-danger/bold": "#FFFFFF",
    "border/neutral/subtle": "#E8E8E4", "border/neutral/default": "#D4D4D0", "border/neutral/bold": "#8B8B86",
    "border/neutral/suggested": "#D4D4D0", "border/inverse/bold": "#0B0B0B",
    "border/signature/bold": "#10B981", "border/success/bold": "#447202", "border/danger/subtle": "#FEE2E2",
    "overlay/neutral/halo": "#0B0B0B0F",
}
RADII = {4: "var(--r-sm)", 8: "var(--r-md)", 12: "var(--r-lg)", 40: "var(--r-device)", 999: "var(--r-full)"}


def cvar(name):
    if name.startswith("#"):
        raise ValueError("raw colour %s in Figma data: bind it to a variable in Figma first" % name)
    if name not in COLORS:
        raise KeyError("unknown colour token " + name)
    return "var(--color-%s)" % name.replace("/", "-")


def css_vars():
    lines = ["--color-%s:%s" % (k.replace("/", "-"), v) for k, v in COLORS.items()]
    return ":root{" + ";".join(lines) + ";--r-sm:4px;--r-md:8px;--r-lg:12px;--r-device:40px;--r-full:999px}"


class Strings:
    """Collects every visible string; resolves French from the table."""

    def __init__(self, fr):
        self.fr = fr
        self.used = {}
        self.missing = []

    def attrs(self, en):
        """Return (html-escaped EN text, data-fr attribute string)."""
        self.used[en] = True
        # a slide-specific entry ("@s18|Inbox") wins over the shared one when one English word means two things
        fr = self.fr.get("@%s|%s" % (getattr(self, "slide", ""), en))
        if fr is None:
            fr = self.fr.get(en)
        if fr is None:
            if en.strip() and re.search(r"[A-Za-z]", en):
                self.missing.append(en)
            return html.escape(en, quote=False), ""
        # French typography: no-break space before : ; ! ? % and inside « »
        fr = re.sub(r" ([:;!?%»])", " \\1", fr).replace("« ", "« ")
        return html.escape(en, quote=False), ' data-fr="%s"' % html.escape(fr, quote=True)


def style_classes(styles):
    out = []
    for name, (ff, fw, fs, lh, ls, tc) in styles.items():
        cls = "s-" + name.replace("/", "-")
        wt = {"Regular": 400, "Medium": 500, "SemiBold": 600, "Semi Bold": 600, "Bold": 700}[fw]
        fam = {"Bricolage Grotesque": "var(--font-display)", "Inter": "var(--font-ui)",
               "Instrument Sans": "var(--font-text)"}[ff]
        v = ""
        if ff == "Bricolage Grotesque":
            v = 'font-optical-sizing:auto;font-variation-settings:"wdth" 100;'
        elif ff == "Instrument Sans":
            v = 'font-variation-settings:"wdth" 100;'
        rule = "font-family:%s;font-weight:%d;font-size:%spx;%s%sletter-spacing:%spx;%s" % (
            fam, wt, fs, ("line-height:%spx;" % lh) if lh else "", v, ls,
            "text-transform:uppercase;" if tc == "UPPER" else "")
        out.append(".%s{%s}" % (cls, rule))
    return "\n".join(out)


def fmt(v):
    return ("%.2f" % v).rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


ALIGN = {"m": "flex-start", "c": "center", "x": "flex-end", "s": "space-between", "b": "baseline"}
FONTS = {"Bricolage Grotesque": "var(--font-display)", "Inter": "var(--font-ui)", "Instrument Sans": "var(--font-text)"}
WEIGHTS = {"Regular": 400, "Medium": 500, "SemiBold": 600, "Semi Bold": 600, "Bold": 700}


class Ctx:
    def __init__(self, strings, styles, icons, images, logos):
        self.s = strings
        self.styles = styles
        self.icons = icons
        self.images = images
        self.logos = logos
        self.uid = 0
        self.used_icons = set()

    def next(self):
        self.uid += 1
        return self.uid


def text_inline_style(n):
    st = []
    if "ff" in n:
        st.append("font-family:" + FONTS[n["ff"]])
        st.append("font-weight:%d" % WEIGHTS[n["fw"]])
        st.append("font-size:%spx" % fmt(n["fs"]))
        if n.get("lh"):
            st.append("line-height:%spx" % fmt(n["lh"]))
        st.append("letter-spacing:%spx" % fmt(n["ls"]))
        if n.get("tc") == "UPPER":
            st.append("text-transform:uppercase")
    return st


def seg_style(d):
    st = []
    if "f" in d and d["f"]:
        st.append("color:" + cvar(d["f"]["c"]))
    if "fw" in d:
        st.append("font-weight:%d" % WEIGHTS[d["fw"]])
    if "fs" in d:
        st.append("font-size:%spx" % fmt(d["fs"]))
    if "ls" in d:
        st.append("letter-spacing:%spx" % fmt(d["ls"]))
    if "ff" in d:
        st.append("font-family:" + FONTS[d["ff"]])
    return st


def left_style(n):
    # a vector with exw alone keeps its right end fixed (left end moves by exw); with exl as well, exl is the move of the left end and
    # exw the growth of the width (both ends may move: right end move = exl - exw)
    factor = n.get("exw") if n.get("t") == "V" and "exw" in n and "exl" not in n else n.get("exl")
    if factor is not None:
        return "left:calc(%spx - var(--ex) * %s)" % (fmt(n.get("x", 0)), fmt(factor))
    return "left:%spx" % fmt(n.get("x", 0))


def render_text(n, ctx, par):
    cls = ["tx"]
    if n.get("s"):
        cls.append("s-" + n["s"].replace("/", "-"))
    st = []
    pos_abs = par is None or not par.get("lm") or n.get("ab")
    if pos_abs:
        st.append("position:absolute")
        st.append(left_style(n))
        st.append("top:%spx" % fmt(n.get("y", 0)))
    else:
        st.append("position:relative")
        if "exl" in n:
            st.append(left_style(n))
    flex_in = par is not None and par.get("lm") and not n.get("ab")
    if "w" in n:
        st.append("width:%spx" % fmt(n["w"]))
        if flex_in:
            st.append("flex:none")
    if "h" in n:
        st.append("height:%spx" % fmt(n["h"]))
    if flex_in:
        if n.get("sh") == "L":
            if par["lm"] == "H":
                st.append("flex:1 1 0;min-width:0")
            else:
                st.append("align-self:stretch")
        if n.get("sv") == "L":
            if par["lm"] == "V":
                st.append("flex:1 1 0;min-height:0")
            else:
                st.append("align-self:stretch")
    if n.get("nw"):
        st.append("white-space:pre")
    elif "\n" in n.get("c", ""):
        st.append("white-space:pre-line")
    if n.get("al"):
        st.append("text-align:%s" % {"C": "center", "R": "right", "J": "justify"}[n["al"]])
    if n.get("va"):
        st.append("display:flex;align-items:%s" % ("center" if n["va"] == "c" else "flex-end"))
    if n.get("f"):
        st.append("color:" + cvar(n["f"]["c"]))
    if n.get("td") == "UNDERLINE":
        st.append("text-decoration:underline")
    st += text_inline_style(n)
    if n.get("m"):
        st.append("transform-origin:0 0;transform:matrix(%s,%s,%s,%s,0,0)" % tuple(n["m"]))
    if n.get("sg"):
        parts = []
        for d in n["sg"]:
            body, _ = ctx.s.attrs(d["c"])
            ss = seg_style(d)
            parts.append('<span%s>%s</span>' % (' style="%s"' % ";".join(ss) if ss else "", body))
        # whole-string translation replaces the segmented markup
        full = "".join(d["c"] for d in n["sg"])
        _, fr = ctx.s.attrs(full)
        return '<span class="%s" style="%s" data-en-html="%s"%s>%s</span>' % (
            " ".join(cls), ";".join(st), html.escape("".join(parts), quote=True), fr, "".join(parts))
    body, fr = ctx.s.attrs(n["c"])
    return '<span class="%s" style="%s"%s>%s</span>' % (" ".join(cls), ";".join(st), fr, body)


def render_vector(n, ctx, par):
    st = ["position:absolute", left_style(n), "top:%spx" % fmt(n.get("y", 0)),
          # an svg with a zero width or height is not rendered, so straight connectors get a 1px box (overflow stays visible)
          "width:%spx" % fmt(max(n.get("w", 0), 1)), "height:%spx" % fmt(max(n.get("h", 0), 1)), "overflow:visible"]
    if "exw" in n:
        st[3] = "width:calc(%spx + var(--ex) * %s)" % (fmt(n["w"]), fmt(n["exw"]))
    if n.get("m"):
        st.append("transform-origin:0 0;transform:matrix(%s,%s,%s,%s,0,0)" % tuple(n["m"]))
    if n.get("op") is not None:
        st.append("opacity:%s" % fmt(n["op"]))
    name = n.get("n", "")
    attrs = ' data-name="%s"' % html.escape(name, quote=True)
    if "exw" in n:
        attrs += ' viewBox="0 0 %s %s" preserveAspectRatio="none"' % (fmt(n["w"]), fmt(max(n["h"], 1)))
    kind = "connector" if name.startswith("Connector") else "vec"
    if n.get("svg"):
        # exported fallback: keep the markup, drop width/height attributes so CSS sizes it
        svg = re.sub(r"<svg ", '<svg class="vec raw" style="%s" ' % ";".join(st), n["svg"], count=1)
        return svg
    paths = []
    ids = ctx.next()
    for d in n.get("d", []):
        rule = ""
        m = re.match(r"^(EVENODD|NONZERO)\s+(.*)$", d)
        if m:
            rule, d = ' fill-rule="%s"' % m.group(1).lower(), m.group(2)
        fill = cvar(n["f"]["c"]) if n.get("f") else "none"
        stroke = ""
        if n.get("sk"):
            stroke = ' stroke="%s" stroke-width="%s"' % (cvar(n["sk"]["c"]), fmt(n["sw"]))
            if n.get("da"):
                stroke += ' stroke-dasharray="%s"' % " ".join(fmt(x) for x in n["da"])
            stroke += ' stroke-linecap="%s" stroke-linejoin="%s"' % (
                {"ROUND": "round", "SQUARE": "square"}.get(n.get("cap"), "butt"),
                {"ROUND": "round", "BEVEL": "bevel"}.get(n.get("jn"), "miter"))
        if "exw" in n:
            stroke += ' vector-effect="non-scaling-stroke"'
        paths.append('<path d="%s" fill="%s"%s%s/>' % (d, fill, rule, stroke))
    if n.get("ln"):
        stroke = ' stroke="%s" stroke-width="%s"' % (cvar(n["sk"]["c"]), fmt(n["sw"]))
        if "exw" in n:
            stroke += ' vector-effect="non-scaling-stroke"'
        if n.get("da"):
            stroke += ' stroke-dasharray="%s"' % " ".join(fmt(x) for x in n["da"])
        paths.append('<line x1="0" y1="0" x2="%s" y2="0"%s/>' % (fmt(n["w"]), stroke))
    return '<svg class="%s" style="%s"%s>%s</svg>' % (kind, ";".join(st), attrs, "".join(paths))


def render_icon(n, ctx, par):
    name = n["ic"]
    ctx.used_icons.add(name)
    if name not in ctx.icons:
        raise KeyError("icon not exported yet: " + name)
    st = ["width:%spx" % fmt(n.get("w", 20)), "height:%spx" % fmt(n.get("h", 20)), "flex:none"]
    if par is None or not par.get("lm") or n.get("ab"):
        st += ["position:absolute", left_style(n), "top:%spx" % fmt(n.get("y", 0))]
    else:
        st.append("position:relative")
        if "exl" in n:
            st.append(left_style(n))
    col = n.get("f") and n["f"].get("c")
    if col:
        st.append("color:" + cvar(col))
    return '<span class="ic" data-icon="%s" style="%s">%s</span>' % (name, ";".join(st), ctx.icons[name])


def render_logo(n, ctx, par):
    key = json.dumps(n["vp"], sort_keys=True)
    cn = n.get("cn", "")
    svg = ctx.logos.get(cn + "|" + key) or ctx.logos.get(cn)
    if svg is None:
        raise KeyError("logo not mapped: %s %s" % (cn, key))
    st = ["width:%spx" % fmt(n["w"]), "height:%spx" % fmt(n["h"]), "flex:none"]
    if par is None or not par.get("lm") or n.get("ab"):
        st += ["position:absolute", left_style(n), "top:%spx" % fmt(n.get("y", 0))]
    else:
        st.append("position:relative")
        if "exl" in n:
            st.append(left_style(n))
    return '<span class="lg" data-logo="%s" style="%s">%s</span>' % (html.escape(cn), ";".join(st), svg)


def render_image_fill(f, n):
    h = f["im"]
    tr = f.get("tr")
    mode = f.get("sm")
    w, hh = n.get("w", 0), n.get("h", 0)
    return h, mode, tr, w, hh


def render_node(n, ctx, par=None, extra_cls=""):
    markup = node_markup(n, ctx, par, extra_cls)
    if "seq" in n:
        data = html.escape(json.dumps(n["seq"], ensure_ascii=False), quote=True)
        tag, space, rest = markup.partition(" ")
        return f'{tag} data-seq="{data}"{space}{rest}'
    return markup


def node_markup(n, ctx, par, extra_cls):
    t = n.get("t")
    if n.get("ic"):
        return render_icon(n, ctx, par)
    if n.get("lg"):
        return render_logo(n, ctx, par)
    if t == "T":
        return render_text(n, ctx, par)
    if t == "V":
        return render_vector(n, ctx, par)
    return render_box(n, ctx, par, extra_cls)


def render_box(n, ctx, par, extra_cls=""):
    st = ["position:relative"]
    cls = ["b"]
    if extra_cls:
        cls.append(extra_cls)
    flex_in = par is not None and par.get("lm") and not n.get("ab")
    pos_abs = (par is None or not par.get("lm") or n.get("ab"))
    if pos_abs:
        st = ["position:absolute", left_style(n), "top:%spx" % fmt(n.get("y", 0))]
    elif "exl" in n:
        st.append(left_style(n))
    if "w" in n:
        if "exw" in n:      # a card that grows with the screen: its left edge moves by exl, its width grows by exw
            st.append("width:calc(%spx + var(--ex) * %s)" % (fmt(n["w"]), fmt(n["exw"])))
        else:
            st.append("width:%spx" % fmt(n["w"]))
        if flex_in:
            st.append("flex:none")
    if "h" in n:
        st.append("height:%spx" % fmt(n["h"]))
        if flex_in:
            st.append("flex:none")
    if flex_in:
        main = par["lm"]
        if n.get("sh") == "L":
            if main == "H":
                st.append("flex:1 1 0;min-width:0")
            else:
                st.append("align-self:stretch")
        if n.get("sv") == "L":
            if main == "V":
                st.append("flex:1 1 0;min-height:0")
            else:
                st.append("align-self:stretch")
        if n.get("sh") == "H" and main == "H" or n.get("sv") == "H" and main == "V":
            st.append("flex:none")
    if n.get("sh") == "H" and pos_abs:
        st.append("width:max-content")
    if n.get("minw"):
        st.append("min-width:%spx" % fmt(n["minw"]))
    if n.get("maxw"):
        st.append("max-width:%spx" % fmt(n["maxw"]))
    if n.get("lm"):
        st.append("display:flex")
        st.append("flex-direction:%s" % ("row" if n["lm"] == "H" else "column"))
        if n.get("gap"):
            st.append("gap:%spx" % fmt(n["gap"]))
        pad = list(n.get("pad") or [0, 0, 0, 0])
        if n.get("sk") and not n.get("sa"):
            # Figma includes an inside stroke in auto-layout (every stroked auto-layout node in the file does)
            sw = n["sw"]
            sws = list(sw) if isinstance(sw, list) else [sw] * 4
            pad = [p + w for p, w in zip(pad, sws)]
        if any(pad):
            st.append("padding:%s" % " ".join("%spx" % fmt(p) for p in pad))
        st.append("justify-content:" + ALIGN[n.get("pa", "m")])
        st.append("align-items:" + ALIGN[n.get("ca", "m")])
        if n.get("wr"):
            st.append("flex-wrap:wrap")
            if n.get("cgap"):
                st.append("row-gap:%spx" % fmt(n["cgap"]))
        if n.get("gap") and n["gap"] < 0:
            # CSS has no negative gap: overlap by pulling every later child back
            st[st.index("gap:%spx" % fmt(n["gap"]))] = "gap:0"
            st.append("--ng:%spx" % fmt(n["gap"]))
            cls.append("ng-h" if n["lm"] == "H" else "ng-v")
    if n.get("m"):
        st.append("transform-origin:0 0;transform:matrix(%s,%s,%s,%s,0,0)" % tuple(n["m"]))
    if n.get("op") is not None:
        st.append("opacity:%s" % fmt(n["op"]))
    if n.get("k"):
        st.append("overflow:hidden")
    cr = n.get("cr")
    if cr is None and n.get("t") == "E":
        st.append("border-radius:50%")
    if cr is not None:
        if isinstance(cr, list):
            st.append("border-radius:%s" % " ".join(RADII.get(int(c), "%spx" % fmt(c)) for c in cr))
        else:
            st.append("border-radius:" + RADII.get(int(cr), "%spx" % fmt(cr)))
    fills = n.get("f") or []
    bg = [f for f in fills if "c" in f]
    if bg:
        st.append("background-color:" + cvar(bg[-1]["c"]))
    if n.get("sk"):
        sw = n["sw"]
        bw = " ".join("%spx" % fmt(x) for x in sw) if isinstance(sw, list) else "%spx" % fmt(sw)
        st.append("--bw:%s;--bc:%s;--bs:%s" % (bw, cvar(n["sk"]["c"]), "dashed" if n.get("da") else "solid"))
        cls.append("bd")
        if n.get("sa") == "OUTSIDE" and not n.get("k"):  # a clipped box (portrait) keeps the ring inside: overflow:hidden would hide an outside one
            cls.append("bdo")
    if n.get("kg"):
        cls.append("kg")
    nm = n.get("n")
    attrs = ""
    if n.get("cn"):
        attrs += ' data-c="%s"' % html.escape(n["cn"], quote=True)
    if nm:
        attrs += ' data-name="%s"' % html.escape(nm, quote=True)
    inner = ""
    for f in fills:
        if "im" in f:
            src = ctx.images.get(f["im"])
            if not src:
                raise KeyError("image hash not mapped: " + f["im"])
            tr = f.get("tr")
            if f["sm"] == "CROP" and tr:
                a, tx, d, ty = tr[0][0], tr[0][2], tr[1][1], tr[1][2]
                ist = "position:absolute;width:%s%%;height:%s%%;left:%s%%;top:%s%%;max-width:none" % (
                    fmt(round(100 / a, 3)), fmt(round(100 / d, 3)), fmt(round(-tx / a * 100, 3)), fmt(round(-ty / d * 100, 3)))
            else:
                ist = "position:absolute;inset:0;width:100%;height:100%;object-fit:" + ("contain" if f["sm"] == "FIT" else "cover")
            lazy = ' loading="lazy" decoding="async"' if f["sm"] in ("FILL", "FIT") else ""  # photos only; portraits are small and sit on the first slides
            inner += '<img alt="" draggable="false"%s src="%s" style="%s">' % (lazy, src, ist)
    for c in n.get("ch", []):
        inner += render_node(c, ctx, n)
    return '<div class="%s" style="%s"%s>%s</div>' % (" ".join(cls), ";".join(st), attrs, inner)
