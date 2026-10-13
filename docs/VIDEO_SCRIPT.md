# Kịch bản video 5 phút — Mission 2

(Demo màn hình: giao diện `streamlit run app.py`. Quay màn hình + đọc đúng nội dung trong ngoặc kép.)

---

## 0:00–0:40 — Bài toán (quay màn hình intro)

"Tập đoàn có tri thức ở nhiều cấp: Tập đoàn, Công ty, Phòng, Nhóm. Hai nhân sự hỏi cùng một câu
về nghỉ phép nhưng thuộc hai đơn vị khác nhau thì phải nhận câu trả lời khác nhau. Thách thức
không phải tìm cho ra tài liệu, mà là tìm đúng tài liệu người này *được phép* dùng, đúng bản đang
có hiệu lực."

"Hướng giải quyết mình chọn từ Mission 1: AI không được quyết định ai xem cái gì — đó là code.
Mình hiện thực hóa đúng ý đó trong MVP."

## 0:40–1:40 — Phần chọn để chứng minh (đưa màn hình tới phần "Bối cảnh người dùng" bên sidebar)

"Phần quan trọng nhất mình chọn là tầng lọc quyền chạy trước mọi bước tìm kiếm."

'Khai báo mình là Nguyễn Anh — Nhóm Nội Dung 1. Cùng câu hỏi "Quy định nghỉ phép của tôi như thế nào?"…'

"Quy trình: bước 1 loại bản nháp và bản hết hiệu lực; bước 2 lọc phạm vi theo chuỗi đơn vị và nhóm
quyền của người hỏi — điều kiện AND, vừa đúng đơn vị vừa đúng nhóm; bước 3 mới chạy tìm kiếm và
trả lời kèm nguồn, phiên bản, ngày hiệu lực. Toàn bộ chạy offline trong ~50ms, không gọi API ngoài."

## 1:40–3:30 — Demo (bấm các nút trong app)

"Ví dụ 1 — cùng câu hỏi nghỉ phép. Nguyễn Anh, Phòng Nội Dung, nhận phụ lục riêng: 16 ngày.
Trần Bình, Phòng Kế Toán, nhận đúng bản chung của mình: 14 ngày. Vì phụ lục của Phòng Nội Dung
nằm ngoài chuỗi quyền của Trần Bình nên nó không bao giờ lọt vào câu trả lời."

"Ví dụ 2 — ngân sách quý 1. Trần Bình, nhân viên, không có nhóm quyền: hệ thống từ chối, trả về
câu chung chung — không lộ dù chỉ một dấu hiệu có tồn tại số liệu. Lê Chi, trưởng phòng, nhóm
quản lý: nhận 1,2 tỷ đồng kèm nguồn."

"Nhấn mạnh: hai trường hợp từ chối giống nhau hệt nhau trên màn hình; lý do chi tiết chỉ nằm
trong log nội bộ. Đó là cách chống lộ thông tin."

## 3:30–4:10 — Tình huống khó (hỏi "chính sách làm việc từ xa")

"Đây là ca khó: có hai văn bản cùng hiệu lực nhưng nội dung khác nhau — bản A nói 2 ngày một tuần,
bản B nói 3 ngày. Hệ thống không tự chọn, nêu cả hai và yêu cầu xác nhận với bộ phận nhân sự.
Nguyên tắc: với quyết định về quyền lợi, để con người chốt, không để AI quyết thay."

## 4:10–5:00 — Hạn chế trung thực (kể ngắn, nêu tests/report.md, case T10)

"Hạn chế thật của MVP: khi câu hỏi chạm văn bản ngoài quyền, ví dụ nhân viên Nội Dung hỏi tăng ca,
hệ thống trả đúng quy trình thuộc quyền nhưng chưa báo với người hỏi rằng còn hệ số lương ở văn bản
đơn vị khác mà họ không được xem. Chưa có cơ chế nút mức tin cậy. Ngoài ra chưa có LLM để diễn đạt
lại tự nhiên."

"Bộ kiểm thử 11 case, trong đó có 1 case thất bại trung thực như trên — đúng yêu cầu của đề.
Tóm lại: phần lõi là tầng quyền hoạt động đúng, và mình biết chính xác phần nào đang tốt, phần nào chưa."

© và ghi chú: mọi số liệu đều từ dữ liệu giả lập trong repo.