"""High-level Vietnamese OCR-correction service used by the web app.

Ties together provider construction, input normalisation (structured OCR JSON, or
pasted Markdown/text), the block-by-block correction pipeline, structure
validation, and Markdown/text re-rendering — returning JSON-friendly dicts.

The OCR engine is never touched; this runs only when the user asks for correction.
"""

from __future__ import annotations

import re
from typing import Any, List, Optional

from .pipeline import correct_document, PipelineOptions
from .validation import validate_document
from .renderers import blocks_to_markdown, blocks_to_text
from .providers import get_provider

# UI-facing catalogue. `hf` = HuggingFace id (also the default download target).
PROVIDERS = [
    {"id": "protonx", "label": "ProtonX (Vietnamese OCR correction)", "models": [
        {"id": "nano",      "label": "ProtonX Nano (~43.7M)",  "hf": "protonx-models/nano-protonx-legal-tc"},
        {"id": "distilled", "label": "ProtonX Distilled (~0.1B)", "hf": "protonx-models/distilled-protonx-legal-tc"},
        {"id": "full",      "label": "ProtonX Full (~0.2B)",   "hf": "protonx-models/protonx-legal-tc"},
    ]},
    {"id": "bmd1905", "label": "bmd1905 vietnamese-correction-v2", "models": [
        {"id": "bmd1905", "label": "vietnamese-correction-v2", "hf": "bmd1905/vietnamese-correction-v2"},
    ]},
    {"id": "mock", "label": "Mock (no model — UI/pipeline smoke test)", "models": [
        {"id": "mock", "label": "Mock dictionary", "hf": None},
    ]},
]

# UI model id -> ProtonX provider alias (provider knows nano/distilled/base)
_PROTONX_ALIAS = {"nano": "nano", "distilled": "distilled", "full": "base", "base": "base"}


def list_providers() -> List[dict]:
    return PROVIDERS


def _provider_kwargs(provider: str, model: Optional[str] = None, model_path: Optional[str] = None,
                     device: Optional[str] = None, max_new_tokens=None, num_beams=None) -> dict:
    p = (provider or "").lower()
    kw: dict = {}
    if p in ("protonx", "proton", "px"):
        if model_path:
            kw["model_id"] = model_path
        elif model:
            kw["model_id"] = _PROTONX_ALIAS.get(model, model)
        if device:
            kw["device"] = device
        if max_new_tokens:
            kw["max_new_tokens"] = int(max_new_tokens)
        if num_beams:
            kw["num_beams"] = int(num_beams)
    elif p in ("bmd1905", "bmd", "b"):
        if model_path:
            kw["model_id"] = model_path
        if device:
            kw["device"] = device
        if max_new_tokens:
            kw["max_length"] = int(max_new_tokens)
    elif p in ("mrlasdt", "a"):
        if model_path:
            kw["weight_path"] = model_path
        if device:
            kw["device"] = device
    # mock: no kwargs
    return kw


def build_provider(provider: str, **cfg):
    """Construct a provider. Never downloads here — model load happens on warmup()."""
    return get_provider(provider, **_provider_kwargs(provider, **cfg))


def normalize_input(*, ocr_json=None, text: str = None, markdown: str = None) -> List[Any]:
    """Return a canonical document = list of pages, each a list of block dicts.

    - `ocr_json`: used as-is (GLM-style [[block,...]] or [block,...]).
    - `markdown`/`text`: split into paragraph blocks so the pipeline can segment
      and correct them (structure preserved, protected tokens masked)."""
    if ocr_json is not None:
        return ocr_json
    raw = markdown if markdown is not None else (text or "")
    paras = [p for p in re.split(r"\n\s*\n", raw) if p.strip()]
    if not paras and raw.strip():
        paras = [raw]
    blocks = [{"index": i, "label": "text", "native_label": "text", "content": p}
              for i, p in enumerate(paras)]
    return [blocks]


def _span(s) -> dict:
    return {"page": s.page, "block_index": s.block_index, "label": s.label,
            "role": s.role, "classification": s.classification,
            "before": s.before, "after": s.after, "status": s.status}


def run_correction(doc: List[Any], provider) -> dict:
    """Run correction on `doc` (unchanged) and return a serialisable result bundle."""
    result = correct_document(doc, provider, PipelineOptions())
    vrep = validate_document(doc, result.document)
    return {
        "corrected_json": result.document,
        "corrected_markdown": blocks_to_markdown(result.document),
        "corrected_text": blocks_to_text(result.document),
        "changed": [_span(s) for s in result.changed],
        "skipped": [_span(s) for s in result.skipped],
        "counts": {"blocks": result.n_blocks, "units": result.n_units,
                   "sent": result.n_sent, "changed": len(result.changed),
                   "skipped": len(result.skipped)},
        "timing": {"provider_seconds": round(result.provider_seconds, 3),
                   "total_seconds": round(result.total_seconds, 3)},
        "validation": {"passed": vrep.passed,
                       "checks": [{"name": c.name, "ok": c.ok, "detail": c.detail}
                                  for c in vrep.checks]},
        "provider": result.provider_name,
    }
