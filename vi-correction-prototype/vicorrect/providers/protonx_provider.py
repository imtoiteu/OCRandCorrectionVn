"""Provider — ProtonX Vietnamese text-correction family (ViT5 seq2seq).

Models (all `AutoModelForSeq2SeqLM`, ViT5/T5 encoder-decoder), purpose-built for
Vietnamese OCR post-processing (diacritic restoration, word segmentation,
punctuation) WITHOUT paraphrasing — closer to our task than a general corrector.

    protonx-models/distilled-protonx-legal-tc   ~0.1B   (default; lighter/faster)
    protonx-models/protonx-legal-tc             ~0.2B   (teacher; higher quality)
    protonx-models/nano-protonx-legal-tc        ~43.7M  (lightest fallback)

Reference inference (from the model cards):
    model.generate(**inputs, num_beams=10, max_new_tokens=160)

License: "ProtonX Text Correction Model License (v1.3-NC)" — NON-COMMERCIAL.
Recorded as "needs later review before production/commercial use". Not a blocker
for this internal prototype.

`model_id` accepts a HuggingFace id (auto-downloads) OR a local directory path.
"""

from __future__ import annotations

from typing import List, Tuple

from .base import CorrectionProvider

MODELS = {
    "distilled": "protonx-models/distilled-protonx-legal-tc",
    "base": "protonx-models/protonx-legal-tc",
    "nano": "protonx-models/nano-protonx-legal-tc",
}
DEFAULT_MODEL_ID = MODELS["distilled"]
LICENSE_NOTE = "ProtonX Text Correction Model License (v1.3-NC) — non-commercial; needs later review before production/commercial use"


class ProtonxProvider(CorrectionProvider):
    name = "protonx"

    def __init__(self, model_id: str = DEFAULT_MODEL_ID, device: str | None = None,
                 num_beams: int = 4, max_new_tokens: int = 160, max_input_length: int = 160,
                 batch_size: int = 4):
        # allow short aliases: --model distilled|base|nano
        self.model_id = MODELS.get(model_id, model_id)
        self.num_beams = num_beams
        self.max_new_tokens = max_new_tokens
        self.max_input_length = max_input_length
        self.batch_size = batch_size
        self._device = device
        self._tok = None
        self._model = None
        self._torch = None
        self._err = ""
        try:
            import torch  # noqa: F401
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM  # noqa: F401
            self._torch = torch
            self._AutoTokenizer = AutoTokenizer
            self._AutoModel = AutoModelForSeq2SeqLM
        except Exception as e:
            self._err = f"transformers/torch not importable: {e}"

    def available(self) -> Tuple[bool, str]:
        return (not self._err), self._err

    def _resolve_device(self) -> str:
        if self._device in (None, "auto"):
            return "cuda" if self._torch.cuda.is_available() else "cpu"
        if self._device in ("gpu", 0):
            return "cuda"
        return str(self._device)

    def warmup(self) -> None:
        self._ensure()

    def _ensure(self):
        if self._model is None:
            if self._err:
                raise RuntimeError(self._err)
            self._device_str = self._resolve_device()
            self._tok = self._AutoTokenizer.from_pretrained(self.model_id)
            self._model = self._AutoModel.from_pretrained(self.model_id)
            self._model.to(self._device_str)
            self._model.eval()

    def correct_text(self, text: str) -> str:
        if not text or not text.strip():
            return text
        return self.correct_batch([text])[0]

    def correct_batch(self, texts: List[str]) -> List[str]:
        result = list(texts)
        idx = [i for i, t in enumerate(texts) if t and t.strip()]
        if not idx:
            return result
        self._ensure()
        torch = self._torch
        payload = [texts[i] for i in idx]
        decoded: List[str] = []
        for start in range(0, len(payload), self.batch_size):
            chunk = payload[start:start + self.batch_size]
            enc = self._tok(chunk, return_tensors="pt", padding=True,
                            truncation=True, max_length=self.max_input_length)
            enc = {k: v.to(self._device_str) for k, v in enc.items()}
            with torch.no_grad():
                out = self._model.generate(
                    **enc, num_beams=self.num_beams,
                    max_new_tokens=self.max_new_tokens, do_sample=False,
                )
            decoded.extend(self._tok.batch_decode(out, skip_special_tokens=True))
        for i, gen in zip(idx, decoded):
            result[i] = gen.strip()
        return result
