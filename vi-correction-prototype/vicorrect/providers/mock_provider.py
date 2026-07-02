"""Mock provider — an OFFLINE test double, NOT part of the correction design.

Purpose: exercise the pipeline (segmentation, masking, validation, JSON I/O)
without downloading any ML model. It applies Unicode NFC normalisation plus a
tiny, general dictionary of frequent Vietnamese OCR diacritic confusions at the
word level. It intentionally knows nothing about invoices/receipts and leaves
protected-token placeholders (⟦n⟧) untouched.

Real quality evaluation must use the ML providers (bmd1905 / mrlasdt). This mock
exists only so the harness runs end-to-end when models are unavailable.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Tuple

from .base import CorrectionProvider

# General Vietnamese OCR confusions (lowercased NFC keys). Not receipt-specific:
# these are common diacritic/character errors seen across many document types.
_CONFUSIONS = {
    "dộn": "đơn", "hd": "hđ", "mā": "mã",
    "gìo": "giờ", "glo": "giờ", "gio": "giờ",
    "tiện": "tiền", "tông": "tổng", "mát": "mặt",
    "đja": "địa", "phương": "phường", "quân": "quận",
    "tống": "tổng", "thanh": "thanh", "toàn": "toàn",
    "hoá": "hóa", "khỏan": "khoản", "duyêt": "duyệt",
}

_WORD = re.compile(r"[^\W\d_]+", re.UNICODE)


def _match_case(src: str, dst: str) -> str:
    if src.isupper():
        return dst.upper()
    if src[:1].isupper():
        return dst[:1].upper() + dst[1:]
    return dst


class MockProvider(CorrectionProvider):
    name = "mock"

    def available(self) -> Tuple[bool, str]:
        return True, ""

    def correct_text(self, text: str) -> str:
        if not text or not text.strip():
            return text
        text = unicodedata.normalize("NFC", text)

        def repl(m: "re.Match[str]") -> str:
            w = m.group(0)
            key = unicodedata.normalize("NFC", w).lower()
            if key in _CONFUSIONS:
                return _match_case(w, _CONFUSIONS[key])
            return w

        return _WORD.sub(repl, text)
