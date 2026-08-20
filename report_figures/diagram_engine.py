#!/usr/bin/env python3
"""Diagram engine for the OCRandCorrectionVn report figures.

Emits BOTH for every figure:
  * <name>.drawio  — native, fully editable mxGraph XML (real vertices/edges/
                     swimlanes/UML lifelines; NOT an embedded image)
  * <name>.svg     — clean vector graphic sized for insertion into Word

Adapted from OCRandCorrectionVn/glm-ocr-ui/docs/diagrams/build_diagrams.py
(the project's own diagram generator). The project file is NOT modified.
"""
import os, math, html

OUT = os.path.dirname(os.path.abspath(__file__))


def set_out(path):
    """Redirect write() to another directory (created if missing)."""
    global OUT
    OUT = path
    os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- palette
P = {
    'fe':    ('#DAE8FC', '#6C8EBF'),  # frontend  - blue
    'be':    ('#D4E1F5', '#3F61A8'),  # backend   - indigo
    'ocr':   ('#B0E3E6', '#0E8088'),  # ocr       - teal
    'ai':    ('#FFE6CC', '#D79B00'),  # ai svc    - orange
    'rag':   ('#D5E8D4', '#82B366'),  # rag       - green
    'agent': ('#E1D5E7', '#9673A6'),  # agent     - purple
    'llm':   ('#FFF2CC', '#D6B656'),  # providers - yellow
    'db':    ('#EDEDED', '#5A5A5A'),  # database  - gray
    'sec':   ('#F8CECC', '#B85450'),  # security  - red
    'ext':   ('#F5F5F5', '#999999'),  # external  - light gray
    'note':  ('#FFF2CC', '#D6B656'),
    # ── report-figure palette (consistent across Chapters 2–4) ──────────────
    'actor': ('#FFFFFF', '#33475B'),  # UML actors / boundary
    'ui':    ('#DAE8FC', '#6C8EBF'),  # presentation tier      - blue
    'api':   ('#D4E1F5', '#3F61A8'),  # Flask routes / HTTP    - indigo
    'svc':   ('#D5E8D4', '#82B366'),  # service layer          - green
    'eng':   ('#B0E3E6', '#0E8088'),  # OCR engines / adapters - teal
    'proc':  ('#FFE6CC', '#D79B00'),  # external process/model - orange
    'corr':  ('#E1D5E7', '#9673A6'),  # VI correction          - purple
    'data':  ('#EDEDED', '#5A5A5A'),  # SQLite / files         - gray
    'flow':  ('#F2F7FD', '#4B6E9C'),  # flow-chart step        - pale blue
    'dec':   ('#FFF2CC', '#D6B656'),  # decision diamond       - yellow
    'err':   ('#F8CECC', '#B85450'),  # error / security       - red
    'todo':  ('#FFFFFF', '#B85450'),  # manual-completion marker
    'plot':  ('#FFFFFF', '#33475B'),  # empty chart plotting area
    'axis':  ('#FFFFFF', '#FFFFFF'),  # invisible box, visible text (axis labels)
}

def tint(hx, t):
    r = int(hx[1:3], 16); g = int(hx[3:5], 16); b = int(hx[5:7], 16)
    r = int(r + (255 - r) * t); g = int(g + (255 - g) * t); b = int(b + (255 - b) * t)
    return '#%02X%02X%02X' % (r, g, b)

def esc(s):
    return html.escape(str(s), quote=True)

