# 3 Câu hỏi bắt buộc — Mission 2

Dán vào các ô riêng của form. Mỗi câu nằm trong khoảng 60–150 từ.

---

## Q1. Phần quan trọng nhất bạn chọn để hiện thực hóa trong MVP là gì? Vì sao nếu phần này hoạt động, bạn tin rằng hướng giải quyết của mình là khả thi?

Mình chọn đúng tầng lọc quyền ngay khi truy vấn, chạy trước mọi bước "suy nghĩ". Sản phẩm xác định người hỏi qua SSO, lấy chuỗi đơn vị và nhóm quyền, loại văn bản ngoài phạm vi cùng bản nháp/bản hết hiệu lực, chỉ giao phần còn lại cho bộ tìm kiếm và trả lời. Mình tin hướng này khả thi vì nó biến bài toán "không được lộ dữ liệu" thành một điều kiện kiểm thử: rò ngoài phạm vi luôn bằng 0 về mặt cấu trúc, không phụ thuộc AI có tự kiềm chế hay không. MVP đã chạy offline hoàn toàn và cho thấy cùng câu hỏi, nhân sự Phòng Nội Dung nhận 16 ngày phép còn Phòng Kế Toán nhận 14 ngày, cùng 11/11 case kiểm thử đạt.

## Q2. So với kế hoạch ở Mission 1, bạn đã thay đổi quyết định hoặc thiết kế nào? Điều gì trong quá trình làm khiến bạn thay đổi?

Hai thay đổi rõ nhất. Thứ nhất, bỏ tìm kiếm vector để dùng BM25 thuần Python (word + char-bigram): vì không có API key cho mô hình nhúng, lựa chọn này chạy offline, tất định và dễ giải thích. Thứ hai, phát hiện ra "đúng đơn vị nhưng thiếu nhóm quyền" khi test quản lý và nhân viên: ban đầu nghĩ phạm vi và nhóm là hoặc/hoặc, thực tế phải là AND (vừa đúng đơn vị vừa đúng nhóm) để không rò tài liệu nhạy cảm. Quá trình làm cho mình thấy rủi ro lớn nhất không nằm ở thuật toán tìm kiếm mà ở ngữ nghĩa quyền, nên mình chuyển thời gian vào tầng lọc và bộ kiểm thử.

## Q3. Trường hợp nào hiện khiến hệ thống dễ trả lời sai hoặc sử dụng sai tri thức nhất? Bạn phát hiện và kiểm soát rủi ro đó như thế nào?

Rủi ro lớn nhất là nhân viên hỏi đúng chủ đề nhưng văn bản thuộc phạm vi khác. Khi test "quy trình triển khai Backend" cho nhân viên Phòng Kế Toán, hệ thống suýt trả bừa văn bản yếu hợp phạm vi. Mình phát hiện nhờ chạy bộ kiểm thử với đúng ba loại tình huống bắt buộc và phát minh ra lưới an toàn: nếu văn bản khớp nhất toàn cục nằm ngoài quyền và văn bản trong quyền chỉ đạt dưới một nửa điểm, hệ thống từ chối thay vì đoán; cùng đó là tầng lọc từ đặc tả buộc ít nhất một từ chủ chốt của câu hỏi phải có trong văn bản. Hệ quả: mọi trường hợp từ chối hiển thị cùng một câu trả lời chung chung, không hề lộ việc có tồn tại văn bản ngoài quyền.