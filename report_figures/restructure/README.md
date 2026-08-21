# Gộp Chương 2, 3, 4 thành một Chương 2

Bộ script đã tạo ra `BAO_CAO_DE_TAI_OCR_DA_HIEU_CHINH_restructured.docx` từ
`BAO_CAO_DE_TAI_OCR_DA_HIEU_CHINH.docx`. Chạy tuần tự:

```bash
python3 restructure.py  <goc>.docx    b1.docx     # gộp chương, đánh số lại mục
python3 renumber.py     b1.docx       b2.docx     # đánh số lại Hình và Bảng
python3 toc.py          b2.docx       b3.docx     # dựng lại bảng mục lục
soffice --headless --convert-to pdf b3.docx       # kết xuất để lấy số trang
pdftotext -layout b3.pdf b3.txt
python3 pages.py        b3.docx  <ket_qua>.docx  b3.txt   # điền số trang
```

Nguyên tắc: không thêm nội dung kỹ thuật mới. Chỉ gộp, đổi tên, đánh số lại và
chỉnh những câu tự tham chiếu tới số chương cho đúng sau khi gộp.

## Cấu trúc Chương 2 sau khi gộp

| Mục | Nguồn |
|---|---|
| 1. Phân tích bài toán và yêu cầu hệ thống | Chương 2 cũ, mục 1 + 2 |
| 2. Thiết kế kiến trúc hệ thống | Chương 2 cũ, mục 3 |
| 3. Thiết kế quy trình xử lý tài liệu | Chương 2 cũ, mục 4 |
| 4. Thiết kế dữ liệu | Chương 2 cũ, mục 5 |
| 5. Thiết kế giao diện và bảo đảm an toàn thông tin | Chương 2 cũ, mục 6 + 7 |
| 6. Môi trường, công nghệ và công cụ xây dựng hệ thống | Chương 3 cũ, mục 1 |
| 7. Xây dựng các thành phần chính của hệ thống | Chương 3 cũ, mục 2 |
| 8. Xây dựng mô-đun xử lý tài liệu và OCR | Chương 3 cũ, mục 3 |
| 9. Triển khai và tối ưu hệ thống | Chương 3 cũ, mục 4 |
| 10. Thử nghiệm và kiểm thử chức năng hệ thống | Chương 4 cũ, mục 1 + 2 |
| 11. Thực nghiệm và đánh giá chất lượng OCR | Chương 4 cũ, mục 3 |
| 12. Đánh giá hiệu năng và khả năng vận hành | Chương 4 cũ, mục 4 |
| 13. Nhận xét chung về kết quả xây dựng và thử nghiệm | Chương 4 cũ, mục 5 |
| Kết luận chương 2 | ba phần "Kết luận chương" cũ, ghép theo thứ tự |

Hình: 2.1–2.10 giữ nguyên · 3.1–3.11 → 2.11–2.21 · 4.1–4.5 → 2.22–2.26.
Bảng: 4.1–4.11 → 2.1–2.11.

## Bước rà soát bố cục (lần 2)

Sau khi đọc lại toàn bộ báo cáo, chạy tiếp hai script để tinh chỉnh bố cục và
tạo ra `BAO_CAO_DE_TAI_OCR_DA_HIEU_CHINH_final.docx`:

```bash
python3 refine.py  <ban_gop>.docx  c1.docx      # chuyển ảnh, tách mục 5, đánh số lại
python3 toc2.py    c1.docx         c2.docx      # dựng lại mục lục (thêm/bớt dòng linh hoạt)
soffice --headless --convert-to pdf c2.docx
pdftotext -layout c2.pdf c2.txt
python3 pages.py   c2.docx  <ket_qua>.docx  c2.txt
```

Ba thay đổi:

1. **14 ảnh chụp màn hình bị bỏ quên.** Chúng nằm ngay dưới tiêu đề mục thiết kế
   giao diện, không có chú thích, trong khi năm chú thích hình ở phần hiện thực
   hóa lại không có ảnh. Ảnh được chuyển về đúng chú thích mô tả chúng:

   | Hình | Ảnh được gán |
   |---|---|
   | 2.13 Giao diện đăng nhập và trang làm việc chính | đăng nhập · trang chính (quản trị viên) · trang chính (người dùng) |
   | 2.14 Giao diện tải tài liệu, lựa chọn công cụ và xem kết quả OCR | trang tải tệp · màn hình làm việc có hộp chọn công cụ và kết quả |
   | 2.15 Giao diện quản trị người dùng, tài liệu và nhật ký | tổng quan quản trị · quản lý người dùng · nhật ký hoạt động · quản lý tệp tin |
   | 2.18 Giao diện kết quả OCR theo văn bản và dữ liệu có cấu trúc | thẻ Nguồn · thẻ Hình ảnh · thẻ JSON |
   | 2.21 Một số giao diện hoàn thiện của hệ thống | thư viện tài liệu · kết quả OCR đầy đủ một trang |

   Hình 2.20 (giao diện chọn môi trường của ứng dụng desktop) vẫn để trống vì
   trong tài liệu không có ảnh chụp nào của ứng dụng desktop.

2. **Tách mục 5** "Thiết kế giao diện và bảo đảm an toàn thông tin" thành
   "5. Thiết kế giao diện hệ thống" (5.1–5.2) và "6. Thiết kế bảo mật và an toàn
   thông tin" (6.1–6.3); các mục sau dồn lên thành 7–14.

3. **Sửa hai chỗ không nhất quán**: tiêu đề "Cơ sở thực tiễn" ở Chương 1 thiếu số
   thứ tự (→ "2. Cơ sở thực tiễn"); câu cuối Kết luận chương 1 nói "ở các chương
   tiếp theo" trong khi chỉ còn một chương (→ "ở chương tiếp theo").
