# vicorrect — Vietnamese Post-OCR Correction (isolated prototype)

A **document-type-agnostic** module that takes structured OCR JSON (GLM-OCR or any
engine that emits blocks with `content` + geometry) and produces the **same JSON
with an added `corrected_content` field per block**. It never overwrites `content`
and never touches geometry/metadata.

> Status: **isolated prototype**. NOT wired into the SmartDocs OCR UI or the OCR
> flow. Nothing here modifies the production app.

## Why it is general (not invoice/receipt-specific)

The pipeline has **no** document-type rules. It works block-by-block:

1. **Segmentation** (`segmentation.py`) — splits a block into correctable units
   while preserving structure:
   - HTML: only **text nodes between tags** become units; tags/attributes are kept
     byte-for-byte → tables stay valid, row/col counts can't change.
   - Markdown tables: split each row on `|`, correct each **cell** separately,
     rebuild with the same number of columns.
   - Text/Markdown: split by line; preserve leading indent + heading (`#`),
     bullet (`-`/`*`/`+`) and numbering (`1.`) markers; only the text after the
     marker is correctable.
2. **Classification** (`classification.py`) — labels each span:
   `natural_language_vi`, `natural_language_mixed`, `numeric_or_money`,
   `date_or_time`, `id_or_code`, `formula_or_symbolic`, `url_or_email_or_domain`,
   `table_header`, `table_cell_text`, `unknown`.
3. **Masking** (`masking.py`) — before a span is sent, protected tokens are
   replaced with opaque placeholders `⟦n⟧`: numbers, money, percentages, dates,
   times, IDs/`#codes`, alphanumeric codes, ranges, units, URLs, emails, domains,
   formulas, code spans, Markdown links/images, HTML tags. Restored verbatim after.
4. **Provider** (`providers/`) — only `natural_language_*` (and Vietnamese table
   cells) are sent, through the generic interface `correct_text(str) -> str`.
5. **Safe restore** — if a provider mangles a placeholder, that span's correction
   is **rejected** and the original text kept (default = safe, not creative).
6. **Validation** (`validation.py`) — checks structure + that protected tokens,
   HTML tags, and Markdown table shape are unchanged, geometry preserved, and
   `corrected_content` is present/non-empty.

The design is reusable for receipts, contracts, admin docs, scanned books, forms,
tables, mixed VI/EN, and technical docs — add more samples under `tests/correction/`.

## Generic provider interface

```python
class CorrectionProvider:
    def correct_text(self, text: str) -> str: ...
    def correct_batch(self, texts: list[str]) -> list[str]: ...
    def available(self) -> tuple[bool, str]: ...
```

The pipeline depends **only** on this interface — it is not coupled to either repo.

### Providers

| name      | repo / model | how it runs | status |
|-----------|--------------|-------------|--------|
| `mrlasdt` | [mrlasdt/vietnamese-ocr-error-corrector](https://github.com/mrlasdt/vietnamese-ocr-error-corrector) (cloned to `vendor/mrlasdt`) | `from main import Corrector; Corrector(...)(text, "ocr")` — seq2seq weights `weights/seq2seq_*.pth` | **weights not shipped / no download link → OCR corrector cannot load.** Adapter reports this via `available()`. |
| `bmd1905` | [bmd1905/vietnamese-correction](https://github.com/bmd1905/vietnamese-correction), model **`bmd1905/vietnamese-correction-v2`** (BARTpho) | `transformers.pipeline("text2text-generation", model=...)` | model auto-downloads from HuggingFace. |
| `mock`    | — | offline test double (NFC + tiny general confusion dict) | for running the pipeline without any ML model. **Not** the correction design. |

> **Model version used for Provider B:** `bmd1905/vietnamese-correction-v2` — the
> repo README explicitly recommends v2 over the original.

## Licensing

Neither repo states a clear license in its README/repo root at the time of testing:
- `mrlasdt/vietnamese-ocr-error-corrector` — **license unclear / needs later review.**
- `bmd1905/vietnamese-correction` (+ `vietnamese-correction-v2` model card) —
  **license unclear / needs later review.**

Per instruction, this does not block the technical prototype; licensing must be
confirmed before any production integration.

## Run

```bash
# offline logic check (no model needed):
python scripts/test_vi_correction.py --input tests/correction/sample_receipt_glm.json --provider mock

# real providers (needs the venv with torch+transformers):
python scripts/test_vi_correction.py --input tests/correction/sample_receipt_glm.json --provider mrlasdt
python scripts/test_vi_correction.py --input tests/correction/sample_receipt_glm.json --provider bmd1905
```

Outputs: corrected JSON (`<input>.corrected.<provider>.json`), raw-vs-corrected
diff, timing, changed spans, skipped/protected spans, and a validation report.

## What is general vs sample-specific

- **General (reusable):** everything in `vicorrect/` — segmentation, classification,
  masking/restore, pipeline, validation, provider interface + adapters.
- **Sample-specific (test data only):** `tests/correction/sample_receipt_glm.json`
  and the reference expectations used to *eyeball* quality. No receipt rules live in
  the module. Add `sample_contract.json`, `sample_admin_doc.json`,
  `sample_book_page.json`, `sample_table.json`, `sample_mixed_vi_en.json`,
  `sample_formula_doc.json`, … and run the same harness.

## Layout

```
vicorrect/
  masking.py         classification.py   segmentation.py
  pipeline.py        validation.py
  providers/  base.py registry.py bmd1905_provider.py mrlasdt_provider.py mock_provider.py
scripts/test_vi_correction.py
tests/correction/sample_receipt_glm.json
vendor/            # cloned candidate repos (gitignored)
```
