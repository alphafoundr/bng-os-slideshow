/* BNG OS sound. The bed (C's track, 32 s loop with a 2 s crossfade) plays from the first moment the browser lets it: at load where
   autoplay is allowed, otherwise on the first pointer or key event. M mutes; the choice is kept in localStorage. Same files and
   same transition sound as the pre-show prototype C2 (slideshow/preshow/audio/c.js, decoded to audio/bed.mp3 and audio/sfx.mp3).
   Exposes window.BNG_AUDIO { muted, toggle(), mute(), onStart(spec), deck() } and fires "bng:audio" on window when the state changes. */
(function () {
  'use strict';
  var KEY = 'bng-os-muted', W = 32, X = 2, SFX_GAIN = 0.9, DECK_LEVEL = 0.35;
  function get() { try { return window.localStorage.getItem(KEY); } catch (e) { return null; } }
  function put(v) { try { window.localStorage.setItem(KEY, v); } catch (e) { /* ignore */ } }
  var S = { ctx: null, master: null, bedBus: null, sfxBus: null, bedBuf: null, sfxBuf: null, timer: 0, next: 0, first: true, ready: false, started: false, muted: get() === '1', log: [] };

  function emit() { try { window.dispatchEvent(new CustomEvent('bng:audio', { detail: { muted: S.muted } })); } catch (e) { /* ignore */ } }
  function decode(url) {
    return fetch(url).then(function (r) { if (!r.ok) throw new Error(url); return r.arrayBuffer(); }).then(function (b) {
      return new Promise(function (res, rej) { var p = S.ctx.decodeAudioData(b, res, rej); if (p && p.then) p.then(res, rej); });
    });
  }
  function pump() {
    var ctx = S.ctx; if (!ctx || !S.started || S.over) return;
    while (S.next < ctx.currentTime + 6) {
      var t = S.next, g = ctx.createGain(), src = ctx.createBufferSource(), n = 48, up = new Float32Array(n), dn = new Float32Array(n);
      src.buffer = S.bedBuf; src.connect(g); g.connect(S.bedBus);
      for (var i = 0; i < n; i++) { var p = i / (n - 1); up[i] = Math.sin(p * Math.PI / 2); dn[i] = Math.cos(p * Math.PI / 2); }
      var fin = S.first ? 2.0 : X; S.first = false;
      g.gain.setValueAtTime(0, t); g.gain.setValueCurveAtTime(up, t, fin); g.gain.setValueAtTime(1, t + fin);
      g.gain.setValueAtTime(1, t + W); g.gain.setValueCurveAtTime(dn, t + W, X);
      src.start(t); src.stop(t + W + X + 0.05); S.next += W;
    }
  }
  function kick() {
    if (!S.ready || S.started || !S.ctx || S.ctx.state !== 'running' || window.BNG_NOPRESHOW) return;
    S.started = true; S.next = S.ctx.currentTime + 0.1; S.first = true; pump(); S.timer = setInterval(pump, 500);
  }
  function resume() {
    var ctx = S.ctx; if (!ctx) return;
    if (ctx.state === 'running') { kick(); return; }
    try { var p = ctx.resume(); if (p && p.then) p.then(kick, function () { /* needs a gesture */ }); } catch (e) { /* ignore */ }
  }
  function init() {
    var AC = window.AudioContext || window.webkitAudioContext; if (!AC || S.ctx) return;
    try { S.ctx = new AC(); } catch (e) { return; }
    var ctx = S.ctx;
    S.master = ctx.createGain(); S.master.gain.value = S.muted ? 0 : 1; S.master.connect(ctx.destination);
    S.bedBus = ctx.createGain(); S.bedBus.gain.value = window.BNG_NOPRESHOW ? 0 : 1; S.bedBus.connect(S.master);
    S.sfxBus = ctx.createGain(); S.sfxBus.gain.value = SFX_GAIN; S.sfxBus.connect(S.master);
    ctx.onstatechange = function () { if (ctx.state === 'running') kick(); };
    Promise.all([decode('audio/bed.mp3'), decode('audio/sfx.mp3')]).then(function (b) { S.bedBuf = b[0]; S.sfxBuf = b[1]; S.ready = true; resume(); }, function () { /* no sound, the show still runs */ });
  }
  function mute() {
    S.muted = !S.muted; put(S.muted ? '1' : '0');
    if (S.master) S.master.gain.setTargetAtTime(S.muted ? 0 : 1, S.ctx.currentTime, 0.05);
    emit();
  }

  /* the start of the show (Khalid, 2026-11-17: "Sound should fade out with the space click"): the bed fades to silence from the key press
     and does not come back; the soft hit still lands on the beat */
  var FADE = 1.6;
  function onStart(spec) {
    var ctx = S.ctx; if (!ctx || !S.ready || !S.started) return;
    var now = ctx.currentTime, g = S.bedBus.gain;
    g.cancelScheduledValues(now); g.setValueAtTime(g.value, now); g.linearRampToValueAtTime(0, now + FADE);
    S.over = true; clearInterval(S.timer);
    var delay = Math.max(0, spec.boomAt - spec.sfxKey), offset = Math.max(0, spec.sfxKey - spec.boomAt);
    var s = ctx.createBufferSource(); s.buffer = S.sfxBuf; s.connect(S.sfxBus); s.start(now + 0.03 + delay, offset);
    S.log.push({ at: now, delay: delay, offset: offset });
  }
  /* the deck is silent: the bed stays at zero and no further loop is scheduled */
  function deck() {
    var ctx = S.ctx; if (!ctx || !S.bedBus) return;
    var now = ctx.currentTime, g = S.bedBus.gain;
    S.over = true; clearInterval(S.timer);
    g.cancelScheduledValues(now); g.setValueAtTime(Math.min(g.value, 0.0001), now); g.linearRampToValueAtTime(0, now + 0.2);
  }

  window.BNG_AUDIO = { get muted() { return S.muted; }, get state() { return S.ctx ? S.ctx.state : 'none'; }, get playing() { return S.started && S.ctx.state === 'running'; },
    toggle: mute, mute: mute, onStart: onStart, deck: deck, _S: S };

  var evs = ['pointerdown', 'pointermove', 'keydown', 'touchend', 'click'];
  function gesture() { resume(); if (S.ctx && S.ctx.state === 'running') evs.forEach(function (e) { window.removeEventListener(e, gesture, true); }); }
  evs.forEach(function (e) { window.addEventListener(e, gesture, true); });
  window.addEventListener('keydown', function (e) {
    if (e.code === 'KeyM' && !e.repeat && !e.ctrlKey && !e.metaKey && !e.altKey) mute();
  });
  init();
})();
