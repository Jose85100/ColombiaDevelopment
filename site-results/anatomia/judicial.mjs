// Figura de /proyectos/riesgo-judicial: ilustración del método propuesto, sin cifras (no hay resultados todavía).
// Una cinta lleva documentos por cinco estaciones; la barrera final no se levanta sin la llave de revisión humana.
import { scene } from './common.mjs';
const PLATE = { x: -176, y: -78, w: 352, d: 156, r: 9 };
const c = scene({ W: 640, H: 330, plate: PLATE, pts: [[0, 0, 44]] });
const { k, P, at, S, L, Dt, depth, text } = c;
const BELT = { x: -166, y: -13, w: 322, d: 26, r: 3 }, BZ = 5;
const ST = [{ x: -126, n: 'fuentes' }, { x: -62, n: 'procedencia' }, { x: 2, n: 'normalización' }, { x: 64, n: 'entidades y grafo' }, { x: 118, n: 'revisión humana' }];

function belt() {
  const out = [S(k.slabOf(BELT, 0, BZ, P, 5, 0.8), { tone: 'mid' })];
  for (let x = -158; x < 150; x += 10) out.push(L(k.lineOnTop([x, -11], [x, 11], BZ, P), { tone: 'faint' }));
  for (const y of [-13.6, 13.6]) out.push(S(k.slabOf({ x: BELT.x, y: y - 1, w: BELT.w, d: 2, r: 0.6 }, 0, BZ + 2.2, P, 2, 0.3), { tone: 'lo', crease: 'none' }));
  return out.join('');
}
const sheet = (x, y, z = BZ, w = 15, d = 19, lit = false) => S(k.slabOf({ x, y, w, d, r: 1 }, z, 0.9, P, 2, 0.2), { tone: 'hi', lit, crease: 'none' }) +
  L(k.lineOnTop([x + 2.5, y + 5], [x + w - 2.5, y + 5], z + 0.9, P), { tone: 'faint' }) + L(k.lineOnTop([x + 2.5, y + 9], [x + w - 4, y + 9], z + 0.9, P), { tone: 'faint' }) + L(k.lineOnTop([x + 2.5, y + 13], [x + w - 6, y + 13], z + 0.9, P), { tone: 'faint' });
function portal(cx, beamZ, depthX = 14) {
  const out = [];
  for (const y of [-20, 20]) {
    out.push(S(k.slabOf({ x: cx - 7, y: y - 5, w: 14, d: 10, r: 2 }, 0, 3, P, 2, 0.4), { tone: 'lo' }));
    out.push(S(k.cylinder(cx, y, 2.6, 3, beamZ - 3, P, 20), { tone: 'mid', crease: 'none' }));
  }
  return { posts: out.join(''), beam: S(k.slabOf({ x: cx - depthX / 2, y: -23, w: depthX, d: 46, r: 2 }, beamZ, 5, P, 3, 0.5), { tone: 'mid' }) };
}
const lamp = (x, y, z, lit) => S(k.cylinder(x, y, 3.2, z, 5, P, 24), { tone: 'hi', lit }) + L(k.ring(x, y, 1.6, z + 5, P, 14), { tone: 'lo' });

