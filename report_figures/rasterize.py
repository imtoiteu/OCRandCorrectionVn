#!/usr/bin/env python3
"""Rasterize the report SVGs to PNG for embedding in the .docx.

* librsvg (via GObject introspection) is used instead of ImageMagick's internal
  SVG renderer: it goes through pango/fontconfig, so Vietnamese diacritics are
  shaped correctly.
* The font stack is swapped to Liberation Sans (metric-compatible with Arial,
  full Vietnamese coverage) for rasterization only -- the shipped .svg files keep
  their Helvetica/Arial stack.
* The in-figure title band is removed: in the report the Word caption
  ("Hình X.Y. ...") sits directly under the image, so keeping the title inside the
  picture would print it twice. The provenance subtitle is kept.
"""
import gi, sys, os, glob, re
gi.require_version('Rsvg', '2.0')
gi.require_foreign('cairo')
from gi.repository import Rsvg
import cairo

SRC, OUT = sys.argv[1], sys.argv[2]
SCALE = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
KEEP_TITLE = '--keep-title' in sys.argv
TOP = 44.0                      # crop line: below the title text and its rule

TITLE_RE = re.compile(r'<text x="40" y="38"[^>]*>.*?</text>', re.S)
RULE_RE = re.compile(r'<line x1="40" y1="48"[^>]*stroke-width="1\.5"/>')

os.makedirs(OUT, exist_ok=True)
for p in sorted(glob.glob(os.path.join(SRC, 'chapter*', '*.svg'))):
    xml = open(p, encoding='utf-8').read()
    xml = xml.replace('font-family="Helvetica, Arial, sans-serif"',
                      'font-family="Liberation Sans, DejaVu Sans, sans-serif"')
    m = re.search(r'width="(\d+)" height="(\d+)" viewBox="0 0 (\d+) (\d+)"', xml)
    W, H = int(m.group(1)), int(m.group(2))
    if not KEEP_TITLE:
        xml, n1 = TITLE_RE.subn('', xml, count=1)
        xml, n2 = RULE_RE.subn('', xml, count=1)
        assert n1 == 1 and n2 == 1, ('title/rule not matched in ' + p, n1, n2)
        xml = xml.replace('width="%d" height="%d" viewBox="0 0 %d %d"' % (W, H, W, H),
                          'width="%d" height="%d" viewBox="0 %g %d %g"'
                          % (W, H - TOP, TOP, W, H - TOP))
        H = int(H - TOP)
    handle = Rsvg.Handle.new_from_data(xml.encode('utf-8'))
    w, h = int(W * SCALE), int(H * SCALE)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    ctx = cairo.Context(surf)
    ctx.set_source_rgb(1, 1, 1); ctx.paint()
    ctx.scale(SCALE, SCALE)
    vp = Rsvg.Rectangle()
    vp.x, vp.y, vp.width, vp.height = 0, 0, W, H
    handle.render_document(ctx, vp)
    dst = os.path.join(OUT, os.path.basename(p)[:-4] + '.png')
    surf.write_to_png(dst)
    print('%-52s %5dx%-5d' % (os.path.basename(dst), w, h))
