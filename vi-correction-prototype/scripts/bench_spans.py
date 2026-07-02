#!/usr/bin/env python3
"""Minimal per-span benchmark for a correction provider.

Runs a handful of representative Vietnamese spans through the real pipeline steps
(mask -> provider -> restore) ONE AT A TIME, reporting per-span latency, quality,
and protected-token preservation. Intended for a quick quality/latency read before
committing to a full-document run on a slow CPU.

    python scripts/bench_spans.py --provider protonx --model distilled --device cpu \
        --num-beams 4 --max-new-tokens 96
"""

from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from vicorrect.masking import MASKER              # noqa: E402
from vicorrect.classification import classify     # noqa: E402
from vicorrect.providers import get_provider      # noqa: E402

# Default representative spans (OCR-noisy Vietnamese; no protected tokens in most).
DEFAULT_SPANS = [
    "HÓA DỘN THANH TOÁN",
    "Thành tiện",
    "Tông tiện",
    "+Thanh toán tiện mát",
    "ĐJA chi: Đường Nguyễn Văn Thoa,i, Phương Phước Mỹ, Quân Sơn Trà, Đà Nẵng, Việt Nam",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True)
    ap.add_argument("--model", default=None, help="model id or local path (alias: distilled|base|nano)")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--num-beams", type=int, default=None)
    ap.add_argument("--max-new-tokens", type=int, default=None)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--spans-file", default=None, help="optional text file, one span per line")
    args = ap.parse_args()

    try:
        import torch
        torch.set_num_threads(args.threads)
    except Exception:
        pass

    spans = DEFAULT_SPANS
    if args.spans_file:
        with open(args.spans_file, encoding="utf-8") as f:
            spans = [ln.rstrip("\n") for ln in f if ln.strip()]

    kwargs = {"device": args.device}
    if args.model:
        kwargs["model_id"] = args.model
    if args.num_beams is not None:
        kwargs["num_beams"] = args.num_beams
    if args.max_new_tokens is not None:
        kwargs["max_new_tokens"] = args.max_new_tokens
    provider = get_provider(args.provider, **kwargs)

    ok, reason = provider.available()
    print(f"[provider] {provider.name}  available={ok}")
    if not ok:
        print(f"[provider] UNAVAILABLE: {reason}")
        return 0

    t0 = time.time()
    provider.warmup()
    print(f"[model load] {time.time() - t0:.1f}s   beams={getattr(provider,'num_beams','?')} "
          f"max_new_tokens={getattr(provider,'max_new_tokens','?')} threads={args.threads}\n")

    total = 0.0
    for raw in spans:
        cat = classify(raw)
        mr = MASKER.mask(raw)
        t = time.time()
        out = provider.correct_text(mr.text)
        dt = time.time() - t
        total += dt
        intact = MASKER.placeholders_intact(out, mr)
        corrected = MASKER.restore(out, mr) if intact else raw
        changed = corrected.strip() != raw.strip()
        print(f"raw       : {raw}")
        print(f"corrected : {corrected}" + ("" if changed else "   (unchanged)"))
        print(f"class={cat}  latency={dt:.2f}s  protected={len(mr.mapping)}  "
              f"placeholders_intact={intact}")
        print("-" * 70)
    print(f"TOTAL provider time: {total:.2f}s for {len(spans)} spans "
          f"({total/len(spans):.2f}s/span avg)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
