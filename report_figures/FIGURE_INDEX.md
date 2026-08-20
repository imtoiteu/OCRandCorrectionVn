# FIGURE INDEX — BAO_CAO_DE_TAI_OCR_DA_HIEU_CHINH.docx

Generated from the source tree of **OCRandCorrectionVn** — the repository this
directory lives in. All source-file paths below are relative to the repository
root; paths given without a top-level folder (e.g. `app.py`, `services/**`) are
inside `glm-ocr-ui/`.

Every diagram below is derived from the implementation. Where the report asks for
something the code does not contain, the figure says so explicitly instead of
inventing it — see `MANUAL_COMPLETION.md`.

* `.drawio` files are **native mxGraph XML** (real vertices, edges, swimlanes, UML
  lifelines and frames). They open and edit normally in diagrams.net / draw.io.
  No raster or embedded-SVG image is used anywhere.
* `.svg` files are plain vector graphics (no rasterization, no external font
  files, no scripts) sized for insertion into Microsoft Word.

## Status values

| Status | Meaning |
|---|---|
| `GENERATED` | Fully derived from the source code; nothing manual is required. |
| `GENERATED_WITH_LIMITATIONS` | Derived from the source code, but part of the report's requested content is not supported by the implementation; the figure states the gap. |
| `MANUAL_COMPLETION_REQUIRED` | Cannot be produced from source code (UI capture or missing measurement data). A template and/or a capture checklist is provided. |
| `NOT_SUPPORTED_BY_SOURCE` | The subject of the figure does not exist in this repository at all. |

---

## Chapter 2 — System analysis and design

