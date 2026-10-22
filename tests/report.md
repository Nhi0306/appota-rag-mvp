# Bộ kiểm thử Mission 2

Số case: 15 (yêu cầu tối thiểu 5).

| ID | Kỳ vọng | Kết quả thực tế | Đạt/Chưa đạt | Điều học được |
|---|---|---|---|---|
| T1 (tốt) | Cùng một câu hỏi, hai bối cảnh khác nhau phải cho kết quả khác nhau | kind: DUNG (OK -> OK) | chosen: DUNG (qd-nghi-phep-phu-luc-nd -> qd-nghi-phep-phu-luc-nd) | contains: 16 ngày: DUNG (16 ngày -> Được. Theo Phụ lục nghỉ phép riêng của Phòng Nội Dung (bản 2025.1, hiệu lực 2025-01-01 → hiện hành):

"Phụ lục này áp dụng cho toàn bộ nhân sự Phòng Nội Dung (Appota Media) và áp dụng thay cho
điều 3 ) | not_contains: 12 ngày: DUNG (12 ngày -> Được. Theo Phụ lục nghỉ phép riêng của Phòng Nội Dung (bản 2025.1, hiệu lực 2025-01-01 → hiện hành):

"Phụ lục này áp dụng cho toàn bộ nhân sự Phòng Nội Dung (Appota Media) và áp dụng thay cho
điều 3 ) | has_source: DUNG (>=1 -> 2) | Đạt | Phần lõi hoạt động: cùng câu hỏi, nhân sự Phòng Nội Dung nhận phụ lục riêng 16 ngày. Bản đặc thù (phạm vi sâu hơn) thắng bản chung. Đây chính là thứ giả thuyết cần chứng minh. |
| T2 (tốt) | Nhân sự đơn vị khác (Kế Toán) nhận đúng bản chung của mình | kind: DUNG (OK -> OK) | chosen: DUNG (qd-nghi-phep-2025 -> qd-nghi-phep-2025) | contains: 14 ngày: DUNG (14 ngày -> Được. Theo Quy định nghỉ phép (Bản hiện hành) (bản 2025.2, hiệu lực 2025-01-01 → hiện hành):

"Chi tiết cụ thể:
Tổng số ngày nghỉ phép năm của nhân viên là 14 ngày. Mỗi nhân viên được nghỉ phép cộng t) | not_contains: 16 ngày: DUNG (16 ngày -> Được. Theo Quy định nghỉ phép (Bản hiện hành) (bản 2025.2, hiệu lực 2025-01-01 → hiện hành):

"Chi tiết cụ thể:
Tổng số ngày nghỉ phép năm của nhân viên là 14 ngày. Mỗi nhân viên được nghỉ phép cộng t) | not_contains: 16 ngày phép: DUNG (16 ngày phép -> Được. Theo Quy định nghỉ phép (Bản hiện hành) (bản 2025.2, hiệu lực 2025-01-01 → hiện hành):

"Chi tiết cụ thể:
Tổng số ngày nghỉ phép năm của nhân viên là 14 ngày. Mỗi nhân viên được nghỉ phép cộng t) | has_source: DUNG (>=1 -> 1) | Đạt | Phụ lục của Phòng Nội Dung không lọt vào ngữ cảnh của người ngoài phòng: lọc phạm vi chạy trước khi tìm kiếm nên không cần dựa vào AI để ‘tự biết’. |
| T3 (tốt) | Văn bản áp dụng chung toàn Tập đoàn | kind: DUNG (OK -> OK) | chosen: DUNG (qd-nghi-le-2026 -> qd-nghi-le-2026) | contains: 11 ngày: DUNG (11 ngày -> Được. Theo Quy định nghỉ lễ năm 2026 (bản 2026.1, hiệu lực 2026-01-01 → hiện hành):

"Tổng số ngày nghỉ lễ trong năm 2026 là 11 ngày, gồm Tết Dương lịch, Tết Nguyên đán,
30/4, 1/5, Quốc khánh 2/9 theo) | has_source: DUNG (>=1 -> 1) | Đạt | Tài liệu phạm vi appota (toàn Tập đoàn) nhân viên bất kỳ đơn vị nào cũng truy cập được. |
| T4 (tốt) | Người quản lý được truy cập tài liệu nhạy cảm theo nhóm quyền manager | kind: DUNG (OK -> OK) | chosen: DUNG (qd-ngan-sach-q1-media -> qd-ngan-sach-q1-media) | contains: 1,2 tỷ: DUNG (1,2 tỷ -> Được. Theo Ngân sách quý 1 — Appota Media (bản 2026.1, hiệu lực 2026-01-01 → hiện hành):

"Ngân sách quý 1 năm 2026 của Appota Media là 1,2 tỷ đồng. Ngân sách nội dung chiếm 45%; ngân sách marketing c) | not_contains: quyền: DUNG (quyền -> Được. Theo Ngân sách quý 1 — Appota Media (bản 2026.1, hiệu lực 2026-01-01 → hiện hành):

"Ngân sách quý 1 năm 2026 của Appota Media là 1,2 tỷ đồng. Ngân sách nội dung chiếm 45%; ngân sách marketing c) | has_source: DUNG (>=1 -> 1) | Đạt | Nhóm quyền quản lý mở thêm tài liệu nhạy cảm. Điều kiện là AND (đơn vị media VÀ nhóm manager) nên không xảy ra tình trạng ‘đúng đơn vị nhưng thiếu nhóm’. |
| T5 (khó) | Mâu thuẫn phiên bản cùng hiệu lực → KHÔNG tự chọn | kind: DUNG (CONFLICT -> CONFLICT) | contains: 2 ngày: DUNG (2 ngày -> Lưu ý: hiện có hai văn bản cùng cấp áp dụng và cùng giai đoạn hiệu lực nhưng nội dung khác nhau về chủ đề này:

1. Chính sách làm việc từ xa (Bản A) — cấp Tập đoàn (Tập đoàn Appota), bản 2025.1: "Nhân) | contains: 3 ngày: DUNG (3 ngày -> Lưu ý: hiện có hai văn bản cùng cấp áp dụng và cùng giai đoạn hiệu lực nhưng nội dung khác nhau về chủ đề này:

1. Chính sách làm việc từ xa (Bản A) — cấp Tập đoàn (Tập đoàn Appota), bản 2025.1: "Nhân) | n_sources: DUNG (2 -> 2) | Đạt | Hai văn bản cùng hiệu lực nội dung khác nhau (2 vs 3 ngày). Hệ thống nêu cả hai và yêu cầu xác nhận thay vì đoán bừa. Kết luận: để con người chốt, không để AI quyết thay. |
| T6 (khó) | Bản hết hạn (2024) và bản nháp (2026) không bao giờ được dùng để trả lời | kind: DUNG (OK -> OK) | not_contains: 12 ngày: DUNG (12 ngày -> Được. Theo Phụ lục nghỉ phép riêng của Phòng Nội Dung (bản 2025.1, hiệu lực 2025-01-01 → hiện hành):

"Phụ lục này áp dụng cho toàn bộ nhân sự Phòng Nội Dung (Appota Media) và áp dụng thay cho
điều 3 ) | not_contains: 15 ngày phép: DUNG (15 ngày phép -> Được. Theo Phụ lục nghỉ phép riêng của Phòng Nội Dung (bản 2025.1, hiệu lực 2025-01-01 → hiện hành):

"Phụ lục này áp dụng cho toàn bộ nhân sự Phòng Nội Dung (Appota Media) và áp dụng thay cho
điều 3 ) | not_contains: bản nháp: DUNG (bản nháp -> Được. Theo Phụ lục nghỉ phép riêng của Phòng Nội Dung (bản 2025.1, hiệu lực 2025-01-01 → hiện hành):

"Phụ lục này áp dụng cho toàn bộ nhân sự Phòng Nội Dung (Appota Media) và áp dụng thay cho
điều 3 ) | no_source_ids: DUNG (['qd-nghi-phep-2024', 'ban-nhap-qd-nghi-phep-2026'] -> ['qd-nghi-phep-2025', 'qd-nghi-phep-phu-luc-nd']) | Đạt | Trạng thái hiệu lực và trạng thái bản nháp được lọc ở tầng dữ liệu (usable) nên model/đoạn mã không bao giờ nhìn thấy chúng. Nguyên tắc: sai metadata/hiệu lực thì sai ngay ở tầng truy vấn, không phải ở câu trả lời. |
| T7 (an-toan) | Câu hỏi nhạy cảm ngoài quyền → từ chối và KHÔNG lộ số liệu | kind: DUNG (REFUSE -> REFUSE) | reason: DUNG (out_of_scope -> out_of_scope) | not_contains: 1,2 tỷ: DUNG (1,2 tỷ -> Xin lỗi, hệ thống không tìm thấy văn bản trong phạm vi quyền của bạn đủ để trả lời câu hỏi này. Bạn có thể liên hệ Phòng Nhân Sự để được hỗ trợ.) | not_contains: 45%: DUNG (45% -> Xin lỗi, hệ thống không tìm thấy văn bản trong phạm vi quyền của bạn đủ để trả lời câu hỏi này. Bạn có thể liên hệ Phòng Nhân Sự để được hỗ trợ.) | not_contains: 500 triệu: DUNG (500 triệu -> Xin lỗi, hệ thống không tìm thấy văn bản trong phạm vi quyền của bạn đủ để trả lời câu hỏi này. Bạn có thể liên hệ Phòng Nhân Sự để được hỗ trợ.) | Đạt | Khi văn bản đúng chủ đề nằm ngoài quyền, hệ thống từ chối với câu trả lời chung chung — không hề lộ việc ‘có tồn tại một con số ngân sách’. Lý do chi tiết chỉ ghi ở log nội bộ. |
| T8 (an-toan) | Câu hỏi đúng chủ đề nhưng văn bản thuộc đơn vị khác → từ chối, không trả nhầm | kind: DUNG (REFUSE -> REFUSE) | reason: DUNG (out_of_scope -> out_of_scope) | Đạt | Từ khóa ‘triển khai’ rất khớp với quy trình Backend nhưng bản đó chỉ cho nhóm Backend. Nhờ kiểm tra ‘văn bản đúng nhất thế giới có nằm trong quyền không’ trước khi trả lời, hệ thống chọn từ chối thay vì đoán. |
| T9 (thất-bại) | Thiếu dữ liệu hoàn toàn → từ chối sạch | kind: DUNG (REFUSE -> REFUSE) | reason: DUNG (no_source -> no_source) | Đạt | Không tồn tại văn bản nào về mua sắm. Có ít nhất một từ đặc tả (‘mua sắm’) không trùng bất kỳ văn bản nào trong quyền → chặn để không đoán bừa ‘theo quy trình…’. |
| T10 (thất-bại) | Tăng ca: trả lời đúng quy trình nhưng THIẾU hệ số lương vì bản hệ số ngoài quyền | kind: DUNG (OK -> OK) | contains: Quy trình đăng ký tăng ca: DUNG (Quy trình đăng ký tăng ca -> Được. Theo Quy trình đăng ký tăng ca — Phòng Nội Dung (bản 2025.1, hiệu lực 2025-01-01 → hiện hành):

"Nhân sự Phòng Nội Dung đăng ký tăng ca qua form nội bộ, trưởng phòng duyệt trước
khi làm. Thời gi) | contains: trưởng phòng: DUNG (trưởng phòng -> Được. Theo Quy trình đăng ký tăng ca — Phòng Nội Dung (bản 2025.1, hiệu lực 2025-01-01 → hiện hành):

"Nhân sự Phòng Nội Dung đăng ký tăng ca qua form nội bộ, trưởng phòng duyệt trước
khi làm. Thời gi) | misses (những thứ CHƯA có): DUNG (['1,5 lần lương', '1.5 lần lương', '2 lần vào cuối tuần'] -> Được. Theo Quy trình đăng ký tăng ca — Phòng Nội Dung (bản 2025.1, hiệu lực 2025-01-01 → hiện hành):

"Nhân sự Phòng Nội Dung đăng ký tăng ca qua form nội bộ, t) | Đạt | Trả lời đúng phần thuộc quyền (quy trình đăng ký của Phòng Nội Dung) nhưng không trả lời được hệ số lương vì bản quy định hệ số là của Appota Tech. Đây là hạn chế thật của MVP: chưa có cơ chế nói với người dùng rằng câu trả lời có thể chưa đầy đủ. Hướng khắc phục ở Mission 3: thêm trạng thái mức tin cậy + đường dẫn hỏi HR. |
| T11 (an-toan) | Tài liệu nội bộ của một nhóm không lọt sang người khác | kind: DUNG (REFUSE -> REFUSE) | Đạt | Biên bản họp nhóm g1 là tài liệu chỉ nhóm ấy xem; người phòng khác bị từ chối đồng nhất với mọi trường hợp từ chối khác. |
| T12 (tốt) | B3 — cấp Group áp dụng quy định của Tập đoàn (10 ngày) | kind: DUNG (OK -> OK) | chosen: DUNG (qd-cty-tv-appota -> qd-cty-tv-appota) | contains: 10 ngày: DUNG (10 ngày -> Được. Theo Quy định làm việc tại công ty thành viên (cấp Tập đoàn) (bản 2026.1, hiệu lực 2026-01-01 → hiện hành):

"Nhân viên được cử sang làm việc tại công ty thành viên khác tối đa 10 ngày mỗi năm. ) | not_contains: 5 ngày: DUNG (5 ngày -> Được. Theo Quy định làm việc tại công ty thành viên (cấp Tập đoàn) (bản 2026.1, hiệu lực 2026-01-01 → hiện hành):

"Nhân viên được cử sang làm việc tại công ty thành viên khác tối đa 10 ngày mỗi năm. ) | not_contains: 7 ngày: DUNG (7 ngày -> Được. Theo Quy định làm việc tại công ty thành viên (cấp Tập đoàn) (bản 2026.1, hiệu lực 2026-01-01 → hiện hành):

"Nhân viên được cử sang làm việc tại công ty thành viên khác tối đa 10 ngày mỗi năm. ) | has_source: DUNG (>=1 -> 1) | Đạt | Người hỏi ở cấp Group không được tự động dùng quy định của công ty thành viên. Mức áp dụng phải theo đúng cấp của người hỏi. |
| T13 (tốt) | B3 — cấp công ty thành viên dùng quy định riêng (Media 5 ngày), không phải mức chung 10 ngày | kind: DUNG (OK -> OK) | chosen: DUNG (qd-cty-tv-media -> qd-cty-tv-media) | contains: 5 ngày: DUNG (5 ngày -> Được. Theo Quy định làm việc tại công ty thành viên — Appota Media (bản 2026.1, hiệu lực 2026-01-01 → hiện hành):

"Nhân viên Appota Media được cử sang làm việc tại công ty thành viên khác tối đa 5 ng) | not_contains: 10 ngày: DUNG (10 ngày -> Được. Theo Quy định làm việc tại công ty thành viên — Appota Media (bản 2026.1, hiệu lực 2026-01-01 → hiện hành):

"Nhân viên Appota Media được cử sang làm việc tại công ty thành viên khác tối đa 5 ng) | not_contains: 7 ngày: DUNG (7 ngày -> Được. Theo Quy định làm việc tại công ty thành viên — Appota Media (bản 2026.1, hiệu lực 2026-01-01 → hiện hành):

"Nhân viên Appota Media được cử sang làm việc tại công ty thành viên khác tối đa 5 ng) | has_source: DUNG (>=1 -> 2) | Đạt | Bản đặc thù của công ty thay bản chung của Tập đoàn. Trước B3, hệ thống so độ sâu tuyệt đối (appota và media cùng depth 1) nên báo CONFLICT giả cho câu hỏi này. |
| T14 (khó) | B3 — hai bản CÙNG cấp, cùng hiệu lực, khác nội dung → vẫn phải báo CONFLICT | kind: DUNG (CONFLICT -> CONFLICT) | contains: 2 ngày: DUNG (2 ngày -> Lưu ý: hiện có hai văn bản cùng cấp áp dụng và cùng giai đoạn hiệu lực nhưng nội dung khác nhau về chủ đề này:

1. Chính sách làm việc từ xa (Bản A) — cấp Tập đoàn (Tập đoàn Appota), bản 2025.1: "Nhân) | contains: 3 ngày: DUNG (3 ngày -> Lưu ý: hiện có hai văn bản cùng cấp áp dụng và cùng giai đoạn hiệu lực nhưng nội dung khác nhau về chủ đề này:

1. Chính sách làm việc từ xa (Bản A) — cấp Tập đoàn (Tập đoàn Appota), bản 2025.1: "Nhân) | n_sources: DUNG (2 -> 2) | Đạt | B3 chỉ giải quyết mâu thuẫn GIỮA các cấp. Mâu thuẫn trong cùng một cấp vẫn phải đưa ra cho người dùng xác nhận — không tự chọn. |
| T15 (an-toan) | B3 — câu trả lời không lộ nội dung của bản ở cấp khác (không rò số ngày của Tập đoàn) | kind: DUNG (OK -> OK) | not_contains: 10 ngày: DUNG (10 ngày -> Được. Theo Quy định làm việc tại công ty thành viên — Appota Media (bản 2026.1, hiệu lực 2026-01-01 → hiện hành):

"Nhân viên Appota Media được cử sang làm việc tại công ty thành viên khác tối đa 5 ng) | has_source: DUNG (>=1 -> 2) | Đạt | Khi nêu đối chiếu các cấp, hệ thống chỉ nêu TÊN văn bản và cấp của bản không áp dụng, không trích số liệu của bản đó — tránh gây hiểu nhầm là nhiều mức áp dụng cùng lúc. |

**Tổng kết: 15/15 case đạt.**

Danh mục nhóm case: tốt · khó · an-toàn · thất-bại (để trung thực về giới hạn MVP).