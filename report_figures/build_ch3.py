#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chapter 3 report figures (3.1, 3.2, 3.6, 3.7, 3.8, 3.9).

Figures 3.3, 3.4, 3.5, 3.10 and 3.11 are user-interface captures and are handled
in MANUAL_COMPLETION.md — no UI is fabricated here.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram_engine import Diagram, write, set_out, row_x

set_out(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chapter3'))


# ══════════════════════════════════════════════════ 3.1 Development structure
def f31():
    d = Diagram('fig_3_1_development_structure',
                'Hình 3.1 – Cấu trúc môi trường phát triển và các thành phần mã nguồn của hệ thống',
                1420, 1180,
                subtitle='Repository layout and Python environments of OCRandCorrectionVn '
                         '(verified against the working tree)')

    d.container('repo', 40, 92, 880, 990,
                'OCRandCorrectionVn/   —   git repository', 'api', header=40)

    X, W = 62, 836
    rows = [
        (146, 34, 'glm-ocr-ui/     —     SmartDocs web application (Flask, port 5001)', 'api', True, 11.5),
        (186, 54, 'app.py · auth.py · admin_bp.py · correction_bp.py · config.py · models.py\n'
                  'entry point, blueprints, configuration singleton, SQLAlchemy models', 'ui', False, 10),
        (246, 52, 'services/     ocr_service · smart_ocr_service · text_service · layout_service\n'
                  'geometry_service · markdown_normalize · activity_registry · cpu_threads', 'svc', False, 10),
        (304, 52, 'services/ocr_engines/     base · router · paddle_adapter · paddle_modern_adapter\n'
                  'vietocr_adapter · glm_adapter · glm_vietocr_adapter', 'eng', False, 10),
        (362, 52, 'services/vi_correction/     classification · masking · segmentation · pipeline · validation\n'
                  'renderers · service · providers/{protonx, bmd1905, mrlasdt, mock}', 'corr', False, 10),
        (420, 44, 'static/     index.html · app.js · ocr-canvas.js · correction.html · correction.js · i18n.js\n'
                  'style.css · vendor/{katex, marked}   (no frontend build step)', 'ui', False, 10),
        (470, 38, 'templates/     login.html · 403.html · admin/{base, dashboard, users, logs, files}.html',
         'ui', False, 10),
        (514, 44, 'tools/     glm_serve.sh · setup_offline.py · warmup_modern_models.py\n'
                  'download_chat_model.py · eval_model.py · ab_harness.py', 'svc', False, 10),
        (564, 38, 'docs/     ARCHITECTURE.md · ARCHITECTURE-DIAGRAMS.md · DEPLOYMENT.md · INSTALLATION.md\n'
                  'OCR_ENGINES.md · diagrams/', 'ext', False, 9.5),
        (608, 38, 'test_layout.py · test_regression.py · test_vietocr.py · test_refactored_ocr.py · '
                  'test_markdown_normalize.py', 'ext', False, 9.5),
        (652, 38, 'requirements.txt · .env.example · run_mac.sh · run_windows.bat · README.md · CLAUDE.md',
         'ext', False, 9.5),
        (696, 40, 'created at run time (git-ignored):     uploads/     paddleocr.db     models/', 'data', False, 10.5),
        (752, 34, 'glm-ocr-server/     —     GLM-OCR SDK and MLX model server', 'proc', True, 11.5),
        (792, 52, 'glmocr/     cli · api · config · server · pipeline/ (pipeline, _workers, _state, _unit_tracker)\n'
                  'layout/ (PP-DocLayoutV3) · dataloader/ · ocr_client · maas_client · postprocess/ · utils/ · tests/',
         'proc', False, 9.5),
        (850, 38, 'mlx_config.yaml (self-hosted mode → :8080) · glmocr/config.yaml · examples/ · skills/ · ui/ · resources/',
         'proc', False, 9.5),
        (894, 38, 'apps/backend (FastAPI) · apps/frontend (React + Vite) · Dockerfiles     —     upstream GLM-OCR demo, '
                  'NOT used by SmartDocs', 'ext', False, 9.5),
        (938, 34, 'models/     protonx-legal-tc · distilled-protonx-legal-tc · nano-protonx-legal-tc · vietocr/config.yml',
         'corr', True, 10.5),
        (978, 34, 'vi-correction-prototype/     standalone prototype: vicorrect/ · scripts/bench_spans.py · tests/',
         'svc', True, 10.5),
        (1018, 34, 'README.md     ·     RUN_MACOS.md   (installation and run guide)', 'ext', True, 10.5),
    ]
    for i, (y, h, lab, key, bold, fs) in enumerate(rows):
        d.node('r%d' % i, X, y, W, h, lab, key, parent='repo', fontsize=fs, bold=bold)

    d.container('env', 950, 92, 430, 470, 'Python environments  (created by the developer)', 'proc', header=40)
    d.node('v1', 972, 148, 386, 120,
           'glm-ocr-ui/.venv          Python 3.10\nflask · flask-login · flask-sqlalchemy\n'
           'paddleocr 3.7.x · paddlex[ocr-core] · paddlepaddle\nvietocr · torch · transformers · pypdfium2\n'
           'Pillow · layoutparser · python-docx · python-dotenv',
           'api', parent='env', fontsize=9.5)
    d.node('v2', 972, 282, 386, 78,
           'glm-ocr-server/.venv-sdk          Python 3.10\npip install -e ".[selfhosted]"\n'
           'provides the glmocr CLI called by GLMOCREngine',
           'proc', parent='env', fontsize=9.5)
    d.node('v3', 972, 374, 386, 78,
           'glm-ocr-server/.venv-mlx          Python 3.10\npip install -U mlx-vlm\n'
           'runs  python -m mlx_vlm.server --port 8080',
           'proc', parent='env', fontsize=9.5)
    d.node('v4', 972, 466, 386, 74,
           'None of the three environments is committed to git;\nall are created from RUN_MACOS.md (§3, §6, §7). '
           'GLM_ROOT / GLM_SDK_PYTHON / GLM_MLX_PYTHON in .env\npoint glm-ocr-ui at the other two.',
           'ext', parent='env', fontsize=9)

    d.node('mdl', 950, 590, 430, 140,
           'Model artifacts resolved at run time\n\n'
           '• MODEL_DIR/huggingface  —  HF_HOME / HF_HUB_CACHE (OFFLINE=1 blocks downloads)\n'
           '• PaddleOCR / PaddleX model cache  —  downloaded on first OCR run\n'
           '• MODEL_DIR/vietocr/<config>.pth  —  VietOCR weights\n'
           '• default HF cache  —  PP-DocLayoutV3 and mlx-community/GLM-OCR-bf16\n'
           '  (the GLM subprocess deliberately runs without the HF_* redirects)',
           'data', fontsize=9.5)

    d.node('todo', 950, 756, 430, 232,
           'MANUAL COMPLETION REQUIRED\n\n'
           'The report describes Figure 3.1 as two blocks, SmartDocs-Agent-WebApp and '
           'SmartDocs-Agent-DesktopApp (Tauri/Rust, embedded web UI, Python sidecar and three '
           'backend modes).\n\n'
           'No desktop-application source exists in this repository. A repository-wide search for '
           '"tauri", "sidecar", "Bundled Core", "Remote Server" and port 5002 returns no application '
           'code, and there is no src-tauri/, Cargo.toml or package.json for a desktop shell.\n\n'
           'Only the WebApp block above can be drawn from the source. The DesktopApp block must be '
           'added manually, or the caption reduced to the WebApp.',
           'todo', shape='note', fontsize=9.5)

    d.node('n1', 40, 1096, 1340, 60,
           'Reading note — README.md and docs/ in glm-ocr-ui describe a larger "SmartDocs-Agent" product '
           '(RAG chat, translation, summarization, LLM agent, agent/ package). Those directories are not '
           'present in this repository; requirements.txt still lists their dependencies. The figure shows '
           'the files that actually exist in the working tree.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 3.2 Backend modules + API flow
def f32():
    d = Diagram('fig_3_2_backend_modules',
                'Hình 3.2 – Cấu trúc các mô-đun backend và luồng gọi API của hệ thống',
                1420, 1210,
                subtitle='Every route below was read from app.py, auth.py, admin_bp.py and correction_bp.py')

    d.container('cli', 40, 92, 1340, 104, 'Clients  (HTTP)', 'ui', header=32)
    d.node('c1', 62, 130, 420, 52, 'SmartDocs SPA — static/index.html + app.js\nfetch() JSON + multipart',
           'ui', parent='cli', fontsize=10)
    d.node('c2', 502, 130, 400, 52, 'Correction page — static/correction.html\n+ correction.js', 'corr',
           parent='cli', fontsize=10)
    d.node('c3', 922, 130, 436, 52, 'Server-rendered admin pages and login form\ntemplates/admin/*.html · login.html',
           'ui', parent='cli', fontsize=10)

    d.node('cfg', 40, 236, 300, 104,
           'config.py\ncfg singleton read at import:\nHOST · PORT · DB_PATH · UPLOAD_DIR\nMODEL_DIR · OFFLINE · DEVICE\n'
           'OCR_ENGINE · GLM_* · VI_CORRECTION_*',
           'ext', fontsize=9.5)
    d.node('app', 400, 236, 620, 104,
           'app.py   —   Flask application object\n'
           'SECRET_KEY · MAX_CONTENT_LENGTH · session-cookie flags · LoginManager + user_loader\n'
           'unauthorized_handler (401 JSON / redirect) · RequestEntityTooLarge → 413 · after_request no-cache\n'
           'register_blueprint(auth_bp, admin_bp, correction_bp) · vn_time Jinja filter',
           'api', fontsize=10, bold=True)
    d.node('mdl', 1080, 236, 300, 104,
           'models.py\ndb (SQLAlchemy) · User · Document\nDocumentArtifact · ActivityLog\n'
           'log_activity() · save_artifact() · seed_admin()',
           'data', fontsize=9.5)

    d.table('t_core', 40, 386, 330, 'Core routes  (app.py)', [
        ('GET     /', 'SPA shell'),
        ('POST   /api/upload', 'intake'),
        ('POST   /api/read-text', 'text'),
        ('POST   /api/ocr/page', 'OCR'),
        ('POST   /api/ocr/all', 'OCR'),
        ('POST   /api/ocr/reconstruct-region', 'layout'),
        ('GET     /api/documents', 'library'),
        ('GET     /api/documents/<id>/text', 'artifacts'),
        ('GET     /api/documents/<id>/ocr-images', 'artifacts'),
        ('DELETE /api/documents/<id>', 'library'),
        ('GET     /api/documents/<id>/download', 'library'),
        ('POST   /api/ocr/export-docx', 'pandoc'),
    ], 'api')

    d.table('t_auth', 400, 386, 300, 'auth_bp  (auth.py)', [
        ('GET / POST   /login', 'session'),
        ('GET     /logout', 'session'),
        ('GET     /api/auth/me', 'identity'),
        ('POST   /api/set-lang', 'UI language'),
        ('GET     /api/admin/users', 'admin only'),
        ('app_errorhandler(403)', '403.html'),
    ], 'svc')

    d.table('t_admin', 730, 386, 320, 'admin_bp  (url_prefix = /admin)', [
        ('GET     /admin/', 'dashboard'),
        ('GET     /admin/users', 'list'),
        ('POST   /admin/users/create', ''),
        ('POST   /admin/users/<uid>/edit', ''),
        ('POST   /admin/users/<uid>/reset-password', ''),
        ('POST   /admin/users/<uid>/toggle', ''),
        ('POST   /admin/users/<uid>/delete', ''),
        ('GET     /admin/logs', 'filters'),
        ('GET     /admin/files', 'filters'),
    ], 'corr')

    d.table('t_corr', 1080, 386, 300, 'correction_bp', [
        ('GET     /correction', 'page'),
        ('GET     /api/correction/config', 'providers'),
        ('GET     /api/correction/documents', 'picker'),
        ('POST   /api/correction/run', 'model run'),
        ('POST   /api/correction/save', 'artifacts'),
        ('GET     /api/correction/result/<doc_id>', 'reload'),
    ], 'eng')

    d.container('svc', 40, 720, 1340, 178, 'Service layer  (services/)', 'svc', header=34)
    d.node('s1', 62, 768, 330, 108,
           'smart_ocr_service.run_ocr_pipeline()\n→ ocr_service.run_ocr()\n\n'
           'activity_registry.track("ocr")\n_normalize_block() · overlay rendering',
           'svc', parent='svc', fontsize=9.5)
    d.node('s2', 412, 768, 300, 108,
           'services/ocr_engines/router.py\nnormalize_engine_name() · get_engine()\n\n'
           'five OCREngine adapters\n(see Figure 3.7)',
           'eng', parent='svc', fontsize=9.5)
    d.node('s3', 732, 768, 300, 108,
           'layout_service / geometry_service\nreading-order reconstruction\n\n'
           'text_service.read_file()\nmarkdown_normalize.repair_…()',
           'svc', parent='svc', fontsize=9.5)
    d.node('s4', 1052, 768, 306, 108,
           'vi_correction.run_correction()\nclassification → masking → segmentation\n→ provider.correct_batch()\n'
           '→ restore → validation → renderers',
           'corr', parent='svc', fontsize=9.5)

    d.container('data', 40, 928, 1340, 130, 'Data and external resources', 'data', header=34)
    d.node('d1', 62, 972, 320, 66, 'SQLite  paddleocr.db\nusers · documents\ndocument_artifacts · activity_logs',
           'data', parent='data', shape='cyl', fontsize=9.5)
    d.node('d2', 402, 972, 300, 66, 'uploads/\n{uuid4}{suffix}\n+ transient page .png files', 'data',
           parent='data', fontsize=9.5)
    d.node('d3', 722, 972, 300, 66, 'models/  ·  HF cache\nPaddleX cache  ·  VietOCR weights', 'data',
           parent='data', fontsize=9.5)
    d.node('d4', 1042, 972, 316, 66, 'External processes\nglmocr CLI (.venv-sdk)  ·  MLX :8080\npandoc',
           'proc', parent='data', fontsize=9.5)

    d.edge('c1', 'app', 'JSON / multipart', color='#3F61A8', srcside='bottom', dstside='top',
           waypoints=[(272, 214), (560, 214)])
    d.edge('c2', 'app', '', color='#9673A6', srcside='bottom', dstside='top',
           waypoints=[(702, 214), (710, 214)])
    d.edge('c3', 'app', 'form POST / HTML', color='#3F61A8', srcside='bottom', dstside='top',
           waypoints=[(1140, 214), (860, 214)])
    d.edge('cfg', 'app', 'config', color='#999999', dashed=True,
           srcside='right', dstside='left')
    d.edge('app', 'mdl', 'ORM', color='#5A5A5A', srcside='right', dstside='left')

    for tid, cx in (('t_core', 205), ('t_auth', 550), ('t_admin', 890), ('t_corr', 1230)):
        d.edge('app', tid, '', color='#3F61A8', srcside='bottom', dstside='top',
               waypoints=[(710, 362), (cx, 362)])
    d.edge('t_core', 's1', 'OCR routes', color='#82B366', srcside='bottom', dstside='top')
    d.edge('t_core', 's3', 'text / layout routes', color='#82B366', srcside='right', dstside='top',
           waypoints=[(700, 700), (882, 700)])
    d.edge('t_corr', 's4', '', color='#9673A6', srcside='bottom', dstside='top')
    d.edge('s1', 's2', '', color='#0E8088', srcside='right', dstside='left')
    d.edge('s2', 's3', '', color='#82B366', srcside='right', dstside='left')
    d.edge('s1', 'd2', '', color='#5A5A5A', srcside='bottom', dstside='top',
           waypoints=[(222, 910), (552, 910)])
    d.edge('s2', 'd4', '', color='#D79B00', srcside='bottom', dstside='top',
           waypoints=[(562, 912), (1200, 912)])
    d.edge('mdl', 'data', 'INSERT / SELECT / DELETE', color='#5A5A5A',
           srcside='right', dstside='right', waypoints=[(1404, 288), (1404, 993)])

    d.node('n1', 40, 1078, 1340, 76,
           'Call-flow rule visible in the code: the browser never reaches a model or the database directly. '
           'Every request enters Flask, is checked by @login_required (and @admin_required for /admin), is resolved '
           'to an owned Document, and only then reaches the service layer; persistence happens exclusively through '
           'models.py. The OCR routes never import an OCR library themselves — they call '
           'smart_ocr_service → ocr_service → router → adapter.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 3.6 Intake and normalization
def f36():
    d = Diagram('fig_3_6_intake_normalization',
                'Hình 3.6 – Quy trình tiếp nhận và chuẩn hóa tài liệu đã được hiện thực hóa',
                1400, 1160,
                subtitle='Implemented intake path — app.py::upload(), _resolve_owned_file(), ocr_page() / ocr_all(), '
                         'ocr_service.py, text_service.py')

    d.container('p1', 40, 92, 660, 640, 'Phase A — upload    POST /api/upload', 'api', header=34)
    A = [
        ('a1', 138, 44, 'User selects or drops a file in the SPA\n(accept = .jpg .jpeg .png .webp .pdf .txt .docx)', 'flow'),
        ('a2', 198, 40, 'Flask rejects the body if it exceeds\nMAX_CONTENT_LENGTH → 413 JSON', 'dec'),
        ('a3', 254, 40, '@login_required  ·  request.files.get("file")\nmissing file → 400', 'dec'),
        ('a4', 310, 44, '_safe_basename(): drop directory parts, strip\ncontrol characters, keep Unicode, cap 255 chars', 'flow'),
        ('a5', 370, 40, 'suffix = Path(name).suffix.lower()\nsuffix ∈ ALL_EXTS ?   otherwise 400', 'dec'),
        ('a6', 426, 44, 'fid = uuid4()   ·   file saved as\nUPLOAD_DIR/{fid}{suffix}  (name never user-supplied)', 'flow'),
        ('a7', 486, 44, 'page_count = pdf_page_count() for PDF, else 1\nfile_size = path.stat().st_size', 'flow'),
        ('a8', 546, 44, 'INSERT Document(user_id, filename, file_id, file_type,\nfile_size, page_count, status="uploaded")', 'data'),
        ('a9', 606, 36, 'log_activity("upload", "<name> (<suffix>, <size>B)")', 'data'),
        ('a10', 654, 44, '200 {file_id, filename, size, suffix, doc_id,\nis_pdf, is_image, page_count}', 'flow'),
    ]
    for nid, y, h, lab, key in A:
        d.node(nid, 62, y, 616, h, lab, key, parent='p1', fontsize=9.5)
    for x, y in zip([a[0] for a in A], [a[0] for a in A][1:]):
        d.edge(x, y, '', color='#4B6E9C', srcside='bottom', dstside='top')

    d.container('p2', 740, 92, 640, 640,
                'Phase B — normalization before OCR    POST /api/ocr/page  ·  /api/ocr/all', 'eng', header=34)
    B = [
        ('b1', 138, 44, '_resolve_owned_file(file_id)\nDocument lookup → 404 · ownership → 403', 'dec'),
        ('b2', 198, 44, 'glob UPLOAD_DIR/{stored uuid}.*\nnever globs the raw file_id → traversal-proof', 'flow'),
        ('b3', 258, 40, '/api/ocr/all only: reject anything that is not\nan image or a PDF → 400', 'dec'),
        ('b4', 314, 40, 'suffix == ".pdf" ?', 'dec'),
        ('b5', 370, 56, 'PDF: pypdfium2 renders page N at scale = 2.0\n→ PIL image → NamedTemporaryFile(".png") inside\nUPLOAD_DIR (deleted in the finally block)', 'flow'),
        ('b6', 442, 48, 'Image: PIL.Image.open(path) directly\n(no resizing, no binarization, no deskew)', 'flow'),
        ('b7', 506, 44, 'preview_only = true → return page_image_b64 +\nimg_width / img_height, results = [] (no OCR)', 'flow'),
        ('b8', 566, 44, '_resolve_selected_engine(): engine parameter →\nalias → cfg.OCR_ENGINE; vietocr + .pdf → paddleocr', 'eng'),
        ('b9', 626, 40, 'smart_ocr_service.run_ocr_pipeline(image_path,\nengine_name)  →  OCR router (Figure 3.7)', 'eng'),
        ('b10', 678, 36, 'page_image_b64 attached to the response for the canvas overlay', 'flow'),
    ]
    for nid, y, h, lab, key in B:
        d.node(nid, 762, y, 596, h, lab, key, parent='p2', fontsize=9.5)
    for x, y in zip([b[0] for b in B], [b[0] for b in B][1:]):
        d.edge(x, y, '', color='#0E8088', srcside='bottom', dstside='top')

    d.edge('a10', 'b1', 'file_id', color='#3F61A8',
           srcside='right', dstside='left', waypoints=[(716, 676), (716, 160)])

    d.container('p3', 40, 764, 1340, 190,
                'Alternative intake path for text documents    POST /api/read-text', 'svc', header=34)
    d.node('t1', 62, 812, 400, 56, 'text_service.read_file(path)\ndispatch on the file extension', 'svc',
           parent='p3', fontsize=10)
    d.node('t2', 500, 806, 250, 62, '.txt\nopen(errors="replace")', 'svc', parent='p3', fontsize=10)
    d.node('t3', 500, 878, 250, 62, '.docx\npython-docx paragraphs', 'svc', parent='p3', fontsize=10)
    d.node('t4', 790, 842, 250, 62, '.pdf\npypdfium2 text page\n(embedded text, no OCR)', 'svc', parent='p3', fontsize=10)
    d.node('t5', 1078, 842, 280, 62, '_persist_and_index(file_id, "text", text)\n→ save_artifact(kind = "text")',
           'data', parent='p3', fontsize=10)
    d.edge('t1', 't2', '', color='#82B366', srcside='right', dstside='left')
    d.edge('t1', 't3', '', color='#82B366', srcside='right', dstside='left')
    d.edge('t2', 't4', '', color='#82B366', srcside='right', dstside='left')
    d.edge('t4', 't5', '', color='#82B366', srcside='right', dstside='left')

    d.node('err', 40, 984, 660, 108,
           'Implemented error branches\n'
           '• body too large → 413 {"error": "File too large (max N MB)"}\n'
           '• no file / unsupported suffix → 400\n'
           '• unknown file_id → 404;  foreign document → 403 (admins exempt)\n'
           '• file record present but missing on disk → 404 "File missing from disk"\n'
           '• any exception inside the OCR call → 500 with the traceback written to the log',
           'err', fontsize=9.5)
    d.node('lim', 740, 984, 640, 108,
           'Scope of "normalization" in this implementation\n'
           'The only image preparation performed by the application is page rasterization '
           '(pypdfium2, scale = 2.0) and format conversion to PNG/JPEG. Orientation classification and '
           'UVDoc unwarping happen only inside the PaddleOCR Modern pipeline '
           '(PPStructureV3(use_doc_orientation_classify=True, use_doc_unwarping=True)). '
           'No deskew, denoise, binarization or DPI normalization step exists in the application code.',
           'note', shape='note', fontsize=9.5)

    d.node('n1', 40, 1108, 1340, 34,
           'Result caching: _run_page_ocr() stores each page result in an in-memory dictionary keyed by '
           '(sha-256 of the file, page number, size + mtime, engine name), so re-running the same page with '
           'the same engine does not repeat the inference.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 3.7 OCR orchestration
def f37():
    d = Diagram('fig_3_7_ocr_orchestration',
                'Hình 3.7 – Cơ chế tích hợp và điều phối các công cụ OCR',
                1440, 1080,
                subtitle='services/ocr_engines/ — one abstract interface, five adapters, one common '
                         'result contract')

    d.node('req', 40, 110, 300, 150,
           'Request from the OCR service\n\nsmart_ocr_service.run_ocr_pipeline(\n     image_path,\n'
           '     engine_name)\n\n→ ocr_service.run_ocr()\n     activity_registry.track("ocr")',
           'svc', fontsize=10)

    d.node('router', 420, 128, 560, 114,
           'OCR ROUTER   services/ocr_engines/router.py\n\n'
           '_ENGINES = {paddleocr, vietocr, paddleocr_modern, glmocr, glm_vietocr}\n'
           '_ALIASES  (paddle, auto, modern, ppstructure, glm, glm_ocr, glm_layout_vietocr)\n'
           'normalize_engine_name() → get_engine() → engine.run(image_path)',
           'eng', fontsize=10.5, bold=True)

    d.node('abc', 1060, 128, 340, 114,
           'Abstract interface\nservices/ocr_engines/base.py\n\n'
           'class OCREngine(ABC):\n     engine_name: str\n     def run(self, image_path) -> dict',
           'api', fontsize=10)

    ax, aw = 40, 330
    ADP = [
        ('ad1', 40, 'PaddleOCR Legacy adapter\npaddle_adapter.py · engine_name = "paddleocr"\n\n'
                    'lazy PaddleOCR(ocr_version="PP-OCRv5",\n use_doc_orientation_classify=False,\n use_doc_unwarping=False)\n'
                    'in-process · returns rec_texts / rec_scores / det_polys', 'eng'),
        ('ad2', 390, 'PaddleOCR Modern adapter\npaddle_modern_adapter.py · "paddleocr_modern"\n\n'
                     'lazy PPStructureV3(use_doc_orientation_classify=True,\n use_doc_unwarping=True,\n'
                     ' text_detection_model_name="PP-OCRv6_medium_det",\n text_recognition_model_name="PP-OCRv6_medium_rec")\n'
                     'adds markdown · html · tables_html · layout_blocks', 'eng'),
        ('ad3', 740, 'VietOCR adapter\nvietocr_adapter.py · engine_name = "vietocr"\n\n'
                     'PaddleOCR PP-OCRv5 used as the line DETECTOR;\neach polygon crop is recognised by\n'
                     'vietocr Predictor (vgg_transformer, cfg.VIETOCR_DEVICE)\n'
                     'config from VIETOCR_CONFIG_PATH → MODEL_DIR → built-in defaults', 'eng'),
        ('ad4', 1090, 'GLM-OCR adapter\nglm_adapter.py · engine_name = "glmocr"\n\n'
                      'out-of-process client — see the panel below\nlayout_native = True (no geometric reordering)\n'
                      'returns markdown · tables_html · layout_blocks\n· images (layout_vis + crops) · raw_json', 'proc'),
    ]
    for nid, x, lab, key in ADP:
        d.node(nid, x, 316, 310, 168, lab, key, fontsize=9)
        d.edge('router', nid, '', color='#0E8088', srcside='bottom', dstside='top',
               waypoints=[(700, 292), (x + 155, 292)])

    d.node('ad5', 40, 512, 660, 118,
           'Hybrid adapter — glm_vietocr_adapter.py · engine_name = "glm_vietocr"\n\n'
           'composes GLMOCREngine (layout, reading order, labels, layout_vis) with VietOCREngine '
           '(line-level Vietnamese recognition on the same page image); every VietOCR line is assigned to the '
           'GLM block whose pixel box contains the line centre, lines are sorted top→bottom / left→right, and '
           'each block records recognition_source ∈ {vietocr, glm, fallback} plus fallback_reason.',
           'corr', fontsize=9.5)
    d.edge('ad1', 'ad5', '', color='#9673A6', dashed=True, srcside='bottom', dstside='top')
    d.edge('ad4', 'ad5', 'reuses both adapters', color='#9673A6', dashed=True,
           srcside='bottom', dstside='top', waypoints=[(1245, 500), (370, 500)])

    d.node('glm', 740, 512, 660, 190,
           'Out-of-process GLM-OCR integration  (glm_adapter.py)\n\n'
           '1.  Path(cfg.GLM_SDK_PYTHON).exists()  —  otherwise a structured error is returned\n'
           '2.  TCP connect to cfg.GLM_OCR_API_URL (default http://localhost:8080), timeout 3 s\n'
           '3.  child environment: HF_HOME / HF_HUB_CACHE / TRANSFORMERS_CACHE removed,\n'
           '     HF_HUB_OFFLINE = 1, TRANSFORMERS_OFFLINE = 1\n'
           '4.  subprocess.run([GLM_SDK_PYTHON, "-m", "glmocr.cli", "parse", <image>,\n'
           '     "--config", GLM_CONFIG_YAML, "--mode", "selfhosted", "--output", <tmpdir>],\n'
           '     cwd = GLM_ROOT, timeout = cfg.GLM_TIMEOUT)\n'
           '5.  read <tmpdir>/<stem>/: *.json (regions), *.md, layout_vis/*, imgs/*  → temp dir removed\n'
           '6.  boxes converted from the 0–1000 normalised space to image pixels (_scale_box)',
           'proc', fontsize=9.5)

    d.node('mlx', 740, 726, 660, 74,
           'glmocr SDK internals (glm-ocr-server): PageLoader → PP-DocLayoutV3 layout detection →\n'
           'per-region OCR request to the MLX server (OpenAI-compatible /chat/completions,\n'
           'model mlx-community/GLM-OCR-bf16) → ResultFormatter (json + markdown)',
           'proc', fontsize=9.5)
    d.edge('glm', 'mlx', '', color='#D79B00', srcside='bottom', dstside='top')

    d.node('norm', 40, 726, 660, 200,
           'Common result normalisation  (ocr_service.run_ocr)\n\n'
           '• _normalize_block(): guarantees text, content, box, confidence on every block\n'
           '• raw_results keeps the engine\'s original order\n'
           '• blocks WITH geometry → layout_service.reconstruct_layout(); blocks WITHOUT geometry are\n'
           '  appended afterwards so no text is silently dropped\n'
           '• layout_native = True (Modern, GLM, hybrid) skips the geometric reordering\n'
           '• engines that produce no visual artifact get a generated overlay image\n'
           '  (_render_overlay_image, colour-coded by confidence)\n\n'
           'Contract returned to app.py:\n'
           '{success, results[{text, content, box, confidence, index}], img_width, img_height,\n'
           ' elapsed_ms, ocr_engine, inference_status, layout_native?, markdown?, html?,\n'
           ' tables_html?, layout_blocks?, images?, raw_json?}',
           'svc', fontsize=9.5)

    d.edge('req', 'router', '', color='#82B366', srcside='right', dstside='left')
    d.edge('abc', 'router', 'implements', color='#3F61A8', dashed=True,
           srcside='left', dstside='right')
    d.edge('ad3', 'norm', '', color='#82B366', srcside='bottom', dstside='top',
           waypoints=[(895, 712), (370, 712)])
    d.edge('ad4', 'glm', '', color='#D79B00', srcside='bottom', dstside='top',
           waypoints=[(1245, 498), (1070, 498)])

    d.node('n1', 40, 950, 1360, 92,
           'Integration facts: the five adapters are instantiated once at import time in router.py, so heavy '
           'models are loaded lazily on first use and then reused. Adding or replacing an engine means adding one '
           'OCREngine subclass and one entry in _ENGINES / _ALIASES — the upload API, the persistence code and the '
           'database schema are unaffected, because every engine returns the same result contract. '
           'The GLM path is the only one that leaves the Flask process, and it is also the only one that can fail '
           'because of a missing environment (SDK venv) or an unavailable model server.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 3.8 Result representations
def f38():
    d = Diagram('fig_3_8_ocr_result_representations',
                'Hình 3.8 – Kết quả OCR dạng văn bản và dữ liệu có cấu trúc',
                1440, 1030,
                subtitle='Data flow behind the result view — which engine produces which representation, '
                         'how it is persisted and how it is delivered')

    d.node('res', 40, 110, 320, 168,
           'Engine result dict\n(one per page)\n\nresults[] · img_width / img_height\nelapsed_ms · ocr_engine\n'
           'inference_status · layout_native\nmarkdown? · html? · tables_html?\nlayout_blocks? · images? · raw_json?',
           'eng', fontsize=10)

    d.node('p1', 420, 100, 300, 76, '_ocr_pages_to_text()\njoin every block text across pages', 'svc', fontsize=10)
    d.node('p2', 420, 190, 300, 76, '_build_ocr_layout()\nboxes · confidence · size · timing', 'svc', fontsize=10)
    d.node('p3', 420, 280, 300, 100,
           '_persist_ocr_structured()\nmarkdown → markdown_normalize\n.repair_unmatched_display_math()', 'svc', fontsize=10)

    d.table('art', 800, 96, 380, 'document_artifacts written by app.py', [
        ('ocr                 plain text', 'all engines'),
        ('ocr_layout      JSON boxes / confidence', 'all engines'),
        ('ocr_images    JSON base64 overlays + crops', 'all engines'),
        ('ocr_json         JSON per-page regions', 'all engines'),
        ('ocr_markdown  Markdown', 'GLM · Modern'),
        ('ocr_html         HTML', 'Modern'),
        ('ocr_tables      JSON list of table HTML', 'GLM · Modern'),
        ('ocr_blocks     JSON label / content / bbox / order', 'GLM · Modern'),
    ], 'data')

    d.node('db', 1240, 96, 160, 226, 'SQLite\ndocument_artifacts\n\nUNIQUE\n(document_id, kind)\n\nupserted by\nsave_artifact()',
           'data', shape='cyl', fontsize=9.5)

    d.container('view', 40, 420, 700, 300,
                'Delivery to the browser   (static/app.js — OCRView)', 'ui', header=34)
    d.node('v1', 62, 470, 320, 56, 'Markdown tab\nvendored marked + KaTeX + sanitizeHtml()', 'ui', parent='view', fontsize=9.5)
    d.node('v2', 62, 538, 320, 56, 'Raw tab\nplain text joined from results[]', 'ui', parent='view', fontsize=9.5)
    d.node('v3', 62, 606, 320, 56, 'Images tab\nlayout overlays and cropped regions', 'ui', parent='view', fontsize=9.5)
    d.node('v4', 402, 470, 316, 56, 'JSON tab\nstructured per-page regions', 'ui', parent='view', fontsize=9.5)
    d.node('v5', 402, 538, 316, 56, 'Canvas overlay (ocr-canvas.js)\nboxes drawn over the page image', 'ui', parent='view', fontsize=9.5)
    d.node('v6', 402, 606, 316, 56, 'Statistics strip\nregions · mean confidence · time · pages', 'ui', parent='view', fontsize=9.5)

    d.container('exp', 780, 420, 620, 300, 'Export and downstream use', 'svc', header=34)
    d.node('x1', 802, 470, 280, 56, 'Download .md\n(real Markdown when available)', 'svc', parent='exp', fontsize=9.5)
    d.node('x2', 802, 538, 280, 56, 'Download .txt\nplain OCR text', 'svc', parent='exp', fontsize=9.5)
    d.node('x3', 802, 606, 280, 56, 'Download .json\nstructured output, all pages', 'svc', parent='exp', fontsize=9.5)
    d.node('x4', 1102, 470, 278, 90, 'POST /api/ocr/export-docx\npandoc  markdown+smart+tex_math_dollars\n→ .docx  (timeout 30 s)',
           'ext', parent='exp', fontsize=9.5)
    d.node('x5', 1102, 578, 278, 84, 'Vietnamese correction\nconsumes the ocr_json artifact →\ncorrected_json / corrected_md',
           'corr', parent='exp', fontsize=9.5)

    d.edge('res', 'p1', '', color='#82B366', srcside='right', dstside='left')
    d.edge('res', 'p2', '', color='#82B366', srcside='right', dstside='left')
    d.edge('res', 'p3', '', color='#82B366', srcside='right', dstside='left')
    d.edge('p1', 'art', '', color='#5A5A5A', srcside='right', dstside='left')
    d.edge('p2', 'art', '', color='#5A5A5A', srcside='right', dstside='left')
    d.edge('p3', 'art', '', color='#5A5A5A', srcside='right', dstside='left')
    d.edge('art', 'db', 'upsert', color='#5A5A5A', srcside='right', dstside='left')
    d.edge('res', 'view', 'HTTP response of /api/ocr/page and /api/ocr/all', color='#3F61A8',
           srcside='bottom', dstside='top', waypoints=[(200, 400), (390, 400)])
    d.edge('db', 'view', 'GET /api/documents/<id>/text  and  /ocr-images   (reopening a saved document)',
           color='#5A5A5A', dashed=True, srcside='bottom', dstside='top',
           waypoints=[(1320, 400), (390, 400)])
    d.edge('view', 'exp', '', color='#82B366', srcside='right', dstside='left')

    d.node('cap', 40, 748, 1360, 128,
           'Engine capability matrix (from the adapters)\n\n'
           'PaddleOCR Legacy   →  results + confidence + boxes;  ocr_json holds results + layout_blocks;  generated overlay image\n'
           'VietOCR                    →  results + boxes (confidence = None);  ocr_json fallback shape;  generated overlay image\n'
           'PaddleOCR Modern  →  results + confidence + boxes  +  markdown, html, tables_html, layout_blocks, labelled overlay\n'
           'GLM-OCR                  →  results + boxes (confidence = None)  +  markdown, tables_html, layout_blocks, raw_json,\n'
           '                                      layout_vis images and cropped region images\n'
           'GLM + VietOCR        →  GLM structure with VietOCR text, plus per-block recognition_source and fallback_reason',
           'note', shape='note', fontsize=9.5)

    d.node('todo', 40, 900, 1360, 96,
           'PARTIAL — the report presents Figure 3.8 as a screen capture of the result view. The diagram above is the '
           'architecture and data flow behind that screen, which is what the source code supports. If the report needs '
           'the screen itself, capture the OCR workspace of one document with the Markdown, Raw, Images and JSON tabs '
           'visible next to the page canvas (see MANUAL_COMPLETION.md, Figure 3.8).',
           'todo', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 3.9 Test-environment deployment
def f39():
    d = Diagram('fig_3_9_test_deployment',
                'Hình 3.9 – Mô hình triển khai hệ thống trong môi trường thử nghiệm',
                1400, 940,
                subtitle='Test-environment deployment exactly as documented in RUN_MACOS.md and '
                         'implemented in config.py / tools/glm_serve.sh')

    d.container('mach', 40, 92, 1000, 646,
                'Test machine  —  macOS Apple Silicon (M1 / M2 / M3 / M4) · Python 3.10 · Homebrew', 'proc', header=38)

    d.node('t1', 64, 150, 470, 152,
           'Terminal 1   —   GLM-OCR MLX model server\n\n'
           'GLM_ROOT="$PWD/glm-ocr-server"\nGLM_MLX_PYTHON="$PWD/glm-ocr-server/.venv-mlx/bin/python"\n'
           'bash glm-ocr-ui/tools/glm_serve.sh\n\n'
           'exec python -m mlx_vlm.server --trust-remote-code --port 8080\nmodel held resident between requests',
           'proc', parent='mach', fontsize=9.5)
    d.node('t2', 552, 150, 466, 152,
           'Terminal 2   —   SmartDocs web application\n\n'
           'cd glm-ocr-ui  ·  source .venv/bin/activate\npython app.py\n\n'
           'Flask threaded development server\nhttp://localhost:5001   (HOST 0.0.0.0, PORT 5001)',
           'api', parent='mach', fontsize=9.5)

    d.node('sdk', 64, 328, 470, 96,
           'GLM-OCR SDK  —  glm-ocr-server/.venv-sdk\nstarted per OCR request by glm_adapter.py:\n'
           'python -m glmocr.cli parse <page.png> --config mlx_config.yaml --mode selfhosted\n'
           'PP-DocLayoutV3 runs on the CPU (mlx_config.yaml: layout.device = cpu)',
           'proc', parent='mach', fontsize=9.5)
    d.node('eng', 552, 328, 466, 96,
           'In-process OCR engines (inside the Flask interpreter)\nPaddleOCR PP-OCRv5 · PP-StructureV3 + PP-OCRv6_medium\n'
           'VietOCR vgg_transformer\ncfg.DEVICE resolved automatically: CUDA → MPS → CPU',
           'eng', parent='mach', fontsize=9.5)

    d.node('db', 64, 450, 300, 88, 'SQLite  paddleocr.db\ncreated by db.create_all()\nseeded accounts:\n'
                                   'admin / admin123 · user / user123', 'data', parent='mach', shape='cyl', fontsize=9.5)
    d.node('up', 384, 450, 300, 88, 'uploads/\noriginal files, UUID-named\n+ transient page .png files\n'
                                    'MAX_UPLOAD_MB = 50', 'data', parent='mach', fontsize=9.5)
    d.node('mm', 704, 450, 314, 88, 'models/  ·  HF cache  ·  PaddleX cache\nOFFLINE=0 on the first run to fetch models,\n'
                                    'then OFFLINE=1 for offline operation', 'data', parent='mach', fontsize=9.5)

    d.node('env', 64, 562, 954, 152,
           '.env keys that define this environment  (glm-ocr-ui/.env, from .env.example and RUN_MACOS.md)\n\n'
           'HOST=0.0.0.0   PORT=5001   OFFLINE=0/1   DEVICE=auto   MODEL_DIR=./models   OCR_ENGINE=paddle\n'
           'GLM_ROOT=<repo>/glm-ocr-server        GLM_SDK_PYTHON=<repo>/glm-ocr-server/.venv-sdk/bin/python\n'
           'GLM_MLX_PYTHON=<repo>/glm-ocr-server/.venv-mlx/bin/python     GLM_CONFIG_YAML=<repo>/glm-ocr-server/mlx_config.yaml\n'
           'GLM_OCR_API_URL=http://localhost:8080   GLM_TIMEOUT=300\n'
           'VI_CORRECTION_ENABLED=true   VI_CORRECTION_PROVIDER=protonx   VI_CORRECTION_MODEL=nano   VI_CORRECTION_DEVICE=cpu',
           'ext', parent='mach', fontsize=9.5)

    d.node('cliB', 1080, 150, 280, 130,
           'Tester\nweb browser on the same machine\n(http://localhost:5001)\nor on another machine in the same\n'
           'network (HOST = 0.0.0.0)',
           'ui', fontsize=10)

    d.edge('cliB', 't2', 'HTTP', color='#3F61A8', srcside='left', dstside='right')
    d.edge('t2', 'sdk', 'subprocess', color='#D79B00', srcside='left', dstside='top',
           waypoints=[(540, 226), (540, 310), (299, 310)])
    d.edge('sdk', 't1', 'HTTP  localhost:8080', color='#D79B00', srcside='top', dstside='bottom')
    d.edge('t2', 'eng', 'in-process', color='#0E8088', srcside='bottom', dstside='top')
    d.edge('t2', 'db', 'SQLAlchemy', color='#5A5A5A', srcside='bottom', dstside='top',
           waypoints=[(785, 436), (214, 436)])
    d.edge('t2', 'up', 'file I/O', color='#5A5A5A', srcside='bottom', dstside='top',
           waypoints=[(785, 436), (534, 436)])

    d.node('todo', 1080, 310, 300, 300,
           'MANUAL COMPLETION REQUIRED\n\n'
           'The report asks Figure 3.9 to show the WebApp on port 5002 and a DesktopApp with the three '
           'backend modes Bundled Core, Existing WebApp Runtime and Remote Server.\n\n'
           'Neither exists in this repository: the application port is 5001 (config.py default and '
           'RUN_MACOS.md), and there is no desktop application, no runtime-mode selector and no '
           'remote-server client code.\n\n'
           'Port 5002 appears only in glm-ocr-server/glmocr/config.yaml and mlx_config.yaml as the default '
           'port of the optional glmocr.server HTTP wrapper, which SmartDocs does not use — it calls the CLI '
           'instead.',
           'todo', shape='note', fontsize=9.5)

    d.node('n1', 40, 762, 1320, 62,
           'Access rule visible in the deployment: the browser talks only to Flask on :5001. The MLX model server '
           'on :8080 is reached exclusively by the transient glmocr subprocess, and the database and the uploads '
           'directory are reached exclusively by app.py / models.py, so authorisation, document status and the '
           'activity log stay consistent regardless of the client.',
           'note', shape='note', fontsize=10)
    d.node('n2', 40, 838, 1320, 62,
           'Not part of the test environment: no container runtime, no reverse proxy, no production WSGI server, '
           'no external database and no cloud OCR service. The GLM cloud (MaaS) path of the SDK is disabled by '
           'mlx_config.yaml (pipeline.maas.enabled = false) and the adapter always passes --mode selfhosted.',
           'note', shape='note', fontsize=10)
    return d


if __name__ == '__main__':
    for fn in (f31, f32, f36, f37, f38, f39):
        write(fn())
