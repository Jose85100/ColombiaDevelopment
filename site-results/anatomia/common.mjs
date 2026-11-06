// Utilidades compartidas de las figuras isométricas (kit de Anatomy, MIT). Una figura = un módulo; el resultado va a out/<slug>.fragment.svg.
import { writeFileSync, mkdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import * as k from './kit/iso-kit.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
export const OUT = join(HERE, 'out');
mkdirSync(OUT, { recursive: true });
export const results = () => JSON.parse(readFileSync(join(HERE, '..', 'out', 'resultados.json'), 'utf-8'));
export { k };

export function scene({ W, H, plate, pts = [], azimuth = 42 }) {
  const PLATE_H = 12, FOOT_H = 5;
  const P = k.fitProjection([...k.boxCorners(plate, -PLATE_H - FOOT_H, 0), ...pts], W, H, { pad: 26, azimuth });
  const at = (p) => k.iso(p, P);
  const S = (paths, style) => k.solidSvg(paths, style), L = (d, style) => k.lineSvg(d, style), Dt = (p, style) => k.dotsSvg(p, style);
  const depth = (x, y, z = 0) => k.depthOf([x, y, z], P);
  const text = (x, y, z, str, o = {}) => k.faceTextSvg(k.topMatrix([x, y], z, P, o.along || 'x'), str, { size: o.size || 4, tone: o.tone || 'mid', anchor: o.anchor || 'middle' });
  const front = (x, y, z, str, o = {}) => k.faceTextSvg(k.sideMatrix([x, y], z, P, 'left'), str, { size: o.size || 3.4, tone: o.tone || 'mid', anchor: o.anchor || 'middle' });
  function base(strip_ = true) {
    const out = [`<path class="iso-halo" d="${k.haloOf(plate, -PLATE_H - FOOT_H, PLATE_H, P)}"/>`];
    for (const [x, y] of [...k.corners(plate, 24)].sort((a, b) => depth(a[0], a[1]) - depth(b[0], b[1]))) {
      out.push(S(k.cylinder(x, y, 7, -PLATE_H - FOOT_H, 1.6, P, 28), { tone: 'lo' }));
      out.push(S(k.cylinder(x, y, 5.4, -PLATE_H - FOOT_H + 1.6, FOOT_H - 1.6, P, 28), { tone: 'mid' }));
    }
    out.push(S(k.slabOf(plate, -PLATE_H, PLATE_H, P, 8, 1.6), { tone: 'mid' }));
    out.push(L(k.planOutline(k.insetPlan(plate, 5), 0, P), { tone: 'lo' }));
    const screws = k.corners(plate, 11);
    out.push(L(screws.map(([x, y]) => k.ring(x, y, 2.2, 0, P, 16)).join(''), { tone: 'lo' }));
    out.push(Dt(screws.map(([x, y]) => at([x, y, 0])), { size: 0.5 }));
    if (!strip_) return out.join('');
    const strip = { x: plate.x + 26, y: plate.y + plate.d - 17, w: plate.w - 80, d: 8, r: 1 };
    out.push(S(k.slabOf(strip, 0, 0.6, P, 3), { tone: 'lo', crease: 'none' }));
    const t = k.topTicks(strip.x + 4, strip.x + strip.w - 4, 4, 5, strip.y + 0.9, 0.6, [2, 3.8], P);
    out.push(L(t.minor, { tone: 'lo' }), L(t.major, { tone: 'mid' }));
    out.push(Dt([at([strip.x + 2, strip.y + 4, 0.6]), at([strip.x + strip.w - 2, strip.y + 4, 0.6])], { size: 0.45 }));
    return out.join('');
  }
  function emit(slug, label, body) {
    const fragment = k.figureSvg({ width: W, height: H, label, body });
    writeFileSync(join(OUT, slug + '.fragment.svg'), fragment);
    for (const t of ['dark', 'light']) {
      const svg = k.figureSvg({ width: W, height: H, label, body, standalone: t });
      writeFileSync(join(OUT, `${slug}-preview-${t}.html`), `<!doctype html><meta charset=utf-8><body style="margin:0;background:${t === 'dark' ? '#0b0b0b' : '#f2f2ef'}"><div style="width:900px">${svg}</div>`);
    }
    console.log('ok', slug, fragment.length, 'bytes');
  }
  return { k, P, at, S, L, Dt, depth, text, front, base, emit, W, H };
}