# ---------------------------------------------------------------- model
class Diagram:
    def __init__(self, name, title, w, h, subtitle=''):
        self.name = name; self.title = title; self.w = w; self.h = h
        self.subtitle = subtitle
        self.containers = []   # dict: id,x,y,w,h,title,fill,stroke,header,bodyfill,kind
        self.nodes = []        # dict: id,x,y,w,h,label,fill,stroke,shape,parent,fontsize,bold,fontcolor
        self.tables = []       # dict: id,x,y,w,title,rows,fill,stroke,rowh,header
        self.edges = []        # dict: src,dst,label,dashed,color,waypoints,srcside,dstside,arrow
        self.lifelines = []    # sequence: id,x,label,fill,stroke,hy,hh,hw,bottom
        self.messages = []     # sequence: frm,to,y,label,dashed,color,kind
        self.fragments = []    # sequence: x1,x2,y1,y2,label
        self.byid = {}
        self._llx = {}

    def container(self, id, x, y, w, h, title, key, header=34):
        fill, stroke = P[key]
        c = dict(id=id, x=x, y=y, w=w, h=h, title=title, fill=fill, stroke=stroke,
                 header=header, bodyfill=tint(fill, 0.62), kind='container')
        self.containers.append(c); self.byid[id] = c; return c

    def node(self, id, x, y, w, h, label, key, shape='round', parent=None,
             fontsize=12.5, bold=False, fontcolor='#15202B'):
        fill, stroke = P[key]
        n = dict(id=id, x=x, y=y, w=w, h=h, label=label, fill=fill, stroke=stroke,
                 shape=shape, parent=parent, fontsize=fontsize, bold=bold,
                 fontcolor=fontcolor, kind='node')
        self.nodes.append(n); self.byid[id] = n; return n

    def table(self, id, x, y, w, title, rows, key, rowh=21, header=28):
        fill, stroke = P[key]
        h = header + rowh * len(rows) + 6
        t = dict(id=id, x=x, y=y, w=w, h=h, title=title, rows=rows, fill=fill,
                 stroke=stroke, rowh=rowh, header=header, kind='table')
        self.tables.append(t); self.byid[id] = t; return t

    def edge(self, src, dst, label='', dashed=False, color='#445', waypoints=None,
             srcside=None, dstside=None, arrow='end'):
        self.edges.append(dict(src=src, dst=dst, label=label, dashed=dashed, color=color,
                               waypoints=waypoints or [], srcside=srcside, dstside=dstside,
                               arrow=arrow))

    # ---- sequence-diagram primitives (UML) ----
    def lifeline(self, id, x, label, key, hy=66, hh=46, hw=160, bottom=None):
        fill, stroke = P[key]
        self.lifelines.append(dict(id=id, x=x, label=label, fill=fill, stroke=stroke,
                                   hy=hy, hh=hh, hw=hw, bottom=bottom))
        self._llx[id] = x
        self.byid[id] = dict(x=x - hw / 2, y=hy, w=hw, h=hh)
        return id

    def message(self, frm, to, y, label='', dashed=False, color='#33475B', kind='call'):
        self.messages.append(dict(frm=frm, to=to, y=y, label=label, dashed=dashed,
                                  color=color, kind=kind))

    def fragment(self, x1, y1, x2, y2, label):
        self.fragments.append(dict(x1=x1, y1=y1, x2=x2, y2=y2, label=label))

# ---------------------------------------------------------------- geometry
def cell_rect(c):
    return c['x'], c['y'], c['w'], c['h']

def side_point(c, side, frac=0.5):
    x, y, w, h = cell_rect(c)
    if side == 'top':    return x + w * frac, y
    if side == 'bottom': return x + w * frac, y + h
    if side == 'left':   return x, y + h * frac
    if side == 'right':  return x + w, y + h * frac
    return x + w / 2, y + h / 2

def border_toward(c, px, py):
    x, y, w, h = cell_rect(c)
    cx, cy = x + w / 2, y + h / 2
    dx, dy = px - cx, py - cy
    if dx == 0 and dy == 0: return cx, cy
    sx = (w / 2) / abs(dx) if dx else 1e9
    sy = (h / 2) / abs(dy) if dy else 1e9
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s

def poly_midpoint(pts):
    if len(pts) == 1: return pts[0]
    seg = []; total = 0
    for i in range(len(pts) - 1):
        d = math.hypot(pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i][1])
        seg.append(d); total += d
    half = total / 2; acc = 0
    for i, d in enumerate(seg):
        if acc + d >= half:
            t = (half - acc) / d if d else 0
            return (pts[i][0] + (pts[i+1][0]-pts[i][0]) * t,
                    pts[i][1] + (pts[i+1][1]-pts[i][1]) * t)
        acc += d
    return pts[-1]

