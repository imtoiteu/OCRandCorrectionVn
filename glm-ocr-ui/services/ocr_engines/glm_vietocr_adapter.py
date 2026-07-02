"""GLM Layout + VietOCR Text — reworked spatial-assignment hybrid engine.

Algorithm (v2)
==============
OLD (broken): crop each GLM paragraph → send one big multi-line image to VietOCR
  → bad: VietOCR is a *line-level* recogniser; multi-line crops produce garbage.

NEW (this file):
  1. Run GLM-OCR for layout only  (bbox, polygon, label, reading order,
                                   layout_vis images, markdown scaffold).
  2. Run the existing VietOCR *full-page* pipeline (PaddleOCR text-line
     detector → VietOCR per-line recogniser) on the SAME source image.
     This produces a flat list of short, high-quality line-level results.
  3. Spatially assign every VietOCR line to the GLM block whose pixel bbox
     contains the line's centre point (cx, cy). Lines not covered by any
     GLM block are collected into a "remainder" block at the end.
  4. Within each GLM block, assigned lines are sorted top→bottom then
     left→right and joined with newlines → vietocr_content.
  5. Sanity checks before accepting VietOCR text:
       • vietocr_content must not be empty.
       • Assigned line count must be ≥ 1.
       • vietocr_content must be ≥ SANITY_MIN_RATIO × len(glm_plain) chars
         when glm_plain is long (avoids replacing a 200-char paragraph with
         a 3-char token).
     On failure the block falls back to GLM plain text.
  6. Table / figure / formula / code / image labels: skip VietOCR entirely
     and preserve GLM content verbatim.

Per-block fields
-----------------
  text               final chosen text
  content            same as text
  glm_content        raw GLM content (may be HTML for tables)
  vietocr_content    VietOCR joined lines  ('' when skipped/failed)
  vietocr_lines      list of raw VietOCR line dicts assigned to this block
  assigned_line_count number of VietOCR lines assigned
  recognition_source "vietocr" | "glm" | "fallback"
  fallback_reason    reason string when recognition_source != "vietocr"
  layout_source      "glm"
  label / native_label
  index / bbox_2d / polygon / box
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from config import cfg

from .base import OCREngine
from .glm_adapter import GLMOCREngine, _scale_box, _strip_html, _HTML_LABELS

logger = logging.getLogger(__name__)

# Block labels where we skip VietOCR and keep GLM content verbatim.
_SKIP_VIETOCR_LABELS: frozenset[str] = frozenset({
    "table", "figure", "image", "equation", "formula", "code",
})

# If the GLM block plain-text is longer than this many characters AND the
# VietOCR result is shorter than SANITY_MIN_RATIO × glm_plain length,
# reject the VietOCR result as a likely failure.
_SANITY_LONG_THRESHOLD = 40    # chars — below this we accept any VietOCR result
_SANITY_MIN_RATIO      = 0.25  # VietOCR must be ≥ 25 % of GLM length


def _pt_in_box(cx: float, cy: float, box: list) -> bool:
    """Return True if (cx, cy) is inside the axis-aligned bounding rect
    of a pixel-space polygon [[x,y],...].
    """
    if not box:
        return False
    xs = [p[0] for p in box]
    ys = [p[1] for p in box]
    return min(xs) <= cx <= max(xs) and min(ys) <= cy <= max(ys)


def _line_centre(box: list) -> tuple[float, float]:
    """Return (cx, cy) of a line bounding-box polygon [[x,y],...]."""
    xs = [p[0] for p in box]
    ys = [p[1] for p in box]
    return (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0


def _sort_lines(lines: list[dict]) -> list[dict]:
    """Sort a list of VietOCR line dicts top→bottom, then left→right."""
    def key(ln):
        box = ln.get("box") or []
        if not box:
            return (0, 0)
        cx, cy = _line_centre(box)
        return (cy, cx)
    return sorted(lines, key=key)


def _sanity_ok(vietocr_text: str, glm_plain: str) -> tuple[bool, str]:
    """Return (True, '') or (False, reason) for the sanity check."""
    if not vietocr_text.strip():
        return False, "vietocr_empty"
    if len(glm_plain) > _SANITY_LONG_THRESHOLD:
        ratio = len(vietocr_text) / max(len(glm_plain), 1)
        if ratio < _SANITY_MIN_RATIO:
            return False, f"too_short_ratio={ratio:.2f}"
    return True, ""


class GLMVietOCREngine(OCREngine):
    """GLM layout + VietOCR line-level recognition hybrid.

    Uses GLM-OCR for document structure and VietOCR's standalone full-page
    pipeline (PaddleOCR detection + VietOCR per-line recognition) for text
    quality. VietOCR lines are spatially assigned to GLM layout blocks.
    """

    engine_name = "glm_vietocr"

    def __init__(self) -> None:
        self._glm = GLMOCREngine()
        # VietOCR components are loaded lazily.
        self._detector  = None
        self._predictor = None

    # ── VietOCR detector (PaddleOCR) ─────────────────────────────────────
    def _get_detector(self):
        if self._detector is None:
            from paddleocr import PaddleOCR
            self._detector = PaddleOCR(
                ocr_version="PP-OCRv5",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
            )
        return self._detector

    # ── VietOCR text recogniser ───────────────────────────────────────────
    def _get_predictor(self):
        if self._predictor is None:
            from vietocr.tool.predictor import Predictor
            from .vietocr_adapter import (
                _resolve_vietocr_config,
                _resolve_vietocr_weights,
            )
            config = _resolve_vietocr_config()
            config["cnn"]["pretrained"]       = False
            config["device"]                  = cfg.VIETOCR_DEVICE or "cpu"
            config["predictor"]["beamsearch"] = False
            config["weights"]                 = _resolve_vietocr_weights()
            config["quiet"]                   = True
            logger.info(
                "GLMVietOCR: loading VietOCR predictor device=%s", config["device"]
            )
            self._predictor = Predictor(config)
        return self._predictor

    # ── VietOCR full-page pipeline ────────────────────────────────────────
    def _run_vietocr_lines(self, image_path: str, image) -> list[dict]:
        """Run PaddleOCR detection + VietOCR recognition on the full page.

        Returns a list of dicts:
          { "text": str, "box": [[x,y],...], "confidence": None }
        matching the standard results schema. Empty list on any failure.
        """
        from .vietocr_adapter import VietOCREngine as _VietOCRHelper

        detector  = self._get_detector()
        predictor = self._get_predictor()

        try:
            detected = detector.predict(image_path)
        except Exception as exc:
            logger.error("GLMVietOCR: PaddleOCR detect failed: %s", exc)
            return []

        lines: list[dict] = []
        for res in detected:
            boxes = res.get("det_polys", res.get("dt_polys", []))
            for poly in boxes:
                polygon = poly.tolist() if hasattr(poly, "tolist") else poly
                # Crop the line region
                crop = _VietOCRHelper._crop_polygon(image, polygon)
                if crop is None:
                    continue
                try:
                    text = predictor.predict(crop) or ""
                except Exception as exc:
                    logger.warning("GLMVietOCR: VietOCR predict failed: %s", exc)
                    self._predictor = None   # reset so next call retries
                    text = ""
                lines.append({
                    "text":       text.strip(),
                    "box":        polygon,
                    "confidence": None,
                })
        return lines

    # ── Spatial assignment ────────────────────────────────────────────────
    @staticmethod
    def _assign_lines_to_blocks(
        vietocr_lines: list[dict],
        glm_blocks: list[dict],   # each has "box" (pixel polygon) + original fields
    ) -> dict[int, list[dict]]:
        """Assign each VietOCR line to a GLM block index by centre-point containment.

        Returns a dict mapping block_index → [list of assigned line dicts].
        Unmatched lines are keyed to -1.
        """
        assignment: dict[int, list[dict]] = {-1: []}
        for idx in range(len(glm_blocks)):
            assignment[idx] = []

        for line in vietocr_lines:
            if not line.get("text"):
                continue
            box = line.get("box")
            if not box:
                assignment[-1].append(line)
                continue
            cx, cy = _line_centre(box)
            matched = False
            for idx, blk in enumerate(glm_blocks):
                blk_box = blk.get("box")
                if blk_box and _pt_in_box(cx, cy, blk_box):
                    assignment[idx].append(line)
                    matched = True
                    break
            if not matched:
                assignment[-1].append(line)

        return assignment

    # ── Main pipeline ──────────────────────────────────────────────────────
    def run(self, image_path: str) -> dict:
        from PIL import Image

        # ── Step 1: GLM layout ─────────────────────────────────────────────
        t_total = time.time()
        glm_res = self._glm.run(image_path)
        if not glm_res.get("success"):
            glm_res["ocr_engine"] = self.engine_name
            return glm_res

        w: int = glm_res["img_width"]
        h: int = glm_res["img_height"]
        raw_json: list = glm_res.get("raw_json") or []

        # ── Step 2: open image ─────────────────────────────────────────────
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as exc:
            logger.error("GLMVietOCR: cannot open image: %s", exc)
            glm_res["ocr_engine"] = self.engine_name
            return glm_res

        # ── Step 3: VietOCR full-page pipeline ────────────────────────────
        t_viet = time.time()
        vietocr_lines = self._run_vietocr_lines(image_path, image)
        logger.info(
            "GLMVietOCR: VietOCR produced %d lines in %.1fs",
            len(vietocr_lines), time.time() - t_viet,
        )

        # ── Step 4: Parse GLM JSON → build block list for assignment ──────
        glm_blocks_raw: list[dict] = []  # ordered, with box already computed
        tables_html: list[str] = []
        order = 0

        for page in (raw_json or []):
            for region in (page or []):
                if not isinstance(region, dict):
                    continue
                label       = (region.get("label") or "text").lower()
                glm_content = str(region.get("content") or "")
                box         = _scale_box(region, w, h)
                glm_plain   = (
                    _strip_html(glm_content) if label in _HTML_LABELS else glm_content
                )
                if label in _HTML_LABELS and "<table" in glm_content.lower():
                    tables_html.append(glm_content)

                glm_blocks_raw.append({
                    "_region":    region,
                    "_label":     label,
                    "_glm_content": glm_content,
                    "_glm_plain": glm_plain,
                    "box":        box,
                    "_order":     region.get("index", order),
                })
                order += 1

        # ── Step 5: Spatial assignment ─────────────────────────────────────
        assignment = self._assign_lines_to_blocks(vietocr_lines, glm_blocks_raw)

        # ── Step 6: Build final result blocks ──────────────────────────────
        items: list[dict]       = []
        layout_blocks: list[dict] = []
        idx_counter = 0

        for blk_idx, blk in enumerate(glm_blocks_raw):
            region      = blk["_region"]
            label       = blk["_label"]
            glm_content = blk["_glm_content"]
            glm_plain   = blk["_glm_plain"]
            box         = blk["box"]
            blk_order   = blk["_order"]

            assigned_lines = _sort_lines(assignment.get(blk_idx, []))
            vietocr_text   = "\n".join(
                ln["text"] for ln in assigned_lines if ln.get("text")
            )

            # Determine final text
            recog_source   = "glm"
            fallback_reason = ""
            vietocr_content = ""

            if label in _SKIP_VIETOCR_LABELS:
                # Keep GLM verbatim — skip VietOCR entirely
                fallback_reason = "skip_label"
                final_text = glm_plain
            elif not vietocr_lines:
                # VietOCR pipeline produced nothing (engine error)
                fallback_reason = "vietocr_pipeline_failed"
                final_text = glm_plain
            else:
                ok, reason = _sanity_ok(vietocr_text, glm_plain)
                if ok:
                    recog_source    = "vietocr"
                    vietocr_content = vietocr_text
                    final_text      = vietocr_text
                else:
                    fallback_reason = reason
                    recog_source    = "fallback"
                    final_text      = glm_plain

            item: dict = {
                # Standard frontend fields
                "text":               final_text,
                "content":            final_text,
                "confidence":         None,
                "box":                box,
                # Dual provenance (JSON tab)
                "glm_content":        glm_content,
                "vietocr_content":    vietocr_content,
                "vietocr_lines":      assigned_lines,
                "assigned_line_count": len(assigned_lines),
                # Geometry / metadata
                "label":             region.get("label"),
                "native_label":      region.get("label"),
                "index":             blk_order,
                "bbox_2d":           region.get("bbox_2d"),
                "polygon":           region.get("polygon"),
                # Engine provenance
                "layout_source":          "glm",
                "recognition_source":     recog_source,
                "fallback_reason":        fallback_reason,
            }
            items.append(item)

            layout_blocks.append({
                "label":              region.get("label"),
                "content":            final_text,
                "glm_content":        glm_content,
                "vietocr_content":    vietocr_content,
                "bbox":               region.get("bbox_2d"),
                "order":              blk_order,
                "recognition_source": recog_source,
                "assigned_line_count": len(assigned_lines),
            })
            idx_counter += 1

        # ── Step 7: Remainder lines (not inside any GLM block) ─────────────
        remainder = _sort_lines(assignment.get(-1, []))
        if remainder:
            rem_text = "\n".join(ln["text"] for ln in remainder if ln.get("text"))
            if rem_text.strip():
                items.append({
                    "text":               rem_text,
                    "content":            rem_text,
                    "confidence":         None,
                    "box":                None,
                    "glm_content":        "",
                    "vietocr_content":    rem_text,
                    "vietocr_lines":      remainder,
                    "assigned_line_count": len(remainder),
                    "label":              "text",
                    "native_label":       "text",
                    "index":              idx_counter,
                    "bbox_2d":            None,
                    "polygon":            None,
                    "layout_source":      "vietocr_unmatched",
                    "recognition_source": "vietocr",
                    "fallback_reason":    "",
                })

        # ── Step 8: Rebuild markdown with chosen text ──────────────────────
        glm_markdown = glm_res.get("markdown", "") or ""
        markdown = _rebuild_markdown(glm_markdown, items)

        elapsed_ms = round((time.time() - t_total) * 1000)

        return {
            "success":          True,
            "results":          items,
            "img_width":        w,
            "img_height":       h,
            "elapsed_ms":       elapsed_ms,
            "ocr_engine":       self.engine_name,   # "glm_vietocr"
            "inference_status": "ok",
            # GLM-compatible fields (Images tab, JSON tab, layout)
            "layout_native":    True,
            "markdown":         markdown,
            "tables_html":      tables_html,
            "layout_blocks":    layout_blocks,
            "images":           glm_res.get("images") or [],
            # JSON tab: expose structured data including dual content
            "raw_json": {
                "engine":        "glm_vietocr",
                "layout_source": "glm",
                "recognition":   "vietocr_line_level",
                "blocks":        layout_blocks,
                "vietocr_lines": vietocr_lines,
                "glm_raw":       raw_json,
            },
        }


# ── Markdown rebuilder ─────────────────────────────────────────────────────

def _rebuild_markdown(glm_md: str, items: list[dict]) -> str:
    """Return a markdown string where GLM text fragments are replaced by
    their VietOCR-corrected equivalents where available.

    Strategy:
    1. If GLM markdown is non-empty: do literal substring substitution for
       each block where glm_content appears verbatim in the markdown.
    2. If GLM markdown is empty (or nothing survived substitution): fall
       back to synthesising markdown from block labels and final text.
    """
    if not glm_md:
        return _synthesise_markdown(items)

    result = glm_md
    for item in items:
        glm_raw  = (item.get("glm_content") or "").strip()
        final    = (item.get("text") or "").strip()
        if not glm_raw or not final or glm_raw == final:
            continue
        if glm_raw in result:
            result = result.replace(glm_raw, final, 1)

    # If the result still looks empty after substitution, synthesise.
    if not result.strip():
        return _synthesise_markdown(items)
    return result


def _synthesise_markdown(items: list[dict]) -> str:
    """Build minimal markdown from block labels and final text."""
    lines: list[str] = []
    for item in items:
        text  = (item.get("text") or "").strip()
        if not text:
            continue
        label = (item.get("label") or "text").lower()
        if label == "title":
            lines.append(f"# {text}")
        elif label in ("table",):
            lines.append(text)
        else:
            lines.append(text)
    return "\n\n".join(lines)
