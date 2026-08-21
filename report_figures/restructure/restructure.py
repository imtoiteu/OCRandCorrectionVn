#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gộp Chương 2, 3, 4 của báo cáo thành một Chương 2 duy nhất.

Giữ nguyên Chương 1, MỞ ĐẦU, KẾT LUẬN và TÀI LIỆU THAM KHẢO.
Không thêm nội dung kỹ thuật mới: chỉ gộp/đổi tên/đánh số lại và chỉnh những câu
tự tham chiếu tới số chương cho đúng sau khi gộp.
"""
import re, sys, docx
from copy import deepcopy

SRC, DST = sys.argv[1], sys.argv[2]
d = docx.Document(SRC)
ps = d.paragraphs

NEW_TITLE = ('CHƯƠNG 2. XÂY DỰNG HỆ THỐNG SỐ HÓA TÀI LIỆU THÔNG MINH '
             'ỨNG DỤNG CÔNG NGHỆ NHẬN DẠNG KÝ TỰ QUANG HỌC (OCR)')


def set_par_text(p, text):
    """Đặt lại nội dung đoạn, giữ định dạng của run đầu tiên."""
    runs = p.runs
    if not runs:
        p.add_run(text)
        return
    runs[0].text = text
    for r in runs[1:]:
        r._element.getparent().remove(r._element)


def drop(p):
    p._p.getparent().remove(p._p)


# ── 1. Mục "8. Kết cấu đề tài" trong MỞ ĐẦU ────────────────────────────────
set_par_text(ps[44], 'Ngoài phần Mở đầu, Kết luận, Tài liệu tham khảo và Phụ lục, '
                     'đề tài gồm hai chương:')
set_par_text(ps[46], 'Chương 2. Xây dựng hệ thống số hóa tài liệu thông minh ứng dụng '
                     'công nghệ nhận dạng ký tự quang học (OCR)')

# ── 2. Tiêu đề chương mới + sửa các câu tự tham chiếu số chương ────────────
set_par_text(ps[145], NEW_TITLE)

set_par_text(ps[354],
    'Những kết quả phân tích và thiết kế nêu trên là cơ sở để xây dựng các thành phần '
    'phần mềm, tích hợp công cụ OCR, triển khai giao diện và tổ chức kiểm thử được '
    'trình bày ở các mục tiếp theo. Trong quá trình hiện thực hóa, các sơ đồ, quy trình '
    'và mô hình dữ liệu có thể được điều chỉnh ở mức chi tiết để phù hợp với phần mềm, '
    'nhưng phải duy trì các nguyên tắc đã xác định về tính nhất quán, khả năng truy vết '
    'và kiểm soát quyền truy cập.')
set_par_text(ps[496],
    'Trên cơ sở kiến trúc và yêu cầu đã xác định ở các mục phân tích và thiết kế, chương '
    'này đã trình bày quá trình xây dựng và triển khai hệ thống SmartDocs. Sản phẩm được '
    'tổ chức thành WebApp và DesktopApp. WebApp chứa đầy đủ chức năng quản lý tài liệu, '
    'cơ sở dữ liệu, dịch vụ xử lý và các công cụ OCR; DesktopApp cung cấp lớp giao diện '
    'cài đặt trên máy tính, quản lý vòng đời backend và hỗ trợ nhiều phương án kết nối. '
    'Việc tách hai dự án tạo điều kiện sử dụng hệ thống linh hoạt trong môi trường cục bộ, '
    'mạng nội bộ hoặc máy chủ tập trung.')
set_par_text(ps[501],
    'Những kết quả nêu trên cho thấy hệ thống đã chuyển từ thiết kế sang một nền tảng có '
    'khả năng vận hành và xử lý tài liệu thực tế. Tuy nhiên, mức độ chính xác của từng '
    'công cụ, thời gian xử lý, khả năng chịu tải và mức độ phù hợp với các nhóm tài liệu '
    'của Học viện cần được đánh giá bằng dữ liệu kiểm thử cụ thể. Đây là nội dung được '
    'tiếp tục trình bày ở các mục thử nghiệm và đánh giá hệ thống.')
set_par_text(ps[638],
    'Công tác thử nghiệm và đánh giá hệ thống được tổ chức trên bốn phương diện: chức năng, '
    'chất lượng OCR, hiệu năng vận hành và khả năng quản lý dữ liệu. Môi trường thử nghiệm '
    'chính được tổ chức trên macOS Apple Silicon, trong đó WebApp, cơ sở dữ liệu và các '
    'công cụ OCR được triển khai cục bộ; DesktopApp sử dụng lại môi trường xử lý đầy đủ '
    'hoặc kết nối đến backend đã được cấu hình.')

# ── 3. Đánh số lại và đổi tên các mục ──────────────────────────────────────
# (chỉ số đoạn gốc, tiêu đề mới)
RENAME = {
    146: '1. Phân tích bài toán và yêu cầu hệ thống',
    147: '1.1. Đặt vấn đề và mục tiêu xây dựng hệ thống',
    154: '1.2. Phạm vi chức năng của hệ thống',
    161: '1.3. Các nhóm người dùng và quyền sử dụng',
    167: '1.4. Yêu cầu chức năng',
    177: '1.5. Yêu cầu phi chức năng',
    188: '1.6. Mô hình ca sử dụng của hệ thống',

    198: '2. Thiết kế kiến trúc hệ thống',
    199: '2.1. Biểu đồ ngữ cảnh hệ thống',
    208: '2.2. Kiến trúc tổng thể và kiến trúc triển khai',
    225: '2.3. Mô hình tương tác giữa các thành phần',

    235: '3. Thiết kế quy trình xử lý tài liệu',
    236: '3.1. Quy trình tiếp nhận và chuẩn hóa tài liệu',
    247: '3.2. Quy trình tiền xử lý và lựa chọn công cụ OCR',
    257: '3.3. Quy trình nhận dạng và hậu xử lý kết quả',
    263: '3.4. Quy trình lưu trữ, ghi log và xử lý lỗi',

    269: '4. Thiết kế dữ liệu',
    270: '4.1. Mô hình dữ liệu tổng thể',
    279: '4.2. Dữ liệu người dùng, tài liệu và kết quả OCR',
    285: '4.3. Dữ liệu cấu hình, lịch sử xử lý và nhật ký hệ thống',

    291: '5. Thiết kế giao diện và bảo đảm an toàn thông tin',
    312: '5.1. Giao diện người dùng và xử lý tài liệu',
    322: '5.2. Giao diện lịch sử và quản trị hệ thống',
    329: '5.3. Xác thực, phân quyền và kiểm soát truy cập',
    334: '5.4. Bảo vệ tài liệu và dữ liệu lưu trữ',
    340: '5.5. Lưu vết hoạt động, sao lưu và xử lý sự cố',

    357: '6. Môi trường, công nghệ và công cụ xây dựng hệ thống',
    358: '6.1. Môi trường phát triển và triển khai',
    370: '6.2. Công nghệ xây dựng hệ thống',
    378: '6.3. Các công cụ OCR được tích hợp',

    385: '7. Xây dựng các thành phần chính của hệ thống',
    386: '7.1. Xây dựng backend, API và cơ sở dữ liệu',
    400: '7.2. Xây dựng giao diện người dùng',
    415: '7.3. Xây dựng chức năng quản trị hệ thống',

    425: '8. Xây dựng mô-đun xử lý tài liệu và OCR',
    426: '8.1. Tiếp nhận, chuẩn hóa và tiền xử lý tài liệu',
    437: '8.2. Tích hợp và lựa chọn công cụ OCR',
    448: '8.3. Thực hiện OCR và chuẩn hóa kết quả',

    460: '9. Triển khai và tối ưu hệ thống',
    461: '9.1. Triển khai hệ thống trong môi trường thử nghiệm',
    476: '9.2. Tối ưu hiệu năng xử lý và lưu trữ',
    484: '9.3. Hoàn thiện giao diện và trải nghiệm người dùng',

    503: '10. Thử nghiệm và kiểm thử chức năng hệ thống',
    504: '10.1. Môi trường thử nghiệm',
    514: '10.2. Bộ dữ liệu và phương pháp thử nghiệm',
    533: '10.3. Kiểm thử các chức năng người dùng',
    544: '10.4. Kiểm thử chức năng quản trị và phân quyền',
    551: '10.5. Tổng hợp kết quả kiểm thử chức năng',

    557: '11. Thực nghiệm và đánh giá chất lượng OCR',
    558: '11.1. Tiêu chí đánh giá',
    569: '11.2. Kết quả thử nghiệm trên các nhóm tài liệu',
    582: '11.3. So sánh các công cụ OCR',
    589: '11.4. Nhận xét và lựa chọn công cụ phù hợp',

    593: '12. Đánh giá hiệu năng và khả năng vận hành',
    594: '12.1. Thời gian xử lý và khả năng xử lý tài liệu nhiều trang',
    604: '12.2. Mức sử dụng tài nguyên và độ ổn định',
    610: '12.3. Đánh giá khả năng lưu trữ, truy vết và kiểm soát dữ liệu',

    617: '13. Nhận xét chung về kết quả xây dựng và thử nghiệm',
    618: '13.1. Kết quả đạt được',
    623: '13.2. Hạn chế và nguyên nhân',
    631: '13.3. Hướng hoàn thiện',

    637: 'Kết luận chương 2',
}
for idx, title in RENAME.items():
    set_par_text(ps[idx], title)

# ── 4. Chuyển hai khối kết luận cũ về cuối chương ──────────────────────────
anchor = ps[638]._p                      # đoạn đầu của phần kết luận hợp nhất
for i in list(range(350, 355)) + list(range(496, 502)):
    anchor.addprevious(ps[i]._p)         # lxml: chuyển phần tử, không nhân bản

# ── 5. Xóa các tiêu đề đã bị gộp / không còn cần ───────────────────────────
for i in (166, 328, 356, 349, 495, 502, 532, 47, 48):
    drop(ps[i])

d.save(DST)
print('bước cấu trúc: xong ->', DST)