def edge_points(d, e):
    s = d.byid[e['src']]; t = d.byid[e['dst']]
    wps = e['waypoints']
    # start
    if e['srcside']:
        sp = side_point(s, e['srcside'])
    else:
        aim = wps[0] if wps else (t['x'] + t['w'] / 2, t['y'] + t['h'] / 2)
        sp = border_toward(s, aim[0], aim[1])
    # end
    if e['dstside']:
        ep = side_point(t, e['dstside'])
    else:
        aim = wps[-1] if wps else (s['x'] + s['w'] / 2, s['y'] + s['h'] / 2)
        ep = border_toward(t, aim[0], aim[1])
    return [sp] + list(wps) + [ep]

def wrap_text(label, w, fontsize):
    maxchars = max(6, int((w - 14) / (fontsize * 0.55)))
    lines = []
    for part in str(label).split('\n'):
        words = part.split(' '); cur = ''
        for wd in words:
            if cur == '': cur = wd
            elif len(cur) + 1 + len(wd) <= maxchars: cur += ' ' + wd
            else: lines.append(cur); cur = wd
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- SVG render
def render_svg(d):
    out = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
               'viewBox="0 0 %d %d" font-family="Helvetica, Arial, sans-serif">'
               % (d.w, d.h, d.w, d.h))
    # markers
    colors = sorted({e['color'] for e in d.edges} | {m['color'] for m in d.messages} | {'#445'})
    out.append('<defs>')
    for col in colors:
        mid = 'arr_' + col.replace('#', '')
        out.append('<marker id="%s" markerWidth="11" markerHeight="11" refX="8.5" refY="3.2" '
                   'orient="auto" markerUnits="userSpaceOnUse">'
                   '<path d="M0,0 L9,3.2 L0,6.4 Z" fill="%s"/></marker>' % (mid, col))
    out.append('</defs>')
    out.append('<rect x="0" y="0" width="%d" height="%d" fill="#FFFFFF"/>' % (d.w, d.h))
    # title
    out.append('<text x="%d" y="38" font-size="20" font-weight="700" fill="#10202E">%s</text>'
               % (40, esc(d.title)))
    out.append('<line x1="40" y1="48" x2="%d" y2="48" stroke="#10202E" stroke-width="1.5"/>'
               % (d.w - 40))
    if getattr(d, 'subtitle', ''):
        out.append('<text x="%d" y="64" font-size="11.5" fill="#5A6B7B">%s</text>'
                   % (40, esc(d.subtitle)))

    # sequence: fragments (back)
    for fr in d.fragments:
        x1, y1, x2, y2 = fr['x1'], fr['y1'], fr['x2'], fr['y2']
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="none" '
                   'stroke="#5B6B7B" stroke-width="1.3"/>' % (x1, y1, x2 - x1, y2 - y1))
        tw = 22 + len(fr['label']) * 5.6
        out.append('<path d="M%.1f,%.1f h%.1f l-8,9 h-%.1f z" fill="#E8EEF5" stroke="#5B6B7B" '
                   'stroke-width="1.0"/>' % (x1, y1, tw, tw - 8))
        out.append('<text x="%.1f" y="%.1f" font-size="10.5" font-weight="700" fill="#243B4A">%s</text>'
                   % (x1 + 6, y1 + 13, esc(fr['label'])))

    # sequence: lifelines
    for ll in d.lifelines:
        x, hw, hy, hh = ll['x'], ll['hw'], ll['hy'], ll['hh']
        bot = ll['bottom'] if ll['bottom'] else d.h - 30
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.3" '
                   'stroke-dasharray="5 5"/>' % (x, hy + hh, x, bot, ll['stroke']))
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="9" fill="%s" stroke="%s" '
                   'stroke-width="1.6"/>' % (x - hw / 2, hy, hw, hh, ll['fill'], ll['stroke']))
        llines = wrap_text(ll['label'], hw, 12)
        lh = 12 * 1.2; y0 = hy + hh / 2 - (len(llines) * lh) / 2 + 12 * 0.9
        for i, ln in enumerate(llines):
            out.append('<text x="%.1f" y="%.1f" font-size="12" font-weight="700" fill="#15202B" '
                       'text-anchor="middle">%s</text>' % (x, y0 + i * lh, esc(ln)))

    # sequence: messages (front)
    for m in d.messages:
        mk = 'arr_' + m['color'].replace('#', '')
        dash = ' stroke-dasharray="6 4"' if m['dashed'] else ''
        if m['kind'] == 'self':
            x = d._llx[m['frm']]; y = m['y']
            out.append('<path d="M%.1f,%.1f h26 v18 h-26" fill="none" stroke="%s" stroke-width="1.6"%s '
                       'marker-end="url(#%s)"/>' % (x, y, m['color'], dash, mk))
            for i, ln in enumerate(wrap_text(m['label'], 260, 10)):
                out.append('<text x="%.1f" y="%.1f" font-size="10.5" fill="#243B4A">%s</text>'
                           % (x + 34, y + 1 + i * 12, esc(ln)))
        else:
            x1 = d._llx[m['frm']]; x2 = d._llx[m['to']]; y = m['y']
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6"%s '
                       'marker-end="url(#%s)"/>' % (x1, y, x2, y, m['color'], dash, mk))
            lx = (x1 + x2) / 2
            mlines = wrap_text(m['label'], max(abs(x2 - x1), 150), 10)
            for i, ln in enumerate(mlines):
                yy = y - 6 - (len(mlines) - 1 - i) * 12
                out.append('<text x="%.1f" y="%.1f" font-size="10.5" fill="#243B4A" '
                           'text-anchor="middle">%s</text>' % (lx, yy, esc(ln)))

    # containers (back)
    for c in d.containers:
        x, y, w, h = cell_rect(c)
        hd = c['header']
        out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="11" fill="%s" stroke="%s" '
                   'stroke-width="1.6"/>' % (x, y, w, h, c['bodyfill'], c['stroke']))
        out.append('<path d="M%.1f,%.1f L%.1f,%.1f A11,11 0 0 1 %.1f,%.1f L%.1f,%.1f '
                   'A11,11 0 0 1 %.1f,%.1f L%.1f,%.1f Z" fill="%s" stroke="%s" stroke-width="1.6"/>'
                   % (x, y + hd, x, y + 11, x + 11, y, x + w - 11, y, x + w, y + 11,
                      x + w, y + hd, c['fill'], c['stroke']))
        out.append('<text x="%.1f" y="%.1f" font-size="14.5" font-weight="700" fill="#10202E">%s</text>'
                   % (x + 14, y + hd - 10, esc(c['title'])))

    # edges (under nodes)
    for e in d.edges:
        pts = edge_points(d, e)
        path = 'M%.1f,%.1f ' % (pts[0][0], pts[0][1]) + ' '.join('L%.1f,%.1f' % (p[0], p[1]) for p in pts[1:])
        dash = ' stroke-dasharray="6 5"' if e['dashed'] else ''
        mid = 'arr_' + e['color'].replace('#', '')
        end = ' marker-end="url(#%s)"' % mid if e['arrow'] in ('end', 'both') else ''
        start = ' marker-start="url(#%s)"' % mid if e['arrow'] == 'both' else ''
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.7"%s%s%s/>'
                   % (path, e['color'], dash, end, start))
        if e['label']:
            mx, my = poly_midpoint(pts)
            llines = [l for l in str(e['label']).split('\n') if l != '']
            ww = max(max(len(l) for l in llines) * 5.9 + 10, 16)
            hh = 13.6 * len(llines) + 4
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="#FFFFFF" '
                       'stroke="%s" stroke-width="0.8" opacity="0.96"/>'
                       % (mx - ww / 2, my - hh / 2, ww, hh, e['color']))
            for li, ln in enumerate(llines):
                out.append('<text x="%.1f" y="%.1f" font-size="10.5" fill="#243B4A" '
                           'text-anchor="middle">%s</text>'
                           % (mx, my - hh / 2 + 13.6 * li + 12, esc(ln)))

    # nodes
    for n in d.nodes:
        x, y, w, h = cell_rect(n); cx, cy = x + w / 2, y + h / 2
        if n['shape'] == 'cyl':
            ry = 9
            out.append('<path d="M%.1f,%.1f a%.1f,%.1f 0 0 0 %.1f,0 v%.1f a%.1f,%.1f 0 0 1 -%.1f,0 z" '
                       'fill="%s" stroke="%s" stroke-width="1.6"/>'
                       % (x, y + ry, w/2, ry, w, h - 2*ry, w/2, ry, w, n['fill'], n['stroke']))
            out.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
                       'stroke-width="1.6"/>' % (cx, y + ry, w/2, ry, tint(n['fill'], .2), n['stroke']))
            tcy = cy + ry/2
        elif n['shape'] == 'diamond':
            out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" '
                       'stroke="%s" stroke-width="1.6"/>'
                       % (cx, y, x + w, cy, cx, y + h, x, cy, n['fill'], n['stroke']))
            tcy = cy
        elif n['shape'] == 'ellipse':
            out.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
                       'stroke-width="1.6"/>' % (cx, cy, w / 2, h / 2, n['fill'], n['stroke']))
            tcy = cy
        elif n['shape'] == 'actor':
            hx = cx; hcy = y + 13; r = 8
            out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" stroke-width="1.6"/>'
                       % (hx, hcy, r, n['fill'], n['stroke']))
            bt = hcy + r; bb = bt + 18
            for (xa, ya, xb, yb) in [(hx, bt, hx, bb), (hx - 12, bt + 6, hx + 12, bt + 6),
                                     (hx, bb, hx - 10, bb + 12), (hx, bb, hx + 10, bb + 12)]:
                out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6"/>'
                           % (xa, ya, xb, yb, n['stroke']))
            for i, ln in enumerate(wrap_text(n['label'], w + 50, n['fontsize'])):
                out.append('<text x="%.1f" y="%.1f" font-size="%.1f" font-weight="700" fill="%s" '
                           'text-anchor="middle">%s</text>'
                           % (cx, bb + 26 + i * (n['fontsize'] * 1.15), n['fontsize'], n['fontcolor'], esc(ln)))
            continue
        elif n['shape'] == 'note':
            f = 14
            out.append('<path d="M%.1f,%.1f h%.1f l%.1f,%.1f v%.1f h-%.1f z" fill="%s" '
                       'stroke="%s" stroke-width="1.4"/>'
                       % (x, y, w - f, f, f, h - f, w, n['fill'], n['stroke']))
            out.append('<path d="M%.1f,%.1f l%.1f,%.1f h-%.1f z" fill="%s" stroke="%s" '
                       'stroke-width="1.2"/>' % (x + w - f, y, f, f, f, tint(n['fill'], .35), n['stroke']))
            tcy = cy
        elif n['shape'] == 'para':
            sk = 14
            out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" '
                       'stroke="%s" stroke-width="1.6"/>'
                       % (x + sk, y, x + w, y, x + w - sk, y + h, x, y + h, n['fill'], n['stroke']))
            tcy = cy
        else:
            rx = 9 if n['shape'] == 'round' else 0
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" fill="%s" '
                       'stroke="%s" stroke-width="1.6"/>' % (x, y, w, h, rx, n['fill'], n['stroke']))
            tcy = cy
        lines = wrap_text(n['label'], w, n['fontsize'])
        lh = n['fontsize'] * 1.22
        y0 = tcy - (len(lines) * lh) / 2 + n['fontsize'] * 0.92
        fw = '700' if n['bold'] else '400'
        for i, ln in enumerate(lines):
            out.append('<text x="%.1f" y="%.1f" font-size="%.1f" font-weight="%s" fill="%s" '
                       'text-anchor="middle">%s</text>'
                       % (cx, y0 + i * lh, n['fontsize'], fw, n['fontcolor'], esc(ln)))

    # tables
    for t in d.tables:
        x, y, w, h = cell_rect(t)
        th = t['header']
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="7" fill="#FFFFFF" '
                   'stroke="%s" stroke-width="1.6"/>' % (x, y, w, h, t['stroke']))
        out.append('<path d="M%.1f,%.1f L%.1f,%.1f A7,7 0 0 1 %.1f,%.1f L%.1f,%.1f '
                   'A7,7 0 0 1 %.1f,%.1f L%.1f,%.1f Z" fill="%s" stroke="%s" stroke-width="1.6"/>'
                   % (x, y + th, x, y + 7, x + 7, y, x + w - 7, y, x + w, y + 7,
                      x + w, y + th, t['fill'], t['stroke']))
        out.append('<text x="%.1f" y="%.1f" font-size="13" font-weight="700" fill="#10202E" '
                   'text-anchor="middle">%s</text>' % (x + w/2, y + t['header'] - 9, esc(t['title'])))
        ry = y + t['header']
        for (txt, tag) in t['rows']:
            out.append('<text x="%.1f" y="%.1f" font-size="11" fill="#243B4A">%s</text>'
                       % (x + 9, ry + t['rowh'] - 6, esc(txt)))
            if tag:
                out.append('<text x="%.1f" y="%.1f" font-size="9.5" font-weight="700" fill="%s" '
                           'text-anchor="end">%s</text>' % (x + w - 8, ry + t['rowh'] - 6, t['stroke'], esc(tag)))
            ry += t['rowh']
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="0.5" '
                       'opacity="0.5"/>' % (x + 4, ry, x + w - 4, ry, t['stroke']))
    out.append('</svg>')
    return '\n'.join(out)

