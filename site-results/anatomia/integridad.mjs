// Figura de /proyectos/integridad-publica: dos hileras de registro sobre una placa.
// Atrás, el registro original; adelante, el reescrito. Los dos encadenan bien por dentro,
// pero solo el original encaja con el pasador del punto de control externo.
// Uso: node integridad.mjs [--light] [--page]   Escribe out/integridad[.-light].svg  (y .html con --page para revisar).
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import * as k from './kit/iso-kit.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, 'out');
mkdirSync(OUT, { recursive: true });
const R = JSON.parse(readFileSync(join(HERE, '..', 'out', 'resultados.json'), 'utf-8')).integridad;
const D = R.digests.map((h) => h.slice(0, 6)), ROOT = R.root.slice(0, 6);
const V = R.verificaciones;                       // original, forged_self, forged_ext, truncated

const W = 640, H = 420;
const PLATE = { x: -184, y: -104, w: 360, d: 208, r: 9 }, PLATE_H = 12, FOOT_H = 5;
const ROWS = [{ y: -52, name: 'original', ok: V.original, shift: 0 }, { y: 52, name: 'reescrito', ok: V.forged_ext, shift: 14 }];
const BX = [74, -10, -94];                        // x de los tres bloques (la cadena corre hacia -x)
const BW = 58, BD = 44, BH = 18;
const ROOT_X = -154, ROOT_W = 36, ROOT_H = 28;    // bloque de la raíz
const POST_X = -170;                               // soporte del punto de control externo (al fondo)

const P = k.fitProjection([...k.boxCorners(PLATE, -PLATE_H - FOOT_H, 0), [POST_X, 0, 66], [-184, -104, 40]], W, H, { pad: 26, azimuth: 42 });
const at = (p) => k.iso(p, P);
const S = (paths, style) => k.solidSvg(paths, style), L = (d, style) => k.lineSvg(d, style), Dt = (pts, style) => k.dotsSvg(pts, style);
const depth = (x, y, z = 0) => k.depthOf([x, y, z], P);

function plate() {
  const out = [`<path class="iso-halo" d="${k.haloOf(PLATE, -PLATE_H - FOOT_H, PLATE_H, P)}"/>`];
  for (const [x, y] of [...k.corners(PLATE, 24)].sort((a, b) => depth(a[0], a[1]) - depth(b[0], b[1]))) {
    out.push(S(k.cylinder(x, y, 7, -PLATE_H - FOOT_H, 1.6, P, 28), { tone: 'lo' }));
    out.push(S(k.cylinder(x, y, 5.4, -PLATE_H - FOOT_H + 1.6, FOOT_H - 1.6, P, 28), { tone: 'mid' }));
  }
  out.push(S(k.slabOf(PLATE, -PLATE_H, PLATE_H, P, 8, 1.6), { tone: 'mid' }));
  out.push(L(k.planOutline(k.insetPlan(PLATE, 5), 0, P), { tone: 'lo' }));
  const screws = k.corners(PLATE, 11);
  out.push(L(screws.map(([x, y]) => k.ring(x, y, 2.2, 0, P, 16)).join(''), { tone: 'lo' }));
  out.push(Dt(screws.map(([x, y]) => at([x, y, 0])), { size: 0.5 }));
  const strip = { x: -150, y: PLATE.y + PLATE.d - 17, w: 270, d: 8, r: 1 };
  out.push(S(k.slabOf(strip, 0, 0.6, P, 3), { tone: 'lo', crease: 'none' }));
  const t = k.topTicks(strip.x + 4, strip.x + strip.w - 4, 4, 5, strip.y + 0.9, 0.6, [2, 3.8], P);
  out.push(L(t.minor, { tone: 'lo' }), L(t.major, { tone: 'mid' }));
  out.push(Dt([at([strip.x + 2, strip.y + 4, 0.6]), at([strip.x + strip.w - 2, strip.y + 4, 0.6])], { size: 0.45 }));
  return out.join('');
}

function rails(row) {
  const out = [];
  for (const dy of [-15, 12]) {
    out.push(S(k.slabOf({ x: -124, y: row.y + dy, w: 270, d: 5, r: 1 }, 0, 3, P, 3, 0.4), { tone: 'mid' }));
    out.push(Dt([-116, -30, 60, 132].map((x) => at([x, row.y + dy + 2.5, 3])), { size: 0.4 }));
  }
  for (const x of [-130, 140]) {
    out.push(S(k.slabOf({ x, y: row.y - 20, w: 6, d: 44, r: 1.2 }, 0, 8, P, 3, 0.5), { tone: 'mid' }));
    out.push(Dt([at([x + 3, row.y - 14, 8]), at([x + 3, row.y + 14, 8])], { size: 0.45 }));
  }
  return out.join('');
}

