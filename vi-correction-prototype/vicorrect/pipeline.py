"""Correction pipeline: structured OCR JSON -> same JSON + `corrected_content`.

Guarantees:
  * The original `content` is never overwritten; a sibling `corrected_content`
    is added to every block.
  * index / label / native_label / bbox_2d / polygon / page order / block order
    are copied through untouched.
  * Only natural-language Vietnamese spans reach the provider, and only after
    protected tokens are masked. If the provider mangles a placeholder, that
    span's correction is REJECTED and the original text is kept (safe default).
  * Providers are called in ONE batch for accurate, comparable timing.
"""

from __future__ import annotations

import copy
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .classification import classify, is_correctable
from .masking import MASKER
from .segmentation import segment_block
from .providers.base import CorrectionProvider


@dataclass
class PipelineOptions:
    mode: str = "safe"          # "safe" = conservative (default). Reserved for future modes.
    add_field: str = "corrected_content"


@dataclass
class SpanRecord:
    page: int
    block: int
    block_index: Any
    label: str
    role: str
    classification: str
    before: str
    after: str = ""
    status: str = ""            # ok | unchanged | rejected_mask | skipped


@dataclass
class PipelineResult:
    document: List[Any]
    changed: List[SpanRecord] = field(default_factory=list)
    skipped: List[SpanRecord] = field(default_factory=list)
    n_blocks: int = 0
    n_units: int = 0
    n_sent: int = 0
    provider_seconds: float = 0.0
    total_seconds: float = 0.0
    provider_name: str = ""


def _iter_pages(doc):
    """Support both [[block,...]] (pages) and [block,...] (single page)."""
    if doc and isinstance(doc[0], dict):
        return [doc]              # single, un-paged list of blocks
    return doc                    # list of pages


def correct_document(doc: List[Any], provider: CorrectionProvider,
                     options: PipelineOptions | None = None) -> PipelineResult:
    options = options or PipelineOptions()
    t_start = time.time()
    corrected = copy.deepcopy(doc)
    pages = _iter_pages(corrected)

    res = PipelineResult(document=corrected, provider_name=getattr(provider, "name", "?"))

    segs: Dict[tuple, Any] = {}          # (pi,bi) -> (segmented, corr_map, block)
    meta: List[tuple] = []               # (pi,bi,unit,mask_result)
    payload: List[str] = []

    for pi, page in enumerate(pages):
        for bi, block in enumerate(page):
            res.n_blocks += 1
            seg = segment_block(block)
            corr_map: Dict[int, str] = {}
            segs[(pi, bi)] = (seg, corr_map, block)
            for u in seg.units:
                res.n_units += 1
                u.classification = classify(u.text)
                if is_correctable(u.classification):
                    mr = MASKER.mask(u.text)
                    meta.append((pi, bi, u, mr))
                    payload.append(mr.text)
                else:
                    res.skipped.append(SpanRecord(
                        page=pi, block=bi, block_index=block.get("index", bi),
                        label=block.get("label", ""), role=u.role,
                        classification=u.classification, before=u.text,
                        after=u.text, status="skipped"))

    # ── one batched provider call ──
    res.n_sent = len(payload)
    t0 = time.time()
    outs = provider.correct_batch(payload) if payload else []
    res.provider_seconds = time.time() - t0

    for (pi, bi, u, mr), out in zip(meta, outs):
        seg, corr_map, block = segs[(pi, bi)]
        if not MASKER.placeholders_intact(out, mr):
            final, status = u.text, "rejected_mask"
        else:
            final, status = MASKER.restore(out, mr), "ok"
        corr_map[u.id] = final
        rec = SpanRecord(page=pi, block=bi, block_index=block.get("index", bi),
                         label=block.get("label", ""), role=u.role,
                         classification=u.classification, before=u.text,
                         after=final, status=status)
        if final != u.text:
            res.changed.append(rec)
        # rejected spans are also surfaced so reviewers can see them
        elif status == "rejected_mask":
            res.changed.append(rec)

    # ── render corrected_content for every block (preserving all other fields) ──
    for (pi, bi), (seg, corr_map, block) in segs.items():
        block[options.add_field] = seg.render(corr_map)

    res.total_seconds = time.time() - t_start
    return res
