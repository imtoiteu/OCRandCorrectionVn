#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Điền số trang thật vào bảng mục lục, đọc từ bản kết xuất PDF."""
import re, sys, docx

DOCX_IN, DOCX_OUT, PDF_TXT = sys.argv[1], sys.argv[2], sys.argv[3]

pages = open(PDF_TXT, encoding='utf-8').read().split('\f')[:-1]
folio = []
for pg in pages:
    first = pg.split('\n')[0].strip()
    folio.append(int(first) if first.isdigit() else None)
norm = [re.sub(r'\s+', ' ', pg) for pg in pages]

d = docx.Document(DOCX_IN)
toc = d.tables[0]
heads = [p for p in d.paragraphs if p.style.name in ('Heading 1', 'Heading 2', 'Heading 3')]
rows = toc.rows[1:]
assert len(heads) == len(rows), (len(heads), len(rows))

# bắt đầu tìm sau phần mục lục (trang có bảng chữ viết tắt)
start = next(i for i, t in enumerate(norm) if ' 00 ' not in t)


def set_cell(cell, text):
    p = cell.paragraphs[0]
    r = p.runs
    if not r:
        p.add_run(text)
    else:
        r[0].text = text
        for x in r[1:]:
            x._element.getparent().remove(x._element)


cur, missing = start, []
for h, row in zip(heads, rows):
    key = re.sub(r'\s+', ' ', h.text).strip()
    hit = None
    # tiêu đề có thể bị ngắt qua hai dòng/trang -> thử dần với tiền tố ngắn hơn
    for cut in (len(key), 60, 45, 32, 24):
        k = key[:cut].strip()
        if not k:
            continue
        for i in range(cur, len(norm)):
            if k in norm[i]:
                hit = i; break
        if hit is None:
            for i in range(start, len(norm)):
                if k in norm[i]:
                    hit = i; break
        if hit is not None:
            break
    if hit is None:
        missing.append(key[:60]); continue
    cur = hit
    set_cell(row.cells[2], str(folio[hit]) if folio[hit] else '')

d.save(DOCX_OUT)
print('không xác định được trang cho:', missing or 'không có mục nào')
print('đã lưu:', DOCX_OUT)
