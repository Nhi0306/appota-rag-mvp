# Câu trả lời Mission 3 — Tri thức nội bộ Appota

## 1. Trước (M2) → Vấn đề mới → Quyết định → Sau (M3) → Bằng chứng → Giới hạn

### M2 — Trước cải tiến
MVP chứng minh được: cùng một câu hỏi, hai người dùng khác đơn vị nhận câu trả lời khác nhau;
lọc phạm vi quyền chạy trước tìm kiếm; từ chối khi thiếu căn cứ; trả lời kèm nguồn.

### Vấn đề / yêu cầu mới (Mission 3)
- Tài liệu thay đổi theo thời gian: cần phân biệt phiên bản và thời điểm có hiệu lực.
- Quyền truy cập khác nhau theo bối cảnh người dùng (đã có, cần làm rõ hơn).
- Thông tin mâu thuẫn giữa nhiều nguồn/cấp tổ chức.
- Không phải lúc nào cũng đủ căn cứ để trả lời.
- Người dùng cần tự kiểm chứng tài liệu được sử dụng.

### Quyết định thay đổi / không thay đổi
Thay đổi:
1. Thêm tham số `as_of` (thời điểm hiệu lực) vào `Engine.answer` — cho phép truy vấn "tại thời điểm X".
2. Làm giàu `Source` (citation): đơn vị, cấp tổ chức, điểm BM25, trích đoạn, `as_of`.
3. Ghi audit log (JSONL) cho mỗi truy vấn: ai, đơn vị, câu hỏi, thời điểm, kết quả, nguồn.
4. Thêm trạng thái mức độ đầy đủ (`coverage`, `confidence`) và ghi chú khi câu trả lời có thể chưa đầy đủ.
5. `explain()` — giải thích vì sao một tài liệu hiển thị/ẩn với một người dùng.
6. `version_diff()` — so sánh khác biệt giữa hai phiên bản.
7. `visibility_reason()` — mã lý do chi tiết khi từ chối (unit/group/effective/status).

Không thay đổi:
- Không thêm LLM (vẫn trả lời bằng trích đoạn, không paraphrase).
- Không đổi schema dữ liệu cũ (tương thích ngược 11 test M2).
- Không thêm vector DB (BM25 thuần Python đủ cho quy mô giả lập).

### M3 — Sau cải tiến
- Truy vấn theo thời điểm: `engine.answer(q, user, as_of=date(...))`.
- Audit log tại `data/audit.jsonl`.
- Citation đầy đủ để tự kiểm chứng.
- Từ chối kèm mã lý do nội bộ, ghi chú "có thể chưa đầy đủ" khi coverage thiếu.

### Bằng chứng cho thấy tốt hơn
- 15/15 case kiểm thử (11 case M2 + 4 case B3) đều đạt.
- 25 test pytest đạt (10 test M3 + 7 test B3 + 8 test phiên/ngữ cảnh).
- Demo: cùng câu hỏi "Quy định nghỉ phép" với `as_of=2024-06-01` trả về bản 2024 (12 ngày),
  với `as_of=2025-06-01` trả về phụ lục phòng (16 ngày).
- Demo B3: cùng câu hỏi "cử sang công ty thành viên" cho 3 người ở 3 cấp → 10 / 5 / 7 ngày.

### Giới hạn còn lại
- Chưa có LLM để diễn đạt tự nhiên.
- Metadata vẫn do con người gắn; sai metadata ⇒ sai toàn chuỗi.
- Chưa có co chế xác nhận/ban hành tài liệu (workflow phê duyệt).
- Dữ liệu giả lập đơn giản hơn thực tế.

## 2. Ba câu quyết định bắt buộc

### Sau khi nhận yêu cầu mới, bạn đã ưu tiên thay đổi điều gì và chủ động chưa làm điều gì? Vì sao?
Ưu tiên: phân biệt phiên bản theo thời điểm hiệu lực (`as_of`) và làm giàu kiểm chứng nguồn (citation + audit + coverage),
vì đây là phần Mission 3 nhấn mạnh và đo được trực tiếp trên dữ liệu. Chưa làm: LLM diễn đạt và workflow phê duyệt tài liệu,
vì làm hai thứ đó không cải thiện chỉ số an toàn/phạm vi, và tốn thời gian hơn giá trị mang lại trong 3 ngày.

