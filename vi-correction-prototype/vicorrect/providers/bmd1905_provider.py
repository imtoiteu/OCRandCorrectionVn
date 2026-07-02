"""Provider B — bmd1905/vietnamese-correction.

Repo recommends the v2 model, hosted on HuggingFace as
`bmd1905/vietnamese-correction-v2` (fine-tuned on `vinai/bartpho-syllable`).
The README shows a `transformers.pipeline("text2text-generation", ...)` call, but
that task alias was removed in transformers 5.x, so we load the seq2seq model
directly with `AutoModelForSeq2SeqLM` + `AutoTokenizer` and run greedy decoding.
This is version-independent (works on transformers 4.x and 5.x) and is exactly
what the pipeline did under the hood.

`model_id` accepts a HuggingFace id (auto-downloads) OR a local directory path.
Decoding is greedy (num_beams=1, do_sample=False) — safe correction, not creative
rewriting.
"""

from __future__ import annotations

from typing import List, Tuple

from .base import CorrectionProvider

DEFAULT_MODEL_ID = "bmd1905/vietnamese-correction-v2"  # repo-recommended v2


class Bmd1905Provider(CorrectionProvider):
    name = "bmd1905"

    def __init__(self, model_id: str = DEFAULT_MODEL_ID, device: str | None = None,
                 max_length: int = 512, batch_size: int = 8, num_beams: int = 1):
        self.model_id = model_id
        self.max_length = max_length
        self.batch_size = batch_size
        self.num_beams = num_beams
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
                            truncation=True, max_length=self.max_length)
            enc = {k: v.to(self._device_str) for k, v in enc.items()}
            with torch.no_grad():
                out = self._model.generate(
                    **enc, max_length=self.max_length,
                    num_beams=self.num_beams, do_sample=False,
                )
            decoded.extend(self._tok.batch_decode(out, skip_special_tokens=True))
        for i, gen in zip(idx, decoded):
            result[i] = gen.strip()
        return result
