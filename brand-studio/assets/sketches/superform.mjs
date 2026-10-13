// Superformula symbols — from crisp geometric stars to organic petals/blobs; optional inner cut-out and orbit dot.
// params: m, n1, n2, n3 (Gielis), hole (0..0.6), layers (1..3)
import { superformula, circle, P, EO } from './lib.mjs';
export const meta = { w: 1000, h: 1000, params: {} };

export function draw({ rnd, w, params, pal }) {
  const c = w / 2;
  const m = params.m ?? rnd.pick([3, 4, 5, 6, 8]);
  const n1 = params.n1 ?? rnd.pick([0.3, 0.6, 1, 2, 4, 8]);
  const n2 = params.n2 ?? rnd.pick([0.5, 1, 1.7, 3]);
  const n3 = params.n3 ?? n2;
  // normalise scale so the shape fills ~80 % of the canvas
  const probe = superformula(0, 0, 1, { m, n1, n2, n3 }, 720).match(/-?[\d.]+/g).map(Number);
  let maxR = 0; for (let i = 0; i < probe.length; i += 2) maxR = Math.max(maxR, Math.hypot(probe[i], probe[i + 1]));
  const k = (w * 0.4) / (maxR || 1);
  const outer = superformula(c, c, k, { m, n1, n2, n3 }, 720);
  const hole = params.hole ?? rnd.pick([0, 0, 0.25, 0.4]);
  const layers = params.layers ?? (rnd.chance(0.25) ? 2 : 1);
  const out = [];
  if (hole) out.push(EO(outer + ' ' + superformula(c, c, k * hole, { m, n1: n1 * 1.2, n2, n3 }, 720)));
  else out.push(P(outer));
  if (layers > 1) out.push(P(superformula(c, c, k * 0.42, { m: m * 2, n1: 1, n2: 1, n3: 1 }, 720), pal.accent));
  if (rnd.chance(0.3)) out.push(P(circle(c + k * maxR * 0.95, c - k * maxR * 0.4, w * 0.04), pal.accent));
  return out.join('');
}
