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

### Câu 1 — Sau khi nhận yêu cầu mới, bạn đã ưu tiên thay đổi điều gì và chủ động chưa làm điều gì? Vì sao?

**Ưu tiên (theo thứ tự):**

1. **Sửa quy tắc chọn bản áp dụng theo cấp (Change Request B3).** Đây là thứ ưu tiên cao nhất vì nó
   không phải "thêm tính năng" mà là **sửa một lỗi trả lời sai**: M2 dùng `scope_depth` (độ sâu tuyệt đối
   của đơn vị trong cây tổ chức), nên `appota` và `media` cùng có depth 1 → hai quy định ở **hai cấp khác
   nhau** bị coi là "cùng cấp" → hệ thống báo `CONFLICT` giả, bắt người dùng tự xác nhận.
   M3 đo **khoảng cách tới đơn vị của người hỏi** thay vì độ sâu tuyệt đối.
2. **Truy vấn theo thời điểm hiệu lực (`as_of`)** — văn bản trong thực tế có nhiều bản theo thời gian;
   không có nó thì "đúng hiện hành" là may mắn, không phải thiết kế.
3. **Làm giàu kiểm chứng + audit + coverage** — để người dùng tự kiểm chứng và để chúng ta phát hiện
   được hệ thống trả sai.
4. **Tách phiên theo người dùng** (SQLite, `st.form(clear_on_submit=True)`) — trải nghiệm và
   điều kiện tiên quyết để hỏi nhiều lượt mà không lẫn ngữ cảnh.

**Chủ động KHÔNG làm:**

- **Không thêm LLM diễn đạt.** Lý do: LLM sẽ đặt "quyết định nguồn" vào chỗ không kiểm thử được —
  đúng cái rủi ro mà kiến trúc này sinh ra để tránh. Câu trả lời là **trích đoạn nguyên văn**
  kèm metadata (đơn vị, cấp, phiên bản, hiệu lực) nên người dùng tự kiểm chứng được.
- **Không dùng vector DB.** BM25 thuần Python đã đủ cho quy mô giả lập, và BM25 cho điểm từ khóa
  minh bạch hơn — thêm embedding lúc này chỉ thêm dependency và thêm chỗ có thể sai.
- **Không làm workflow duyệt/ban hành tài liệu.** Cần nghiệp vụ HR thật, vượt ngoài 3 ngày; nếu làm
  vội thì thành "form cho có" — hại nhiều hơn giúp.
- **Không tự động hóa việc gắn metadata.** Metadata là do con người gắn; tự đoán thì sai âm thầm
  và nguy hiểm hơn là bắt người dùng khai.

### Câu 2 — Thay đổi nào tạo ra khác biệt lớn nhất giữa M2 và M3? Bằng chứng nào?

**Khác biệt lớn nhất: quy tắc chọn bản áp dụng theo cấp tổ chức (B3).**

Lý do là vì nó thay đổi **kết quả trả lời**, không chỉ mở thêm khả năng:

| | M2 (cũ) | M3 (mới) |
|---|---|---|
| Cách đo "cấp" | `scope_depth` — độ sâu tuyệt đối của đơn vị trong cây tổ chức | khoảng cách tới đơn vị của **người hỏi** (`ancestors(user.unit)`) |
| Hệ quả với `appota` vs `media` | cùng depth 1 → tưởng là "cùng cấp" → `CONFLICT` | khác cấp → bản của công ty thành viên thắng, bản Tập đoàn bị thay thế |
| Tìm ứng viên | chỉ top-6 theo điểm BM25 | **toàn bộ** văn bản cùng `family` mà người hỏi được phép xem |

**Bằng chứng (cùng một câu hỏi, 3 người ở 3 cấp):**

> "Nhân viên được cử sang làm việc tại công ty thành viên khác tối đa bao nhiêu ngày?"

