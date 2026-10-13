// Concentric ring segments with gaps — kinetic emblems, timers, "energy" marks, motion-friendly (rotate rings).
// params: rings (2..6), segs (1..4 per ring), thickness, gapDeg, core ('dot'|'none'|'ngon')
import { sector, circle, ngon, P, TAU } from './lib.mjs';
export const meta = { w: 1000, h: 1000, params: {} };

export function draw({ rnd, w, params, pal }) {
  const c = w / 2, R = w * 0.42, rings = params.rings ?? rnd.int(2, 5);
  const th = (params.thickness ?? rnd.range(0.35, 0.7)) * (R / rings);
  const gapR = (R / rings) - th;
  const out = [];
  for (let k = 0; k < rings; k++) {
    const r1 = R - k * (th + gapR), r0 = r1 - th;
    if (r0 < w * 0.05) break;
    const segs = params.segs ?? rnd.int(1, 3), gap = ((params.gapDeg ?? rnd.range(8, 40)) * Math.PI) / 180;
    const start = rnd.range(0, TAU), span = rnd.range(0.55, 0.92) * TAU;
    for (let s = 0; s < segs; s++) {
      const a0 = start + (s * span) / segs, a1 = start + ((s + 1) * span) / segs - gap;
      if (a1 > a0) out.push(P(sector(c, c, r0, r1, a0, a1), k === 0 && s === 0 && rnd.chance(0.5) ? pal.accent : 'currentColor'));
    }
  }
  const core = params.core ?? rnd.pick(['dot', 'none', 'ngon']);
  const rc = R / rings * 0.6;
  if (core === 'dot') out.push(P(circle(c, c, rc), pal.accent));
  if (core === 'ngon') out.push(P(ngon(c, c, rc * 1.2, rnd.pick([3, 4, 6])), pal.accent));
  return out.join('');
}
