#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dựng lại bảng mục lục theo cấu trúc mới (số trang điền ở bước sau)."""
import re, sys, docx

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


# ── thu thập các mục của Chương 2 từ chính các heading trong văn bản ───────
start = next(i for i, p in enumerate(ps)
             if p.style.name == 'Heading 1' and p.text.startswith('CHƯƠNG 2.'))
end = next(i for i, p in enumerate(ps)
           if p.style.name == 'Heading 1' and p.text.strip() == 'KẾT LUẬN')

entries = [('Chương 2', ps[start].text.split('.', 1)[1].strip())]
for p in ps[start + 1:end]:
    st = p.style.name
    if st not in ('Heading 2', 'Heading 3'):
        continue
    t = p.text.strip()
    m = re.match(r'^(\d+(?:\.\d+)?\.)\s+(.*)$', t)
    entries.append((m.group(1), m.group(2)) if m else ('', t))

print('số dòng mục lục cho Chương 2:', len(entries))

# ── ghi đè khối cũ (dòng 26..95) và xóa các dòng dư ────────────────────────
FIRST, LAST = 26, 95
rows = toc.rows
assert rows[FIRST].cells[0].text.strip().startswith('Chương 2'), rows[FIRST].cells[0].text
assert 'Kết luận chương 4' in rows[LAST].cells[1].text, rows[LAST].cells[1].text

for k, (num, title) in enumerate(entries):
    r = rows[FIRST + k]
    set_cell(r.cells[0], num)
    set_cell(r.cells[1], title)
    set_cell(r.cells[2], '00')

for r in list(rows[FIRST + len(entries):LAST + 1]):
    r._tr.getparent().remove(r._tr)

# số trang của các dòng còn lại cũng phải tính lại
for r in toc.rows[1:]:
    if r.cells[2].text.strip():
        set_cell(r.cells[2], '00')

d.save(DST)
print('mục lục: %d dòng sau khi dựng lại' % len(toc.rows))
