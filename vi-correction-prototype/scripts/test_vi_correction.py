#!/usr/bin/env python3
"""Isolated test harness for the Vietnamese post-OCR correction prototype.

Usage:
    python scripts/test_vi_correction.py --input tests/correction/sample_receipt_glm.json --provider mrlasdt
    python scripts/test_vi_correction.py --input tests/correction/sample_receipt_glm.json --provider bmd1905
    python scripts/test_vi_correction.py --input tests/correction/sample_receipt_glm.json --provider mock

Outputs: corrected JSON (written to --output), raw-vs-corrected diff, timing,
list of changed spans, list of skipped/protected spans, and a validation report.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import sys
import time

# make the package importable no matter the CWD
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from vicorrect.pipeline import correct_document, PipelineOptions       # noqa: E402
from vicorrect.validation import validate_document                     # noqa: E402
from vicorrect.providers import get_provider, PROVIDER_NAMES           # noqa: E402


def _c(s, code):
    return f"\033[{code}m{s}\033[0m" if sys.stdout.isatty() else str(s)


def _blocks(doc):
    pages = [doc] if (doc and isinstance(doc[0], dict)) else doc
    return [b for page in pages for b in page]


def main() -> int:
    ap = argparse.ArgumentParser(description="Vietnamese post-OCR correction prototype tester")
    ap.add_argument("--input", required=True, help="structured OCR JSON")
    ap.add_argument("--provider", required=True, help="provider: " + ", ".join(PROVIDER_NAMES))
    ap.add_argument("--output", default=None, help="corrected JSON path (default: <input>.corrected.<provider>.json)")
    ap.add_argument("--device", default=None, help="cpu | cuda | auto (model providers)")
    ap.add_argument("--model", default=None, help="model id or local path (bmd1905/protonx)")
    ap.add_argument("--num-beams", type=int, default=None, help="beam search width (protonx)")
    ap.add_argument("--max-new-tokens", type=int, default=None, help="generation cap (protonx)")
    ap.add_argument("--max-length", type=int, default=512)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--stdout", action="store_true", help="also print corrected JSON to stdout")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        doc = json.load(f)

    out_path = args.output or f"{os.path.splitext(args.input)[0]}.corrected.{args.provider}.json"

    print("=" * 78)
    print(f" Vietnamese post-OCR correction  |  provider={args.provider}  input={args.input}")
    print("=" * 78)

    # ── provider setup + availability ──
    kwargs = {}
    if args.provider.lower() in ("bmd1905", "bmd", "b"):
        kwargs = {"device": args.device, "max_length": args.max_length, "batch_size": args.batch_size}
        if args.model:
            kwargs["model_id"] = args.model
    elif args.provider.lower() in ("protonx", "proton", "px"):
        kwargs = {"device": args.device, "batch_size": args.batch_size}
        if args.model:
            kwargs["model_id"] = args.model
        if args.num_beams is not None:
            kwargs["num_beams"] = args.num_beams
        if args.max_new_tokens is not None:
            kwargs["max_new_tokens"] = args.max_new_tokens
    elif args.provider.lower() in ("mrlasdt", "a"):
        kwargs = {"device": args.device or "cpu"}
    provider = get_provider(args.provider, **kwargs)

    ok, reason = provider.available()
    print(f"\n[provider] name={provider.name}  installed/available={ok}")
    if not ok:
        print(_c(f"[provider] UNAVAILABLE: {reason}", "31"))
        print("\nRESULT: provider could not run — see reason above. No correction performed.")
        return 0

    # warmup so timing reflects inference, not model load
    t_load0 = time.time()
    try:
        provider.warmup()
    except Exception as e:
        print(_c(f"[provider] failed during warmup/load: {e}", "31"))
        return 0
    load_s = time.time() - t_load0
    print(f"[provider] model load/warmup: {load_s:.2f}s")

    # ── run pipeline ──
    result = correct_document(doc, provider, PipelineOptions())

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result.document, f, ensure_ascii=False, indent=2)

    # ── timing ──
    print("\n── timing ─────────────────────────────────────────────────────────────")
    print(f"  blocks={result.n_blocks}  units={result.n_units}  spans_sent={result.n_sent}")
    print(f"  provider inference: {result.provider_seconds:.3f}s"
          + (f"  ({result.provider_seconds / result.n_sent * 1000:.0f} ms/span)" if result.n_sent else ""))
    print(f"  pipeline total    : {result.total_seconds:.3f}s")

    # ── changed spans ──
    print("\n── changed spans ──────────────────────────────────────────────────────")
    if not result.changed:
        print("  (none)")
    for r in result.changed:
        tag = "REJECTED(mask broke)" if r.status == "rejected_mask" else "changed"
        print(f"  [p{r.page} idx={r.block_index} {r.label}/{r.role} {r.classification}] ({tag})")
        print(f"      - {r.before}")
        print(f"      + {r.after}")

    # ── skipped / protected spans ──
    print("\n── skipped / protected spans ──────────────────────────────────────────")
    if not result.skipped:
        print("  (none)")
    by_cat: dict = {}
    for r in result.skipped:
        by_cat.setdefault(r.classification, []).append(r.before)
    for cat, items in sorted(by_cat.items()):
        shown = ", ".join(repr(x) for x in items[:8])
        more = f"  (+{len(items) - 8} more)" if len(items) > 8 else ""
        print(f"  {cat}: {shown}{more}")

    # ── raw vs corrected diff (per changed block) ──
    print("\n── raw vs corrected (per block) ───────────────────────────────────────")
    o_blocks = _blocks(doc)
    c_blocks = _blocks(result.document)
    any_diff = False
    for ob, cb in zip(o_blocks, c_blocks):
        raw = ob.get("content", "") or ""
        cor = cb.get("corrected_content", "") or ""
        if raw != cor:
            any_diff = True
            print(f"  idx={ob.get('index')} ({ob.get('label')}):")
            for line in difflib.unified_diff(raw.splitlines() or [raw], cor.splitlines() or [cor],
                                             lineterm="", n=0, fromfile="raw", tofile="corrected"):
                if line.startswith(("---", "+++", "@@")):
                    continue
                print("     " + _c(line, "31" if line.startswith("-") else "32"))
    if not any_diff:
        print("  (no textual changes)")

    # ── validation ──
    print("\n── validation report ──────────────────────────────────────────────────")
    vrep = validate_document(doc, result.document)
    for c in vrep.checks:
        mark = _c("PASS", "32") if c.ok else _c("FAIL", "31")
        print(f"  [{mark}] {c.name}" + (f"  — {c.detail}" if c.detail else ""))
    print("\n" + ("=" * 78))
    overall = _c("VALIDATION PASSED", "32") if vrep.passed else _c("VALIDATION FAILED", "31")
    print(f" {overall}   corrected JSON -> {out_path}")
    print("=" * 78)

    return 0 if vrep.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
