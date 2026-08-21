#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hình chương 2 (2.1 - 2.10).

Mọi thành phần đều được rút ra từ mã nguồn OCRandCorrectionVn; danh sách tệp
nguồn của từng hình xem trong FIGURE_INDEX.md.

Quy ước: tên tệp, tên hàm, tên lớp, đường dẫn API, tên biến môi trường và các
định danh kỹ thuật được giữ nguyên; phần diễn giải dùng tiếng Việt.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram_engine import Diagram, write, set_out, row_x

set_out(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chapter2'))

SYS = 'Ứng dụng web SmartDocs  (glm-ocr-ui, Flask :5001)'


# ══════════════════════════════════════════════════ 2.1 Ca sử dụng
def f21():
    d = Diagram('fig_2_1_use_case',
                'Hình 2.1 – Biểu đồ ca sử dụng tổng quát của hệ thống',
                1300, 1090,
                subtitle='Rút ra từ các tuyến (route) Flask trong app.py, auth.py, admin_bp.py '
                         'và correction_bp.py')

    d.node('act_user', 60, 330, 130, 96, 'Người dùng\n(role = "user")', 'actor', shape='actor', fontsize=12)
    d.node('act_admin', 1120, 330, 130, 96, 'Quản trị viên\n(role = "admin")', 'actor', shape='actor', fontsize=12)

    d.container('sys', 240, 92, 800, 826, SYS, 'ui', header=38)

    user_uc = [
        ('u1',  'Đăng nhập / Đăng xuất\n/login · /logout'),
        ('u2',  'Tải tài liệu lên\nPOST /api/upload'),
        ('u3',  'Xem trước và chuyển trang\nPOST /api/ocr/page (preview_only)'),
        ('u4',  'Lựa chọn công cụ OCR\n(tham số engine)'),
        ('u5',  'Thực hiện OCR một trang\nPOST /api/ocr/page'),
        ('u6',  'Thực hiện OCR toàn bộ trang\nPOST /api/ocr/all'),
        ('u7',  'Sắp xếp lại một vùng đã chọn\nPOST /api/ocr/reconstruct-region'),
        ('u8',  'Đọc văn bản từ TXT / DOCX / PDF\nPOST /api/read-text'),
        ('u9',  'Xem kết quả (Markdown · Raw ·\nImages · JSON)'),
        ('u10', 'Sao chép và tải kết quả\n.md · .txt · .json · .docx'),
        ('u11', 'Quản lý tài liệu của mình\nGET/DELETE /api/documents'),
        ('u12', 'Chạy hiệu chỉnh tiếng Việt\nPOST /api/correction/run'),
        ('u13', 'Lưu và mở lại bản đã hiệu chỉnh\n/api/correction/save · /result'),
        ('u14', 'Đổi ngôn ngữ giao diện\nPOST /api/set-lang'),
    ]
    y = 146
    for i, (uid, lab) in enumerate(user_uc):
        d.node(uid, 276, y + i * 54, 330, 46, lab, 'svc', shape='ellipse', fontsize=9.5)

    adm_uc = [
        ('a1', 'Xem trang tổng quan quản trị\nGET /admin/'),
        ('a2', 'Quản lý tài khoản người dùng\ntạo · sửa · đặt lại mật khẩu\nkhóa/mở khóa · xóa'),
        ('a3', 'Giám sát toàn bộ tài liệu\nGET /admin/files'),
        ('a4', 'Xem nhật ký hoạt động\nGET /admin/logs'),
        ('a5', 'Truy cập tài liệu của mọi người dùng\n(ngoại lệ trong kiểm tra quyền sở hữu)'),
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
           '«generalization» — quản trị viên thực hiện được mọi ca sử dụng của người dùng',
           dashed=True, color='#33475B', waypoints=[(1185, 944), (125, 944)],
           srcside='bottom', dstside='bottom')

    d.node('n1', 240, 1000, 800, 62,
           'Ghi chú phạm vi: hệ thống không có màn hình "cấu hình OCR" trong ứng dụng — các giá trị '
           'mặc định của công cụ OCR được đặt bằng biến môi trường do config.py đọc (OCR_ENGINE, '
           'VIETOCR_*, GLM_*, VI_CORRECTION_*). Vì vậy không có ca sử dụng tương ứng.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 2.2 Ngữ cảnh
def f22():
    d = Diagram('fig_2_2_context',
                'Hình 2.2 – Biểu đồ ngữ cảnh của hệ thống số hóa tài liệu',
                1340, 900,
                subtitle='Phạm vi hệ thống và các tác nhân / tiến trình / vùng dữ liệu bên ngoài '
                         'thực sự có trong kho mã nguồn')

    d.node('sys', 430, 336, 440, 150,
           'Hệ thống số hóa tài liệu\n' + SYS +
           '\napp.py · auth.py · admin_bp.py · correction_bp.py',
           'api', shape='round', fontsize=13, bold=True)

    d.node('user', 130, 118, 130, 96, 'Người dùng', 'actor', shape='actor')
    d.node('admin', 1040, 118, 130, 96, 'Quản trị viên', 'actor', shape='actor')

    d.node('paddle', 60, 590, 300, 116,
           'Công cụ OCR chạy trong tiến trình\nPaddleOCR (PP-OCRv5)\nPP-StructureV3 (PP-OCRv6)\n'
           'VietOCR (vgg_transformer)',
           'eng', fontsize=11)
    d.node('glmcli', 470, 574, 360, 74,
           'Tiến trình con GLM-OCR SDK\nglm-ocr-server/.venv-sdk · glmocr.cli parse',
           'proc', fontsize=11)
    d.node('mlx', 470, 700, 360, 74,
           'Máy chủ mô hình GLM-OCR MLX\nhttp://localhost:8080 · mlx-community/GLM-OCR-bf16',
           'proc', fontsize=11)
    d.node('store', 940, 590, 320, 116,
           'Vùng dữ liệu\nSQLite  paddleocr.db\nuploads/  (tệp gốc đặt tên theo UUID)\n'
           'models/  (kho mô hình cục bộ)',
           'data', fontsize=11)
    d.node('pandoc', 1000, 336, 260, 70,
           'Chương trình pandoc\n(Markdown → xuất DOCX)', 'ext', fontsize=11)

    d.edge('user', 'sys', '→  Tài khoản, tài liệu, yêu cầu OCR\n←  Trạng thái, kết quả, lịch sử',
           color='#3F61A8', arrow='both')
    d.edge('admin', 'sys', '→  Quản lý tài khoản, truy vấn nhật ký / tệp\n←  Nhật ký, thống kê, trạng thái hệ thống',
           color='#9673A6', arrow='both')
    d.edge('sys', 'paddle', '→  Ảnh trang đã chuẩn hóa\n←  Khối văn bản, khung bao, độ tin cậy',
           color='#0E8088', arrow='both')
    d.edge('sys', 'glmcli', '→  Ảnh trang + tham số dòng lệnh\n←  JSON / Markdown / layout_vis / imgs',
           color='#D79B00', arrow='both')
    d.edge('glmcli', 'mlx', '→  HTTP /chat/completions (theo từng vùng)\n←  Nội dung vùng đã nhận dạng',
           color='#D79B00', arrow='both')
    d.edge('sys', 'store', '→  Tệp gốc, kết xuất, bản ghi\n←  Tài liệu và kết xuất đã lưu',
           color='#5A5A5A', arrow='both')
    d.edge('sys', 'pandoc', '→  Markdown    ←  .docx', color='#999999', arrow='both')

    d.node('n1', 60, 792, 1220, 62,
           'Nhánh GLM-OCR là tùy chọn và chỉ chạy trên Apple Silicon: config.py phân giải GLM_ROOT / '
           'GLM_SDK_PYTHON / GLM_OCR_API_URL, còn glm_adapter.py từ chối chạy khi thiếu môi trường ảo SDK '
           'hoặc khi không có tiến trình nào lắng nghe ở cổng MLX. Nhánh OCR đám mây (MaaS) bị tắt — '
           'mlx_config.yaml đặt pipeline.maas.enabled: false.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 2.3 Kiến trúc tổng thể
def f23():
    d = Diagram('fig_2_3_architecture',
                'Hình 2.3 – Kiến trúc tổng thể các thành phần của hệ thống',
                1400, 1130,
                subtitle='Kiến trúc thành phần theo tầng, dựng lại từ mã nguồn '
                         '(glm-ocr-ui/ và glm-ocr-server/)')

    SL = [62, 300, 538, 776]
    NW = 230

    d.container('l1', 40, 92, 1000, 134, 'Tầng giao diện  (trình duyệt)', 'ui')
    d.node('corrpage', SL[0], 140, NW, 70, 'Trang hiệu chỉnh\nstatic/correction.html\ncorrection.js',
           'corr', parent='l1', fontsize=10)
    d.node('spa', SL[1], 140, NW, 70, 'SPA SmartDocs\nstatic/index.html · app.js\nocr-canvas.js · i18n.js',
           'ui', parent='l1', fontsize=10)
    d.node('adminui', SL[2], 140, NW, 70, 'Trang quản trị (Jinja)\ntemplates/admin/\nbase·dashboard·users·logs·files',
           'ui', parent='l1', fontsize=10)
    d.node('loginui', SL[3], 140, NW, 70, 'Trang đăng nhập / 403\ntemplates/login.html\ntemplates/403.html',
           'ui', parent='l1', fontsize=10)

    d.container('l2', 40, 262, 1000, 150,
                'Tầng ứng dụng  —  Flask (app.py; máy chủ phát triển đa luồng, HOST/PORT lấy từ config.py)', 'api')
    d.node('corrbp', SL[0], 314, NW, 82,
           'correction_bp\ncorrection_bp.py\n/correction\n/api/correction/*', 'api', parent='l2', fontsize=9.5)
    d.node('routes', SL[1], 314, NW, 82,
           'Tuyến chính (app.py)\n/api/upload · /api/ocr/page\n/api/ocr/all · /api/documents\n/api/ocr/export-docx',
           'api', parent='l2', fontsize=9.5)
    d.node('adminbp', SL[2], 314, NW, 82,
           'admin_bp\nadmin_bp.py\n/admin tổng quan · người dùng\nnhật ký · tệp', 'api', parent='l2', fontsize=9.5)
    d.node('authbp', SL[3], 314, NW, 82,
           'auth_bp (auth.py)\nđăng nhập / đăng xuất\n/api/auth/me · /api/set-lang\n@admin_required',
           'api', parent='l2', fontsize=9.5)

    d.container('l3', 40, 442, 1000, 158, 'Tầng dịch vụ  (services/)', 'svc')
    d.node('vicorr', SL[0], 494, NW, 88,
           'vi_correction/\nclassification · masking\nsegmentation · pipeline\nvalidation · renderers · service',
           'corr', parent='l3', fontsize=9.5)
    d.node('ocrsvc', SL[1], 494, NW, 88,
           'ocr_service.py\nsmart_ocr_service.py\nchuẩn hóa khối,\nvẽ ảnh phủ vùng nhận dạng',
           'svc', parent='l3', fontsize=9.5)
    d.node('layout', SL[2], 494, NW, 88,
           'layout_service.py\ngeometry_service.py\ndựng lại thứ tự đọc\ntheo hình học', 'svc', parent='l3', fontsize=9.5)
    d.node('textsvc', SL[3], 494, NW, 88,
           'text_service.py\nmarkdown_normalize.py\nactivity_registry.py\ncpu_threads.py',
           'svc', parent='l3', fontsize=9.5)

    d.container('l4', 40, 630, 1000, 226,
                'Tầng công cụ OCR  (services/ocr_engines/ — lớp trừu tượng OCREngine + các bộ thích nghi)', 'eng')
    d.node('router', 62, 682, 956, 46,
           'router.py   —   bảng _ENGINES · _ALIASES · normalize_engine_name() · get_engine() · run_ocr()',
           'eng', parent='l4', fontsize=11, bold=True)
    d.node('e_pad', SL[0], 744, NW, 92,
           'PaddleOCREngine\npaddleocr.PaddleOCR\nocr_version = PP-OCRv5\n(dòng văn bản + khung + độ tin cậy)',
           'eng', parent='l4', fontsize=9.5)
    d.node('e_mod', SL[1], 744, NW, 92,
           'PaddleOCRModernEngine\npaddleocr.PPStructureV3\nPP-OCRv6_medium det/rec\n(markdown · html · bảng)',
           'eng', parent='l4', fontsize=9.5)
    d.node('e_vi', SL[2], 744, NW, 92,
           'VietOCREngine\nPP-OCRv5 phát hiện dòng +\nvietocr Predictor\n(vgg_transformer)',
           'eng', parent='l4', fontsize=9.5)
    d.node('e_glm', SL[3], 744, NW, 92,
           'GLMOCREngine\nGLMVietOCREngine\ngọi tiến trình con\n(kết quả có sẵn bố cục)',
           'eng', parent='l4', fontsize=9.5)

    d.container('l4b', 40, 886, 596, 156,
                'Bộ cung cấp mô hình hiệu chỉnh  (services/vi_correction/providers/)', 'corr', header=32)
    d.node('p_px', 62, 930, 254, 48, 'ProtonxProvider\nnano · distilled · full', 'corr', parent='l4b', fontsize=10)
    d.node('p_bmd', 336, 930, 254, 48, 'Bmd1905Provider\nvietnamese-correction-v2', 'corr', parent='l4b', fontsize=10)
    d.node('p_mock', 62, 986, 254, 44, 'MockProvider', 'corr', parent='l4b', fontsize=10)
    d.node('p_mr', 336, 986, 254, 44, 'MrlasdtProvider (có trong registry)', 'corr', parent='l4b', fontsize=10)

    d.container('ext', 660, 886, 380, 156,
                'Tiến trình bên ngoài (Apple Silicon)', 'proc', header=32)
    d.node('glmsdk', 682, 930, 336, 48,
           'glmocr CLI  ·  .venv-sdk\nphát hiện bố cục PP-DocLayoutV3', 'proc', parent='ext', fontsize=10)
    d.node('mlxsrv', 682, 986, 336, 44,
           'Máy chủ MLX :8080  ·  .venv-mlx\nmlx-community/GLM-OCR-bf16', 'proc', parent='ext', fontsize=10)

    d.container('data', 1060, 262, 300, 594, 'Tầng dữ liệu', 'data', header=36)
    d.node('db', 1082, 316, 256, 80, 'SQLite\npaddleocr.db\n(cfg.DB_PATH)', 'data',
           parent='data', shape='cyl', fontsize=10.5)
    d.node('up', 1082, 408, 256, 76, 'uploads/\n{uuid4}{suffix}\n(cfg.UPLOAD_DIR)', 'data',
           parent='data', fontsize=10.5)
    d.node('mdl', 1082, 496, 256, 80, 'models/  +  bộ nhớ đệm HF\n(cfg.MODEL_DIR;\nOFFLINE=1 chặn tải về)',
           'data', parent='data', fontsize=10.5)
    d.node('dnote', 1082, 588, 256, 250,
           'Chỉ truy cập qua models.py /\nSQLAlchemy và thao tác tệp\ntrong app.py\n\n'
           'Lược đồ vật lý (models.py)\n• users\n• documents\n• document_artifacts\n• activity_logs\n\n'
           'Phiên bản này không dùng máy chủ\ncơ sở dữ liệu riêng, kho đối tượng,\nbộ nhớ đệm hay hàng đợi.',
           'data', parent='data', fontsize=9.5)

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
           srcside='right', dstside='left', waypoints=[(1050, 337), (1050, 545)])
    d.edge('l4', 'mdl', '', color='#5A5A5A',
           srcside='right', dstside='left', waypoints=[(1050, 743), (1050, 536)])

    d.node('n1', 40, 1062, 1320, 52,
           'Không có trong kho mã nguồn nên không được vẽ: ứng dụng desktop Tauri/Rust và các mô-đun trò chuyện '
           'RAG, dịch, tóm tắt, tác tử LLM được nhắc tới trong README.md và docs/. Hình chỉ thể hiện các thành '
           'phần thực sự tồn tại trong mã của phiên bản này.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 2.4 Kiến trúc triển khai
def f24():
    d = Diagram('fig_2_4_deployment',
                'Hình 2.4 – Kiến trúc triển khai của hệ thống',
                1340, 800,
                subtitle='Góc nhìn triển khai — các tiến trình, cổng và đường trao đổi được xác định bởi '
                         'app.py, config.py, tools/glm_serve.sh và RUN_MACOS.md')

    d.container('client', 50, 100, 300, 230, 'Máy người dùng', 'ui')
    d.node('browser', 76, 152, 248, 76, 'Trình duyệt web\nSPA + trang quản trị dựng phía máy chủ\n'
                                        '(không cần bước build frontend)',
           'ui', parent='client', fontsize=10.5)
    d.node('brnote', 76, 244, 248, 64, 'http://<host>:5001\nCookie phiên làm việc\n(HttpOnly · SameSite=Lax)',
           'ui', parent='client', fontsize=9.5)

    d.container('host', 430, 100, 800, 530,
                'Máy chủ ứng dụng  —  macOS Apple Silicon · Python 3.10  (RUN_MACOS.md)', 'proc', header=38)

    d.node('flask', 460, 158, 740, 82,
           'Tiến trình 1 · Máy chủ ứng dụng Flask\nglm-ocr-ui/.venv/bin/python app.py\n'
           'app.run(host=cfg.HOST 0.0.0.0, port=cfg.PORT 5001, threaded=True, debug=False)',
           'api', parent='host', fontsize=11, bold=True)

    d.node('inproc', 460, 268, 356, 80,
           'Công cụ OCR chạy trong tiến trình\n(cùng trình thông dịch với Flask)\n'
           'PaddleOCR · PP-StructureV3 · VietOCR',
           'eng', parent='host', fontsize=10)
    d.node('sdkp', 844, 268, 356, 80,
           'Tiến trình 3 (tạm thời) · GLM-OCR SDK\n.venv-sdk · python -m glmocr.cli parse\n'
           'khởi tạo cho mỗi lần OCR · giới hạn GLM_TIMEOUT',
           'proc', parent='host', fontsize=10)
    d.node('pandoc', 460, 392, 356, 80,
           'Chương trình pandoc (tùy chọn)\ntìm bằng shutil.which() lúc nạp mô-đun;\n'
           '/api/ocr/export-docx trả 501 nếu không có',
           'ext', parent='host', fontsize=10)
    d.node('mlxp', 844, 392, 356, 80,
           'Tiến trình 2 · Máy chủ mô hình GLM-OCR MLX\n.venv-mlx · python -m mlx_vlm.server\n'
           'lắng nghe cổng :8080 · mô hình nằm thường trú',
           'proc', parent='host', fontsize=10)

    d.container('stor', 460, 516, 740, 96, 'Lưu trữ cục bộ trên máy chủ', 'data', header=30)
    d.node('db', 478, 552, 226, 50, 'SQLite  paddleocr.db\n(cfg.DB_PATH)', 'data',
           parent='stor', shape='cyl', fontsize=10)
    d.node('up', 722, 552, 216, 50, 'uploads/ {uuid4}{suffix}\n(cfg.UPLOAD_DIR)', 'data', parent='stor', fontsize=10)
    d.node('mdl', 956, 552, 226, 50, 'models/ + bộ nhớ đệm HF\n(cfg.MODEL_DIR)', 'data', parent='stor', fontsize=10)

    d.edge('browser', 'flask', 'HTTP  (localhost hoặc mạng nội bộ)\nJSON + tải tệp multipart', color='#3F61A8',
           srcside='right', dstside='left')
    d.edge('flask', 'inproc', 'gọi trong tiến trình', color='#0E8088',
           srcside='bottom', dstside='top', waypoints=[(830, 254), (638, 254)])
    d.edge('flask', 'sdkp', 'subprocess.run()\nmôi trường đã lọc', color='#D79B00',
           srcside='bottom', dstside='top', waypoints=[(830, 254), (1022, 254)])
    d.edge('sdkp', 'mlxp', 'HTTP localhost:8080  ·  /chat/completions', color='#D79B00',
           srcside='bottom', dstside='top')
    d.edge('flask', 'pandoc', 'subprocess.run(pandoc)', color='#999999',
           srcside='left', dstside='left', waypoints=[(452, 199), (452, 432)])
    d.edge('flask', 'stor', 'SQLAlchemy  ·  thao tác tệp', color='#5A5A5A',
           srcside='right', dstside='right', waypoints=[(1216, 199), (1216, 564)])
    d.edge('inproc', 'mdl', 'tệp mô hình', color='#5A5A5A', dashed=True,
           srcside='bottom', dstside='top', waypoints=[(638, 494), (1069, 494)])

    d.node('n1', 50, 660, 1240, 92,
           'Sự kiện triển khai lấy từ kho mã nguồn: ứng dụng web không dùng container, máy chủ proxy ngược, '
           'máy chủ WSGI cho môi trường thật, hàng đợi thông điệp hay dịch vụ đám mây nào — app.py khởi động '
           'chính máy chủ phát triển đa luồng của Flask. Các tệp Dockerfile và kịch bản khởi động Docker trong '
           'glm-ocr-server/apps/ thuộc bản demo GLM-OCR gốc (FastAPI + React) và không được SmartDocs sử dụng. '
           'Tiến trình 2 và 3 là tùy chọn: nếu thiếu, chỉ còn các công cụ PaddleOCR / VietOCR hoạt động.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 2.5 Biểu đồ tuần tự
def f25():
    d = Diagram('fig_2_5_sequence_ocr',
                'Hình 2.5 – Biểu đồ tuần tự quá trình xử lý một yêu cầu OCR',
                1380, 1276,
                subtitle='Lần theo app.py (/api/upload, /api/ocr/page), ocr_service.py, '
                         'services/ocr_engines/router.py, glm_adapter.py và models.py')

    LL = [('u', 120, 'Người dùng\n(SPA trên trình duyệt)', 'ui'),
          ('api', 330, 'Flask app.py\nhàm xử lý tuyến', 'api'),
          ('svc', 550, 'ocr_service /\nsmart_ocr_service', 'svc'),
          ('rt', 770, 'ocr_engines\nrouter + bộ thích nghi', 'eng'),
          ('ext', 990, 'Tiến trình con GLM SDK\n+ máy chủ MLX :8080', 'proc'),
          ('db', 1210, 'models.py\nSQLite + uploads/', 'data')]
    for lid, x, lab, key in LL:
        d.lifeline(lid, x, lab, key, hy=100, hh=54, hw=178, bottom=1218)

    m = d.message
    seq = [
        ('u', 'api', 'POST /api/upload   (tệp multipart)', False, 'call', 38),
        ('api', 'api', '@login_required · MAX_CONTENT_LENGTH · _safe_basename() · kiểm tra phần mở rộng',
         False, 'self', 62),
        ('api', 'db', 'lưu uploads/{uuid4}{suffix} · INSERT Document(status="uploaded") · log_activity("upload")',
         False, 'call', 36),
        ('db', 'api', 'doc_id, file_id', True, 'call', 32),
        ('api', 'u', '200 {file_id, filename, page_count, is_pdf, …}', True, 'call', 52),
        ('u', 'api', 'POST /api/ocr/page  {file_id, page, engine}', False, 'call', 36),
        ('api', 'db', '_resolve_owned_file(): tra cứu Document + kiểm tra quyền sở hữu / quản trị', False, 'call', 32),
        ('db', 'api', 'đường dẫn tệp trên đĩa  (404 không tồn tại · 403 không sở hữu)', True, 'call', 42),
        ('api', 'api', 'PDF → pdf_page_to_pil(scale=2.0) → tệp .png tạm     |     ảnh → PIL.Image.open()',
         False, 'self', 62),
        ('api', 'api', '_resolve_selected_engine(): normalize_engine_name(); "vietocr" + ".pdf" → "paddleocr"',
         False, 'self', 74),
        ('api', 'svc', 'smart_ocr_service.run_ocr_pipeline(image_path, engine_name)', False, 'call', 36),
        ('svc', 'rt', 'router.run_ocr() → get_engine(name).run(image_path)', False, 'call', 38),
        ('rt', 'ext', 'chỉ với công cụ GLM: kiểm tra TCP cổng :8080, sau đó gọi tiến trình con glmocr.cli parse',
         False, 'call', 42),
        ('ext', 'ext', 'phát hiện bố cục PP-DocLayoutV3 → gọi mô hình VLM theo từng vùng → JSON / Markdown / imgs',
         False, 'self', 58),
        ('ext', 'rt', 'đọc kết xuất từ thư mục đầu ra', True, 'call', 36),
        ('rt', 'svc', '{success, results[text/box/confidence], img_width, img_height, elapsed_ms, …}',
         True, 'call', 42),
        ('svc', 'svc', '_normalize_block() · dựng lại thứ tự đọc (bỏ qua khi layout_native) · vẽ ảnh phủ vùng',
         False, 'self', 62),
        ('svc', 'api', 'từ điển kết quả đã chuẩn hóa', True, 'call', 36),
        ('api', 'db', 'status = "ocr_done" · save_artifact(ocr, ocr_layout, ocr_markdown, ocr_json, ocr_images …)',
         False, 'call', 34),
        ('api', 'db', 'log_activity("ocr", engine · processing_time_ms · inference_status)', False, 'call', 38),
        ('api', 'u', '200 {results, page_image_b64, markdown, images, elapsed_ms}', True, 'call', 36),
    ]
    y = 194
    for frm, to, lab, dash, kind, step in seq:
        m(frm, to, y, lab, dashed=dash, kind=kind)
        y += step

    d.fragment(52, 1094, 1310, 1208, 'alt  [công cụ OCR lỗi]')
    m('rt', 'api', 1138, 'lỗi có cấu trúc {success: false, error, inference_status: "error"}',
      dashed=True, color='#B85450')
    m('api', 'u', 1180, 'HTTP 500 / {success: false} → SPA hiện thông báo lỗi; vết lỗi được ghi vào nhật ký ứng dụng',
      dashed=True, color='#B85450')
    return d


# ══════════════════════════════════════════════════ 2.6 Quy trình tổng quát
def f26():
    d = Diagram('fig_2_6_document_workflow',
                'Hình 2.6 – Quy trình xử lý tài liệu tổng quát của hệ thống',
                1300, 1170,
                subtitle='Lưu đồ đường đi thực tế của một yêu cầu (app.py · ocr_service.py · models.py)')

    X = 300
    W = 380
    steps = [
        ('s1',  118, 46, 'Bắt đầu — người dùng chọn tệp trên SPA', 'flow', 'round'),
        ('d1',  186, 62, 'Đã đăng nhập?\n@login_required', 'dec', 'diamond'),
        ('d2',  272, 62, 'Kích thước ≤ MAX_CONTENT_LENGTH?\n(cfg.MAX_UPLOAD_MB = 50)', 'dec', 'diamond'),
        ('d3',  358, 62, 'Phần mở rộng hợp lệ?\n.jpg .jpeg .png .webp .pdf .txt .docx', 'dec', 'diamond'),
        ('s2',  444, 50, 'Làm sạch tên hiển thị · sinh UUID ·\nlưu uploads/{uuid}{suffix}', 'flow', 'round'),
        ('s3',  518, 50, 'Đếm số trang (pypdfium2) · INSERT Document\n(status = "uploaded") · log_activity', 'flow', 'round'),
        ('d4',  592, 62, 'Loại tệp?', 'dec', 'diamond'),
        ('s4',  678, 50, 'Kết xuất trang → ảnh PIL\n(PDF: pdf_page_to_pil, scale = 2.0)', 'flow', 'round'),
        ('s5',  752, 46, 'Xác định công cụ OCR (tham số → bí danh → mặc định)', 'flow', 'round'),
        ('s6',  818, 46, 'Chạy bộ thích nghi của công cụ đã chọn', 'eng', 'round'),
        ('d5',  884, 62, 'OCR thành công?', 'dec', 'diamond'),
        ('s7',  970, 50, 'Hậu xử lý: chuẩn hóa khối · dựng lại thứ tự đọc\n· vẽ ảnh phủ vùng nhận dạng', 'svc', 'round'),
        ('s8', 1044, 46, 'Lưu kết xuất · status = "ocr_done" · log_activity("ocr")', 'data', 'round'),
    ]
    for sid, y, h, lab, key, shape in steps:
        d.node(sid, X, y, W, h, lab, key, shape=shape, fontsize=10.5)

    order = [s[0] for s in steps]
    labels = {('d1', 'd2'): 'có', ('d2', 'd3'): 'có', ('d3', 's2'): 'có',
              ('d4', 's4'): 'ảnh / PDF', ('d5', 's7'): 'có'}
    for a, b in zip(order, order[1:]):
        d.edge(a, b, labels.get((a, b), ''), color='#4B6E9C', srcside='bottom', dstside='top')

    d.node('sTxt', 760, 678, 300, 50, 'Văn bản TXT / DOCX / PDF\n/api/read-text → text_service.read_file()',
           'svc', fontsize=10)
    d.edge('d4', 'sTxt', 'tệp văn bản', color='#82B366', srcside='right', dstside='left')
    d.node('sTxt2', 760, 752, 300, 46, 'save_artifact(kind = "text")', 'data', fontsize=10)
    d.edge('sTxt', 'sTxt2', '', color='#82B366', srcside='bottom', dstside='top')
    d.edge('sTxt2', 's8', '', color='#82B366', dashed=True,
           waypoints=[(1110, 775), (1110, 1067)], srcside='right', dstside='right')

    ERR = 900
    errs = [
        ('e1', 186, '401 / chuyển hướng tới /login'),
        ('e2', 272, '413 {"error": "File too large"}'),
        ('e3', 358, '400 {"error": "Unsupported type"}'),
        ('e5', 884, '500 {"error": "OCR failed (engine)"}\nghi vết lỗi vào nhật ký'),
    ]
    for eid, y, lab in errs:
        d.node(eid, ERR, y, 330, 56, lab, 'err', fontsize=10)
    for eid, dsrc in (('e1', 'd1'), ('e2', 'd2'), ('e3', 'd3'), ('e5', 'd5')):
        d.edge(dsrc, eid, 'không', color='#B85450', srcside='right', dstside='left')

    d.node('own', 44, 460, 230, 76,
           'Mọi yêu cầu sau đó đều kiểm tra lại\nquyền sở hữu: _resolve_owned_file()\n→ 404 không tồn tại,\n'
           '403 không phải chủ sở hữu\n(quản trị viên là ngoại lệ)',
           'err', fontsize=9)
    d.edge('own', 's5', '', color='#B85450', dashed=True, srcside='right', dstside='left')

    d.node('res', 44, 960, 230, 120,
           'Trả kết quả\n• Phản hồi JSON → SPA\n• Thẻ Markdown / Raw / Images / JSON\n'
           '• Tải về .md .txt .json .docx\n• Tùy chọn hiệu chỉnh tiếng Việt\n  (/api/correction/run)',
           'ui', fontsize=9.5)
    d.edge('s8', 'res', '', color='#3F61A8', srcside='left', dstside='right')

    d.node('n1', 44, 1096, 1216, 56,
           'Ghi chú: khâu tiền xử lý chỉ gồm kết xuất ảnh trang và, riêng với công cụ PaddleOCR Modern, '
           'phân loại hướng tài liệu cùng nắn phẳng UVDoc do chính pipeline đó thực hiện. Mã ứng dụng '
           'không có bước nhị phân hóa hay hiệu chỉnh nghiêng riêng.',
           'note', shape='note', fontsize=9.5)
    return d


# ══════════════════════════════════════════════════ 2.7 Lựa chọn công cụ OCR
def f27():
    d = Diagram('fig_2_7_engine_selection',
                'Hình 2.7 – Cơ chế lựa chọn công cụ OCR theo đặc điểm tài liệu',
                1340, 1000,
                subtitle='Cơ chế đúng như đã hiện thực hóa — app.py::_resolve_selected_engine(), '
                         'router.py::normalize_engine_name(), glm_vietocr_adapter.py')

    d.node('warn', 40, 92, 1260, 74,
           'LƯU Ý QUAN TRỌNG — hệ thống KHÔNG hiện thực hóa cơ chế tự động chọn công cụ theo nội dung tài liệu. '
           'Không có đoạn mã nào xét độ phức tạp bố cục, ngôn ngữ hay chất lượng ảnh để chọn công cụ. '
           'Công cụ do người dùng chọn (hộp thả xuống) hoặc do cấu hình quyết định; chỉ tồn tại hai quyết định '
           'theo quy tắc, cả hai đều được thể hiện dưới đây.',
           'todo', shape='note', fontsize=11, bold=True)

    d.node('start', 460, 196, 420, 46, 'Yêu cầu OCR:  {file_id, page, engine?}', 'flow', fontsize=11, bold=True)
    d.node('d1', 440, 268, 460, 68, 'Yêu cầu có kèm giá trị\ntham số "engine" không?', 'dec', shape='diamond', fontsize=10.5)
    d.node('cfg', 40, 278, 340, 62, 'Không → dùng cfg.OCR_ENGINE\n(biến OCR_ENGINE, mặc định "paddle")',
           'flow', fontsize=10)
    d.node('ui', 960, 254, 340, 110,
           'Có → giá trị người dùng chọn trên SPA\n"Recommended"  → glmocr\n"GLM Layout + VietOCR Text"  → glm_vietocr\n'
           '"Vietnamese"  → vietocr\n"Standard"  → paddleocr',
           'ui', fontsize=10)
    d.node('norm', 440, 368, 460, 66,
           'normalize_engine_name(): bảng bí danh\npaddle|auto→paddleocr · modern|ppstructure→paddleocr_modern\n'
           'glm|glm_ocr→glmocr · glm_layout_vietocr→glm_vietocr',
           'eng', fontsize=9.5)
    d.node('bad', 960, 380, 340, 46, 'Bí danh không hợp lệ → ValueError → HTTP 400', 'err', fontsize=10)

    d.node('d2', 420, 466, 500, 76,
           'QUY TẮC 1 (theo loại tệp)\nengine đã chọn == "vietocr"  VÀ  phần mở rộng == ".pdf" ?',
           'dec', shape='diamond', fontsize=10.5)
    d.node('fb', 960, 476, 340, 58,
           'engine thực thi = "paddleocr"\ninference_status = "fallback_to_paddle_for_pdf"',
           'err', fontsize=10)
    d.node('disp', 440, 578, 460, 46, 'engine thực thi → router.get_engine(name).run(image)', 'eng',
           fontsize=11, bold=True)

    eng_y = 660
    labels = [
        ('en1', 'PaddleOCREngine\nPP-OCRv5\n(dòng văn bản + khung bao)'),
        ('en2', 'PaddleOCRModernEngine\nPP-StructureV3 + PP-OCRv6\n(markdown/html/bảng)'),
        ('en3', 'VietOCREngine\nPP-OCRv5 phát hiện dòng +\nVietOCR nhận dạng'),
        ('en4', 'GLMOCREngine\nPP-DocLayoutV3 + mô hình\nGLM-OCR (tiến trình con)'),
        ('en5', 'GLMVietOCREngine\nBố cục GLM + văn bản VietOCR'),
    ]
    xs = row_x(40, 1300, 5, 236)
    for (nid, lab), x in zip(labels, xs):
        d.node(nid, x, eng_y, 236, 84, lab, 'eng', fontsize=9.5)
        d.edge('disp', nid, '', color='#0E8088', srcside='bottom', dstside='top')

    d.node('r2', 40, 782, 620, 128,
           'QUY TẮC 2 (theo từng khối, chỉ bên trong GLMVietOCREngine)\n'
           '• nhãn khối ∈ {table, figure, image, equation, formula, code} → giữ nguyên văn bản của GLM\n'
           '• ngược lại, gán các dòng VietOCR có tâm nằm trong khung bao của khối GLM\n'
           '• kiểm tra hợp lý: nếu độ dài văn bản GLM > 40 ký tự và văn bản VietOCR < 25 % độ dài đó\n'
           '  thì loại bỏ và quay về văn bản GLM (recognition_source = "glm" / "fallback")',
           'corr', fontsize=10)
    d.edge('en5', 'r2', '', color='#9673A6', dashed=True, srcside='bottom', dstside='right')

    d.node('n2', 700, 782, 600, 128,
           'Một số dữ kiện khác từ mã nguồn\n'
           '• paddleocr_modern có đăng ký trong router.py và gọi được qua API, nhưng không xuất hiện\n'
           '  trong hộp thả xuống của SPA (static/index.html).\n'
           '• Công cụ đã dùng được ghi lại theo từng yêu cầu: res["selected_engine"], res["ocr_engine"] và\n'
           '  chuỗi mô tả trong ActivityLog, nhờ đó có thể so sánh nhiều lần xử lý trên cùng một tài liệu.\n'
           '• Lựa chọn thủ công của người dùng được giữ trong suốt phiên (OCRView._sessionEngine).',
           'note', shape='note', fontsize=10)

    d.edge('start', 'd1', '', color='#4B6E9C', srcside='bottom', dstside='top')
    d.edge('d1', 'cfg', 'không', color='#4B6E9C', srcside='left', dstside='right')
    d.edge('d1', 'ui', 'có', color='#4B6E9C', srcside='right', dstside='left')
    d.edge('cfg', 'norm', '', color='#4B6E9C', srcside='bottom', dstside='left')
    d.edge('ui', 'norm', '', color='#4B6E9C', srcside='bottom', dstside='right')
    d.edge('d1', 'norm', '', color='#4B6E9C', srcside='bottom', dstside='top')
    d.edge('norm', 'bad', 'không hợp lệ', color='#B85450', srcside='right', dstside='left')
    d.edge('norm', 'd2', '', color='#4B6E9C', srcside='bottom', dstside='top')
    d.edge('d2', 'fb', 'có', color='#B85450', srcside='right', dstside='left')
    d.edge('fb', 'disp', '', color='#B85450', dashed=True, srcside='bottom', dstside='right')
    d.edge('d2', 'disp', 'không', color='#4B6E9C', srcside='bottom', dstside='top')
    return d


# ══════════════════════════════════════════════════ 2.8 Sơ đồ thực thể
def f28():
    d = Diagram('fig_2_8_erd',
                'Hình 2.8 – Sơ đồ quan hệ thực thể của hệ thống',
                1340, 1010,
                subtitle='Sơ đồ quan hệ thực thể của các mô hình SQLAlchemy trong models.py '
                         '(SQLite, sinh bởi db.create_all())')

    d.table('users', 70, 110, 330, 'users  (người dùng)', [
        ('PK  id : Integer', 'PK'),
        ('username : String(80)', 'UNIQUE'),
        ('email : String(120)', 'UNIQUE'),
        ('password_hash : String(256)', ''),
        ('role : String(20) = "user"', "'admin'|'user'"),
        ('is_active : Boolean = True', ''),
        ('created_at : DateTime (UTC)', ''),
    ], 'api')

    d.table('documents', 500, 110, 360, 'documents  (tài liệu)', [
        ('PK  id : Integer', 'PK'),
        ('FK  user_id → users.id', 'NOT NULL, idx'),
        ('filename : String(255)', 'tên hiển thị'),
        ('file_id : String(36)', 'UNIQUE (uuid4)'),
        ('file_type : String(10)', 'phần mở rộng'),
        ('file_size : BigInteger', ''),
        ('page_count : Integer = 1', ''),
        ('upload_date : DateTime (UTC)', ''),
        ('status : String(20)', 'uploaded|ocr_done'),
    ], 'svc')

    d.table('artifacts', 950, 110, 330, 'document_artifacts  (kết xuất)', [
        ('PK  id : Integer', 'PK'),
        ('FK  document_id → documents.id', 'ON DELETE CASCADE'),
        ('kind : String(20)', 'xem chú giải'),
        ('content : Text', ''),
        ('meta : String(200)', 'có thể NULL'),
        ('created_at : DateTime', ''),
        ('updated_at : DateTime', 'onupdate'),
        ('UNIQUE (document_id, kind)', 'uq_artifact_doc_kind'),
    ], 'eng')

    d.table('logs', 70, 420, 330, 'activity_logs  (nhật ký hoạt động)', [
        ('PK  id : Integer', 'PK'),
        ('FK  user_id → users.id', 'ON DELETE SET NULL'),
        ('action : String(50)', 'NOT NULL'),
        ('detail : String(500)', 'có thể NULL'),
        ('ip_address : String(45)', 'request.remote_addr'),
        ('created_at : DateTime (UTC)', ''),
    ], 'data')

    d.edge('users', 'documents', '1 ── 0..*  sở hữu', color='#3F61A8', srcside='right', dstside='left')
    d.edge('documents', 'artifacts', '1 ── 0..*  sinh ra\n(xóa theo tài liệu)', color='#0E8088',
           srcside='right', dstside='left')
    d.edge('users', 'logs', '1 ── 0..*  thực hiện\n(user_id có thể NULL)', color='#5A5A5A',
           srcside='bottom', dstside='top')

    d.table('kinds', 500, 420, 360, 'Các giá trị document_artifacts.kind mà mã nguồn ghi ra', [
        ("text  —  văn bản TXT / DOCX / PDF (/api/read-text)", ''),
        ("ocr  —  văn bản OCR đã làm phẳng", ''),
        ("ocr_layout  —  khung bao, độ tin cậy, thời gian", 'mọi công cụ'),
        ("ocr_json  —  vùng nhận dạng theo từng trang", 'mọi công cụ'),
        ("ocr_markdown  —  bản dựng lại dạng Markdown", 'GLM / Modern'),
        ("ocr_html  —  bản dựng lại dạng HTML", 'Modern'),
        ("ocr_tables  —  bảng phát hiện được, dạng HTML", 'GLM / Modern'),
        ("ocr_blocks  —  khối bố cục (nhãn/bbox/thứ tự)", 'GLM / Modern'),
        ("ocr_images  —  ảnh phủ vùng + ảnh cắt (base64)", 'mọi công cụ'),
        ("corrected_json / corrected_md / corrected_meta", 'correction_bp'),
    ], 'note', rowh=20)

    d.container('legacy', 950, 420, 330, 300,
                'Đã khai báo, không dùng ở bản này', 'ext', header=32)
    for i, (nid, lab) in enumerate([
            ('t1', 'chat_conversations'), ('t2', 'chat_messages'),
            ('t3', 'agent_conversations'), ('t4', 'agent_messages'),
            ('t5', 'agent_artifacts')]):
        d.node(nid, 972, 466 + i * 48, 286, 38, lab, 'ext', parent='legacy', fontsize=10.5)

    d.node('n1', 70, 762, 1210, 96,
           'Ghi chú đối chiếu — phần thuyết minh đề xuất các thực thể User, Role, Document, DocumentPage, OCRJob, '
           'OCRResult, OCRConfiguration, ActivityLog và ErrorLog. Mã nguồn chỉ có bốn bảng vẽ ở trên: không có '
           'bảng Role (role là một cột chuỗi trong bảng users), không có DocumentPage, OCRJob, OCRResult, '
           'OCRConfiguration hay ErrorLog. Kết quả OCR theo từng trang được lưu dưới dạng JSON trong '
           'document_artifacts, tham số công cụ OCR nằm trong biến môi trường do config.py đọc, còn lỗi được ghi '
           'vào nhật ký ứng dụng và bảng activity_logs.',
           'note', shape='note', fontsize=10)
    d.node('n2', 70, 878, 1210, 76,
           'Năm bảng bên phải được khai báo trong models.py nên vẫn được db.create_all() tạo ra, nhưng không tuyến '
           'nào của phiên bản này đọc hay ghi chúng — các blueprint trò chuyện / RAG / tác tử đã bị gỡ bỏ (xem chú '
           'thích trong app.py::_persist_and_index). Chúng được vẽ để mô tả đầy đủ lược đồ vật lý và không được '
           'trình bày như chức năng đang hoạt động.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 2.9 Điều hướng giao diện
def f29():
    d = Diagram('fig_2_9_navigation',
                'Hình 2.9 – Sơ đồ điều hướng chính của giao diện người dùng',
                1340, 980,
                subtitle='Dựng lại từ các tuyến Flask và bộ định tuyến theo hash trong static/app.js '
                         '(Router.register / Router.goto / Router._render)')

    d.node('login', 60, 250, 230, 74, 'Trang đăng nhập\nGET / POST  /login', 'ui', fontsize=11, bold=True)
    d.node('logout', 60, 700, 230, 64, 'Đăng xuất\nGET /logout → /login', 'ui', fontsize=10.5)

    d.container('spa', 330, 96, 640, 466,
                'Ứng dụng một trang (SPA)  —  GET /   (static/index.html)', 'ui', header=36)
    d.node('home', 356, 150, 250, 60, '#home\nTrang chính (thẻ chức năng)', 'ui', parent='spa', fontsize=11, bold=True)
    d.node('ocr', 356, 250, 250, 64, '#ocr\nMàn hình làm việc OCR', 'ui', parent='spa', fontsize=11, bold=True)
    d.node('docs', 356, 360, 250, 64, '#documents\nThư viện tài liệu', 'ui', parent='spa', fontsize=11, bold=True)
    d.node('tabs', 640, 250, 300, 64,
           'Thẻ kết quả — hiện sau khi chạy OCR\nMarkdown · Raw · Images · JSON\n'
           '(kèm tải về .md .txt .json .docx)', 'ui', parent='spa', fontsize=9)
    d.node('deep', 640, 360, 300, 64, '#ocr/<file_id>  (liên kết sâu)\nmở lại tài liệu và khôi phục\n'
                                      'các kết xuất đã lưu',
           'ui', parent='spa', fontsize=9.5)
    d.node('nav', 356, 470, 584, 64,
           'Thanh điều hướng thường trực\nTrang chính · OCR · Tài liệu · [Quản trị] · ngôn ngữ · Đăng xuất',
           'ui', parent='spa', fontsize=10)

    d.container('admin', 330, 700, 640, 220,
                'Trang quản trị  —  dựng phía máy chủ (Jinja), chỉ dành cho role = "admin"', 'api', header=36)
    d.node('adash', 356, 754, 280, 54, 'GET /admin/\nTổng quan + hoạt động gần đây', 'api', parent='admin', fontsize=10)
    d.node('alogs', 660, 754, 280, 54, 'GET /admin/logs\nNhật ký hoạt động (bộ lọc)', 'api', parent='admin', fontsize=10)
    d.node('ausers', 356, 828, 280, 54, 'GET /admin/users\nQuản lý người dùng', 'api', parent='admin', fontsize=10)
    d.node('afiles', 660, 828, 280, 54, 'GET /admin/files\nToàn bộ tài liệu', 'api', parent='admin', fontsize=10)

    d.node('corr', 1060, 250, 270, 100,
           'Trang hiệu chỉnh tiếng Việt\nGET /correction\n(trang riêng, chỉ vào được bằng URL,\n'
           'có liên kết "← Back to SmartDocs")',
           'corr', fontsize=10)
    d.node('f403', 1060, 754, 270, 74, 'Trang 403\ntemplates/403.html\n(không phải quản trị viên)', 'err', fontsize=10)

    d.edge('login', 'home', 'đăng nhập thành công\n→ chuyển hướng tới /', color='#3F61A8',
           srcside='right', dstside='left', waypoints=[(312, 287), (312, 180)])
    d.edge('home', 'ocr', '', color='#3F61A8', srcside='bottom', dstside='top')
    d.edge('home', 'docs', '', color='#3F61A8',
           srcside='left', dstside='left', waypoints=[(344, 180), (344, 392)])
    d.edge('ocr', 'tabs', '', color='#3F61A8', srcside='right', dstside='left')
    d.edge('docs', 'deep', '', color='#3F61A8', srcside='right', dstside='left')
    d.edge('nav', 'adash', 'Liên kết Quản trị — chỉ hiện khi role = "admin"', color='#9673A6',
           srcside='bottom', dstside='top', waypoints=[(648, 630), (496, 630)])
    d.edge('adash', 'ausers', '', color='#9673A6', arrow='none', srcside='bottom', dstside='top')
    d.edge('adash', 'alogs', '', color='#9673A6', arrow='none', srcside='right', dstside='left')
    d.edge('ausers', 'afiles', '', color='#9673A6', arrow='none', srcside='right', dstside='left')
    d.edge('admin', 'home', '"← Ứng dụng"  →  /#home', color='#9673A6', dashed=True,
           srcside='left', dstside='top', waypoints=[(306, 810), (306, 126), (481, 126)])
    d.edge('nav', 'logout', 'Đăng xuất', color='#3F61A8', dashed=True,
           srcside='left', dstside='right', waypoints=[(322, 502), (322, 732)])
    d.edge('corr', 'spa', 'chỉ qua URL', color='#9673A6', arrow='both',
           srcside='left', dstside='right')
    d.edge('f403', 'admin', 'abort(403)', color='#B85450', dashed=True,
           srcside='left', dstside='right')

    d.node('n1', 60, 900, 1270, 56,
           'Trang /correction chỉ truy cập được bằng URL — thanh điều hướng của SPA (static/index.html) không có '
           'liên kết tới nó. Nút Back / Forward của trình duyệt hoạt động tự nhiên vì location.hash là nguồn '
           'trạng thái duy nhất của SPA; liên kết sâu duy nhất là #ocr/<file_id>.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 2.10 Các lớp bảo vệ dữ liệu
def f210():
    d = Diagram('fig_2_10_data_protection',
                'Hình 2.10 – Mô hình các lớp bảo vệ dữ liệu của hệ thống',
                1340, 1040,
                subtitle='Các lớp bảo vệ nhiều tầng — chỉ liệt kê cơ chế thực sự đã hiện thực hóa; '
                         'mỗi lớp ghi rõ tệp nguồn tương ứng')

    layers = [
        ('L1', 'Lớp 1 · Bảo vệ phiên làm việc và đường truyền',
         'SECRET_KEY (biến môi trường hoặc secrets.token_hex(32)) · SESSION_COOKIE_HTTPONLY = True · '
         'SAMESITE = "Lax" · SESSION_COOKIE_SECURE phụ thuộc cfg.SESSION_COOKIE_SECURE · cookie ghi nhớ đăng nhập '
         'dùng đúng các cờ trên   [app.py, config.py]', 'ui'),
        ('L2', 'Lớp 2 · Xác thực người dùng',
         'Phiên làm việc Flask-Login · werkzeug generate_password_hash / check_password_hash · kiểm tra is_active '
         'khi đăng nhập · @login_required trên mọi trang và mọi tuyến API · unauthorized_handler trả 401 JSON cho '
         '/api/* và chuyển hướng trình duyệt tới /login   [auth.py, app.py, models.py]', 'api'),
        ('L3', 'Lớp 3 · Phân quyền theo vai trò',
         'users.role ∈ {"admin", "user"} · decorator admin_required trong auth.py và admin_bp.py · abort(403) kèm '
         'mẫu 403 riêng · quản trị viên không thể tự khóa hoặc tự xóa tài khoản của mình   [auth.py, admin_bp.py]', 'svc'),
        ('L4', 'Lớp 4 · Kiểm soát truy cập tài liệu',
         '_resolve_owned_file() tra file_id qua bảng Document và từ chối tài liệu của người khác (403) hoặc mã '
         'không tồn tại (404); cùng phép kiểm tra chủ sở hữu-hoặc-quản trị được lặp lại ở mọi tuyến '
         '/api/documents/<id> và ở các tuyến hiệu chỉnh   [app.py, correction_bp.py]', 'eng'),
        ('L5', 'Lớp 5 · Kiểm tra tệp tải lên và an toàn đường dẫn',
         'MAX_CONTENT_LENGTH (MAX_UPLOAD_MB, mặc định 50 MB) kèm bộ xử lý 413 trả JSON · _safe_basename() loại bỏ '
         'thành phần thư mục và ký tự điều khiển nhưng giữ nguyên Unicode tiếng Việt · danh sách phần mở rộng cho '
         'phép · tên tệp trên đĩa luôn là UUID do máy chủ sinh, không bao giờ lấy từ người dùng · không bao giờ '
         'dò tệp bằng file_id thô nên chuỗi "../" không khớp tài liệu nào   [app.py]', 'proc'),
        ('L6', 'Lớp 6 · Cách ly tiến trình và mô hình',
         'Công cụ GLM-OCR chạy trong tiến trình con với môi trường ảo riêng; môi trường của tiến trình con bị gỡ '
         'HF_HOME / HF_HUB_CACHE / TRANSFORMERS_CACHE và ép HF_HUB_OFFLINE=1 · thời gian chạy bị giới hạn bởi '
         'GLM_TIMEOUT và một phép kiểm tra kết nối TCP · khi lỗi thì trả về lỗi có cấu trúc thay vì ném ngoại lệ   '
         '[glm_adapter.py, config.py]', 'corr'),
        ('L7', 'Lớp 7 · Làm sạch đầu ra và giữ dữ liệu tại chỗ',
         'sanitizeHtml() loại bỏ script/style/iframe/object/embed/link/meta cùng thuộc tính on* và javascript: '
         'trước khi hiển thị HTML do công cụ OCR sinh ra · markdown_normalize sửa các dấu $$ không khớp cặp · '
         'OFFLINE=1 chặn tải mô hình và mlx_config.yaml tắt nhánh đám mây MaaS, nhờ đó nội dung tài liệu không rời '
         'khỏi máy chủ   [static/app.js, services/markdown_normalize.py, mlx_config.yaml]', 'data'),
        ('L8', 'Lớp 8 · Nhật ký và giám sát',
         'Bảng activity_logs ghi (user_id, action, detail, ip_address, created_at) cho các hành động login, logout, '
         'upload, ocr, delete_doc, vi_correct và mọi thao tác quản trị · log_activity() không bao giờ ném ngoại lệ · '
         'trang xem nhật ký của quản trị viên lọc theo hành động, người dùng và từ khóa   '
         '[models.py, app.py, admin_bp.py]', 'note'),
    ]
    y = 92
    for lid, title, body, key in layers:
        d.node(lid, 60, y, 1220, 84, title + '\n' + body, key, shape='round', fontsize=10)
        y += 96

    d.node('core', 400, 872, 540, 72,
           'DỮ LIỆU CẦN BẢO VỆ\nTệp gốc đã tải lên (uploads/) · kết xuất OCR và bản hiệu chỉnh '
           '(document_artifacts) · tài khoản người dùng (users) · nhật ký hoạt động (activity_logs)',
           'err', shape='round', fontsize=11, bold=True)
    d.edge('L8', 'core', '', color='#B85450', srcside='bottom', dstside='top')

    d.node('n1', 60, 960, 1220, 62,
           'Chưa hiện thực hóa trong kho mã nguồn nên cố ý không đưa vào hình: kết thúc TLS, mã hóa dữ liệu khi lưu '
           'trữ, token CSRF, giới hạn tần suất truy cập, tự động sao lưu / phục hồi cơ sở dữ liệu và nhà cung cấp '
           'định danh bên ngoài. SESSION_COOKIE_SECURE chỉ đánh dấu cookie — bản thân TLS phải do môi trường triển '
           'khai cung cấp.',
           'todo', shape='note', fontsize=10)
    return d


if __name__ == '__main__':
    for fn in (f21, f22, f23, f24, f25, f26, f27, f28, f29, f210):
        write(fn())
