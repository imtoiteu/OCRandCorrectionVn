"""Post-correction validation.

Verifies the corrected document against the original:
  * page count and per-page block count unchanged
  * per-block geometry/metadata unchanged: index, label, native_label,
    bbox_2d, polygon
  * corrected_content present; non-empty when content was non-empty
  * protected tokens unchanged (same multiset in content and corrected_content)
  * HTML tag sequence unchanged (tables stay valid, row/col counts preserved)
  * Markdown table shape unchanged (per-line `|` counts preserved)
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, List

from .masking import MASKER

_GEOMETRY_FIELDS = ["index", "label", "native_label", "bbox_2d", "polygon"]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class ValidationReport:
    checks: List[Check] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.ok for c in self.checks)

    def add(self, name: str, ok: bool, detail: str = ""):
        self.checks.append(Check(name, ok, detail))

    def failures(self) -> List[Check]:
        return [c for c in self.checks if not c.ok]


def _iter_pages(doc):
    if doc and isinstance(doc[0], dict):
        return [doc]
    return doc


def _pipe_shape(text: str) -> List[int]:
    return [ln.count("|") for ln in (text or "").split("\n")]


def validate_document(original: List[Any], corrected: List[Any]) -> ValidationReport:
    rep = ValidationReport()
    o_pages = _iter_pages(original)
    c_pages = _iter_pages(corrected)

    rep.add("page_count_unchanged", len(o_pages) == len(c_pages),
            f"{len(o_pages)} -> {len(c_pages)}")
    if len(o_pages) != len(c_pages):
        return rep

    geom_bad, block_count_bad = [], []
    empty_bad, missing_field = [], []
    tok_bad, html_bad, md_bad = [], [], []

    for pi, (op, cp) in enumerate(zip(o_pages, c_pages)):
        if len(op) != len(cp):
            block_count_bad.append(f"page {pi}: {len(op)} -> {len(cp)}")
            continue
        for bi, (ob, cb) in enumerate(zip(op, cp)):
            where = f"p{pi}b{bi}(idx={ob.get('index')})"
            for fld in _GEOMETRY_FIELDS:
                if ob.get(fld) != cb.get(fld):
                    geom_bad.append(f"{where}.{fld}")
            content = ob.get("content", "") or ""
            corr = cb.get("corrected_content", None)
            if corr is None:
                missing_field.append(where)
                continue
            if content.strip() and not corr.strip():
                empty_bad.append(where)
            # protected tokens (multiset) unchanged
            if Counter(MASKER.extract_tokens(content)) != Counter(MASKER.extract_tokens(corr)):
                o_t = Counter(MASKER.extract_tokens(content))
                c_t = Counter(MASKER.extract_tokens(corr))
                tok_bad.append(f"{where}: -{list((o_t - c_t).elements())} +{list((c_t - o_t).elements())}")
            # html tags unchanged
            if MASKER.extract_html_tags(content) != MASKER.extract_html_tags(corr):
                html_bad.append(where)
            # markdown table shape unchanged
            if _pipe_shape(content) != _pipe_shape(corr):
                md_bad.append(where)

    rep.add("block_count_unchanged", not block_count_bad, "; ".join(block_count_bad))
    rep.add("geometry_metadata_unchanged", not geom_bad,
            "changed: " + ", ".join(geom_bad) if geom_bad else "index/label/native_label/bbox_2d/polygon preserved")
    rep.add("corrected_content_present", not missing_field,
            "missing: " + ", ".join(missing_field) if missing_field else "")
    rep.add("corrected_content_nonempty", not empty_bad,
            "empty: " + ", ".join(empty_bad) if empty_bad else "")
    rep.add("protected_tokens_unchanged", not tok_bad,
            "; ".join(tok_bad) if tok_bad else "all numbers/dates/money/ids/urls preserved")
    rep.add("html_tags_unchanged", not html_bad,
            "; ".join(html_bad) if html_bad else "tag sequence identical")
    rep.add("markdown_table_shape_unchanged", not md_bad,
            "; ".join(md_bad) if md_bad else "per-line pipe counts identical")
    return rep
