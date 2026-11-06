// Figura de /proyectos/agroindustria: dos estaciones, una por caso. Un pilar mide el ingreso del año 1 y una pila de bloques los costos.
// Una regla sobre el pilar marca el nivel del ingreso: si la pila la sobrepasa, el año pierde dinero; si queda debajo, el hueco es el margen.
import { scene, results } from './common.mjs';
const Y1 = results().agro.year1;
const U = 1 / 80;                                  // 1 unidad de dibujo = 80 millones de COP
const fm = (v) => Math.round(v).toLocaleString('es-CO');
const PLATE = { x: -168, y: -108, w: 286, d: 216, r: 9 };
const c = scene({ W: 640, H: 420, plate: PLATE, pts: [[-100, -60, 112], [60, 60, 112]] });
const { k, P, at, S, L, Dt, depth, text, front } = c;

const PX0 = -96, PW = 44, PD = 44;                   // pilar de ingresos
const CX0 = -6, CW = 44, CD = 44;                    // pila de costos
const STAGES = [
  { y: -62, dx: 40, nombre: 'ejercicio inicial', d: Y1.inicial },
  { y: 62, dx: -40, nombre: 'caso rediseñado', d: Y1.diseno },
];
const ORDER = [['fijos', 'fijos'], ['nomina', 'nómina'], ['campo', 'campo'], ['variables', 'variables']];

function station(st) {
  const d = st.d, y0 = st.y - PD / 2, rev = d.ingresos * U, PX = PX0 + st.dx, CX = CX0 + st.dx;
  const cost = ORDER.reduce((a, [key]) => a + d[key], 0), top = cost * U;
  const out = [];
  // pilar de ingresos
  const pil = { x: PX, y: y0, w: PW, d: PD, r: 3 };
  out.push(S(k.slabOf(pil, 0, rev, P, 4, 0.8), { tone: 'hi', crease: 'lo' }));
  out.push(L(k.planOutline(k.insetPlan(pil, 3), rev, P, 3), { tone: 'faint' }));
  out.push(text(PX + 16, st.y + 3, rev, 'ingresos', { size: 3.4, tone: 'mid' }));
  out.push(text(PX + 16, st.y - 4, rev, fm(d.ingresos), { size: 4.6, tone: 'hi' }));
  out.push(front(PX + PW / 2, y0 + PD, rev - 9, 'ingresos del año 1', { size: 3.1 }));
  // pila de costos
  const stack = [];
  let z = 0;
  for (const [key, name] of ORDER) {
    const h = d[key] * U, plan = { x: CX, y: y0, w: CW, d: CD, r: 2 };
    stack.push(S(k.slabOf(plan, z, h, P, 3, 0.5), { tone: key === 'nomina' ? 'hi' : 'mid', lit: key === 'nomina', crease: 'lo' }));
    if (h > 9) stack.push(front(CX + CW / 2, y0 + CD, z + h - 4, `${name} ${fm(d[key])}`, { size: 3.1, tone: key === 'nomina' ? 'hi' : 'mid' }));
    z += h;
  }
  stack.push(text(CX + CW / 2, st.y + 3, top, 'costos', { size: 3.4, tone: 'mid' }));
  stack.push(text(CX + CW / 2, st.y - 4, top, fm(cost), { size: 4.6, tone: 'hi' }));
  // regla de nivel sobre el pilar
  const over = top < rev;                           // la pila queda debajo: la regla pasa por encima y se ve el margen
  const barEnd = over ? CX + CW - 4 : CX;
  const bar = { x: PX + PW - 12, y: st.y - 5, w: barEnd - (PX + PW - 12), d: 10, r: 1.5 };
  const barSvg = [S(k.slabOf(bar, rev, 3, P, 3, 0.5), { tone: 'mid', lit: true }),
    L(k.lineOnTop([bar.x + 5, st.y], [bar.x + bar.w - 4, st.y], rev + 3, P), { tone: 'lo' }),
    Dt([at([bar.x + 3, st.y - 2.5, rev + 3]), at([bar.x + bar.w - 3, st.y - 2.5, rev + 3])], { size: 0.42 })].join('');
  const flag = text(PX + PW / 2, y0 + PD + 10, 0, st.nombre, { size: 5.2, tone: 'hi' });
  const res = text(PX + PW / 2, y0 + PD + 19, 0, over ? `margen del año 1: +${fm(d.ingresos - cost)}` : `faltan ${fm(cost - d.ingresos)} en el año 1`, { size: 3.8, tone: 'mid' });
  const pieces = over ? [out.join(''), ...stack, barSvg] : [out.join(''), barSvg, ...stack];
  return pieces.join('') + flag + res;
}

const body = [c.base(false), ...[...STAGES].sort((a, b) => depth(0, a.y) - depth(0, b.y)).map(station)];
const label = `Dos estaciones sobre una placa, una por caso. En cada una, un pilar mide el ingreso del primer año y una pila de cuatro bloques (fijos, nómina, campo y variables) los costos. En el ejercicio inicial la pila sobrepasa la regla de nivel del ingreso por ${fm(Y1.inicial.fijos + Y1.inicial.nomina + Y1.inicial.campo + Y1.inicial.variables - Y1.inicial.ingresos)} millones; en el caso rediseñado queda por debajo y el hueco es el margen.`;
c.emit('agroindustria', label, body);