# ---------------------------------------------------------------- drawio render
def style_node(n):
    base = 'whiteSpace=wrap;html=1;fontSize=%g;fillColor=%s;strokeColor=%s;fontColor=%s;' % (
        n['fontsize'], n['fill'], n['stroke'], n['fontcolor'])
    if n['bold']: base += 'fontStyle=1;'
    if n['shape'] == 'cyl':   return 'shape=cylinder3;backgroundOutline=1;' + base
    if n['shape'] == 'diamond': return 'rhombus;' + base
    if n['shape'] == 'ellipse': return 'ellipse;' + base
    if n['shape'] == 'actor':
        return 'shape=umlActor;verticalLabelPosition=bottom;labelPosition=center;verticalAlign=top;outlineConnect=0;' + base
    if n['shape'] == 'note':  return 'shape=note;size=14;' + base
    if n['shape'] == 'para':  return 'shape=parallelogram;perimeter=parallelogramPerimeter;fixedSize=1;size=14;' + base
    if n['shape'] == 'round': return 'rounded=1;arcSize=12;' + base
    return 'rounded=0;' + base

def render_drawio(d):
    cells = []
    cells.append('<mxCell id="0"/>')
    cells.append('<mxCell id="1" parent="0"/>')
    # title
    cells.append('<mxCell id="title" value="%s" style="text;html=1;fontSize=20;fontStyle=1;'
                 'verticalAlign=middle;align=left;fontColor=#10202E;" vertex="1" parent="1">'
                 '<mxGeometry x="40" y="14" width="%d" height="32" as="geometry"/></mxCell>'
                 % (esc(d.title), d.w - 80))
    if getattr(d, 'subtitle', ''):
        cells.append('<mxCell id="subtitle" value="%s" style="text;html=1;fontSize=11;'
                     'verticalAlign=middle;align=left;fontColor=#5A6B7B;" vertex="1" parent="1">'
                     '<mxGeometry x="40" y="52" width="%d" height="20" as="geometry"/></mxCell>'
                     % (esc(d.subtitle), d.w - 80))
    # containers (swimlane)
    for c in d.containers:
        st = ('swimlane;rounded=1;arcSize=4;startSize=%d;html=1;whiteSpace=wrap;fontSize=14;'
              'fontStyle=1;fillColor=%s;strokeColor=%s;swimlaneFillColor=%s;fontColor=#10202E;'
              'verticalAlign=middle;align=left;spacingLeft=8;'
              % (c['header'], c['fill'], c['stroke'], c['bodyfill']))
        cells.append('<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">'
                     '<mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>'
                     % (c['id'], esc(c['title']), st, c['x'], c['y'], c['w'], c['h']))
    # nodes
    for n in d.nodes:
        val = '&lt;br&gt;'.join(esc(p) for p in str(n['label']).split('\n'))
        parent = n['parent'] if n['parent'] else '1'
        gx, gy = n['x'], n['y']
        if n['parent']:
            pc = d.byid[n['parent']]; gx -= pc['x']; gy -= pc['y']
        cells.append('<mxCell id="%s" value="%s" style="%s" vertex="1" parent="%s">'
                     '<mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>'
                     % (n['id'], val, style_node(n), parent, gx, gy, n['w'], n['h']))
    # tables (swimlane + row children)
    for t in d.tables:
        st = ('swimlane;rounded=1;arcSize=6;startSize=%d;html=1;fontSize=13;fontStyle=1;'
              'fillColor=%s;strokeColor=%s;swimlaneFillColor=#FFFFFF;fontColor=#10202E;align=center;'
              % (t['header'], t['fill'], t['stroke']))
        cells.append('<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">'
                     '<mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>'
                     % (t['id'], esc(t['title']), st, t['x'], t['y'], t['w'], t['h']))
        for i, (txt, tag) in enumerate(t['rows']):
            label = esc(txt) + ('  &lt;b&gt;%s&lt;/b&gt;' % esc(tag) if tag else '')
            rst = ('text;html=1;align=left;verticalAlign=middle;spacingLeft=8;fontSize=11;'
                   'strokeColor=none;fillColor=none;fontColor=#243B4A;')
            cells.append('<mxCell id="%s_r%d" value="%s" style="%s" vertex="1" parent="%s">'
                         '<mxGeometry x="0" y="%d" width="%d" height="%d" as="geometry"/></mxCell>'
                         % (t['id'], i, label, rst, t['id'], t['header'] + i * t['rowh'], t['w'], t['rowh']))
    # edges
    for k, e in enumerate(d.edges):
        endarr = 'none' if e['arrow'] == 'none' else 'block'
        st = ('edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;fontSize=11;endArrow=%s;'
              'strokeColor=%s;labelBackgroundColor=#FFFFFF;' % (endarr, e['color']))
        if e['dashed']: st += 'dashed=1;'
        if e['arrow'] == 'both': st += 'startArrow=block;'
        if e['srcside']:
            sx = {'top': .5, 'bottom': .5, 'left': 0, 'right': 1}[e['srcside']]
            sy = {'top': 0, 'bottom': 1, 'left': .5, 'right': .5}[e['srcside']]
            st += 'exitX=%g;exitY=%g;exitDx=0;exitDy=0;' % (sx, sy)
        if e['dstside']:
            tx = {'top': .5, 'bottom': .5, 'left': 0, 'right': 1}[e['dstside']]
            ty = {'top': 0, 'bottom': 1, 'left': .5, 'right': .5}[e['dstside']]
            st += 'entryX=%g;entryY=%g;entryDx=0;entryDy=0;' % (tx, ty)
        geo = '<mxGeometry relative="1" as="geometry">'
        if e['waypoints']:
            geo += '<Array as="points">' + ''.join(
                '<mxPoint x="%d" y="%d"/>' % (int(p[0]), int(p[1])) for p in e['waypoints']) + '</Array>'
        geo += '</mxGeometry>'
        eval_ = '&lt;br&gt;'.join(esc(p) for p in str(e['label']).split('\n'))
        cells.append('<mxCell id="e%d" value="%s" style="%s" edge="1" parent="1" source="%s" '
                     'target="%s">%s</mxCell>' % (k, eval_, st, e['src'], e['dst'], geo))

    # sequence: lifelines (umlLifeline)
    for ll in d.lifelines:
        bot = ll['bottom'] if ll['bottom'] else d.h - 30
        h = int(bot - ll['hy'])
        st = ('shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=0;'
              'fillColor=%s;strokeColor=%s;fontColor=#15202B;fontStyle=1;fontSize=12;size=%d;'
              % (ll['fill'], ll['stroke'], ll['hh']))
        val = '&lt;br&gt;'.join(esc(p) for p in str(ll['label']).split('\n'))
        cells.append('<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">'
                     '<mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>'
                     % (ll['id'], val, st, int(ll['x'] - ll['hw'] / 2), ll['hy'], ll['hw'], h))
    # sequence: fragments (umlFrame)
    for j, fr in enumerate(d.fragments):
        st = ('shape=umlFrame;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#5B6B7B;'
              'fontColor=#243B4A;fontStyle=1;fontSize=11;align=left;verticalAlign=top;width=%d;height=20;'
              % int(max(46, 22 + len(fr['label']) * 5.6)))
        cells.append('<mxCell id="frag%d" value="%s" style="%s" vertex="1" parent="1">'
                     '<mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>'
                     % (j, esc(fr['label']), st, int(fr['x1']), int(fr['y1']),
                        int(fr['x2'] - fr['x1']), int(fr['y2'] - fr['y1'])))
    # sequence: messages (free point edges)
    for k2, m in enumerate(d.messages):
        st = ('html=1;endArrow=block;rounded=0;fontSize=10;strokeColor=%s;'
              'labelBackgroundColor=#FFFFFF;align=center;verticalAlign=bottom;' % m['color'])
        if m['dashed']: st += 'dashed=1;'
        if m['kind'] == 'self':
            x = d._llx[m['frm']]; y = m['y']
            st += 'edgeStyle=orthogonalEdgeStyle;'
            geo = ('<mxGeometry relative="1" as="geometry">'
                   '<mxPoint x="%d" y="%d" as="sourcePoint"/><mxPoint x="%d" y="%d" as="targetPoint"/>'
                   '<Array as="points"><mxPoint x="%d" y="%d"/><mxPoint x="%d" y="%d"/></Array>'
                   '</mxGeometry>' % (int(x), int(y), int(x), int(y + 18),
                                      int(x + 26), int(y), int(x + 26), int(y + 18)))
        else:
            x1 = d._llx[m['frm']]; x2 = d._llx[m['to']]; y = m['y']
            geo = ('<mxGeometry relative="1" as="geometry">'
                   '<mxPoint x="%d" y="%d" as="sourcePoint"/><mxPoint x="%d" y="%d" as="targetPoint"/>'
                   '</mxGeometry>' % (int(x1), int(y), int(x2), int(y)))
        cells.append('<mxCell id="msg%d" value="%s" style="%s" edge="1" parent="1">%s</mxCell>'
                     % (k2, esc(m['label']), st, geo))

    body = ('<mxGraphModel dx="900" dy="600" grid="1" gridSize="10" guides="1" tooltips="1" '
            'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="%d" pageHeight="%d" '
            'math="0" shadow="0"><root>%s</root></mxGraphModel>'
            % (d.w, d.h, ''.join(cells)))
    return ('<mxfile host="app.diagrams.net" type="device">'
            '<diagram name="%s" id="%s">%s</diagram></mxfile>' % (esc(d.title), d.name, body))

def write(d):
    with open(os.path.join(OUT, d.name + '.drawio'), 'w') as f:
        f.write(render_drawio(d))
    with open(os.path.join(OUT, d.name + '.svg'), 'w') as f:
        f.write(render_svg(d))
    print('wrote', d.name + '.drawio', '+', d.name + '.svg', '(%dx%d)' % (d.w, d.h))

def row_x(x0, x1, n, w):
    if n == 1: return [(x0 + x1 - w) / 2]
    gap = ((x1 - x0) - n * w) / (n - 1)
    return [x0 + i * (w + gap) for i in range(n)]


