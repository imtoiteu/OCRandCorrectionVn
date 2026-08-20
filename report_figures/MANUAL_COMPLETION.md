# MANUAL COMPLETION REQUIRED

This file lists every report figure that could **not** be produced completely from
the source code of `OCRandCorrectionVn`, why, and exactly what has to be supplied.

Preparation common to all screenshot figures:

```bash
# Terminal 1 (optional — only needed for the GLM-OCR engine, Apple Silicon)
cd <repo>
GLM_ROOT="$PWD/glm-ocr-server" \
GLM_MLX_PYTHON="$PWD/glm-ocr-server/.venv-mlx/bin/python" \
bash glm-ocr-ui/tools/glm_serve.sh          # serves :8080

# Terminal 2
cd <repo>/glm-ocr-ui && source .venv/bin/activate && python app.py
# open http://localhost:5001   ·   user / user123   ·   admin / admin123
```

Capture rules for a consistent report:

* Use **one browser at one fixed viewport** for every screenshot — 1440 × 900 is a
  good choice; do not resize between captures.
* Set the interface language once (the language selector in the navigation bar) and
  keep it for all figures.
* Use the **same document** across Figures 3.4, 3.8, 4.3 and 4.4 wherever possible,
  so the reader can follow one document through the report.
* Crop to the browser content area (no OS chrome, no bookmarks bar).
* Export as PNG at 2× device pixel ratio, then insert into Word at 100 % width of
  the text column; do not upscale a small capture.
* Blank or replace any personal data before publishing.

---

## Figure 3.3 — Giao diện đăng nhập và trang làm việc chính

**Why it cannot be generated:** it is a screen capture of a rendered interface
(`templates/login.html`, `static/index.html`). Reconstructing pixels from HTML/CSS
would be a fabricated mock-up, not the real interface.

**Where it goes in the report:** Chapter 3, section on the interface implementation
(caption line "Hình 3.3" in the DOCX).

**Screenshot checklist**

1. Open a private/incognito window at `http://localhost:5001` — you are redirected
   to the login page. Capture the **complete login form** (username field, password
   field, submit button, any error area).
2. Log in as `user / user123`.
3. Capture the **home view** (`#home`): navigation bar (Home · OCR · Documents ·
   language · Sign out) and the tool cards.
4. Place the two captures side by side, label them **a)** and **b)**.
5. Use the same viewport for both.

Optional third capture: log in as `admin / admin123` to show that the **Admin** card
and navigation link appear only for the administrator role.

---

## Figure 3.4 — Giao diện tải tài liệu, lựa chọn công cụ và xem kết quả OCR

**Why it cannot be generated:** UI capture of the OCR workspace.

**Where it goes in the report:** Chapter 3, OCR interface section.

**Screenshot checklist** (split into 3.4a and 3.4b if one image is too dense — the
report explicitly allows this)

1. `#ocr` with the empty drop zone visible → **3.4a, part 1**.
2. Upload one document (a PDF with several pages makes the page navigation
   visible). Capture the workspace immediately after upload: page preview on the
   left, toolbar with the **engine drop-down open** showing the four options
   (Recommended · GLM Layout + VietOCR Text · Vietnamese · Standard),
   Run OCR / OCR All / Stop / Reset buttons → **3.4a, part 2**.
3. Run OCR. Capture the completed state: recognition boxes drawn on the page
   canvas, the statistics strip (regions, mean confidence, time, pages) and the
   result panel → **3.4b**.

Note for the caption: `paddleocr_modern` (PP-StructureV3) is reachable through the
API but is **not** offered in the drop-down, so do not claim five selectable engines.

---

## Figure 3.5 — Giao diện quản trị người dùng, tài liệu và nhật ký hệ thống

**Why it cannot be generated:** UI capture of the Jinja admin pages.

**Where it goes in the report:** Chapter 3, administration section.

**Screenshot checklist** (log in as `admin / admin123`)

1. `/admin/` — dashboard with the four counters (total users, active users, total
   files, AI tasks) and the recent-activity list.
2. `/admin/users` — the user table with role, status and document count, and the
   create/edit/reset/disable actions visible.
3. `/admin/logs` — the activity log with the filter controls (action, user, free
   text) and at least one `ocr` row whose detail string shows the engine and
   `processing_time_ms`.
4. Optionally `/admin/files` — all documents with the user/type/status filters.

Combine as 3.5a (dashboard + users) and 3.5b (logs + files) if a single image
becomes unreadable.

---

## Figure 3.8 — Giao diện kết quả OCR theo văn bản và dữ liệu có cấu trúc

**Status:** the architecture and data flow **were** generated
(`chapter3/fig_3_8_ocr_result_representations.*`). Only the screen capture is
missing.

**Screenshot checklist**

1. Choose a document with a clear layout that contains a table (for example
   `glm-ocr-server/examples/source/table.png`).
