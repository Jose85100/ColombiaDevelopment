"""Gráficos SVG mínimos para colombiarisk.com/proyectos.

Sin librerías y sin atributos style (la política de seguridad del sitio los bloquea): todo el color vive en clases
que define proyectos/figuras/resultados.css con las variables de tema del sitio (claro y oscuro).
"""
from html import escape as esc
from math import ceil, floor, log10

W, H = 720, 380
ML, MR, MT, MB = 64, 24, 20, 56


def nice_ticks(lo, hi, n=5):
    if lo == hi:
        hi = lo + 1
    span = hi - lo
    step = 10 ** floor(log10(span / n))
    for m in (1, 2, 2.5, 5, 10):
        if span / (step * m) <= n:
            step *= m
            break
    a = floor(lo / step) * step
    b = ceil(hi / step) * step
    out, v = [], a
    while v <= b + step * 1e-9:
        out.append(round(v, 10))
        v += step
    return out


def fmt_es(v, dec=0):
    s = f"{v:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


class Plot:
    def __init__(self, title, desc, xdom, ydom, xlabel='', ylabel='', xfmt=lambda v: fmt_es(v), yfmt=lambda v: fmt_es(v), xticks=None, yticks=None, w=W, h=H):
        self.w, self.h = w, h
        self.title, self.desc = title, desc
        self.x0, self.x1 = xdom
        yt = yticks or nice_ticks(*ydom)
        self.yt = yt
        self.y0, self.y1 = yt[0], yt[-1]
        self.xt = xticks or nice_ticks(self.x0, self.x1)
        self.xfmt, self.yfmt = xfmt, yfmt
        self.parts = []
        self.xlabel, self.ylabel = xlabel, ylabel
        self._frame()

    def X(self, v):
        return ML + (v - self.x0) / (self.x1 - self.x0) * (self.w - ML - MR)

    def Y(self, v):
        return self.h - MB - (v - self.y0) / (self.y1 - self.y0) * (self.h - MB - MT)

    def _frame(self):
        p = self.parts
        for t in self.yt:
            y = self.Y(t)
            p.append(f'<line class="rs-grid{" rs-zero" if t == 0 else ""}" x1="{ML}" x2="{self.w - MR}" y1="{y:.1f}" y2="{y:.1f}"/>')
            p.append(f'<text class="rs-tick" x="{ML - 8}" y="{y + 4:.1f}" text-anchor="end">{esc(self.yfmt(t))}</text>')
        for t in self.xt:
            x = self.X(t)
            p.append(f'<line class="rs-tickmark" x1="{x:.1f}" x2="{x:.1f}" y1="{self.h - MB}" y2="{self.h - MB + 5}"/>')
            p.append(f'<text class="rs-tick" x="{x:.1f}" y="{self.h - MB + 20}" text-anchor="middle">{esc(self.xfmt(t))}</text>')
        p.append(f'<line class="rs-axis" x1="{ML}" x2="{self.w - MR}" y1="{self.h - MB}" y2="{self.h - MB}"/>')
        if self.xlabel:
            p.append(f'<text class="rs-axlabel" x="{(ML + self.w - MR) / 2:.0f}" y="{self.h - 10}" text-anchor="middle">{esc(self.xlabel)}</text>')
        if self.ylabel:
            p.append(f'<text class="rs-axlabel" transform="translate(16 {(MT + self.h - MB) / 2:.0f}) rotate(-90)" text-anchor="middle">{esc(self.ylabel)}</text>')

    def line(self, xs, ys, cls, label=None, label_dx=6, label_dy=4, label_at=-1):
        pts = ' '.join(f'{self.X(x):.1f},{self.Y(y):.1f}' for x, y in zip(xs, ys))
        self.parts.append(f'<polyline class="rs-line {cls}" points="{pts}"/>')
        if label:
            x, y = self.X(xs[label_at]), self.Y(ys[label_at])
            anchor = 'end' if label_dx <= 0 else 'start'
            self.parts.append(f'<text class="rs-direct {cls}" x="{x + label_dx:.1f}" y="{y + label_dy:.1f}" text-anchor="{anchor}">{esc(label)}</text>')

    def band(self, xs, lo, hi, cls):
        up = [f'{self.X(x):.1f},{self.Y(v):.1f}' for x, v in zip(xs, hi)]
        dn = [f'{self.X(x):.1f},{self.Y(v):.1f}' for x, v in reversed(list(zip(xs, lo)))]
        self.parts.append(f'<polygon class="rs-band {cls}" points="{" ".join(up + dn)}"/>')

    def vline(self, x, label, cls='rs-ref'):
        xx = self.X(x)
        self.parts.append(f'<line class="rs-refline {cls}" x1="{xx:.1f}" x2="{xx:.1f}" y1="{MT}" y2="{self.h - MB}"/>')
        self.parts.append(f'<text class="rs-reflabel" x="{xx + 6:.1f}" y="{MT + 12}">{esc(label)}</text>')

    def hline(self, y, label, cls='rs-ref'):
        yy = self.Y(y)
        self.parts.append(f'<line class="rs-refline {cls}" x1="{ML}" x2="{self.w - MR}" y1="{yy:.1f}" y2="{yy:.1f}"/>')
        self.parts.append(f'<text class="rs-reflabel" x="{self.w - MR - 4}" y="{yy - 6:.1f}" text-anchor="end">{esc(label)}</text>')

    def dot(self, x, y, cls, label=None, dx=8, dy=-8):
        self.parts.append(f'<circle class="rs-dot {cls}" cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="5"/>')
        if label:
            self.parts.append(f'<text class="rs-direct {cls}" x="{self.X(x) + dx:.1f}" y="{self.Y(y) + dy:.1f}" text-anchor="{"end" if dx < 0 else "start"}">{esc(label)}</text>')

    def bars(self, xs, ys, cls_fn, width=34, labels=True, fmt=None):
        for x, y in zip(xs, ys):
            x0, y0, y1 = self.X(x) - width / 2, self.Y(max(y, 0)), self.Y(min(y, 0))
            self.parts.append(f'<rect class="rs-bar {cls_fn(x, y)}" x="{x0:.1f}" y="{y0:.1f}" width="{width}" height="{max(y1 - y0, 1):.1f}"/>')
            if labels:
                ty = y0 - 6 if y >= 0 else y1 + 14
                self.parts.append(f'<text class="rs-value" x="{self.X(x):.1f}" y="{ty:.1f}" text-anchor="middle">{esc((fmt or self.yfmt)(y))}</text>')

    def svg(self):
        return (f'<svg class="rs-svg" viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="t d" xmlns="http://www.w3.org/2000/svg">'
                f'<title id="t">{esc(self.title)}</title><desc id="d">{esc(self.desc)}</desc>' + ''.join(self.parts) + '</svg>')


