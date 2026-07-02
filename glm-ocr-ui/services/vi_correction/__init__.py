"""Vietnamese OCR post-correction (optional, user-triggered).

Document-agnostic: masks protected tokens, corrects only Vietnamese
natural-language spans block-by-block (Markdown/HTML/table structure preserved),
restores protected tokens, and validates the structure is unchanged. Never
overwrites raw OCR — it adds `corrected_content` and re-renders Markdown/text.

Providers are modular and load either a HuggingFace id or a local path:
    protonx (nano/distilled/full), bmd1905, mock.
"""

from .service import (  # noqa: F401
    PROVIDERS,
    list_providers,
    build_provider,
    normalize_input,
    run_correction,
)
from .pipeline import correct_document, PipelineOptions  # noqa: F401
from .validation import validate_document  # noqa: F401
from .renderers import blocks_to_markdown, blocks_to_text  # noqa: F401