| Fig. | Title | `.drawio` | `.svg` | Main source files | Status | Notes |
|---|---|---|---|---|---|---|
| 2.1 | Biểu đồ ca sử dụng tổng quát của hệ thống | `chapter2/fig_2_1_use_case.drawio` | `chapter2/fig_2_1_use_case.svg` | `glm-ocr-ui/app.py`, `auth.py`, `admin_bp.py`, `correction_bp.py`, `static/index.html` | `GENERATED_WITH_LIMITATIONS` | Two actors (`role = "user"` / `"admin"`), 14 user + 5 admin use cases, each labelled with its real route. The report's "quản lý cấu hình OCR" use case is **not** shown: there is no in-app OCR configuration screen — settings come from environment variables read by `config.py`. |
| 2.2 | Biểu đồ ngữ cảnh của hệ thống số hóa tài liệu | `chapter2/fig_2_2_context.drawio` | `chapter2/fig_2_2_context.svg` | `app.py`, `config.py`, `services/ocr_engines/glm_adapter.py`, `tools/glm_serve.sh`, `glm-ocr-server/mlx_config.yaml` | `GENERATED` | Boundary + four external groups (user, administrator, OCR tooling, data area), plus `pandoc`. Cloud OCR is not an external entity: `pipeline.maas.enabled = false`. |
| 2.3 | Kiến trúc tổng thể các thành phần của hệ thống | `chapter2/fig_2_3_architecture.drawio` | `chapter2/fig_2_3_architecture.svg` | `app.py`, `auth.py`, `admin_bp.py`, `correction_bp.py`, `services/**`, `models.py`, `static/**`, `templates/**` | `GENERATED_WITH_LIMITATIONS` | Six layers with the real module names. A footnote records that the desktop app, RAG chat, translation, summarization and agent modules named in `README.md` are absent from this build. |
| 2.4 | Kiến trúc triển khai của hệ thống | `chapter2/fig_2_4_deployment.drawio` | `chapter2/fig_2_4_deployment.svg` | `app.py` (`app.run`), `config.py`, `tools/glm_serve.sh`, `RUN_MACOS.md`, `glm_adapter.py` | `GENERATED` | Three processes (Flask :5001, MLX :8080, transient `glmocr` CLI) + local storage. Explicitly notes that no container / reverse proxy / WSGI server / queue exists. |
| 2.5 | Biểu đồ tuần tự quá trình xử lý một yêu cầu OCR | `chapter2/fig_2_5_sequence_ocr.drawio` | `chapter2/fig_2_5_sequence_ocr.svg` | `app.py` (`upload`, `ocr_page`, `_run_page_ocr`), `services/ocr_service.py`, `services/ocr_engines/router.py`, `glm_adapter.py`, `models.py` | `GENERATED` | Native UML lifelines + an `alt [engine failure]` frame. Follows the real two-request flow (upload, then OCR). |
| 2.6 | Quy trình xử lý tài liệu tổng quát của hệ thống | `chapter2/fig_2_6_document_workflow.drawio` | `chapter2/fig_2_6_document_workflow.svg` | `app.py`, `services/ocr_service.py`, `services/text_service.py`, `models.py` | `GENERATED` | Includes the real error branches (401 / 413 / 400 / 403 / 404 / 500). A note states that no separate binarization/deskew stage exists. |
| 2.7 | Cơ chế lựa chọn công cụ OCR theo đặc điểm tài liệu | `chapter2/fig_2_7_engine_selection.drawio` | `chapter2/fig_2_7_engine_selection.svg` | `app.py::_resolve_selected_engine`, `services/ocr_engines/router.py`, `services/ocr_engines/glm_vietocr_adapter.py`, `static/index.html`, `static/app.js` | `GENERATED_WITH_LIMITATIONS` | **The system has no automatic content-based engine selection.** The figure documents the two rule-based decisions that do exist (VietOCR + PDF → PaddleOCR; per-block label / sanity rule inside the hybrid engine) and states the absence prominently. Nothing was invented. |
| 2.8 | Sơ đồ quan hệ thực thể của hệ thống | `chapter2/fig_2_8_erd.drawio` | `chapter2/fig_2_8_erd.svg` | `glm-ocr-ui/models.py` | `GENERATED_WITH_LIMITATIONS` | Four real tables with PK/FK, uniqueness, cascade rules and cardinalities, plus the `document_artifacts.kind` catalogue. The report's suggested `Role`, `DocumentPage`, `OCRJob`, `OCRResult`, `OCRConfiguration`, `ErrorLog` entities do not exist and are not drawn; the five chat/agent tables that exist but are unused in this build are shown separately. |
| 2.9 | Sơ đồ điều hướng chính của giao diện người dùng | `chapter2/fig_2_9_navigation.drawio` | `chapter2/fig_2_9_navigation.svg` | `static/app.js` (`Router`), `static/index.html`, `templates/admin/base.html`, `auth.py`, `correction_bp.py` | `GENERATED` | Derived from the hash router and the Flask routes; no visual UI interpretation was needed. |
| 2.10 | Mô hình các lớp bảo vệ dữ liệu của hệ thống | `chapter2/fig_2_10_data_protection.drawio` | `chapter2/fig_2_10_data_protection.svg` | `app.py`, `auth.py`, `admin_bp.py`, `config.py`, `models.py`, `glm_adapter.py`, `static/app.js`, `services/markdown_normalize.py` | `GENERATED_WITH_LIMITATIONS` | Eight layers, each naming its source file. A closing note lists what is **not** implemented (TLS termination, encryption at rest, CSRF tokens, rate limiting, backup automation, external IdP) so no protection is over-claimed. |

## Chapter 3 — Implementation

