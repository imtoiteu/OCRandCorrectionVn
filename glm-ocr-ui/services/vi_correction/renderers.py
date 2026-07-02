"""Render corrected OCR blocks back into Markdown and plain text.

Operates on the corrected document (blocks carrying `corrected_content`). Falls
back to the raw `content` for any block that was not corrected. Table blocks keep
their (corrected) HTML verbatim so structure is preserved.
"""

from __future__ import annotations

import re
from typing import Any, List

_TAG_RE = re.compile(r"<[^>]+>")


def _iter_pages(doc):
    if doc and isinstance(doc[0], dict):
        return [doc]
    return doc


def _block_text(block: dict) -> str:
    cc = block.get("corrected_content")
    if cc is None:
        cc = block.get("content", "") or ""
    return cc


def blocks_to_markdown(doc: List[Any]) -> str:
    """Corrected blocks -> Markdown. One block per paragraph, pages separated by a
    horizontal rule. Table HTML is kept as-is (Markdown renderers accept inline HTML)."""
    pages = _iter_pages(doc)
    page_chunks = []
    for page in pages:
        parts = [t for t in (_block_text(b) for b in page) if t.strip()]
        page_chunks.append("\n\n".join(parts))
    return "\n\n---\n\n".join(c for c in page_chunks if c.strip())


def _html_to_text(s: str) -> str:
    s = re.sub(r"</(tr|p|div|h\d|li)>", "\n", s, flags=re.I)
    s = re.sub(r"</t[dh]>", "\t", s, flags=re.I)
    s = _TAG_RE.sub("", s)
    s = (s.replace("&nbsp;", " ").replace("&amp;", "&")
          .replace("&lt;", "<").replace("&gt;", ">"))
    lines = [ln.strip(" \t") for ln in s.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def blocks_to_text(doc: List[Any]) -> str:
    """Corrected blocks -> plain text (HTML stripped), one block per line group."""
    pages = _iter_pages(doc)
    out = []
    for page in pages:
        for b in page:
            t = _block_text(b)
            if "<" in t and ">" in t:
                t = _html_to_text(t)
            if t.strip():
                out.append(t)
    return "\n".join(out)
