"""Provider A — mrlasdt/vietnamese-ocr-error-corrector.

The repo is a toolbox (OCR / address / lettercase / datetime correctors). The OCR
corrector is a from-scratch seq2seq/transformer whose weights live at
`weights/seq2seq_*.pth`. Those weights are NOT shipped with the repo and the
README provides no download link (it points to the upstream
`buiquangmanhhp1999/VietnameseOcrCorrection`, which also ships no weights). So the
OCR corrector cannot run out-of-the-box.

This adapter installs the repo on `sys.path`, and if the weights are present it
runs `Corrector(...)(text, "ocr")`. Otherwise `available()` reports exactly why,
and the test harness records the provider as unavailable rather than crashing.
"""

from __future__ import annotations

import os
import sys
from typing import Tuple

from .base import CorrectionProvider

_HERE = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", "vendor", "mrlasdt"))


class MrlasdtProvider(CorrectionProvider):
    name = "mrlasdt"

    def __init__(self, repo_dir: str = _DEFAULT_REPO, weight_path: str | None = None,
                 device: str = "cpu", ngram: int = 5):
        self.repo_dir = os.path.abspath(repo_dir)
        self.device = device
        self.ngram = ngram
        self.weight_path = weight_path or os.path.join(self.repo_dir, "weights", "seq2seq_1.pth")
        self._corrector = None
        self._err = ""
        if not os.path.isdir(self.repo_dir):
            self._err = f"repo not cloned at {self.repo_dir}"
        elif not os.path.isfile(self.weight_path):
            self._err = (
                f"pretrained OCR weights not found at {self.weight_path}. "
                "mrlasdt / VietnameseOcrCorrection ships no weights and documents no "
                "download link, so the seq2seq OCR corrector cannot be loaded."
            )

    def available(self) -> Tuple[bool, str]:
        return (not self._err), self._err

    def warmup(self) -> None:
        self._ensure()

    def _ensure(self):
        if self._corrector is None:
            if self._err:
                raise RuntimeError(self._err)
            if self.repo_dir not in sys.path:
                sys.path.insert(0, self.repo_dir)
            cwd = os.getcwd()
            os.chdir(self.repo_dir)
            try:
                from main import Corrector  # type: ignore
                self._corrector = Corrector(kwargs_ocr={
                    "device": self.device, "model_type": "seq2seq",
                    "weight_path": self.weight_path,
                })
            finally:
                os.chdir(cwd)

    def correct_text(self, text: str) -> str:
        if not text or not text.strip():
            return text
        self._ensure()
        cwd = os.getcwd()
        os.chdir(self.repo_dir)
        try:
            out = self._corrector(text, "ocr")
        finally:
            os.chdir(cwd)
        return out if isinstance(out, str) and out.strip() else text
