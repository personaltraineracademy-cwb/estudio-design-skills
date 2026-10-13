// Vector halftone: dot grid whose size follows a field (radial burst, linear fade, noise or a shape SDF).
// Print-like texture that stays vector. params: cell, field ('radial'|'linear'|'noise'|'ring'), shape ('dot'|'square'|'diamond')
import { circle, rect, ngon, P } from './lib.mjs';
export const meta = { w: 1080, h: 1080, params: {} };

export function draw({ rnd, noise, w, h, params, pal }) {
  const cell = params.cell ?? rnd.pick([18, 24, 30, 40]);
  const field = params.field ?? rnd.pick(['radial', 'linear', 'noise', 'ring']);
  const shape = params.shape ?? rnd.pick(['dot', 'dot', 'square', 'diamond']);
  const ang = rnd.range(0, Math.PI * 2), fx = rnd.range(0.2, 0.8) * w, fy = rnd.range(0.2, 0.8) * h;
  const out = [];
  for (let y = cell / 2; y < h; y += cell) for (let x = cell / 2; x < w; x += cell) {
    let v;
    if (field === 'radial') v = 1 - Math.hypot(x - fx, y - fy) / (0.75 * Math.hypot(w, h));
    else if (field === 'linear') v = ((x - w / 2) * Math.cos(ang) + (y - h / 2) * Math.sin(ang)) / w + 0.5;
    else if (field === 'ring') v = 1 - Math.abs(Math.hypot(x - w / 2, y - h / 2) - w * 0.3) / (w * 0.25);
    else v = 0.5 + 0.5 * noise(x * 0.004, y * 0.004);
    v = Math.max(0, Math.min(1, v));
    const r = (cell / 2) * v * 0.98;
    if (r < cell * 0.04) continue;
    const d = shape === 'square' ? rect(x - r, y - r, 2 * r, 2 * r) : shape === 'diamond' ? ngon(x, y, r * 1.2, 4, 0) : circle(x, y, r);
    out.push(d);
  }
  // one path per colour keeps files light
  return P(out.join(' '), rnd.chance(0.3) ? pal.accent : 'currentColor');
}
