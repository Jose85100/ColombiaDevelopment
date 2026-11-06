#!/usr/bin/env python3
"""Calcula con el código de los programas los resultados que muestra colombiarisk.com/proyectos y genera sus páginas.

    python3 site-results/build_results.py <carpeta sitio-principal del sitio>

Escribe en el sitio: proyectos/<slug>/index.html (una por propuesta), proyectos/figuras/resultados.css y
las cifras de las tarjetas de proyectos/index.html. También deja site-results/out/resultados.json con todos los números.
Todo es un ejercicio con parámetros sintéticos; ninguna cifra es una proyección real de un proyecto.
"""
import csv, json, os, random, re, subprocess, sys
from dataclasses import replace
from html import escape as esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for prog in ('01-territorial-development', '02-fraud-identity', '04-agroindustry-farmer-ownership', '05-public-integrity'):
    sys.path.insert(0, os.path.join(ROOT, 'programs', prog, 'python'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from colombia_dev.rail import RailScenario, evaluate as rail_eval            # noqa: E402
from colombia_dev.projections import project, ProjectionConfig, quantile      # noqa: E402
from colombia_dev.fraud import Signals, score, counterfactual                  # noqa: E402
from colombia_dev.agro_finance import Project, evaluate as agro_eval          # noqa: E402
from colombia_dev.agro_equity import Ownership, equity_after_round            # noqa: E402
from colombia_dev.integrity import build_log, checkpoint, verify              # noqa: E402
import charts                                                                   # noqa: E402
from charts import Plot, hbars, boxes, flow, fmt_es as f_                     # noqa: E402

SITE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else None
COMMIT = subprocess.run(['git', '-C', ROOT, 'log', '-1', '--format=%h', '--', 'programs'], capture_output=True, text=True).stdout.strip()
GH = 'https://github.com/Jose85100/ColombiaDevelopment'
R = {}  # todos los resultados


def bisect(f, lo, hi, n=80):
    for _ in range(n):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if f(m) < 0 else (lo, m)
    return hi


def fm(v, d=0):
    return f_(v, d)


def sgn(v, d=0):
    return ('+' if v > 0 else '−' if v < 0 else '') + f_(abs(v), d)


# ======================= 01 · DESARROLLO TERRITORIAL =======================
base = RailScenario(annual_tons=850, passengers=450, freight_rate_per_ton=.55, fare_per_passenger=.15, operating_cost=290, capex=2800, discount_rate=.10, horizon=25, annual_growth=.025)
esc_rail = {'Pesimista': RailScenario(**{**base.__dict__, 'annual_growth': 0, 'annual_tons': 550}), 'Base': base,
            'Optimista': RailScenario(**{**base.__dict__, 'annual_growth': .05, 'annual_tons': 1200})}
rail = {k: rail_eval(v) for k, v in esc_rail.items()}
cum = {k: [sum(r['cashflows'][:i + 1]) for i in range(len(r['cashflows']))] for k, r in rail.items()}
payback = {k: next((i for i, c in enumerate(v) if c >= 0), None) for k, v in cum.items()}
tons_be = bisect(lambda x: rail_eval(replace(base, annual_tons=x))['npv'], 10, 5000)
cf_esc = [-base.capex] + [(1 + base.annual_growth) ** (t - 1) * (base.annual_tons * base.freight_rate_per_ton + base.passengers * base.fare_per_passenger - base.operating_cost) for t in range(1, 26)]
npv_opex_grows = sum(c / 1.1 ** t for t, c in enumerate(cf_esc))
ton_pts = [700, 800, 850, 900, 1000]
npv_ton = [rail_eval(replace(base, annual_tons=t))['npv'] for t in ton_pts]
year1 = base.annual_tons * base.freight_rate_per_ton + base.passengers * base.fare_per_passenger
mc = project(ProjectionConfig())
R['territorial'] = dict(rail_npv={k: v['npv'] for k, v in rail.items()}, payback_year=payback, tons_breakeven=tons_be, npv_if_opex_grows=npv_opex_grows,
                        year1_revenue=year1, mc_year10={k: mc[-1][k] for k in ('p05', 'p50', 'p95', 'mean')})

# ======================= 02 · FRAUDE =======================
rng = random.Random(2026)
REQ, LOSS = 1200, 750000
prevs = {'Controlado': .005, 'Base': .015, 'Estrés': .04}
sims = {k: [sum(rng.random() < p for _ in range(REQ)) * LOSS for _ in range(600)] for k, p in prevs.items()}
fraud = {k: dict(expected=REQ * p * LOSS, q=[quantile(v, q) for q in (.05, .25, .5, .75, .95)], mean=sum(v) / len(v)) for (k, p), v in zip(prevs.items(), sims.values())}
sig = Signals(.6, .5, .7, .4, .5, .8)
sc0 = score(sig)
cf = counterfactual(sig, 'graph', .2)
p_zero = score(Signals(0, 0, 0, 0, 0, 0))['fraud_probability']
WEIGHTS = (('Identidad', 1.35, sig.identity), ('Dispositivo', 1.15, sig.device), ('Velocidad', 1.10, sig.velocity), ('Comportamiento', .75, sig.behavioral), ('Documento', 1.25, sig.document), ('Grafo de relaciones', 1.55, sig.graph))
R['fraude'] = dict(scenarios=fraud, example=dict(p=sc0['fraud_probability'], action=sc0['action'], after=cf['after']['fraud_probability'], after_action=cf['after']['action']), p_all_zero=p_zero)

# ======================= 04 · AGROINDUSTRIA =======================
ap = Project()
a0 = agro_eval(ap)
price_be = bisect(lambda x: agro_eval(replace(ap, sale_price_mcop_ton=x))['npv_mcop'], .1, 50)
yield_be = bisect(lambda x: agro_eval(replace(ap, yield_ton_ha=x))['npv_mcop'], .1, 200)
ha_be = bisect(lambda x: agro_eval(replace(ap, hectares=x))['npv_mcop'], 1, 5000)
price_ebitda0 = bisect(lambda x: agro_eval(replace(ap, sale_price_mcop_ton=x))['year1']['ebitda_mcop'], .1, 50)
a_ha = agro_eval(replace(ap, hectares=ha_be))
payroll_share = a0['annual_staff_cost_mcop'] / a0['year1']['revenue_mcop']
cases = {'Caso base': ap, 'Precio −20 %': replace(ap, sale_price_mcop_ton=ap.sale_price_mcop_ton * .8), 'Rendimiento −25 %': replace(ap, yield_ton_ha=ap.yield_ton_ha * .75),
         'CAPEX +35 %': replace(ap, capex_mcop=ap.capex_mcop * 1.35), 'Precio +35 %': replace(ap, sale_price_mcop_ton=ap.sale_price_mcop_ton * 1.35)}
agro_cases = {k: agro_eval(v)['npv_mcop'] for k, v in cases.items()}
prices = [1.5 + .25 * i for i in range(19)]
agro_price = [agro_eval(replace(ap, sale_price_mcop_ton=x))['npv_mcop'] for x in prices]
own = Ownership()
rounds = [0, 10, 25, 50, 100]
dil = [equity_after_round(own, 100, n)['farmers'] * 100 for n in rounds]
with open(os.path.join(ROOT, 'programs/04-agroindustry-farmer-ownership/data/department_opportunities.csv'), newline='', encoding='utf-8') as fh:
    deptos = list(csv.DictReader(fh))
R['agro'] = dict(npv_base=a0['npv_mcop'], ebitda_year1=a0['year1']['ebitda_mcop'], revenue_year1=a0['year1']['revenue_mcop'], payroll=a0['annual_staff_cost_mcop'], payroll_share=payroll_share,
                 price_breakeven=price_be, yield_breakeven=yield_be, hectares_breakeven=ha_be, water_at_breakeven=a_ha['annual_water_m3'], water_cap=ap.max_water_m3_year, water_base=a0['annual_water_m3'],
                 cases=agro_cases, dilution=dict(zip(rounds, dil)), departamentos=len(deptos))

# ======================= 05 · INTEGRIDAD =======================
pl = [{"contract": "SYNTHETIC-RAIL-001", "milestone": "M1", "action": "registered"}, {"contract": "SYNTHETIC-RAIL-001", "milestone": "M1", "action": "verified"}]
orig = build_log(pl)
trusted = checkpoint(orig)
forged = build_log([dict(pl[0], action="paid"), pl[1]])
ver = dict(original=verify(orig, trusted), forged_self=verify(forged, checkpoint(forged)), forged_ext=verify(forged, trusted), truncated=verify(orig[:-1], trusted))
R['integridad'] = dict(verificaciones=ver, digests=[e['digest'] for e in orig], root=trusted['root'])
with open(os.path.join(ROOT, 'programs/05-public-integrity/README.md'), encoding='utf-8') as fh:
    readme = fh.read()
componentes = [[c.strip() for c in ln.strip().strip('|').split('|')] for ln in readme.splitlines() if ln.startswith('| ') and not ln.startswith('| Proyecto') and not ln.startswith('|---')]
componentes = [c for c in componentes if len(c) == 3]

os.makedirs(os.path.join(ROOT, 'site-results', 'out'), exist_ok=True)
R['_meta'] = dict(commit_programas=COMMIT, semilla=2026, nota='Ejercicio con parámetros sintéticos; no son proyecciones reales.')
json.dump(R, open(os.path.join(ROOT, 'site-results', 'out', 'resultados.json'), 'w'), ensure_ascii=False, indent=1, default=float)

# ======================= HTML =======================
FIGN = [0]


def uid():
    FIGN[0] += 1
    return f'f{FIGN[0]}'


def table(headers, rows, cls=''):
    h = ''.join(f'<th scope="col">{esc(str(x))}</th>' for x in headers)
    b = ''.join('<tr>' + ''.join(f'<td>{esc(str(c))}</td>' for c in r) + '</tr>' for r in rows)
    return f'<div class="rs-tabla"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def figure(svg, title, note, headers, rows):
    u = uid()
    svg = svg.replace('aria-labelledby="t d"', f'aria-labelledby="{u}-t {u}-d"').replace('id="t"', f'id="{u}-t"').replace('id="d"', f'id="{u}-d"')
    return (f'<figure class="rs-fig"><figcaption class="rs-title">{esc(title)}</figcaption>{svg}<p class="rs-note">{note}</p>'
            f'<details class="rs-data"><summary>Ver los valores del gráfico</summary>{table(headers, rows)}</details></figure>')


def cifras(items):
    return '<ul class="rs-cifras">' + ''.join(f'<li><strong>{esc(a)}</strong><span>{b}</span></li>' for a, b in items) + '</ul>'


def limites(items):
    return '<ul class="rs-limites">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'


def seccion(titulo, cuerpo, id=''):
    return f'<section class="rs-sec"{f" id={chr(34)}{id}{chr(34)}" if id else ""}><h2>{esc(titulo)}</h2>{cuerpo}</section>'


def aviso():
    return (f'<p class="rs-aviso"><strong>Ejercicio con datos sintéticos.</strong> Los números de esta página salen del código público de la propuesta, '
            f'con parámetros inventados para probar el método. No describen un proyecto real ni son una proyección ni una oferta. '
            f'Calculado con el código del repositorio (commit <code>{esc(COMMIT)}</code>, semilla 2026).</p>')


def cierre(slug, prog, nombre):
    return (f'<section class="rs-sec rs-cierre"><h2>Código y reproducción</h2><p>Todo lo que ves se calcula con el código del programa. '
            f'Puedes revisarlo y repetir las cuentas.</p><p class="rs-acciones"><a class="enlace" href="{GH}/tree/main/programs/{prog}" target="_blank" rel="noopener noreferrer">Código en GitHub ↗<span class="visually-hidden"> de {esc(nombre)} (abre en una pestaña nueva)</span></a>'
            f' <a class="enlace" href="/proyectos/">← Volver a Proyectos</a> <a class="enlace" href="mailto:contacto@colombiarisk.com?subject=Proponer%20una%20necesidad">Proponer una necesidad →</a></p></section>')


def page(slug, titulo, dek, cuerpo):
    s = open(os.path.join(SITE, 'proyectos', 'index.html'), encoding='utf-8').read()
    head = s[:s.index('<main')]
    head = re.sub(r'<title>.*?</title>', f'<title>{esc(titulo)} | Colombia Risk</title>', head)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(dek)}">', head)
    head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="https://colombiarisk.com/proyectos/{slug}">', head)
    head = re.sub(r'\s*<link rel="stylesheet" href="/proyectos/figuras/medidor-pendiente\.css[^"]*">', '', head)
    head = re.sub(r'\s*<script type="module" src="/proyectos/figuras/medidor-pendiente\.js[^"]*"></script>', '', head)
    head = head.replace('href="../', 'href="/').replace('src="../', 'src="/')
    head = head.replace('</head>', '  <link rel="stylesheet" href="/proyectos/figuras/resultados.css?v=20261106a">\n</head>')
    foot = s[s.index('</main>'):]
    main = (f'<main id="contenido"><header class="article-header"><a class="article-back" href="/proyectos/">← Volver a Proyectos</a>'
            f'<h1>{esc(titulo)}</h1><p class="article-dek">{dek}</p><p class="rs-estado"><span class="estado estado--prep"><i aria-hidden="true"></i>Propuesta en estudio</span></p></header>{cuerpo}')
    d = os.path.join(SITE, 'proyectos', slug)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(head + main + foot)


# ---------------- 01 ----------------
def pg_territorial():
    xs = list(range(0, 26))
    p = Plot('Flujo acumulado del ferrocarril por escenario', 'Tres curvas del flujo acumulado sin descuento durante 25 años, en unidades monetarias sintéticas.',
             (0, 25), (min(min(v) for v in cum.values()), max(max(v) for v in cum.values())), xlabel='Años', xticks=[0, 5, 10, 15, 20, 25])
    for k, cls in (('Pesimista', 'rs-a'), ('Base', 'rs-b'), ('Optimista', 'rs-c')):
        p.line(xs, cum[k], cls, label=k, label_dx=-4, label_dy=-8)
    f1 = figure(p.svg(), 'Fig. 1 · Flujo acumulado por escenario',
                'Flujo de caja acumulado, sin descuento, en unidades monetarias sintéticas (millones de COP). Cruzar el cero es recuperar la inversión; no equivale al VPN.',
                ['Escenario', 'VPN al 10 %', 'Año en que se recupera la inversión'],
                [[k, sgn(rail[k]['npv'], 0), (str(payback[k]) if payback[k] is not None else 'no se recupera en 25 años')] for k in ('Pesimista', 'Base', 'Optimista')])
    q = Plot('VPN del caso base según las toneladas transportadas', 'Barras del VPN para cinco niveles de carga anual; el equilibrio está en 771 mil toneladas.',
             (650, 1050), (min(npv_ton + [0]), max(npv_ton)), xlabel='Toneladas por año (miles)', xticks=[700, 800, 900, 1000])
    q.bars(ton_pts, npv_ton, lambda x, y: 'rs-pos' if y >= 0 else 'rs-neg', width=44, fmt=lambda v: sgn(v))
    q.vline(tons_be, f'equilibrio: {fm(tons_be)}')
    f2 = figure(q.svg(), 'Fig. 2 · ¿Cuánta carga necesita el caso base?',
                f'Todo lo demás igual al caso base ({fm(base.annual_tons)} mil t por año). El VPN se vuelve positivo a partir de unas {fm(tons_be)} mil t.',
                ['Toneladas por año (miles)', 'VPN al 10 %'], [[fm(t), sgn(v)] for t, v in zip(ton_pts, npv_ton)])
    yrs = [m['year'] for m in mc]
    m = Plot('Proyección territorial sintética a 10 años', 'Mediana y rango entre el percentil 5 y el 95 de 5.000 trayectorias de un índice que parte de 100.',
             (0, 10), (min(x['p05'] for x in mc), max(x['p95'] for x in mc)), xlabel='Años', xticks=[0, 2, 4, 6, 8, 10])
    m.band(yrs, [x['p05'] for x in mc], [x['p95'] for x in mc], 'rs-b')
    m.line(yrs, [x['p50'] for x in mc], 'rs-b', label='mediana', label_dx=-6, label_dy=-10)
    m.line(yrs, [x['p05'] for x in mc], 'rs-b rs-fino')
    m.line(yrs, [x['p95'] for x in mc], 'rs-b rs-fino')
    f3 = figure(m.svg(), 'Fig. 3 · Abanico de un índice territorial sintético',
                'Índice base 100, crecimiento de 3,5 % y volatilidad de 12 % por año, 5.000 trayectorias, semilla 2026. El abanico recoge escenarios, no un intervalo de confianza.',
                ['Año', 'p05', 'mediana', 'p95'], [[x['year'], fm(x['p05'], 1), fm(x['p50'], 1), fm(x['p95'], 1)] for x in mc if x['year'] in (0, 2, 4, 6, 8, 10)])
    t = R['territorial']
    hall = cifras([(sgn(rail['Base']['npv']), 'VPN del caso base (unidades monetarias sintéticas). El pesimista da ' + sgn(rail['Pesimista']['npv']) + ' y el optimista ' + sgn(rail['Optimista']['npv']) + '.'),
                   (f'{fm(tons_be)} mil t', f'carga de equilibrio, frente a las {fm(base.annual_tons)} mil del caso base: un margen de {fm((1 - tons_be / base.annual_tons) * 100)} %.'),
                   (sgn(npv_opex_grows), 'VPN del caso base si los costos operativos crecieran igual que los ingresos (2,5 % al año). El resultado positivo depende de que no crezcan.')])
    est = (f'<p>Con los parámetros del ejemplo, el ingreso del primer año es {fm(base.annual_tons)} mil t × {f_(base.freight_rate_per_ton, 2)} + {fm(base.passengers)} mil pasajeros × {f_(base.fare_per_passenger, 2)} = {fm(year1, 1)}; '
           f'descontado el costo operativo de {fm(base.operating_cost)}, queda un flujo de {fm(year1 - base.operating_cost, 1)} frente a una inversión de {fm(base.capex)}.</p>'
           f'<p>Dos lecturas que conviene no perder. Primero, la inversión se recupera, en el caso base, en el año {payback["Base"]}, y el VPN positivo es modesto frente a lo invertido ({fm(rail["Base"]["npv"] / base.capex * 100)} % del capex). '
           f'Segundo, el modelo hace crecer los ingresos 2,5 % al año pero deja el costo operativo fijo en {fm(base.operating_cost)} durante 25 años; si el costo creciera al mismo ritmo, el VPN pasaría a {sgn(npv_opex_grows, 1)}. '
           f'Es una limitación del modelo, no un hallazgo sobre un ferrocarril: la cifra positiva no debe leerse como una señal de viabilidad.</p>'
           f'<p>En la proyección territorial, la mediana del índice a 10 años es {fm(mc[-1]["p50"], 1)} (el crecimiento supuesto de 3,5 % daría cerca de 132 sin ruido), y el rango entre p05 y p95 va de {fm(mc[-1]["p05"], 1)} a {fm(mc[-1]["p95"], 1)}: '
           f'la volatilidad de 12 % que se supuso pesa casi tanto como el crecimiento.</p>')
    lim = limites(['El ferrocarril es un modelo conceptual: no incluye impuestos, estructura de deuda, ramp-up de carga y pasajeros, ingresos auxiliares, riesgo de construcción, cronograma del capex, terminales ni costos de montaña.',
                   'La recuperación simple de la Fig. 1 no sustituye al VPN.',
                   'La proyección no incorpora ciclos, correlación espacial ni rupturas estructurales. Sus percentiles son cuantiles de escenarios, no intervalos de confianza.',
                   'El cribado topográfico usa modelos globales de 30 m para cribado regional. No hay corredor definido ni diseño de ingeniería, y la pendiente del terreno no es la de diseño de la vía.'])
    cuerpo = seccion('Qué muestran los números', aviso() + hall) + seccion('Los gráficos', f1 + f2 + f3) + seccion('Qué dicen los números', est) + seccion('Lo que no dicen', lim) + cierre('desarrollo-territorial', '01-territorial-development', 'Desarrollo territorial y económico')
    page('desarrollo-territorial', 'Desarrollo territorial y económico: resultados',
         'Cribar oportunidades por territorio en infraestructura, energía y conectividad. Aquí, los resultados de un ejercicio sintético: un ferrocarril conceptual y una proyección territorial.', cuerpo)


# ---------------- 02 ----------------
def pg_fraude():
    rows = [(k, v['q'][0] / 1e6, v['q'][1] / 1e6, v['q'][2] / 1e6, v['q'][3] / 1e6, v['q'][4] / 1e6, c, v['expected'] / 1e6) for (k, v), c in zip(fraud.items(), ('rs-a', 'rs-b', 'rs-c'))]
    f1 = figure(boxes('Pérdida anual simulada por escenario', 'Caja con percentiles 25, 50 y 75 y bigotes en 5 y 95 de 600 simulaciones por escenario; el triángulo marca la pérdida esperada.',
                      rows, lambda v: f_(v, 0), (0, max(r[5] for r in rows) * 1.12), xlabel='Pérdida anual (millones de COP)'),
                'Fig. 1 · Cuánto puede variar la pérdida por fraude',
                'Caja: del percentil 25 al 75; línea: mediana; bigotes: percentiles 5 y 95; triángulo: pérdida esperada (1.200 solicitudes × prevalencia × 750.000 COP). 600 simulaciones por escenario, semilla 2026.',
                ['Escenario', 'Prevalencia', 'Esperada', 'p05', 'mediana', 'p95'],
                [[k, f'{prevs[k] * 100:.1f} %'.replace('.', ','), f_(v['expected'] / 1e6, 1), f_(v['q'][0] / 1e6, 1), f_(v['q'][2] / 1e6, 1), f_(v['q'][4] / 1e6, 1)] for k, v in fraud.items()])
    # puntaje: antes y después
    p0, p1 = sc0['fraud_probability'], cf['after']['fraud_probability']
    pl_ = hbars('Probabilidad de fraude del ejemplo antes y después de bajar la señal de grafo', 'Dos barras de probabilidad con los umbrales de 30 % y 65 % que separan permitir, verificar más y revisar.',
                [('Señal de grafo en 0,8', p0 * 100, 'rs-c'), ('Señal de grafo en 0,2', p1 * 100, 'rs-b')], lambda v: f_(v, 0) + ' %', xdom=(0, 100), xlabel='Probabilidad de fraude (%)',
                refs=((30, 'verificar más ≥ 30 %'), (65, 'revisar ≥ 65 %')))
    f2 = figure(pl_, 'Fig. 2 · Un caso, dos señales',
                'Solicitud sintética con señales de 0,6 (identidad), 0,5 (dispositivo), 0,7 (velocidad), 0,4 (comportamiento), 0,5 (documento) y 0,8 (grafo). Por encima de 65 % pasa a revisión; entre 30 % y 65 %, a verificación adicional; por debajo, se permite.',
                ['Caso', 'Probabilidad', 'Acción'], [['Señal de grafo en 0,8', f'{p0 * 100:.1f} %'.replace('.', ','), sc0['action']], ['Señal de grafo en 0,2', f'{p1 * 100:.1f} %'.replace('.', ','), cf['after']['action']]])
    contrib = [(n, w * v, 'rs-b') for n, w, v in WEIGHTS]
    f3 = figure(hbars('Aporte de cada señal al puntaje del ejemplo', 'Barras con el aporte de cada señal (peso por valor) al puntaje que se convierte en probabilidad.',
                      contrib, lambda v: f_(v, 2), xdom=(0, 1.4), xlabel='Peso × valor de la señal'),
                'Fig. 3 · Qué señal pesa más en el puntaje',
                'El puntaje es −3,2 + Σ (peso × señal), convertido a probabilidad con la función logística. Los pesos son fijos y no están calibrados con datos.',
                ['Señal', 'Peso', 'Valor', 'Aporte'], [[n, f_(w, 2), f_(v, 1), f_(w * v, 2)] for n, w, v in WEIGHTS])
    c, b, e = fraud['Controlado'], fraud['Base'], fraud['Estrés']
    hall = cifras([(f'{f_(c["expected"] / 1e6, 1)} / {f_(b["expected"] / 1e6, 1)} / {f_(e["expected"] / 1e6, 1)} M', 'pérdida anual esperada en millones de COP, en los escenarios controlado, base y estrés (prevalencias de 0,5 %, 1,5 % y 4 %).'),
                   (f'{f_(c["q"][0] / 1e6, 1)} a {f_(c["q"][4] / 1e6, 1)} M', f'rango entre p05 y p95 del escenario controlado: con pocos casos, el azar mueve mucho la pérdida de un año a otro.'),
                   (f'{p0 * 100:.0f} % → {p1 * 100:.0f} %'.replace('.', ','), f'probabilidad de fraude del ejemplo al bajar la señal de grafo de 0,8 a 0,2: la acción pasa de {sc0["action"]} a {cf["after"]["action"]}.')])
    est = (f'<p>La pérdida esperada es simple: solicitudes × prevalencia × pérdida media. Con 1.200 solicitudes y 750.000 COP por caso, cada punto porcentual de prevalencia vale {f_(REQ * .01 * LOSS / 1e6, 1)} millones al año. '
           f'Pasar del escenario controlado al de estrés multiplica la pérdida esperada por {f_(prevs["Estrés"] / prevs["Controlado"], 0)}.</p>'
           f'<p>Lo más instructivo es la dispersión. En el escenario controlado se esperan {REQ * prevs["Controlado"]:.0f} casos al año, y en 600 años simulados la pérdida va de {f_(c["q"][0] / 1e6, 1)} a {f_(c["q"][4] / 1e6, 1)} millones entre p05 y p95. '
           f'Con tan pocos eventos, un solo año bueno o malo dice poco sobre la prevalencia real: hace falta una ventana larga o más solicitudes para distinguir escenarios.</p>'
           f'<p>El puntaje de ejemplo tiene una propiedad que conviene conocer: con todas las señales en cero la probabilidad no es cero sino {p_zero * 100:.1f} %'.replace('.', ',') +
           f', porque el término independiente es −3,2. Y la señal de grafo, con el mayor peso (1,55), es la que más mueve la decisión: bajarla de 0,8 a 0,2 reduce la probabilidad en {abs(cf["delta"]) * 100:.0f} puntos. Son pesos escogidos a mano para ilustrar, no estimados.</p>')
    lim = limites(['Trabaja con datos simulados. No se almacenan datos personales.',
                   'La simulación es Bernoulli independiente: ignora agrupamiento de casos, recuperaciones, exposición variable, errores de detección y cambios de composición.',
                   'Los pesos del puntaje no están calibrados ni validados con datos históricos. La probabilidad que produce no es una tasa observada.',
                   'No incluye el costo de los falsos positivos ni el de la verificación reforzada. Antes de cualquier uso hacen falta datos con permisos, calibración, backtesting y revisión de sesgos y privacidad.'])
    cuerpo = seccion('Qué muestran los números', aviso() + hall) + seccion('Los gráficos', f1 + f2 + f3) + seccion('Qué dicen los números', est) + seccion('Lo que no dicen', lim) + cierre('fraude-identidad', '02-fraud-identity', 'Fraude, identidad y KYC')
    page('fraude-identidad', 'Fraude, identidad y KYC: resultados',
         'Combinar anomalías, grafos de relaciones y señales de dispositivo para detectar identidades sintéticas. Aquí, los resultados de un ejercicio con datos simulados.', cuerpo)


# ---------------- 03 ----------------
def pg_judicial():
    nodes = [('a', 'Fuentes públicas\nautorizadas', 'rs-n1'), ('b', 'Procedencia\ny trazabilidad', 'rs-n1'), ('c', 'Normalización', 'rs-n1'), ('d', 'Resolución\nde entidades', 'rs-n2'),
             ('e', 'Eventos\nprocesales', 'rs-n2'), ('f', 'Grafo de\nrelaciones', 'rs-n2'), ('g', 'Modelos de\nduración', 'rs-n3'), ('h', 'Exposición\ny contexto', 'rs-n3'), ('i', 'Revisión\nhumana', 'rs-n4'), ('j', 'Reporte\nauditable', 'rs-n4')]
    f = figure(flow('Método propuesto para la analítica judicial', 'Diez pasos en cuatro filas: de las fuentes públicas autorizadas al reporte auditable, con revisión humana antes del resultado.', nodes, cols=5),
               'Fig. 1 · Cómo se propone trabajar', 'Esquema del método en formulación. Ninguna de estas etapas está implementada ni produce resultados todavía.',
               ['Paso', 'Qué hace'], [['Fuentes públicas autorizadas', 'Solo fuentes con permiso y procedencia.'], ['Procedencia y trazabilidad', 'Cada dato conserva su origen y su control de cambios.'], ['Normalización', 'Formatos y nombres comparables.'],
                                      ['Resolución de entidades', 'Identificar personas jurídicas con salvaguardas.'], ['Eventos procesales', 'Taxonomía de procesos y eventos.'], ['Grafo de relaciones', 'Proceso, parte, evento y jurisdicción.'],
                                      ['Modelos de duración', 'Tiempo hasta hitos procesales.'], ['Exposición y contexto', 'Estimación probabilística por escenario.'], ['Revisión humana', 'Obligatoria antes de cualquier resultado.'], ['Reporte auditable', 'Con la evidencia que lo respalda.']])
    cartera = ('<ol class="rs-lista">' + ''.join(f'<li>{x}</li>' for x in ['Taxonomía de procesos y eventos judiciales.', 'Pipeline de datos públicos con procedencia y control de cambios.', 'Resolución de entidades de personas jurídicas, con salvaguardas.',
                                                                               'Modelo de duración y supervivencia hasta hitos procesales.', 'Estimación probabilística de exposición económica por escenario.', 'Grafo de conocimiento proceso–parte–evento–jurisdicción.',
                                                                               'Motor de alertas por cambio material, no por perfilamiento sensible.']) + '</ol>')
    estado = ('<p class="rs-aviso"><strong>Todavía no hay resultados.</strong> La fuente de investigación de este programa estaba sin contenido sustantivo recuperable, así que esta propuesta es una formulación inicial, no una afirmación sobre capacidades existentes. '
              'No hay código que produzca cifras, y por eso esta página no muestra ninguna. Cuando exista un ejercicio reproducible, sus resultados se publicarán aquí con el mismo formato que los otros programas.</p>')
    lim = limites(['No se automatizan conclusiones legales ni decisiones adversas sobre personas.', 'Requiere revisión jurídica, protección de datos y revisión humana en cada resultado.', 'Ningún resultado se presenta como conclusión automática.'])
    cuerpo = seccion('Dónde está hoy', estado) + seccion('El método propuesto', f + '<h3 class="rs-sub">Cartera inicial</h3>' + cartera) + seccion('Lo que no haría', lim) + cierre('riesgo-judicial', '03-judicial-risk', 'Riesgo y analítica judicial')
    page('riesgo-judicial', 'Riesgo y analítica judicial: método',
         'Dar trazabilidad a las fuentes, resolver entidades y estimar exposición a procesos judiciales, con revisión humana de cada resultado. Todavía sin resultados: aquí, el método propuesto.', cuerpo)


# ---------------- 04 ----------------
def pg_agro():
    a = Plot('VPN del proyecto según el precio de venta', 'Línea del VPN para precios de 1,5 a 6 millones de COP por tonelada; cruza el cero en 5,0 y el caso base está en 2,4.',
             (1.5, 6.0), (min(agro_price), max(agro_price)), xlabel='Precio de venta (millones de COP por tonelada)', xticks=[2, 3, 4, 5, 6], xfmt=lambda v: f_(v, 0))
    a.line(prices, agro_price, 'rs-b')
    a.dot(ap.sale_price_mcop_ton, a0['npv_mcop'], 'rs-c', f'caso base · {f_(ap.sale_price_mcop_ton, 1)}', dx=12, dy=26)
    a.dot(price_be, 0, 'rs-b', f'equilibrio · {f_(price_be, 1)}', dx=-10, dy=-14)
    f1 = figure(a.svg(), 'Fig. 1 · Qué precio necesita el proyecto', f'VPN en millones de COP constantes, con los demás parámetros iguales. Con el precio base de {f_(ap.sale_price_mcop_ton, 1)} el VPN es {sgn(a0["npv_mcop"])}; el equilibrio llega cerca de {f_(price_be, 1)}, {f_(price_be / ap.sale_price_mcop_ton, 1)} veces el precio base.',
                ['Precio (M COP/t)', 'VPN (M COP)'], [[f_(x, 2), sgn(v)] for x, v in zip(prices, agro_price) if round(x * 4) % 2 == 0])
    rows = [(k, v, 'rs-neg' if v < 0 else 'rs-pos') for k, v in agro_cases.items()]
    f2 = figure(hbars('VPN del proyecto por escenario', 'Barras horizontales del VPN en millones de COP para el caso base y cuatro variaciones; todas son negativas.',
                      rows, lambda v: sgn(v), xdom=(min(v for _, v, _ in rows) * 1.12, 0), xlabel='VPN (millones de COP constantes)'),
                'Fig. 2 · Ningún escenario cierra', 'Variaciones de un parámetro a la vez. Se omite el costo de capital: con flujos negativos, descontar más reduce las pérdidas y daría una señal engañosa.',
                ['Escenario', 'VPN (M COP)'], [[k, sgn(v)] for k, v in agro_cases.items()])
    d = Plot('Participación de los productores tras una ronda de capital', 'Curva de la participación de productores, que parte de 55 %, según el capital nuevo que entra a un valor previo de 100.',
             (0, 100), (30, 60), xlabel='Capital nuevo (unidades monetarias, valor previo = 100)', ylabel='Participación de productores (%)', xticks=[0, 25, 50, 75, 100], yticks=[30, 40, 50, 60])
    d.line(rounds, dil, 'rs-b')
    for i, (r, v) in enumerate(zip(rounds, dil)):
        d.dot(r, v, 'rs-b', f'{f_(v, 1)} %', dx=(-8 if i == len(rounds) - 1 else 8), dy=-10)
    f3 = figure(d.svg(), 'Fig. 3 · Dilución de los productores', 'Estructura inicial hipotética: productores 55 %, inversionistas 30 %, bolsa de incentivos 10 %, fundadores 5 %. Sin aporte propio de los productores a la ronda.',
                ['Capital nuevo', 'Participación de productores'], [[str(r), f'{f_(v, 1)} %'] for r, v in zip(rounds, dil)])
    tdep = table(['Departamento', 'Cadenas candidatas', 'Transformación', 'Logística'], [[x['departamento'], x['cadenas_candidatas'], x['transformacion'], x['logistica']] for x in deptos])
    hall = cifras([(sgn(a0['npv_mcop']), 'VPN del caso base en millones de COP: con estos parámetros sintéticos el proyecto no se sostiene.'),
                   (f'{payroll_share * 100:.0f} %'.replace('.', ','), f'peso de la nómina ({fm(a0["annual_staff_cost_mcop"])}) sobre el ingreso del primer año ({fm(a0["year1"]["revenue_mcop"])}): el EBITDA del año 1 es {sgn(a0["year1"]["ebitda_mcop"])}.'),
                   (f'{f_(price_be, 1)} M/t', f'precio de equilibrio, {f_(price_be / ap.sale_price_mcop_ton, 1)} veces el base de {f_(ap.sale_price_mcop_ton, 1)}. Escalar no lo resuelve: con {fm(ha_be)} ha el agua llega a {fm(a_ha["annual_water_m3"])} m³ y supera el tope de {fm(ap.max_water_m3_year)}.')])
    est = (f'<p>El ejemplo de capital privado parte de {fm(ap.hectares)} hectáreas, {ap.yield_ton_ha:g} t por hectárea y un precio de {f_(ap.sale_price_mcop_ton, 1)} millones por tonelada. El ingreso del primer año es {fm(a0["year1"]["revenue_mcop"])} y la nómina de dos cuadrillas rotativas ({a0["headcount_assumed"]} personas) cuesta {fm(a0["annual_staff_cost_mcop"])}: '
           f'ya consume {payroll_share * 100:.0f} % de lo que se vende, antes de costos variables, de campo y fijos. Por eso el EBITDA es negativo todos los años y el VPN es de {sgn(a0["npv_mcop"])} millones.</p>'
           f'<p>Se necesitarían cerca de {f_(price_be, 1)} millones por tonelada, {f_(yield_be, 0)} t por hectárea o {fm(ha_be)} hectáreas para llegar al equilibrio. Las hectáreas parecen una salida, pero el agua lo impide: a {fm(ha_be)} ha el uso es de {fm(a_ha["annual_water_m3"])} m³ al año, {f_(a_ha["annual_water_m3"] / ap.max_water_m3_year, 1)} veces el tope de {fm(ap.max_water_m3_year)} m³. '
           f'El caso base usa {fm(a0["annual_water_m3"])} m³, que sí cumple, pero deja poco margen para crecer.</p>'
           f'<p>La lectura honesta es la que ya traía el propio ejercicio: un VPN negativo obliga a rediseñar el proyecto antes de buscar capital. Qué rediseñar lo dicen los números: la estructura de personal, el precio al que se vende y el rendimiento por hectárea pesan más que el costo de capital.</p>'
           f'<p>La curva de la Fig. 1 cambia de pendiente cerca de {f_(price_ebitda0, 1)} millones por tonelada: desde ahí el EBITDA del primer año es positivo y el modelo empieza a restar el impuesto de 35 %, que solo aplica a EBITDA positivo. Es una simplificación declarada del modelo, no un efecto del proyecto.</p>'
           f'<p>En la dilución, una ronda de 50 unidades sobre un valor previo de 100 baja a los productores de 55 % a {f_(dil[3], 1)} % si no aportan capital; la mecánica es aritmética, no una recomendación de estructura.</p>')
    lim = limites(['Todos los parámetros son sintéticos: no es un estudio de mercado ni usa costos observados en Colombia ni una nómina validada legalmente.',
                   'La rotación 15/15 se modela con dos cuadrillas y no constituye validación de jornada laboral.',
                   'Los impuestos son una simplificación (sobre el EBITDA positivo): no hay deuda, depreciación ni arrastre de pérdidas.',
                   'No es una valoración, una oferta de acciones ni asesoría legal. Cualquier mecanismo patrimonial requiere acuerdos jurídicos y consentimiento de los productores.',
                   'La tabla de departamentos lista cadenas candidatas para estudio; no es un ranking ni evidencia de rentabilidad.'])
    cuerpo = (seccion('Qué muestran los números', aviso() + hall) + seccion('Los gráficos', f1 + f2 + f3) + seccion('Qué dicen los números', est)
              + seccion('Cadenas candidatas por departamento', f'<p>Punto de partida para estudiar dónde probar la propuesta: {len(deptos)} departamentos con las cadenas productivas que se consideraría analizar.</p>{tdep}', 'departamentos')
              + seccion('Lo que no dicen', lim) + cierre('agroindustria', '04-agroindustry-farmer-ownership', 'Agroindustria tecnificada y propiedad campesina'))
    page('agroindustria', 'Agroindustria tecnificada y propiedad campesina: resultados',
         'Estudiar si el productor puede participar como proveedor, trabajador o copropietario con derechos exigibles. Aquí, los resultados de un ejercicio sintético de rentabilidad, agua y dilución.', cuerpo)


# ---------------- 05 ----------------
def pg_integridad():
    d = R['integridad']['digests']
    short = lambda h: '#' + h[:12] + '…'
    nodes = [('g', 'Inicio\n#' + '0' * 12 + '…', 'rs-n1'), ('e0', 'Evento 0 · registrado\n' + short(d[0]), 'rs-n2'), ('e1', 'Evento 1 · verificado\n' + short(d[1]), 'rs-n2'), ('r', 'Raíz del árbol\n' + short(trusted['root']), 'rs-n3')]
    f1 = figure(flow('Cadena de eventos con huellas encadenadas', 'Cuatro cajas: el inicio, dos eventos cuyas huellas dependen de la anterior, y la raíz del árbol que resume toda la cadena.', nodes, cols=4, node_h=70),
                'Fig. 1 · Cómo se encadena el expediente', 'Cada evento guarda la huella SHA-256 del anterior: cambiar cualquiera cambia todas las siguientes. La raíz resume toda la cadena. Contratos y datos sintéticos.',
                ['Pieza', 'Huella (primeros 12 caracteres)'], [['Evento 0', d[0][:12]], ['Evento 1', d[1][:12]], ['Raíz', trusted['root'][:12]]])
    ok = lambda b: 'Coincide' if b else 'No coincide'
    ver_rows = [['El registro original frente al punto de control externo', ok(ver['original']), 'Es la verificación que debe pasar.'],
                ['Una historia reescrita (se cambió «registrado» por «pagado»), frente a su propio punto de control', ok(ver['forged_self']), 'Es internamente consistente: pasa su propia verificación.'],
                ['La misma historia reescrita, frente al punto de control externo original', ok(ver['forged_ext']), 'Aquí se detecta la reescritura.'],
                ['Una historia truncada (sin el último evento), frente al punto de control externo', ok(ver['truncated']), 'También se detecta.']]
    f2 = ('<figure class="rs-fig"><figcaption class="rs-title">Tabla 1 · Cuatro verificaciones sobre el mismo ejemplo</figcaption>'
          + table(['Qué se comprueba', 'Resultado', 'Qué significa'], ver_rows) + '<p class="rs-note">Ejemplo sintético con dos eventos de un contrato ficticio, ejecutado con el código del programa. Ningún contrato ni pago es real.</p></figure>')
    comp = table(['Proyecto', 'Resultado propuesto', 'Control y límite'], componentes)
    hall = cifras([('Sí', 'el registro reescrito pasa su propia verificación: sin una referencia externa, una cadena falsa puede verse perfectamente válida.'),
                   ('2 de 2', 'las alteraciones del ejemplo (reescribir y truncar) se detectan al compararlas con un punto de control obtenido fuera de quien opera el registro.'),
                   ('0', 'cosas que acredita la cadena sobre si un documento es verdadero: un documento falso puede quedar perfectamente registrado.')])
    est = ('<p>La idea central del programa cabe en la tabla 1. Una cadena de huellas permite detectar que algo cambió, pero solo si alguien guardó antes una referencia confiable de cómo era. '
           'Quien opera el registro puede reescribir la historia y recalcular todas las huellas: el resultado será internamente impecable. Lo que lo delata es la comparación con un punto de control que no controla el operador, como una copia en poder de un testigo independiente.</p>'
           '<p>Por eso el diseño no se apoya en «usar cadena de bloques» sino en tres cosas: una referencia externa, separación de funciones entre quien propone, verifica y autoriza, y un registro que conserva la historia agregando eventos en vez de borrarla. '
           'Y por eso la hipótesis del programa es falsable: frente al expediente convencional, estos controles reducirían las alteraciones no detectadas sin volver inviable el trámite. No se presume que reduzcan la corrupción.</p>')
    lim = limites(['Es un laboratorio sintético: no hay firmas, persistencia, identidad ni cadena de bloques.', 'Un punto de control solo es confiable si se obtiene y autentica fuera de quien opera el registro.',
                   'El registro no prueba que un documento sea verdadero, ni fecha, ni que la historia esté completa más allá de lo que el punto de control comprometió.',
                   'Los identificadores de hito son registros de control no transferibles: no son moneda ni un derecho negociable.', 'No hay convenios con entidades ni despliegues.'])
    cuerpo = (seccion('Qué muestran los números', aviso() + hall) + seccion('El ejemplo', f1 + f2) + seccion('Qué dicen los números', est)
              + seccion('Los diez componentes propuestos y sus límites', f'<p>Cada componente nombra su resultado y también lo que no puede garantizar.</p>{comp}', 'componentes')
              + seccion('Lo que no dicen', lim) + cierre('integridad-publica', '05-public-integrity', 'Integridad pública verificable'))
    page('integridad-publica', 'Integridad pública verificable: resultados',
         'Un expediente verificable por contrato e hito para dar trazabilidad a la ejecución de recursos públicos. Aquí, un ejemplo sintético que muestra qué detecta y qué no detecta una cadena de huellas.', cuerpo)


# ---------------- portada y CSS ----------------
CARDS = {1: ('desarrollo-territorial', '01-territorial-development', 'Desarrollo territorial y económico', f'{sgn(rail["Base"]["npv"])} · {sgn(npv_opex_grows)}',
             f'VPN del ferrocarril conceptual, y el mismo caso si los costos crecieran igual que los ingresos. Ejercicio sintético.', 'Ver resultados'),
         2: ('fraude-identidad', '02-fraud-identity', 'Fraude, identidad y KYC', f'{f_(fraud["Controlado"]["expected"] / 1e6, 1)} a {f_(fraud["Estrés"]["expected"] / 1e6, 0)} M',
             'pérdida anual esperada en COP, del escenario controlado al de estrés. Datos simulados.', 'Ver resultados'),
         3: ('riesgo-judicial', '03-judicial-risk', 'Riesgo y analítica judicial', 'Sin resultados aún', 'Esta propuesta está en formulación: aquí, el método propuesto.', 'Ver el método'),
         4: ('agroindustria', '04-agroindustry-farmer-ownership', 'Agroindustria tecnificada y propiedad campesina', sgn(a0['npv_mcop']) + ' M',
             f'VPN del caso base: con estos parámetros sintéticos el proyecto no se sostiene; el precio de equilibrio es {f_(price_be / ap.sale_price_mcop_ton, 1)} veces el base.', 'Ver resultados'),
         5: ('integridad-publica', '05-public-integrity', 'Integridad pública verificable', 'Sí · 2 de 2', 'un registro reescrito pasa su propia verificación y solo se detecta con un punto de control externo.', 'Ver resultados')}


def portada():
    p = os.path.join(SITE, 'proyectos', 'index.html')
    s = open(p, encoding='utf-8').read()
    for n, (slug, prog, nombre, cifra, texto, verbo) in CARDS.items():
        m = re.search(r'<article id="propuesta-%d">.*?</article>' % n, s, re.S)
        art = m.group(0)
        cut = min(i for i in (art.find('<p class="rs-cifra-card"'), art.find('<p><a class="enlace" href="https://github.com')) if i >= 0)
        new = (art[:cut] + f'<p class="rs-cifra-card"><strong>{esc(cifra)}</strong> {esc(texto)}</p>'
               f'<p class="rs-acciones"><a class="enlace" href="/proyectos/{slug}/">{verbo}<span class="visually-hidden"> de {esc(nombre)}</span> →</a> '
               f'<a class="enlace rs-secundario" href="{GH}/tree/main/programs/{prog}" target="_blank" rel="noopener noreferrer">Código en GitHub ↗<span class="visually-hidden"> de {esc(nombre)} (abre en una pestaña nueva)</span></a></p></article>')
        s = s.replace(art, new)
    s = re.sub(r'<link rel="stylesheet" href="/proyectos/figuras/resultados\.css[^"]*">\s*', '', s)
    s = s.replace('<link rel="stylesheet" href="/proyectos/figuras/medidor-pendiente.css', '<link rel="stylesheet" href="/proyectos/figuras/resultados.css?v=20261106a">\n  <link rel="stylesheet" href="/proyectos/figuras/medidor-pendiente.css', 1)
    open(p, 'w', encoding='utf-8').write(s)


if SITE:
    pg_territorial(); pg_fraude(); pg_judicial(); pg_agro(); pg_integridad(); portada()
    src = os.path.join(ROOT, 'site-results', 'resultados.css')
    open(os.path.join(SITE, 'proyectos', 'figuras', 'resultados.css'), 'w', encoding='utf-8').write(open(src, encoding='utf-8').read())
    print(f'Páginas y cifras escritas en {SITE}/proyectos (commit de los programas {COMMIT})')
else:
    print('Resultados calculados en site-results/out/resultados.json (sin carpeta de sitio no se escriben páginas).')
