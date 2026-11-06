// Figura de /proyectos/fraude-identidad: un banco con seis correderas (las señales) y un reloj (la probabilidad de fraude).
// La posición de cada carro es el valor de la señal en el ejemplo; el reloj marca p = 75 % (zona de revisión).
// El carro fantasma del grafo y la aguja tenue muestran el contrafactual: con grafo = 0,2 la probabilidad baja a 55 %.
import { scene, results } from './common.mjs';
const F = results().fraude;
const SEN = F.senales, TH = F.umbrales, p1 = F.example.p, p2 = F.example.after;
const pct = (v) => Math.round(v * 100) + ' %';
const NOMBRE = ['identidad', 'dispositivo', 'velocidad', 'comportamiento', 'documento', 'grafo'];
const PLATE = { x: -192, y: -104, w: 332, d: 216, r: 9 };
const c = scene({ W: 640, H: 410, plate: PLATE, pts: [[60, 0, 40]] });
const { k, P, at, S, L, Dt, depth, text } = c;

// --- banco de señales ---
const BANK = { x: -178, y: -72, w: 150, d: 144, r: 4 }, RX0 = -118, RLEN = 84, RY = [-55, -33, -11, 11, 33, 55];
function bank() {
  const out = [S(k.slabOf(BANK, 0, 6, P, 5, 0.8), { tone: 'mid' })];
  out.push(L(k.planOutline(k.insetPlan(BANK, 4), 6, P, 4), { tone: 'faint' }));
  RY.forEach((y, i) => {
    out.push(S(k.slabOf({ x: RX0, y: y - 2.5, w: RLEN, d: 5, r: 1 }, 6, 2.4, P, 2, 0.3), { tone: 'lo' }));
    const t = k.topTicks(RX0, RX0 + RLEN, 8.4, 2, y + 3.4, 8.4, [1.4, 2.6], P);
    out.push(L(t.minor, { tone: 'lo' }), L(t.major, { tone: 'mid' }));
    out.push(text(RX0 - 5, y + 1.2, 6, `${NOMBRE[i]} · ${String(SEN[i].valor).replace('.', ',')}`, { size: 3.3, tone: i === 5 ? 'hi' : 'mid', anchor: 'end' }));
    const v = SEN[i].valor, x = RX0 + v * RLEN;
    if (i === 5) {                                           // posición contrafactual: grafo = 0,2
      const gx = RX0 + 0.2 * RLEN;
      out.push(L(k.planOutline({ x: gx - 5, y: y - 6.5, w: 10, d: 13, r: 1.5 }, 8.4, P, 2), { tone: 'mid' }));
    }
    out.push(S(k.slabOf({ x: x - 5, y: y - 6.5, w: 10, d: 13, r: 1.5 }, 8.4, 6, P, 2, 0.4), { tone: 'hi', lit: i === 5, crease: 'lo' }));
    out.push(S(k.cylinder(x, y, 2.6, 14.4, 3.4, P, 20), { tone: 'mid' }));
    out.push(L(k.knurl(x, y, 2.6, 14.4, 17.8, 18, P), { tone: 'lo' }));
  });
  out.push(text(BANK.x + BANK.w / 2, BANK.y + BANK.d + 9, 0, 'señales de la solicitud (0 a 1)', { size: 4.4, tone: 'hi' }));
  return out.join('');
}
// --- ducto ---
const duct = () => S(k.slabOf({ x: -30, y: -9, w: 52, d: 18, r: 3 }, 0, 4, P, 3, 0.5), { tone: 'lo' }) +
  L(k.lineOnTop([-24, 0], [16, 0], 4, P), { tone: 'faint' });

// --- reloj ---
const CX = 68, CY = 0, R = 31, CON = { x: CX - 55, y: CY - 55, w: 110, d: 110, r: 6 }, CONH = 16, TOP = CONH + 1.2;
const ang = (p) => (-135 + 270 * p) * Math.PI / 180;
const pt = (p, r) => [CX + Math.sin(ang(p)) * r, CY - Math.cos(ang(p)) * r];
function dial() {
  const out = [S(k.slabOf(CON, 0, CONH, P, 6, 1), { tone: 'mid' })];
  out.push(L(k.planOutline(k.insetPlan(CON, 3), CONH, P, 5), { tone: 'faint' }));
  out.push(S(k.cylinder(CX, CY, R, CONH, 1.2, P, 72, 0.6), { tone: 'hi', crease: 'lo' }));
  out.push(L(k.ring(CX, CY, R - 2, TOP, P, 72), { tone: 'lo' }));
  const tk = { lo: [], mid: [], hi: [] };
  for (let i = 0; i <= 50; i++) {
    const p = i / 50, major = i % 5 === 0, zone = p < TH.verificar ? 'lo' : p < TH.revisar ? 'mid' : 'hi';
    tk[major ? (zone === 'lo' ? 'mid' : 'hi') : 'lo'].push(k.lineOnTop(pt(p, R - 3), pt(p, R - (major ? 8 : 6)), TOP, P));
  }
  out.push(L(tk.lo.join(''), { tone: 'lo' }), L(tk.mid.join(''), { tone: 'mid' }), L(tk.hi.join(''), { tone: 'hi' }));
  // umbrales: marcas largas
  for (const th of [TH.verificar, TH.revisar]) out.push(L(k.lineOnTop(pt(th, R - 3), pt(th, R - 13), TOP, P), { tone: 'hi' }));
  out.push(text(...pt(0.1, R + 11), TOP, 'permitir', { size: 3, tone: 'mid' }));
  out.push(text(...pt(0.5, R + 11), TOP, 'verificar', { size: 3, tone: 'mid' }));
  out.push(text(...pt(0.9, R + 11), TOP, 'revisar', { size: 3, tone: 'hi' }));
  // aguja tenue (contrafactual) y aguja del caso
  out.push(L(k.lineOnTop(pt(p2, 4), pt(p2, R - 9), TOP + 0.1, P), { tone: 'mid' }));
  out.push(L(k.lineOnTop([CX - Math.sin(ang(p1)) * 5, CY + Math.cos(ang(p1)) * 5], pt(p1, R - 5), TOP + 0.2, P), { tone: 'lit' }));
  out.push(S(k.cylinder(CX, CY, 2.6, TOP, 1.6, P, 20), { tone: 'mid' }));
  out.push(text(CX, CY + 17, TOP, pct(p1), { size: 7.2, tone: 'hi' }));
  out.push(text(CX, CON.y + CON.d + 8, 0, `probabilidad de fraude · con grafo = 0,2: ${pct(p2)}`, { size: 4.2, tone: 'hi' }));
  return out.join('');
}
const body = [c.base(false), bank(), duct(), dial()];
const label = `Un banco con seis correderas, una por señal de la solicitud (identidad, dispositivo, velocidad, comportamiento, documento y grafo de relaciones), conectado a un reloj que marca la probabilidad de fraude. En el ejemplo la aguja marca ${pct(p1)}, en la zona de revisión. Un marcador tenue muestra la corredera del grafo en 0,2 y una aguja tenue la probabilidad resultante, ${pct(p2)}, en la zona de verificación adicional.`;
c.emit('fraude-identidad', label, body);
