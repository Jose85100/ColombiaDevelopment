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
R['territorial'] = dict(toneladas={k: v.annual_tons for k, v in esc_rail.items()}, crecimiento={k: v.annual_growth for k, v in esc_rail.items()}, rail_npv={k: v['npv'] for k, v in rail.items()}, payback_year=payback, tons_breakeven=tons_be, npv_if_opex_grows=npv_opex_grows,
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
R['fraude'] = dict(senales=[dict(nombre=n, peso=w, valor=v) for n, w, v in WEIGHTS], umbrales=dict(revisar=.65, verificar=.30), scenarios=fraud, example=dict(p=sc0['fraud_probability'], action=sc0['action'], after=cf['after']['fraud_probability'], after_action=cf['after']['action']), p_all_zero=p_zero)

# ======================= 04 · AGROINDUSTRIA =======================
ap_ini = Project()                       # ejercicio inicial del repo
a_ini = agro_eval(ap_ini)
# Caso rediseñado: ver supuestos en DISENO. Se mantiene el tope de agua del ejercicio inicial.
DISENO = dict(hectares=220, yield_ton_ha=10, sale_price_mcop_ton=3.0, staff_per_rotation=10, water_m3_per_ton=90)
ap = replace(ap_ini, **DISENO)
a0 = agro_eval(ap)
price_be_ini = bisect(lambda x: agro_eval(replace(ap_ini, sale_price_mcop_ton=x))['npv_mcop'], .1, 50)
price_be = bisect(lambda x: agro_eval(replace(ap, sale_price_mcop_ton=x))['npv_mcop'], .1, 50)
yield_be = bisect(lambda x: agro_eval(replace(ap, yield_ton_ha=x))['npv_mcop'], .1, 200)
ha_be = bisect(lambda x: agro_eval(replace(ap, hectares=x))['npv_mcop'], 1, 5000)
price_ebitda0 = bisect(lambda x: agro_eval(replace(ap, sale_price_mcop_ton=x))['year1']['ebitda_mcop'], .1, 50)
a_ha = agro_eval(replace(ap, hectares=ha_be))
payroll_share = a0['annual_staff_cost_mcop'] / a0['year1']['revenue_mcop']
cases = {'Ejercicio inicial': ap_ini, 'Caso rediseñado': ap, 'Precio −10 %': replace(ap, sale_price_mcop_ton=ap.sale_price_mcop_ton * .9), 'Precio −20 %': replace(ap, sale_price_mcop_ton=ap.sale_price_mcop_ton * .8),
         'Rendimiento −10 %': replace(ap, yield_ton_ha=ap.yield_ton_ha * .9), 'Rendimiento −25 %': replace(ap, yield_ton_ha=ap.yield_ton_ha * .75),
         'CAPEX +35 %': replace(ap, capex_mcop=ap.capex_mcop * 1.35), 'Precio +35 %': replace(ap, sale_price_mcop_ton=ap.sale_price_mcop_ton * 1.35)}
agro_cases = {k: agro_eval(v)['npv_mcop'] for k, v in cases.items()}
prices = [1.5 + .25 * i for i in range(19)]   # 1,5 a 6,0
agro_price = [agro_eval(replace(ap, sale_price_mcop_ton=x))['npv_mcop'] for x in prices]
own = Ownership()
rounds = [0, 10, 25, 50, 100]
dil = [equity_after_round(own, 100, n)['farmers'] * 100 for n in rounds]
with open(os.path.join(ROOT, 'programs/04-agroindustry-farmer-ownership/data/department_opportunities.csv'), newline='', encoding='utf-8') as fh:
    deptos = list(csv.DictReader(fh))
def _y1(p_, e_):
    sold = p_.hectares * p_.yield_ton_ha * (1 - p_.spoilage)
    return dict(ingresos=sold * p_.sale_price_mcop_ton, variables=sold * p_.variable_cost_mcop_ton, campo=p_.hectares * p_.field_cost_mcop_ha,
                nomina=e_['annual_staff_cost_mcop'], fijos=p_.annual_fixed_mcop)
R['agro'] = dict(year1=dict(inicial=_y1(ap_ini, a_ini), diseno=_y1(ap, a0)), npv_inicial=a_ini['npv_mcop'], diseno=DISENO, npv_base=a0['npv_mcop'], ebitda_year1=a0['year1']['ebitda_mcop'], revenue_year1=a0['year1']['revenue_mcop'], payroll=a0['annual_staff_cost_mcop'], payroll_share=payroll_share,
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


def anatomia_fig(slug, title, note, headers, rows):
    """Figura isométrica hecha con el kit de Anatomy (site-results/anatomia). El SVG ya viene sin estilos en línea."""
    svg = open(os.path.join(ROOT, 'site-results', 'anatomia', 'out', slug + '.fragment.svg'), encoding='utf-8').read()
    u = uid()
    svg = svg.replace('role="img" aria-label=', f'role="img" aria-describedby="{u}-n" aria-label=')
    return (f'<figure class="rs-fig"><figcaption class="rs-title">{esc(title)}</figcaption><div class="iso iso-figura">{svg}</div><p class="rs-note" id="{u}-n">{note}</p>'
            f'<details class="rs-data"><summary>Ver los valores de la figura</summary>{table(headers, rows)}</details></figure>')


def cifras(items):
    return '<ul class="rs-cifras">' + ''.join(f'<li><strong>{esc(a)}</strong><span>{b}</span></li>' for a, b in items) + '</ul>'


def limites(items):
    return '<ul class="rs-limites">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'


def seccion(titulo, cuerpo, id=''):
    return f'<section class="rs-sec"{f" id={chr(34)}{id}{chr(34)}" if id else ""}><h2>{esc(titulo)}</h2>{cuerpo}</section>'


def aviso():
    return (f'<p class="rs-aviso"><strong>Cómo leer estas cifras.</strong> Salen del código público de la propuesta, ejecutado con parámetros definidos por Colombia Risk '
            f'(commit <code>{esc(COMMIT)}</code>, semilla 2026). Es un ejercicio de modelado para comparar escenarios y decisiones; no es una proyección ni una oferta.</p>')


def cierre(slug, prog, nombre):
    return (f'<section class="rs-sec rs-cierre"><h2>Código y reproducción</h2><p>Todo lo que ves se calcula con el código del programa. '
            f'Puedes revisarlo y repetir las cuentas.</p><p class="rs-acciones"><a class="enlace" href="{GH}/tree/main/programs/{prog}" target="_blank" rel="noopener noreferrer">Código en GitHub ↗<span class="visually-hidden"> de {esc(nombre)} (abre en una pestaña nueva)</span></a>'
            f' <a class="enlace" href="/proyectos/">← Volver a Proyectos</a> <a class="enlace" href="mailto:contacto@colombiarisk.com?subject=Proponer%20una%20necesidad">Proponer una necesidad →</a></p></section>')


ETAPA = {'desarrollo-territorial': (3, 'Prefactibilidad'), 'fraude-identidad': (2, 'Validación'), 'riesgo-judicial': (1, 'Idea'),
         'agroindustria': (2, 'Validación'), 'integridad-publica': (2, 'Validación')}


def page(slug, titulo, dek, cuerpo):
    s = open(os.path.join(SITE, 'proyectos', 'index.html'), encoding='utf-8').read()
    head = s[:s.index('<main')]
    head = re.sub(r'<title>.*?</title>', f'<title>{esc(titulo)} | Colombia Risk</title>', head)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(dek)}">', head)
    head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="https://colombiarisk.com/proyectos/{slug}">', head)
    head = re.sub(r'\s*<link rel="stylesheet" href="/proyectos/figuras/medidor-pendiente\.css[^"]*">', '', head)
    head = re.sub(r'\s*<script type="module" src="/proyectos/figuras/medidor-pendiente\.js[^"]*"></script>', '', head)
    head = head.replace('href="../', 'href="/').replace('src="../', 'src="/')
    head = head.replace('</head>', '  <link rel="stylesheet" href="/proyectos/figuras/resultados.css?v=20261106a">\n  <link rel="stylesheet" href="/proyectos/figuras/anatomia.css?v=20261106a">\n</head>')
    foot = s[s.index('</main>'):]
    main = (f'<main id="contenido"><header class="article-header"><a class="article-back" href="/proyectos/">← Volver a Proyectos</a>'
            f'<h1>{esc(titulo)}</h1><p class="article-dek">{dek}</p><p class="rs-estado"><span class="estado estado--prep"><i aria-hidden="true"></i>Propuesta en estudio · Etapa {ETAPA[slug][0]} de 8: {ETAPA[slug][1]}</span></p></header>{cuerpo}')
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
                   (sgn(npv_opex_grows), 'VPN del caso base si los costos operativos crecieran igual que los ingresos (2,5 % al año). El caso base se mantiene positivo mientras los costos crezcan por debajo de los ingresos.')])
    est = (f'<p>Con los parámetros del ejemplo, el ingreso del primer año es {fm(base.annual_tons)} mil t × {f_(base.freight_rate_per_ton, 2)} + {fm(base.passengers)} mil pasajeros × {f_(base.fare_per_passenger, 2)} = {fm(year1, 1)}; '
           f'descontado el costo operativo de {fm(base.operating_cost)}, queda un flujo de {fm(year1 - base.operating_cost, 1)} frente a una inversión de {fm(base.capex)}.</p>'
           f'<p>Dos cosas para leer bien el resultado. Primero, la inversión se recupera, en el caso base, en el año {payback["Base"]}, y el VPN positivo es modesto frente a lo invertido ({fm(rail["Base"]["npv"] / base.capex * 100)} % del capex). '
           f'Segundo, el modelo hace crecer los ingresos 2,5 % al año pero deja el costo operativo fijo en {fm(base.operating_cost)} durante 25 años; si el costo creciera al mismo ritmo, el VPN pasaría a {sgn(npv_opex_grows, 1)}. '
           f'Es una simplificación del modelo que el siguiente paso resuelve con una curva de costos; por ahora el caso base queda cerca del equilibrio si los costos suben al ritmo de los ingresos.</p>'
           f'<p>En la proyección territorial, la mediana del índice a 10 años es {fm(mc[-1]["p50"], 1)} (el crecimiento supuesto de 3,5 % daría cerca de 132 sin ruido), y el rango entre p05 y p95 va de {fm(mc[-1]["p05"], 1)} a {fm(mc[-1]["p95"], 1)}: '
           f'la volatilidad de 12 % que se supuso pesa casi tanto como el crecimiento.</p>')
    lim = limites(['El ferrocarril es un modelo conceptual: no incluye impuestos, estructura de deuda, ramp-up de carga y pasajeros, ingresos auxiliares, riesgo de construcción, cronograma del capex, terminales ni costos de montaña.',
                   'La recuperación simple de la Fig. 1 no sustituye al VPN.',
                   'La proyección no incorpora ciclos, correlación espacial ni rupturas estructurales. Sus percentiles son cuantiles de escenarios, no intervalos de confianza.',
                   'El cribado topográfico usa modelos globales de 30 m para cribado regional. No hay corredor definido ni diseño de ingeniería, y la pendiente del terreno no es la de diseño de la vía.'])
    fi = anatomia_fig('desarrollo-territorial', 'Ilustración · Tres cargas frente al equilibrio',
                      f'Ilustración del modelo. Cada vagón lleva una carga proporcional a las toneladas anuales de su escenario; el poste de al lado marca la carga de equilibrio del caso base ({fm(tons_be)} mil toneladas). El escenario pesimista también supone crecimiento cero, así que el poste es una referencia del caso base y no su propio equilibrio.',
                      ['Escenario', 'Toneladas al año (miles)', 'Crecimiento anual', 'VPN'], [[k, fm(R['territorial']['toneladas'][k]), f_(R['territorial']['crecimiento'][k] * 100, 1) + ' %', sgn(rail[k]['npv'])] for k in rail])
    cuerpo = seccion('Qué muestran los números', aviso() + hall) + seccion('Los gráficos', fi + f1 + f2 + f3) + seccion('Qué dicen los números', est) + seccion('Supuestos y alcance', lim) + cierre('desarrollo-territorial', '01-territorial-development', 'Desarrollo territorial y económico')
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
           f', porque el término independiente es −3,2. Y la señal de grafo, con el mayor peso (1,55), es la que más mueve la decisión: bajarla de 0,8 a 0,2 reduce la probabilidad en {abs(cf["delta"]) * 100:.0f} puntos. Los pesos son parámetros de partida del modelo; el siguiente paso es calibrarlos con datos históricos.</p>')
    lim = limites(['Trabaja con datos simulados, así que no almacena datos personales.',
                   'La simulación es Bernoulli independiente: ignora agrupamiento de casos, recuperaciones, exposición variable, errores de detección y cambios de composición.',
                   'Los pesos del puntaje son parámetros de partida y se calibrarán con datos históricos y backtesting. La probabilidad que produce es una puntuación del modelo, no una tasa observada.',
                   'Aún no incorpora el costo de los falsos positivos ni el de la verificación reforzada. Para uso real se requieren datos con permisos, calibración, backtesting y revisión de sesgos y privacidad.'])
    fi = anatomia_fig('fraude-identidad', 'Ilustración · Seis señales y un reloj',
                      f'Ilustración del modelo. Cada corredera es una señal de la solicitud de ejemplo (de 0 a 1) y el reloj marca la probabilidad que resulta: {f_(sc0["fraud_probability"] * 100, 0)} %, en la zona de revisión (desde 65 %). El marcador tenue muestra el contrafactual: con la señal del grafo en 0,2 la probabilidad baja a {f_(cf["after"]["fraud_probability"] * 100, 0)} %.',
                      ['Señal', 'Valor en el ejemplo', 'Peso'], [[n, f_(v, 1), f_(w, 2)] for n, w, v in WEIGHTS])
    cuerpo = seccion('Qué muestran los números', aviso() + hall) + seccion('Los gráficos', fi + f1 + f2 + f3) + seccion('Qué dicen los números', est) + seccion('Supuestos y alcance', lim) + cierre('fraude-identidad', '02-fraud-identity', 'Fraude, identidad y KYC')
    page('fraude-identidad', 'Fraude, identidad y KYC: resultados',
         'Combinar anomalías, grafos de relaciones y señales de dispositivo para detectar identidades sintéticas. Aquí, los resultados de un ejercicio con datos simulados.', cuerpo)