function fuentes() {                                         // bandeja con pila de documentos
  const cx = ST[0].x, out = [S(k.slabOf({ x: cx - 17, y: -30, w: 34, d: 60, r: 3 }, 0, 4, P, 4, 0.6), { tone: 'mid' })];
  out.push(L(k.planOutline(k.insetPlan({ x: cx - 17, y: -30, w: 34, d: 60, r: 3 }, 3), 4, P, 3), { tone: 'faint' }));
  for (let i = 0; i < 7; i++) out.push(sheet(cx - 8 + (i % 2) * 1.2, -9.5 + (i % 3) * 0.8, 4 + i * 1.1, 16, 19, i === 6));
  return out.join('');
}
function procedencia() {                                     // sello de origen
  const cx = ST[1].x, g = portal(cx, 24), out = [g.posts, g.beam];
  out.push(S(k.cylinder(cx, 0, 4.2, 12, 12, P, 24), { tone: 'hi', lit: true }));
  out.push(S(k.cylinder(cx, 0, 2.2, 24, 6, P, 20), { tone: 'mid' }));
  out.push(L(k.knurl(cx, 0, 4.2, 12, 24, 22, P), { tone: 'lo' }));
  return out.join('');
}
function normalizacion() {                                   // criba con huecos regulares
  const cx = ST[2].x, g = portal(cx, 26, 8), out = [g.posts, g.beam];
  const plate = { x: cx - 11, y: -17, w: 22, d: 34, r: 2 };
  out.push(S(k.slabOf(plate, 13, 2.4, P, 3, 0.4), { tone: 'hi' }));
  const rings = [];
  for (const dx of [-5, 5]) for (const dy of [-11, -4, 3.5, 11]) rings.push(k.ring(cx + dx, dy, 2, 15.4, P, 14));
  out.push(L(rings.join(''), { tone: 'mid' }));
  out.push(Dt([[cx - 8, -14], [cx + 8, -14], [cx - 8, 14], [cx + 8, 14]].map(([a, b]) => at([a, b, 15.4])), { size: 0.42 }));
  for (const y of [-12, 12]) out.push(S(k.slabOf({ x: cx - 1.5, y: y - 1.5, w: 3, d: 3, r: 0.5 }, 15.4, 10.6, P, 2, 0.2), { tone: 'mid', crease: 'none' }));
  return out.join('');
}
function entidades() {                                       // peine de clavijas: cada clavija encuentra su registro
  const cx = ST[3].x, g = portal(cx, 28, 10), out = [g.posts, g.beam];
  for (let i = 0; i < 7; i++) {
    const y = -15 + i * 5;
    out.push(S(k.cylinder(cx, y, 1.2, 12, 16, P, 12), { tone: i === 3 ? 'hi' : 'mid', lit: i === 3, crease: 'none' }));
  }
  out.push(L(k.lineOnTop([cx - 4, -17], [cx - 4, 17], 33, P), { tone: 'lo' }));
  return out.join('');
}
function revision() {                                        // barrera abajo, lámpara apagada y llave en el pupitre
  const cx = ST[4].x, out = [];
  for (const y of [-19, 19]) out.push(S(k.slabOf({ x: cx - 4, y: y - 4, w: 8, d: 8, r: 1.5 }, 0, 24, P, 3, 0.4), { tone: 'mid' }));
  out.push(S(k.slabOf({ x: cx - 2.5, y: -20, w: 5, d: 40, r: 1.2 }, 8, 5, P, 3, 0.4), { tone: 'hi', crease: 'lo' }));   // barrera baja
  for (let y = -17; y <= 17; y += 8) out.push(L(k.lineOnTop([cx - 2.5, y], [cx + 2.5, y + 4], 13, P), { tone: 'lo' }));
  out.push(lamp(cx, 19, 24, false));
  const desk = { x: cx - 10, y: 28, w: 20, d: 18, r: 2 };
  out.push(S(k.slabOf(desk, 0, 12, P, 3, 0.5), { tone: 'mid' }));
  out.push(S(k.cylinder(cx, 37, 4, 12, 3, P, 24), { tone: 'hi', lit: true }));
  out.push(L(k.lineOnTop([cx - 3, 37], [cx + 3, 37], 15, P), { tone: 'lo' }));
  return out.join('');
}
function bandeja() {                                         // salida: vacía, no hay resultados todavía
  const x = 138, out = [S(k.slabOf({ x, y: -17, w: 22, d: 34, r: 2.5 }, 0, 3, P, 3, 0.5), { tone: 'mid' })];
  out.push(L(k.planOutline(k.insetPlan({ x, y: -17, w: 22, d: 34, r: 2.5 }, 3), 3, P, 2), { tone: 'faint' }));
  out.push(text(x + 11, 0, 3, 'reporte', { size: 3, tone: 'lo' }));
  return out.join('');
}
const labels = ST.map((s, i) => text(s.x, i === 4 ? 54 : 27, 0, s.n, { size: 4.4, tone: 'hi' })).join('') + text(0, -66, 0, 'método propuesto · revisión humana obligatoria', { size: 4.6, tone: 'hi' });
const order = [
  belt(), fuentes(), sheet(-98, -9.5), procedencia(), sheet(-34, -9.5), normalizacion(), sheet(30, -9.5), entidades(), sheet(88, -9.5), revision(), bandeja(), labels,
];
const label = 'Una cinta transportadora lleva documentos por cinco estaciones: fuentes autorizadas, procedencia, normalización, resolución de entidades con grafo, y revisión humana. La barrera de la última estación está abajo y la lámpara apagada: nada pasa al reporte sin la llave de revisión humana. La bandeja de salida espera los reportes que el método producirá.';
c.emit('riesgo-judicial', label, [c.base(false), ...order]);
