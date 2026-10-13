// brand-studio generative helpers — pure JS, returns SVG strings (vector, logo-ready). No DOM, runs in Node.
// A sketch exports: export const meta = {w, h, params}; export function draw(ctx) { return '<path .../>' }
// ctx = { rnd, noise, w, h, params, pal, lib } — see run.mjs.

export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function makeRnd(seed) {
  const r = mulberry32(seed);
  const rnd = () => r();
  rnd.range = (a, b) => a + (b - a) * r();
  rnd.int = (a, b) => Math.floor(a + (b - a + 1) * r());
  rnd.pick = (arr) => arr[Math.floor(r() * arr.length)];
  rnd.chance = (p) => r() < p;
  rnd.gauss = () => { let u = 0, v = 0; while (!u) u = r(); while (!v) v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  rnd.shuffle = (arr) => { const a = arr.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  return rnd;
}

// 2D simplex noise (Gustavson), seeded
export function makeNoise(seed) {
  const r = mulberry32(seed ^ 0x9e3779b9);
  const p = new Uint8Array(512), perm = Array.from({ length: 256 }, (_, i) => i);
  for (let i = 255; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [perm[i], perm[j]] = [perm[j], perm[i]]; }
  for (let i = 0; i < 512; i++) p[i] = perm[i & 255];
  const g = [[1, 1], [-1, 1], [1, -1], [-1, -1], [1, 0], [-1, 0], [0, 1], [0, -1]];
  const F2 = 0.5 * (Math.sqrt(3) - 1), G2 = (3 - Math.sqrt(3)) / 6;
  return function (xin, yin) {
    const s = (xin + yin) * F2, i = Math.floor(xin + s), j = Math.floor(yin + s);
    const t = (i + j) * G2, x0 = xin - (i - t), y0 = yin - (j - t);
    const [i1, j1] = x0 > y0 ? [1, 0] : [0, 1];
    const x1 = x0 - i1 + G2, y1 = y0 - j1 + G2, x2 = x0 - 1 + 2 * G2, y2 = y0 - 1 + 2 * G2;
    const ii = i & 255, jj = j & 255;
    const c = (x, y, gi) => { let t0 = 0.5 - x * x - y * y; if (t0 < 0) return 0; t0 *= t0; const gg = g[gi & 7]; return t0 * t0 * (gg[0] * x + gg[1] * y); };
    return 70 * (c(x0, y0, p[ii + p[jj]]) + c(x1, y1, p[ii + i1 + p[jj + j1]]) + c(x2, y2, p[ii + 1 + p[jj + 1]]));
  };
}

// ---------------------------------------------------------------- geometry → path data
export const f = (n) => (Math.round(n * 100) / 100).toString();
export function poly(pts, close = true) { return 'M' + pts.map(([x, y]) => f(x) + ',' + f(y)).join(' L') + (close ? ' Z' : ''); }
export function circle(cx, cy, r) { return `M${f(cx - r)},${f(cy)} a${f(r)},${f(r)} 0 1,0 ${f(2 * r)},0 a${f(r)},${f(r)} 0 1,0 ${f(-2 * r)},0 Z`; }
export function rect(x, y, w, h, r = 0) {
  if (!r) return `M${f(x)},${f(y)} h${f(w)} v${f(h)} h${f(-w)} Z`;
  r = Math.min(r, w / 2, h / 2);
  return `M${f(x + r)},${f(y)} H${f(x + w - r)} A${f(r)},${f(r)} 0 0 1 ${f(x + w)},${f(y + r)} V${f(y + h - r)} A${f(r)},${f(r)} 0 0 1 ${f(x + w - r)},${f(y + h)} H${f(x + r)} A${f(r)},${f(r)} 0 0 1 ${f(x)},${f(y + h - r)} V${f(y + r)} A${f(r)},${f(r)} 0 0 1 ${f(x + r)},${f(y)} Z`;
}
export function ngon(cx, cy, r, n, rot = -Math.PI / 2) { return poly(Array.from({ length: n }, (_, i) => [cx + r * Math.cos(rot + (i * 2 * Math.PI) / n), cy + r * Math.sin(rot + (i * 2 * Math.PI) / n)])); }
export function star(cx, cy, R, r, n, rot = -Math.PI / 2) { return poly(Array.from({ length: 2 * n }, (_, i) => { const rr = i % 2 ? r : R; const a = rot + (i * Math.PI) / n; return [cx + rr * Math.cos(a), cy + rr * Math.sin(a)]; })); }
// arc band (annular sector) from a0→a1 (radians)
export function sector(cx, cy, r0, r1, a0, a1) {
  const p = (r, a) => [cx + r * Math.cos(a), cy + r * Math.sin(a)];
  const large = a1 - a0 > Math.PI ? 1 : 0;
  const [x0, y0] = p(r1, a0), [x1, y1] = p(r1, a1), [x2, y2] = p(r0, a1), [x3, y3] = p(r0, a0);
  if (r0 <= 0) return `M${f(cx)},${f(cy)} L${f(x0)},${f(y0)} A${f(r1)},${f(r1)} 0 ${large} 1 ${f(x1)},${f(y1)} Z`;
  return `M${f(x0)},${f(y0)} A${f(r1)},${f(r1)} 0 ${large} 1 ${f(x1)},${f(y1)} L${f(x2)},${f(y2)} A${f(r0)},${f(r0)} 0 ${large} 0 ${f(x3)},${f(y3)} Z`;
}
// superformula (Gielis) — organic ↔ geometric symbol outlines
export function superformula(cx, cy, scale, { m = 6, n1 = 1, n2 = 1, n3 = 1, a = 1, b = 1 } = {}, steps = 360) {
  const pts = [];
  for (let i = 0; i < steps; i++) {
    const t = (i / steps) * 2 * Math.PI;
    const r = Math.pow(Math.pow(Math.abs(Math.cos((m * t) / 4) / a), n2) + Math.pow(Math.abs(Math.sin((m * t) / 4) / b), n3), -1 / n1);
    pts.push([cx + scale * r * Math.cos(t), cy + scale * r * Math.sin(t)]);
  }
  return poly(pts);
}
// thick polyline → filled outline (round-ish joins by miter clamp) — keeps marks free of strokes
export function ribbon(pts, width) {
  const L = [], R = [], hw = width / 2;
  for (let i = 0; i < pts.length; i++) {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
    let dx = b[0] - a[0], dy = b[1] - a[1]; const d = Math.hypot(dx, dy) || 1; dx /= d; dy /= d;
    L.push([pts[i][0] - dy * hw, pts[i][1] + dx * hw]); R.push([pts[i][0] + dy * hw, pts[i][1] - dx * hw]);
  }
  return poly(L.concat(R.reverse()));
}
export const lerp = (a, b, t) => a + (b - a) * t;
export const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
export const TAU = Math.PI * 2;

// path element helpers
export const P = (d, fill = 'currentColor', extra = '') => `<path d="${d}" fill="${fill}"${extra}/>`;
export const EO = (d, fill = 'currentColor') => `<path d="${d}" fill="${fill}" fill-rule="evenodd"/>`;