# ---------------- 03 ----------------
def pg_judicial():
    nodes = [('a', 'Fuentes públicas\nautorizadas', 'rs-n1'), ('b', 'Procedencia\ny trazabilidad', 'rs-n1'), ('c', 'Normalización', 'rs-n1'), ('d', 'Resolución\nde entidades', 'rs-n2'),
             ('e', 'Eventos\nprocesales', 'rs-n2'), ('f', 'Grafo de\nrelaciones', 'rs-n2'), ('g', 'Modelos de\nduración', 'rs-n3'), ('h', 'Exposición\ny contexto', 'rs-n3'), ('i', 'Revisión\nhumana', 'rs-n4'), ('j', 'Reporte\nauditable', 'rs-n4')]
    f = figure(flow('Método propuesto para la analítica judicial', 'Diez pasos en cuatro filas: de las fuentes públicas autorizadas al reporte auditable, con revisión humana antes del resultado.', nodes, cols=5),
               'Fig. 1 · Cómo se propone trabajar', 'Esquema del método propuesto: diez pasos, con revisión humana antes de cualquier resultado.',
               ['Paso', 'Qué hace'], [['Fuentes públicas autorizadas', 'Solo fuentes con permiso y procedencia.'], ['Procedencia y trazabilidad', 'Cada dato conserva su origen y su control de cambios.'], ['Normalización', 'Formatos y nombres comparables.'],
                                      ['Resolución de entidades', 'Identificar personas jurídicas con salvaguardas.'], ['Eventos procesales', 'Taxonomía de procesos y eventos.'], ['Grafo de relaciones', 'Proceso, parte, evento y jurisdicción.'],
                                      ['Modelos de duración', 'Tiempo hasta hitos procesales.'], ['Exposición y contexto', 'Estimación probabilística por escenario.'], ['Revisión humana', 'Obligatoria antes de cualquier resultado.'], ['Reporte auditable', 'Con la evidencia que lo respalda.']])
    cartera = ('<ol class="rs-lista">' + ''.join(f'<li>{x}</li>' for x in ['Taxonomía de procesos y eventos judiciales.', 'Pipeline de datos públicos con procedencia y control de cambios.', 'Resolución de entidades de personas jurídicas, con salvaguardas.',
                                                                               'Modelo de duración y supervivencia hasta hitos procesales.', 'Estimación probabilística de exposición económica por escenario.', 'Grafo de conocimiento proceso–parte–evento–jurisdicción.',
                                                                               'Motor de alertas por cambio material, no por perfilamiento sensible.']) + '</ol>')
    estado = ('<p class="rs-aviso"><strong>En diseño.</strong> Esta propuesta define el método y su cartera inicial. El siguiente paso es un ejercicio reproducible; mientras tanto, la página presenta el método, y sus resultados '
              'se publicarán aquí con el mismo formato que los otros programas.</p>')
    lim = limites(['No se automatizan conclusiones legales ni decisiones adversas sobre personas.', 'Requiere revisión jurídica, protección de datos y revisión humana en cada resultado.', 'Ningún resultado se presenta como conclusión automática.'])
    fi = anatomia_fig('riesgo-judicial', 'Ilustración · La cinta del método',
                      'Ilustración del método propuesto: los documentos avanzan por cinco estaciones y la barrera final solo se levanta con la revisión humana, antes de que haya un reporte.',
                      ['Estación', 'Qué representa'], [['Fuentes', 'Solo fuentes públicas con permiso y procedencia.'], ['Procedencia', 'Cada dato conserva su origen y su control de cambios.'], ['Normalización', 'Formatos y criterios comunes.'], ['Entidades y grafo', 'Resolución de entidades y relaciones entre proceso, parte y evento.'], ['Revisión humana', 'Obligatoria antes de cualquier resultado.']])
    cuerpo = seccion('Estado de la propuesta', estado) + seccion('El método propuesto', fi + f + '<h3 class="rs-sub">Cartera inicial</h3>' + cartera) + seccion('Principios de uso', lim) + cierre('riesgo-judicial', '03-judicial-risk', 'Riesgo y analítica judicial')
    page('riesgo-judicial', 'Riesgo y analítica judicial: método',
         'Dar trazabilidad a las fuentes, resolver entidades y estimar exposición a procesos judiciales, con revisión humana de cada resultado. Aquí, el método propuesto y su cartera inicial.', cuerpo)


