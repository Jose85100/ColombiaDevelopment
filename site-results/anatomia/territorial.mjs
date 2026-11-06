// Figura de /proyectos/desarrollo-territorial: tres vagones con carga proporcional a las toneladas anuales de cada escenario.
// Junto a cada vagón, un poste con casquete marca la carga de equilibrio del caso base: el VPN es positivo si la carga lo sobrepasa.
import { scene, results } from './common.mjs';
const T = results().territorial;
const fm = (v) => Math.round(v).toLocaleString('es-CO');
const sg = (v) => (v > 0 ? '+' : v < 0 ? '−' : '') + fm(Math.abs(v));
const ESC = ['Pesimista', 'Base', 'Optimista'], XS = [-92, 0, 92];
const U = 1 / 20, DECK = 11, BE = T.tons_breakeven;
const PLATE = { x: -160, y: -68, w: 320, d: 148, r: 9 };
const c = scene({ W: 640, H: 340, plate: PLATE, pts: [[0, 0, 80]] });
const { k, P, at, S, L, Dt, depth, text } = c;

function track() {
  const out = [];
  for (let x = -146; x <= 146; x += 12) out.push(S(k.slabOf({ x, y: -14, w: 4, d: 28, r: 0.6 }, 0, 2.6, P, 2, 0.3), { tone: 'lo', crease: 'none' }));
  for (const y of [-9.5, 5.5]) out.push(S(k.slabOf({ x: -150, y, w: 300, d: 4, r: 0.8 }, 2.6, 2.4, P, 2, 0.3), { tone: 'mid', crease: 'none' }));
  out.push(S(k.slabOf({ x: -156, y: -16, w: 6, d: 32, r: 1.4 }, 0, 12, P, 3, 0.5), { tone: 'mid' }));      // tope de fin de vía
  out.push(S(k.slabOf({ x: 150, y: -16, w: 6, d: 32, r: 1.4 }, 0, 12, P, 3, 0.5), { tone: 'mid' }));
  return out.join('');
}
function wagon(i) {
  const cx = XS[i], tons = T.toneladas[ESC[i]], h = tons * U, out = [];
  for (const bx of [-17, 17]) out.push(S(k.slabOf({ x: cx + bx - 8, y: -14, w: 16, d: 28, r: 2 }, 4, 5, P, 3, 0.5), { tone: 'lo' }));
  out.push(S(k.slabOf({ x: cx - 28, y: -14, w: 56, d: 28, r: 2 }, 9, 2, P, 3, 0.5), { tone: 'mid' }));
  for (const sx of [-30, 28]) out.push(S(k.slabOf({ x: cx + sx, y: -3, w: 4, d: 6, r: 1 }, 9, 2, P, 2, 0.3), { tone: 'lo', crease: 'none' }));   // enganche
  out.push(Dt([[cx - 24, -11], [cx + 24, -11], [cx - 24, 11], [cx + 24, 11]].map(([a, b]) => at([a, b, 11])), { size: 0.42 }));
  const load = { x: cx - 22, y: -11, w: 44, d: 22, r: 2 };
  out.push(S(k.slabOf(load, DECK, h, P, 3, 0.6), { tone: 'hi', crease: 'lo', lit: i === 1 }));
  for (const sx of [-12, 12]) out.push(L(k.lineOnTop([cx + sx, -11], [cx + sx, 11], DECK + h, P), { tone: 'lo' }));
  out.push(L(k.planOutline(k.insetPlan(load, 3), DECK + h, P, 2), { tone: 'faint' }));
  out.push(text(cx, 0, DECK + h, fm(tons), { size: 5.4, tone: 'hi' }));
  out.push(text(cx, 7.5, DECK + h, 'mil t al año', { size: 2.8, tone: 'mid' }));
  return out.join('');
}
function gauge(i) {                                        // poste a la misma altura de base que la carga: su tope es la carga de equilibrio
  const gx = XS[i] + 25, gy = -25, top = DECK + BE * U, out = [];   // misma profundidad en pantalla que el centro del vagón: las alturas se comparan directo
  out.push(S(k.slabOf({ x: gx - 5, y: gy - 5, w: 10, d: 10, r: 1.5 }, 0, DECK, P, 3, 0.4), { tone: 'lo' }));
  out.push(S(k.cylinder(gx, gy, 1.8, DECK, top - DECK, P, 16), { tone: 'mid', crease: 'none' }));
  out.push(S(k.cylinder(gx, gy, 3.6, top, 2.6, P, 24), { tone: 'hi', lit: true }));
  out.push(L(k.ring(gx, gy, 1.6, top + 2.6, P, 14), { tone: 'lo' }));
  return out.join('');
}
function labels() {
  const out = [];
  ESC.forEach((n, i) => {
    out.push(text(XS[i], 52, 0, n.toLowerCase(), { size: 5.6, tone: 'hi' }));
    out.push(text(XS[i], 61, 0, `VPN ${sg(T.rail_npv[n])}`, { size: 4.6, tone: T.rail_npv[n] > 0 ? 'hi' : 'mid' }));
  });
  out.push(text(-150, 72, 0, `poste = equilibrio del caso base: ${fm(BE)} mil t al año`, { size: 3.8, tone: 'hi', anchor: 'start' }));
  return out.join('');
}
const body = [c.base(false), track(), ...[0, 1, 2].map((i) => wagon(i) + gauge(i)), labels()];
const label = `Un tramo de vía con tres vagones, uno por escenario, cargados en proporción a sus toneladas anuales: pesimista ${T.toneladas.Pesimista}, base ${T.toneladas.Base} y optimista ${T.toneladas.Optimista} mil. Junto a cada vagón un poste marca la carga de equilibrio del caso base, ${fm(BE)} mil toneladas: la del escenario pesimista queda por debajo y su VPN es ${sg(T.rail_npv.Pesimista)}; las otras dos lo sobrepasan, con VPN ${sg(T.rail_npv.Base)} y ${sg(T.rail_npv.Optimista)}.`;
c.emit('desarrollo-territorial', label, body);