| Fig. | Title | `.drawio` | `.svg` | Main source files | Status | Notes |
|---|---|---|---|---|---|---|
| 3.1 | Cấu trúc môi trường phát triển và các thành phần mã nguồn | `chapter3/fig_3_1_development_structure.drawio` | `chapter3/fig_3_1_development_structure.svg` | Whole working tree; `requirements.txt`, `RUN_MACOS.md`, `.env.example`, `glm-ocr-server/pyproject.toml` | `GENERATED_WITH_LIMITATIONS` | Real directory contents + the three Python environments. The report's `SmartDocs-Agent-DesktopApp` block **cannot** be drawn — no desktop source exists (see `MANUAL_COMPLETION.md`). |
| 3.2 | Cấu trúc các mô-đun backend và luồng gọi API | `chapter3/fig_3_2_backend_modules.drawio` | `chapter3/fig_3_2_backend_modules.svg` | `app.py`, `auth.py`, `admin_bp.py`, `correction_bp.py`, `config.py`, `models.py`, `services/**` | `GENERATED` | All 33 routes were read from the source; four route tables + the service and data layers, with the call-flow rule stated. |
| 3.3 | Giao diện đăng nhập và trang làm việc chính | — | — | `templates/login.html`, `static/index.html` | `MANUAL_COMPLETION_REQUIRED` | UI capture. Screenshot checklist in `MANUAL_COMPLETION.md`. |
| 3.4 | Giao diện tải tài liệu, lựa chọn công cụ và xem kết quả OCR | — | — | `static/index.html`, `static/app.js` | `MANUAL_COMPLETION_REQUIRED` | UI capture. See also Figure 3.8, which supplies the architecture behind this screen. |
| 3.5 | Giao diện quản trị người dùng, tài liệu và nhật ký | — | — | `templates/admin/*.html`, `admin_bp.py` | `MANUAL_COMPLETION_REQUIRED` | UI capture (3 screens). |
| 3.6 | Quy trình tiếp nhận và chuẩn hóa tài liệu đã hiện thực hóa | `chapter3/fig_3_6_intake_normalization.drawio` | `chapter3/fig_3_6_intake_normalization.svg` | `app.py` (`upload`, `_safe_basename`, `_resolve_owned_file`, `ocr_page`, `ocr_all`), `services/ocr_service.py`, `services/text_service.py` | `GENERATED` | Two phases (upload, pre-OCR normalization) + the `/api/read-text` path + the real error branches and the in-memory result cache. |
| 3.7 | Cơ chế tích hợp và điều phối các công cụ OCR | `chapter3/fig_3_7_ocr_orchestration.drawio` | `chapter3/fig_3_7_ocr_orchestration.svg` | `services/ocr_engines/{base,router,paddle_adapter,paddle_modern_adapter,vietocr_adapter,glm_adapter,glm_vietocr_adapter}.py`, `services/ocr_service.py` | `GENERATED` | Router + five adapters + the six-step out-of-process GLM integration + the common result contract. |
| 3.8 | Giao diện kết quả OCR theo văn bản và dữ liệu có cấu trúc | `chapter3/fig_3_8_ocr_result_representations.drawio` | `chapter3/fig_3_8_ocr_result_representations.svg` | `app.py` (`_build_ocr_layout`, `_persist_ocr_structured`), `models.py`, `static/app.js`, `services/markdown_normalize.py` | `GENERATED_WITH_LIMITATIONS` | Data flow + engine capability matrix. The screen capture the report asks for is still a manual item. |
| 3.9 | Mô hình triển khai hệ thống trong môi trường thử nghiệm | `chapter3/fig_3_9_test_deployment.drawio` | `chapter3/fig_3_9_test_deployment.svg` | `RUN_MACOS.md`, `config.py`, `tools/glm_serve.sh`, `.env.example`, `glm_adapter.py` | `GENERATED_WITH_LIMITATIONS` | Two-terminal test deployment with real ports (**5001**, 8080). The report's port 5002 and the DesktopApp's three backend modes do not exist in the code; the figure explains where 5002 actually comes from. |
| 3.10 | Giao diện lựa chọn môi trường xử lý của ứng dụng desktop | — | — | — | `NOT_SUPPORTED_BY_SOURCE` | No desktop application in the repository. Nothing can be generated or captured from this code base. |
| 3.11 | Một số giao diện hoàn thiện trên WebApp và DesktopApp | — | — | `static/**`, `templates/**` | `MANUAL_COMPLETION_REQUIRED` | WebApp captures only; the DesktopApp half is not supported by the source. |

## Chapter 4 — Testing and evaluation

