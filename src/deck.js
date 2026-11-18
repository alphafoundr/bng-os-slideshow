/* BNG OS deck runtime: fit-to-viewport, navigation, EN/FR, slide motion. No network, no framework. */
(function () {
  'use strict';
  var deck = document.getElementById('deck');
  var slides = Array.prototype.slice.call(deck.querySelectorAll('.slide'));
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var FRUI = window.BNG_FR_UI || {};
  var cur = -1, busy = false, lang = 'en', tlIn = null;
  var store = {
    get: function (k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* private mode */ } }
  };

  /* ---------- fit 1440 x 900 to the viewport, letterboxed ---------- */
  function fit() {
    var w = window.innerWidth, h = window.innerHeight;
    var k = Math.min(w / 1440, h / 900);
    /* wider than 16:10: widen the artboard (up to 1920) instead of leaving side bars */
    var ex = Math.max(0, Math.min(480, Math.floor(w / k - 1440)));
    var W = 1440 + ex;
    deck.style.setProperty('--ex', ex + 'px');
    deck.style.transform = 'translate(' + ((w - W * k) / 2) + 'px,' + ((h - 900 * k) / 2) + 'px) scale(' + k + ')';
  }
  window.addEventListener('resize', fit);
  window.addEventListener('orientationchange', fit);
  fit();

  /* ---------- language ---------- */
  var frNodes = Array.prototype.slice.call(deck.querySelectorAll('[data-fr]'));
  frNodes.forEach(function (n) {
    n.setAttribute('data-en', n.hasAttribute('data-en-html') ? '' : n.textContent);
  });
  function setLang(l, persist) {
    lang = l === 'fr' ? 'fr' : 'en';
    document.documentElement.lang = lang;
    frNodes.forEach(function (n) {
      if (lang === 'fr') n.textContent = n.getAttribute('data-fr');
      else if (n.hasAttribute('data-en-html')) n.innerHTML = n.getAttribute('data-en-html');
      else n.textContent = n.getAttribute('data-en');
    });
    Array.prototype.forEach.call(document.querySelectorAll('.ui [data-lang]'), function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-lang') === lang ? 'true' : 'false');
    });
    Array.prototype.forEach.call(document.querySelectorAll('.pager.prev'), function (b) { b.setAttribute('aria-label', lang === 'fr' ? FRUI.prev : 'Previous slide'); });
    Array.prototype.forEach.call(document.querySelectorAll('.pager.next'), function (b) { b.setAttribute('aria-label', lang === 'fr' ? FRUI.next : 'Next slide'); });
    updateSoundLabel();
    if (persist) {
      store.set('bng-os-lang', lang);
      try { var u = new URL(window.location.href); u.searchParams.set('lang', lang); window.history.replaceState(null, '', u); } catch (e) { /* ignore */ }
    }
  }
  function initialLang() {
    var q = null;
    try { q = new URL(window.location.href).searchParams.get('lang'); } catch (e) { /* ignore */ }
    if (q === 'fr' || q === 'en') return q;
    var s = store.get('bng-os-lang');
    return s === 'fr' || s === 'en' ? s : 'en';
  }

  /* ---------- sound label (the audio itself lives in preshow.js) ---------- */
  function updateSoundLabel() {
    var b = document.getElementById('snd');
    if (!b) return;
    var muted = !!(window.BNG_AUDIO && window.BNG_AUDIO.muted);
    b.setAttribute('aria-pressed', muted ? 'false' : 'true');
    var k = b.querySelector('[data-k=sound]'), st = b.querySelector('[data-k=state]');
    k.textContent = lang === 'fr' ? FRUI.sound : 'Sound';
    st.textContent = lang === 'fr' ? (muted ? FRUI.off : FRUI.on) : (muted ? 'off' : 'on');
  }
  window.addEventListener('bng:audio', updateSoundLabel);

  /* ---------- motion ---------- */
  var DUR = { slide: 0.95 }, FRAME = ['.nav', '.wm', '.frule', '.foot'], finish = null;
  var SEQUENCE = {
    header: 0.72, beat: 0.60, draw: 0.48, part: 0.35, rise: 6,
    dotLead: 0.06, dot: 0.08, labelLead: 0.12, row: 0.18, rowGap: 0.18,
    finishDraw: 0.12, approach: 12
  };
  var sequence = null, seen = new Set(), maskId = 0;

  function buildSequence(slide, nodes, sliding) {
    var cfg = SEQUENCE, G = window.gsap, restore = [];
    var lead = sliding ? DUR.slide : cfg.header;
    var tl = G.timeline({ paused: true, defaults: { ease: 'power3.out' } });
    function beat(step) { return lead + step * cfg.beat; }
    function enter(el, when, duration, rise) {
      var style = el.getAttribute('style');
      var opacity = getComputedStyle(el).opacity;
      var y = Number(G.getProperty(el, 'y'));
      G.set(el, { y: y + rise, opacity: 0 });
      tl.to(el, { y: y, opacity: opacity, duration: duration }, when);
      restore.push(function () {
        if (style === null) el.removeAttribute('style'); else el.setAttribute('style', style);
        G.core.getCache(el).uncache = 1;
      });
    }
    function stroke(svg, step) {
      var end = beat(step.step + 1), arrival = beat(step.arrival);
      var ns = 'http://www.w3.org/2000/svg';
      Array.prototype.forEach.call(svg.querySelectorAll('path'), function (path) {
        // The solid mask follows the path while the original keeps its dash pattern.
        var mask = document.createElementNS(ns, 'mask'), trace = document.createElementNS(ns, 'path');
        var box = path.getBBox(), pad = 8, length = path.getTotalLength(), len = length + pad;
        var direction = step.reverse ? -1 : 1;
        var hold = direction * (pad + Math.min(cfg.approach, length / 3));
        var id = 'seq-mask-' + (++maskId);
        mask.setAttribute('id', id);
        mask.setAttribute('maskUnits', 'userSpaceOnUse');
        mask.setAttribute('x', box.x - pad); mask.setAttribute('y', box.y - pad);
        mask.setAttribute('width', box.width + 2 * pad); mask.setAttribute('height', box.height + 2 * pad);
        trace.setAttribute('d', path.getAttribute('d'));
        trace.setAttribute('fill', 'none');
        trace.setAttribute('stroke', 'white');
        trace.setAttribute('stroke-width', pad);
        trace.setAttribute('stroke-linejoin', 'round');
        trace.setAttribute('stroke-dasharray', len + ' ' + len);
        trace.setAttribute('stroke-dashoffset', direction * len);
        mask.appendChild(trace); svg.appendChild(mask);
        path.setAttribute('mask', 'url(#' + id + ')');
        function drawTo(offset, duration, finishAt) {
          tl.to(trace, { strokeDashoffset: offset, duration: duration, ease: 'power2.inOut', autoRound: false }, finishAt - duration);
        }
        if (step.via.length) {
          step.via.forEach(function (stop) { drawTo(direction * (len - length * stop[1]), cfg.draw, beat(stop[0])); });
          drawTo(0, cfg.draw, arrival);
        } else {
          drawTo(arrival > end ? hold : 0, cfg.draw, end);
          if (arrival > end) drawTo(0, cfg.finishDraw, arrival);
        }
        restore.push(function () { path.removeAttribute('mask'); mask.remove(); });
      });
    }
    if (!sliding) {
      tl.from(slide.querySelectorAll('.titlecol .eyebrow, .titlecol .title, .titlecol .lede'),
        { y: 14, opacity: 0, duration: 0.55, stagger: 0.07, clearProps: 'transform,opacity' }, 0);
    }
    nodes.forEach(function (el) {
      var data = JSON.parse(el.dataset.seq), when = beat(data.step);
      if (data.motion === 'draw') stroke(el, data);
      else if (data.motion === 'dot') enter(el, when + cfg.beat - cfg.draw - cfg.dotLead, cfg.dot, 0);
      else if (data.motion === 'end') enter(el, when, cfg.dot, 0);
      else if (data.motion === 'label') enter(el, when + cfg.beat - cfg.labelLead, cfg.part, 0);
      else if (data.motion === 'row') enter(el, when + data.index * cfg.rowGap, cfg.row, cfg.rise);
      else enter(el, when, cfg.part, cfg.rise);
    });
    function complete() {
      tl.kill();
      restore.forEach(function (reset) { reset(); });
      sequence = null;
      slide.dataset.sequence = 'complete';
    }
    slide.dataset.sequence = 'playing';
    sequence = { finish: function () { tl.progress(1); } };
    tl.eventCallback('onComplete', complete);
    tl.play();
  }

  function drawSetup(svg) {
    if (svg._drawn) return svg._drawn;
    var NS = 'http://www.w3.org/2000/svg';
    var w = parseFloat(svg.style.width) || 0, h = parseFloat(svg.style.height) || 0;
    var d = svg.querySelector('path');
    var g = document.createElementNS(NS, 'g');
    while (svg.firstChild) g.appendChild(svg.firstChild);
    var id = 'm' + Math.random().toString(36).slice(2, 8);
    var defs = document.createElementNS(NS, 'defs');
    var mask = document.createElementNS(NS, 'mask');
    mask.setAttribute('id', id); mask.setAttribute('maskUnits', 'userSpaceOnUse');
    var pad = 6;
    mask.setAttribute('x', -pad); mask.setAttribute('y', -pad);
    mask.setAttribute('width', w + 2 * pad); mask.setAttribute('height', h + 2 * pad);
    var rect = document.createElementNS(NS, 'rect');
    rect.setAttribute('x', -pad); rect.setAttribute('y', -pad);
    rect.setAttribute('width', w + 2 * pad); rect.setAttribute('height', h + 2 * pad);
    rect.setAttribute('fill', '#fff');
    mask.appendChild(rect); defs.appendChild(mask);
    g.setAttribute('mask', 'url(#' + id + ')');
    svg.appendChild(defs); svg.appendChild(g);
    /* direction: from the path's first point toward its last */
    var horizontal = w >= h, rev = false;
    var m = d && d.getAttribute('d').match(/^M\s*([-\d.]+)\s+([-\d.]+)/);
    if (m) rev = horizontal ? parseFloat(m[1]) > w / 2 : parseFloat(m[2]) > h / 2;
    var ox = rev ? w + pad : -pad, oy = rev ? h + pad : -pad;
    svg._drawn = { rect: rect, horizontal: horizontal, origin: horizontal ? ox + ' 0' : '0 ' + oy };
    return svg._drawn;
  }
  /* sliding: the slide arrives by travelling, so its text and cards are not faded in on top of that; only the connectors draw and the nodes land, once it is nearly home */
  function buildIn(slide, sliding) {
    var tl = window.gsap.timeline({ defaults: { ease: 'power3.out' } });
    var tc = sliding ? [] : slide.querySelectorAll('.titlecol .eyebrow, .titlecol .title, .titlecol .lede');
    if (tc.length) tl.from(tc, { y: 14, opacity: 0, duration: 0.55, stagger: 0.07, clearProps: 'transform,opacity' }, 0);
    var slot = slide.querySelector('.slot');
    if (!slot) return tl;
    var kids = Array.prototype.slice.call(slot.children);
    var cards = [], conns = [], nodes = [], tags = [];
    kids.forEach(function (k) {
      if (k.classList.contains('connector')) conns.push(k);
      else if (k.getAttribute('data-c') === 'Illo / Node') nodes.push(k);
      else if (k.getAttribute('data-c') === 'Illo / Annotation' || k.getAttribute('data-c') === 'Illo / Tag') tags.push(k);
      else cards.push(k);
    });
    if (cards.length && !sliding) tl.from(cards, { y: 18, opacity: 0, duration: 0.6, stagger: Math.min(0.08, 0.7 / cards.length), clearProps: 'transform,opacity' }, 0.12);
    var t0 = sliding ? 0.5 : 0.3;
    conns.forEach(function (c, i) {
      var s = drawSetup(c);
      var vars = s.horizontal ? { scaleX: 0, svgOrigin: s.origin } : { scaleY: 0, svgOrigin: s.origin };
      tl.from(s.rect, Object.assign({ duration: 0.7, ease: 'power2.inOut' }, vars), t0 + i * 0.07);
    });
    if (nodes.length) tl.from(nodes, { scale: 0.3, opacity: 0, duration: 0.45, ease: 'back.out(2.2)', stagger: 0.03, clearProps: 'transform,opacity' }, t0 + 0.45);
    if (tags.length) tl.from(tags, { opacity: 0, y: 6, duration: 0.4, stagger: 0.04, clearProps: 'transform,opacity' }, t0 + 0.6);
    return tl;
  }

  /* ---------- navigation ---------- */
  function show(i, dir, instant) {
    if (i < 0 || i >= slides.length || i === cur) return;
    if (finish) finish();                       /* a key pressed mid-slide lands the running slide at once and starts the next */
    if (sequence) sequence.finish();
    var prev = cur >= 0 ? slides[cur] : null, next = slides[i];
    var immediate = instant || reduce || !window.gsap || !prev;
    if (tlIn) { tlIn.progress(1); tlIn = null; }
    next.hidden = false;
    next.style.zIndex = 2;
    cur = i;
    var parts = next.querySelectorAll('[data-seq]');
    var playSequence = parts.length && !seen.has(next) && !reduce && window.gsap;
    seen.add(next);
    if (parts.length) next.dataset.sequence = 'complete';
    document.body.setAttribute('data-slide', next.getAttribute('data-key'));
    try { window.history.replaceState(null, '', window.location.pathname + (window.location.search || '') + (next.getAttribute('data-key') === 'op' ? '' : '#' + next.getAttribute('data-key'))); } catch (e) { /* ignore */ }
    if (immediate) {
      if (prev) { prev.hidden = true; prev.style.zIndex = ''; }
      next.style.zIndex = '';
      if (playSequence) buildSequence(next, parts, false);
      return;
    }
    /* the slide (Khalid, 2026-11-17: "bring back the sliding effect"): the title column and the illustration travel one full artboard width,
       the old ones out and the new ones in, as on the previous deck (0.95 s, expo.inOut). The frame (wordmark, chapter bar, footer) does not move:
       the incoming slide's frame replaces the outgoing one at once, and a frame part that only one of the two slides has fades. */
    var G = window.gsap, W = deck.offsetWidth, art = next.querySelector('.art');
    var pm = prev.querySelectorAll('.titlecol,.slot'), nm = next.querySelectorAll('.titlecol,.slot'), touched = [];
    art.style.background = 'transparent';
    var tl = G.timeline({ defaults: { duration: DUR.slide, ease: 'expo.inOut' } });
    tl.fromTo(pm, { x: 0 }, { x: -W * dir }, 0).fromTo(nm, { x: W * dir }, { x: 0 }, 0);
    FRAME.forEach(function (sel) {
      var p = prev.querySelector(sel), n = next.querySelector(sel);
      if (p && n) { p.style.visibility = 'hidden'; touched.push(p); }
      else if (p) { tl.to(p, { opacity: 0, duration: 0.3, ease: 'power1.out' }, 0); touched.push(p); }
      else if (n) { tl.fromTo(n, { opacity: 0 }, { opacity: 1, duration: 0.45, ease: 'power1.out' }, 0.45); touched.push(n); }
    });
    finish = function () {
      finish = null; tl.kill();
      G.set([].concat(Array.prototype.slice.call(pm), Array.prototype.slice.call(nm), touched), { clearProps: 'transform,opacity,visibility' });
      art.style.background = '';
      prev.hidden = true; prev.style.zIndex = ''; next.style.zIndex = '';
    };
    tl.eventCallback('onComplete', function () { if (finish) finish(); });
    if (playSequence) buildSequence(next, parts, true);
    else if (!parts.length) tlIn = buildIn(next, true);
  }
  function go(d) {
    if (d > 0 && sequence) { sequence.finish(); if (finish) finish(); return; }
    show(Math.max(0, Math.min(slides.length - 1, cur + d)), d);
  }
  function goKey(key) { var i = slides.findIndex(function (s) { return s.getAttribute('data-key') === key; }); if (i >= 0) show(i, i > cur ? 1 : -1, true); }

  document.addEventListener('keydown', function (e) {
    if (e.altKey || e.ctrlKey || e.metaKey || document.body.classList.contains('preshow-on')) return;
    var k = e.key;
    if (k === 'ArrowRight' || k === ' ' || k === 'PageDown' || k === 'Enter') { e.preventDefault(); go(1); }
    else if (k === 'ArrowLeft' || k === 'PageUp') { e.preventDefault(); go(-1); }
    else if (k === 'Home') { e.preventDefault(); show(0, -1); }
    else if (k === 'End') { e.preventDefault(); show(slides.length - 1, 1); }
  });
  deck.addEventListener('click', function (e) {
    var t = e.target;
    var p = t.closest && t.closest('.pager');
    if (p) { go(p.classList.contains('next') ? 1 : -1); return; }
    var s = t.closest && t.closest('.seg');
    if (s) {
      var ch = parseInt(s.getAttribute('data-ch'), 10);
      var i = slides.findIndex(function (x) { return parseInt(x.getAttribute('data-ch'), 10) >= ch; });
      if (i >= 0) show(i, i > cur ? 1 : -1);
      return;
    }
    var lb = t.closest && t.closest('[data-lang]');
    if (lb) { setLang(lb.getAttribute('data-lang'), true); return; }
    var sn = t.closest && t.closest('#snd');
    if (sn && window.BNG_AUDIO) { window.BNG_AUDIO.toggle(); }
  });
  var tx = null;
  deck.addEventListener('touchstart', function (e) { tx = e.touches[0].clientX; }, { passive: true });
  deck.addEventListener('touchend', function (e) {
    if (tx === null) return;
    var dx = e.changedTouches[0].clientX - tx; tx = null;
    if (Math.abs(dx) > 50) go(dx < 0 ? 1 : -1);
  });
  Array.prototype.forEach.call(deck.querySelectorAll('.seg'), function (s) { s.setAttribute('role', 'button'); s.setAttribute('tabindex', '0'); s.setAttribute('aria-label', 'Chapter ' + s.getAttribute('data-ch')); });
  deck.addEventListener('keydown', function (e) { if ((e.key === 'Enter' || e.key === ' ') && e.target.classList && e.target.classList.contains('seg')) { e.stopPropagation(); e.target.click(); } }, true);

  /* ---------- start ---------- */
  setLang(initialLang(), false);
  var api = { show: show, go: go, goKey: goKey, setLang: setLang, count: slides.length, fit: fit, get index() { return cur; }, get lang() { return lang; } };
  window.BNG_DECK = api;
  function start(o) {
    document.body.classList.remove('preshow-on');
    document.body.classList.add('deck-on');
    var h = (window.location.hash || '').replace('#', '');
    var i = slides.findIndex(function (s) { return s.getAttribute('data-key') === h; });
    show(i >= 0 ? i : 0, 1, true);
    /* handed over from the pre-show: the opener is already on screen as the pre-show left it, so no entrance */
    if (window.gsap && !reduce && !(o && o.quiet) && !slides[cur].dataset.sequence) { tlIn = buildIn(slides[cur]); }
  }
  window.BNG_DECK.start = start;
  if (!document.getElementById('preshow') || !window.BNG_PRESHOW) {
    /* until the pre-show script claims the page (or when it is absent) the deck opens at once */
    window.addEventListener('load', function () { if (!window.BNG_PRESHOW) start(); });
  }
})();
