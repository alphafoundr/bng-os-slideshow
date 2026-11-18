/* Concept C2 · Physical stencil field (explores C further, keeps A's idea of one fixed dot with the signs built around it).
   The parts the signs and the wordmark are cut from are rigid bodies (Matter.js): they drift, spin, collide softly and are scattered
   by the pointer. One green dot holds the centre and never moves; on a seeded slow cycle the parts of one sign are pulled around it by a
   damped spring (a force, so a part knocked away on its way still arrives), held for a beat and released. Space starts the show: every
   body is handed from the simulation to a GSAP timeline that starts from its current position, rotation and velocity, flies it to its
   place in the wordmark, closes the ring on the dot and settles the O on opener A's O. Geometry comes verbatim from geometry.js
   (= brand-kit SVGs built by logo_build.py); parts are only moved, rotated, scaled and faded. Collision shapes are derived from the
   same path data (sampled, simplified, triangulated at load); nothing is redrawn. */
(function () {
  'use strict';
  const G = window.PS_G, M = window.Matter, gsap = window.gsap;
  const { Engine, Bodies, Body, Composite, Vertices } = M;
  const Q = new URLSearchParams(location.search);
  const DARK = Q.get('stage') === 'dark';
  const RM = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
  const SEED = (parseInt(Q.get('seed') || '1', 10) || 1) >>> 0;
  const COL = { canvas: '#FAFAF8', ink: '#0B0B0B', white: '#FFFFFF', green: '#10B981' };
  const NS = 'http://www.w3.org/2000/svg';
  const TAU = Math.PI * 2;
  const clamp01 = (x) => (x < 0 ? 0 : x > 1 ? 1 : x);
  const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
  const prog = (t, a, b) => clamp01((t - a) / (b - a));
  const lerp = (a, b, w) => a + (b - a) * w;
  const wrapPi = (a) => { a = (a + Math.PI) % TAU; if (a < 0) a += TAU; return a - Math.PI; };
  const f3 = (v) => Math.round(v * 1000) / 1000;

  /* ---------- tunable constants (README lists them) ---------- */
  const K = {
    S: G.O_SIGN_SCALE,    /* px per 96-grid unit for every sign: the size the O has at rest in opener A, so nothing changes size at the start of the show (Khalid, 2026-11-17; was 4.0) */
    SL: G.OPENER.k,       /* px per wordmark unit for the letters in the field: their size at rest in opener A (was 2.0) */
    CLEAR: 30,            /* the stencil clear space around the dot: dot r 16.629 + cut 13.36 = 30 grid units (the OS ring's inner radius) */
    SUB: 120,             /* physics sub-steps per second, fixed */
    cruise: 26,           /* drift: cruising speed, px/s */
    cruiseSpin: 0.13,     /* drift: cruising spin, rad/s */
    steer: 0.55,          /* drift: pull back to the cruising velocity, 1/s (how fast a scattered part recovers) */
    spinSteer: 0.8,       /* same for spin */
    vmax: 1000,           /* hard speed cap, px/s */
    wmax: 12,             /* hard spin cap, rad/s */
    restitution: 0.6,     /* collisions are soft */
    density: 0.0012,
    edgeBand: 60,         /* a part nearer than this to the stage edge is steered inward */
    edgeSpeed: 80,
    dotBand: 36,          /* soft repulsion band outside the clear space; the clear space itself is a hard collider */
    dotSpeed: 70,
    /* signs form fast and with a small overshoot ("quickly ... in a snappy way", Khalid, 2026-11-17): omega_n = 10.2 1/s, zeta = 0.64 (was 4.0 and 0.81) */
    kp: 8.0,              /* spring: stiffness term, 1/s (desired speed = kp x distance) */
    kv: 13.0,             /* spring: velocity servo, 1/s  (omega_n = sqrt(kp x kv), zeta = kv / (2 omega_n)) */
    vSpring: 1100,        /* spring: cap of the desired speed, px/s */
    kth: 8.0, kw: 13.0, wSpring: 10,   /* the same for rotation */
    ptrR: 170,            /* pointer: reach, px */
    ptrGain: 1.6,         /* pointer: push per px travelled (px/s of velocity per px of pointer path), at the centre of the reach */
    ptrSpeedBoost: 900,   /* pointer: speed (px/s) at which the push doubles */
    ptrMaxDv: 420,        /* pointer: most velocity one part can gain from one sweep step, px/s */
    burstR: 380,          /* click or tap: reach, px */
    burstDv: 800,         /* click or tap: peak velocity change, px/s */
    gatherLead: 0.15,     /* seconds of spring ramp-up at the start of a gather */
    holdGrace: 1.5,       /* a broken sign is kept up to this long past its release time to re-form, s */
    gatherBudget: 1.3,    /* a sign must be formed this long after its gather starts */
    holdMin: 1.0, holdJitter: 0.4,       /* hold after the budget, s */
    gapMin: 0.7, gapJitter: 0.5,         /* field-only time between a release and the next gather, s */
    releaseS: 0.35, releaseKick: 340,    /* release ramp, s; outward kick, px/s */
    firstGather: 0.8,     /* first gather starts here, s */
    stage: 60,            /* a gathering part first goes to a staging pose this far out along the line from the dot, then docks along that line, px */
    zoneSpeed: 520,       /* the parts of other signs are pushed out of the zone of the forming sign at this speed, px/s ... */
    zoneGain: 9.0,        /* ... with this pull on their velocity, 1/s */
    dimTo: 0.4,          /* the parts not in the held sign dim to this opacity */
    Tt: 3.4, KEY: 2.5,    /* start: total length and the beat of the soft hit (the dot's pulse), s */
    settle0: 0.45, settle1: 2.3   /* start: the ring and the dot move and shrink onto the O between these times, s */
  };
  const CAT = { free: 1, dot: 2, member: 4, wall: 8 };
  const DT = 1 / K.SUB;
  const R_EX = K.CLEAR * K.S;                 /* clear-space radius around the dot, px (the dot itself is 16.629 x S) */
  const R_COL = R_EX - 0.5;                   /* collider: the clear space itself, a hair smaller so the ink of a formed sign (tangent to it) never touches it */
  const C0 = [720, 450];

  function mulberry(a) { return function () { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

  /* ---------- easing: same tokens as the other prototypes ---------- */
  function bez(x1, y1, x2, y2) {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx, cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const X = (t) => ((ax * t + bx) * t + cx) * t, Y = (t) => ((ay * t + by) * t + cy) * t;
    return function (x) { if (x <= 0) return 0; if (x >= 1) return 1; let lo = 0, hi = 1, t = x; for (let i = 0; i < 22; i++) { const v = X(t); if (v < x) lo = t; else hi = t; t = (lo + hi) / 2; } return Y(t); };
  }
  const E = { out: bez(0.22, 1, 0.36, 1), io: bez(0.65, 0, 0.35, 1), sync: bez(0.45, 0, 0.2, 1), land: bez(0.5, 0, 0.15, 1) };

  const el = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };

  /* ---------- collision geometry, derived from the path data ---------- */
  const measurePath = (() => {
    const s = document.createElementNS(NS, 'svg'); s.setAttribute('width', 0); s.setAttribute('height', 0); s.style.cssText = 'position:absolute;visibility:hidden';
    const p = el('path', {}, s); document.body.appendChild(s); return p;
  })();
  function outlines(d) {
    return d.split(/(?=M)/).map((s) => s.trim()).filter(Boolean).map((sub) => {
      measurePath.setAttribute('d', sub);
      const L = measurePath.getTotalLength(), n = Math.max(12, Math.ceil(L / 0.6)), pts = [];
      for (let i = 0; i < n; i++) { const p = measurePath.getPointAtLength(L * i / n); pts.push([p.x, p.y]); }
      return pts;
    });
  }
  function rdp(pts, eps) {
    const n = pts.length; if (n < 3) return pts.slice();
    const keep = new Uint8Array(n); keep[0] = keep[n - 1] = 1; const st = [[0, n - 1]];
    while (st.length) {
      const [a, b] = st.pop(); const ax = pts[a][0], ay = pts[a][1], dx = pts[b][0] - ax, dy = pts[b][1] - ay, L = Math.hypot(dx, dy) || 1e-9;
      let dm = 0, im = -1;
      for (let i = a + 1; i < b; i++) { const d = Math.abs((pts[i][0] - ax) * dy - (pts[i][1] - ay) * dx) / L; if (d > dm) { dm = d; im = i; } }
      if (dm > eps && im > 0) { keep[im] = 1; st.push([a, im], [im, b]); }
    }
    return pts.filter((_, i) => keep[i]);
  }
  function simplifyClosed(pts, eps) {
    let k = 0, best = 0; pts.forEach((p, i) => { const d = Math.hypot(p[0] - pts[0][0], p[1] - pts[0][1]); if (d > best) { best = d; k = i; } });
    const A = rdp(pts.slice(0, k + 1), eps), B = rdp(pts.slice(k).concat([pts[0]]), eps);
    let out = A.slice(0, -1).concat(B.slice(0, -1)), changed = true;
    while (changed && out.length > 3) {                      /* drop collinear leftovers */
      changed = false;
      for (let i = 0; i < out.length; i++) {
        const a = out[(i + out.length - 1) % out.length], b = out[i], c = out[(i + 1) % out.length];
        const cr = Math.abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) / (Math.hypot(c[0] - a[0], c[1] - a[1]) || 1e-9);
        if (cr < eps * 0.25) { out.splice(i, 1); changed = true; break; }
      }
    }
    return out;
  }
  const cross3 = (a, b, c) => (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
  function area2(p) { let s = 0; for (let i = 0; i < p.length; i++) { const j = (i + 1) % p.length; s += p[i][0] * p[j][1] - p[j][0] * p[i][1]; } return s; }
  function isConvex(p) { let sg = 0; for (let i = 0; i < p.length; i++) { const c = cross3(p[i], p[(i + 1) % p.length], p[(i + 2) % p.length]); if (Math.abs(c) < 1e-9) continue; const s = c > 0 ? 1 : -1; if (sg && s !== sg) return false; sg = s; } return true; }
  function triangulate(poly) {
    const pts = poly.slice(); if (area2(pts) < 0) pts.reverse();
    const idx = pts.map((_, i) => i), tris = []; let guard = 0;
    while (idx.length > 3 && guard++ < 4000) {
      let ear = -1, bestC = -1, bestI = 0;
      for (let i = 0; i < idx.length; i++) {
        const a = pts[idx[(i + idx.length - 1) % idx.length]], b = pts[idx[i]], c = pts[idx[(i + 1) % idx.length]], cr = cross3(a, b, c);
        if (cr > bestC) { bestC = cr; bestI = i; }
        if (cr <= 1e-9) continue;
        let ok = true;
        for (const j of idx) { const p = pts[j]; if (p === a || p === b || p === c) continue; if (cross3(a, b, p) >= -1e-9 && cross3(b, c, p) >= -1e-9 && cross3(c, a, p) >= -1e-9) { ok = false; break; } }
        if (ok) { ear = i; break; }
      }
      if (ear < 0) ear = bestI;
      const n = idx.length; tris.push([pts[idx[(ear + n - 1) % n]], pts[idx[ear]], pts[idx[(ear + 1) % n]]]); idx.splice(ear, 1);
    }
    if (idx.length === 3) tris.push([pts[idx[0]], pts[idx[1]], pts[idx[2]]]);
    return tris.filter((t) => Math.abs(cross3(t[0], t[1], t[2])) > 1e-4);
  }
  function hullPolys(d, sc) {
    const eps = 0.5 / sc, out = [], outline = [];
    outlines(d).forEach((raw) => {
      const poly = simplifyClosed(raw, eps); outline.push(poly);
      if (isConvex(poly)) out.push(poly); else triangulate(poly).forEach((t) => out.push(t));
    });
    return { polys: out, outline };
  }
  function polyCentroid(v) {
    let a = 0, cx = 0, cy = 0;
    for (let i = 0; i < v.length; i++) { const j = (i + 1) % v.length, f = v[i].x * v[j].y - v[j].x * v[i].y; a += f; cx += (v[i].x + v[j].x) * f; cy += (v[i].y + v[j].y) * f; }
    if (Math.abs(a) < 1e-9) return { x: v.reduce((s, p) => s + p.x, 0) / v.length, y: v.reduce((s, p) => s + p.y, 0) / v.length };
    return { x: cx / (3 * a), y: cy / (3 * a) };
  }

  /* ---------- the parts ---------- */
  const SG = G.SIGN;
  const DOTU = { os: SG.os.dot, cortex: SG.cortex.dot, studio: SG.studio.dot };
  /* d = what is drawn (verbatim sign or wordmark path, or a bar of one with 0.5 unit of overlap so two bars never show an anti-aliasing seam);
     hull = the disjoint bar the collider is built from (when it differs from d) */
  const PARTS = [
    { id: 'osTop', d: SG.os.top, sc: K.S, sign: 'os' },
    { id: 'osBot', d: SG.os.bot, sc: K.S, sign: 'os' },
    { id: 'cxV', d: 'M12 0H30V49.39H12Z', sc: K.S, sign: 'cortex' },
    { id: 'cxH', d: 'M29.5 0H72V18H29.5Z', hull: 'M30 0H72V18H30Z', sc: K.S, sign: 'cortex' },
    { id: 'stT', d: 'M0 0H49.39V18H0Z', sc: K.S, sign: 'studio' },
    { id: 'stL', d: 'M0 17.5H18V78.5H0Z', hull: 'M0 18H18V78H0Z', sc: K.S, sign: 'studio' },
    { id: 'stB', d: 'M0 78H96V96H0Z', sc: K.S, sign: 'studio' },
    { id: 'stR', d: 'M78 46.61H96V78.5H78Z', hull: 'M78 46.61H96V78H78Z', sc: K.S, sign: 'studio' },
    ...['B1', 'B2', 'B3', 'N1', 'N2', 'G', 'S'].map((id) => ({ id, d: G.WM[id].d, sc: K.SL, sign: null }))
  ];
  const SIGNS = ['os', 'cortex', 'studio'];
  const SIGN_GROUP = { os: -1, cortex: -2, studio: -3 };
  const N = PARTS.length;

  /* ---------- physics world ---------- */
  const engine = Engine.create({ gravity: { x: 0, y: 0, scale: 0 }, positionIterations: 8, velocityIterations: 5, enableSleeping: false });
  const world = engine.world;
  const bodies = [];
  PARTS.forEach((P) => {
    const h = hullPolys(P.hull || P.d, P.sc);
    P.outline = h.outline;
    const ref = h.polys[0][0], opts = { restitution: K.restitution, friction: 0.02, frictionStatic: 0, frictionAir: 0, density: K.density, slop: 0.4 };
    const parts = h.polys.map((poly) => {
      const v = poly.map((p) => ({ x: (p[0] - ref[0]) * P.sc, y: (p[1] - ref[1]) * P.sc }));
      Vertices.clockwiseSort(v);
      return Body.create(Object.assign({ position: polyCentroid(v), vertices: v }, opts));
    });
    const body = Body.create(Object.assign({ parts }, opts));
    P.comU = { x: ref[0] + body.position.x / P.sc, y: ref[1] + body.position.y / P.sc };
    P.rb = 0; parts.forEach((pt) => pt.vertices.forEach((v) => { P.rb = Math.max(P.rb, Math.hypot(v.x - body.position.x, v.y - body.position.y)); }));
    P.rg2 = body.inertia / body.mass;
    P.outlineU = [];                                           /* outline densified to <= 30 px, in units relative to the COM, for the pointer */
    P.outline.forEach((poly) => { for (let i = 0; i < poly.length; i++) { const a = poly[i], b = poly[(i + 1) % poly.length], n = Math.max(1, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) * P.sc / 30)); for (let k = 0; k < n; k++) P.outlineU.push([(lerp(a[0], b[0], k / n) - P.comU.x) * P.sc, (lerp(a[1], b[1], k / n) - P.comU.y) * P.sc]); } });
    P.body = body; P.i = bodies.length; bodies.push(body); setFilter(body, 0);
  });
  /* collision filters: free parts (1) collide with everything; while a sign forms its members (4) collide only with the dot (2) and the stage edge (8),
     and the free parts stop colliding with the members, so a part that sits where the sign must go can never block it; the zone push clears it */
  function setFilter(body, group, cat, mask) {
    cat = cat || CAT.free; mask = mask === undefined ? 0xFFFF : mask;
    const apply = (f) => { f.group = group; f.category = cat; f.mask = mask; };
    apply(body.collisionFilter); body.parts.forEach((p) => apply(p.collisionFilter));
  }
  const dotBody = Bodies.circle(C0[0], C0[1], R_COL, { isStatic: true, restitution: 0.6, friction: 0, collisionFilter: { category: 2 } }, 56);
  Composite.add(world, dotBody);
  Composite.add(world, bodies);
  let walls = [], B = { x0: 0, y0: 0, x1: 1440, y1: 900 };
  function stageBounds() {
    const vw = window.innerWidth || 1440, vh = window.innerHeight || 900, k = Math.min(vw / 1440, vh / 900), hw = vw / (2 * k), hh = vh / (2 * k);
    return { x0: 720 - hw, x1: 720 + hw, y0: 450 - hh, y1: 450 + hh };
  }
  function buildWalls() {
    if (walls.length) Composite.remove(world, walls);
    const T = 500, w = B.x1 - B.x0, h = B.y1 - B.y0, o = { isStatic: true, restitution: 0.6, friction: 0, collisionFilter: { category: 8 } };
    walls = [Bodies.rectangle((B.x0 + B.x1) / 2, B.y0 - T / 2, w + 2 * T, T, o), Bodies.rectangle((B.x0 + B.x1) / 2, B.y1 + T / 2, w + 2 * T, T, o),
      Bodies.rectangle(B.x0 - T / 2, (B.y0 + B.y1) / 2, T, h + 2 * T, o), Bodies.rectangle(B.x1 + T / 2, (B.y0 + B.y1) / 2, T, h + 2 * T, o)];
    Composite.add(world, walls);
  }
  B = stageBounds(); buildWalls();

  /* ---------- per-part runtime state ---------- */
  const rng = mulberry(SEED * 2654435761 >>> 0);
  const S_ = PARTS.map(() => ({
    px: 0, py: 0, pa: 0, x: 0, y: 0, a: 0, op: 1,            /* previous and current state, for interpolated rendering */
    phi: rng() * TAU, w1: 0.05 + rng() * 0.05, p1: rng() * TAU, w2: 0.11 + rng() * 0.06, p2: rng() * TAU, p3: rng() * TAU,
    spin: (rng() < 0.5 ? -1 : 1) * (0.55 + 0.45 * rng()), hand: rng() < 0.5 ? -1 : 1,
    tgt: null, dock: 0, slowT: 0
  }));
  function place() {
    const order = PARTS.map((p, i) => i).sort((a, b) => PARTS[b].rb - PARTS[a].rb), placed = [];
    order.forEach((i) => {
      const P = PARTS[i], rb = P.rb; let ok = false, x = 0, y = 0;
      for (let tries = 0; tries < 900 && !ok; tries++) {
        const f = tries < 300 ? 0.7 : tries < 600 ? 0.55 : 0.4;
        x = lerp(B.x0 + rb * 0.6 + 20, B.x1 - rb * 0.6 - 20, rng()); y = lerp(B.y0 + rb * 0.6 + 20, B.y1 - rb * 0.6 - 20, rng());
        ok = Math.hypot(x - C0[0], y - C0[1]) > R_EX + rb * f + 30 && placed.every((q) => Math.hypot(x - q.x, y - q.y) > (rb + q.rb) * f + 10);
      }
      placed.push({ x, y, rb });
      Body.setPosition(P.body, { x, y }); Body.setAngle(P.body, (rng() - 0.5) * TAU);
      const bd = P.body.bounds, m = 12;                       /* the whole part, not just its centre, starts inside the stage */
      const fx = Math.max(0, B.x0 + m - bd.min.x) - Math.max(0, bd.max.x - (B.x1 - m)), fy = Math.max(0, B.y0 + m - bd.min.y) - Math.max(0, bd.max.y - (B.y1 - m));
      if (fx || fy) Body.setPosition(P.body, { x: x + fx, y: y + fy });
      const sp = K.cruise * (0.7 + 0.6 * rng()), dir = rng() * TAU;
      Body.setVelocity(P.body, { x: Math.cos(dir) * sp / 60, y: Math.sin(dir) * sp / 60 });
      Body.setAngularVelocity(P.body, S_[i].spin * K.cruiseSpin / 60);
    });
  }
  if (!RM) place();

  /* ---------- the sign schedule (deterministic from the seed) ---------- */
  const srng = mulberry((SEED * 40503 + 977) >>> 0);
  const sched = [];
  function ensureSched(t) {
    while (!sched.length || sched[sched.length - 1].tEnd < t + 2) {
      const last = sched[sched.length - 1], k = sched.length;
      const tG = last ? last.tEnd : K.firstGather, tF = tG + K.gatherBudget, tR = tF + K.holdMin + srng() * K.holdJitter, tEnd = tR + K.releaseS + K.gapMin + srng() * K.gapJitter;
      sched.push({ k, sign: SIGNS[k % 3], tG, tF, tR, tR0: tR, pushed: 0, tEnd, started: false, kicked: false, formedAt: null, formedFor: 0, holdOk: 0, holdN: 0, broke: 0, wasFormed: false });
    }
  }
  let warming = false;
  const sim = { t: 0, steps: 0, lam: { os: 0, cortex: 0, studio: 0 }, active: null, log: [], escapes: 0, escLog: [], nudges: 0, simMs: 0, worstSimMs: 0 };

  /* targets of one sign's members in the world, relative to the dot (fixed at the stage centre) */
  function memberTarget(P, flip) {
    const du = DOTU[P.sign], s = K.S;
    let dx = (P.comU.x - du[0]) * s, dy = (P.comU.y - du[1]) * s, a = 0;
    if (flip) { dx = -dx; dy = -dy; a = Math.PI; }
    return { x: C0[0] + dx, y: C0[1] + dy, a };
  }
  function startGather(slot) {
    slot.started = true;
    PARTS.forEach((P, i) => { S_[i].tgt = null; S_[i].dock = 0; S_[i].slowT = 0; });
    PARTS.forEach((P, i) => { if (P.sign === slot.sign) S_[i].tgt = memberTarget(P, false); });
    if (slot.sign === 'os') {                       /* the two halves are the same shape turned 180 degrees: take the cheaper pairing */
      const iT = 0, iB = 1, a = bodies[iT].position, b = bodies[iB].position, tT = memberTarget(PARTS[iT], false), tB = memberTarget(PARTS[iB], false);
      const cost = (p, t, ang) => Math.hypot(p.x - t.x, p.y - t.y) + 120 * Math.abs(wrapPi(t.a - ang));
      const straight = cost(a, tT, bodies[iT].angle) + cost(b, tB, bodies[iB].angle);
      const swapped = cost(a, memberTarget(PARTS[iT], true), bodies[iT].angle) + cost(b, memberTarget(PARTS[iB], true), bodies[iB].angle);
      if (swapped < straight) { S_[iT].tgt = memberTarget(PARTS[iT], true); S_[iB].tgt = memberTarget(PARTS[iB], true); }
    }
    /* keep the target angle on the branch nearest to the body's own angle so it turns the short way */
    PARTS.forEach((P, i) => { const t = S_[i].tgt; if (t) { const ang = bodies[i].angle; t.a = ang + wrapPi(t.a - ang); } });
    /* the zone of the sign (a bounding circle of its target ink), used to keep the other parts out while it forms */
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9; const pts = [];
    PARTS.forEach((P, i) => { const t = S_[i].tgt; if (!t) return; const co = Math.cos(t.a), si = Math.sin(t.a); P.outlineU.forEach((q) => { const x = t.x + q[0] * co - q[1] * si, y = t.y + q[0] * si + q[1] * co; pts.push([x, y]); x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }); });
    const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2; let r = 0; pts.forEach((p) => { r = Math.max(r, Math.hypot(p[0] - cx, p[1] - cy)); });
    slot.zone = { x: cx, y: cy, r: r + 40 };
  }

  /* ---------- pointer ---------- */
  const ptr = { x: 0, y: 0, vx: 0, vy: 0, t: -9, on: false, path: 0 };
  function pointerMove(x, y, t) {
    const dt = Math.max(t - ptr.t, 1e-3);
    if (ptr.on && ptr.t > t - 0.2) { const vx = (x - ptr.x) / dt, vy = (y - ptr.y) / dt; ptr.vx = lerp(ptr.vx, vx, 0.6); ptr.vy = lerp(ptr.vy, vy, 0.6); ptr.dx = x - ptr.x; ptr.dy = y - ptr.y; ptr.pend = (ptr.pend || 0) + Math.hypot(x - ptr.x, y - ptr.y); }
    else { ptr.vx = 0; ptr.vy = 0; ptr.pend = 0; }
    ptr.x = x; ptr.y = y; ptr.t = t; ptr.on = true;
  }
  /* nearest outline point of a body to (x, y), world; returns {d, x, y} */
  function nearest(i, x, y) {
    const b = bodies[i], P = PARTS[i], co = Math.cos(b.angle), si = Math.sin(b.angle), bx = b.position.x, by = b.position.y; let best = 1e9, nx = bx, ny = by;
    const o = P.outlineU;
    for (let k = 0; k < o.length; k++) { const wx = bx + o[k][0] * co - o[k][1] * si, wy = by + o[k][0] * si + o[k][1] * co, d = Math.hypot(wx - x, wy - y); if (d < best) { best = d; nx = wx; ny = wy; } }
    return { d: best, x: nx, y: ny };
  }
  function applyPointerStep() {
    if (!ptr.on) return;
    if (sim.t - ptr.t > 0.09) { ptr.on = false; return; }
    const sp = Math.hypot(ptr.vx, ptr.vy); if (sp < 25) return;
    const boost = 1 + sp / K.ptrSpeedBoost, ux = ptr.vx / sp, uy = ptr.vy / sp;
    for (let i = 0; i < N; i++) {
      const b = bodies[i], n = nearest(i, ptr.x, ptr.y);
      if (n.d > K.ptrR) continue;
      let f = 1 - n.d / K.ptrR; f *= f;
      let rx = n.x - ptr.x, ry = n.y - ptr.y, rl = Math.hypot(rx, ry);
      if (rl < 1e-3) { rx = b.position.x - ptr.x; ry = b.position.y - ptr.y; rl = Math.hypot(rx, ry) || 1; }
      rx /= rl; ry /= rl;
      let dx = 0.65 * rx + 0.35 * ux, dy = 0.65 * ry + 0.35 * uy; const dl = Math.hypot(dx, dy) || 1; dx /= dl; dy /= dl;
      const dv = Math.min(K.ptrMaxDv * DT * 10, K.ptrGain * sp * boost * f * DT);        /* velocity gained in this sub-step */
      const v = Body.getVelocity(b), w = Body.getAngularVelocity(b);
      Body.setVelocity(b, { x: v.x + dx * dv / 60, y: v.y + dy * dv / 60 });
      const lx = n.x - b.position.x, ly = n.y - b.position.y, dw = clamp((lx * dy - ly * dx) * dv / Math.max(PARTS[i].rg2, 1), -0.35, 0.35);
      Body.setAngularVelocity(b, w + dw / 60);
    }
  }
  function burst(x, y) {
    for (let i = 0; i < N; i++) {
      const b = bodies[i], n = nearest(i, x, y); if (n.d > K.burstR) continue;
      const f = Math.pow(1 - n.d / K.burstR, 1.5);
      let rx = n.x - x, ry = n.y - y, rl = Math.hypot(rx, ry); if (rl < 1e-3) { rx = b.position.x - x; ry = b.position.y - y; rl = Math.hypot(rx, ry) || 1; }
      rx /= rl; ry /= rl;
      const v = Body.getVelocity(b), w = Body.getAngularVelocity(b), dv = K.burstDv * f;
      Body.setVelocity(b, { x: v.x + rx * dv / 60, y: v.y + ry * dv / 60 });
      const lx = n.x - b.position.x, ly = n.y - b.position.y;
      Body.setAngularVelocity(b, w + clamp((lx * ry - ly * rx) * dv / Math.max(PARTS[i].rg2, 1), -3, 3) / 60);
    }
  }

  /* every member of the sign within 3 px and 1.5 degrees of its place */
  function isFormed(slot) {
    let ok = true;
    PARTS.forEach((P, i) => { if (P.sign !== slot.sign) return; const t2 = S_[i].tgt, b = bodies[i]; if (!t2 || Math.hypot(b.position.x - t2.x, b.position.y - t2.y) > 3 || Math.abs(wrapPi(t2.a - b.angle)) > 0.026) ok = false; });
    return ok;
  }

  /* ---------- one fixed sub-step: controller (forces as velocity changes), pointer, Matter, safety net ---------- */
  function lamOf(slot, t) { return E.io(prog(t, slot.tG, slot.tG + K.gatherLead)) * (1 - E.io(prog(t, slot.tR, slot.tR + K.releaseS))); }
  function step() {
    const t = sim.t; if (!warming) ensureSched(t);
    let slot = null; if (!warming) for (let k = Math.max(0, sched.length - 4); k < sched.length; k++) { const s = sched[k]; if (t >= s.tG && t < s.tR + K.releaseS) slot = s; }
    sim.lam.os = sim.lam.cortex = sim.lam.studio = 0; let lam = 0;
    if (slot) {
      if (!slot.started) startGather(slot);
      lam = lamOf(slot, t); sim.lam[slot.sign] = lam;
      /* a sign the pointer has broken is not released until it has re-formed (at most holdGrace late): push this slot's release and every later slot by one step */
      if (!slot.kicked && t >= slot.tR - DT * 0.5 && t < slot.tR0 + K.holdGrace && slot.formedFor < 0.5) {
        slot.tR += DT; slot.tEnd += DT; slot.pushed += DT;
        for (let k = slot.k + 1; k < sched.length; k++) { sched[k].tG += DT; sched[k].tF += DT; sched[k].tR += DT; sched[k].tR0 += DT; sched[k].tEnd += DT; }
        lam = lamOf(slot, t); sim.lam[slot.sign] = lam;
      }
      if (t >= slot.tR && !slot.kicked) {
        slot.kicked = true;
        PARTS.forEach((P, i) => { if (P.sign !== slot.sign) return; const b = bodies[i], dx = b.position.x - C0[0], dy = b.position.y - C0[1], l = Math.hypot(dx, dy) || 1, v = Body.getVelocity(b);
          Body.setVelocity(b, { x: v.x + dx / l * K.releaseKick / 60, y: v.y + dy / l * K.releaseKick / 60 }); Body.setAngularVelocity(b, Body.getAngularVelocity(b) + S_[i].spin * 0.5 / 60); });
      }
    }
    sim.active = slot;
    for (let i = 0; i < N; i++) {
      const b = bodies[i], P = PARTS[i], s = S_[i]; s.px = b.position.x; s.py = b.position.y; s.pa = b.angle;
      const member = slot && P.sign === slot.sign, lm = member ? lam : 0;
      if (member && lam > 0.25) setFilter(b, SIGN_GROUP[P.sign], CAT.member, s.slowT > 1 ? CAT.member : CAT.wall | CAT.member | (s.dock ? 0 : CAT.dot));   /* members meet the dot as a hard collider until they dock; a docking part slides in radially, so it cannot hook on it */
      else if (slot && lam > 0.25) setFilter(b, 0, CAT.free, 0xFFFF & ~CAT.member);
      else setFilter(b, member && lam > 0.01 ? SIGN_GROUP[P.sign] : 0);
      /* wander: a slowly turning cruising velocity */
      let ph = s.phi + 0.9 * Math.sin(s.w1 * t + s.p1) + 0.5 * Math.sin(s.w2 * t + s.p2); const cs = K.cruise * (0.75 + 0.25 * Math.sin(0.05 * t + s.p3));
      let vtx = Math.cos(ph) * cs, vty = Math.sin(ph) * cs;
      /* a cruising heading that points into an edge, the dot or the zone of a forming sign is mirrored once (so nothing hovers where a push and the cruise balance), and the obstacle pushes out */
      const turn = (nx, ny) => {
        const hx = Math.cos(ph), hy = Math.sin(ph), vin = hx * nx + hy * ny;
        if (vin < -0.02) { const rx = hx - 2 * vin * nx, ry = hy - 2 * vin * ny; s.phi += wrapPi(Math.atan2(ry, rx) - ph); ph = ph + wrapPi(Math.atan2(ry, rx) - ph); vtx = Math.cos(ph) * cs; vty = Math.sin(ph) * cs; }
      };
      const bd = b.bounds, band = K.edgeBand;
      const fL = clamp01((B.x0 + band - bd.min.x) / band), fR = clamp01((bd.max.x - (B.x1 - band)) / band), fT = clamp01((B.y0 + band - bd.min.y) / band), fB = clamp01((bd.max.y - (B.y1 - band)) / band);
      if (fL > 0.1) turn(1, 0); if (fR > 0.1) turn(-1, 0); if (fT > 0.1) turn(0, 1); if (fB > 0.1) turn(0, -1);
      vtx += K.edgeSpeed * (fL - fR); vty += K.edgeSpeed * (fT - fB);
      let dx = b.position.x - C0[0], dy = b.position.y - C0[1], dl = Math.hypot(dx, dy) || 1;
      const rs = R_EX + P.rb * 0.5 + K.dotBand;
      if (dl < rs && !member) {
        const f = clamp01((rs - dl) / K.dotBand) * (1 - lm), nx = dx / dl, ny = dy / dl;
        if (f > 0.1) turn(nx, ny);
        vtx += nx * K.dotSpeed * f; vty += ny * K.dotSpeed * f;
      }
      let nmGain = 0;
      if (slot && !member && slot.zone) {
        const zx = b.position.x - slot.zone.x, zy = b.position.y - slot.zone.y, zl = Math.hypot(zx, zy) || 1, zr = slot.zone.r + P.rb * 1.0;
        /* pushed away from the dot, not from the zone centre: every sign holds the dot, and a ring half pushed from a centre above it was pressed onto the dot and stayed under the next sign */
        if (zl < zr) { const f = clamp01((zr - zl) / 50) * lam, nx = dx / dl, ny = dy / dl; if (f > 0.1) turn(nx, ny); vtx += nx * K.zoneSpeed * f; vty += ny * K.zoneSpeed * f; nmGain = K.zoneGain * f; }
      }
      let wt = s.spin * K.cruiseSpin * (0.7 + 0.3 * Math.sin(0.09 * t + s.p2));
      const v = Body.getVelocity(b), w = Body.getAngularVelocity(b); let vx = v.x * 60, vy = v.y * 60, om = w * 60;
      let gain = K.steer + nmGain, wgain = K.spinSteer, vdx = vtx, vdy = vty;
      if (lm > 0 && s.tgt) {
        /* two legs: first to a staging pose K.stage px further out along the line from the dot, then in along that line (a ring half or a bar that arrives
           turned and eccentric would hook on the dot; coming in radially it cannot) */
        const T = s.tgt, tx = T.x - C0[0], ty = T.y - C0[1], tl2 = Math.hypot(tx, ty) || 1;
        let so = K.stage;                                   /* the staging pose must leave room to turn: shorten the leg until a circle round the part fits in the stage */
        while (so > 0 && (T.x + tx / tl2 * so < B.x0 + P.rb + 4 || T.x + tx / tl2 * so > B.x1 - P.rb - 4 || T.y + ty / tl2 * so < B.y0 + P.rb + 4 || T.y + ty / tl2 * so > B.y1 - P.rb - 4)) so -= 10;
        const sx0 = T.x + tx / tl2 * Math.max(0, so), sy0 = T.y + ty / tl2 * Math.max(0, so);
        const dT = Math.hypot(b.position.x - T.x, b.position.y - T.y), dS = Math.hypot(b.position.x - sx0, b.position.y - sy0), dA = Math.abs(wrapPi(T.a - b.angle));
        if (!s.dock && dS < 35 && dA < 0.35) s.dock = 1; else if (s.dock && dT > K.stage + 60) s.dock = 0;
        /* a member that cannot make headway (wedged against an edge) for a second passes through whatever holds it until it is home */
        s.slowT = (Math.hypot(vx, vy) < 6 && dT > 20) ? s.slowT + DT : (dT < 8 ? 0 : Math.max(0, s.slowT - DT));
        /* leg 0: a part that still has to turn does it well away from the dot (its bounding circle clear of the dot and of the stage edges), so the turn cannot sweep through either */
        const rotNeed = !s.dock && dA >= 0.35, distDot = Math.hypot(b.position.x - C0[0], b.position.y - C0[1]);
        let DR = P.rb + R_COL + 15, prx = b.position.x, pry = b.position.y, rotFar = 1;
        if (rotNeed) {
          const inBox = (x, y, m) => x >= B.x0 + P.rb + m && x <= B.x1 - P.rb - m && y >= B.y0 + P.rb + m && y <= B.y1 - P.rb - m;
          for (; DR > R_COL + 20; DR -= 25) { let best = 1e18; for (let k = 0; k < 72; k++) { const an = k * Math.PI / 36, x = C0[0] + DR * Math.cos(an), y = C0[1] + DR * Math.sin(an); if (!inBox(x, y, 4)) continue; const q = (x - b.position.x) ** 2 + (y - b.position.y) ** 2; if (q < best) { best = q; prx = x; pry = y; } } if (best < 1e17) break; }
          if (distDot >= DR - 10 && inBox(b.position.x, b.position.y, 0)) { prx = b.position.x; pry = b.position.y; }
          rotFar = clamp01((distDot - (DR - 50)) / 40);
        }
        const aimX = s.dock ? T.x : rotNeed ? prx : sx0, aimY = s.dock ? T.y : rotNeed ? pry : sy0;
        const ex = aimX - b.position.x, ey = aimY - b.position.y, d = Math.hypot(ex, ey), sp = Math.min(K.kp * d, K.vSpring);
        let sx = d > 1e-6 ? ex / d * sp : 0, sy = d > 1e-6 ? ey / d * sp : 0;
        /* go round the dot rather than through it when it is in the way */
        const ax = dx / dl, ay = dy / dl, cs2 = d > 1e-6 ? (ax * ex + ay * ey) / d : 1;
        if (!s.dock && cs2 < 0 && d > 40) { const perp = Math.abs(ax * ey - ay * ex) / d, clear = R_EX + P.rb * 0.8; if (perp < clear) { const k = (-cs2) * (1 - perp / clear), sgn = Math.sign(ax * ey - ay * ex) || s.hand; sx += -ay * sgn * sp * 0.9 * k; sy += ax * sgn * sp * 0.9 * k; } }
        vdx = lerp(vtx, sx, lm); vdy = lerp(vty, sy, lm); { const m2 = Math.hypot(vdx, vdy); if (lm > 0.25 && m2 > K.vSpring) { vdx *= K.vSpring / m2; vdy *= K.vSpring / m2; } } gain = lerp(K.steer, K.kv, lm);
        /* turn only where the part's bounding circle clears the stage edges: a half ring turning against the wall is held by it (friction) and never gets out */
        const wallD = Math.min(b.position.x - B.x0, B.x1 - b.position.x, b.position.y - B.y0, B.y1 - b.position.y), ar = clamp01((wallD - P.rb * 0.75) / (P.rb * 0.25));
        const wd = clamp(K.kth * wrapPi(s.tgt.a - b.angle), -K.wSpring, K.wSpring) * (s.dock ? 1 : ar * (rotNeed ? rotFar : 1)); wt = lerp(wt, wd, lm); wgain = lerp(K.spinSteer, K.kw, lm);
      }
      vx += (vdx - vx) * Math.min(1, gain * DT); vy += (vdy - vy) * Math.min(1, gain * DT); om += (wt - om) * Math.min(1, wgain * DT);
      Body.setVelocity(b, { x: vx / 60, y: vy / 60 }); Body.setAngularVelocity(b, om / 60);
      /* the parts that are not in the sign dim, so the sign reads */
      const dimTarget = slot ? lerp(1, K.dimTo, member ? 0 : lam) : 1;
      s.op += (dimTarget - s.op) * Math.min(1, 6 * DT);
    }
    applyPointerStep();
    const t0 = performance.now();
    Engine.update(engine, 1000 / K.SUB);
    const ms = performance.now() - t0; sim.simMs += ms; if (ms > sim.worstSimMs) sim.worstSimMs = ms;
    for (let i = 0; i < N; i++) {                      /* safety net: caps and stage edge */
      const b = bodies[i], s = S_[i], v = Body.getVelocity(b), sp = Math.hypot(v.x, v.y) * 60;
      if (sp > K.vmax) Body.setVelocity(b, { x: v.x * K.vmax / sp, y: v.y * K.vmax / sp });
      const w = Body.getAngularVelocity(b) * 60; if (Math.abs(w) > K.wmax) Body.setAngularVelocity(b, Math.sign(w) * K.wmax / 60);
      const bd = b.bounds; let ox = 0, oy = 0;
      if (bd.min.x < B.x0) ox = B.x0 - bd.min.x; else if (bd.max.x > B.x1) ox = B.x1 - bd.max.x;
      if (bd.min.y < B.y0) oy = B.y0 - bd.min.y; else if (bd.max.y > B.y1) oy = B.y1 - bd.max.y;
      if (ox || oy) {                                    /* a corner of a part got past the stage edge: put the part back and turn the speed that carried it out */
        const vv = Body.getVelocity(b); if (Math.max(Math.abs(ox), Math.abs(oy)) > 6) { sim.escapes++; if (sim.escLog.length < 30) sim.escLog.push({ t: +t.toFixed(2), id: PARTS[i].id, ox: +ox.toFixed(1), oy: +oy.toFixed(1), v: +(Math.hypot(vv.x, vv.y) * 60).toFixed(0), lam: +sim.lam[slot ? slot.sign : 'os'].toFixed(2), member: !!(slot && PARTS[i].sign === slot.sign) }); } sim.nudges++;
        Body.setPosition(b, { x: b.position.x + ox, y: b.position.y + oy });
        Body.setVelocity(b, { x: ox && Math.sign(ox) !== Math.sign(vv.x) ? -vv.x * 0.6 : vv.x, y: oy && Math.sign(oy) !== Math.sign(vv.y) ? -vv.y * 0.6 : vv.y });
      }
      s.x = b.position.x; s.y = b.position.y; s.a = b.angle;
    }
    /* bookkeeping for the formation log */
    if (slot) {
      const ok = isFormed(slot); slot.formedFor = ok ? slot.formedFor + DT : 0;
      if (ok && slot.formedAt === null) slot.formedAt = t - slot.tG;
      if (ok && !slot.wasFormed) slot.wasFormed = true; else if (!ok && slot.wasFormed && slot.formedAt !== null && t < slot.tR) { slot.broke++; slot.wasFormed = false; }
      if (t >= slot.tF && t < slot.tR) { slot.holdN++; if (ok) slot.holdOk++; }
    }
    sim.t += DT; sim.steps++;
  }
  /* warm-up: let the first overlaps of the random placement resolve, then start the clock at 0 */
  warming = true; if (!RM) for (let k = 0; k < 600; k++) step(); warming = false;
  sim.t = 0; sim.steps = 0; sched.length = 0; sim.simMs = 0; sim.worstSimMs = 0; sim.escapes = 0; sim.nudges = 0; sim.escLog.length = 0;
  for (let i = 0; i < N; i++) { const b = bodies[i], s = S_[i]; s.px = s.x = b.position.x; s.py = s.y = b.position.y; s.pa = s.a = b.angle; s.op = 1; s.tgt = null; }

  /* ---------- sound (same as the other prototypes: only after a gesture, track and effect of C) ---------- */
  let hintEl, goEl, hintTimer, goTimer;
  function setHint(txt) { if (hintEl) { hintEl.textContent = txt; showHint(); } }
  function showHint(ms) { if (!hintEl || document.body.dataset.phase !== 'loop') return; document.body.classList.add('hint-on'); clearTimeout(hintTimer); hintTimer = setTimeout(() => document.body.classList.remove('hint-on'), ms || 6000); }
  function hideGo() { document.body.classList.remove('go-on'); clearTimeout(goTimer); }
  const Snd = {
    ctx: null, master: null, bedBus: null, sfxBus: null, bedBuf: null, sfxBuf: null, timer: 0, next: 0, on: false, muted: false, ready: false, log: [],
    async enable() {
      if (this.ctx) { this.toggle(); return; }
      const D = window.PRESHOW_AUDIO; this.on = true;
      if (!D) { setHint('Sound file not found'); return; }
      const AC = window.AudioContext || window.webkitAudioContext; this.ctx = new AC(); const ctx = this.ctx;
      this.master = ctx.createGain(); this.master.gain.value = this.muted ? 0 : 1; this.master.connect(ctx.destination);
      this.bedBus = ctx.createGain(); this.bedBus.gain.value = 1; this.bedBus.connect(this.master);
      this.sfxBus = ctx.createGain(); this.sfxBus.gain.value = D.sfxGain || 0.9; this.sfxBus.connect(this.master);
      const dec = (b64) => { const bin = atob(b64), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return ctx.decodeAudioData(u.buffer); };
      try { [this.bedBuf, this.sfxBuf] = await Promise.all([dec(D.bed), dec(D.sfx)]); } catch (e) { setHint('Sound could not be decoded'); return; }
      this.ready = true; setHint('Sound on · M mute · S stop');
      if (this.ctx.state === 'suspended') await this.ctx.resume();
      this.next = ctx.currentTime + 0.1; this.first = true; this.pump(); this.timer = setInterval(() => this.pump(), 250);
    },
    pump() {
      const D = window.PRESHOW_AUDIO, ctx = this.ctx; if (!ctx || !this.ready || this.stopped) return;
      while (this.next < ctx.currentTime + 2.5) {
        const t = this.next, X = D.bedX, W = D.bedW, g = ctx.createGain(), src = ctx.createBufferSource();
        src.buffer = this.bedBuf; src.connect(g); g.connect(this.bedBus);
        const n = 48, up = new Float32Array(n), dn = new Float32Array(n);
        for (let i = 0; i < n; i++) { const p = i / (n - 1); up[i] = Math.sin(p * Math.PI / 2); dn[i] = Math.cos(p * Math.PI / 2); }
        const fin = this.first ? 2.0 : X; this.first = false;
        g.gain.setValueAtTime(0, t); g.gain.setValueCurveAtTime(up, t, fin); g.gain.setValueAtTime(1, t + fin);
        g.gain.setValueAtTime(1, t + W); g.gain.setValueCurveAtTime(dn, t + W, X);
        src.start(t); src.stop(t + W + X + 0.05); this.next += W;
      }
    },
    toggle() {
      if (!this.ctx) return;
      if (this.stopped) { this.stopped = false; this.next = this.ctx.currentTime + 0.1; this.first = true; this.bedBus.gain.cancelScheduledValues(0); this.bedBus.gain.value = 1; this.pump(); setHint('Sound on · M mute · S stop'); }
      else { this.stopped = true; this.bedBus.gain.cancelScheduledValues(0); this.bedBus.gain.setTargetAtTime(0, this.ctx.currentTime, 0.2); setHint('Sound off · press S'); }
    },
    mute() { this.muted = !this.muted; if (this.master) this.master.gain.setTargetAtTime(this.muted ? 0 : 1, this.ctx.currentTime, 0.05); },
    onStart(spec) {
      const ctx = this.ctx; if (!ctx || !this.ready) return;
      const now = ctx.currentTime, g = this.bedBus.gain;
      g.cancelScheduledValues(now); g.setValueAtTime(this.stopped ? 0 : g.value, now); g.linearRampToValueAtTime(0.3, now + 0.5);
      g.setValueAtTime(0.3, now + Math.max(0.5, spec.boomAt - 0.2)); g.linearRampToValueAtTime(0, now + spec.boomAt + 1.4);
      const delay = Math.max(0, spec.boomAt - spec.sfxKey), offset = Math.max(0, spec.sfxKey - spec.boomAt);
      const s = ctx.createBufferSource(); s.buffer = this.sfxBuf; s.connect(this.sfxBus); s.start(now + 0.03 + delay, offset);
      this.log.push({ at: now, delay, offset });
    }
  };
  const SPEC = { name: 'C2', boomAt: K.KEY, sfxKey: 0.5 };

  /* ---------- scene ---------- */
  const svg = document.getElementById('stage'), scene = document.getElementById('scene'), gParts = document.getElementById('parts'), gSwap = document.getElementById('wmSwap'), gDot = document.getElementById('dotG');
  const lightLayer = document.getElementById('lightLayer'), floodC = document.getElementById('floodC'), opener = document.getElementById('opener'), lineEl = document.getElementById('line');
  const rmLayer = document.getElementById('rmLayer'), veil = document.getElementById('veil');
  hintEl = document.getElementById('hint-sound'); goEl = document.getElementById('hint-go');
  document.body.classList.toggle('dark', DARK);
  svg.style.setProperty('--ink', DARK ? COL.white : COL.ink);
  document.body.dataset.phase = 'loop';
  const partEl = PARTS.map((P) => el('path', { d: P.d, class: 'ink' }, gParts));
  const dotEl = el('path', { d: G.UNIT_DOT, class: 'grn' }, gDot);
  const wmOT = el('path', { d: G.WM.OT.d, class: 'ink' }, gSwap), wmOB = el('path', { d: G.WM.OB.d, class: 'ink' }, gSwap), wmCore = el('path', { d: G.UNIT_DOT, class: 'grn' }, gSwap);
  const dotTf = (x, y, r) => 'translate(' + f3(x) + ' ' + f3(y) + ') scale(' + f3(r) + ')';
  const D_R0 = G.DOT_R * K.S;
  dotEl.setAttribute('transform', dotTf(C0[0], C0[1], D_R0));
  if (DARK) document.getElementById('lightUse').setAttribute('style', '--ink:' + COL.ink);

  /* opener A, the static rest state (same as the other prototypes) */
  const gO = el('g', { class: 'ink', transform: 'translate(' + G.OPENER.left + ' ' + G.OPENER.top + ') scale(' + G.OPENER.k + ') translate(' + -G.WM_VB[0] + ' ' + -G.WM_VB[1] + ')' }, opener);
  ['B1', 'B2', 'B3', 'N1', 'N2', 'G', 'OT', 'OB', 'S'].forEach((id) => el('path', { d: G.WM[id].d }, gO));
  el('circle', { cx: G.CORE.c[0], cy: G.CORE.c[1], r: G.CORE.r, fill: COL.green }, gO);
  lineEl.setAttribute('x', G.OPENER.lineX); lineEl.setAttribute('y', G.OPENER.lineY); lineEl.setAttribute('font-size', G.OPENER.lineSize); lineEl.setAttribute('font-weight', G.OPENER.lineWeight); lineEl.textContent = G.OPENER.text;

  /* reduced motion: the dot and the assembled OS sign, still; Space cross-fades to the opener */
  let rmSign = null;
  if (RM) {
    rmLayer.setAttribute('display', 'inline'); svg.setAttribute('data-rm', '1');
    const sc = 3.4, g = el('g', { transform: 'translate(' + (720 - 48 * sc) + ' ' + (450 - 48 * sc) + ') scale(' + sc + ')' }, rmLayer);
    [SG.os.top, SG.os.bot].forEach((d) => el('path', { d, class: 'ink' }, g));
    el('circle', { cx: 48, cy: 48, r: G.DOT_R, fill: COL.green }, g); rmSign = g; scene.setAttribute('display', 'none');
  }

  /* ---------- render of the idle loop ---------- */
  function poseTf(x, y, aDeg, s, P) { return 'translate(' + f3(x) + ' ' + f3(y) + ') rotate(' + f3(aDeg) + ') scale(' + f3(s) + ') translate(' + f3(-P.comU.x) + ' ' + f3(-P.comU.y) + ')'; }
  function renderLoop(alpha) {
    for (let i = 0; i < N; i++) { const s = S_[i], P = PARTS[i]; partEl[i].setAttribute('transform', poseTf(lerp(s.px, s.x, alpha), lerp(s.py, s.y, alpha), lerp(s.pa, s.a, alpha) * 180 / Math.PI, P.sc, P)); partEl[i].setAttribute('opacity', s.op >= 0.999 ? 1 : f3(s.op)); }
  }
  renderLoop(1);

  /* ---------- phases ---------- */
  let phase = 'loop', tl = null, virt = false, acc = 0, lastTs = 0, simClock = 0;
  const stat = { frames: 0, worst: 0, sum: 0, long: 0, worstRender: 0, simMs: 0, worstSimMs: 0 };

  function enterRest() {
    phase = 'rest'; document.body.dataset.phase = 'rest'; document.body.classList.remove('hint-on', 'go-on');
    if (tl) { tl.pause(); }
    scene.setAttribute('display', 'none'); lightLayer.setAttribute('display', 'none'); rmLayer.setAttribute('display', 'none');
    opener.setAttribute('display', 'inline'); opener.setAttribute('opacity', 1); lineEl.setAttribute('opacity', 1); lineEl.setAttribute('transform', 'translate(0 0)');
    document.body.classList.remove('dark'); veil.style.opacity = 0; svg.style.setProperty('--ink', COL.ink);
  }

  /* the start: everything below is the GSAP timeline plus compose(), which turns the timeline's numbers into poses */
  const TAU_COAST = 0.55;
  let H = null;            /* the hand-over: state of every body at the press */
  const ws = {}, gq = { q: 0 }, fl = { r: 0 }, lineSt = { o: 0, dy: 14 }, rmSt = { e: 0 };
  function begin() {
    if (phase !== 'loop') return;
    hideGo(); document.body.classList.remove('hint-on');
    phase = 'trans'; document.body.dataset.phase = 'trans';
    if (RM) {
      tl = gsap.timeline({ paused: true, onUpdate: composeRM }).to(rmSt, { e: 1, duration: 0.6, ease: E.io }, 0);
      Snd.onStart(SPEC); if (!virt) tl.play(0); return;
    }
    const alpha = virt ? 1 : acc / DT;
    H = { items: [], lam: sim.lam };
    /* ring halves: choose which slot each one closes into (the same shape turned 180 degrees): the cheaper pairing */
    const ringPose = (i, flip) => { const P = PARTS[i], du = DOTU.os; let dx = (P.comU.x - du[0]), dy = (P.comU.y - du[1]), a = 0; if (flip) { dx = -dx; dy = -dy; a = Math.PI; } return { dx, dy, a }; };
    const cur = PARTS.map((P, i) => {
      const s = S_[i], b = bodies[i], v = Body.getVelocity(b);
      return { x: lerp(s.px, s.x, alpha), y: lerp(s.py, s.y, alpha), a: lerp(s.pa, s.a, alpha), vx: v.x * 60, vy: v.y * 60, om: Body.getAngularVelocity(b) * 60, op: s.op };
    });
    const costRing = (flipT, flipB) => {
      let c = 0; [[0, flipT], [1, flipB]].forEach(([i, fl2]) => { const r = ringPose(i, fl2), tx = C0[0] + r.dx * K.S, ty = C0[1] + r.dy * K.S; c += Math.hypot(cur[i].x - tx, cur[i].y - ty) + 120 * Math.abs(wrapPi(r.a - cur[i].a)); });
      return c;
    };
    const flipRing = costRing(true, true) < costRing(false, false);
    PARTS.forEach((P, i) => {
      const c = cur[i], it = { i, c, kind: P.sign === 'os' ? 'ring' : P.sign ? 'absorb' : 'letter' };
      if (it.kind === 'letter') {
        const f = G.wmPos(P.comU.x, P.comU.y); it.tx = f[0]; it.ty = f[1]; it.ta = Math.round(c.a / TAU) * TAU;
        const dist = Math.hypot(c.x - f[0], c.y - f[1]), rank = ['B1', 'B2', 'B3', 'N1', 'N2', 'G', 'S'].indexOf(P.id);
        it.d0 = 0.05 + 0.05 * rank; it.dur = 1.65 + 0.0006 * dist; if (it.d0 + it.dur > 2.45) it.dur = 2.45 - it.d0;
      } else if (it.kind === 'ring') {
        const r = ringPose(i, flipRing); it.dx = r.dx; it.dy = r.dy; it.ta = c.a + wrapPi(r.a - c.a); it.d0 = 0; it.dur = 1.1;
      } else { it.d0 = 0.04 + 0.04 * (i % 6); it.dur = 1.15; }
      H.items.push(it);
    });
    H.grp = { t0: K.settle0, t1: K.settle1 };
    tl = gsap.timeline({ paused: true, onUpdate: compose });
    H.items.forEach((it) => { ws[it.i] = 0; tl.to(ws, { [it.i]: 1, duration: it.dur, ease: E.sync }, it.d0); });
    gq.q = 0; fl.r = 0; lineSt.o = 0; lineSt.dy = 14;
    tl.to(gq, { q: 1, duration: H.grp.t1 - H.grp.t0, ease: E.sync }, H.grp.t0);
    tl.to(fl, { r: 4600, duration: 1.2, ease: E.io }, 1.1);
    tl.to(lineSt, { o: 1, dy: 0, duration: 0.5, ease: E.out }, K.KEY + 0.4);
    tl.to({}, { duration: 0.001 }, K.Tt - 0.001);
    Snd.onStart(SPEC);
    if (!virt) tl.play(0); else compose();
  }
  const D_R1 = G.CORE.r * G.OPENER.k;
  function compose() {
    const u = tl.time();
    if (u >= K.Tt) { enterRest(); return; }
    const q = gq.q, cx = lerp(C0[0], G.O_CENTRE[0], q), cy = lerp(C0[1], G.O_CENTRE[1], q), sg = K.S * Math.pow(G.O_SIGN_SCALE / K.S, q), rd = D_R0 * Math.pow(D_R1 / D_R0, q);
    const f = TAU_COAST * (1 - Math.exp(-u / TAU_COAST)), swap = u >= K.KEY + 0.4;
    H.items.forEach((it) => {
      const c = it.c, P = PARTS[it.i], w = ws[it.i], e = partEl[it.i];
      const x0 = c.x + c.vx * f, y0 = c.y + c.vy * f, a0 = c.a + c.om * f;
      let tx, ty, ta, ts, o;
      if (it.kind === 'letter') { tx = it.tx; ty = it.ty; ta = it.ta; ts = G.OPENER.k; o = lerp(c.op, 1, E.out(prog(u, 0, 0.9))); }
      else if (it.kind === 'ring') {
        /* a flipped half is the same shape turned half a turn: its COM offset is already mirrored in dx, dy */
        tx = cx + sg * it.dx; ty = cy + sg * it.dy; ta = it.ta; ts = sg; o = lerp(c.op, 1, E.out(prog(u, 0, 0.6)));
      } else { tx = cx; ty = cy; ta = a0 + 1.2; ts = P.sc * 0.03; o = c.op * (1 - E.io(prog(w, 0.7, 1))); }
      const s = P.sc * Math.pow(Math.max(ts, 1e-4) / P.sc, w);
      const a = lerp(a0, ta, w);
      if ((swap && it.kind !== 'letter') || o <= 0.002) { if (e.getAttribute('display') !== 'none') e.setAttribute('display', 'none'); }
      else { if (e.hasAttribute('display')) e.removeAttribute('display'); e.setAttribute('transform', poseTf(lerp(x0, tx, w), lerp(y0, ty, w), a * 180 / Math.PI, s, P)); e.setAttribute('opacity', o >= 0.999 ? 1 : f3(o)); }
    });
    /* the dot: stays at the centre until the group starts to move; only part of the settle */
    const pulse = 1 + 0.12 * Math.sin(Math.PI * prog(u, K.KEY, K.KEY + 0.4));
    if (swap) {
      dotEl.setAttribute('display', 'none'); gSwap.removeAttribute('display');
      const O = G.O_CENTRE, k = G.OPENER.k;
      wmOT.setAttribute('transform', 'translate(' + O[0] + ' ' + O[1] + ') scale(' + k + ') translate(' + -G.WM.OT.pv[0] + ' ' + -G.WM.OT.pv[1] + ')');
      wmOB.setAttribute('transform', 'translate(' + O[0] + ' ' + O[1] + ') scale(' + k + ') translate(' + -G.WM.OB.pv[0] + ' ' + -G.WM.OB.pv[1] + ')');
      wmCore.setAttribute('transform', dotTf(O[0], O[1], G.CORE.r * k));
    } else dotEl.setAttribute('transform', dotTf(cx, cy, rd * pulse));
    if (DARK) {
      if (fl.r > 0.5) { lightLayer.setAttribute('display', 'inline'); floodC.setAttribute('transform', 'translate(' + f3(G.O_CENTRE[0]) + ' ' + f3(G.O_CENTRE[1]) + ') scale(' + f3(fl.r) + ')'); }
    }
    lineEl.setAttribute('opacity', f3(lineSt.o)); lineEl.setAttribute('transform', 'translate(0 ' + f3(lineSt.dy) + ')');
  }
  function composeRM() {
    const e = rmSt.e;
    if (tl.time() >= 0.6) { enterRest(); return; }
    rmSign.setAttribute('opacity', f3(1 - e)); opener.setAttribute('display', 'inline'); opener.setAttribute('opacity', f3(e)); lineEl.setAttribute('opacity', f3(e));
    if (DARK) veil.style.opacity = f3(e);
  }

  /* ---------- input ---------- */
  function advance() {
    if (phase === 'loop') begin();
    else if (phase === 'rest') document.dispatchEvent(new CustomEvent('preshow:done', { bubbles: true }));
  }
  function toStage(cx, cy) {
    const vw = window.innerWidth, vh = window.innerHeight, k = Math.min(vw / 1440, vh / 900);
    return [720 + (cx - vw / 2) / k, 450 + (cy - vh / 2) / k];
  }
  window.addEventListener('keydown', (e) => {
    if (e.repeat) return;
    if (e.code === 'Space' || e.code === 'Enter' || e.code === 'ArrowRight') { e.preventDefault(); hideGo(); advance(); }
    else if (e.code === 'KeyS') { hideGo(); Snd.enable(); if (Snd.ctx && !Snd.on) Snd.on = true; }
    else if (e.code === 'KeyM') { Snd.mute(); }
  });
  if (!RM) {
    svg.addEventListener('pointermove', (e) => { if (phase !== 'loop') return; const p = toStage(e.clientX, e.clientY); pointerMove(p[0], p[1], virt ? sim.t : simClock); });
    svg.addEventListener('pointerdown', (e) => { if (phase !== 'loop') return; const p = toStage(e.clientX, e.clientY); ptr.on = false; burst(p[0], p[1]); });
    svg.addEventListener('pointerleave', () => { ptr.on = false; });
    svg.addEventListener('pointercancel', () => { ptr.on = false; });
  }
  hintEl.addEventListener('click', (e) => { e.stopPropagation(); Snd.enable(); });
  window.addEventListener('resize', () => { if (RM) return; B = stageBounds(); buildWalls(); bodies.forEach((b) => { const p = b.position; Body.setPosition(b, { x: clamp(p.x, B.x0 + 10, B.x1 - 10), y: clamp(p.y, B.y0 + 10, B.y1 - 10) }); }); });
  document.body.classList.add('go-on'); goTimer = setTimeout(() => document.body.classList.remove('go-on'), 14000);
  showHint(8000);

  /* ---------- the frame loop: fixed sub-steps with an accumulator, rendering interpolated between the last two ---------- */
  function frame(ts) {
    const tNow = ts / 1000;
    if (lastTs) { const dt = tNow - lastTs; stat.frames++; stat.sum += dt; if (dt > stat.worst) stat.worst = dt; if (dt > 0.0205) stat.long++; }
    const dtr = lastTs ? Math.min(0.05, tNow - lastTs) : 0; lastTs = tNow;
    if (!virt) {
      const r0 = performance.now();
      if (phase === 'loop' && !RM) {
        acc += dtr; simClock += dtr; sim.simMs = 0; let n = 0;
        while (acc >= DT && n < 12) { step(); acc -= DT; n++; }
        if (n === 12) acc = 0;
        renderLoop(acc / DT);
        if (sim.simMs > stat.worstSimMs) stat.worstSimMs = sim.simMs;
      }
      const rd = performance.now() - r0; if (rd > stat.worstRender) stat.worstRender = rd;
    }
    requestAnimationFrame(frame);
  }
  if (!RM) requestAnimationFrame(frame); else requestAnimationFrame(function f(ts) { const tn = ts / 1000; if (lastTs) { const dt = tn - lastTs; stat.frames++; stat.sum += dt; if (dt > stat.worst) stat.worst = dt; } lastTs = tn; requestAnimationFrame(f); });
  gsap.ticker.lagSmoothing(0);

  /* ---------- test hooks (no effect on the show) ---------- */
  function worldVerts(i) { const out = []; bodies[i].parts.forEach((p, k) => { if (k === 0 && bodies[i].parts.length > 1) return; out.push(p.vertices); }); return out; }
  function distToPoly(v, x, y) {                      /* signed: negative inside */
    let best = 1e9, inside = false;
    for (let a = 0, b = v.length - 1; a < v.length; b = a++) {
      const ax = v[a].x, ay = v[a].y, bx = v[b].x, by = v[b].y, dx = bx - ax, dy = by - ay, l2 = dx * dx + dy * dy || 1e-9, t = clamp(((x - ax) * dx + (y - ay) * dy) / l2, 0, 1);
      best = Math.min(best, Math.hypot(ax + dx * t - x, ay + dy * t - y));
      if ((ay > y) !== (by > y) && x < (bx - ax) * (y - ay) / (by - ay) + ax) inside = !inside;
    }
    return inside ? -best : best;
  }
  const api = {
    K, PARTS, sim, S_, E, G, Snd, bodies, sched, R_EX, SEED,
    virtual(v) { virt = v; },
    step(n) { for (let k = 0; k < (n || 1); k++) step(); },
    render() { renderLoop(1); },
    press() { begin(); },
    seek(u) { if (!tl) return; tl.time(u, true); if (phase === 'trans') { if (RM) composeRM(); else compose(); } },
    phase() { return phase; },
    pointer(x, y) { pointerMove(x, y, sim.t); },
    burst(x, y) { burst(x, y); },
    pointerOff() { ptr.on = false; },
    stats() { return { frames: stat.frames, worstMs: stat.worst * 1000, avgMs: stat.frames ? stat.sum / stat.frames * 1000 : 0, longFrames: stat.long, worstRenderMs: stat.worstRender, worstSimMs: stat.worstSimMs }; },
    resetStats() { stat.frames = 0; stat.worst = 0; stat.sum = 0; stat.long = 0; stat.worstRender = 0; stat.worstSimMs = 0; },
    /* geometry audit of the current state: dot clearance (negative = a part intrudes into the clear space), edge overrun, speeds */
    audit() {
      let minClear = 1e9, minWho = '', over = 0, vmax = 0, wmaxv = 0, outside = 0, clearMem = 1e9, clearFree = 1e9, whoFree = '';
      const act = sim.active && sim.lam[sim.active.sign] > 0.25 ? sim.active.sign : null;
      for (let i = 0; i < N; i++) {
        const vs = worldVerts(i); let d = 1e9;
        vs.forEach((v) => { d = Math.min(d, distToPoly(v, C0[0], C0[1])); v.forEach((p) => { over = Math.max(over, B.x0 - p.x, p.x - B.x1, B.y0 - p.y, p.y - B.y1); }); });
        if (d < minClear) { minClear = d; minWho = PARTS[i].id; }
        if (act && PARTS[i].sign === act) clearMem = Math.min(clearMem, d); else if (d < clearFree) { clearFree = d; whoFree = PARTS[i].id; }
        const v = Body.getVelocity(bodies[i]); vmax = Math.max(vmax, Math.hypot(v.x, v.y) * 60); wmaxv = Math.max(wmaxv, Math.abs(Body.getAngularVelocity(bodies[i]) * 60));
        const p = bodies[i].position; if (p.x < B.x0 || p.x > B.x1 || p.y < B.y0 || p.y > B.y1) outside++;
      }
      return { clearance: minClear - R_EX, who: minWho, clearFree: clearFree - R_EX, whoFree, clearMem: clearMem - R_EX, overrun: over, vmax, wmax: wmaxv, comOutside: outside };
    },
    dbg(id) {
      const i = PARTS.findIndex((P) => P.id === id), b = bodies[i], v = Body.getVelocity(b), pairs = [];
      (engine.pairs.list || []).forEach((p) => { if (!p.isActive) return; const a = p.bodyA.parent, c = p.bodyB.parent; if (a === b || c === b) pairs.push((a === b ? c : a).label || (a === b ? c : a).id); });
      return { dock: S_[i].dock, slowT: S_[i].slowT, rb: PARTS[i].rb, B, C0, v: [v.x * 60, v.y * 60], w: Body.getAngularVelocity(b) * 60, bounds: [b.bounds.min.x, b.bounds.min.y, b.bounds.max.x, b.bounds.max.y], pairs, cat: b.collisionFilter.mask };
    },
    poses() { return PARTS.map((P, i) => ({ id: P.id, x: S_[i].x, y: S_[i].y, a: S_[i].a, op: S_[i].op })); },
    members() { return PARTS.map((P, i) => ({ id: P.id, sign: P.sign, tgt: S_[i].tgt, x: bodies[i].position.x, y: bodies[i].position.y, a: bodies[i].angle })); },
    formed() { return sim.active ? isFormed(sim.active) : null; },
    velocities() { return bodies.map((b) => { const v = Body.getVelocity(b); return { x: v.x * 60, y: v.y * 60, w: Body.getAngularVelocity(b) * 60 }; }); },
    tlTime() { return tl ? tl.time() : null; },
    handoverPose(i) { const s = S_[i]; return { x: s.x, y: s.y, a: s.a }; }
  };
  window.__preshow = api; window.__c2 = api;
})();