# ---------------- 04 ----------------
def pg_agro():
    a = Plot('VPN del proyecto según el precio de venta', f'Línea del VPN para precios de 1,5 a 6 millones de COP por tonelada; cruza el cero cerca de {f_(price_be, 1)} y el caso rediseñado está en {f_(ap.sale_price_mcop_ton, 1)}.',
             (1.5, 6.0), (min(agro_price), max(agro_price)), xlabel='Precio de venta (millones de COP por tonelada)', xticks=[2, 3, 4, 5, 6], xfmt=lambda v: f_(v, 0))
    a.line(prices, agro_price, 'rs-b')
    a.dot(ap.sale_price_mcop_ton, a0['npv_mcop'], 'rs-c', f'caso rediseñado · {f_(ap.sale_price_mcop_ton, 1)}', dx=12, dy=26)
    a.dot(price_be, 0, 'rs-b', f'equilibrio · {f_(price_be, 1)}', dx=-10, dy=-14)
    f1 = figure(a.svg(), 'Fig. 1 · Qué precio necesita el proyecto', f'VPN en millones de COP constantes, con los demás parámetros del caso rediseñado iguales. Con {f_(ap.sale_price_mcop_ton, 1)} el VPN es {sgn(a0["npv_mcop"])}; el equilibrio está cerca de {f_(price_be, 1)}, apenas {f_((1 - price_be / ap.sale_price_mcop_ton) * 100, 0)} % por debajo.',
                ['Precio (M COP/t)', 'VPN (M COP)'], [[f_(x, 2), sgn(v)] for x, v in zip(prices, agro_price) if round(x * 4) % 2 == 0])
    sens = {k: v for k, v in agro_cases.items() if k != 'Ejercicio inicial'}
    rows = [(k, v, 'rs-neg' if v < 0 else 'rs-pos') for k, v in sens.items()]
    f2 = figure(hbars('VPN del caso rediseñado y sus variaciones', 'Barras horizontales del VPN en millones de COP para el caso rediseñado y siete variaciones; las que reducen precio, rendimiento o suben el CAPEX son negativas.',
                      rows, lambda v: sgn(v), xdom=(min(v for _, v, _ in rows) * 1.25, max(v for _, v, _ in rows) * 1.12), xlabel='VPN (millones de COP constantes)'),
                'Fig. 2 · Sensibilidad del caso', 'Variaciones de un parámetro a la vez sobre el caso rediseñado. Se omite el costo de capital: con flujos negativos, descontar más reduce las pérdidas y daría una señal engañosa.',
                ['Escenario', 'VPN (M COP)'], [[k, sgn(v)] for k, v in sens.items()])
    d = Plot('Participación de los productores tras una ronda de capital', 'Curva de la participación de productores, que parte de 55 %, según el capital nuevo que entra a un valor previo de 100.',
             (0, 100), (30, 60), xlabel='Capital nuevo (unidades monetarias, valor previo = 100)', ylabel='Participación de productores (%)', xticks=[0, 25, 50, 75, 100], yticks=[30, 40, 50, 60])
    d.line(rounds, dil, 'rs-b')
    for i, (r, v) in enumerate(zip(rounds, dil)):
        d.dot(r, v, 'rs-b', f'{f_(v, 1)} %', dx=(-8 if i == len(rounds) - 1 else 8), dy=-10)
    f3 = figure(d.svg(), 'Fig. 3 · Dilución de los productores', 'Estructura inicial hipotética: productores 55 %, inversionistas 30 %, bolsa de incentivos 10 %, fundadores 5 %. Sin aporte propio de los productores a la ronda.',
                ['Capital nuevo', 'Participación de productores'], [[str(r), f'{f_(v, 1)} %'] for r, v in zip(rounds, dil)])
    tdep = table(['Departamento', 'Cadenas candidatas', 'Transformación', 'Logística'], [[x['departamento'], x['cadenas_candidatas'], x['transformacion'], x['logistica']] for x in deptos])
    hall = cifras([(sgn(a0['npv_mcop']) + ' M', f'VPN del caso rediseñado en millones de COP, frente a {sgn(a_ini["npv_mcop"])} del ejercicio inicial. Es un caso de diseño con supuestos explícitos, no una proyección.'),
                   (f'{payroll_share * 100:.0f} %'.replace('.', ','), f'peso de la nómina ({fm(a0["annual_staff_cost_mcop"])}) sobre el ingreso del primer año ({fm(a0["year1"]["revenue_mcop"])}); en el ejercicio inicial era {a_ini["annual_staff_cost_mcop"] / a_ini["year1"]["revenue_mcop"] * 100:.0f} %. El EBITDA del año 1 es {sgn(a0["year1"]["ebitda_mcop"])}.'),
                   (f'{f_(price_be, 1)} M/t · {f_(yield_be, 1)} t/ha', f'precio y rendimiento mínimos para equilibrar. El caso rediseñado los supera en {f_((1 - price_be / ap.sale_price_mcop_ton) * 100, 0)} % y {f_((1 - yield_be / ap.yield_ton_ha) * 100, 0)} %: son las dos variables que un piloto en campo debe confirmar.')])
    ini_tbl = table(['Parámetro', 'Ejercicio inicial', 'Caso rediseñado', 'Supuesto del cambio'],
                    [['Hectáreas', fm(ap_ini.hectares), fm(ap.hectares), 'El máximo que cabe bajo el tope de agua.'],
                     ['Rendimiento (t/ha)', f_(ap_ini.yield_ton_ha, 0), f_(ap.yield_ton_ha, 0), 'Producción tecnificada.'],
                     ['Precio (M COP/t)', f_(ap_ini.sale_price_mcop_ton, 1), f_(ap.sale_price_mcop_ton, 1), 'Producto con algo de transformación.'],
                     ['Personal por cuadrilla', fm(ap_ini.staff_per_rotation), fm(ap.staff_per_rotation), 'Riego y mecanización reducen la mano de obra por tonelada.'],
                     ['Agua (m³/t)', fm(ap_ini.water_m3_per_ton), fm(ap.water_m3_per_ton), 'Riego por goteo.'],
                     ['VPN (M COP)', sgn(a_ini['npv_mcop']), sgn(a0['npv_mcop']), 'Resultado.']])
    est = (f'<p>El ejercicio inicial del repositorio ({fm(ap_ini.hectares)} ha, {ap_ini.yield_ton_ha:g} t/ha, {f_(ap_ini.sale_price_mcop_ton, 1)} millones por tonelada) daba un VPN de {sgn(a_ini["npv_mcop"])} millones: la nómina consumía {a_ini["annual_staff_cost_mcop"] / a_ini["year1"]["revenue_mcop"] * 100:.0f} % del ingreso del primer año y el precio de equilibrio era {f_(price_be_ini, 1)}, más del doble del base. Ese resultado obligaba a rediseñar antes de buscar capital, y eso es lo que se hizo aquí.</p>'
           f'<p>El caso rediseñado cambia cinco supuestos, todos en la dirección que propone el proyecto (tecnificación, riego eficiente, transformación) y todos visibles en la tabla. El ingreso del primer año sube a {fm(a0["year1"]["revenue_mcop"])}, la nómina de {a0["headcount_assumed"]} personas pesa {payroll_share * 100:.0f} % y el EBITDA del año 1 es {sgn(a0["year1"]["ebitda_mcop"])}. El VPN es de {sgn(a0["npv_mcop"])} millones y la suma de los flujos a {len(a0["cashflows_mcop"]) - 1} años es de {sgn(sum(a0["cashflows_mcop"]))} millones. El uso de agua, {fm(a0["annual_water_m3"])} m³, queda dentro del tope de {fm(ap.max_water_m3_year)}.</p>'
           f'<p>Los dos supuestos que más pesan son precio y rendimiento. El equilibrio está en {f_(price_be, 1)} millones por tonelada y {f_(yield_be, 1)} t/ha: si el precio o el rendimiento caen 10 %, el VPN pasa a {sgn(agro_cases["Precio −10 %"])} y {sgn(agro_cases["Rendimiento −10 %"])}. Por eso el primer paso es validarlos en campo con un piloto, antes de comprometer capital.</p>'
           f'<p>La curva de la Fig. 1 cambia de pendiente cerca de {f_(price_ebitda0, 1)} millones por tonelada: desde ahí el EBITDA del primer año es positivo y el modelo empieza a restar el impuesto de 35 %, que solo aplica a EBITDA positivo. Es una simplificación declarada del modelo, no un efecto del proyecto.</p>'
           f'<p>En la dilución, una ronda de 50 unidades sobre un valor previo de 100 baja a los productores de 55 % a {f_(dil[3], 1)} % si no aportan capital; la mecánica es aritmética, no una recomendación de estructura.</p>')
    lim = limites(['Los cinco supuestos del caso rediseñado son decisiones de diseño del proyecto y se validan en campo. Los parámetros del modelo son ilustrativos: no provienen de un estudio de mercado ni de costos observados en Colombia, y la nómina no está validada legalmente.',
                   'La rotación 15/15 se modela con dos cuadrillas; la jornada laboral requiere su propia validación.',
                   'Los impuestos son una simplificación (sobre el EBITDA positivo): no hay deuda, depreciación ni arrastre de pérdidas.',
                   'Alcance: no es una valoración, una oferta de acciones ni asesoría legal. Cualquier mecanismo patrimonial requiere acuerdos jurídicos y el consentimiento de los productores.',
                   'La tabla de departamentos lista cadenas candidatas para estudiar; el orden no es un ranking.'])
    fi = anatomia_fig('agroindustria', 'Ilustración · Ingresos frente a costos del año 1',
                      'Ilustración del modelo. En cada estación, el pilar es el ingreso del primer año y la pila de bloques son sus costos (fijos, nómina, campo y variables); la regla sobre el pilar marca el nivel del ingreso. Alturas proporcionales: una unidad de dibujo son 80 millones de COP.',
                      ['Caso', 'Ingresos', 'Costos', 'Margen del año 1'], [[n, fm(d['ingresos']), fm(sum(v for kk, v in d.items() if kk != 'ingresos')), sgn(d['ingresos'] - sum(v for kk, v in d.items() if kk != 'ingresos'))] for n, d in (('Ejercicio inicial', R['agro']['year1']['inicial']), ('Caso rediseñado', R['agro']['year1']['diseno']))])
    cuerpo = (seccion('Qué muestran los números', aviso() + hall) + seccion('Los gráficos', fi + f1 + f2 + f3) + seccion('Qué dicen los números', est + ini_tbl)
              + seccion('Cadenas candidatas por departamento', f'<p>Punto de partida para estudiar dónde probar la propuesta: {len(deptos)} departamentos con las cadenas productivas que se consideraría analizar.</p>{tdep}', 'departamentos')
              + seccion('Supuestos y alcance', lim) + cierre('agroindustria', '04-agroindustry-farmer-ownership', 'Agroindustria tecnificada y propiedad campesina'))
    page('agroindustria', 'Agroindustria tecnificada y propiedad campesina: resultados',
         'Estudiar si el productor puede participar como proveedor, trabajador o copropietario con derechos exigibles. Aquí, un caso rediseñado a partir de un ejercicio inicial negativo, con sus supuestos y su margen, más agua y dilución.', cuerpo)


