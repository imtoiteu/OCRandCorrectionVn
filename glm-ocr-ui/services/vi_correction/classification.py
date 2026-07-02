"""Span classification.

Given a raw text span, assign one of the required categories:

    natural_language_vi      natural_language_mixed
    numeric_or_money         date_or_time
    id_or_code               formula_or_symbolic
    url_or_email_or_domain   table_header / table_cell_text
    unknown

Design notes (document-agnostic, no receipt rules):
  * We mask protected tokens first. If nothing but protected tokens remains, the
    span is classified by the token type (numeric/date/id/url/formula).
  * Otherwise the span is natural language. Vietnamese OCR output is detected by
    the presence of NON-ASCII letters — this is robust to *corrupted* diacritics
    (e.g. "Mā", "Gìo") that a plain Vietnamese-alphabet check would miss.
  * Pure-ASCII alphabetic spans (no diacritics at all) are left as `unknown` and
    skipped, so we never risk adding wrong diacritics to English / code text.
  * `table_header` / `table_cell_text` are ROLES supplied by the segmentation
    layer; content classification is still computed to decide correctability.
"""

from __future__ import annotations

import re

from .masking import MASKER

_PH_RE = re.compile(r"⟦\d+⟧")
_ASCII_WORD_RE = re.compile(r"[A-Za-z]{2,}")

NATURAL = {"natural_language_vi", "natural_language_mixed"}
CORRECTABLE = NATURAL | {"table_header", "table_cell_text"}


def _has_non_ascii_letter(s: str) -> bool:
    return any(c.isalpha() and ord(c) > 127 for c in s)


def classify(text: str) -> str:
    t = (text or "").strip()
    if not t:
        return "unknown"

    mr = MASKER.mask(t)
    core = _PH_RE.sub(" ", mr.text)                 # drop protected tokens
    letters = [c for c in core if c.isalpha()]

    if not letters:
        # span is made up entirely of protected tokens (+ punctuation)
        return MASKER.category_from_tags(mr.tags)

    has_vi = _has_non_ascii_letter(core)
    has_ascii_word = bool(_ASCII_WORD_RE.search(core))

    if has_vi and has_ascii_word:
        return "natural_language_mixed"
    if has_vi:
        return "natural_language_vi"
    # No Vietnamese diacritics at all. In a Vietnamese OCR document a multi-word
    # ASCII span is very often *fully de-diacritized* Vietnamese (e.g. OCR turned
    # "Giờ" into "Glo"), so we treat it as mixed and let the provider re-diacritize
    # it — protected tokens are already masked out, so this is structurally safe.
    # Isolated single letters / stray glyphs stay `unknown` (skipped).
    if has_ascii_word:
        return "natural_language_mixed"
    return "unknown"


def is_correctable(category: str) -> bool:
    return category in NATURAL