| Fig. | Title | `.drawio` | `.svg` | Main source files | Status | Notes |
|---|---|---|---|---|---|---|
| 4.1 | Bố trí các thành phần trong môi trường thử nghiệm | `chapter4/fig_4_1_test_environment.drawio` | `chapter4/fig_4_1_test_environment.svg` | `RUN_MACOS.md`, `config.py`, `app.py`, `models.py`, `glm-ocr-server/examples/**`, `glm-ocr-server/ui/_runs/**` | `GENERATED` | Topology + the five evidence points the implementation actually produces + the sample material that already exists in the repository. |
| 4.2 | Quy trình chuẩn bị dữ liệu và đánh giá kết quả OCR | `chapter4/fig_4_2_evaluation_procedure.drawio` | `chapter4/fig_4_2_evaluation_procedure.svg` | `app.py`, `services/vi_correction/**`, `vi-correction-prototype/scripts/bench_spans.py`, `test_*.py`, `glmocr/tests/**` | `GENERATED_WITH_LIMITATIONS` | Implemented steps are filled; ground truth, text normalization, CER/WER and aggregation are drawn as red-outlined **manual** steps because no such code exists. |
| 4.3 | Một số bước kiểm thử chức năng xử lý tài liệu | `chapter4/fig_4_3_functional_test_steps.drawio` | `chapter4/fig_4_3_functional_test_steps.svg` | `app.py`, `auth.py`, `admin_bp.py`, `correction_bp.py`, `static/app.js`, `RUN_MACOS.md` | `GENERATED_WITH_LIMITATIONS` | Ten-step procedure with the API call and the observable evidence per step. The report's version of this figure is a set of screenshots — checklist provided. |
| 4.4 | Minh họa kết quả OCR trên một số nhóm tài liệu | `chapter4/fig_4_4_result_examples_template.drawio` | `chapter4/fig_4_4_result_examples_template.svg` | `glm-ocr-server/examples/source/**`, `glm-ocr-server/examples/result/**`, `glm-ocr-server/ui/_runs/**` | `MANUAL_COMPLETION_REQUIRED` | **Composition template only** — no OCR output is reproduced. Names the three usable samples in the repository and marks the missing low-quality photograph. |
| 4.5 | So sánh thời gian xử lý theo công cụ và số trang | `chapter4/fig_4_5_processing_time_template.drawio` | `chapter4/fig_4_5_processing_time_template.svg` | `services/ocr_engines/*_adapter.py` (`elapsed_ms`), `app.py` (`processing_time_ms`, `log_activity`), `admin_bp.py` | `MANUAL_COMPLETION_REQUIRED` | **Empty, editable chart frame + measurement protocol.** The repository contains no OCR timing measurements, so no data points are drawn. |

---

## Summary

The report contains 26 figures (2.1–2.10, 3.1–3.11, 4.1–4.5).

| Status | Count | Figures |
|---|---|---|
| `GENERATED` | 9 | 2.2, 2.4, 2.5, 2.6, 2.9, 3.2, 3.6, 3.7, 4.1 |
| `GENERATED_WITH_LIMITATIONS` | 10 | 2.1, 2.3, 2.7, 2.8, 2.10, 3.1, 3.8, 3.9, 4.2, 4.3 |
| `MANUAL_COMPLETION_REQUIRED` | 6 | 3.3, 3.4, 3.5, 3.11, 4.4, 4.5 |
| `NOT_SUPPORTED_BY_SOURCE` | 1 | 3.10 |

**Files produced: 21 `.drawio` + 21 `.svg`.**
They cover 21 of the 26 report figures — including 4.4 and 4.5, which are delivered
as an honest composition template and an empty measurement frame rather than as
fabricated content. Five figures have no file at all because they are pure
user-interface captures (3.3, 3.4, 3.5, 3.11) or describe an application that does
not exist in this repository (3.10).

## Regenerating

```bash
cd report_figures
python3 build_ch2.py      # Chapter 2
python3 build_ch3.py      # Chapter 3
python3 build_ch4.py      # Chapter 4
```

`diagram_engine.py` is a copy of the project's own generator
(`glm-ocr-ui/docs/diagrams/build_diagrams.py`), so the visual language matches the
diagrams that already ship with the code base. **No file inside
`OCRandCorrectionVn/` was modified.**