2. Run OCR with an engine that produces structured output — **Recommended
   (glmocr)** or, through the API, `paddleocr_modern`. The legacy PaddleOCR and
   VietOCR engines produce no Markdown/HTML/table artifacts, so the structured tabs
   will fall back to plain text.
3. Capture the workspace with the **Markdown** tab active next to the page canvas.
4. Capture the **JSON** tab (and the **Images** tab if the layout overlay is
   informative).
5. If the report needs the position-matching evidence, click a region in the result
   list so the matching box highlights on the canvas, and capture that state.

---

## Figure 3.10 — Giao diện lựa chọn môi trường xử lý của ứng dụng desktop

**Status: `NOT_SUPPORTED_BY_SOURCE` — nothing can be captured or generated.**

**Why:** the repository contains no desktop application. A repository-wide search
for `tauri`, `sidecar`, `Bundled Core`, `Remote Server` and a Backend-Runtime
selector returns no application code, and there is no `src-tauri/`, `Cargo.toml` or
desktop `package.json`. The repository is exactly two applications:

* `glm-ocr-ui/` — the Flask web application (port 5001)
* `glm-ocr-server/` — the GLM-OCR SDK and the MLX model server (port 8080)

**Options for the report**

1. Supply the screenshot from the separate desktop project if it exists outside this
   repository, and add that project to the source list of Chapter 3; **or**
2. remove Figure 3.10 and the paragraphs describing the three backend modes; **or**
3. reword the paragraph as future work and mark the figure as not applicable.

Do **not** present a mock-up as an implemented screen.

---

## Figure 3.11 — Một số giao diện hoàn thiện trên WebApp và DesktopApp

**Why it cannot be generated:** montage of real screenshots; and the DesktopApp half
does not exist (see 3.10).

**Screenshot checklist (WebApp only)**

1. `#home` — the tool cards.
2. `#ocr` — a completed OCR result with the overlay boxes.
3. `#documents` — the document library with the type filters, the search box and the
   "processed" badges that come from `artifact_kinds`.
4. `/correction` — the Vietnamese correction page with a provider/model selected and
   a finished run (changed / skipped counts and the validation result visible).
5. `/admin/` — the dashboard.

Arrange as 3.11a (user-facing screens) and 3.11b (correction + administration).
State in the caption that the figure shows the WebApp; drop the DesktopApp claim
unless option 1 of Figure 3.10 applies.

---

## Figure 4.3 — Một số bước kiểm thử chức năng xử lý tài liệu

**Status:** the ten-step test procedure **was** generated
(`chapter4/fig_4_3_functional_test_steps.*`). The report additionally wants
representative captures.

**Screenshot checklist** (use one document for all four)

* **a) Tải tài liệu** — the drop zone with the file being uploaded, or the workspace
  immediately after upload showing the file name and page count.
* **b) Lựa chọn công cụ OCR** — the engine drop-down open.
* **c) Kết quả nhận dạng** — the completed result with the overlay boxes and the
  statistics strip.
* **d) Lịch sử xử lý** — `#documents` showing the saved document, or `/admin/logs`
  filtered to `action = ocr` showing the engine and `processing_time_ms`.

---

## Figure 4.4 — Minh họa kết quả OCR trên một số nhóm tài liệu

**Status: `MANUAL_COMPLETION_REQUIRED`.** A composition template was generated
(`chapter4/fig_4_4_result_examples_template.*`); it contains **no OCR output**.

**Why it cannot be generated:** the figure must show recognition output on real
documents. The repository stores GLM-OCR reference outputs, but those were produced
by the upstream GLM-OCR project, not by a run of this system, so reusing them as
"results of the system" would be misleading.

**Material that already exists in the repository**

| Group | Source file | Existing reference output |
|---|---|---|
| Clear printed text | `glm-ocr-server/examples/source/page.png` | `examples/result/page/page.json`, `page.md`, `layout_vis/` |
| Table / structured layout | `glm-ocr-server/examples/source/table.png` | `examples/result/table/table.{json,md}`, plus the recorded run `glm-ocr-server/ui/_runs/0359de69/` |
| Scientific paper | `glm-ocr-server/examples/source/paper.png` | `examples/result/paper/paper.{json,md}`, recorded runs `ui/_runs/06f98b02`, `1cedd2ac`, `25393301` |
| Handwriting (difficult) | `glm-ocr-server/examples/source/handwritten.png` | `examples/result/handwritten/handwritten.{json,md}` |
| Seal / stamp | `glm-ocr-server/examples/source/seal.png` | `examples/result/seal/seal.{json,md}` |
| Source code | `glm-ocr-server/examples/source/code.png` | `examples/result/code/code.{json,md}` |
| Multi-page PDF | `glm-ocr-server/examples/source/GLM-4.5V.pdf` | `examples/result/GLM-4.5V/` (41 pages of layout visualisations) |