function block(row, i) {
  const x = BX[i], plan = { x, y: row.y - BD / 2, w: BW, d: BD, r: 3 };
  const out = [S(k.slabOf(plan, 3, BH, P, 5, 0.7), { tone: 'hi', crease: 'lo' })];
  out.push(L(k.planOutline(k.insetPlan(plan, 3), 3 + BH, P, 3), { tone: 'faint' }));
  out.push(Dt([[x + 5, row.y - BD / 2 + 5], [x + BW - 5, row.y - BD / 2 + 5], [x + 5, row.y + BD / 2 - 5], [x + BW - 5, row.y + BD / 2 - 5]].map(([a, b]) => at([a, b, 3 + BH])), { size: 0.42 }));
  const label = { x: x + 8, y: row.y - 11, w: BW - 16, d: 22, r: 1.5 };
  out.push(S(k.slabOf(label, 3 + BH, 0.8, P, 3), { tone: 'lo', crease: 'none' }));
  out.push(L(k.lineOnTop([label.x + 3, label.y + 6], [label.x + label.w - 3, label.y + 6], 3 + BH + 0.8, P), { tone: 'faint' }));
  out.push(k.faceTextSvg(k.topMatrix([x + BW / 2, row.y + 4], 3 + BH + 0.8, P, 'x'), row.name === 'original' ? (i === 0 ? '#000000' : '#' + D[i - 1]) : 'recalculado', { size: row.name === 'original' ? 5.2 : 3.6, tone: 'hi', anchor: 'middle' }));
  out.push(k.faceTextSvg(k.topMatrix([x + BW / 2, row.y - 5], 3 + BH + 0.8, P, 'x'), i === 0 ? 'inicio' : `evento ${i - 1}`, { size: 3.4, tone: 'mid', anchor: 'middle' }));
  return out.join('');
}

function bar(row, i) {            // eslabón entre bloque i y el siguiente (o la raíz)
  const hi = BX[i] + 8, lo = i < 2 ? BX[i + 1] + BW - 8 : ROOT_X + ROOT_W - 8 + (i === 2 ? row.shift : 0);
  const x0 = lo, x1 = hi;
  const plan = { x: x0, y: row.y - 7, w: x1 - x0, d: 14, r: 2 };
  const z = 3 + BH;
  return [S(k.slabOf(plan, z, 4, P, 3, 0.5), { tone: 'mid' }),
    Dt([at([x0 + 4, row.y, z + 4]), at([x1 - 4, row.y, z + 4])], { size: 0.5 }),
    L(k.lineOnTop([x0 + 7, row.y], [x1 - 7, row.y], z + 4, P), { tone: 'lo' })].join('');
}

function rootBlock(row) {
  const RX = ROOT_X + row.shift, cx = RX + ROOT_W / 2, top = 3 + ROOT_H;
  const plan = { x: RX, y: row.y - 18, w: ROOT_W, d: 36, r: 4 };
  const out = [S(k.slabOf(plan, 3, ROOT_H, P, 5, 0.8), { tone: 'hi', crease: 'lo' })];
  out.push(L(k.planOutline(k.insetPlan(plan, 3), top, P, 4), { tone: 'faint' }));
  out.push(Dt([[RX + 5, row.y - 13], [RX + ROOT_W - 5, row.y - 13], [RX + 5, row.y + 13], [RX + ROOT_W - 5, row.y + 13]].map(([a, b]) => at([a, b, top])), { size: 0.42 }));
  out.push(L(k.ring(cx, row.y, 6.5, top, P, 28), { tone: 'mid' }));       // boca del orificio
  out.push(L(k.ring(cx, row.y, 4.2, top, P, 24), { tone: 'hi' }));
  out.push(L(k.ring(cx, row.y, 4.2, top - 8, P, 24), { tone: 'lo' }));     // fondo
  out.push(k.faceTextSvg(k.topMatrix([RX + 13, row.y + 13], top, P, 'x'), row.name === 'original' ? '#' + ROOT : 'distinta', { size: 3.2, tone: 'mid', anchor: 'middle' }));
  out.push(k.faceTextSvg(k.topMatrix([RX + 13, row.y - 11], top, P, 'x'), 'raíz', { size: 3.2, tone: 'mid', anchor: 'middle' }));
  return out.join('');
}

