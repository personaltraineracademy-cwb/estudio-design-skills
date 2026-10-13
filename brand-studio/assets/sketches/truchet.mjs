// Modular tile marks: N×N grid of quarter-circles, triangles, half-rounds — with symmetry so it reads as a logo,
// not noise. Good for monograms (a letter emerges), app icons and patterns.
// params: n (2..4), symmetry ('none'|'mirror'|'rot4'|'mirrorxy'), gapRatio, roundCorners
import { rect, P, f } from './lib.mjs';
export const meta = { w: 1000, h: 1000, params: {} };

const TILES = ['full', 'quarter', 'quarter', 'tri', 'half', 'empty', 'arc'];

function tile(type, x, y, s, rot) {
  // define in unit square, rotate by rot*90 around centre
  const c = (px, py) => {
    const ux = px - 0.5, uy = py - 0.5; let rx = ux, ry = uy;
    for (let k = 0; k < rot; k++) [rx, ry] = [-ry, rx];
    return [x + (rx + 0.5) * s, y + (ry + 0.5) * s];
  };
  const L = (pts) => 'M' + pts.map((p) => c(...p).map(f).join(',')).join(' L') + ' Z';
  switch (type) {
    case 'full': return L([[0, 0], [1, 0], [1, 1], [0, 1]]);
    case 'tri': return L([[0, 0], [1, 0], [0, 1]]);
    case 'half': { // half-disc on the bottom edge
      const pts = []; for (let i = 0; i <= 24; i++) { const a = Math.PI + (i / 24) * Math.PI; pts.push([0.5 + 0.5 * Math.cos(a), 1 + 0.5 * Math.sin(a)]); }
      return L(pts);
    }
    case 'quarter': { // quarter disc anchored at corner (0,1)
      const pts = [[0, 1]]; for (let i = 0; i <= 24; i++) { const a = -Math.PI / 2 + (i / 24) * (Math.PI / 2); pts.push([Math.cos(a), 1 + Math.sin(a)]); }
      return L(pts);
    }
    case 'arc': { // quarter ring
      const pts = []; for (let i = 0; i <= 24; i++) { const a = -Math.PI / 2 + (i / 24) * (Math.PI / 2); pts.push([Math.cos(a), 1 + Math.sin(a)]); }
      for (let i = 24; i >= 0; i--) { const a = -Math.PI / 2 + (i / 24) * (Math.PI / 2); pts.push([0.5 * Math.cos(a), 1 + 0.5 * Math.sin(a)]); }
      return L(pts);
    }
    default: return '';
  }
}

export function draw({ rnd, w, params, pal }) {
  const n = params.n ?? rnd.int(2, 4), sym = params.symmetry ?? rnd.pick(['mirror', 'rot4', 'mirrorxy', 'none']);
  const M = w * 0.12, S = (w - 2 * M) / n, g = S * (params.gapRatio ?? rnd.pick([0, 0, 0.06, 0.1]));
  const grid = [];
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) grid.push({ t: rnd.pick(TILES), r: rnd.int(0, 3) });
  const at = (i, j) => grid[j * n + i];
  // symmetry: derive mirrored tiles (rotation index mapping for quarter-based tiles)
  const mirrorR = [1, 0, 3, 2], flipR = [3, 2, 1, 0];
  const cells = [];
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    let { t, r } = at(i, j);
    if ((sym === 'mirror' || sym === 'mirrorxy') && i >= Math.ceil(n / 2)) { ({ t, r } = at(n - 1 - i, j)); r = mirrorR[r]; }
    if (sym === 'mirrorxy' && j >= Math.ceil(n / 2)) { const src = (i >= Math.ceil(n / 2)) ? at(n - 1 - i, n - 1 - j) : at(i, n - 1 - j); t = src.t; r = flipR[(i >= Math.ceil(n / 2)) ? mirrorR[src.r] : src.r]; }
    if (sym === 'rot4') { const h = Math.ceil(n / 2); let ii = i, jj = j, k = 0; while (!(ii < h && jj < h) && k < 4) { [ii, jj] = [jj, n - 1 - ii]; k++; } const src = at(ii, jj); t = src.t; r = (src.r + (4 - k)) % 4; }
    cells.push(tile(t, M + i * S + g / 2, M + j * S + g / 2, S - g, r));
  }
  // one compound path per colour: adjacent tiles fuse without anti-aliasing seams
  const accentAt = rnd.chance(0.3) ? rnd.int(0, cells.length - 1) : -1;
  const ink = cells.filter((d, k) => d && k !== accentAt).join(' ');
  return P(ink) + (accentAt >= 0 && cells[accentAt] ? P(cells[accentAt], pal.accent) : '');
}
