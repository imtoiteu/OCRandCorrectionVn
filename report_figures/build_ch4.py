#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chapter 4 report figures (4.1 - 4.5).

4.4 and 4.5 are produced as honest *templates / protocols*: the repository
contains sample documents and reference outputs, but it contains no ground-truth
transcriptions, no CER/WER implementation and no recorded timing measurements.
Nothing is invented.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram_engine import Diagram, write, set_out, row_x

set_out(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chapter4'))


# ══════════════════════════════════════════════════ 4.1 Test environment topology
def f41():
    d = Diagram('fig_4_1_test_environment',
                'Hình 4.1 – Bố trí các thành phần trong môi trường thử nghiệm',
                1400, 1020,
                subtitle='Test topology and the points at which the implementation produces observable '
                         'evidence during a test run')

    d.container('mach', 40, 92, 900, 660,
                'Test machine  —  macOS Apple Silicon · Python 3.10  (RUN_MACOS.md)', 'proc', header=38)

    d.node('br', 64, 150, 400, 84,
           'Test client — web browser\nhttp://localhost:5001\nseeded accounts: user / user123 · admin / admin123',
           'ui', parent='mach', fontsize=10)
    d.node('flask', 64, 264, 852, 76,
           'SmartDocs Flask application  —  port 5001  (single threaded development server process)\n'
           'authentication · ownership checks · OCR routes · document library · admin console · correction API',
           'api', parent='mach', fontsize=10.5, bold=True)
    d.node('eng', 64, 370, 412, 92,
           'In-process OCR engines\nPaddleOCR PP-OCRv5\nPP-StructureV3 + PP-OCRv6_medium\nVietOCR vgg_transformer',
           'eng', parent='mach', fontsize=10)
    d.node('glm', 504, 370, 412, 92,
           'GLM-OCR path (optional)\nglmocr CLI in .venv-sdk (per request)\n→ MLX server :8080 in .venv-mlx\nmodel mlx-community/GLM-OCR-bf16',
           'proc', parent='mach', fontsize=10)
    d.node('db', 64, 492, 264, 88, 'SQLite  paddleocr.db\nusers · documents\ndocument_artifacts\nactivity_logs',
           'data', parent='mach', shape='cyl', fontsize=9.5)
    d.node('up', 348, 492, 264, 88, 'uploads/\noriginal documents\n+ transient page .png\nMAX_UPLOAD_MB = 50',
           'data', parent='mach', fontsize=9.5)
    d.node('mm', 632, 492, 284, 88, 'models/ · HF cache · PaddleX cache\nVietOCR weights\nOFFLINE flag controls downloads',
           'data', parent='mach', fontsize=9.5)
    d.node('smp', 64, 608, 852, 116,
           'Test material already present in the repository\n'
           'glm-ocr-server/examples/source/     page.png · paper.png · table.png · seal.png · code.png · handwritten.png · GLM-4.5V.pdf\n'
           'glm-ocr-server/examples/result/<name>/     <name>.json · <name>.md · layout_vis/ · imgs/   (GLM-OCR reference outputs)\n'
           'glm-ocr-server/ui/_runs/<id>/     input/ · output/ · result .zip   (recorded GLM-OCR runs)\n'
           'vi-correction-prototype/tests/correction/sample_receipt_glm.json   (structured OCR JSON for the correction pipeline)',
           'svc', parent='mach', fontsize=9.5)

    d.node('lan', 980, 150, 380, 92,
           'Optional second client\nAnother machine on the same network;\nreachable because cfg.HOST = 0.0.0.0.\n'
           'No remote-server mode exists in the code —\nthe browser is the only remote client.',
           'ui', fontsize=9.5)

    d.container('obs', 980, 274, 380, 478,
                'Evidence produced by the implementation', 'note', header=36)
    OBS = [
        ('o1', 322, 74, 'Per-page timing\nadapter elapsed_ms → response field\nprocessing_time_ms'),
        ('o2', 406, 74, 'Engine actually used\nselected_engine · ocr_engine\n(kept per page in the response)'),
        ('o3', 490, 74, 'inference_status\nok | error |\nfallback_to_paddle_for_pdf'),
        ('o4', 574, 84, 'activity_logs rows (action = ocr)\ndetail contains mode, engine,\nprocessing_time_ms, inference_status,\npage count — viewable at /admin/logs'),
        ('o5', 668, 70, 'document_artifacts\npersisted outputs of each run,\ncomparable between engines'),
    ]
    for nid, y, h, lab in OBS:
        d.node(nid, 1002, y, 336, h, lab, 'note', parent='obs', fontsize=9)

    d.edge('br', 'flask', 'HTTP', color='#3F61A8', srcside='bottom', dstside='top')
    d.edge('lan', 'flask', 'HTTP over the local network', color='#3F61A8',
           srcside='bottom', dstside='right', waypoints=[(1170, 256), (950, 256), (950, 300)])
    d.edge('flask', 'eng', 'in-process', color='#0E8088', srcside='bottom', dstside='top',
           waypoints=[(490, 352), (270, 352)])
    d.edge('flask', 'glm', 'subprocess + HTTP :8080', color='#D79B00', srcside='bottom', dstside='top',
           waypoints=[(490, 352), (710, 352)])
    d.edge('eng', 'db', '', color='#5A5A5A', dashed=True, srcside='bottom', dstside='top')
    d.edge('eng', 'up', '', color='#5A5A5A', dashed=True, srcside='bottom', dstside='top')
    d.edge('glm', 'mm', '', color='#5A5A5A', dashed=True, srcside='bottom', dstside='top')
    d.edge('flask', 'obs', 'writes', color='#D6B656', srcside='right', dstside='left',
           waypoints=[(964, 302), (964, 513)])

    d.node('n1', 40, 776, 1320, 62,
           'Every component in the figure runs on one machine. The browser never contacts the MLX model server '
           'or the database directly: the only network endpoint exposed to a tester is Flask on :5001, and :8080 '
           'is contacted only by the transient glmocr subprocess on localhost.',
           'note', shape='note', fontsize=10)
    d.node('n2', 40, 852, 1320, 76,
           'Test-environment limitations to state in the report: the application runs on Flask\'s development '
           'server (single process, threaded), the database is a local SQLite file, and the GLM-OCR engine is '
           'available only on Apple Silicon with both virtual environments installed and the MLX server running. '
           'On a machine without them, the engine drop-down still offers "Recommended", but the request returns a '
           'structured error instead of a result.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 4.2 Data preparation & evaluation
def f42():
    d = Diagram('fig_4_2_evaluation_procedure',
                'Hình 4.2 – Quy trình chuẩn bị dữ liệu và đánh giá kết quả OCR',
                1420, 1120,
                subtitle='Filled boxes are supported by code or data in the repository; '
                         'red-outlined boxes are NOT implemented and must be done manually')

    d.node('leg', 40, 92, 1340, 44,
           'LEGEND      coloured fill = implemented in the repository (the responsible file is named in the box)            '
           'red outline on white = no implementation exists — the step must be performed manually',
           'note', shape='note', fontsize=10.5, bold=True)

    d.container('prep', 40, 156, 660, 476, 'Data preparation', 'svc', header=34)
    P = [
        ('p1', 204, 62, 'Select the documents to evaluate\nSamples available in the repository:\n'
                        'examples/source/*.png · GLM-4.5V.pdf'),
        ('p2', 280, 62, 'Group them by document type\nprinted page · scientific paper · table ·\nseal · source code · handwriting'),
        ('p3', 356, 58, 'Upload each document through the SPA\nPOST /api/upload → Document row +\nuploads/{uuid}{suffix}'),
        ('p4', 428, 62, 'Run OCR once per engine on the same file\nengine parameter of /api/ocr/page and\n/api/ocr/all (drop-down or API)'),
        ('p5', 504, 62, 'Results are persisted automatically\ndocument_artifacts: ocr, ocr_json,\nocr_markdown, ocr_layout, ocr_images'),
        ('p6', 580, 44, 'Optional: run the Vietnamese correction\nPOST /api/correction/run → corrected_json'),
    ]
    for nid, y, h, lab in P:
        d.node(nid, 62, y, 616, h, lab, 'svc', parent='prep', fontsize=9.5)
    for a, b in zip([x[0] for x in P], [x[0] for x in P][1:]):
        d.edge(a, b, '', color='#82B366', srcside='bottom', dstside='top')

    d.container('meas', 740, 156, 640, 476, 'Measurement and scoring', 'eng', header=34)
    d.node('m1', 762, 204, 596, 68,
           'AUTOMATIC — processing time\nEvery adapter records elapsed_ms; app.py copies it to processing_time_ms and\n'
           'writes it into the activity_logs detail string for each page and for OCR-All.',
           'eng', parent='meas', fontsize=9.5)
    d.node('m2', 762, 284, 596, 68,
           'AUTOMATIC — recognition metadata\nregion count, mean confidence (PaddleOCR engines only), page count,\n'
           'inference_status and the engine actually used are returned with every response.',
           'eng', parent='meas', fontsize=9.5)
    d.node('m3', 762, 364, 596, 76,
           'AUTOMATIC — correction quality signals (vi_correction)\ncounts {blocks, units, sent, changed, skipped} · timing {provider_seconds,\n'
           'total_seconds} · validation report (structure preserved, placeholders intact)\n'
           'plus scripts/bench_spans.py for per-span latency in the prototype.',
           'corr', parent='meas', fontsize=9.5)
    d.node('m4', 762, 452, 596, 62,
           'MANUAL — create the ground truth\nNo transcription, annotation tool or reference-text file for the Vietnamese\n'
           'corpus exists in the repository.',
           'todo', parent='meas', fontsize=9.5)
    d.node('m5', 762, 526, 596, 46,
           'MANUAL — text normalisation before scoring\nNo normalisation routine for evaluation exists in the repository.',
           'todo', parent='meas', fontsize=9.5)
    d.node('m6', 762, 584, 596, 40,
           'MANUAL — compute CER and WER (no implementation exists: no jiwer, no edit-distance code)',
           'todo', parent='meas', fontsize=9.5)
    for a, b in (('m1', 'm2'), ('m2', 'm3'), ('m3', 'm4'), ('m4', 'm5'), ('m5', 'm6')):
        d.edge(a, b, '', color='#0E8088', srcside='bottom', dstside='top')
    d.edge('p6', 'm1', '', color='#82B366', srcside='right', dstside='left',
           waypoints=[(716, 602), (716, 238)])

    d.container('agg', 40, 668, 1340, 218, 'Aggregation and reporting', 'note', header=34)
    d.node('g1', 62, 716, 420, 68,
           'Export the raw evidence\n/admin/logs (activity_logs, filterable) ·\n/api/documents/<id>/text (all artifacts) ·\n'
           'downloads .md / .txt / .json / .docx',
           'svc', parent='agg', fontsize=9.5)
    d.node('g2', 502, 716, 420, 68,
           'MANUAL — build the comparison tables\nAccuracy per document group and engine;\nno aggregation script exists in the repository.',
           'todo', parent='agg', fontsize=9.5)
    d.node('g3', 942, 716, 416, 68,
           'MANUAL — build the timing chart (Figure 4.5)\nSeparate the first-run model-loading time from the\nsteady-state time, as the report requires.',
           'todo', parent='agg', fontsize=9.5)
    d.node('g4', 62, 800, 1296, 68,
           'Regression / smoke tests that do exist\n'
           'glm-ocr-ui: test_layout.py · test_regression.py (reading-order reconstruction) · test_vietocr.py · '
           'test_refactored_ocr.py (engine dispatch) · test_markdown_normalize.py (pytest)\n'
           'glm-ocr-server: glmocr/tests/test_unit.py · test_integration.py (pytest, with conftest.py)   —   '
           'none of these measures OCR accuracy; they verify behaviour, not quality.',
           'ext', parent='agg', fontsize=9.5)
    d.edge('g1', 'g2', '', color='#5A5A5A', srcside='right', dstside='left')
    d.edge('g2', 'g3', '', color='#5A5A5A', srcside='right', dstside='left')
    d.edge('m6', 'g2', '', color='#B85450', dashed=True, srcside='bottom', dstside='top')

    d.node('warn', 40, 916, 1340, 96,
           'ACCURACY NOTICE — the repository contains no OCR accuracy evaluation. There is no ground-truth data set, '
           'no CER/WER or layout-accuracy implementation (a repository-wide search for CER, WER, jiwer, '
           'levenshtein and edit_distance returns nothing outside model vocabulary files), and no recorded '
           'measurement results. tools/eval_model.py and tools/ab_harness.py evaluate candidate Qwen chat/rewrite '
           'language models, not OCR, and they import services that no longer exist in this build. '
           'Everything drawn as a red-outlined box must be produced manually before Chapter 4 can report numbers.',
           'todo', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 4.3 Functional test steps
def f43():
    d = Diagram('fig_4_3_functional_test_steps',
                'Hình 4.3 – Một số bước kiểm thử chức năng xử lý tài liệu',
                1420, 1090,
                subtitle='Functional test procedure derived from the implemented request flow; each step lists '
                         'the API call and the evidence the system produces')

    steps = [
        ('s1', 'a)  Log in',
         'Open http://localhost:5001 → the login form is served\nfor any unauthenticated request.\n'
         'POST /login  (user / user123)',
         'Evidence: redirect to /, navigation bar shows the user\nname and role; activity_logs gains action = "login".'),
        ('s2', 'b)  Upload a document',
         'OCR view → drop zone or file picker.\nPOST /api/upload  (multipart)',
         'Evidence: 200 with file_id, page_count, is_pdf;\nfile appears in uploads/ as {uuid}{suffix};\n'
         'Document row status = "uploaded"; log action = "upload".'),
        ('s3', 'c)  Preview and navigate pages',
         'POST /api/ocr/page with preview_only = true\n(page navigation buttons for a PDF)',
         'Evidence: page_image_b64 rendered on the canvas,\nresults = [], no OCR performed, no artifact written.'),
        ('s4', 'd)  Select the OCR tool',
         'Engine drop-down: Recommended (glmocr) ·\nGLM Layout + VietOCR Text · Vietnamese (vietocr) ·\nStandard (paddleocr)',
         'Evidence: the chosen value is sent as the "engine"\nfield and echoed back as selected_engine;\n'
         'the choice is kept for the whole session.'),
        ('s5', 'e)  Run recognition and follow the status',
         'POST /api/ocr/page  (Run OCR)  or\nPOST /api/ocr/all  (OCR All) · Stop button aborts\nthe fetch on the client side',
         'Evidence: processing_time_ms and inference_status per\npage; statistics strip shows regions, mean confidence,\n'
         'time and page count; log action = "ocr" with details.'),
        ('s6', 'f)  Inspect the result representations',
         'Result tabs: Markdown · Raw · Images · JSON;\nclicking a region highlights the matching box\non the page canvas',
         'Evidence: artifacts ocr, ocr_layout, ocr_json,\nocr_markdown, ocr_images written to document_artifacts\n'
         '(one row per kind, upserted).'),
        ('s7', 'g)  Export the result',
         'Download .md / .txt / .json;\nPOST /api/ocr/export-docx  (pandoc)',
         'Evidence: files downloaded; a missing pandoc returns\n501 with an explanatory message rather than failing.'),
        ('s8', 'h)  Reopen from the document library',
         '#documents → open a document →\n#ocr/<file_id> → GET /api/documents/<id>/text\nand /ocr-images',
         'Evidence: the previous OCR result, overlay boxes and\nimages are restored without re-running OCR.'),
        ('s9', 'i)  Optional — Vietnamese correction',
         'GET /correction → pick a document that has ocr_json →\nPOST /api/correction/run → POST /api/correction/save',
         'Evidence: counts, timing and a validation report;\ncorrected_json / corrected_md stored beside — never\n'
         'overwriting — the raw OCR artifacts.'),
        ('s10', 'j)  Administration checks',
         '/admin/ dashboard · /admin/users · /admin/logs ·\n/admin/files   (admin / admin123)',
         'Evidence: every action above appears in the log list;\na non-admin account receives 403 from the same URLs.'),
    ]
    d.node('h1', 40, 100, 300, 38, 'Test step', 'flow', shape='rect', fontsize=11, bold=True)
    d.node('h2', 360, 100, 480, 38, 'Action performed and API call exercised', 'api', shape='rect',
           fontsize=11, bold=True)
    d.node('h3', 860, 100, 520, 38, 'Evidence produced by the implementation', 'data', shape='rect',
           fontsize=11, bold=True)
    y = 152
    for nid, title, act, ev in steps:
        d.node(nid + '_t', 40, y, 300, 76, title, 'flow', fontsize=11, bold=True)
        d.node(nid + '_a', 360, y, 480, 76, act, 'api', fontsize=9)
        d.node(nid + '_e', 860, y, 520, 76, ev, 'data', fontsize=9)
        y += 86
    for a, b in zip([s[0] for s in steps], [s[0] for s in steps][1:]):
        d.edge(a + '_t', b + '_t', '', color='#4B6E9C', srcside='bottom', dstside='top')

    d.node('n1', 40, 1024, 1340, 44,
           'Screenshot note: the report presents Figure 4.3 as captures a) upload, b) engine selection, '
           'c) recognition result, d) processing history — see MANUAL_COMPLETION.md.',
           'todo', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 4.4 Result examples (template)
def f44():
    d = Diagram('fig_4_4_result_examples_template',
                'Hình 4.4 – Minh họa kết quả OCR trên một số nhóm tài liệu  (khung trình bày)',
                1400, 900,
                subtitle='COMPOSITION TEMPLATE — no OCR output is reproduced here. The boxes name the sample '
                         'files that exist in the repository and where each capture must be inserted.')

    d.node('warn', 40, 92, 1320, 58,
           'This figure cannot be generated from source code: it shows recognition output on real documents. '
           'The template below lists the sample material that already exists in the repository so the captures '
           'can be produced consistently. Do not reuse the stored reference outputs as if they were results of '
           'this system without re-running them.',
           'todo', shape='note', fontsize=10.5, bold=True)

    cases = [
        ('c1', 'a)  Clear printed text',
         'Source in the repository\nglm-ocr-server/examples/source/page.png\n\n'
         'Existing GLM-OCR reference output\nexamples/result/page/page.json · page.md\nlayout_vis/layout_page0.jpg'),
        ('c2', 'b)  Table / structured layout',
         'Source in the repository\nglm-ocr-server/examples/source/table.png\n\n'
         'Existing GLM-OCR reference output\nexamples/result/table/table.json · table.md\nplus ui/_runs/0359de69/ (recorded run)'),
        ('c3', 'c)  Handwriting  (difficult case)',
         'Source in the repository\nglm-ocr-server/examples/source/handwritten.png\n\n'
         'Existing GLM-OCR reference output\nexamples/result/handwritten/handwritten.json · .md'),
        ('c4', 'd)  Low-quality photograph  —  MISSING',
         'No low-quality photograph exists in the repository.\nA real photograph taken by the author must be added\n'
         'and uploaded through the application.\n\nThe report requires at least one difficult case, so this\n'
         'sample cannot be skipped.'),
    ]
    xs = [40, 380, 720, 1060]
    for (nid, title, body), x in zip(cases, xs):
        key = 'todo' if 'MISSING' in title else 'svc'
        d.node(nid + '_h', x, 176, 300, 44, title, key, fontsize=10.5, bold=True)
        d.node(nid + '_s', x, 232, 300, 130, body, 'note', fontsize=9)
        d.node(nid + '_l', x, 376, 300, 190,
               'INSERT CAPTURE\n\nleft: the original document\nright: the OCR result produced by\nthis system\n\n'
               'mark two or three correct and\nincorrect positions on the image',
               'todo', fontsize=9.5)
        d.node(nid + '_c', x, 580, 300, 96,
               'Caption to write\n• engine used (selected_engine)\n• page processing time (processing_time_ms)\n'
               '• region count / mean confidence\n• the specific error type observed',
               'ext', fontsize=9)

    d.node('n1', 40, 700, 1320, 84,
           'How to obtain each capture reproducibly: upload the sample through POST /api/upload, run OCR with a '
           'named engine, then use the OCR workspace to place the page canvas (with the recognition boxes shown) '
           'next to the Markdown or Raw tab. The values needed for the caption are visible in the statistics strip '
           'and are also recorded in activity_logs, so the figure and the text can be kept consistent.',
           'note', shape='note', fontsize=10)
    d.node('n2', 40, 800, 1320, 66,
           'Honesty requirement stated in the report: at least one difficult case must be included, and the '
           'examples must not be selected only from successful runs. The repository provides three usable samples; '
           'the low-quality photograph has to be supplied by the author.',
           'todo', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 4.5 Timing chart (empty template)
def f45():
    d = Diagram('fig_4_5_processing_time_template',
                'Hình 4.5 – So sánh thời gian xử lý theo công cụ và số trang  (khung biểu đồ, chưa có dữ liệu)',
                1400, 960,
                subtitle='NO MEASUREMENT DATA EXISTS IN THE REPOSITORY — the chart frame is provided empty, '
                         'together with the procedure for collecting the values')

    d.node('warn', 40, 92, 1320, 74,
           'The repository contains no OCR benchmark results. There is no timing data set, no benchmark script for '
           'the OCR engines, and no stored measurement file. tools/eval_results/*.json holds latency figures for '
           'candidate Qwen chat/rewrite language models, not for OCR. Plotting anything here without running the '
           'measurements would fabricate results, so the chart is delivered as an empty, editable frame.',
           'todo', shape='note', fontsize=10.5, bold=True)

    # ── chart frame (empty, editable) ──────────────────────────────────────
    d.node('plot', 140, 210, 600, 390, '', 'plot', shape='rect')
    d.node('nodata', 240, 370, 400, 70,
           'NO DATA\nDraw one series per OCR engine here after running\nthe measurement procedure given below.',
           'todo', shape='rect', fontsize=11, bold=True)
    d.node('ylab', 20, 300, 110, 210,
           'Processing time\nper document\n(seconds)\n\nvertical scale to be\nset from the measured\nvalues',
           'axis', shape='rect', fontsize=10, bold=True)
    for i, t in enumerate(['1', '2', '5', '10', '20']):
        d.node('xt%d' % i, 150 + i * 120, 606, 100, 26, t, 'axis', shape='rect', fontsize=10.5, bold=True)
    d.node('xlab', 340, 640, 200, 30, 'Number of pages', 'axis', shape='rect', fontsize=10.5, bold=True)

    d.node('leg', 780, 210, 300, 190,
           'Series — one per OCR engine\n\n'
           '■  PaddleOCR Legacy      (paddleocr)\n'
           '■  PaddleOCR Modern    (paddleocr_modern)\n'
           '■  VietOCR                        (vietocr)\n'
           '■  GLM-OCR                     (glmocr)\n'
           '■  GLM Layout + VietOCR (glm_vietocr)',
           'note', fontsize=10)
    d.node('sep', 780, 418, 300, 192,
           'Report the first run separately\n\nThe first request with an engine also loads its model:\n'
           '• PaddleOCR / PP-StructureV3 download and initialise\n  their pipelines on first use\n'
           '• VietOCR loads the .pth weights\n• the MLX server holds GLM-OCR resident, but the\n'
           '  glmocr subprocess and PP-DocLayoutV3 start per call\n\n'
           'Mixing that first measurement into the steady-state\ncurve distorts the scale.',
           'ext', fontsize=9)

    d.node('proc', 1120, 210, 240, 400,
           'Where the numbers come from\n(already implemented)\n\n'
           '1. Each adapter measures its own\n    wall-clock time and returns\n    elapsed_ms.\n\n'
           '2. app.py copies it to\n    processing_time_ms in the\n    response for /api/ocr/page.\n\n'
           '3. For /api/ocr/all the values are\n    summed and written into the\n    activity_logs detail string\n'
           '    together with the engine and\n    the page count.\n\n'
           '4. /admin/logs lists those rows and\n    can be filtered by action = "ocr".',
           'svc', fontsize=9)

    d.node('rec', 40, 690, 1320, 130,
           'Measurement procedure to run before this figure can be completed\n\n'
           '1.  Choose a fixed set of documents with 1, 2, 5, 10 and 20 pages and upload each one once.\n'
           '2.  For every engine, warm it up on a throw-away document; record that first measurement separately.\n'
           '3.  Run POST /api/ocr/all with the engine parameter set explicitly, three times per (document, engine) pair.\n'
           '4.  Read processing_time_ms (or the summed value in the activity_logs detail string) and take the median.\n'
           '5.  Record the fixed conditions with the numbers: machine model, cfg.DEVICE, OFFLINE flag, whether the MLX\n'
           '     server was already running, and the exact page size / resolution of the documents.\n'
           '6.  Note that VietOCR falls back to PaddleOCR for PDF input, so its multi-page column measures the fallback.',
           'note', shape='note', fontsize=10)

    d.node('n1', 40, 836, 1320, 74,
           'Fairness constraint that follows from the implementation: results are cached in memory per '
           '(file hash, page, file state, engine), so repeating the same page with the same engine in one server '
           'session returns the cached result instead of re-running inference. Restart the application, or use '
           'different documents, between repetitions.',
           'todo', shape='note', fontsize=10)
    return d


if __name__ == '__main__':
    for fn in (f41, f42, f43, f44, f45):
        write(fn())
