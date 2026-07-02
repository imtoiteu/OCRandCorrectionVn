"""Structure-preserving segmentation of an OCR block into correctable units.

Rules (all generic):
  * Never send a whole HTML table or whole Markdown table to the model.
  * HTML: only the TEXT NODES between tags become units; tags/attributes are kept
    byte-for-byte, so structure & validity are preserved by construction.
  * Markdown table: split each row on `|`; each cell is a unit; column count is
    preserved because the number of `|`-separated parts never changes.
  * Plain / Markdown text: split by line; the leading indent + heading (`#`),
    bullet (`-`,`*`,`+`) or numbering (`1.`) marker is preserved literally; only
    the text after the marker is a correctable unit.

Each `Segmented` carries a `render(corrections)` that rebuilds the block content
from a `{unit_id: corrected_text}` map, falling back to the original text for any
unit that was not corrected.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class Unit:
    id: int
    text: str                 # raw correctable core (masking happens in the pipeline)
    role: str                 # text | heading | list_item | table_header | table_cell_text
    classification: str = ""  # filled by the pipeline


@dataclass
class Segmented:
    kind: str
    units: List[Unit]
    render: Callable[[Dict[int, str]], str]


_WS = re.compile(r"^(\s*)(.*?)(\s*)$", re.S)
_LINE_PREFIX = re.compile(r"^(\s*)(#{1,6}\s+|[-*+]\s+|\d+[.)]\s+)?(.*)$")
_MD_ROW = re.compile(r"^\s*\|.*\|\s*$")
_MD_SEP = re.compile(r"^\s*\|?\s*:?-{2,}.*$")
_TAG_SPLIT = re.compile(r"(<[^>]+>)")


def _split_ws(s: str):
    m = _WS.match(s)
    return m.group(1), m.group(2), m.group(3)


def _role_for_marker(marker: str) -> str:
    if marker.startswith("#"):
        return "heading"
    if marker[:1] in "-*+" or re.match(r"\d", marker):
        return "list_item"
    return "text"


def segment_block(block: dict) -> Segmented:
    content = block.get("content", "") or ""
    label = (block.get("label") or "").lower()
    if "<table" in content.lower() or "<td" in content.lower() or "<tr" in content.lower():
        return _segment_html(content)
    if label in ("table",) and ("<" in content):
        return _segment_html(content)
    if _looks_like_md_table(content):
        return _segment_md_table(content)
    return _segment_text(content)


# ── plain / markdown text ──────────────────────────────────────────────────────
def _segment_text(content: str) -> Segmented:
    lines = content.split("\n")
    units: List[Unit] = []
    template: List[dict] = []   # per line: {indent, marker, uid|None, literal}
    uid = 0
    for line in lines:
        m = _LINE_PREFIX.match(line)
        indent, marker, core = m.group(1), (m.group(2) or ""), m.group(3)
        if core.strip():
            role = _role_for_marker(marker) if marker else "text"
            units.append(Unit(id=uid, text=core, role=role))
            template.append({"indent": indent, "marker": marker, "uid": uid, "core": core})
            uid += 1
        else:
            template.append({"indent": indent, "marker": marker, "uid": None, "core": core})

    def render(corr: Dict[int, str]) -> str:
        out = []
        for t in template:
            core = corr.get(t["uid"], t["core"]) if t["uid"] is not None else t["core"]
            out.append(f"{t['indent']}{t['marker']}{core}")
        return "\n".join(out)

    return Segmented(kind="text", units=units, render=render)


# ── markdown table ─────────────────────────────────────────────────────────────
def _looks_like_md_table(content: str) -> bool:
    rows = [ln for ln in content.split("\n") if _MD_ROW.match(ln)]
    return len(rows) >= 2


def _segment_md_table(content: str) -> Segmented:
    lines = content.split("\n")
    units: List[Unit] = []
    template: List[dict] = []
    uid = 0
    header_seen = False
    for line in lines:
        if _MD_ROW.match(line) and not _MD_SEP.match(line):
            parts = line.split("|")
            role = "table_header" if not header_seen else "table_cell_text"
            header_seen = True
            cell_tpl = []
            for part in parts:
                lead, coreseg, trail = _split_ws(part)
                if coreseg:
                    units.append(Unit(id=uid, text=coreseg, role=role))
                    cell_tpl.append({"lead": lead, "uid": uid, "core": coreseg, "trail": trail})
                    uid += 1
                else:
                    cell_tpl.append({"lead": lead, "uid": None, "core": coreseg, "trail": trail})
            template.append({"type": "row", "cells": cell_tpl})
        else:
            # separator or non-table line: keep literal
            template.append({"type": "literal", "text": line})

    def render(corr: Dict[int, str]) -> str:
        out = []
        for t in template:
            if t["type"] == "literal":
                out.append(t["text"])
            else:
                segs = []
                for c in t["cells"]:
                    core = corr.get(c["uid"], c["core"]) if c["uid"] is not None else c["core"]
                    segs.append(f"{c['lead']}{core}{c['trail']}")
                out.append("|".join(segs))
        return "\n".join(out)

    return Segmented(kind="md_table", units=units, render=render)


# ── html (tables and inline markup) ────────────────────────────────────────────
def _segment_html(content: str) -> Segmented:
    parts = _TAG_SPLIT.split(content)   # alternating text / "<tag>"
    units: List[Unit] = []
    template: List[dict] = []
    uid = 0
    last_tag = ""
    for part in parts:
        if part.startswith("<") and part.endswith(">"):
            template.append({"type": "tag", "text": part})
            name = part.lower()
            if name.startswith("<th"):
                last_tag = "th"
            elif name.startswith("<td"):
                last_tag = "td"
            elif name.startswith("</td") or name.startswith("</th"):
                last_tag = ""
            continue
        if part == "":
            continue
        lead, coreseg, trail = _split_ws(part)
        if coreseg:
            role = "table_header" if last_tag == "th" else ("table_cell_text" if last_tag == "td" else "text")
            units.append(Unit(id=uid, text=coreseg, role=role))
            template.append({"type": "text", "lead": lead, "uid": uid, "core": coreseg, "trail": trail})
            uid += 1
        else:
            template.append({"type": "text", "lead": "", "uid": None, "core": part, "trail": ""})

    def render(corr: Dict[int, str]) -> str:
        out = []
        for t in template:
            if t["type"] == "tag":
                out.append(t["text"])
            elif t["uid"] is None:
                out.append(t["core"])
            else:
                core = corr.get(t["uid"], t["core"])
                out.append(f"{t['lead']}{core}{t['trail']}")
        return "".join(out)

    return Segmented(kind="html", units=units, render=render)
