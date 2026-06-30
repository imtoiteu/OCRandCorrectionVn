"""
SmartDocs Platform — OCR Service
================================
Standard OCR is the canonical PaddleOCR/engine path.

The optional LLM-based post-correction ("AI Cleanup" / Smart OCR) was removed:
this module now performs pure OCR extraction only and has no LLM dependency.
"""

import logging

from services import ocr_service

logger = logging.getLogger(__name__)


def run_standard_ocr(image_path: str, engine_name: str | None = None) -> dict:
    """Run OCR with the selected engine."""
    result = ocr_service.run_ocr(image_path, engine_name=engine_name)
    result["ai_enhancement"] = False
    result["smart_applied"] = False
    result["smart_flow"] = "standard_only"
    return result


def run_ocr_pipeline(
    image_path: str,
    engine_name: str | None = None,
    apply_ai: bool = False,
    standard_result: dict | None = None,
) -> dict:
    """Run the OCR pipeline.

    Pure OCR extraction only. ``apply_ai`` is accepted for backward-compatible
    call sites but is ignored — the LLM post-correction path has been removed.
    """
    return run_standard_ocr(image_path, engine_name=engine_name)