| Người hỏi | Cấp | M3 trả lời | M2 sẽ trả lời |
|---|---|---|---|
| Hoàng Minh (`appota`) | Group / Tập đoàn | **10 ngày** (`qd-cty-tv-appota`) | 10 ngày (đúng) |
| Nguyễn Anh (`media.nd.g1`) | Công ty Appota Media | **5 ngày** (`qd-cty-tv-media`) | ⚠️ **CONFLICT giả** |
| Phạm Đức (`tech.kt.be`) | Công ty Appota Tech | **7 ngày** (`qd-cty-tv-tech`) | ⚠️ **CONFLICT giả** |

Cột "M2 sẽ trả lời" là **mô phỏng lại đúng hàm `_select` của M2** trên bộ dữ liệu mới
(`git show c8c03cb:ragscope/engine.py`): cả hai đều rơi vào `CONFLICT` vì `scope_depth` bằng nhau.

Test chứng minh: **case T12–T15** (`tests/report.md`) + **7 test pytest** `test_b3_*` trong
`tests/test_mission3.py`. Regression M2 không hỏng: **15/15 case** + **25/25 test pytest**.

Khác biệt lớn thứ hai là `as_of`: cùng người, cùng câu hỏi "Quy định nghỉ phép" →
`as_of=2024-06-01` trả **12 ngày** (bản 2024.1), `as_of=2025-06-01` trả **16 ngày** (phụ lục phòng 2025.1).

### Câu 3 — Nếu đưa cho người dùng thật vào ngày mai, rủi ro/giới hạn lớn nhất còn lại là gì? Ưu tiên xử lý thế nào?

**Rủi ro lớn nhất: metadata sai hoặc thiếu.**
Cụ thể là `scope_units`, `unit` (đơn vị ban hành), `effective_from/to`, `family`, `scope_groups`.
Vì **mọi tầng phía sau đều dựa trên metadata**: lọc quyền, chọn phiên bản, đối chiếu cấp, coverage —
một ô sai thì hệ thống trả lời **đúng theo metadata sai**, và không có cơ chế nào phát hiện.
Người dùng thật nhận câu trả lời sai về chính sách lương/nghỉ phép — rủi ro pháp lý và uy tín,
không phải rủi ro "UX xấu".

Rủi ro thứ hai: **quy tắc "cấp gần hơn thắng" là giả định tổ chức.** Hiện tại suy ra từ cây tổ chức;
nếu một công ty ban hành quy định *chung* yếu hơn quy định của Tập đoàn thì hệ thống vẫn chọn
sai. Cần trường `priority` trong metadata thay vì suy luận.

**Thứ tự ưu tiên xử lý:**

1. **Chặn ở tầng dữ liệu (rẻ, hiệu quả nhất).** Validate lúc nạp: bắt buộc có `unit`, `scope_units`,
   `effective_from`, `family`; `scope_units` phải tồn tại trong `org.yaml`; `unit` phải thuộc
   `scope_units`. Sai → **từ chối nạp và báo sai ở đâu**, không cho lọt xuống tầng trả lời.
   Nguyên tắc: sai metadata ⇒ sai ngay ở tầng truy vấn, không phải ở câu trả lời.
2. **Dùng audit log để phát hiện sớm, không chỉ để lưu.** `data/audit.jsonl` đã ghi
   ai/đơn vị/câu hỏi/bản được chọn/đối chiếu cấp. Bước tiếp theo là báo cáo hằng tuần:
   câu nào hay bị `CONFLICT`, văn bản nào không bao giờ được dùng, câu nào có `coverage.partial`
   → đây chính là danh sách tài liệu cần sửa metadata.
3. **Workflow HR duyệt trước khi `status=active`.** Tài liệu chỉ được trả lời khi HR xác nhận
   metadata đúng và hiệu lực đã ban hành.
4. **Sau đó mới bổ sung `priority` cho B3** và mở rộng `family` thành quan hệ nhiều-nhiều
   (hiện là một `family` = một chủ đề).

Còn lại nhưng chưa ưu tiên: chưa có LLM diễn đạt (chấp nhận được — trích đoạn nguyên văn +
metadata là đủ kiểm chứng), dữ liệu giả lập đơn giản hơn thực tế, và BM25 chưa xử lý được
câu hỏi diễn đạt lệch (ví dụ "nghỉ phép thì được mấy ngày" → vẫn dựa vào từ khóa).

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