### Thay đổi nào tạo ra khác biệt lớn nhất giữa M2 và M3? Bằng chứng nào?
Truy vấn theo thời điểm hiệu lực (`as_of`). Bằng chứng: test `test_change_request_as_of_effective_date` đạt —
cùng một người dùng, cùng câu hỏi, nhưng `as_of=2024-06-01` trả bản 2024 (12 ngày) và `as_of=2025-06-01` trả bản 2025 (16 ngày).
M2 không thể làm điều này (cố định `today=2026-03-20`).

### Nếu đưa cho người dùng thật vào ngày mai, rủi ro/giới hạn lớn nhất còn lại là gì? Ưu tiên xử lý thế nào?
Rủi ro lớn nhất: metadata sai/thiếu (đơn vị, ngày hiệu lực, nhóm quyền) ⇒ trả lời sai phạm vi mà hệ thống không phát hiện.
Ưu tiên: (1) chặn tải lên nếu thiếu trường bắt buộc; (2) audit log + báo cáo câu trả lời sai để phát hiện sớm;
(3) thêm workflow HR duyệt/ban hành tài liệu trước khi `status=active`.

## 3. Change Request
Đại diện ban đầu: **B2 — truy vấn theo thời điểm hiệu lực (as-of)**. Các capability khác (version diff, access explanation,
audit, coverage) triển khai như cải tiến chung để bao phủ B1–B5.

### B3 — Xung đột giữa các cấp (Group vs công ty thành viên) [bổ sung]

**Vấn đề.** Một chủ đề có thể được quy định ở nhiều cấp tổ chức: Tập đoàn ban hành quy định chung,
mỗi công ty thành viên ban hành quy định riêng. Người hỏi ở cấp nào phải được trả lời theo quy định của cấp đó.

**Lỗi ở M2 (before).** Bộ chọn dùng `scope_depth` — độ sâu tuyệt đối của đơn vị trong cây tổ chức.
Với cây `appota → media/tech → phòng → nhóm`, `appota` và `media` cùng có depth 1, nên hai bản
"công ty thành viên" (Tập đoàn 10 ngày vs Media 5 ngày) bị coi là **cùng cấp** và hệ thống báo
`CONFLICT` — người hỏi ở Appota Media phải tự xác nhận, dù quy định riêng đã rõ ràng.

**Quyết định.** Đo khoảng cách tới **đơn vị của người hỏi** (`matched_unit` ∈ `ancestors(user.unit)`),
không phải độ sâu tuyệt đối:
- Bản nào có khoảng cách nhỏ nhất (cấp gần người hỏi nhất) → **được áp dụng**.
- Hai bản cùng khoảng cách (= cùng cấp) mà nội dung khác nhau → vẫn `CONFLICT`, không tự chọn.
- Gom toàn bộ văn bản cùng `family` mà người hỏi được phép xem (không giới hạn top-6 BM25),
  vì bản đặc thù ở cấp sâu có thể không nằm trong top-6 theo điểm từ khóa.

**Sau (M3).**
| Người hỏi | Cấp | Bản áp dụng | Kết quả |
|---|---|---|---|
| Hoàng Minh (`appota`) | Group / Tập đoàn | `qd-cty-tv-appota` | 10 ngày |
| Nguyễn Anh (`media.nd.g1`) | Công ty (Media) | `qd-cty-tv-media` | 5 ngày |
| Phạm Đức (`tech.kt.be`) | Công ty (Tech) | `qd-cty-tv-tech` | 7 ngày |

Câu trả lời kèm ghi chú đối chiếu cấp (chỉ nêu **tên** văn bản và cấp của bản bị thay thế,
không trích số liệu của bản đó), và giao diện có bảng "Đối chiếu giữa các cấp".

**Bằng chứng.** Case `T12`–`T15` trong `tests/report.md` và 7 test pytest mới
(`test_b3_*`) — tổng 25 test pytest + 15/15 case M2 vẫn đạt.

**Giới hạn.** Quy tắc "cấp gần hơn thắng" là giả định tổ chức (mức đặc thù hơn luôn thắng mức chung).
Nếu một công ty ban hành quy định *chung* yếu hơn quy định của Tập đoàn, cần bổ sung trường
`priority` trong metadata thay vì suy ra từ cây tổ chức.
