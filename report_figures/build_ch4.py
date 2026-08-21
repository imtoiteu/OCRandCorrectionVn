#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hình chương 4 (4.1 - 4.5).

4.4 và 4.5 được dựng dưới dạng *khung trình bày / quy trình đo* trung thực: kho mã
nguồn có tài liệu mẫu và kết quả tham chiếu, nhưng KHÔNG có dữ liệu chuẩn, không có
phần tính CER/WER và không có số đo thời gian nào. Không bịa bất kỳ số liệu nào.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram_engine import Diagram, write, set_out, row_x

set_out(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chapter4'))


# ══════════════════════════════════════════════════ 4.1 Bố trí môi trường thử nghiệm
def f41():
    d = Diagram('fig_4_1_test_environment',
                'Hình 4.1 – Bố trí các thành phần trong môi trường thử nghiệm',
                1400, 1020,
                subtitle='Sơ đồ bố trí và những điểm mà hệ thống sinh ra dữ liệu quan sát được '
                         'trong một lần chạy thử')

    d.container('mach', 40, 92, 900, 660,
                'Máy thử nghiệm  —  macOS Apple Silicon · Python 3.10  (RUN_MACOS.md)', 'proc', header=38)

    d.node('br', 64, 150, 400, 84,
           'Máy khách thử nghiệm — trình duyệt web\nhttp://localhost:5001\n'
           'tài khoản khởi tạo sẵn: user / user123 · admin / admin123',
           'ui', parent='mach', fontsize=10)
    d.node('flask', 64, 264, 852, 76,
           'Ứng dụng Flask SmartDocs  —  cổng 5001  (một tiến trình, máy chủ phát triển đa luồng)\n'
           'xác thực · kiểm tra quyền sở hữu · tuyến OCR · thư viện tài liệu · trang quản trị · API hiệu chỉnh',
           'api', parent='mach', fontsize=10.5, bold=True)
    d.node('eng', 64, 370, 412, 92,
           'Công cụ OCR chạy trong tiến trình\nPaddleOCR PP-OCRv5\nPP-StructureV3 + PP-OCRv6_medium\nVietOCR vgg_transformer',
           'eng', parent='mach', fontsize=10)
    d.node('glm', 504, 370, 412, 92,
           'Nhánh GLM-OCR (tùy chọn)\nglmocr CLI trong .venv-sdk (mỗi yêu cầu)\n→ máy chủ MLX :8080 trong .venv-mlx\n'
           'mô hình mlx-community/GLM-OCR-bf16',
           'proc', parent='mach', fontsize=10)
    d.node('db', 64, 492, 264, 88, 'SQLite  paddleocr.db\nusers · documents\ndocument_artifacts\nactivity_logs',
           'data', parent='mach', shape='cyl', fontsize=9.5)
    d.node('up', 348, 492, 264, 88, 'uploads/\ntài liệu gốc\n+ tệp .png tạm của trang\nMAX_UPLOAD_MB = 50',
           'data', parent='mach', fontsize=9.5)
    d.node('mm', 632, 492, 284, 88, 'models/ · bộ nhớ đệm HF · PaddleX\ntrọng số VietOCR\ncờ OFFLINE quyết định việc tải về',
           'data', parent='mach', fontsize=9.5)
    d.node('smp', 64, 608, 852, 116,
           'Tài liệu thử nghiệm đã có sẵn trong kho mã nguồn\n'
           'glm-ocr-server/examples/source/     page.png · paper.png · table.png · seal.png · code.png · handwritten.png · GLM-4.5V.pdf\n'
           'glm-ocr-server/examples/result/<tên>/     <tên>.json · <tên>.md · layout_vis/ · imgs/   (kết quả tham chiếu của GLM-OCR)\n'
           'glm-ocr-server/ui/_runs/<id>/     input/ · output/ · tệp .zip kết quả   (các lần chạy GLM-OCR đã ghi lại)\n'
           'vi-correction-prototype/tests/correction/sample_receipt_glm.json   (JSON OCR có cấu trúc cho pipeline hiệu chỉnh)',
           'svc', parent='mach', fontsize=9.5)

    d.node('lan', 980, 150, 380, 92,
           'Máy khách thứ hai (tùy chọn)\nMột máy khác trong cùng mạng nội bộ;\nkết nối được vì cfg.HOST = 0.0.0.0.\n'
           'Mã nguồn không có chế độ máy chủ từ xa —\ntrình duyệt là máy khách từ xa duy nhất.',
           'ui', fontsize=9.5)

    d.container('obs', 980, 274, 380, 478,
                'Dữ liệu quan sát do hệ thống sinh ra', 'note', header=36)
    OBS = [
        ('o1', 322, 74, 'Thời gian xử lý từng trang\nelapsed_ms của bộ thích nghi → trường\nprocessing_time_ms trong phản hồi'),
        ('o2', 406, 74, 'Công cụ thực sự đã dùng\nselected_engine · ocr_engine\n(ghi theo từng trang trong phản hồi)'),
        ('o3', 490, 74, 'inference_status\nok | error |\nfallback_to_paddle_for_pdf'),
        ('o4', 574, 84, 'Bản ghi activity_logs (action = ocr)\ntrường detail chứa chế độ, công cụ,\nprocessing_time_ms, inference_status,\nsố trang — xem tại /admin/logs'),
        ('o5', 668, 70, 'document_artifacts\nkết quả từng lần chạy được lưu lại,\nso sánh được giữa các công cụ'),
    ]
    for nid, y, h, lab in OBS:
        d.node(nid, 1002, y, 336, h, lab, 'note', parent='obs', fontsize=9)

    d.edge('br', 'flask', 'HTTP', color='#3F61A8', srcside='bottom', dstside='top')
    d.edge('lan', 'flask', 'HTTP qua mạng nội bộ', color='#3F61A8',
           srcside='bottom', dstside='right', waypoints=[(1170, 256), (950, 256), (950, 300)])
    d.edge('flask', 'eng', 'trong tiến trình', color='#0E8088', srcside='bottom', dstside='top',
           waypoints=[(490, 352), (270, 352)])
    d.edge('flask', 'glm', 'tiến trình con + HTTP :8080', color='#D79B00', srcside='bottom', dstside='top',
           waypoints=[(490, 352), (710, 352)])
    d.edge('eng', 'db', '', color='#5A5A5A', dashed=True, srcside='bottom', dstside='top')
    d.edge('eng', 'up', '', color='#5A5A5A', dashed=True, srcside='bottom', dstside='top')
    d.edge('glm', 'mm', '', color='#5A5A5A', dashed=True, srcside='bottom', dstside='top')
    d.edge('flask', 'obs', 'ghi', color='#D6B656', srcside='right', dstside='left',
           waypoints=[(964, 302), (964, 513)])

    d.node('n1', 40, 776, 1320, 62,
           'Toàn bộ thành phần trong hình chạy trên một máy. Trình duyệt không bao giờ liên hệ trực tiếp với máy chủ '
           'mô hình MLX hay cơ sở dữ liệu: điểm truy cập mạng duy nhất mở cho người kiểm thử là Flask ở cổng 5001, '
           'còn cổng 8080 chỉ được tiến trình con glmocr gọi tới qua localhost.',
           'note', shape='note', fontsize=10)
    d.node('n2', 40, 852, 1320, 76,
           'Hạn chế của môi trường thử nghiệm cần nêu trong báo cáo: ứng dụng chạy trên máy chủ phát triển của Flask '
           '(một tiến trình, đa luồng), cơ sở dữ liệu là một tệp SQLite cục bộ, và công cụ GLM-OCR chỉ dùng được '
           'trên Apple Silicon khi đã cài đủ hai môi trường ảo và máy chủ MLX đang chạy. Trên máy không có các điều '
           'kiện đó, hộp chọn công cụ vẫn hiện "Recommended" nhưng yêu cầu sẽ trả về lỗi có cấu trúc thay vì kết quả.',
           'note', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 4.2 Chuẩn bị dữ liệu và đánh giá
def f42():
    d = Diagram('fig_4_2_evaluation_procedure',
                'Hình 4.2 – Quy trình chuẩn bị dữ liệu và đánh giá kết quả OCR',
                1420, 1120,
                subtitle='Khối tô màu là bước đã có mã hoặc dữ liệu trong kho; '
                         'khối viền đỏ nền trắng là bước CHƯA hiện thực hóa, phải làm thủ công')

    d.node('leg', 40, 92, 1340, 44,
           'CHÚ GIẢI      khối tô màu = đã hiện thực hóa trong kho mã nguồn (có ghi tệp chịu trách nhiệm)            '
           'khối viền đỏ nền trắng = chưa có mã, phải thực hiện thủ công',
           'note', shape='note', fontsize=10.5, bold=True)

    d.container('prep', 40, 156, 660, 476, 'Chuẩn bị dữ liệu', 'svc', header=34)
    P = [
        ('p1', 204, 62, 'Chọn tài liệu để đánh giá\nMẫu có sẵn trong kho mã nguồn:\n'
                        'examples/source/*.png · GLM-4.5V.pdf'),
        ('p2', 280, 62, 'Phân nhóm theo loại tài liệu\nvăn bản in · bài báo khoa học · bảng biểu ·\ncon dấu · mã nguồn · chữ viết tay'),
        ('p3', 356, 58, 'Tải từng tài liệu lên qua SPA\nPOST /api/upload → bản ghi Document +\nuploads/{uuid}{suffix}'),
        ('p4', 428, 62, 'Chạy OCR lần lượt bằng từng công cụ trên cùng tệp\ntham số engine của /api/ocr/page và\n/api/ocr/all (hộp chọn hoặc API)'),
        ('p5', 504, 62, 'Kết quả được lưu tự động\ndocument_artifacts: ocr, ocr_json,\nocr_markdown, ocr_layout, ocr_images'),
        ('p6', 580, 44, 'Tùy chọn: chạy hiệu chỉnh tiếng Việt\nPOST /api/correction/run → corrected_json'),
    ]
    for nid, y, h, lab in P:
        d.node(nid, 62, y, 616, h, lab, 'svc', parent='prep', fontsize=9.5)
    for a, b in zip([x[0] for x in P], [x[0] for x in P][1:]):
        d.edge(a, b, '', color='#82B366', srcside='bottom', dstside='top')

    d.container('meas', 740, 156, 640, 476, 'Đo đạc và chấm điểm', 'eng', header=34)
    d.node('m1', 762, 204, 596, 68,
           'TỰ ĐỘNG — thời gian xử lý\nMọi bộ thích nghi đều ghi elapsed_ms; app.py chép sang processing_time_ms và\n'
           'ghi vào chuỗi detail của activity_logs cho từng trang cũng như cho lần OCR toàn bộ.',
           'eng', parent='meas', fontsize=9.5)
    d.node('m2', 762, 284, 596, 68,
           'TỰ ĐỘNG — thông tin kèm kết quả nhận dạng\nsố vùng, độ tin cậy trung bình (chỉ với công cụ PaddleOCR), số trang,\n'
           'inference_status và công cụ thực sự đã dùng đều trả về cùng mỗi phản hồi.',
           'eng', parent='meas', fontsize=9.5)
    d.node('m3', 762, 364, 596, 76,
           'TỰ ĐỘNG — chỉ báo chất lượng hiệu chỉnh (vi_correction)\ncounts {blocks, units, sent, changed, skipped} · timing {provider_seconds,\n'
           'total_seconds} · báo cáo kiểm tra (giữ nguyên cấu trúc, placeholder còn nguyên)\n'
           'kèm scripts/bench_spans.py đo độ trễ theo từng đoạn trong bản thử nghiệm.',
           'corr', parent='meas', fontsize=9.5)
    d.node('m4', 762, 452, 596, 62,
           'THỦ CÔNG — tạo dữ liệu chuẩn\nKho mã nguồn không có bản gõ lại, công cụ gán nhãn hay tệp văn bản tham\nchiếu nào cho tập tài liệu tiếng Việt.',
           'todo', parent='meas', fontsize=9.5)
    d.node('m5', 762, 526, 596, 46,
           'THỦ CÔNG — chuẩn hóa văn bản trước khi chấm điểm\nKho mã nguồn không có hàm chuẩn hóa phục vụ đánh giá.',
           'todo', parent='meas', fontsize=9.5)
    d.node('m6', 762, 584, 596, 40,
           'THỦ CÔNG — tính CER và WER (chưa có mã: không có jiwer, không có hàm khoảng cách soạn thảo)',
           'todo', parent='meas', fontsize=9.5)
    for a, b in (('m1', 'm2'), ('m2', 'm3'), ('m3', 'm4'), ('m4', 'm5'), ('m5', 'm6')):
        d.edge(a, b, '', color='#0E8088', srcside='bottom', dstside='top')
    d.edge('p6', 'm1', '', color='#82B366', srcside='right', dstside='left',
           waypoints=[(716, 602), (716, 238)])

    d.container('agg', 40, 668, 1340, 218, 'Tổng hợp và báo cáo', 'note', header=34)
    d.node('g1', 62, 716, 420, 68,
           'Kết xuất dữ liệu thô\n/admin/logs (activity_logs, lọc được) ·\n/api/documents/<id>/text (mọi kết xuất) ·\n'
           'tải về .md / .txt / .json / .docx',
           'svc', parent='agg', fontsize=9.5)
    d.node('g2', 502, 716, 420, 68,
           'THỦ CÔNG — lập bảng so sánh\nĐộ chính xác theo nhóm tài liệu và theo công cụ;\nkho mã nguồn không có kịch bản tổng hợp.',
           'todo', parent='agg', fontsize=9.5)
    d.node('g3', 942, 716, 416, 68,
           'THỦ CÔNG — dựng biểu đồ thời gian (Hình 4.5)\nTách riêng thời gian nạp mô hình lần đầu khỏi thời\ngian xử lý ở trạng thái ổn định như báo cáo yêu cầu.',
           'todo', parent='agg', fontsize=9.5)
    d.node('g4', 62, 800, 1296, 68,
           'Các kiểm thử hồi quy / kiểm tra nhanh thực sự có trong kho\n'
           'glm-ocr-ui: test_layout.py · test_regression.py (dựng lại thứ tự đọc) · test_vietocr.py · '
           'test_refactored_ocr.py (điều phối công cụ) · test_markdown_normalize.py (pytest)\n'
           'glm-ocr-server: glmocr/tests/test_unit.py · test_integration.py (pytest, có conftest.py)   —   '
           'không tệp nào trong số đó đo độ chính xác OCR; chúng kiểm tra hành vi chứ không kiểm tra chất lượng.',
           'ext', parent='agg', fontsize=9.5)
    d.edge('g1', 'g2', '', color='#5A5A5A', srcside='right', dstside='left')
    d.edge('g2', 'g3', '', color='#5A5A5A', srcside='right', dstside='left')
    d.edge('m6', 'g2', '', color='#B85450', dashed=True, srcside='bottom', dstside='top')

    d.node('warn', 40, 916, 1340, 96,
           'CẢNH BÁO VỀ TÍNH CHÍNH XÁC — kho mã nguồn không có phần đánh giá độ chính xác OCR. Không có tập dữ liệu '
           'chuẩn, không có phần tính CER/WER hay độ chính xác bố cục (tìm trên toàn kho các từ khóa CER, WER, jiwer, '
           'levenshtein và edit_distance đều không ra kết quả nào ngoài các tệp từ vựng của mô hình), và không có kết '
           'quả đo nào được lưu lại. tools/eval_model.py và tools/ab_harness.py đánh giá các mô hình ngôn ngữ Qwen '
           'dùng cho trò chuyện / viết lại chứ không đánh giá OCR, và chúng còn nạp những dịch vụ không còn tồn tại '
           'trong phiên bản này. Mọi khối viền đỏ đều phải làm thủ công trước khi chương 4 có thể nêu số liệu.',
           'todo', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 4.3 Các bước kiểm thử chức năng
def f43():
    d = Diagram('fig_4_3_functional_test_steps',
                'Hình 4.3 – Một số bước kiểm thử chức năng xử lý tài liệu',
                1420, 1090,
                subtitle='Quy trình kiểm thử chức năng rút ra từ luồng xử lý đã hiện thực hóa; mỗi bước ghi rõ '
                         'lời gọi API và dữ liệu quan sát được mà hệ thống sinh ra')

    steps = [
        ('s1', 'a)  Đăng nhập',
         'Mở http://localhost:5001 → mọi yêu cầu chưa xác thực\nđều được trả về biểu mẫu đăng nhập.\n'
         'POST /login  (user / user123)',
         'Quan sát: chuyển hướng về /, thanh điều hướng hiện tên\nvà vai trò người dùng; activity_logs thêm action = "login".'),
        ('s2', 'b)  Tải tài liệu lên',
         'Màn hình OCR → vùng kéo thả hoặc hộp chọn tệp.\nPOST /api/upload  (multipart)',
         'Quan sát: mã 200 kèm file_id, page_count, is_pdf;\ntệp xuất hiện trong uploads/ dạng {uuid}{suffix};\n'
         'bản ghi Document có status = "uploaded"; nhật ký action = "upload".'),
        ('s3', 'c)  Xem trước và chuyển trang',
         'POST /api/ocr/page với preview_only = true\n(nút chuyển trang khi tài liệu là PDF)',
         'Quan sát: page_image_b64 được vẽ lên canvas,\nresults = [], chưa chạy OCR, chưa ghi kết xuất nào.'),
        ('s4', 'd)  Lựa chọn công cụ OCR',
         'Hộp thả xuống: Recommended (glmocr) ·\nGLM Layout + VietOCR Text · Vietnamese (vietocr) ·\nStandard (paddleocr)',
         'Quan sát: giá trị đã chọn được gửi trong trường "engine"\nvà trả về trong selected_engine;\n'
         'lựa chọn được giữ trong suốt phiên làm việc.'),
        ('s5', 'e)  Chạy nhận dạng và theo dõi trạng thái',
         'POST /api/ocr/page  (Run OCR)  hoặc\nPOST /api/ocr/all  (OCR All) · nút Stop hủy lời gọi\nfetch ở phía trình duyệt',
         'Quan sát: processing_time_ms và inference_status theo từng\ntrang; dải thống kê hiện số vùng, độ tin cậy trung bình,\n'
         'thời gian và số trang; nhật ký action = "ocr" kèm chi tiết.'),
        ('s6', 'f)  Kiểm tra các dạng biểu diễn kết quả',
         'Các thẻ kết quả: Markdown · Raw · Images · JSON;\nbấm vào một vùng sẽ làm nổi bật khung bao\ntương ứng trên ảnh trang',
         'Quan sát: các kết xuất ocr, ocr_layout, ocr_json,\nocr_markdown, ocr_images được ghi vào document_artifacts\n'
         '(mỗi loại một bản ghi, ghi đè khi chạy lại).'),
        ('s7', 'g)  Kết xuất kết quả',
         'Tải về .md / .txt / .json;\nPOST /api/ocr/export-docx  (pandoc)',
         'Quan sát: tệp được tải xuống; nếu thiếu pandoc thì trả về\n501 kèm thông báo giải thích thay vì báo lỗi chung.'),
        ('s8', 'h)  Mở lại từ thư viện tài liệu',
         '#documents → mở một tài liệu →\n#ocr/<file_id> → GET /api/documents/<id>/text\nvà /ocr-images',
         'Quan sát: kết quả OCR trước đó, khung bao và ảnh minh họa\nđược khôi phục mà không phải chạy lại OCR.'),
        ('s9', 'i)  Tùy chọn — hiệu chỉnh tiếng Việt',
         'GET /correction → chọn tài liệu đã có ocr_json →\nPOST /api/correction/run → POST /api/correction/save',
         'Quan sát: số liệu đếm, thời gian và báo cáo kiểm tra;\ncorrected_json / corrected_md được lưu song song, không\n'
         'bao giờ ghi đè kết xuất OCR gốc.'),
        ('s10', 'j)  Kiểm tra chức năng quản trị',
         '/admin/ tổng quan · /admin/users · /admin/logs ·\n/admin/files   (admin / admin123)',
         'Quan sát: mọi thao tác ở trên đều xuất hiện trong danh sách\nnhật ký; tài khoản thường truy cập các URL đó sẽ nhận 403.'),
    ]
    d.node('h1', 40, 100, 300, 38, 'Bước kiểm thử', 'flow', shape='rect', fontsize=11, bold=True)
    d.node('h2', 360, 100, 480, 38, 'Thao tác và lời gọi API được kiểm tra', 'api', shape='rect',
           fontsize=11, bold=True)
    d.node('h3', 860, 100, 520, 38, 'Dữ liệu quan sát do hệ thống sinh ra', 'data', shape='rect',
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
           'Ghi chú về ảnh chụp: phần thuyết minh trình bày Hình 4.3 dưới dạng các ảnh a) tải tệp, b) lựa chọn công '
           'cụ OCR, c) kết quả nhận dạng, d) lịch sử xử lý — xem MANUAL_COMPLETION.md.',
           'todo', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 4.4 Khung trình bày kết quả
def f44():
    d = Diagram('fig_4_4_result_examples_template',
                'Hình 4.4 – Minh họa kết quả OCR trên một số nhóm tài liệu  (khung trình bày)',
                1400, 900,
                subtitle='KHUNG TRÌNH BÀY — không tái hiện bất kỳ kết quả OCR nào ở đây. Các ô chỉ nêu tên tệp mẫu '
                         'đã có trong kho mã nguồn và vị trí cần chèn ảnh chụp.')

    d.node('warn', 40, 92, 1320, 58,
           'Hình này không thể sinh ra từ mã nguồn vì nó trình bày kết quả nhận dạng trên tài liệu thật. '
           'Khung dưới đây liệt kê tài liệu mẫu đã có sẵn trong kho để việc chụp ảnh được nhất quán. '
           'Không dùng lại các kết quả tham chiếu đã lưu như thể chúng là kết quả do hệ thống này chạy ra, '
           'nếu chưa chạy lại.',
           'todo', shape='note', fontsize=10.5, bold=True)

    cases = [
        ('c1', 'a)  Văn bản in rõ nét',
         'Tệp nguồn trong kho\nglm-ocr-server/examples/source/page.png\n\n'
         'Kết quả tham chiếu GLM-OCR đã có\nexamples/result/page/page.json · page.md\nlayout_vis/layout_page0.jpg'),
        ('c2', 'b)  Bảng biểu / bố cục có cấu trúc',
         'Tệp nguồn trong kho\nglm-ocr-server/examples/source/table.png\n\n'
         'Kết quả tham chiếu GLM-OCR đã có\nexamples/result/table/table.json · table.md\nvà ui/_runs/0359de69/ (lần chạy đã ghi)'),
        ('c3', 'c)  Chữ viết tay  (trường hợp khó)',
         'Tệp nguồn trong kho\nglm-ocr-server/examples/source/handwritten.png\n\n'
         'Kết quả tham chiếu GLM-OCR đã có\nexamples/result/handwritten/handwritten.json · .md'),
        ('c4', 'd)  Ảnh chụp chất lượng thấp  —  CÒN THIẾU',
         'Kho mã nguồn không có ảnh chụp chất lượng thấp nào.\nCần bổ sung một ảnh chụp thật do tác giả tạo và\n'
         'tải lên qua ứng dụng.\n\nBáo cáo yêu cầu ít nhất một trường hợp khó nên không\nthể bỏ qua mẫu này.'),
    ]
    xs = [40, 380, 720, 1060]
    for (nid, title, body), x in zip(cases, xs):
        key = 'todo' if 'CÒN THIẾU' in title else 'svc'
        d.node(nid + '_h', x, 176, 300, 44, title, key, fontsize=10.5, bold=True)
        d.node(nid + '_s', x, 232, 300, 130, body, 'note', fontsize=9)
        d.node(nid + '_l', x, 376, 300, 190,
               'CHÈN ẢNH CHỤP\n\ntrái: tài liệu gốc\nphải: kết quả OCR do hệ thống\nnày tạo ra\n\n'
               'đánh dấu hai đến ba vị trí đúng\nvà sai trên ảnh',
               'todo', fontsize=9.5)
        d.node(nid + '_c', x, 580, 300, 96,
               'Nội dung chú thích cần ghi\n• công cụ đã dùng (selected_engine)\n• thời gian xử lý trang (processing_time_ms)\n'
               '• số vùng / độ tin cậy trung bình\n• loại lỗi cụ thể quan sát được',
               'ext', fontsize=9)

    d.node('n1', 40, 700, 1320, 84,
           'Cách chụp lại từng ảnh một cách tái lặp được: tải tệp mẫu lên qua POST /api/upload, chạy OCR với một '
           'công cụ đã chỉ định rõ, rồi dùng màn hình làm việc OCR để đặt ảnh trang (có hiển thị khung bao nhận '
           'dạng) cạnh thẻ Markdown hoặc Raw. Các giá trị cần cho chú thích đều hiện trên dải thống kê và cũng được '
           'ghi vào activity_logs, nhờ đó hình và phần thuyết minh luôn khớp nhau.',
           'note', shape='note', fontsize=10)
    d.node('n2', 40, 800, 1320, 66,
           'Yêu cầu trung thực đã nêu trong báo cáo: phải có ít nhất một trường hợp khó, và không được chỉ chọn các '
           'ví dụ cho kết quả đẹp. Kho mã nguồn cung cấp ba mẫu dùng được; ảnh chụp chất lượng thấp phải do tác giả '
           'tự bổ sung.',
           'todo', shape='note', fontsize=10)
    return d


# ══════════════════════════════════════════════════ 4.5 Khung biểu đồ thời gian
def f45():
    d = Diagram('fig_4_5_processing_time_template',
                'Hình 4.5 – So sánh thời gian xử lý theo công cụ và số trang  (khung biểu đồ, chưa có dữ liệu)',
                1400, 960,
                subtitle='KHO MÃ NGUỒN KHÔNG CÓ SỐ LIỆU ĐO NÀO — khung biểu đồ được cung cấp ở dạng trống, '
                         'kèm quy trình thu thập số liệu')

    d.node('warn', 40, 92, 1320, 74,
           'Kho mã nguồn không có kết quả đo hiệu năng OCR. Không có tập số liệu thời gian, không có kịch bản đo cho '
           'các công cụ OCR, và không có tệp kết quả đo nào được lưu. Thư mục tools/eval_results/*.json chứa số liệu '
           'độ trễ của các mô hình ngôn ngữ Qwen dùng cho trò chuyện / viết lại, không phải của OCR. Vẽ bất cứ điều '
           'gì ở đây khi chưa thực hiện phép đo sẽ là bịa số liệu, nên biểu đồ được giao ở dạng khung trống, chỉnh '
           'sửa được.',
           'todo', shape='note', fontsize=10.5, bold=True)

    d.node('plot', 140, 210, 600, 390, '', 'plot', shape='rect')
    d.node('nodata', 240, 370, 400, 70,
           'CHƯA CÓ DỮ LIỆU\nVẽ mỗi công cụ OCR thành một đường / nhóm cột tại đây\nsau khi thực hiện quy trình đo bên dưới.',
           'todo', shape='rect', fontsize=11, bold=True)
    d.node('ylab', 20, 300, 110, 210,
           'Thời gian xử lý\nmỗi tài liệu\n(giây)\n\ntrục dọc được chia\ntheo số liệu đo\nthực tế',
           'axis', shape='rect', fontsize=10, bold=True)
    for i, t in enumerate(['1', '2', '5', '10', '20']):
        d.node('xt%d' % i, 150 + i * 120, 606, 100, 26, t, 'axis', shape='rect', fontsize=10.5, bold=True)
    d.node('xlab', 340, 640, 200, 30, 'Số trang', 'axis', shape='rect', fontsize=10.5, bold=True)

    d.node('leg', 780, 210, 300, 190,
           'Chuỗi số liệu — mỗi công cụ OCR một chuỗi\n\n'
           '■  PaddleOCR Legacy      (paddleocr)\n'
           '■  PaddleOCR Modern    (paddleocr_modern)\n'
           '■  VietOCR                        (vietocr)\n'
           '■  GLM-OCR                     (glmocr)\n'
           '■  GLM Layout + VietOCR (glm_vietocr)',
           'note', fontsize=10)
    d.node('sep', 780, 418, 300, 192,
           'Trình bày riêng lần chạy đầu tiên\n\nYêu cầu đầu tiên với mỗi công cụ còn kèm việc nạp mô hình:\n'
           '• PaddleOCR / PP-StructureV3 tải và khởi tạo\n  pipeline ở lần dùng đầu\n'
           '• VietOCR nạp tệp trọng số .pth\n• máy chủ MLX giữ GLM-OCR thường trú, nhưng tiến\n'
           '  trình con glmocr và PP-DocLayoutV3 khởi động lại\n  ở mỗi lần gọi\n\n'
           'Gộp phép đo đầu tiên vào đường ổn định sẽ làm\nsai lệch tỷ lệ của biểu đồ.',
           'ext', fontsize=9)

    d.node('proc', 1120, 210, 240, 400,
           'Số liệu lấy từ đâu\n(đã có sẵn trong mã)\n\n'
           '1. Mỗi bộ thích nghi tự đo thời\n    gian thực và trả về\n    elapsed_ms.\n\n'
           '2. app.py chép giá trị đó sang\n    processing_time_ms trong\n    phản hồi của /api/ocr/page.\n\n'
           '3. Với /api/ocr/all, các giá trị\n    được cộng lại và ghi vào\n    chuỗi detail của activity_logs\n'
           '    cùng tên công cụ và số trang.\n\n'
           '4. /admin/logs liệt kê các bản ghi\n    đó và lọc được theo\n    action = "ocr".',
           'svc', fontsize=9)

    d.node('rec', 40, 690, 1320, 130,
           'Quy trình đo cần thực hiện trước khi hoàn thiện hình này\n\n'
           '1.  Chọn một tập tài liệu cố định có 1, 2, 5, 10 và 20 trang, mỗi tài liệu tải lên một lần.\n'
           '2.  Với mỗi công cụ, chạy làm nóng trên một tài liệu bỏ đi; ghi riêng phép đo đầu tiên đó.\n'
           '3.  Gọi POST /api/ocr/all với tham số engine chỉ định rõ, lặp ba lần cho mỗi cặp (tài liệu, công cụ).\n'
           '4.  Đọc processing_time_ms (hoặc giá trị tổng trong chuỗi detail của activity_logs) và lấy trung vị.\n'
           '5.  Ghi kèm các điều kiện cố định: đời máy, giá trị cfg.DEVICE, cờ OFFLINE, máy chủ MLX có đang chạy sẵn\n'
           '     hay không, và kích thước / độ phân giải chính xác của tài liệu.\n'
           '6.  Lưu ý VietOCR chuyển sang PaddleOCR khi đầu vào là PDF, nên cột nhiều trang của VietOCR thực chất đo\n'
           '     nhánh thay thế đó.',
           'note', shape='note', fontsize=10)

    d.node('n1', 40, 836, 1320, 74,
           'Ràng buộc về tính công bằng suy ra từ mã nguồn: kết quả được lưu trong bộ nhớ theo khóa '
           '(băm tệp, số trang, trạng thái tệp, công cụ), nên lặp lại đúng trang đó với đúng công cụ trong cùng một '
           'phiên máy chủ sẽ trả về kết quả trong bộ nhớ đệm thay vì chạy lại suy luận. Hãy khởi động lại ứng dụng, '
           'hoặc dùng tài liệu khác, giữa các lần lặp.',
           'todo', shape='note', fontsize=10)
    return d


if __name__ == '__main__':
    for fn in (f41, f42, f43, f44, f45):
        write(fn())
