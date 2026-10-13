// Flow-field ribbons (filled, tapered) — energy/motion graphics for key visuals, backgrounds, merch.
// params: count, len, width, scale (noise), accentShare, w, h
import { ribbon, P } from './lib.mjs';
export const meta = { w: 1080, h: 1350, params: {} };

export function draw({ rnd, noise, w, h, params, pal }) {
  const count = params.count ?? rnd.int(120, 260), len = params.len ?? rnd.int(90, 220);
  const width = (params.width ?? rnd.range(0.006, 0.02)) * w, scale = params.scale ?? rnd.range(0.0008, 0.0022);
  const bias = rnd.range(0, Math.PI * 2), turb = rnd.range(0.35, 1.1), acc = params.accentShare ?? 0.18;
  const out = [];
  for (let i = 0; i < count; i++) {
    let x = rnd.range(-0.1, 1.1) * w, y = rnd.range(-0.1, 1.1) * h;
    const pts = [[x, y]], step = w * 0.006;
    for (let s = 0; s < len; s++) {
      const a = bias + turb * Math.PI * noise(x * scale, y * scale);
      x += Math.cos(a) * step; y += Math.sin(a) * step; pts.push([x, y]);
    }
    // taper: thin ends via shorter ribbons stacked
    const wd = width * rnd.range(0.5, 1.6);
    out.push(P(ribbon(pts, wd), rnd.chance(acc) ? pal.accent : 'currentColor', ' opacity="0.9"'));
  }
  return out.join('');
}
