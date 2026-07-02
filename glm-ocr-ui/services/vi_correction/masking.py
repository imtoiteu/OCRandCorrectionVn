"""Protected-token masking.

Before any natural-language span is handed to a correction provider, tokens that
must never be "corrected" (numbers, money, dates, times, IDs/codes, URLs, emails,
domains, units, formulas, Markdown/HTML syntax) are replaced with opaque
placeholders. After correction the placeholders are restored verbatim.

This is deliberately regex-only and document-agnostic — no invoice/receipt rules.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# Ordered by priority. Earlier (more specific) patterns win when starts tie.
# Every pattern is generic; nothing here is receipt-specific.
_PATTERNS: List[Tuple[str, "re.Pattern[str]"]] = [
    ("html_tag",   re.compile(r"<[^>\n]+>")),
    ("md_image",   re.compile(r"!\[[^\]]*\]\([^)]*\)")),
    ("md_link",    re.compile(r"\[[^\]]*\]\([^)]*\)")),
    ("code_span",  re.compile(r"`[^`]+`")),
    ("formula",    re.compile(r"\$[^$\n]+\$|\\\([^)]*\\\)|\\\[[^\]]*\\\]")),
    ("url",        re.compile(r"(?:https?://|www\.)[^\s)]+", re.I)),
    ("email",      re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")),
    # money: 1.234.567 / 1,234,567 with optional currency, or number+currency word
    ("money",      re.compile(r"\d{1,3}(?:[.,]\d{3})+(?:\s?(?:đ|₫|VND|USD|\$))?|\d+(?:[.,]\d+)?\s?(?:đ|₫|VND|USD)\b", re.I)),
    ("percent",    re.compile(r"\d+(?:[.,]\d+)?\s?%")),
    ("time",       re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")),
    ("date",       re.compile(r"\b\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}\b|\b\d{4}[/\-]\d{1,2}[/\-]\d{1,2}\b")),
    ("id_hash",    re.compile(r"#[A-Za-z0-9][\w\-]*")),
    # alphanumeric code: token containing BOTH a letter and a digit (e.g. Q9P94, A1B2)
    ("code_alnum", re.compile(r"\b(?=[A-Za-z0-9\-]*[A-Za-z])(?=[A-Za-z0-9\-]*\d)[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\b")),
    ("range",      re.compile(r"\b\d+\-\d+\b")),
    ("domain",     re.compile(r"\b[A-Za-z0-9]+(?:[.\-][A-Za-z0-9]+)*\.(?:vn|com|net|org|io|co|edu|gov|info|vip|xyz|ai|app|dev)\b", re.I)),
    ("unit",       re.compile(r"\b\d+(?:[.,]\d+)?\s?(?:kg|g|mg|km|cm|mm|ml|l|m2|m3|m|%)\b", re.I)),
    ("number",     re.compile(r"\b\d[\d.,]*\b")),
]

_CATEGORY_BY_TAG = {
    "html_tag": "unknown", "md_image": "unknown", "md_link": "unknown",
    "code_span": "formula_or_symbolic", "formula": "formula_or_symbolic",
    "url": "url_or_email_or_domain", "email": "url_or_email_or_domain",
    "domain": "url_or_email_or_domain",
    "money": "numeric_or_money", "percent": "numeric_or_money",
    "number": "numeric_or_money", "unit": "numeric_or_money",
    "time": "date_or_time", "date": "date_or_time",
    "id_hash": "id_or_code", "code_alnum": "id_or_code", "range": "id_or_code",
}


@dataclass
class MaskResult:
    text: str                      # masked text (placeholders in place of tokens)
    mapping: Dict[str, str] = field(default_factory=dict)   # placeholder -> original
    tags: Dict[str, str] = field(default_factory=dict)      # placeholder -> pattern name

    @property
    def tokens(self) -> List[str]:
        return list(self.mapping.values())


class ProtectedTokenMasker:
    def __init__(self, open_ch: str = "⟦", close_ch: str = "⟧"):
        # ⟦ / ⟧  — rare mathematical brackets, easy to detect on restore.
        self.open_ch = open_ch
        self.close_ch = close_ch
        self._ph_re = re.compile(re.escape(open_ch) + r"(\d+)" + re.escape(close_ch))

    def _ph(self, i: int) -> str:
        return f"{self.open_ch}{i}{self.close_ch}"

    def mask(self, text: str) -> MaskResult:
        if not text:
            return MaskResult(text="", mapping={}, tags={})
        out: List[str] = []
        mapping: Dict[str, str] = {}
        tags: Dict[str, str] = {}
        pos, counter, L = 0, 0, len(text)
        while pos < L:
            best = None  # (start, end, name)
            for name, rx in _PATTERNS:
                m = rx.search(text, pos)
                if not m or m.end() == m.start():
                    continue
                s, e = m.start(), m.end()
                if best is None or s < best[0] or (s == best[0] and e > best[1]):
                    best = (s, e, name)
            if best is None:
                out.append(text[pos:])
                break
            s, e, name = best
            out.append(text[pos:s])
            ph = self._ph(counter)
            mapping[ph] = text[s:e]
            tags[ph] = name
            out.append(ph)
            counter += 1
            pos = e
        return MaskResult(text="".join(out), mapping=mapping, tags=tags)

    def restore(self, text: str, mr: MaskResult) -> str:
        for ph, orig in mr.mapping.items():
            text = text.replace(ph, orig)
        return text

    def placeholders_intact(self, model_out: str, mr: MaskResult) -> bool:
        """True if every placeholder survived AND no stray placeholders appeared."""
        for ph in mr.mapping:
            if ph not in model_out:
                return False
        # any placeholder-looking token that isn't ours = model hallucination
        for m in self._ph_re.finditer(model_out):
            if m.group(0) not in mr.mapping:
                return False
        return True

    def category_from_tags(self, tags: Dict[str, str]) -> str:
        tagset = list(tags.values())

        def has(*names):
            return any(n in tagset for n in names)

        if has("url", "email", "domain"):
            return "url_or_email_or_domain"
        if has("formula", "code_span"):
            return "formula_or_symbolic"
        if has("date", "time"):
            return "date_or_time"
        if has("money", "percent"):
            return "numeric_or_money"
        if has("id_hash", "code_alnum", "range"):
            return "id_or_code"
        if has("number", "unit"):
            return "numeric_or_money"
        return "unknown"

    def extract_tokens(self, text: str) -> List[str]:
        """Protected tokens present in a raw string (order preserved)."""
        return self.mask(text).tokens

    def extract_html_tags(self, text: str) -> List[str]:
        return re.findall(r"<[^>\n]+>", text or "")


# A shared default instance (stateless / thread-safe for reads).
MASKER = ProtectedTokenMasker()