**Missing and required:** a **low-quality photograph** (phone photo of a document,
skewed / uneven lighting). None exists in the repository and the report explicitly
requires at least one difficult case. Take one yourself.

**What to do**

1. Upload each chosen sample through the running application.
2. Run OCR with a named engine (record which one) and, for the Vietnamese samples,
   optionally run the correction step.
3. For each case place the original on the left and the system's own result on the
   right, and mark two or three correct and two or three incorrect positions.
4. Write the caption from the values the application reports: engine, page
   processing time, region count, mean confidence, and the concrete error type.
5. Do not select only successful cases.

---

## Figure 4.5 — So sánh thời gian xử lý theo công cụ và số trang

**Status: `MANUAL_COMPLETION_REQUIRED`.** An empty, editable chart frame and the
full measurement protocol were generated
(`chapter4/fig_4_5_processing_time_template.*`). **No data points are drawn.**

**Why it cannot be generated:** the repository contains no OCR benchmark results.
There is no timing data set, no OCR benchmark script, and no stored measurement
file. `tools/eval_results/Qwen2.5-3B-Instruct.json` and
`tools/eval_results/Qwen3-4B-Instruct-2507.json` contain latency numbers for
candidate **chat / rewrite language models**, not for OCR, and the scripts that
produced them (`tools/eval_model.py`, `tools/ab_harness.py`) import RAG and chat
services that no longer exist in this build.

**Data that must be supplied**

For every cell of the grid *(engine × page count)*:

| Column | Where it comes from |
|---|---|
| Engine | the `engine` parameter sent to `/api/ocr/all` (`paddleocr`, `paddleocr_modern`, `vietocr`, `glmocr`, `glm_vietocr`) |
| Page count | 1, 2, 5, 10, 20 (fixed document set) |
| Processing time | `processing_time_ms` in the response, or the summed value in the `activity_logs` detail string (visible at `/admin/logs`) |
| First-run model-loading time | the first measurement with each engine, reported **separately** |

**Measurement protocol**

1. Fix a document set with 1, 2, 5, 10 and 20 pages; upload each once.
2. Warm up each engine on a throw-away document and record that first measurement
   separately — it includes model download/initialisation.
3. Run `POST /api/ocr/all` with the engine named explicitly, three times per
   *(document, engine)* pair, and take the median.
4. **Restart the application between repetitions**, or use different documents:
   `app.py` caches page results in memory keyed by
   `(sha-256 of the file, page, size + mtime, engine)`, so an immediate repeat
   returns the cached result instead of re-running inference.
5. Record the fixed conditions next to the numbers: machine model, resolved
   `cfg.DEVICE`, the `OFFLINE` flag, whether the MLX server was already running, and
   the page size / resolution of the documents.
6. Note in the caption that **VietOCR falls back to PaddleOCR for PDF input**
   (`_resolve_selected_engine`), so its multi-page column measures the fallback, not
   VietOCR itself.
7. Note that the GLM-OCR column is only meaningful on Apple Silicon with the MLX
   server running.

Then open `chapter4/fig_4_5_processing_time_template.drawio` in diagrams.net, delete
the "NO DATA" box, and draw the series inside the plotting rectangle — or replace
the whole figure with a chart produced in a spreadsheet from the same numbers.

---

## Also worth correcting in the report text

These are not figures, but the diagrams surfaced statements in the report that the
source code does not support. Decide how to handle them before submission.

1. **Port 5002.** The report says the WebApp runs on 5002. `config.py` defaults to
   `PORT = 5001` and `RUN_MACOS.md` uses 5001 throughout. 5002 appears only as the
   default port of the optional `glmocr.server` HTTP wrapper in
   `glm-ocr-server/glmocr/config.yaml` and `mlx_config.yaml`, which SmartDocs does
   not use (it calls the CLI).
2. **DesktopApp / three backend modes.** Not present in this repository
   (Figures 3.1, 3.9, 3.10, 3.11).
3. **Automatic OCR tool selection.** Figure 2.7 in the report is described as a
   decision tree over document characteristics. The implementation has no such
   mechanism — see the generated Figure 2.7 for what actually exists.
4. **ER entities.** `Role`, `DocumentPage`, `OCRJob`, `OCRResult`,
   `OCRConfiguration` and `ErrorLog` do not exist. The physical schema is `users`,
   `documents`, `document_artifacts`, `activity_logs` (plus five chat/agent tables
   that are created but unused).
5. **RAG chat, translation, summarization, LLM agent.** Referenced by
   `glm-ocr-ui/README.md`, `docs/` and `requirements.txt`, but the corresponding
   modules are not in this build; `app.py` states that the indexing path was
   removed. If Chapter 3 or 4 describes them, either restore the code or scope the
   text to what ships.