const SOCKET_X = ROOT_X + ROOT_W / 2;              // posición fija del émbolo externo
const ARM_Z = 56;
function postBody() {              // soporte externo al fondo de la placa
  const out = [];
  const base = { x: POST_X - 14, y: -88, w: 22, d: 176, r: 3 };
  out.push(S(k.slabOf(base, 0, 8, P, 5, 0.8), { tone: 'mid' }));
  out.push(Dt([[POST_X - 8, -82], [POST_X + 4, -82], [POST_X - 8, 82], [POST_X + 4, 82]].map(([a, b]) => at([a, b, 8])), { size: 0.45 }));
  const body = { x: POST_X - 8, y: -80, w: 10, d: 160, r: 2 };
  out.push(S(k.slabOf(body, 8, ARM_Z - 8, P, 4, 0.6), { tone: 'mid' }));
  out.push(L(k.planOutline(k.insetPlan(body, 2), ARM_Z, P, 3), { tone: 'faint' }));
  out.push(k.faceTextSvg(k.topMatrix([POST_X - 3, 0], ARM_Z, P, 'y'), 'punto de control externo', { size: 4.2, tone: 'mid', anchor: 'middle' }));
  return out.join('');
}
function probe(row) {              // brazo y émbolo: baja hasta el fondo solo si el orificio está donde se espera
  const out = [];
  const arm = { x: POST_X + 2, y: row.y - 4, w: SOCKET_X - POST_X - 2 + 6, d: 8, r: 2 };
  out.push(S(k.slabOf(arm, ARM_Z - 6, 6, P, 3, 0.5), { tone: 'mid' }));
  out.push(Dt([at([arm.x + 5, row.y, ARM_Z]), at([arm.x + arm.w - 5, row.y, ARM_Z])], { size: 0.45 }));
  const tip = row.ok ? 3 + ROOT_H - 8 + 1 : 3 + ROOT_H;       // entra al fondo, o apoya sobre la tapa
  out.push(S(k.cylinder(SOCKET_X, row.y, 2.8, tip, ARM_Z - 6 - tip, P, 20), { tone: 'hi', lit: row.ok, crease: 'none' }));
  out.push(S(k.cylinder(SOCKET_X, row.y, 4, ARM_Z, 3, P, 24), { tone: 'mid' }));
  out.push(L(k.knurl(SOCKET_X, row.y, 4, ARM_Z, ARM_Z + 3, 20, P), { tone: 'lo' }));
  return out.join('');
}

// Orden de pintado: de atrás hacia delante por profundidad.
const items = [];
for (const row of ROWS) {
  items.push({ d: depth(0, row.y, 0) - 1000, svg: rails(row) });
  [0, 1, 2].forEach((i) => items.push({ d: depth(BX[i] + BW / 2, row.y, 0), svg: block(row, i) }));
  items.push({ d: depth(ROOT_X + row.shift + 10, row.y, 0), svg: rootBlock(row) });
  [0, 1, 2].forEach((i) => items.push({ d: depth(BX[i], row.y, 21) + 0.5, svg: bar(row, i) }));
}
items.sort((a, b) => a.d - b.d);

const label = 'Dos hileras de registro sobre una placa. En la de atrás, el registro original: tres piezas encadenadas que terminan en la raíz. En la de adelante, el registro reescrito, que también encadena bien por dentro. A la derecha, un soporte externo con un pasador por hilera: el émbolo del original baja hasta el fondo de su orificio y el del reescrito apoya sobre la tapa sin entrar.';
const probes = ROWS.map((r) => ({ d: depth(SOCKET_X, r.y, ARM_Z), svg: probe(r) })).sort((a, b) => a.d - b.d).map((x) => x.svg);
const svgBody = [plate(), postBody(), ...items.map((x) => x.svg), ...probes];
const dark = k.figureSvg({ width: W, height: H, label, body: svgBody, standalone: 'dark' });
const light = k.figureSvg({ width: W, height: H, label, body: svgBody, standalone: 'light' });
const fragment = k.figureSvg({ width: W, height: H, label, body: svgBody });
writeFileSync(join(OUT, 'integridad.fragment.svg'), fragment);
writeFileSync(join(OUT, 'integridad-preview-dark.html'), `<!doctype html><meta charset=utf-8><body style="margin:0;background:#0b0b0b"><div style="width:900px">${dark}</div>`);
writeFileSync(join(OUT, 'integridad-preview-light.html'), `<!doctype html><meta charset=utf-8><body style="margin:0;background:#f2f2ef"><div style="width:900px">${light}</div>`);
console.log('ok', items.length, 'items');
