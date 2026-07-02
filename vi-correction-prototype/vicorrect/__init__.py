"""vicorrect — isolated, document-agnostic Vietnamese post-OCR correction prototype.

Layers (all engine-agnostic; none know about invoices/receipts):
    masking        — mask/restore protected tokens (numbers, dates, money, IDs,
                     URLs, emails, formulas, units, Markdown/HTML syntax).
    classification — label a text span (natural_language_vi, numeric_or_money, ...).
    segmentation   — split an OCR block into correctable units while preserving
                     structure (Markdown markers, HTML tags, table cells).
    providers      — pluggable correction backends behind `correct_text(str)->str`.
    pipeline       — orchestrates JSON-in / JSON-out, adds `corrected_content`,
                     preserves every geometry/metadata field.
    validation     — verifies structure + protected tokens survived correction.

The correction pipeline depends ONLY on the generic provider interface, never on
any specific repo/model.
"""

from .pipeline import correct_document, PipelineOptions  # noqa: F401
from .validation import validate_document  # noqa: F401
