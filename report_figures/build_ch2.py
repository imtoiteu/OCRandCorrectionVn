#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chapter 2 report figures (2.1 - 2.10).

Every element is grounded in the OCRandCorrectionVn source tree; see
FIGURE_INDEX.md for the per-figure source-file list.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram_engine import Diagram, write, set_out, row_x

set_out(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chapter2'))

SYS = 'SmartDocs Web Application  (glm-ocr-ui, Flask :5001)'


# ══════════════════════════════════════════════════ 2.1 Use case
def f21():
    d = Diagram('fig_2_1_use_case',
                'Hình 2.1 – Biểu đồ ca sử dụng tổng quát của hệ thống',
                1300, 1090,
                subtitle='General use case diagram — derived from the Flask routes in '
                         'app.py, auth.py, admin_bp.py and correction_bp.py')

    d.node('act_user', 60, 330, 130, 96, 'User\n(role = "user")', 'actor', shape='actor', fontsize=12)
    d.node('act_admin', 1120, 330, 130, 96, 'Administrator\n(role = "admin")', 'actor', shape='actor', fontsize=12)

    d.container('sys', 240, 92, 800, 826, SYS, 'ui', header=38)

    user_uc = [
        ('u1',  'Log in / Log out\n/login · /logout'),
        ('u2',  'Upload document\nPOST /api/upload'),
        ('u3',  'Preview page / navigate pages\nPOST /api/ocr/page (preview_only)'),
        ('u4',  'Select OCR engine\n(engine parameter)'),
        ('u5',  'Run OCR on one page\nPOST /api/ocr/page'),
        ('u6',  'Run OCR on all pages\nPOST /api/ocr/all'),
        ('u7',  'Re-order a selected region\nPOST /api/ocr/reconstruct-region'),
        ('u8',  'Read text from TXT / DOCX / PDF\nPOST /api/read-text'),
        ('u9',  'View results (Markdown · Raw ·\nImages · JSON)'),
        ('u10', 'Copy / download results\n.md · .txt · .json · .docx'),
        ('u11', 'Manage own document library\nGET/DELETE /api/documents'),
        ('u12', 'Run Vietnamese OCR correction\nPOST /api/correction/run'),
        ('u13', 'Save / reload corrected result\n/api/correction/save · /result'),
        ('u14', 'Switch UI language\nPOST /api/set-lang'),
    ]
    y = 146
    for i, (uid, lab) in enumerate(user_uc):
        d.node(uid, 276, y + i * 54, 330, 46, lab, 'svc', shape='ellipse', fontsize=9.5)

    adm_uc = [
        ('a1', 'View admin dashboard\nGET /admin/'),
        ('a2', 'Manage user accounts\ncreate · edit · reset password\nenable/disable · delete'),
        ('a3', 'Oversee all documents\nGET /admin/files'),
        ('a4', 'View activity logs\nGET /admin/logs'),
        ('a5', 'Access any user\'s documents\n(admin override in ownership check)'),
    ]
    ay = 300
    for i, (uid, lab) in enumerate(adm_uc):
        d.node(uid, 660, ay + i * 96, 350, 66, lab, 'corr', shape='ellipse', fontsize=9.5)

    for uid, _ in user_uc:
        d.edge('act_user', uid, '', color='#33475B', arrow='none',
               srcside='right', dstside='left')
    for uid, _ in adm_uc:
        d.edge('act_admin', uid, '', color='#9673A6', arrow='none',
               srcside='left', dstside='right')
    d.edge('act_admin', 'act_user',
           '«generalization» — an administrator also performs every User use case',
           dashed=True, color='#33475B', waypoints=[(1185, 944), (125, 944)],
           srcside='bottom', dstside='bottom')

    d.node('n1', 240, 1000, 800, 62,
           'Scope note: the system has no in-application "OCR configuration" screen — engine '
           'defaults are set through environment variables read by config.py (OCR_ENGINE, '
           'VIETOCR_*, GLM_*, VI_CORRECTION_*). No such use case is shown.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 2.2 Context
def f22():
    d = Diagram('fig_2_2_context',
                'Hình 2.2 – Biểu đồ ngữ cảnh của hệ thống số hóa tài liệu',
                1320, 900,
                subtitle='System boundary and external actors / processes / data stores actually '
                         'present in the repository')

    d.node('sys', 430, 336, 440, 150,
           'Document Digitization System\n' + SYS +
           '\napp.py · auth.py · admin_bp.py · correction_bp.py',
           'api', shape='round', fontsize=13, bold=True)

    d.node('user', 130, 118, 130, 96, 'User', 'actor', shape='actor')
    d.node('admin', 1040, 118, 130, 96, 'Administrator', 'actor', shape='actor')

    d.node('paddle', 60, 590, 300, 116,
           'In-process OCR runtimes\nPaddleOCR (PP-OCRv5)\nPP-StructureV3 (PP-OCRv6)\n'
           'VietOCR (vgg_transformer)',
           'eng', fontsize=11)
    d.node('glmcli', 470, 574, 360, 74,
           'GLM-OCR SDK subprocess\nglm-ocr-server/.venv-sdk · glmocr.cli parse',
           'proc', fontsize=11)
    d.node('mlx', 470, 700, 360, 74,
           'GLM-OCR MLX model server\nhttp://localhost:8080 · mlx-community/GLM-OCR-bf16',
           'proc', fontsize=11)
    d.node('store', 940, 590, 320, 116,
           'Data area\nSQLite  paddleocr.db\nuploads/  (UUID-named originals)\n'
           'models/  (local model store)',
           'data', fontsize=11)
    d.node('pandoc', 1000, 336, 260, 70,
           'pandoc executable\n(Markdown → DOCX export)', 'ext', fontsize=11)

    d.edge('user', 'sys', '→  Account, document, OCR request\n←  Status, results, history',
           color='#3F61A8', arrow='both')
    d.edge('admin', 'sys', '→  User management, log / file queries\n←  Logs, statistics, system state',
           color='#9673A6', arrow='both')
    d.edge('sys', 'paddle', '→  Normalized page image\n←  Text blocks, boxes, confidence',
           color='#0E8088', arrow='both')
    d.edge('sys', 'glmcli', '→  Page image + CLI arguments\n←  JSON / Markdown / layout_vis / imgs',
           color='#D79B00', arrow='both')
    d.edge('glmcli', 'mlx', '→  HTTP /chat/completions (per region)\n←  Recognized region content',
           color='#D79B00', arrow='both')
    d.edge('sys', 'store', '→  Original file, artifacts, records\n←  Stored documents and artifacts',
           color='#5A5A5A', arrow='both')
    d.edge('sys', 'pandoc', '→  Markdown    ←  .docx', color='#999999', arrow='both')

    d.node('n1', 60, 792, 1200, 62,
           'The GLM-OCR path is optional and Apple-Silicon only: config.py resolves GLM_ROOT / '
           'GLM_SDK_PYTHON / GLM_OCR_API_URL, and glm_adapter.py refuses to run when the SDK venv is '
           'missing or nothing is listening on the MLX port. Cloud (MaaS) OCR is disabled — mlx_config.yaml '
           'sets pipeline.maas.enabled: false.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 2.3 Overall architecture
def f23():
    d = Diagram('fig_2_3_architecture',
                'Hình 2.3 – Kiến trúc tổng thể các thành phần của hệ thống',
                1400, 1130,
                subtitle='Layered component architecture reconstructed from the implementation '
                         '(glm-ocr-ui/ and glm-ocr-server/)')

    SL = [62, 300, 538, 776]          # four aligned column slots
    NW = 230

    # ── L1 presentation ────────────────────────────────────────────────────
    d.container('l1', 40, 92, 1000, 134, 'Presentation layer  (browser)', 'ui')
    d.node('corrpage', SL[0], 140, NW, 70, 'Correction page\nstatic/correction.html\ncorrection.js',
           'corr', parent='l1', fontsize=10)
    d.node('spa', SL[1], 140, NW, 70, 'SmartDocs SPA\nstatic/index.html · app.js\nocr-canvas.js · i18n.js',
           'ui', parent='l1', fontsize=10)
    d.node('adminui', SL[2], 140, NW, 70, 'Admin console (Jinja)\ntemplates/admin/\nbase·dashboard·users·logs·files',
           'ui', parent='l1', fontsize=10)
    d.node('loginui', SL[3], 140, NW, 70, 'Login / 403 pages\ntemplates/login.html\ntemplates/403.html',
           'ui', parent='l1', fontsize=10)

    # ── L2 application ─────────────────────────────────────────────────────
    d.container('l2', 40, 262, 1000, 150,
                'Application layer  —  Flask app (app.py; threaded development server, HOST/PORT from config.py)', 'api')
    d.node('corrbp', SL[0], 314, NW, 82,
           'correction_bp\ncorrection_bp.py\n/correction\n/api/correction/*', 'api', parent='l2', fontsize=9.5)
    d.node('routes', SL[1], 314, NW, 82,
           'Core routes (app.py)\n/api/upload · /api/ocr/page\n/api/ocr/all · /api/documents\n/api/ocr/export-docx',
           'api', parent='l2', fontsize=9.5)
    d.node('adminbp', SL[2], 314, NW, 82,
           'admin_bp\nadmin_bp.py\n/admin dashboard · users\nlogs · files', 'api', parent='l2', fontsize=9.5)
    d.node('authbp', SL[3], 314, NW, 82,
           'auth_bp (auth.py)\nlogin / logout\n/api/auth/me · /api/set-lang\n@admin_required',
           'api', parent='l2', fontsize=9.5)

    # ── L3 services ────────────────────────────────────────────────────────
    d.container('l3', 40, 442, 1000, 158, 'Service layer  (services/)', 'svc')
    d.node('vicorr', SL[0], 494, NW, 88,
           'vi_correction/\nclassification · masking\nsegmentation · pipeline\nvalidation · renderers · service',
           'corr', parent='l3', fontsize=9.5)
    d.node('ocrsvc', SL[1], 494, NW, 88,
           'ocr_service.py\nsmart_ocr_service.py\nblock normalization,\noverlay rendering',
           'svc', parent='l3', fontsize=9.5)
    d.node('layout', SL[2], 494, NW, 88,
           'layout_service.py\ngeometry_service.py\nreading-order\nreconstruction', 'svc', parent='l3', fontsize=9.5)
    d.node('textsvc', SL[3], 494, NW, 88,
           'text_service.py\nmarkdown_normalize.py\nactivity_registry.py\ncpu_threads.py',
           'svc', parent='l3', fontsize=9.5)

    # ── L4 OCR engines ─────────────────────────────────────────────────────
    d.container('l4', 40, 630, 1000, 226,
                'OCR engine layer  (services/ocr_engines/ — OCREngine abstract base + adapters)', 'eng')
    d.node('router', 62, 682, 956, 46,
           'router.py   —   _ENGINES registry · _ALIASES · normalize_engine_name() · get_engine() · run_ocr()',
           'eng', parent='l4', fontsize=11, bold=True)
    d.node('e_pad', SL[0], 744, NW, 92,
           'PaddleOCREngine\npaddleocr.PaddleOCR\nocr_version = PP-OCRv5\n(text lines + boxes + conf.)',
           'eng', parent='l4', fontsize=9.5)
    d.node('e_mod', SL[1], 744, NW, 92,
           'PaddleOCRModernEngine\npaddleocr.PPStructureV3\nPP-OCRv6_medium det/rec\n(markdown · html · tables)',
           'eng', parent='l4', fontsize=9.5)
    d.node('e_vi', SL[2], 744, NW, 92,
           'VietOCREngine\nPP-OCRv5 line detector +\nvietocr Predictor\n(vgg_transformer)',
           'eng', parent='l4', fontsize=9.5)
    d.node('e_glm', SL[3], 744, NW, 92,
           'GLMOCREngine\nGLMVietOCREngine\nsubprocess client\n(layout-native results)',
           'eng', parent='l4', fontsize=9.5)

    # ── row 5: correction providers | external processes ───────────────────
    d.container('l4b', 40, 886, 596, 156,
                'Correction providers  (services/vi_correction/providers/)', 'corr', header=32)
    d.node('p_px', 62, 930, 254, 48, 'ProtonxProvider\nnano · distilled · full', 'corr', parent='l4b', fontsize=10)
    d.node('p_bmd', 336, 930, 254, 48, 'Bmd1905Provider\nvietnamese-correction-v2', 'corr', parent='l4b', fontsize=10)
    d.node('p_mock', 62, 986, 254, 44, 'MockProvider', 'corr', parent='l4b', fontsize=10)
    d.node('p_mr', 336, 986, 254, 44, 'MrlasdtProvider (registry entry)', 'corr', parent='l4b', fontsize=10)

    d.container('ext', 660, 886, 380, 156,
                'External processes  (optional · Apple Silicon)', 'proc', header=32)
    d.node('glmsdk', 682, 930, 336, 48,
           'glmocr CLI  ·  .venv-sdk\nPP-DocLayoutV3 layout detection', 'proc', parent='ext', fontsize=10)
    d.node('mlxsrv', 682, 986, 336, 44,
           'MLX server :8080  ·  .venv-mlx\nmlx-community/GLM-OCR-bf16', 'proc', parent='ext', fontsize=10)

    # ── data column ────────────────────────────────────────────────────────
    d.container('data', 1060, 262, 300, 594,
                'Data layer  (reached only via models.py / SQLAlchemy and app.py file I/O)', 'data', header=48)
    d.node('db', 1082, 328, 256, 84, 'SQLite\npaddleocr.db\n(cfg.DB_PATH)', 'data',
           parent='data', shape='cyl', fontsize=10.5)
    d.node('up', 1082, 434, 256, 80, 'uploads/\n{uuid4}{suffix}\n(cfg.UPLOAD_DIR)', 'data',
           parent='data', fontsize=10.5)
    d.node('mdl', 1082, 540, 256, 80, 'models/  +  HF cache\n(cfg.MODEL_DIR;\nOFFLINE=1 blocks downloads)',
           'data', parent='data', fontsize=10.5)
    d.node('dnote', 1082, 646, 256, 190,
           'Physical schema (models.py)\n• users\n• documents\n• document_artifacts\n• activity_logs\n\n'
           'No external database server,\nobject store, cache or message\nqueue is used by this build.',
           'data', parent='data', fontsize=9.5)

    # ── edges ──────────────────────────────────────────────────────────────
    for s_, t_ in (('corrpage', 'corrbp'), ('spa', 'routes'),
                   ('adminui', 'adminbp'), ('loginui', 'authbp')):
        d.edge(s_, t_, '', color='#3F61A8', srcside='bottom', dstside='top')
    d.edge('corrbp', 'vicorr', '', color='#9673A6', srcside='bottom', dstside='top')
    d.edge('routes', 'ocrsvc', '', color='#82B366', srcside='bottom', dstside='top')
    d.edge('routes', 'textsvc', '', color='#82B366', srcside='bottom', dstside='top',
           waypoints=[(415, 424), (891, 424)])
    d.edge('ocrsvc', 'layout', '', color='#82B366', arrow='none', srcside='right', dstside='left')
    d.edge('ocrsvc', 'router', '', color='#0E8088', srcside='bottom', dstside='top',
           waypoints=[(415, 612), (540, 612)])
    for nid, cx in (('e_pad', 177), ('e_mod', 415), ('e_vi', 653), ('e_glm', 891)):
        d.edge('router', nid, '', color='#0E8088', srcside='bottom', dstside='top',
               waypoints=[(540, 736), (cx, 736)])
    d.edge('vicorr', 'p_px', '', color='#9673A6',
           srcside='left', dstside='left', waypoints=[(24, 538), (24, 954)])
    d.edge('e_glm', 'glmsdk', 'subprocess.run()', color='#D79B00',
           srcside='bottom', dstside='top', waypoints=[(891, 870), (850, 870)])
    d.edge('glmsdk', 'mlxsrv', 'HTTP', color='#D79B00', srcside='bottom', dstside='top')
    d.edge('l2', 'data', '', color='#5A5A5A',
           srcside='right', dstside='left', waypoints=[(1050, 337), (1050, 559)])
    d.edge('l4', 'mdl', '', color='#5A5A5A',
           srcside='right', dstside='left', waypoints=[(1050, 743), (1050, 580)])

    d.node('n1', 40, 1062, 1320, 52,
           'Not present in this repository, and therefore not shown: the Tauri/Rust desktop application, and the '
           'RAG chat, translation, summarization and LLM-agent modules referenced by README.md and docs/. '
           'Only the components drawn above exist in the code of this build.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 2.4 Deployment
def f24():
    d = Diagram('fig_2_4_deployment',
                'Hình 2.4 – Kiến trúc triển khai của hệ thống',
                1340, 800,
                subtitle='Deployment view — processes, ports and communication paths defined by '
                         'app.py, config.py, tools/glm_serve.sh and RUN_MACOS.md')

    d.container('client', 50, 100, 300, 230, 'Client device', 'ui')
    d.node('browser', 76, 152, 248, 76, 'Web browser\nSPA + server-rendered admin pages\n(no frontend build step)',
           'ui', parent='client', fontsize=10.5)
    d.node('brnote', 76, 244, 248, 64, 'http://<host>:5001\nSession cookie\n(HttpOnly · SameSite=Lax)',
           'ui', parent='client', fontsize=9.5)

    d.container('host', 430, 100, 800, 530,
                'Application host  —  macOS Apple Silicon · Python 3.10  (RUN_MACOS.md)', 'proc', header=38)

    d.node('flask', 460, 158, 740, 82,
           'Process 1 · Flask application server\nglm-ocr-ui/.venv/bin/python app.py\n'
           'app.run(host=cfg.HOST 0.0.0.0, port=cfg.PORT 5001, threaded=True, debug=False)',
           'api', parent='host', fontsize=11, bold=True)

    d.node('inproc', 460, 268, 356, 80,
           'In-process OCR runtimes\n(same interpreter as Flask)\nPaddleOCR · PP-StructureV3 · VietOCR',
           'eng', parent='host', fontsize=10)
    d.node('sdkp', 844, 268, 356, 80,
           'Process 3 (transient) · GLM-OCR SDK\n.venv-sdk · python -m glmocr.cli parse\n'
           'spawned per OCR call · timeout GLM_TIMEOUT',
           'proc', parent='host', fontsize=10)
    d.node('pandoc', 460, 392, 356, 80,
           'pandoc executable (optional)\nresolved with shutil.which() at import;\n'
           '/api/ocr/export-docx returns 501 if absent',
           'ext', parent='host', fontsize=10)
    d.node('mlxp', 844, 392, 356, 80,
           'Process 2 · GLM-OCR MLX model server\n.venv-mlx · python -m mlx_vlm.server\n'
           'listens on :8080 · model held resident',
           'proc', parent='host', fontsize=10)

    d.container('stor', 460, 516, 740, 96, 'Local storage on the host', 'data', header=30)
    d.node('db', 478, 552, 226, 50, 'SQLite  paddleocr.db\n(cfg.DB_PATH)', 'data',
           parent='stor', shape='cyl', fontsize=10)
    d.node('up', 722, 552, 216, 50, 'uploads/ {uuid4}{suffix}\n(cfg.UPLOAD_DIR)', 'data', parent='stor', fontsize=10)
    d.node('mdl', 956, 552, 226, 50, 'models/ + HF cache\n(cfg.MODEL_DIR)', 'data', parent='stor', fontsize=10)

    d.edge('browser', 'flask', 'HTTP  (localhost or LAN)\nJSON + multipart upload', color='#3F61A8',
           srcside='right', dstside='left')
    d.edge('flask', 'inproc', 'in-process call', color='#0E8088',
           srcside='bottom', dstside='top', waypoints=[(830, 254), (638, 254)])
    d.edge('flask', 'sdkp', 'subprocess.run()\nsanitized environment', color='#D79B00',
           srcside='bottom', dstside='top', waypoints=[(830, 254), (1022, 254)])
    d.edge('sdkp', 'mlxp', 'HTTP localhost:8080  ·  /chat/completions', color='#D79B00',
           srcside='bottom', dstside='top')
    d.edge('flask', 'pandoc', 'subprocess.run(pandoc)', color='#999999',
           srcside='left', dstside='left', waypoints=[(452, 199), (452, 432)])
    d.edge('flask', 'stor', 'SQLAlchemy  ·  file I/O', color='#5A5A5A',
           srcside='right', dstside='right', waypoints=[(1216, 199), (1216, 564)])
    d.edge('inproc', 'mdl', 'model files', color='#5A5A5A', dashed=True,
           srcside='bottom', dstside='top', waypoints=[(638, 494), (1069, 494)])

    d.node('n1', 50, 660, 1240, 92,
           'Deployment facts taken from the repository: there is no container, reverse proxy, production WSGI '
           'server, message queue or managed cloud service for the web application — app.py starts Flask\'s own '
           'threaded development server. The Dockerfiles and docker start scripts under glm-ocr-server/apps/ '
           'belong to the upstream GLM-OCR demo (FastAPI backend + React frontend) and are not used by SmartDocs. '
           'Processes 2 and 3 are optional: without them only the PaddleOCR / VietOCR engines are available.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 2.5 Sequence
def f25():
    d = Diagram('fig_2_5_sequence_ocr',
                'Hình 2.5 – Biểu đồ tuần tự quá trình xử lý một yêu cầu OCR',
                1380, 1276,
                subtitle='Traced from app.py (/api/upload, /api/ocr/page), ocr_service.py, '
                         'services/ocr_engines/router.py, glm_adapter.py and models.py')

    LL = [('u', 120, 'User\n(browser SPA)', 'ui'),
          ('api', 330, 'Flask app.py\nroute handler', 'api'),
          ('svc', 550, 'ocr_service /\nsmart_ocr_service', 'svc'),
          ('rt', 770, 'ocr_engines\nrouter + adapter', 'eng'),
          ('ext', 990, 'GLM SDK subprocess\n+ MLX server :8080', 'proc'),
          ('db', 1210, 'models.py\nSQLite + uploads/', 'data')]
    for lid, x, lab, key in LL:
        d.lifeline(lid, x, lab, key, hy=100, hh=54, hw=178, bottom=1218)

    m = d.message
    seq = [
        ('u', 'api', 'POST /api/upload   (multipart file)', False, 'call', 38),
        ('api', 'api', '@login_required · MAX_CONTENT_LENGTH · _safe_basename() · extension allowlist',
         False, 'self', 58),
        ('api', 'db', 'save uploads/{uuid4}{suffix} · INSERT Document(status="uploaded") · log_activity("upload")',
         False, 'call', 36),
        ('db', 'api', 'doc_id, file_id', True, 'call', 32),
        ('api', 'u', '200 {file_id, filename, page_count, is_pdf, …}', True, 'call', 52),
        ('u', 'api', 'POST /api/ocr/page  {file_id, page, engine}', False, 'call', 36),
        ('api', 'db', '_resolve_owned_file(): Document lookup + ownership / admin check', False, 'call', 32),
        ('db', 'api', 'on-disk Path  (404 unknown · 403 not owner)', True, 'call', 42),
        ('api', 'api', 'PDF → pdf_page_to_pil(scale=2.0) → temporary .png     |     image → PIL.Image.open()',
         False, 'self', 62),
        ('api', 'api', '_resolve_selected_engine(): normalize_engine_name(); "vietocr" + ".pdf" → "paddleocr"',
         False, 'self', 74),
        ('api', 'svc', 'smart_ocr_service.run_ocr_pipeline(image_path, engine_name)', False, 'call', 36),
        ('svc', 'rt', 'router.run_ocr() → get_engine(name).run(image_path)', False, 'call', 38),
        ('rt', 'ext', 'GLM engines only: TCP health check on :8080, then subprocess glmocr.cli parse',
         False, 'call', 42),
        ('ext', 'ext', 'PP-DocLayoutV3 layout detection → per-region VLM call → JSON / Markdown / imgs',
         False, 'self', 58),
        ('ext', 'rt', 'artifacts read from the output directory', True, 'call', 36),
        ('rt', 'svc', '{success, results[text/box/confidence], img_width, img_height, elapsed_ms, …}',
         True, 'call', 42),
        ('svc', 'svc', '_normalize_block() · reading-order reconstruction (skipped when layout_native) · overlay render',
         False, 'self', 62),
        ('svc', 'api', 'normalized result dict', True, 'call', 36),
        ('api', 'db', 'status = "ocr_done" · save_artifact(ocr, ocr_layout, ocr_markdown, ocr_json, ocr_images …)',
         False, 'call', 34),
        ('api', 'db', 'log_activity("ocr", engine · processing_time_ms · inference_status)', False, 'call', 38),
        ('api', 'u', '200 {results, page_image_b64, markdown, images, elapsed_ms}', True, 'call', 36),
    ]
    y = 194
    for frm, to, lab, dash, kind, step in seq:
        m(frm, to, y, lab, dashed=dash, kind=kind)
        y += step

    d.fragment(52, 1094, 1310, 1208, 'alt  [engine failure]')
    m('rt', 'api', 1138, 'structured error {success: false, error, inference_status: "error"}',
      dashed=True, color='#B85450')
    m('api', 'u', 1180, 'HTTP 500 / {success: false} → SPA error toast; traceback written to the application log',
      dashed=True, color='#B85450')
    return d


# ══════════════════════════════════════════════════ 2.6 General workflow
def f26():
    d = Diagram('fig_2_6_document_workflow',
                'Hình 2.6 – Quy trình xử lý tài liệu tổng quát của hệ thống',
                1300, 1170,
                subtitle='Flow chart of the implemented request path (app.py · ocr_service.py · models.py)')

    X = 300
    W = 380
    steps = [
        ('s1',  118, 46, 'Start — user selects a file in the SPA', 'flow', 'round'),
        ('d1',  186, 62, 'Authenticated?\n@login_required', 'dec', 'diamond'),
        ('d2',  272, 62, 'Body ≤ MAX_CONTENT_LENGTH?\n(cfg.MAX_UPLOAD_MB = 50)', 'dec', 'diamond'),
        ('d3',  358, 62, 'Extension in allowlist?\n.jpg .jpeg .png .webp .pdf .txt .docx', 'dec', 'diamond'),
        ('s2',  444, 50, 'Sanitize display name · generate UUID ·\nsave uploads/{uuid}{suffix}', 'flow', 'round'),
        ('s3',  518, 50, 'Count pages (pypdfium2) · INSERT Document\n(status = "uploaded") · log_activity', 'flow', 'round'),
        ('d4',  592, 62, 'File type?', 'dec', 'diamond'),
        ('s4',  678, 50, 'Render page → PIL image\n(PDF: pdf_page_to_pil, scale = 2.0)', 'flow', 'round'),
        ('s5',  752, 46, 'Resolve OCR engine (request parameter → alias → default)', 'flow', 'round'),
        ('s6',  818, 46, 'Run the selected engine adapter', 'eng', 'round'),
        ('d5',  884, 62, 'OCR succeeded?', 'dec', 'diamond'),
        ('s7',  970, 50, 'Post-process: normalize blocks · reading-order\nreconstruction · overlay image', 'svc', 'round'),
        ('s8', 1044, 46, 'Persist artifacts · status = "ocr_done" · log_activity("ocr")', 'data', 'round'),
    ]
    for sid, y, h, lab, key, shape in steps:
        d.node(sid, X, y, W, h, lab, key, shape=shape, fontsize=10.5)

    order = [s[0] for s in steps]
    labels = {('d1', 'd2'): 'yes', ('d2', 'd3'): 'yes', ('d3', 's2'): 'yes',
              ('d4', 's4'): 'image / PDF', ('d5', 's7'): 'yes'}
    for a, b in zip(order, order[1:]):
        d.edge(a, b, labels.get((a, b), ''), color='#4B6E9C', srcside='bottom', dstside='top')

    d.node('sTxt', 760, 678, 300, 50, 'TXT / DOCX / PDF text\n/api/read-text → text_service.read_file()',
           'svc', fontsize=10)
    d.edge('d4', 'sTxt', 'text file', color='#82B366', srcside='right', dstside='left')
    d.node('sTxt2', 760, 752, 300, 46, 'save_artifact(kind = "text")', 'data', fontsize=10)
    d.edge('sTxt', 'sTxt2', '', color='#82B366', srcside='bottom', dstside='top')
    d.edge('sTxt2', 's8', '', color='#82B366', dashed=True,
           waypoints=[(1110, 775), (1110, 1067)], srcside='right', dstside='right')

    d.node('sEnd', 300, 1118, 380, 0, '', 'flow')  # placeholder (not drawn meaningfully)
    d.nodes.remove(d.byid.pop('sEnd'))

    ERR = 900
    errs = [
        ('e1', 186, '401 / redirect to /login'),
        ('e2', 272, '413 {"error": "File too large"}'),
        ('e3', 358, '400 {"error": "Unsupported type"}'),
        ('e5', 884, '500 {"error": "OCR failed (engine)"}\ntraceback written to the log'),
    ]
    for eid, y, lab in errs:
        d.node(eid, ERR, y, 330, 56, lab, 'err', fontsize=10)
    d.edge('d1', 'e1', 'no', color='#B85450', srcside='right', dstside='left')
    d.edge('d2', 'e2', 'no', color='#B85450', srcside='right', dstside='left')
    d.edge('d3', 'e3', 'no', color='#B85450', srcside='right', dstside='left')
    d.edge('d5', 'e5', 'no', color='#B85450', srcside='right', dstside='left')

    d.node('own', 44, 460, 230, 76,
           'Every later request re-checks ownership:\n_resolve_owned_file() → 404 unknown,\n403 not owner (admins exempt)',
           'err', fontsize=9.5)
    d.edge('own', 's5', '', color='#B85450', dashed=True, srcside='right', dstside='left')

    d.node('res', 44, 960, 230, 120,
           'Result delivery\n• JSON response → SPA\n• Markdown / Raw / Images / JSON tabs\n'
           '• Download .md .txt .json .docx\n• Optional Vietnamese correction\n  (/api/correction/run)',
           'ui', fontsize=9.5)
    d.edge('s8', 'res', '', color='#3F61A8', srcside='left', dstside='right')

    d.node('n1', 44, 1096, 1216, 56,
           'Note: preprocessing is limited to page rasterization and, for the PaddleOCR Modern engine, '
           'the pipeline\'s own document orientation classification and UVDoc unwarping. No separate '
           'binarization / deskew stage exists in the application code.',
           'note', shape='note', fontsize=9.5)
    return d


# ══════════════════════════════════════════════════ 2.7 Engine selection
def f27():
    d = Diagram('fig_2_7_engine_selection',
                'Hình 2.7 – Cơ chế lựa chọn công cụ OCR theo đặc điểm tài liệu',
                1340, 1000,
                subtitle='The mechanism as implemented — app.py::_resolve_selected_engine(), '
                         'router.py::normalize_engine_name(), glm_vietocr_adapter.py')

    d.node('warn', 40, 92, 1260, 74,
           'IMPORTANT — the system does NOT implement automatic engine selection from document content. '
           'No code inspects layout complexity, language or image quality to choose an engine. '
           'The engine is chosen by the user (UI drop-down) or by configuration; only two rule-based '
           'decisions exist, and both are shown below.',
           'todo', shape='note', fontsize=11, bold=True)

    d.node('start', 460, 196, 420, 46, 'OCR request:  {file_id, page, engine?}', 'flow', fontsize=11, bold=True)
    d.node('d1', 440, 268, 460, 68, 'Was an "engine" value sent\nwith the request?', 'dec', shape='diamond', fontsize=10.5)
    d.node('cfg', 40, 278, 340, 62, 'No → fall back to cfg.OCR_ENGINE\n(env OCR_ENGINE, default "paddle")',
           'flow', fontsize=10)
    d.node('ui', 960, 254, 340, 110,
           'Yes → the value chosen in the SPA drop-down\n"Recommended"  → glmocr\n"GLM Layout + VietOCR Text"  → glm_vietocr\n'
           '"Vietnamese"  → vietocr\n"Standard"  → paddleocr',
           'ui', fontsize=10)
    d.node('norm', 440, 368, 460, 66,
           'normalize_engine_name(): alias table\npaddle|auto→paddleocr · modern|ppstructure→paddleocr_modern\n'
           'glm|glm_ocr→glmocr · glm_layout_vietocr→glm_vietocr',
           'eng', fontsize=9.5)
    d.node('bad', 960, 380, 340, 46, 'Unknown alias → ValueError → HTTP 400', 'err', fontsize=10)

    d.node('d2', 420, 466, 500, 76,
           'RULE 1 (file-type rule)\nselected == "vietocr"  AND  file suffix == ".pdf" ?',
           'dec', shape='diamond', fontsize=10.5)
    d.node('fb', 960, 476, 340, 58,
           'effective = "paddleocr"\ninference_status = "fallback_to_paddle_for_pdf"',
           'err', fontsize=10)
    d.node('disp', 440, 578, 460, 46, 'effective engine → router.get_engine(name).run(image)', 'eng',
           fontsize=11, bold=True)

    eng_y = 660
    labels = [
        ('en1', 'PaddleOCREngine\nPP-OCRv5\n(text lines + boxes)'),
        ('en2', 'PaddleOCRModernEngine\nPP-StructureV3 + PP-OCRv6\n(markdown/html/tables)'),
        ('en3', 'VietOCREngine\nPP-OCRv5 detector +\nVietOCR recognizer'),
        ('en4', 'GLMOCREngine\nPP-DocLayoutV3 + GLM-OCR\nVLM (subprocess)'),
        ('en5', 'GLMVietOCREngine\nGLM layout + VietOCR text'),
    ]
    xs = row_x(40, 1300, 5, 236)
    for (nid, lab), x in zip(labels, xs):
        d.node(nid, x, eng_y, 236, 84, lab, 'eng', fontsize=9.5)
        d.edge('disp', nid, '', color='#0E8088', srcside='bottom', dstside='top')

    d.node('r2', 40, 782, 620, 128,
           'RULE 2 (per-block rule, only inside GLMVietOCREngine)\n'
           '• block label ∈ {table, figure, image, equation, formula, code} → keep the GLM text verbatim\n'
           '• otherwise assign the VietOCR text lines whose centre falls inside the GLM block box\n'
           '• sanity check: if len(GLM text) > 40 chars and the VietOCR text is < 25 % of that length,\n'
           '  reject it and fall back to the GLM text (recognition_source = "glm" / "fallback")',
           'corr', fontsize=10)
    d.edge('en5', 'r2', '', color='#9673A6', dashed=True, srcside='bottom', dstside='right')

    d.node('n2', 700, 782, 600, 128,
           'Additional facts from the source\n'
           '• paddleocr_modern is registered in router.py and reachable through the API, but it is not\n'
           '  offered in the SPA drop-down (static/index.html).\n'
           '• The chosen engine is recorded per request: res["selected_engine"], res["ocr_engine"] and the\n'
           '  ActivityLog detail string, so repeated runs on one document can be compared afterwards.\n'
           '• The user\'s manual choice is preserved for the whole session (OCRView._sessionEngine).',
           'note', shape='note', fontsize=10)

    d.edge('start', 'd1', '', color='#4B6E9C', srcside='bottom', dstside='top')
    d.edge('d1', 'cfg', 'no', color='#4B6E9C', srcside='left', dstside='right')
    d.edge('d1', 'ui', 'yes', color='#4B6E9C', srcside='right', dstside='left')
    d.edge('cfg', 'norm', '', color='#4B6E9C', srcside='bottom', dstside='left')
    d.edge('ui', 'norm', '', color='#4B6E9C', srcside='bottom', dstside='right')
    d.edge('d1', 'norm', '', color='#4B6E9C', srcside='bottom', dstside='top')
    d.edge('norm', 'bad', 'invalid', color='#B85450', srcside='right', dstside='left')
    d.edge('norm', 'd2', '', color='#4B6E9C', srcside='bottom', dstside='top')
    d.edge('d2', 'fb', 'yes', color='#B85450', srcside='right', dstside='left')
    d.edge('fb', 'disp', '', color='#B85450', dashed=True, srcside='bottom', dstside='right')
    d.edge('d2', 'disp', 'no', color='#4B6E9C', srcside='bottom', dstside='top')
    return d


# ══════════════════════════════════════════════════ 2.8 ERD
def f28():
    d = Diagram('fig_2_8_erd',
                'Hình 2.8 – Sơ đồ quan hệ thực thể của hệ thống',
                1340, 1010,
                subtitle='Entity-relationship diagram of the SQLAlchemy models in models.py '
                         '(SQLite, created by db.create_all())')

    d.table('users', 70, 110, 330, 'users', [
        ('PK  id : Integer', 'PK'),
        ('username : String(80)', 'UNIQUE'),
        ('email : String(120)', 'UNIQUE'),
        ('password_hash : String(256)', ''),
        ('role : String(20) = "user"', "'admin'|'user'"),
        ('is_active : Boolean = True', ''),
        ('created_at : DateTime (UTC)', ''),
    ], 'api')

    d.table('documents', 500, 110, 360, 'documents', [
        ('PK  id : Integer', 'PK'),
        ('FK  user_id → users.id', 'NOT NULL, idx'),
        ('filename : String(255)', 'display name'),
        ('file_id : String(36)', 'UNIQUE (uuid4)'),
        ('file_type : String(10)', 'suffix'),
        ('file_size : BigInteger', ''),
        ('page_count : Integer = 1', ''),
        ('upload_date : DateTime (UTC)', ''),
        ('status : String(20)', 'uploaded|ocr_done'),
    ], 'svc')

    d.table('artifacts', 950, 110, 330, 'document_artifacts', [
        ('PK  id : Integer', 'PK'),
        ('FK  document_id → documents.id', 'ON DELETE CASCADE'),
        ('kind : String(20)', 'see legend'),
        ('content : Text', ''),
        ('meta : String(200)', 'nullable'),
        ('created_at : DateTime', ''),
        ('updated_at : DateTime', 'onupdate'),
        ('UNIQUE (document_id, kind)', 'uq_artifact_doc_kind'),
    ], 'eng')

    d.table('logs', 70, 420, 330, 'activity_logs', [
        ('PK  id : Integer', 'PK'),
        ('FK  user_id → users.id', 'ON DELETE SET NULL'),
        ('action : String(50)', 'NOT NULL'),
        ('detail : String(500)', 'nullable'),
        ('ip_address : String(45)', 'request.remote_addr'),
        ('created_at : DateTime (UTC)', ''),
    ], 'data')

    d.edge('users', 'documents', '1 ── 0..*  owns', color='#3F61A8', srcside='right', dstside='left')
    d.edge('documents', 'artifacts', '1 ── 0..*  derives\n(cascade delete)', color='#0E8088',
           srcside='right', dstside='left')
    d.edge('users', 'logs', '1 ── 0..*  performs\n(user_id nullable)', color='#5A5A5A',
           srcside='bottom', dstside='top')

    d.table('kinds', 500, 420, 360, 'document_artifacts.kind values written by the code', [
        ("text  —  TXT / DOCX / PDF text (/api/read-text)", ''),
        ("ocr  —  flattened OCR plain text", ''),
        ("ocr_layout  —  boxes, confidence, page timing", 'all engines'),
        ("ocr_json  —  structured per-page regions", 'all engines'),
        ("ocr_markdown  —  Markdown reconstruction", 'GLM / Modern'),
        ("ocr_html  —  HTML reconstruction", 'Modern'),
        ("ocr_tables  —  detected tables as HTML", 'GLM / Modern'),
        ("ocr_blocks  —  layout blocks (label/bbox/order)", 'GLM / Modern'),
        ("ocr_images  —  base64 overlays + cropped regions", 'all engines'),
        ("corrected_json / corrected_md / corrected_meta", 'correction_bp'),
    ], 'note', rowh=20)

    d.container('legacy', 950, 420, 330, 300,
                'Declared but unused in this build', 'ext', header=32)
    for i, (nid, lab) in enumerate([
            ('t1', 'chat_conversations'), ('t2', 'chat_messages'),
            ('t3', 'agent_conversations'), ('t4', 'agent_messages'),
            ('t5', 'agent_artifacts')]):
        d.node(nid, 972, 466 + i * 48, 286, 38, lab, 'ext', parent='legacy', fontsize=10.5)

    d.node('n1', 70, 762, 1210, 96,
           'Fidelity note — the report text suggests the entities User, Role, Document, DocumentPage, OCRJob, '
           'OCRResult, OCRConfiguration, ActivityLog and ErrorLog. The implementation contains only the four '
           'tables drawn above: there is no Role table (role is a string column on users), no DocumentPage, '
           'OCRJob, OCRResult, OCRConfiguration or ErrorLog table. Per-page OCR output is stored as JSON inside '
           'document_artifacts, OCR engine settings live in environment variables read by config.py, and '
           'errors are recorded in the application log and in activity_logs.',
           'note', shape='note', fontsize=10)
    d.node('n2', 70, 878, 1210, 76,
           'The five tables on the right are defined in models.py and are therefore created by db.create_all(), '
           'but no route in this build reads or writes them — the chat / RAG / agent blueprints were removed '
           '(see the comment in app.py::_persist_and_index). They are shown for completeness of the physical '
           'schema and must not be presented as active functionality.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 2.9 Navigation
def f29():
    d = Diagram('fig_2_9_navigation',
                'Hình 2.9 – Sơ đồ điều hướng chính của giao diện người dùng',
                1340, 980,
                subtitle='Reconstructed from the Flask routes and the hash router in static/app.js '
                         '(Router.register / Router.goto / Router._render)')

    d.node('login', 60, 250, 230, 74, 'Login page\nGET / POST  /login', 'ui', fontsize=11, bold=True)
    d.node('logout', 60, 700, 230, 64, 'Logout\nGET /logout → /login', 'ui', fontsize=10.5)

    d.container('spa', 330, 96, 640, 466,
                'Single-page application  —  GET /   (static/index.html)', 'ui', header=36)
    d.node('home', 356, 150, 250, 60, '#home\nHome (tool cards)', 'ui', parent='spa', fontsize=11, bold=True)
    d.node('ocr', 356, 250, 250, 64, '#ocr\nOCR workspace', 'ui', parent='spa', fontsize=11, bold=True)
    d.node('docs', 356, 360, 250, 64, '#documents\nDocument library', 'ui', parent='spa', fontsize=11, bold=True)
    d.node('tabs', 640, 250, 300, 64,
           'Result tabs — shown after Run OCR / OCR All\nMarkdown · Raw · Images · JSON\n'
           '(+ downloads .md .txt .json .docx)', 'ui', parent='spa', fontsize=9)
    d.node('deep', 640, 360, 300, 64, '#ocr/<file_id>  (deep link)\nreopens a document and restores\nits saved artifacts',
           'ui', parent='spa', fontsize=9.5)
    d.node('nav', 356, 470, 584, 64,
           'Persistent navigation bar\nHome · OCR · Documents · [Admin] · language · Sign out',
           'ui', parent='spa', fontsize=10)

    d.container('admin', 330, 700, 640, 220,
                'Admin console  —  server-rendered Jinja pages, role = "admin" only', 'api', header=36)
    d.node('adash', 356, 754, 280, 54, 'GET /admin/\nDashboard + recent activity', 'api', parent='admin', fontsize=10)
    d.node('alogs', 660, 754, 280, 54, 'GET /admin/logs\nActivity logs (filters)', 'api', parent='admin', fontsize=10)
    d.node('ausers', 356, 828, 280, 54, 'GET /admin/users\nUser management', 'api', parent='admin', fontsize=10)
    d.node('afiles', 660, 828, 280, 54, 'GET /admin/files\nAll documents', 'api', parent='admin', fontsize=10)

    d.node('corr', 1060, 250, 270, 100,
           'Correction page\nGET /correction\n(separate page; reachable by URL,\n"← Back to SmartDocs" link)',
           'corr', fontsize=10)
    d.node('f403', 1060, 754, 270, 74, '403 page\ntemplates/403.html\n(non-admin access)', 'err', fontsize=10)

    d.edge('login', 'home', 'successful login\n→ redirect to /', color='#3F61A8',
           srcside='right', dstside='left', waypoints=[(312, 287), (312, 180)])
    d.edge('home', 'ocr', '', color='#3F61A8', srcside='bottom', dstside='top')
    d.edge('home', 'docs', '', color='#3F61A8',
           srcside='left', dstside='left', waypoints=[(344, 180), (344, 392)])
    d.edge('ocr', 'tabs', '', color='#3F61A8', srcside='right', dstside='left')
    d.edge('docs', 'deep', '', color='#3F61A8', srcside='right', dstside='left')
    d.edge('nav', 'adash', 'Admin link — rendered only when role = "admin"', color='#9673A6',
           srcside='bottom', dstside='top', waypoints=[(648, 630), (496, 630)])
    d.edge('adash', 'ausers', '', color='#9673A6', arrow='none', srcside='bottom', dstside='top')
    d.edge('adash', 'alogs', '', color='#9673A6', arrow='none', srcside='right', dstside='left')
    d.edge('ausers', 'afiles', '', color='#9673A6', arrow='none', srcside='right', dstside='left')
    d.edge('admin', 'home', '"← Ứng dụng"  →  /#home', color='#9673A6', dashed=True,
           srcside='left', dstside='top', waypoints=[(306, 810), (306, 126), (481, 126)])
    d.edge('nav', 'logout', 'Sign out', color='#3F61A8', dashed=True,
           srcside='left', dstside='right', waypoints=[(322, 502), (322, 732)])
    d.edge('corr', 'spa', 'URL only', color='#9673A6', arrow='both',
           srcside='left', dstside='right')
    d.edge('f403', 'admin', 'abort(403)', color='#B85450', dashed=True,
           srcside='left', dstside='right')

    d.node('n1', 60, 900, 1230, 56,
           'The /correction page is reachable by URL only — no link to it exists in the SPA navigation bar '
           '(static/index.html). Browser Back / Forward work natively because location.hash is the single source '
           'of SPA view state; the only SPA deep link is #ocr/<file_id>.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 2.10 Data protection layers
def f210():
    d = Diagram('fig_2_10_data_protection',
                'Hình 2.10 – Mô hình các lớp bảo vệ dữ liệu của hệ thống',
                1320, 1040,
                subtitle='Defence-in-depth layers — only mechanisms that are actually implemented '
                         'are shown; each layer names its source location')

    layers = [
        ('L1', 'Layer 1 · Transport & session hardening',
         'SECRET_KEY (env or secrets.token_hex(32)) · SESSION_COOKIE_HTTPONLY = True · SAMESITE = "Lax" · '
         'SESSION_COOKIE_SECURE gated on cfg.SESSION_COOKIE_SECURE · identical flags for the remember-me cookie   '
         '[app.py, config.py]', 'ui'),
        ('L2', 'Layer 2 · Authentication',
         'Flask-Login session · werkzeug generate_password_hash / check_password_hash · is_active check on login · '
         '@login_required on every page and API route · unauthorized_handler returns 401 JSON for /api/* and '
         'redirects browsers to /login   [auth.py, app.py, models.py]', 'api'),
        ('L3', 'Layer 3 · Authorization (role based)',
         'users.role ∈ {"admin", "user"} · admin_required decorators in auth.py and admin_bp.py · abort(403) with a '
         'dedicated 403 template · admins may not disable or delete their own account   [auth.py, admin_bp.py]', 'svc'),
        ('L4', 'Layer 4 · Document access control',
         '_resolve_owned_file() resolves file_id through the Document table and rejects foreign documents (403) or '
         'unknown ids (404); the same owner-or-admin check is repeated on every /api/documents/<id> endpoint and on '
         'the correction endpoints   [app.py, correction_bp.py]', 'eng'),
        ('L5', 'Layer 5 · Upload validation & path safety',
         'MAX_CONTENT_LENGTH (MAX_UPLOAD_MB, default 50 MB) with a JSON 413 handler · _safe_basename() strips '
         'directory parts and control characters while preserving Vietnamese Unicode · extension allowlist · the '
         'on-disk name is always a server-generated UUID, never user input · lookups never glob the raw file_id, so '
         '"../" strings match no document   [app.py]', 'proc'),
        ('L6', 'Layer 6 · Process & model isolation',
         'The GLM-OCR engine runs as a separate subprocess in its own virtual environment; the child environment is '
         'stripped of HF_HOME / HF_HUB_CACHE / TRANSFORMERS_CACHE and forced to HF_HUB_OFFLINE=1 · execution is '
         'bounded by GLM_TIMEOUT and a TCP health check · failures return a structured error instead of raising   '
         '[glm_adapter.py, config.py]', 'corr'),
        ('L7', 'Layer 7 · Output sanitization & data locality',
         'sanitizeHtml() removes script/style/iframe/object/embed/link/meta and on* / javascript: attributes before '
         'rendering engine-produced HTML · markdown_normalize repairs unmatched $$ delimiters · OFFLINE=1 blocks '
         'model downloads and mlx_config.yaml disables the cloud MaaS path, so document content never leaves the host   '
         '[static/app.js, services/markdown_normalize.py, mlx_config.yaml]', 'data'),
        ('L8', 'Layer 8 · Auditing',
         'activity_logs records (user_id, action, detail, ip_address, created_at) for login, logout, upload, ocr, '
         'delete_doc, vi_correct and every admin action · log_activity() never raises · the admin log viewer filters '
         'by action, user and free text   [models.py, app.py, admin_bp.py]', 'note'),
    ]
    y = 92
    for lid, title, body, key in layers:
        d.node(lid, 60, y, 1200, 84, title + '\n' + body, key, shape='round', fontsize=10)
        y += 96

    d.node('core', 400, 872, 520, 72,
           'PROTECTED ASSETS\nUploaded originals (uploads/) · OCR and correction artifacts '
           '(document_artifacts) · user accounts (users) · audit trail (activity_logs)',
           'err', shape='round', fontsize=11, bold=True)
    for lid, *_ in layers:
        pass
    d.edge('L8', 'core', '', color='#B85450', srcside='bottom', dstside='top')

    d.node('n1', 60, 960, 1200, 62,
           'Not implemented in this repository, and therefore deliberately absent from the figure: TLS termination, '
           'encryption at rest, CSRF tokens, rate limiting, database backup/restore automation, and any external '
           'identity provider. SESSION_COOKIE_SECURE only marks the cookie — TLS itself must be provided by the '
           'deployment environment.',
           'todo', shape='note', fontsize=10)
    return d


if __name__ == '__main__':
    for fn in (f21, f22, f23, f24, f25, f26, f27, f28, f29, f210):
        write(fn())
