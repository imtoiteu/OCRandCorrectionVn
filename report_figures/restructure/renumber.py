#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đánh số lại hình và bảng sau khi gộp ba chương thành Chương 2."""
import re, sys, docx

SRC, DST = sys.argv[1], sys.argv[2]
d = docx.Document(SRC)
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

# Hình: 2.1–2.10 giữ nguyên; 3.1–3.11 -> 2.11–2.21; 4.1–4.5 -> 2.22–2.26
FIG = {'2.%d' % i: '2.%d' % i for i in range(1, 11)}
FIG.update({'3.%d' % i: '2.%d' % (10 + i) for i in range(1, 12)})
FIG.update({'4.%d' % i: '2.%d' % (21 + i) for i in range(1, 6)})
# Bảng: 4.1–4.11 -> 2.1–2.11
TBL = {'4.%d' % i: '2.%d' % i for i in range(1, 12)}

RE_FIG = re.compile(r'(Hình\s+)(\d+\.\d+)([a-z]?)')
RE_TBL = re.compile(r'(Bảng\s+)(\d+\.\d+)')

stats = {'fig': 0, 'tbl': 0, 'miss': set()}


def fix(text):
    def f(m):
        n = FIG.get(m.group(2))
        if n is None:
            stats['miss'].add('Hình ' + m.group(2)); return m.group(0)
        stats['fig'] += 1
        return m.group(1) + n + m.group(3)

    def t(m):
        n = TBL.get(m.group(2))
        if n is None:
            stats['miss'].add('Bảng ' + m.group(2)); return m.group(0)
        stats['tbl'] += 1
        return m.group(1) + n
    return RE_TBL.sub(t, RE_FIG.sub(f, text))


# TOC (bảng đầu tiên) được dựng lại riêng nên bỏ qua ở bước này
toc_tbl = d.tables[0]._tbl
for node in d.element.body.iter(W + 't'):
    anc = node
    skip = False
    while anc is not None:
        if anc is toc_tbl:
            skip = True; break
        anc = anc.getparent()
    if skip or not node.text:
        continue
    new = fix(node.text)
    if new != node.text:
        node.text = new

d.save(DST)
print('đã đổi: %d tham chiếu Hình, %d tham chiếu Bảng' % (stats['fig'], stats['tbl']))
print('không có trong bảng ánh xạ:', stats['miss'] or 'không có')