def hbars(title, desc, rows, xfmt, xdom=None, w=W, label_w=190, xlabel='', refs=()):
    """rows: [(etiqueta, valor, clase)]. Barras horizontales con cero y etiquetas directas."""
    vals = [r[1] for r in rows]
    lo, hi = xdom or (min(0, min(vals)), max(0, max(vals)))
    ticks = nice_ticks(lo, hi, 5)
    lo, hi = ticks[0], ticks[-1]
    rowh = 44
    top = MT + (22 if refs else 0)
    h = top + rowh * len(rows) + 56
    x = lambda v: label_w + (v - lo) / (hi - lo) * (w - label_w - 40)
    p = []
    for t in ticks:
        p.append(f'<line class="rs-grid{" rs-zero" if t == 0 else ""}" x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{MT}" y2="{h - 50}"/>')
        p.append(f'<text class="rs-tick" x="{x(t):.1f}" y="{h - 32}" text-anchor="middle">{esc(xfmt(t))}</text>')
    for i, (lab, v, cls) in enumerate(rows):
        y = top + i * rowh + 6
        a, b = sorted((x(0), x(v)))
        p.append(f'<text class="rs-rowlabel" x="{label_w - 10}" y="{y + 20}" text-anchor="end">{esc(lab)}</text>')
        p.append(f'<rect class="rs-bar {cls}" x="{a:.1f}" y="{y}" width="{max(b - a, 1):.1f}" height="28"/>')
        tx = b + 8 if v >= 0 else a - 8
        anchor = 'start' if v >= 0 else 'end'
        p.append(f'<text class="rs-value" x="{tx:.1f}" y="{y + 19}" text-anchor="{anchor}">{esc(xfmt(v))}</text>')
    for xv, lab in refs:
        p.append(f'<line class="rs-refline rs-ref" x1="{x(xv):.1f}" x2="{x(xv):.1f}" y1="{MT}" y2="{h - 50}"/>')
        p.append(f'<text class="rs-reflabel" x="{x(xv) + 6:.1f}" y="{MT + 12}">{esc(lab)}</text>')
    if xlabel:
        p.append(f'<text class="rs-axlabel" x="{(label_w + w - 40) / 2:.0f}" y="{h - 8}" text-anchor="middle">{esc(xlabel)}</text>')
    return (f'<svg class="rs-svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d" xmlns="http://www.w3.org/2000/svg">'
            f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>' + ''.join(p) + '</svg>')


def boxes(title, desc, rows, xfmt, xdom, w=W, label_w=170, xlabel='', marks=()):
    """rows: [(etiqueta, p05, p25, p50, p75, p95, clase, esperado)]. Cajas horizontales con bigotes y valor esperado."""
    ticks = nice_ticks(*xdom, 5)
    lo, hi = ticks[0], ticks[-1]
    rowh = 78
    h = MT + rowh * len(rows) + 56
    x = lambda v: label_w + (v - lo) / (hi - lo) * (w - label_w - 40)
    p = []
    for t in ticks:
        p.append(f'<line class="rs-grid" x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{MT}" y2="{h - 50}"/>')
        p.append(f'<text class="rs-tick" x="{x(t):.1f}" y="{h - 32}" text-anchor="middle">{esc(xfmt(t))}</text>')
    for i, (lab, a, q1, m, q3, b, cls, ex) in enumerate(rows):
        yc = MT + i * rowh + rowh / 2
        p.append(f'<text class="rs-rowlabel" x="{label_w - 10}" y="{yc + 4:.1f}" text-anchor="end">{esc(lab)}</text>')
        p.append(f'<line class="rs-whisker {cls}" x1="{x(a):.1f}" x2="{x(b):.1f}" y1="{yc:.1f}" y2="{yc:.1f}"/>')
        for v in (a, b):
            p.append(f'<line class="rs-whisker {cls}" x1="{x(v):.1f}" x2="{x(v):.1f}" y1="{yc - 8:.1f}" y2="{yc + 8:.1f}"/>')
        p.append(f'<rect class="rs-box {cls}" x="{x(q1):.1f}" y="{yc - 14:.1f}" width="{max(x(q3) - x(q1), 1):.1f}" height="28"/>')
        p.append(f'<line class="rs-median" x1="{x(m):.1f}" x2="{x(m):.1f}" y1="{yc - 14:.1f}" y2="{yc + 14:.1f}"/>')
        p.append(f'<path class="rs-expected {cls}" d="M{x(ex):.1f} {yc + 22:.1f} l-5 8 h10 z"/>')
        p.append(f'<text class="rs-value" x="{x(b) + 8:.1f}" y="{yc + 4:.1f}">{esc(xfmt(b))}</text>')
    if xlabel:
        p.append(f'<text class="rs-axlabel" x="{(label_w + w - 40) / 2:.0f}" y="{h - 8}" text-anchor="middle">{esc(xlabel)}</text>')
    return (f'<svg class="rs-svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d" xmlns="http://www.w3.org/2000/svg">'
            f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>' + ''.join(p) + '</svg>')


def flow(title, desc, nodes, w=W, cols=None, node_h=58, gap_x=26, gap_y=34):
    """nodes: [(id, texto, clase)]; se dibujan en filas de `cols` con flechas entre vecinos en orden."""
    cols = cols or len(nodes)
    nw = (w - 2 * 12 - gap_x * (cols - 1)) / cols
    rows = ceil(len(nodes) / cols)
    h = 24 + rows * node_h + (rows - 1) * gap_y
    pos = {}
    p = []
    for i, (nid, text, cls) in enumerate(nodes):
        r, c = divmod(i, cols)
        x, y = 12 + c * (nw + gap_x), 12 + r * (node_h + gap_y)
        pos[nid] = (x, y)
        p.append(f'<rect class="rs-node {cls}" x="{x:.1f}" y="{y:.1f}" width="{nw:.1f}" height="{node_h}" rx="4"/>')
        lines = text.split('\n')
        for k, ln in enumerate(lines):
            p.append(f'<text class="rs-nodetext{" rs-nodemono" if ln.startswith("#") else ""}" x="{x + nw / 2:.1f}" y="{y + node_h / 2 + (k - (len(lines) - 1) / 2) * 16 + 4:.1f}" text-anchor="middle">{esc(ln.lstrip("#"))}</text>')
    for i in range(len(nodes) - 1):
        a, b = nodes[i][0], nodes[i + 1][0]
        (x0, y0), (x1, y1) = pos[a], pos[b]
        if abs(y0 - y1) < 1:
            p.append(f'<path class="rs-arrow" d="M{x0 + nw:.1f} {y0 + node_h / 2:.1f} H{x1 - 2:.1f}"/><path class="rs-arrowhead" d="M{x1 - 2:.1f} {y1 + node_h / 2:.1f} l-7 -4 v8 z"/>')
        else:
            p.append(f'<path class="rs-arrow" d="M{x0 + nw / 2:.1f} {y0 + node_h:.1f} V{y0 + node_h + gap_y / 2:.1f} H{x1 + nw / 2:.1f} V{y1 - 2:.1f}"/><path class="rs-arrowhead" d="M{x1 + nw / 2:.1f} {y1 - 2:.1f} l-4 -7 h8 z"/>')
    return (f'<svg class="rs-svg" viewBox="0 0 {w} {h:.0f}" role="img" aria-labelledby="t d" xmlns="http://www.w3.org/2000/svg">'
            f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>' + ''.join(p) + '</svg>')
