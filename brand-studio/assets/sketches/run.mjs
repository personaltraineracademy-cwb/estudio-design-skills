// node run.mjs <sketch.mjs> <outDir> <seedFrom> <seedTo> '<json params>'
// Writes <outDir>/<name>-<seed>.svg for each seed. Palette via params.pal = {bg, fg, accent, ...}.
import { pathToFileURL } from 'node:url';
import fs from 'node:fs';
import path from 'node:path';
import * as lib from './lib.mjs';

const [, , sketchPath, outDir, s0, s1, json] = process.argv;
const mod = await import(pathToFileURL(path.resolve(sketchPath)).href);
const params = Object.assign({}, mod.meta?.params || {}, json ? JSON.parse(json) : {});
const pal = Object.assign({ bg: '#1A1A1A', fg: '#F5F5F5', accent: '#F8C100' }, params.pal || {});
const w = params.w || mod.meta?.w || 1000, h = params.h || mod.meta?.h || 1000;
const name = path.basename(sketchPath).replace(/\.m?js$/, '');
fs.mkdirSync(outDir, { recursive: true });
for (let seed = +s0; seed <= +s1; seed++) {
  const ctx = { rnd: lib.makeRnd(seed), noise: lib.makeNoise(seed), w, h, params, pal, lib, seed };
  const body = mod.draw(ctx);
  const bg = params.transparent ? '' : `<rect width="${w}" height="${h}" fill="${pal.bg}"/>`;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" color="${pal.fg}">${bg}${body}</svg>\n`;
  fs.writeFileSync(path.join(outDir, `${name}-${seed}.svg`), svg);
}
console.log(`${+s1 - +s0 + 1} SVG → ${outDir}`);
