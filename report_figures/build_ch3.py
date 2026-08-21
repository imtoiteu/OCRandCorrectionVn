#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hình chương 3 (3.1, 3.2, 3.6, 3.7, 3.8, 3.9).

Các hình 3.3, 3.4, 3.5, 3.10 và 3.11 là ảnh chụp giao diện, được xử lý trong
MANUAL_COMPLETION.md — không dựng giả bất kỳ màn hình nào ở đây.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram_engine import Diagram, write, set_out, row_x

set_out(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chapter3'))


# ══════════════════════════════════════════════════ 3.1 Cấu trúc mã nguồn
def f31():
    d = Diagram('fig_3_1_development_structure',
                'Hình 3.1 – Cấu trúc môi trường phát triển và các thành phần mã nguồn của hệ thống',
                1420, 1180,
                subtitle='Bố cục thư mục và các môi trường Python của OCRandCorrectionVn '
                         '(đối chiếu trực tiếp với cây thư mục làm việc)')

    d.container('repo', 40, 92, 880, 990,
                'OCRandCorrectionVn/   —   kho mã nguồn git', 'api', header=40)

    X, W = 62, 836
    rows = [
        (146, 34, 'glm-ocr-ui/     —     ứng dụng web SmartDocs (Flask, cổng 5001)', 'api', True, 11.5),
        (186, 54, 'app.py · auth.py · admin_bp.py · correction_bp.py · config.py · models.py\n'
                  'điểm khởi động, các blueprint, đối tượng cấu hình, mô hình SQLAlchemy', 'ui', False, 10),
        (246, 52, 'services/     ocr_service · smart_ocr_service · text_service · layout_service\n'
                  'geometry_service · markdown_normalize · activity_registry · cpu_threads', 'svc', False, 10),
        (304, 52, 'services/ocr_engines/     base · router · paddle_adapter · paddle_modern_adapter\n'
                  'vietocr_adapter · glm_adapter · glm_vietocr_adapter', 'eng', False, 10),
        (362, 52, 'services/vi_correction/     classification · masking · segmentation · pipeline · validation\n'
                  'renderers · service · providers/{protonx, bmd1905, mrlasdt, mock}', 'corr', False, 10),
        (420, 44, 'static/     index.html · app.js · ocr-canvas.js · correction.html · correction.js · i18n.js\n'
                  'style.css · vendor/{katex, marked}   (không cần bước build frontend)', 'ui', False, 10),
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
        (696, 40, 'sinh ra lúc chạy (không đưa vào git):     uploads/     paddleocr.db     models/', 'data', False, 10.5),
        (752, 34, 'glm-ocr-server/     —     bộ SDK GLM-OCR và máy chủ mô hình MLX', 'proc', True, 11.5),
        (792, 52, 'glmocr/     cli · api · config · server · pipeline/ (pipeline, _workers, _state, _unit_tracker)\n'
                  'layout/ (PP-DocLayoutV3) · dataloader/ · ocr_client · maas_client · postprocess/ · utils/ · tests/',
         'proc', False, 9.5),
        (850, 38, 'mlx_config.yaml (chế độ self-hosted → :8080) · glmocr/config.yaml · examples/ · skills/ · ui/ · resources/',
         'proc', False, 9.5),
        (894, 38, 'apps/backend (FastAPI) · apps/frontend (React + Vite) · Dockerfile     —     bản demo GLM-OCR gốc, '
                  'SmartDocs KHÔNG sử dụng', 'ext', False, 9.5),
        (938, 34, 'models/     protonx-legal-tc · distilled-protonx-legal-tc · nano-protonx-legal-tc · vietocr/config.yml',
         'corr', True, 10.5),
        (978, 34, 'vi-correction-prototype/     bản thử nghiệm độc lập: vicorrect/ · scripts/bench_spans.py · tests/',
         'svc', True, 10.5),
        (1018, 34, 'README.md     ·     RUN_MACOS.md   (hướng dẫn cài đặt và chạy)', 'ext', True, 10.5),
    ]
    for i, (y, h, lab, key, bold, fs) in enumerate(rows):
        d.node('r%d' % i, X, y, W, h, lab, key, parent='repo', fontsize=fs, bold=bold)

    d.container('env', 950, 92, 430, 470, 'Môi trường Python  (do người phát triển tạo)', 'proc', header=40)
    d.node('v1', 972, 148, 386, 120,
           'glm-ocr-ui/.venv          Python 3.10\nflask · flask-login · flask-sqlalchemy\n'
           'paddleocr 3.7.x · paddlex[ocr-core] · paddlepaddle\nvietocr · torch · transformers · pypdfium2\n'
           'Pillow · layoutparser · python-docx · python-dotenv',
           'api', parent='env', fontsize=9.5)
    d.node('v2', 972, 282, 386, 78,
           'glm-ocr-server/.venv-sdk          Python 3.10\npip install -e ".[selfhosted]"\n'
           'cung cấp lệnh glmocr mà GLMOCREngine gọi tới',
           'proc', parent='env', fontsize=9.5)
    d.node('v3', 972, 374, 386, 78,
           'glm-ocr-server/.venv-mlx          Python 3.10\npip install -U mlx-vlm\n'
           'chạy  python -m mlx_vlm.server --port 8080',
           'proc', parent='env', fontsize=9.5)
    d.node('v4', 972, 466, 386, 74,
           'Cả ba môi trường đều không được đưa vào git;\ntất cả được tạo theo RUN_MACOS.md (§3, §6, §7). '
           'GLM_ROOT / GLM_SDK_PYTHON / GLM_MLX_PYTHON trong .env\nchỉ cho glm-ocr-ui biết vị trí hai môi trường kia.',
           'ext', parent='env', fontsize=9)

    d.node('mdl', 950, 590, 430, 140,
           'Tệp mô hình được phân giải lúc chạy\n\n'
           '• MODEL_DIR/huggingface  —  HF_HOME / HF_HUB_CACHE (OFFLINE=1 chặn tải về)\n'
           '• bộ nhớ đệm mô hình PaddleOCR / PaddleX  —  tải về ở lần OCR đầu tiên\n'
           '• MODEL_DIR/vietocr/<config>.pth  —  trọng số VietOCR\n'
           '• bộ nhớ đệm HF mặc định  —  PP-DocLayoutV3 và mlx-community/GLM-OCR-bf16\n'
           '  (tiến trình con GLM cố ý chạy không kèm các biến HF_* đã đổi hướng)',
           'data', fontsize=9.5)

    d.node('todo', 950, 756, 430, 232,
           'CẦN HOÀN THIỆN THỦ CÔNG\n\n'
           'Phần thuyết minh mô tả Hình 3.1 gồm hai khối là SmartDocs-Agent-WebApp và '
           'SmartDocs-Agent-DesktopApp (Tauri/Rust, giao diện web nhúng, Python sidecar và ba chế độ '
           'kết nối backend).\n\n'
           'Kho mã nguồn này không có mã của ứng dụng desktop. Tìm trên toàn kho các từ khóa '
           '"tauri", "sidecar", "Bundled Core", "Remote Server" và cổng 5002 đều không ra mã ứng dụng, '
           'cũng không có thư mục src-tauri/, tệp Cargo.toml hay package.json của một vỏ desktop.\n\n'
           'Chỉ khối WebApp ở trên là dựng được từ mã nguồn. Khối DesktopApp phải bổ sung thủ công, '
           'hoặc thu hẹp chú thích hình lại còn WebApp.',
           'todo', shape='note', fontsize=9.5)

    d.node('n1', 40, 1096, 1340, 60,
           'Ghi chú khi đọc — README.md và docs/ trong glm-ocr-ui mô tả một sản phẩm lớn hơn ("SmartDocs-Agent" '
           'với trò chuyện RAG, dịch, tóm tắt, tác tử LLM, gói agent/). Các thư mục đó không có trong kho mã nguồn '
           'này; requirements.txt vẫn còn liệt kê thư viện của chúng. Hình chỉ thể hiện các tệp thực sự tồn tại '
           'trong cây thư mục làm việc.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 3.2 Mô-đun backend và luồng API
def f32():
    d = Diagram('fig_3_2_backend_modules',
                'Hình 3.2 – Cấu trúc các mô-đun backend và luồng gọi API của hệ thống',
                1420, 1210,
                subtitle='Toàn bộ các tuyến dưới đây được đọc trực tiếp từ app.py, auth.py, admin_bp.py '
                         'và correction_bp.py')

    d.container('cli', 40, 92, 1340, 104, 'Phía gọi  (HTTP)', 'ui', header=32)
    d.node('c1', 62, 130, 420, 52, 'SPA SmartDocs — static/index.html + app.js\nfetch() JSON + tải tệp multipart',
           'ui', parent='cli', fontsize=10)
    d.node('c2', 502, 130, 400, 52, 'Trang hiệu chỉnh — static/correction.html\n+ correction.js', 'corr',
           parent='cli', fontsize=10)
    d.node('c3', 922, 130, 436, 52, 'Trang quản trị và biểu mẫu đăng nhập (dựng phía máy chủ)\n'
                                    'templates/admin/*.html · login.html',
           'ui', parent='cli', fontsize=10)

    d.node('cfg', 40, 236, 300, 104,
           'config.py\nđối tượng cfg đọc lúc nạp mô-đun:\nHOST · PORT · DB_PATH · UPLOAD_DIR\nMODEL_DIR · OFFLINE · DEVICE\n'
           'OCR_ENGINE · GLM_* · VI_CORRECTION_*',
           'ext', fontsize=9.5)
    d.node('app', 400, 236, 620, 104,
           'app.py   —   đối tượng ứng dụng Flask\n'
           'SECRET_KEY · MAX_CONTENT_LENGTH · cờ cookie phiên · LoginManager + user_loader\n'
           'unauthorized_handler (401 JSON / chuyển hướng) · RequestEntityTooLarge → 413 · after_request no-cache\n'
           'register_blueprint(auth_bp, admin_bp, correction_bp) · bộ lọc Jinja vn_time',
           'api', fontsize=10, bold=True)
    d.node('mdl', 1080, 232, 300, 112,
           'models.py\ndb (SQLAlchemy) · User · Document\nDocumentArtifact · ActivityLog\n'
           'log_activity() · save_artifact() · seed_admin()\nINSERT / SELECT / DELETE',
           'data', fontsize=9.5)

    d.table('t_core', 40, 386, 330, 'Tuyến chính  (app.py)', [
        ('GET     /', 'vỏ SPA'),
        ('POST   /api/upload', 'tiếp nhận'),
        ('POST   /api/read-text', 'văn bản'),
        ('POST   /api/ocr/page', 'OCR'),
        ('POST   /api/ocr/all', 'OCR'),
        ('POST   /api/ocr/reconstruct-region', 'bố cục'),
        ('GET     /api/documents', 'thư viện'),
        ('GET     /api/documents/<id>/text', 'kết xuất'),
        ('GET     /api/documents/<id>/ocr-images', 'kết xuất'),
        ('DELETE /api/documents/<id>', 'thư viện'),
        ('GET     /api/documents/<id>/download', 'thư viện'),
        ('POST   /api/ocr/export-docx', 'pandoc'),
    ], 'api')

    d.table('t_auth', 400, 386, 300, 'auth_bp  (auth.py)', [
        ('GET / POST   /login', 'phiên'),
        ('GET     /logout', 'phiên'),
        ('GET     /api/auth/me', 'định danh'),
        ('POST   /api/set-lang', 'ngôn ngữ'),
        ('GET     /api/admin/users', 'chỉ quản trị'),
        ('app_errorhandler(403)', '403.html'),
    ], 'svc')

    d.table('t_admin', 730, 386, 320, 'admin_bp  (url_prefix = /admin)', [
        ('GET     /admin/', 'tổng quan'),
        ('GET     /admin/users', 'danh sách'),
        ('POST   /admin/users/create', 'tạo'),
        ('POST   /admin/users/<uid>/edit', 'sửa'),
        ('POST   /admin/users/<uid>/reset-password', 'mật khẩu'),
        ('POST   /admin/users/<uid>/toggle', 'khóa/mở'),
        ('POST   /admin/users/<uid>/delete', 'xóa'),
        ('GET     /admin/logs', 'bộ lọc'),
        ('GET     /admin/files', 'bộ lọc'),
    ], 'corr')

    d.table('t_corr', 1080, 386, 300, 'correction_bp', [
        ('GET     /correction', 'trang'),
        ('GET     /api/correction/config', 'mô hình'),
        ('GET     /api/correction/documents', 'chọn tài liệu'),
        ('POST   /api/correction/run', 'chạy mô hình'),
        ('POST   /api/correction/save', 'lưu kết xuất'),
        ('GET     /api/correction/result/<doc_id>', 'mở lại'),
    ], 'eng')

    d.container('svc', 40, 720, 1340, 178, 'Tầng dịch vụ  (services/)', 'svc', header=34)
    d.node('s1', 62, 768, 330, 108,
           'smart_ocr_service.run_ocr_pipeline()\n→ ocr_service.run_ocr()\n\n'
           'activity_registry.track("ocr")\n_normalize_block() · vẽ ảnh phủ vùng',
           'svc', parent='svc', fontsize=9.5)
    d.node('s2', 412, 768, 300, 108,
           'services/ocr_engines/router.py\nnormalize_engine_name() · get_engine()\n\n'
           'năm bộ thích nghi OCREngine\n(xem Hình 3.7)',
           'eng', parent='svc', fontsize=9.5)
    d.node('s3', 732, 768, 300, 108,
           'layout_service / geometry_service\ndựng lại thứ tự đọc\n\n'
           'text_service.read_file()\nmarkdown_normalize.repair_…()',
           'svc', parent='svc', fontsize=9.5)
    d.node('s4', 1052, 768, 306, 108,
           'vi_correction.run_correction()\nphân loại → che token → tách đơn vị\n→ provider.correct_batch()\n'
           '→ khôi phục → kiểm tra → kết xuất',
           'corr', parent='svc', fontsize=9.5)

    d.container('data', 40, 928, 1340, 130, 'Dữ liệu và tài nguyên bên ngoài', 'data', header=34)
    d.node('d1', 62, 972, 320, 66, 'SQLite  paddleocr.db\nusers · documents\ndocument_artifacts · activity_logs',
           'data', parent='data', shape='cyl', fontsize=9.5)
    d.node('d2', 402, 972, 300, 66, 'uploads/\n{uuid4}{suffix}\n+ tệp .png tạm của từng trang', 'data',
           parent='data', fontsize=9.5)
    d.node('d3', 722, 972, 300, 66, 'models/ · bộ nhớ đệm HF\nbộ nhớ đệm PaddleX · trọng số VietOCR', 'data',
           parent='data', fontsize=9.5)
    d.node('d4', 1042, 972, 316, 66, 'Tiến trình bên ngoài\nglmocr CLI (.venv-sdk)  ·  MLX :8080\npandoc',
           'proc', parent='data', fontsize=9.5)

    d.edge('c1', 'app', 'JSON / multipart', color='#3F61A8', srcside='bottom', dstside='top',
           waypoints=[(272, 214), (560, 214)])
    d.edge('c2', 'app', '', color='#9673A6', srcside='bottom', dstside='top',
           waypoints=[(702, 214), (710, 214)])
    d.edge('c3', 'app', 'POST biểu mẫu / HTML', color='#3F61A8', srcside='bottom', dstside='top',
           waypoints=[(1140, 214), (860, 214)])
    d.edge('cfg', 'app', 'cấu hình', color='#999999', dashed=True,
           srcside='right', dstside='left')
    d.edge('app', 'mdl', 'ORM', color='#5A5A5A', srcside='right', dstside='left')

    for tid, cx in (('t_core', 205), ('t_auth', 550), ('t_admin', 890), ('t_corr', 1230)):
        d.edge('app', tid, '', color='#3F61A8', srcside='bottom', dstside='top',
               waypoints=[(710, 362), (cx, 362)])
    d.edge('t_core', 's1', 'tuyến OCR', color='#82B366', srcside='bottom', dstside='top')
    d.edge('t_core', 's3', 'tuyến văn bản / bố cục', color='#82B366', srcside='right', dstside='top',
           waypoints=[(700, 700), (882, 700)])
    d.edge('t_corr', 's4', '', color='#9673A6', srcside='bottom', dstside='top')
    d.edge('s1', 's2', '', color='#0E8088', srcside='right', dstside='left')
    d.edge('s2', 's3', '', color='#82B366', srcside='right', dstside='left')
    d.edge('s1', 'd2', '', color='#5A5A5A', srcside='bottom', dstside='top',
           waypoints=[(222, 910), (552, 910)])
    d.edge('s2', 'd4', '', color='#D79B00', srcside='bottom', dstside='top',
           waypoints=[(562, 912), (1200, 912)])
    d.edge('mdl', 'data', '', color='#5A5A5A',
           srcside='right', dstside='right', waypoints=[(1404, 288), (1404, 993)])

    d.node('n1', 40, 1078, 1340, 76,
           'Nguyên tắc gọi API thể hiện rõ trong mã: trình duyệt không bao giờ chạm trực tiếp vào mô hình hay cơ sở '
           'dữ liệu. Mọi yêu cầu đều vào Flask, được @login_required kiểm tra (và @admin_required với /admin), được '
           'phân giải về một Document thuộc quyền sở hữu, rồi mới xuống tầng dịch vụ; việc ghi dữ liệu chỉ diễn ra '
           'qua models.py. Bản thân các tuyến OCR không nạp thư viện OCR nào — chúng gọi '
           'smart_ocr_service → ocr_service → router → bộ thích nghi.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 3.6 Tiếp nhận và chuẩn hóa
def f36():
    d = Diagram('fig_3_6_intake_normalization',
                'Hình 3.6 – Quy trình tiếp nhận và chuẩn hóa tài liệu đã được hiện thực hóa',
                1400, 1160,
                subtitle='Đường tiếp nhận thực tế — app.py::upload(), _resolve_owned_file(), ocr_page() / ocr_all(), '
                         'ocr_service.py, text_service.py')

    d.container('p1', 40, 92, 660, 640, 'Giai đoạn A — tải lên    POST /api/upload', 'api', header=34)
    A = [
        ('a1', 138, 44, 'Người dùng chọn hoặc kéo thả tệp trên SPA\n(accept = .jpg .jpeg .png .webp .pdf .txt .docx)', 'flow'),
        ('a2', 198, 40, 'Flask từ chối nếu kích thước vượt\nMAX_CONTENT_LENGTH → 413 JSON', 'dec'),
        ('a3', 254, 40, '@login_required  ·  request.files.get("file")\nthiếu tệp → 400', 'dec'),
        ('a4', 310, 44, '_safe_basename(): bỏ thành phần thư mục, loại ký tự\nđiều khiển, giữ Unicode, giới hạn 255 ký tự', 'flow'),
        ('a5', 370, 40, 'suffix = Path(name).suffix.lower()\nsuffix ∈ ALL_EXTS ?   nếu không → 400', 'dec'),
        ('a6', 426, 44, 'fid = uuid4()   ·   tệp được lưu thành\nUPLOAD_DIR/{fid}{suffix}  (tên không lấy từ người dùng)', 'flow'),
        ('a7', 486, 44, 'page_count = pdf_page_count() với PDF, còn lại = 1\nfile_size = path.stat().st_size', 'flow'),
        ('a8', 546, 44, 'INSERT Document(user_id, filename, file_id, file_type,\nfile_size, page_count, status="uploaded")', 'data'),
        ('a9', 606, 36, 'log_activity("upload", "<tên tệp> (<suffix>, <dung lượng>B)")', 'data'),
        ('a10', 654, 44, '200 {file_id, filename, size, suffix, doc_id,\nis_pdf, is_image, page_count}', 'flow'),
    ]
    for nid, y, h, lab, key in A:
        d.node(nid, 62, y, 616, h, lab, key, parent='p1', fontsize=9.5)
    for x, y in zip([a[0] for a in A], [a[0] for a in A][1:]):
        d.edge(x, y, '', color='#4B6E9C', srcside='bottom', dstside='top')

    d.container('p2', 740, 92, 640, 640,
                'Giai đoạn B — chuẩn hóa trước khi OCR    POST /api/ocr/page  ·  /api/ocr/all', 'eng', header=34)
    B = [
        ('b1', 138, 44, '_resolve_owned_file(file_id)\ntra cứu Document → 404 · quyền sở hữu → 403', 'dec'),
        ('b2', 198, 44, 'dò UPLOAD_DIR/{uuid đã lưu}.*\nkhông bao giờ dò bằng file_id thô → chống vượt thư mục', 'flow'),
        ('b3', 258, 40, 'riêng /api/ocr/all: từ chối mọi thứ không phải\nảnh hoặc PDF → 400', 'dec'),
        ('b4', 314, 40, 'suffix == ".pdf" ?', 'dec'),
        ('b5', 370, 56, 'PDF: pypdfium2 kết xuất trang N ở scale = 2.0\n→ ảnh PIL → NamedTemporaryFile(".png") trong\nUPLOAD_DIR (xóa trong khối finally)', 'flow'),
        ('b6', 442, 48, 'Ảnh: PIL.Image.open(path) trực tiếp\n(không đổi kích thước, không nhị phân hóa, không nắn nghiêng)', 'flow'),
        ('b7', 506, 44, 'preview_only = true → trả page_image_b64 +\nimg_width / img_height, results = [] (không OCR)', 'flow'),
        ('b8', 566, 44, '_resolve_selected_engine(): tham số engine →\nbí danh → cfg.OCR_ENGINE; vietocr + .pdf → paddleocr', 'eng'),
        ('b9', 626, 40, 'smart_ocr_service.run_ocr_pipeline(image_path,\nengine_name)  →  bộ định tuyến OCR (Hình 3.7)', 'eng'),
        ('b10', 678, 36, 'page_image_b64 được gắn vào phản hồi để vẽ lớp phủ trên canvas', 'flow'),
    ]
    for nid, y, h, lab, key in B:
        d.node(nid, 762, y, 596, h, lab, key, parent='p2', fontsize=9.5)
    for x, y in zip([b[0] for b in B], [b[0] for b in B][1:]):
        d.edge(x, y, '', color='#0E8088', srcside='bottom', dstside='top')

    d.edge('a10', 'b1', 'file_id', color='#3F61A8',
           srcside='right', dstside='left', waypoints=[(716, 676), (716, 160)])

    d.container('p3', 40, 764, 1340, 190,
                'Đường tiếp nhận thay thế cho tài liệu văn bản    POST /api/read-text', 'svc', header=34)
    d.node('t1', 62, 812, 400, 56, 'text_service.read_file(path)\nphân nhánh theo phần mở rộng', 'svc',
           parent='p3', fontsize=10)
    d.node('t2', 500, 806, 250, 62, '.txt\nopen(errors="replace")', 'svc', parent='p3', fontsize=10)
    d.node('t3', 500, 878, 250, 62, '.docx\nđoạn văn qua python-docx', 'svc', parent='p3', fontsize=10)
    d.node('t4', 790, 842, 250, 62, '.pdf\nlớp văn bản pypdfium2\n(văn bản nhúng, không OCR)', 'svc', parent='p3', fontsize=10)
    d.node('t5', 1078, 842, 280, 62, '_persist_and_index(file_id, "text", text)\n→ save_artifact(kind = "text")',
           'data', parent='p3', fontsize=10)
    d.edge('t1', 't2', '', color='#82B366', srcside='right', dstside='left')
    d.edge('t1', 't3', '', color='#82B366', srcside='right', dstside='left')
    d.edge('t2', 't4', '', color='#82B366', srcside='right', dstside='left')
    d.edge('t4', 't5', '', color='#82B366', srcside='right', dstside='left')

    d.node('err', 40, 984, 660, 108,
           'Các nhánh lỗi đã hiện thực hóa\n'
           '• tệp quá lớn → 413 {"error": "File too large (max N MB)"}\n'
           '• không có tệp / phần mở rộng không hỗ trợ → 400\n'
           '• file_id không tồn tại → 404;  tài liệu của người khác → 403 (quản trị viên là ngoại lệ)\n'
           '• có bản ghi nhưng thiếu tệp trên đĩa → 404 "File missing from disk"\n'
           '• mọi ngoại lệ bên trong lời gọi OCR → 500 và vết lỗi được ghi vào nhật ký',
           'err', fontsize=9.5)
    d.node('lim', 740, 984, 640, 108,
           'Phạm vi của "chuẩn hóa" trong phiên bản này\n'
           'Ứng dụng chỉ chuẩn bị ảnh ở mức kết xuất trang (pypdfium2, scale = 2.0) và chuyển đổi định dạng '
           'sang PNG/JPEG. Phân loại hướng tài liệu và nắn phẳng UVDoc chỉ xảy ra bên trong pipeline '
           'PaddleOCR Modern (PPStructureV3(use_doc_orientation_classify=True, use_doc_unwarping=True)). '
           'Mã ứng dụng không có bước nắn nghiêng, khử nhiễu, nhị phân hóa hay chuẩn hóa DPI.',
           'note', shape='note', fontsize=9.5)

    d.node('n1', 40, 1108, 1340, 34,
           'Bộ nhớ đệm kết quả: _run_page_ocr() lưu kết quả mỗi trang vào một từ điển trong bộ nhớ, khóa theo '
           '(sha-256 của tệp, số trang, kích thước + thời điểm sửa, tên công cụ), nên chạy lại đúng trang đó với '
           'cùng công cụ sẽ không lặp lại quá trình suy luận.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 3.7 Điều phối công cụ OCR
def f37():
    d = Diagram('fig_3_7_ocr_orchestration',
                'Hình 3.7 – Cơ chế tích hợp và điều phối các công cụ OCR',
                1440, 1080,
                subtitle='services/ocr_engines/ — một giao diện trừu tượng, năm bộ thích nghi, '
                         'một hợp đồng kết quả chung')

    d.node('req', 40, 110, 300, 150,
           'Yêu cầu từ dịch vụ OCR\n\nsmart_ocr_service.run_ocr_pipeline(\n     image_path,\n'
           '     engine_name)\n\n→ ocr_service.run_ocr()\n     activity_registry.track("ocr")',
           'svc', fontsize=10)

    d.node('router', 420, 128, 560, 114,
           'BỘ ĐỊNH TUYẾN OCR   services/ocr_engines/router.py\n\n'
           '_ENGINES = {paddleocr, vietocr, paddleocr_modern, glmocr, glm_vietocr}\n'
           '_ALIASES  (paddle, auto, modern, ppstructure, glm, glm_ocr, glm_layout_vietocr)\n'
           'normalize_engine_name() → get_engine() → engine.run(image_path)',
           'eng', fontsize=10.5, bold=True)

    d.node('abc', 1060, 128, 340, 114,
           'Giao diện trừu tượng\nservices/ocr_engines/base.py\n\n'
           'class OCREngine(ABC):\n     engine_name: str\n     def run(self, image_path) -> dict',
           'api', fontsize=10)

    ADP = [
        ('ad1', 40, 'Bộ thích nghi PaddleOCR Legacy\npaddle_adapter.py · engine_name = "paddleocr"\n\n'
                    'khởi tạo trễ PaddleOCR(ocr_version="PP-OCRv5",\n use_doc_orientation_classify=False,\n use_doc_unwarping=False)\n'
                    'chạy trong tiến trình · trả rec_texts / rec_scores / det_polys', 'eng'),
        ('ad2', 390, 'Bộ thích nghi PaddleOCR Modern\npaddle_modern_adapter.py · "paddleocr_modern"\n\n'
                     'khởi tạo trễ PPStructureV3(use_doc_orientation_classify=True,\n use_doc_unwarping=True,\n'
                     ' text_detection_model_name="PP-OCRv6_medium_det",\n text_recognition_model_name="PP-OCRv6_medium_rec")\n'
                     'bổ sung markdown · html · tables_html · layout_blocks', 'eng'),
        ('ad3', 740, 'Bộ thích nghi VietOCR\nvietocr_adapter.py · engine_name = "vietocr"\n\n'
                     'PaddleOCR PP-OCRv5 đóng vai trò BỘ PHÁT HIỆN dòng;\nmỗi vùng cắt được nhận dạng bằng\n'
                     'vietocr Predictor (vgg_transformer, cfg.VIETOCR_DEVICE)\n'
                     'cấu hình lấy theo VIETOCR_CONFIG_PATH → MODEL_DIR → mặc định nội bộ', 'eng'),
        ('ad4', 1090, 'Bộ thích nghi GLM-OCR\nglm_adapter.py · engine_name = "glmocr"\n\n'
                      'chạy ngoài tiến trình — xem khung bên dưới\nlayout_native = True (không sắp lại theo hình học)\n'
                      'trả markdown · tables_html · layout_blocks\n· images (layout_vis + ảnh cắt) · raw_json', 'proc'),
    ]
    for nid, x, lab, key in ADP:
        d.node(nid, x, 316, 310, 168, lab, key, fontsize=9)
        d.edge('router', nid, '', color='#0E8088', srcside='bottom', dstside='top',
               waypoints=[(700, 292), (x + 155, 292)])

    d.node('ad5', 40, 512, 660, 118,
           'Bộ thích nghi lai — glm_vietocr_adapter.py · engine_name = "glm_vietocr"\n\n'
           'kết hợp GLMOCREngine (bố cục, thứ tự đọc, nhãn vùng, layout_vis) với VietOCREngine '
           '(nhận dạng tiếng Việt ở mức dòng trên cùng ảnh trang); mỗi dòng VietOCR được gán vào khối GLM có '
           'khung bao chứa tâm dòng, các dòng được sắp trên→dưới / trái→phải, và mỗi khối ghi lại '
           'recognition_source ∈ {vietocr, glm, fallback} kèm fallback_reason.',
           'corr', fontsize=9.5)
    d.edge('ad1', 'ad5', '', color='#9673A6', dashed=True, srcside='bottom', dstside='top')
    d.edge('ad4', 'ad5', 'dùng lại cả hai bộ thích nghi', color='#9673A6', dashed=True,
           srcside='bottom', dstside='top', waypoints=[(1245, 500), (370, 500)])

    d.node('glm', 740, 512, 660, 190,
           'Tích hợp GLM-OCR ngoài tiến trình  (glm_adapter.py)\n\n'
           '1.  Path(cfg.GLM_SDK_PYTHON).exists()  —  nếu không thì trả về lỗi có cấu trúc\n'
           '2.  kết nối TCP tới cfg.GLM_OCR_API_URL (mặc định http://localhost:8080), timeout 3 giây\n'
           '3.  môi trường tiến trình con: gỡ HF_HOME / HF_HUB_CACHE / TRANSFORMERS_CACHE,\n'
           '     đặt HF_HUB_OFFLINE = 1 và TRANSFORMERS_OFFLINE = 1\n'
           '4.  subprocess.run([GLM_SDK_PYTHON, "-m", "glmocr.cli", "parse", <ảnh>,\n'
           '     "--config", GLM_CONFIG_YAML, "--mode", "selfhosted", "--output", <thư mục tạm>],\n'
           '     cwd = GLM_ROOT, timeout = cfg.GLM_TIMEOUT)\n'
           '5.  đọc <tmp>/<stem>/: *.json (vùng), *.md, layout_vis/*, imgs/*  → xóa thư mục tạm\n'
           '6.  quy đổi khung bao từ hệ chuẩn hóa 0–1000 sang pixel ảnh (_scale_box)',
           'proc', fontsize=9.5)

    d.node('mlx', 740, 726, 660, 74,
           'Bên trong SDK glmocr (glm-ocr-server): PageLoader → phát hiện bố cục PP-DocLayoutV3 →\n'
           'gửi yêu cầu OCR theo từng vùng tới máy chủ MLX (chuẩn OpenAI /chat/completions,\n'
           'mô hình mlx-community/GLM-OCR-bf16) → ResultFormatter (json + markdown)',
           'proc', fontsize=9.5)
    d.edge('glm', 'mlx', '', color='#D79B00', srcside='bottom', dstside='top')

    d.node('norm', 40, 726, 660, 200,
           'Chuẩn hóa kết quả dùng chung  (ocr_service.run_ocr)\n\n'
           '• _normalize_block(): bảo đảm mọi khối đều có text, content, box, confidence\n'
           '• raw_results giữ lại thứ tự gốc do công cụ trả về\n'
           '• khối CÓ tọa độ → layout_service.reconstruct_layout(); khối KHÔNG có tọa độ được\n'
           '  nối vào sau nên không đoạn văn bản nào bị bỏ sót\n'
           '• layout_native = True (Modern, GLM, lai) thì bỏ qua bước sắp lại theo hình học\n'
           '• công cụ không tự sinh ảnh minh họa sẽ được vẽ ảnh phủ vùng\n'
           '  (_render_overlay_image, tô màu theo độ tin cậy)\n\n'
           'Hợp đồng trả về cho app.py:\n'
           '{success, results[{text, content, box, confidence, index}], img_width, img_height,\n'
           ' elapsed_ms, ocr_engine, inference_status, layout_native?, markdown?, html?,\n'
           ' tables_html?, layout_blocks?, images?, raw_json?}',
           'svc', fontsize=9.5)

    d.edge('req', 'router', '', color='#82B366', srcside='right', dstside='left')
    d.edge('abc', 'router', 'hiện thực', color='#3F61A8', dashed=True,
           srcside='left', dstside='right')
    d.edge('ad3', 'norm', '', color='#82B366', srcside='bottom', dstside='top',
           waypoints=[(895, 712), (370, 712)])
    d.edge('ad4', 'glm', '', color='#D79B00', srcside='bottom', dstside='top',
           waypoints=[(1245, 498), (1070, 498)])

    d.node('n1', 40, 950, 1360, 92,
           'Dữ kiện về tích hợp: năm bộ thích nghi được khởi tạo một lần lúc nạp router.py, nên các mô hình nặng chỉ '
           'được nạp ở lần dùng đầu tiên rồi tái sử dụng. Thêm hoặc thay một công cụ OCR chỉ cần thêm một lớp con '
           'OCREngine và một mục trong _ENGINES / _ALIASES — API tải tệp, phần lưu trữ và lược đồ cơ sở dữ liệu đều '
           'không đổi, vì mọi công cụ trả về cùng một hợp đồng kết quả. Nhánh GLM là nhánh duy nhất rời khỏi tiến '
           'trình Flask, và cũng là nhánh duy nhất có thể hỏng vì thiếu môi trường (venv SDK) hoặc vì máy chủ mô '
           'hình không chạy.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 3.8 Biểu diễn kết quả OCR
def f38():
    d = Diagram('fig_3_8_ocr_result_representations',
                'Hình 3.8 – Kết quả OCR theo văn bản và dữ liệu có cấu trúc',
                1440, 1030,
                subtitle='Luồng dữ liệu phía sau màn hình kết quả — công cụ nào sinh ra dạng biểu diễn nào, '
                         'được lưu ra sao và trả về bằng cách nào')

    d.node('res', 40, 110, 320, 168,
           'Từ điển kết quả của công cụ\n(một từ điển cho mỗi trang)\n\nresults[] · img_width / img_height\n'
           'elapsed_ms · ocr_engine\ninference_status · layout_native\nmarkdown? · html? · tables_html?\n'
           'layout_blocks? · images? · raw_json?',
           'eng', fontsize=10)

    d.node('p1', 420, 100, 300, 76, '_ocr_pages_to_text()\nnối văn bản mọi khối trên mọi trang', 'svc', fontsize=10)
    d.node('p2', 420, 190, 300, 76, '_build_ocr_layout()\nkhung bao · độ tin cậy · kích thước · thời gian', 'svc', fontsize=10)
    d.node('p3', 420, 280, 300, 100,
           '_persist_ocr_structured()\nmarkdown → markdown_normalize\n.repair_unmatched_display_math()', 'svc', fontsize=10)

    d.table('art', 800, 96, 380, 'Các kết xuất document_artifacts do app.py ghi', [
        ('ocr                 văn bản thuần', 'mọi công cụ'),
        ('ocr_layout      JSON khung bao / độ tin cậy', 'mọi công cụ'),
        ('ocr_images    JSON ảnh phủ + ảnh cắt (base64)', 'mọi công cụ'),
        ('ocr_json         JSON vùng theo từng trang', 'mọi công cụ'),
        ('ocr_markdown  Markdown', 'GLM · Modern'),
        ('ocr_html         HTML', 'Modern'),
        ('ocr_tables      JSON danh sách bảng HTML', 'GLM · Modern'),
        ('ocr_blocks     JSON nhãn / nội dung / bbox / thứ tự', 'GLM · Modern'),
    ], 'data')

    d.node('db', 1240, 96, 160, 226, 'SQLite\ndocument_artifacts\n\nUNIQUE\n(document_id, kind)\n\nghi đè bằng\nsave_artifact()',
           'data', shape='cyl', fontsize=9.5)

    d.container('view', 40, 420, 700, 300,
                'Hiển thị trên trình duyệt   (static/app.js — OCRView)', 'ui', header=34)
    d.node('v1', 62, 470, 320, 56, 'Thẻ Markdown\nmarked + KaTeX nội bộ + sanitizeHtml()', 'ui', parent='view', fontsize=9.5)
    d.node('v2', 62, 538, 320, 56, 'Thẻ Raw\nvăn bản thuần nối từ results[]', 'ui', parent='view', fontsize=9.5)
    d.node('v3', 62, 606, 320, 56, 'Thẻ Images\nảnh phủ bố cục và ảnh cắt từng vùng', 'ui', parent='view', fontsize=9.5)
    d.node('v4', 402, 470, 316, 56, 'Thẻ JSON\nvùng nhận dạng theo từng trang', 'ui', parent='view', fontsize=9.5)
    d.node('v5', 402, 538, 316, 56, 'Lớp phủ canvas (ocr-canvas.js)\nkhung bao vẽ trên ảnh trang', 'ui', parent='view', fontsize=9.5)
    d.node('v6', 402, 606, 316, 56, 'Dải thống kê\nsố vùng · độ tin cậy TB · thời gian · số trang', 'ui', parent='view', fontsize=9.5)

    d.container('exp', 780, 420, 620, 300, 'Kết xuất và sử dụng tiếp', 'svc', header=34)
    d.node('x1', 802, 470, 280, 56, 'Tải về .md\n(Markdown thật khi có)', 'svc', parent='exp', fontsize=9.5)
    d.node('x2', 802, 538, 280, 56, 'Tải về .txt\nvăn bản OCR thuần', 'svc', parent='exp', fontsize=9.5)
    d.node('x3', 802, 606, 280, 56, 'Tải về .json\ndữ liệu có cấu trúc, mọi trang', 'svc', parent='exp', fontsize=9.5)
    d.node('x4', 1102, 470, 278, 90, 'POST /api/ocr/export-docx\npandoc  markdown+smart+tex_math_dollars\n→ .docx  (timeout 30 giây)',
           'ext', parent='exp', fontsize=9.5)
    d.node('x5', 1102, 578, 278, 84, 'Hiệu chỉnh tiếng Việt\nđọc kết xuất ocr_json →\ncorrected_json / corrected_md',
           'corr', parent='exp', fontsize=9.5)

    d.edge('res', 'p1', '', color='#82B366', srcside='right', dstside='left')
    d.edge('res', 'p2', '', color='#82B366', srcside='right', dstside='left')
    d.edge('res', 'p3', '', color='#82B366', srcside='right', dstside='left')
    d.edge('p1', 'art', '', color='#5A5A5A', srcside='right', dstside='left')
    d.edge('p2', 'art', '', color='#5A5A5A', srcside='right', dstside='left')
    d.edge('p3', 'art', '', color='#5A5A5A', srcside='right', dstside='left')
    d.edge('art', 'db', 'ghi', color='#5A5A5A', srcside='right', dstside='left')
    d.edge('res', 'view', 'phản hồi HTTP của /api/ocr/page và /api/ocr/all', color='#3F61A8',
           srcside='bottom', dstside='top', waypoints=[(200, 400), (390, 400)])
    d.edge('db', 'view', 'GET /api/documents/<id>/text  và  /ocr-images   (khi mở lại tài liệu đã lưu)',
           color='#5A5A5A', dashed=True, srcside='bottom', dstside='top',
           waypoints=[(1320, 400), (390, 400)])
    d.edge('view', 'exp', '', color='#82B366', srcside='right', dstside='left')

    d.node('cap', 40, 748, 1360, 128,
           'Bảng năng lực của từng công cụ (rút ra từ các bộ thích nghi)\n\n'
           'PaddleOCR Legacy   →  kết quả + độ tin cậy + khung bao;  ocr_json chứa results + layout_blocks;  ảnh phủ tự sinh\n'
           'VietOCR                    →  kết quả + khung bao (độ tin cậy = None);  ocr_json dạng dự phòng;  ảnh phủ tự sinh\n'
           'PaddleOCR Modern  →  kết quả + độ tin cậy + khung bao  +  markdown, html, tables_html, layout_blocks, ảnh phủ có nhãn\n'
           'GLM-OCR                  →  kết quả + khung bao (độ tin cậy = None)  +  markdown, tables_html, layout_blocks, raw_json,\n'
           '                                      ảnh layout_vis và ảnh cắt từng vùng\n'
           'GLM + VietOCR        →  bố cục của GLM với văn bản của VietOCR, kèm recognition_source và fallback_reason theo khối',
           'note', shape='note', fontsize=9.5)

    d.node('todo', 40, 900, 1360, 96,
           'MỘT PHẦN — phần thuyết minh trình bày Hình 3.8 dưới dạng ảnh chụp màn hình kết quả. Hình ở trên là kiến '
           'trúc và luồng dữ liệu phía sau màn hình đó, tức là phần mà mã nguồn hỗ trợ. Nếu báo cáo cần chính màn '
           'hình, hãy chụp khu vực làm việc OCR của một tài liệu với các thẻ Markdown, Raw, Images và JSON hiển thị '
           'cạnh ảnh trang (xem MANUAL_COMPLETION.md, Hình 3.8).',
           'todo', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 3.9 Triển khai thử nghiệm
def f39():
    d = Diagram('fig_3_9_test_deployment',
                'Hình 3.9 – Mô hình triển khai hệ thống trong môi trường thử nghiệm',
                1400, 940,
                subtitle='Mô hình triển khai thử nghiệm đúng như tài liệu RUN_MACOS.md mô tả và '
                         'config.py / tools/glm_serve.sh hiện thực hóa')

    d.container('mach', 40, 92, 1000, 646,
                'Máy thử nghiệm  —  macOS Apple Silicon (M1 / M2 / M3 / M4) · Python 3.10 · Homebrew', 'proc', header=38)

    d.node('t1', 64, 150, 470, 152,
           'Cửa sổ lệnh 1   —   máy chủ mô hình GLM-OCR MLX\n\n'
           'GLM_ROOT="$PWD/glm-ocr-server"\nGLM_MLX_PYTHON="$PWD/glm-ocr-server/.venv-mlx/bin/python"\n'
           'bash glm-ocr-ui/tools/glm_serve.sh\n\n'
           'exec python -m mlx_vlm.server --trust-remote-code --port 8080\nmô hình nằm thường trú giữa các yêu cầu',
           'proc', parent='mach', fontsize=9.5)
    d.node('t2', 552, 150, 466, 152,
           'Cửa sổ lệnh 2   —   ứng dụng web SmartDocs\n\n'
           'cd glm-ocr-ui  ·  source .venv/bin/activate\npython app.py\n\n'
           'máy chủ phát triển đa luồng của Flask\nhttp://localhost:5001   (HOST 0.0.0.0, PORT 5001)',
           'api', parent='mach', fontsize=9.5)

    d.node('sdk', 64, 328, 470, 96,
           'GLM-OCR SDK  —  glm-ocr-server/.venv-sdk\nđược glm_adapter.py khởi chạy cho mỗi yêu cầu OCR:\n'
           'python -m glmocr.cli parse <page.png> --config mlx_config.yaml --mode selfhosted\n'
           'PP-DocLayoutV3 chạy trên CPU (mlx_config.yaml: layout.device = cpu)',
           'proc', parent='mach', fontsize=9.5)
    d.node('eng', 552, 328, 466, 96,
           'Công cụ OCR chạy trong tiến trình Flask\nPaddleOCR PP-OCRv5 · PP-StructureV3 + PP-OCRv6_medium\n'
           'VietOCR vgg_transformer\ncfg.DEVICE tự phân giải: CUDA → MPS → CPU',
           'eng', parent='mach', fontsize=9.5)

    d.node('db', 64, 450, 300, 88, 'SQLite  paddleocr.db\ntạo bởi db.create_all()\ntài khoản khởi tạo sẵn:\n'
                                   'admin / admin123 · user / user123', 'data', parent='mach', shape='cyl', fontsize=9.5)
    d.node('up', 384, 450, 300, 88, 'uploads/\ntệp gốc, đặt tên theo UUID\n+ tệp .png tạm của từng trang\n'
                                    'MAX_UPLOAD_MB = 50', 'data', parent='mach', fontsize=9.5)
    d.node('mm', 704, 450, 314, 88, 'models/ · bộ nhớ đệm HF · PaddleX\nOFFLINE=0 ở lần chạy đầu để tải mô hình,\n'
                                    'sau đó OFFLINE=1 để chạy ngoại tuyến', 'data', parent='mach', fontsize=9.5)

    d.node('env', 64, 562, 954, 152,
           'Các khóa .env xác định môi trường này  (glm-ocr-ui/.env, theo .env.example và RUN_MACOS.md)\n\n'
           'HOST=0.0.0.0   PORT=5001   OFFLINE=0/1   DEVICE=auto   MODEL_DIR=./models   OCR_ENGINE=paddle\n'
           'GLM_ROOT=<repo>/glm-ocr-server        GLM_SDK_PYTHON=<repo>/glm-ocr-server/.venv-sdk/bin/python\n'
           'GLM_MLX_PYTHON=<repo>/glm-ocr-server/.venv-mlx/bin/python     GLM_CONFIG_YAML=<repo>/glm-ocr-server/mlx_config.yaml\n'
           'GLM_OCR_API_URL=http://localhost:8080   GLM_TIMEOUT=300\n'
           'VI_CORRECTION_ENABLED=true   VI_CORRECTION_PROVIDER=protonx   VI_CORRECTION_MODEL=nano   VI_CORRECTION_DEVICE=cpu',
           'ext', parent='mach', fontsize=9.5)

    d.node('cliB', 1080, 150, 280, 130,
           'Người kiểm thử\ntrình duyệt trên cùng máy\n(http://localhost:5001)\nhoặc trên một máy khác cùng\n'
           'mạng nội bộ (HOST = 0.0.0.0)',
           'ui', fontsize=10)

    d.edge('cliB', 't2', 'HTTP', color='#3F61A8', srcside='left', dstside='right')
    d.edge('t2', 'sdk', 'tiến trình con', color='#D79B00', srcside='left', dstside='top',
           waypoints=[(540, 226), (540, 310), (299, 310)])
    d.edge('sdk', 't1', 'HTTP  localhost:8080', color='#D79B00', srcside='top', dstside='bottom')
    d.edge('t2', 'eng', 'trong tiến trình', color='#0E8088', srcside='bottom', dstside='top')
    d.edge('t2', 'db', 'SQLAlchemy', color='#5A5A5A', srcside='bottom', dstside='top',
           waypoints=[(785, 436), (214, 436)])
    d.edge('t2', 'up', 'thao tác tệp', color='#5A5A5A', srcside='bottom', dstside='top',
           waypoints=[(785, 436), (534, 436)])

    d.node('todo', 1080, 310, 300, 300,
           'CẦN HOÀN THIỆN THỦ CÔNG\n\n'
           'Phần thuyết minh yêu cầu Hình 3.9 thể hiện WebApp ở cổng 5002 và một DesktopApp với ba chế '
           'độ Bundled Core, Existing WebApp Runtime và Remote Server.\n\n'
           'Kho mã nguồn này không có cả hai: cổng ứng dụng là 5001 (mặc định trong config.py và trong '
           'RUN_MACOS.md), không có ứng dụng desktop, không có phần chọn chế độ chạy và không có mã '
           'kết nối tới máy chủ từ xa.\n\n'
           'Cổng 5002 chỉ xuất hiện trong glm-ocr-server/glmocr/config.yaml và mlx_config.yaml, là cổng '
           'mặc định của dịch vụ HTTP tùy chọn glmocr.server mà SmartDocs không dùng — SmartDocs gọi '
           'trực tiếp qua dòng lệnh.',
           'todo', shape='note', fontsize=9.5)

    d.node('n1', 40, 762, 1320, 62,
           'Nguyên tắc truy cập thể hiện trong mô hình triển khai: trình duyệt chỉ làm việc với Flask ở cổng 5001. '
           'Máy chủ mô hình MLX ở cổng 8080 chỉ được tiến trình con glmocr tạm thời gọi tới, còn cơ sở dữ liệu và '
           'thư mục uploads chỉ được app.py / models.py truy cập, nhờ đó phân quyền, trạng thái tài liệu và nhật ký '
           'hoạt động luôn nhất quán bất kể người dùng truy cập bằng cách nào.',
           'note', shape='note', fontsize=10)
    d.node('n2', 40, 838, 1320, 62,
           'Không thuộc môi trường thử nghiệm: không có container runtime, không có proxy ngược, không có máy chủ '
           'WSGI cho môi trường thật, không có cơ sở dữ liệu ngoài và không có dịch vụ OCR đám mây. Nhánh đám mây '
           '(MaaS) của SDK bị tắt bởi mlx_config.yaml (pipeline.maas.enabled = false) và bộ thích nghi luôn truyền '
           'tham số --mode selfhosted.',
           'note', shape='note', fontsize=10)
    return d


if __name__ == '__main__':
    for fn in (f31, f32, f36, f37, f38, f39):
        write(fn())