# ---------------- 05 ----------------
def pg_integridad():
    d = R['integridad']['digests']
    short = lambda h: '#' + h[:12] + '…'
    nodes = [('g', 'Inicio\n#' + '0' * 12 + '…', 'rs-n1'), ('e0', 'Evento 0 · registrado\n' + short(d[0]), 'rs-n2'), ('e1', 'Evento 1 · verificado\n' + short(d[1]), 'rs-n2'), ('r', 'Raíz del árbol\n' + short(trusted['root']), 'rs-n3')]
    f1 = figure(flow('Cadena de eventos con huellas encadenadas', 'Cuatro cajas: el inicio, dos eventos cuyas huellas dependen de la anterior, y la raíz del árbol que resume toda la cadena.', nodes, cols=4, node_h=70),
                'Fig. 1 · Cómo se encadena el expediente', 'Cada evento guarda la huella SHA-256 del anterior: cambiar cualquiera cambia todas las siguientes. La raíz resume toda la cadena. Contrato y datos de prueba.',
                ['Pieza', 'Huella (primeros 12 caracteres)'], [['Evento 0', d[0][:12]], ['Evento 1', d[1][:12]], ['Raíz', trusted['root'][:12]]])
    ok = lambda b: 'Coincide' if b else 'No coincide'
    f0 = anatomia_fig('integridad', 'Ilustración · El registro como una máquina',
                      'Ilustración del modelo. La hilera de atrás es el registro original y la de adelante el reescrito: ambas encadenan bien por dentro. El soporte del fondo es el punto de control externo: su émbolo baja al orificio de la raíz del original y apoya sobre la tapa del reescrito, cuya raíz es otra. Las huellas son las del ejemplo.',
                      ['Hilera', 'Raíz', 'Frente al punto de control externo'],
                      [['Original', trusted['root'][:6], 'Coincide'], ['Reescrito', 'distinta', 'No coincide']])
    ver_rows = [['El registro original frente al punto de control externo', ok(ver['original']), 'Es la verificación que debe pasar.'],
                ['Una historia reescrita (se cambió «registrado» por «pagado»), frente a su propio punto de control', ok(ver['forged_self']), 'Es internamente consistente: pasa su propia verificación.'],
                ['La misma historia reescrita, frente al punto de control externo original', ok(ver['forged_ext']), 'Aquí se detecta la reescritura.'],
                ['Una historia truncada (sin el último evento), frente al punto de control externo', ok(ver['truncated']), 'También se detecta.']]
    f2 = ('<figure class="rs-fig"><figcaption class="rs-title">Tabla 1 · Cuatro verificaciones sobre el mismo ejemplo</figcaption>'
          + table(['Qué se comprueba', 'Resultado', 'Qué significa'], ver_rows) + '<p class="rs-note">Ejemplo con dos eventos de un contrato de prueba, ejecutado con el código del programa.</p></figure>')
    comp = table(['Proyecto', 'Resultado propuesto', 'Control y límite'], componentes)
    hall = cifras([('Sí', 'el registro reescrito pasa su propia verificación. Por eso el diseño exige una referencia externa.'),
                   ('2 de 2', 'las alteraciones del ejemplo (reescribir y truncar) se detectan al compararlas con un punto de control obtenido fuera de quien opera el registro.'),
                   ('Integridad', 'lo que acredita la cadena: que el registro no cambió. La veracidad de cada documento se verifica aparte, con revisión humana.')])
    est = ('<p>La idea central del programa cabe en la tabla 1. Una cadena de huellas permite detectar que algo cambió, pero solo si alguien guardó antes una referencia confiable de cómo era. '
           'Quien opera el registro puede reescribir la historia y recalcular todas las huellas: el resultado será internamente impecable. Lo que lo delata es la comparación con un punto de control que no controla el operador, como una copia en poder de un testigo independiente.</p>'
           '<p>Por eso el diseño no se apoya en «usar cadena de bloques» sino en tres cosas: una referencia externa, separación de funciones entre quien propone, verifica y autoriza, y un registro que conserva la historia agregando eventos en vez de borrarla. '
           'Y por eso la hipótesis del programa es falsable: frente al expediente convencional, estos controles reducirían las alteraciones no detectadas sin volver inviable el trámite. No se presume que reduzcan la corrupción.</p>')
    lim = limites(['Etapa actual: laboratorio de referencia. Demuestra el mecanismo; firmas, persistencia, identidad y cadena de bloques son fases posteriores.', 'Un punto de control solo es confiable si se obtiene y autentica fuera de quien opera el registro.',
                   'El registro no prueba que un documento sea verdadero, ni fecha, ni que la historia esté completa más allá de lo que el punto de control comprometió.',
                   'Los identificadores de hito son registros de control no transferibles: no son moneda ni un derecho negociable.', 'Los convenios con entidades y el despliegue son fases posteriores.'])
    cuerpo = (seccion('Qué muestran los números', aviso() + hall) + seccion('El ejemplo', f0 + f1 + f2) + seccion('Qué dicen los números', est)
              + seccion('Los diez componentes propuestos y sus límites', f'<p>Cada componente nombra su resultado y también lo que no puede garantizar.</p>{comp}', 'componentes')
              + seccion('Supuestos y alcance', lim) + cierre('integridad-publica', '05-public-integrity', 'Integridad pública verificable'))
    page('integridad-publica', 'Integridad pública verificable: resultados',
         'Un expediente verificable por contrato e hito para dar trazabilidad a la ejecución de recursos públicos. Aquí, un ejemplo que muestra qué detecta una cadena de huellas y cómo una referencia externa cierra el hueco.', cuerpo)


