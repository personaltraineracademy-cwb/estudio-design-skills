// Solid convex shape split by constant-width cuts from an apex — the "hexagon with lines" family, explored.
// params: sides (3..8 | 0=circle), cuts (2..6), gap (fraction), apex ('center'|'vertex'|'edge'|'random'),
//         drop (remove one wedge for negative space), accentWedge (colour one wedge)
import { poly, P, TAU } from './lib.mjs';
export const meta = { w: 1000, h: 1000, params: {} };

function clip(pts, px, py, nx, ny) {           // keep side where (p - P)·n >= 0 (Sutherland–Hodgman)
  const out = [], inside = ([x, y]) => (x - px) * nx + (y - py) * ny >= 0;
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i], b = pts[(i + 1) % pts.length], ia = inside(a), ib = inside(b);
    if (ia) out.push(a);
    if (ia !== ib) {
      const da = (a[0] - px) * nx + (a[1] - py) * ny, db = (b[0] - px) * nx + (b[1] - py) * ny, t = da / (da - db);
      out.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]);
    }
  }
  return out;
}

export function draw({ rnd, w, h, params, pal }) {
  const cx = w / 2, cy = h / 2, R = w * 0.4;
  const sides = params.sides ?? rnd.pick([0, 4, 5, 6, 6, 8]);
  const n = sides || 64, rot = sides === 4 ? -Math.PI / 4 : -Math.PI / 2;
  const base = Array.from({ length: n }, (_, i) => [cx + R * Math.cos(rot + (i * TAU) / n), cy + R * Math.sin(rot + (i * TAU) / n)]);
  const cuts = params.cuts ?? rnd.int(2, 5), gap = (params.gap ?? rnd.range(0.025, 0.06)) * w;
  const apexMode = params.apex ?? rnd.pick(['center', 'vertex', 'edge', 'random']);
  let ax = cx, ay = cy;
  if (apexMode === 'vertex') [ax, ay] = base[0];
  if (apexMode === 'edge') { const i = rnd.int(0, n - 1), j = (i + 1) % n; ax = (base[i][0] + base[j][0]) / 2; ay = (base[i][1] + base[j][1]) / 2; }
  if (apexMode === 'random') { ax = cx + rnd.range(-0.4, 0.4) * R; ay = cy + rnd.range(-0.4, 0.4) * R; }
  // cut angles: even (+jitter) around the apex, or a fan when the apex sits on the boundary
  const onEdge = apexMode === 'vertex' || apexMode === 'edge';
  const toC = Math.atan2(cy - ay, cx - ax);
  let angles;
  if (onEdge) {
    const spread = rnd.range(0.7, 1.2);
    angles = Array.from({ length: cuts }, (_, i) => toC - spread / 2 + (spread * i) / Math.max(1, cuts - 1));
  } else {
    const off = rnd.range(0, TAU), jitter = params.jitter ?? rnd.range(0, 0.25);
    angles = Array.from({ length: cuts }, (_, i) => off + (i * TAU) / cuts + rnd.range(-jitter, jitter)).sort((a, b) => a - b);
  }
  // wedges between consecutive cut rays (full turn when apex inside)
  const wedges = [];
  const rays = onEdge ? [toC - Math.PI / 2 - 0.01, ...angles, toC + Math.PI / 2 + 0.01] : [...angles, angles[0] + TAU];
  for (let i = 0; i < rays.length - 1; i++) {
    const a0 = rays[i], a1 = rays[i + 1];
    let poly0 = base.slice();
    // left of ray a0 (offset gap/2) and right of ray a1 (offset gap/2)
    const n0 = [-Math.sin(a0), Math.cos(a0)], n1 = [Math.sin(a1), -Math.cos(a1)];
    const g0 = onEdge && i === 0 ? 0 : gap / 2, g1 = onEdge && i === rays.length - 2 ? 0 : gap / 2;
    poly0 = clip(poly0, ax + n0[0] * g0, ay + n0[1] * g0, n0[0], n0[1]);
    if (a1 - a0 < Math.PI) poly0 = clip(poly0, ax + n1[0] * g1, ay + n1[1] * g1, n1[0], n1[1]);
    else { // reflex wedge: split in two halves
      const am = (a0 + a1) / 2, nm = [Math.sin(am), -Math.cos(am)], nm2 = [-Math.sin(am), Math.cos(am)];
      const A = clip(poly0, ax, ay, nm[0], nm[1]);
      const B = clip(clip(base.slice(), ax, ay, nm2[0], nm2[1]), ax + n1[0] * g1, ay + n1[1] * g1, n1[0], n1[1]);
      if (A.length > 2) wedges.push(A); poly0 = B;
    }
    if (poly0.length > 2) wedges.push(poly0);
  }
  const drop = params.drop ?? ((wedges.length >= 4 && rnd.chance(0.3)) ? rnd.int(0, wedges.length - 1) : -1);
  const acc = params.accentWedge ?? (rnd.chance(0.35) ? rnd.int(0, wedges.length - 1) : -1);
  return wedges.map((p, i) => (i === drop ? '' : P(poly(p), i === acc ? pal.accent : 'currentColor'))).join('');
}
