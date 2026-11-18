/* Geometry of the BNG OS signs and wordmark. Every path below is copied verbatim from
   brand-kit/svg/family/sign-*-96-light.svg and brand-kit/svg/wordmark-full-light.svg (built by brand/logo_build.py).
   Nothing is redrawn or re-proportioned: parts are only moved, rotated, scaled and faded. */
(function () {
  const G = {};

  /* The one dot rule: dot radius on the 96 grid; wordmark core radius 13.95 (= 16.629 x 0.8385). */
  G.DOT_R = 16.629;

  /* 96-grid signs. `dot` is the dot's centre in the sign's own coordinates. */
  G.SIGN = {
    os: {
      top: 'M0.47 41.32A48 48 0 0 1 95.53 41.32H77.25A30 30 0 0 0 18.75 41.32Z',
      bot: 'M0.47 54.68A48 48 0 0 0 95.53 54.68H77.25A30 30 0 0 1 18.75 54.68Z',
      dot: [48, 48]
    },
    cortex: {
      d: 'M12 0H72V18H30V49.39H12Z',
      /* the same corner as two overlapping bars (concept C only; the union is the corner) */
      barH: 'M12 0H72V18H12Z',
      barV: 'M12 0H30V49.39H12Z',
      dot: [28.63, 79.37]
    },
    studio: {
      d: 'M0 0L49.39 0L49.39 18L18 18L18 78L78 78L78 46.61L96 46.61L96 96L0 96Z',
      /* centre line of the frame, from the top bar's end round to the right bar's end: used as a draw-on mask */
      centre: 'M49.39 9H9V87H87V46.61',
      /* the same frame as four overlapping bars (concept C only; the union is the frame) */
      barTop: 'M0 0H49.39V18H0Z',
      barLeft: 'M0 0H18V96H0Z',
      barBottom: 'M0 78H96V96H0Z',
      barRight: 'M78 46.61H96V96H78Z',
      dot: [79.37, 16.63]
    }
  };

  /* A unit circle: the dot is always drawn as this path scaled by (DOT_R x sign scale). */
  G.UNIT_DOT = 'M-1 0A1 1 0 1 0 1 0A1 1 0 1 0 -1 0Z';

  /* Wordmark, viewBox 34.5 17.67 415.33 81.25. Its sub-paths are separate parts; `pv` is a pivot inside each part. */
  G.WM_VB = [34.5, 17.67, 415.33, 81.25];
  G.WM = {
    B1: { d: 'M34.5 18.7H49.8V96.5H34.5Z', pv: [42.15, 57.6] },
    B2: { d: 'M60.9 18.7H68.3A23.95 23.95 0 0 1 68.3 66.6H60.9V49.6H70.4A7.3 7.3 0 0 0 70.4 35H60.9Z', pv: [76.6, 42.65] },
    B3: { d: 'M60.9 96.5H69.4A23 23 0 0 0 91.3 66.6L77.8 72.04V75.6A5 5 0 0 1 72.8 80.6H60.9Z', pv: [76.5, 81.5] },
    N1: { d: 'M103.5 18.7L155.9 65.07V18.7H171.2V96.5H169.6L103.5 38Z', pv: [137.35, 57.6] },
    N2: { d: 'M103.5 53L118.7 66.45V96.5H103.5Z', pv: [111.1, 74.75] },
    G: { d: 'M251.55 29.15A40.6 40.6 0 1 0 259.39 76.9H240.52A25.35 25.35 0 1 1 240.8 39.9ZM224.3 50.8H263.3V66.2H224.3Z', pv: [222.95, 58.2] },
    OT: { d: 'M302.14 52.6A40.25 40.25 0 0 1 381.86 52.6H366.52A25.15 25.15 0 0 0 317.48 52.6Z', pv: [342, 58.2] },
    OB: { d: 'M302.14 63.8A40.25 40.25 0 0 0 381.86 63.8H366.52A25.15 25.15 0 0 1 317.48 63.8Z', pv: [342, 58.2] },
    S: { d: 'M449.75 18.7H417.03A23.275 23.275 0 0 0 417.03 65.25H426.47A7.975 7.975 0 0 1 426.47 81.2H409.05L393.75 96.5H426.47A23.275 23.275 0 0 0 426.47 49.95H417.03A7.975 7.975 0 0 1 417.03 34H434.45Z', pv: [421.75, 57.6] }
  };
  G.CORE = { c: [342, 58.2], r: 13.95 };

  /* Opener A, measured on the Figma screenshot of 318:3774 (1440 x 900): wordmark 1.5 px per unit,
     core centre (869.5, 400.5), line in Instrument Sans centred on x 720. */
  G.OPENER = { left: 408.1, top: 340.0, k: 1.5, lineX: 720, lineY: 548, lineSize: 30, lineWeight: 500, text: 'One system above the tools BNG already has.' };

  /* screen position of a point of the wordmark (wordmark units) in the opener */
  G.wmPos = function (x, y) {
    const o = G.OPENER;
    return [o.left + (x - G.WM_VB[0]) * o.k, o.top + (y - G.WM_VB[1]) * o.k];
  };
  G.O_CENTRE = G.wmPos(342, 58.2);          /* where the ring and its dot end up */
  G.O_SIGN_SCALE = 40.25 * 1.5 / 48;        /* the OS sign's ring is the wordmark O: 48 grid units = 40.25 wordmark units */

  window.PS_G = G;
})();
