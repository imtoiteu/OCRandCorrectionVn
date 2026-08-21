#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dựng lại bảng mục lục theo cấu trúc hiện tại (số trang điền ở bước sau)."""
import re, sys, docx
from copy import deepcopy

SRC, DST = sys.argv[1], sys.argv[2]
d = docx.Document(SRC)
ps = d.paragraphs
toc = d.tables[0]


def set_cell(cell, text):
    p = cell.paragraphs[0]
    runs = p.runs
    if not runs:
        p.add_run(text)
    else:
        runs[0].text = text
        for r in runs[1:]:
            r._element.getparent().remove(r._element)
    for extra in cell.paragraphs[1:]:
        extra._p.getparent().remove(extra._p)


start = next(i for i, p in enumerate(ps)
             if p.style.name == 'Heading 1' and p.text.startswith('CHƯƠNG 2.'))
end = next(i for i, p in enumerate(ps)
           if p.style.name == 'Heading 1' and p.text.strip() == 'KẾT LUẬN')

entries = [('Chương 2.', ps[start].text.split('.', 1)[1].strip())]
for p in ps[start + 1:end]:
    if p.style.name not in ('Heading 2', 'Heading 3'):
        continue
    t = p.text.strip()
    m = re.match(r'^(\d+(?:\.\d+)?\.)\s+(.*)$', t)
    entries.append((m.group(1), m.group(2)) if m else ('', t))
print('số dòng mục lục cho Chương 2:', len(entries))

rows = toc.rows
FIRST = next(i for i, r in enumerate(rows) if r.cells[0].text.strip().startswith('Chương 2'))
LAST = next(i for i, r in enumerate(rows) if 'Kết luận chương 2' in r.cells[1].text)
have = LAST - FIRST + 1
need = len(entries)

# thêm hoặc bớt dòng cho khớp
tmpl = rows[FIRST + 1]._tr
while need > have:
    rows[LAST]._tr.addnext(deepcopy(tmpl))
    have += 1; LAST += 1
    rows = toc.rows
while need < have:
    rows[LAST]._tr.getparent().remove(rows[LAST]._tr)
    have -= 1; LAST -= 1
    rows = toc.rows

for k, (num, title) in enumerate(entries):
    r = toc.rows[FIRST + k]
    set_cell(r.cells[0], num)
    set_cell(r.cells[1], title)
    set_cell(r.cells[2], '00')
for r in toc.rows[1:]:
    if r.cells[2].text.strip():
        set_cell(r.cells[2], '00')

d.save(DST)
print('mục lục: %d dòng' % len(toc.rows))
