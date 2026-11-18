/* The reveal between the last problem (slide 09) and the system (slide 10). Khalid, 2026-11-17: "should we do something like animate the O of
   the OS logo there with the dot?" ... "looks great, let's integrate it".
   The seven tools of slide 03 drift alone, the O closes in, each tool loses its icon and is pulled into the O, the seven become its one dot,
   the dot turns green, the rest of the wordmark arrives, one line under it. On the next key the wordmark travels to its corner while slide 10 slides in.
   Markup comes from build_site.reveal_html (the wordmark's own paths, slide 03's discs and names). Every frame is a pure function of time. */
(function () {
  'use strict';
  var slide = document.querySelector('.slide.kind-reveal'), svg = slide && slide.querySelector('.rv');
  if (!svg) return;
  var deck = document.getElementById('deck');
  var slides = Array.prototype.slice.call(deck.querySelectorAll('.slide')), index = slides.indexOf(slide);
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var q = function (s) { return svg.querySelector(s); };
  var c01 = function (x) { return Math.max(0, Math.min(1, x)); }, mix = function (a, b, u) { return a + (b - a) * u; };
  var io = function (x) { return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  var out = function (x) { return 1 - Math.pow(1 - x, 3); }, inn = function (x) { return x * x * x; }, lin = function (x) { return x; };
  var expo = function (x) { return x <= 0 ? 0 : x >= 1 ? 1 : x < .5 ? Math.pow(2, 20 * x - 10) / 2 : (2 - Math.pow(2, -20 * x + 10)) / 2; };
  var seg = function (t, a, b, e) { return (e || io)(c01((t - a) / (b - a))); };
  /* colours are read from the tokens once, then mixed */
  var probe = document.createElement('i'); probe.style.display = 'none'; deck.appendChild(probe);
  function token(name) { probe.style.color = 'var(' + name + ')'; return getComputedStyle(probe).color.match(/[\d.]+/g).slice(0, 3).map(Number); }
  var RAISED = token('--color-background-neutral-raised'), GREY = token('--color-text-neutral-placeholder'), GREEN = token('--color-background-signature-bold');
  probe.remove();
  var colour = function (a, b, u) { return 'rgb(' + a.map(function (v, i) { return Math.round(mix(v, b[i], u)); }).join(',') + ')'; };

  var vb = svg.getAttribute('data-vb').split(' ').map(Number);
  var core = q('.rv-core'), OX = +core.getAttribute('cx'), OY = +core.getAttribute('cy'), CORE_R = +core.getAttribute('data-r');
  var wm = q('.rv-wm'), ot = q('.rv-ot'), ob = q('.rv-ob'), line = q('.rv-line');
  var letters = Array.prototype.slice.call(svg.querySelectorAll('.rv-l'));
  var tools = Array.prototype.slice.call(svg.querySelectorAll('.rv-tool')).map(function (g, i) {
    return { g: g, disc: g.querySelector('.rv-disc'), ico: g.querySelector('.rv-ico'), label: g.querySelector('.rv-label'), i: i };
  });
  /* where each tool drifts, as an offset from the centre of the artboard */
  var HOME = [[-390, -180], [370, -215], [-470, 90], [460, 40], [-250, 270], [260, 260], [0, -270]];
  var DISC_R = 35, DOT_R = 7, CY = 430, T1 = 6.2, T2 = 0.9, DELAY = 0.45;
  var CORNER_S = 96 / vb[2];                                    /* the frame's wordmark: .wm, 96 px wide at 36, 21 */
  var CORNER = [36 + (OX - vb[0]) * CORNER_S, 21 + (OY - vb[1]) * CORNER_S, CORNER_S];

  /* t: seconds into the reveal (0 to T1). t2: seconds into the hand-over to slide 10 (0 to T2). */
  function render(t, t2) {
    var CX = deck.offsetWidth / 2, arrived = 0;
    tools.forEach(function (d) {
      var ph = d.i * 1.7, hx = CX + HOME[d.i][0], hy = CY + HOME[d.i][1];
      var wx = hx + Math.sin(t * .9 + ph) * 16 + Math.sin(t * .37 + ph * 2) * 10, wy = hy + Math.cos(t * .7 + ph) * 14 + Math.sin(t * .45 + ph) * 8;
      var u = seg(t, 2.2 + d.i * .11, 3.25 + d.i * .11, inn), dx = CX - wx, dy = CY - wy, bend = Math.sin(Math.PI * u) * .28;
      d.g.setAttribute('transform', 'translate(' + (wx + dx * u - dy * bend).toFixed(2) + ' ' + (wy + dy * u + dx * bend).toFixed(2) + ')');
      d.g.setAttribute('opacity', seg(t, .15 + d.i * .09, .75 + d.i * .09, out) * (1 - seg(u, .92, 1)));
      /* on the way in the disc loses its icon and shrinks to a plain grey dot: seven different tools become the same thing */
      var shed = seg(u, .05, .55);
      d.disc.setAttribute('r', mix(DISC_R, DOT_R, shed)); d.disc.style.fill = colour(RAISED, GREY, shed); d.disc.setAttribute('stroke-opacity', 1 - shed);
      d.ico.setAttribute('opacity', 1 - seg(u, .02, .3));
      d.label.setAttribute('opacity', 1 - seg(t, 1.9, 2.4));
      arrived += seg(u, .85, 1);
    });
    /* the O: its halves close in from above and below */
    var close = seg(t, 1.5, 2.5, out), oOp = seg(t, 1.5, 2.0);
    ot.setAttribute('transform', 'translate(0 ' + (-34 * (1 - close)) + ')'); ob.setAttribute('transform', 'translate(0 ' + (34 * (1 - close)) + ')');
    ot.setAttribute('opacity', oOp); ob.setAttribute('opacity', oOp);
    /* the core grows as the tools land, then turns green with one small pulse (no glow) */
    var pulse = Math.sin(Math.PI * seg(t, 3.85, 4.45, lin)) * .2;
    core.setAttribute('r', CORE_R * Math.sqrt(arrived / 7) * (1 + pulse)); core.style.fill = colour(GREY, GREEN, seg(t, 3.85, 4.25));
    /* the wordmark: the O alone and large, then the whole lockup, then the frame's corner */
    var BIG = [CX, CY, 2.6], LOCK = [CX + (OX - (vb[0] + vb[2] / 2)) * 1.3, 420, 1.3];
    var a = seg(t, 4.3, 5.3, expo), b = seg(t2, 0, T2, expo);
    var P = [0, 1, 2].map(function (i) { return mix(mix(BIG[i], LOCK[i], a), CORNER[i], b); });
    wm.setAttribute('transform', 'translate(' + P[0] + ' ' + P[1] + ') scale(' + P[2] + ') translate(' + (-OX) + ' ' + (-OY) + ')');
    letters.forEach(function (p) {
      var k = p.getAttribute('data-k'), n = { G: 0, N: 1, B: 2, S: 0 }[k], u = seg(t, 4.45 + n * .1, 5.25 + n * .1, out), from = k === 'S' ? -46 : 46 + n * 14;
      p.setAttribute('transform', 'translate(' + from * (1 - u) + ' 0)'); p.setAttribute('opacity', seg(t, 4.45 + n * .1, 4.95 + n * .1));
    });
    var l = seg(t, 5.3, 6.0, out);
    line.setAttribute('x', CX); line.setAttribute('y', 560);
    line.setAttribute('opacity', l * (1 - seg(t2, 0, .3))); line.setAttribute('transform', 'translate(0 ' + 12 * (1 - l) + ')');
  }

  var state = { t: 0, t2: 0, mode: 'idle' }, raf = 0, t0 = 0;
  window.BNG_REVEAL = { state: state, render: render, T1: T1, T2: T2 };
  function stop() { cancelAnimationFrame(raf); raf = 0; }
  function still(t, t2) { stop(); state.t = t; state.t2 = t2; render(t, t2); }
  function play() {
    stop(); svg.style.opacity = ''; state.mode = 'play'; t0 = performance.now() + DELAY * 1000; render(0, 0);
    (function tick(now) {
      state.t = Math.max(0, Math.min(T1, (now - t0) / 1000)); render(state.t, 0);
      if (state.t < T1) raf = requestAnimationFrame(tick); else { raf = 0; state.mode = 'rest'; }
    })(performance.now());
  }
  /* leaving forward: whatever the reveal had reached, the finished wordmark travels to its corner while slide 10 arrives */
  function exit() {
    stop(); state.mode = 'exit'; t0 = performance.now();
    /* slide 10's own wordmark stays out until the travelling one has landed on it: one wordmark on screen, never two */
    var own = slides[index + 1] && slides[index + 1].querySelector('.wm');
    if (own) own.style.visibility = 'hidden';
    (function tick(now) {
      state.t = T1; state.t2 = Math.min(T2, (now - t0) / 1000); render(T1, state.t2);
      if (state.t2 < T2 && !slide.hidden) raf = requestAnimationFrame(tick);
      else { raf = 0; state.mode = 'idle'; if (own) own.style.visibility = ''; }
    })(performance.now());
  }
  var prior = -1;
  function sync() {
    var cur = window.BNG_DECK ? window.BNG_DECK.index : -1;
    if (cur === prior) return;
    var from = prior; prior = cur;
    if (cur === index) {
      svg.style.opacity = '';
      if (reduce || from > index) { state.mode = 'rest'; still(T1, 0); } else play();   /* coming back from slide 10: the finished lockup, no replay */
    } else if (from === index) {
      if (cur === index + 1 && !reduce) exit();
      else { stop(); state.mode = 'idle'; svg.style.opacity = 0; }                        /* going back: it fades while slide 09 returns */
    }
  }
  new MutationObserver(sync).observe(document.body, { attributes: true, attributeFilter: ['data-slide'] });
  window.addEventListener('resize', function () { if (!raf && !slide.hidden) render(state.t, state.t2); });
  render(0, 0); sync();
})();
