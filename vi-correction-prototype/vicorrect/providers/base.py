"""Generic correction-provider interface.

The correction pipeline depends ONLY on this interface. A provider receives a
plain, already-masked, natural-language string and returns a corrected string.
It must never see the OCR JSON, geometry, table structure, or protected tokens.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple


class CorrectionProvider(ABC):
    name: str = "base"

    @abstractmethod
    def correct_text(self, text: str) -> str:
        """Correct one natural-language span. Return input unchanged if unsure."""
        raise NotImplementedError

    def correct_batch(self, texts: List[str]) -> List[str]:
        """Default: per-item. Model-backed providers override for efficiency."""
        return [self.correct_text(t) for t in texts]

    def available(self) -> Tuple[bool, str]:
        """(usable, reason). Lets the harness report install/setup problems
        instead of crashing."""
        return True, ""

    def warmup(self) -> None:
        """Optional: load the model up-front (for clean timing)."""
        return None