# ---------------- portada y CSS ----------------
CARDS = {1: ('desarrollo-territorial', '01-territorial-development', 'Desarrollo territorial y económico', f'{sgn(rail["Base"]["npv"])} (rango {sgn(rail["Pesimista"]["npv"])} a {sgn(rail["Optimista"]["npv"])})',
             'VPN del ferrocarril conceptual en los escenarios base, pesimista y optimista; el índice territorial sube de 100 a una mediana de 131 en diez años. Ejercicio de modelado.', 'Ver resultados'),
         2: ('fraude-identidad', '02-fraud-identity', 'Fraude, identidad y KYC', f'{f_(fraud["Controlado"]["expected"] / 1e6, 1)} a {f_(fraud["Estrés"]["expected"] / 1e6, 0)} M',
             'costo anual esperado del fraude en COP, del escenario controlado al de estrés: es lo que el sistema busca reducir. Simulación del programa.', 'Ver resultados'),
         3: ('riesgo-judicial', '03-judicial-risk', 'Riesgo y analítica judicial', 'En diseño', 'Método propuesto para analizar procesos judiciales, con revisión humana antes de cada resultado.', 'Ver el método'),
         4: ('agroindustria', '04-agroindustry-farmer-ownership', 'Agroindustria tecnificada y propiedad campesina', sgn(a0['npv_mcop']) + ' M',
             f'VPN del caso rediseñado, frente a {sgn(a_ini["npv_mcop"])} M del ejercicio inicial. Rentable con precio desde {f_(price_be, 1)} M/t y rendimiento desde {f_(yield_be, 1)} t/ha.', 'Ver resultados'),
         5: ('integridad-publica', '05-public-integrity', 'Integridad pública verificable', 'Sí · 2 de 2', 'las dos alteraciones del ejemplo, reescribir y truncar, se detectan con un punto de control externo.', 'Ver resultados')}


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
    open(os.path.join(SITE, 'proyectos', 'figuras', 'anatomia.css'), 'w', encoding='utf-8').write(open(os.path.join(ROOT, 'site-results', 'anatomia', 'out', 'anatomia.css'), encoding='utf-8').read())
    print(f'Páginas y cifras escritas en {SITE}/proyectos (commit de los programas {COMMIT})')
else:
    print('Resultados calculados en site-results/out/resultados.json (sin carpeta de sitio no se escriben páginas).')
