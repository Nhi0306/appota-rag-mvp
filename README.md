# RAG Theo Quyền Truy Cập — MVP (Mission 2 + Mission 3)

MVP cho **Mission 2 — Appota NextGen AI Talent 2026**: chứng minh phần quan trọng nhất của giải pháp
"mỗi nhân sự nhận đúng tri thức, đúng bối cảnh, đúng phạm vi được phép" thực sự chạy.
Mission 3 bổ sung: truy vấn theo thời điểm hiệu lực, citation đầy đủ, audit log, phiên riêng theo
người dùng và **Change Request B3 — xử lý xung đột giữa các cấp tổ chức**.


> **Quan trọng:** toàn bộ dữ liệu trong repo này là **dữ liệu giả lập**. Không chứa API key, mật khẩu
> hay dữ liệu thật của Appota.

---

## 1. Phần quan trọng nhất được chọn để chứng minh

**Tầng lọc quyền chạy trước, "suy nghĩ" chạy sau.**

Theo quan điểm ở Mission 1, AI không được phép quyết định ai được xem gì — việc đó là code xác định, kiểm thử được.
Vì vậy MVP tập trung vào một vòng lặp lõi:

```
Câu hỏi + bối cảnh người dùng → lọc đúng phạm vi quyền → tìm đúng tri thức →
chọn đúng phiên bản hiệu lực → trả lời có nguồn / từ chối đúng cách
```

Và bắt buộc chứng minh: **cùng một câu hỏi, hai người có bối cảnh khác nhau → kết quả phù hợp khác nhau.**

## 2. Trải nghiệm nhanh

Chạy demo web:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Giao diện: chọn người dùng ở khung trái → gợi ý nhanh hoặc tự gõ câu hỏi → nhấn **Hỏi**.
Sau mỗi lượt hỏi, ô nhập **tự trống lại** (`st.form(clear_on_submit=True)`).
Mỗi người dùng có **một phiên riêng** lưu trong `data/chat.db`: lượt hỏi được dùng làm ngữ cảnh cho
câu hỏi tiếp theo ("vậy còn …?") nhưng **không hiện lại lịch sử** trên giao diện; có nút xóa phiên.

Chạy bộ kiểm thử (sinh `tests/report.md`):

```bash
python tests/run_tests.py
python -m pytest tests/ -q
```


## 3. Cấu trúc

```
appota-rag-mvp/
├─ app.py                  # giao diện Streamlit (chọn người dùng + ô nhập câu hỏi tự do)
├─ data/
│  ├─ org.yaml             # sơ đồ tổ chức 4 cấp: Tập đoàn → Công ty → Phòng → Nhóm
│  ├─ users.yaml           # 5 người dùng giả lập (2 phòng, 1 quản lý, 1 Group, 1 công ty khác)
│  ├─ documents.yaml       # 19 văn bản giả lập kèm metadata đầy đủ
│  ├─ chat.db              # phiên hỏi theo người dùng (SQLite, git-ignored)
│  └─ audit.jsonl          # nhật ký truy vấn (git-ignored)
├─ ragscope/               # engine thuần Python, không gọi API ngoài
│  ├─ data_loader.py       # load dữ liệu, lọc hiệu lực (usable), lọc phạm vi (visible)
│  ├─ org.py               # phân giải sơ đồ tổ chức, chuỗi cấp trên
│  ├─ bm25.py              # BM25 tự viết: word + char-bigram (hợp tiếng Việt, không cần segmenter)
│  ├─ engine.py            # vòng lặp trả lời + đối chiếu cấp + phát hiện mâu thuẫn + từ chối
│  ├─ scope_resolver.py    # chọn bản áp dụng theo cấp gần người hỏi nhất (Change Request B3)
│  ├─ chat_store.py        # lưu phiên SQLite theo user_id (tách biệt từng người)
│  ├─ conversation.py      # nhận diện & mở rộng câu hỏi nối tiếp bằng ngữ cảnh
│  ├─ text.py              # stopwords + hàm trích từ khóa nội dung
│  └─ models.py
├─ tests/
│  ├─ run_tests.py         # 15 tình huống, tự sinh báo cáo
│  ├─ test_mission3.py     # 17 test M3 (as-of, B3, citation, refusal, audit, coverage)
│  ├─ test_chat.py         # 8 test phiên/ngữ cảnh (tách phiên, lưu/đọc/xóa SQLite)
│  └─ report.md            # Kỳ vọng → Kết quả thực tế → Đạt/Chưa đạt → Điều học được
├─ docs/
│  └─ CAU_TRA_LOI_MISSION3.md
└─ Dockerfile              # để deploy lên bất kỳ nơi nào chạy được container
```


## 4. Cách engine làm việc (đọc 60 giây)

Mỗi văn bản có metadata: `unit` (đơn vị ban hành), `scope_units` (chuỗi đơn vị được phép),
`scope_groups` (nhóm quyền), `effective_from/to` (hiệu lực), `status` (active/draft/expired), `family` (chủ đề).

Pipeline mỗi câu hỏi (`ragscope/engine.py::answer`):

1. **Usable** — loại bản nháp (`draft`), bản hết hiệu lực (ngày hiệu lực > hôm nay).
2. **Visible (AND)** — người hỏi phải thỏa đồng thời: đơn vị của họ nằm trong `scope_units`
   (hoặc là con của đơn vị được cấp) **và** nếu có `scope_groups` thì nhóm quyền phải khớp.
3. **Retrieval** — chỉ tìm trong tập đã qua bước 1+2, bằng BM25 tự viết (token = từ + char-bigram,
   tiêu đề được nhân trọng số).
4. **Chặn trả nhầm chủ đề** — nếu văn bản khớp nhất toàn cục nằm ngoài quyền và điểm của văn bản
   trong quyền thấp hơn một nửa, hệ thống từ chối (không trả bừa văn bản yếu phù hợp).
5. **Chặn trả bừa** — nếu câu hỏi có từ đặc tả (ví dụ "mua sắm") mà không có văn bản nào chứa,
   hệ thống từ chối thay vì bịa.
6. **Đối chiếu cấp (Change Request B3)** — trong cùng chủ đề (`family`), hệ thống gom **toàn bộ** văn bản
   người hỏi được phép xem, rồi chọn bản của **cấp gần đơn vị của người hỏi nhất** (đo bằng khoảng cách
   tới đơn vị, không phải độ sâu tuyệt đối). Bản ở cấp xa hơn chỉ là quy định chung, bị bản đặc thù thay thế;
   giao diện hiển thị bảng "Đối chiếu giữa các cấp".
7. **Mâu thuẫn cùng cấp** — hai bản **cùng cấp**, cùng hiệu lực nhưng nội dung khác nhau → **CONFLICT**,
   nêu cả hai, không tự chọn.
8. **Trả lời có nguồn** — câu trả lời kèm tài liệu, phiên bản, ngày hiệu lực để người dùng tự kiểm chứng.
   Không đủ căn cứ → từ chối với câu trả lời dùng chung cho mọi lý do (không lộ việc "có tồn tại văn bản ngoài quyền").


## 5. Vì sao MVP không có LLM / không gọi API ngoài

- Phần **quyết định quyền, hiệu lực, mâu thuẫn** là code xác định — đúng thứ MVP cần chứng minh.
- Không gọi API ngoài → **chạy offline**, không cần key, không lộ dữ liệu ra ngoài, dễ tái lập kết quả.
- Phần paraphrase/tóm tắt của LLM là đẹp-để-có, không nằm trong giả thuyết quan trọng.

Nếu muốn thêm LLM: `engine.py` trả về văn bản + nguồn đã lọc sẵn, chỉ cần nối một model để diễn đạt lại
dựa trên dữ liệu đã được phép (không cho model "tự chọn" nguồn).

## 6. Bản chạy online

Hướng dẫn deploy nhanh bằng Streamlit Community Cloud:

1. Push repo này lên GitHub (đã có Dockerfile nếu bạn dùng nền tảng container).
2. Vào https://streamlit.io/cloud, chọn "Create app", kết nối repo.
3. Entry point: `app.py`. Không cần secrets (chạy offline).

> Nếu repo này chưa được deploy kèm link online tại thời điểm nộp, lý do: máy local của tác giả ở
> mạng giới hạn + chưa có tài khoản nền tảng deploy. Hướng dẫn trên đã đủ để chạy lại `app.py`.
> Không cần biến môi trường nào.

## 7. Hạn chế trung thực của MVP

- **Chưa có LLM** để diễn đạt tự nhiên — câu trả lời là trích đoạn văn bản, không "tóm tắt" mượt.
- **Chưa có cơ chế "mức tin cậy"**: khi câu hỏi chạm văn bản ngoài quyền, hệ thống trả lời đúng phần
  thuộc quyền nhưng chưa nói với người dùng rằng có thể chưa đầy đủ (case T10 — xem `tests/report.md`).
- **Metadata là chìa khóa**: nếu người quản trị gắn sai `scope_units`/ngày hiệu lực thì mọi tầng sau đều sai theo.
- Dữ liệu giả lập đơn giản hơn thực tế (ít văn bản trùng tên, ít tầng).

## 8. Kết quả kiểm thử

`tests/report.md` — **15/15 case đạt** (4 case "tốt", 3 case "khó/mơ hồ", 5 case "an toàn",
3 case "chưa xử lý tốt"). `pytest` — **25/25 test đạt**.

## 9. Mission 3 — Cải tiến + Change Request B3

Chạy test:

```bash
python -m pytest tests/ -q
python tests/run_tests.py
```

Cải tiến chính:
- Truy vấn theo thời điểm hiệu lực: `engine.answer(q, user, as_of=date(2024,6,1))`.
- Citation đầy đủ: đơn vị, cấp, phiên bản, hiệu lực, điểm, trích đoạn.
- Audit log: `data/audit.jsonl`.
- Mức độ đầy đủ (`coverage`, `confidence`) + ghi chú khi chưa đầy đủ.
- `explain()` và `version_diff()`.
- Phiên riêng theo người dùng trong SQLite (`data/chat.db`), ô nhập tự trống sau khi hỏi.

**Change Request B3 — xung đột giữa các cấp (Group vs công ty thành viên):**
cùng một câu hỏi, người hỏi ở cấp nào sẽ nhận quy định của đúng cấp đó.

| Người hỏi | Cấp | Kết quả |
|---|---|---|
| Hoàng Minh (`appota`) | Group / Tập đoàn | 10 ngày |
| Nguyễn Anh (`media.nd.g1`) | Công ty (Appota Media) | 5 ngày |
| Phạm Đức (`tech.kt.be`) | Công ty (Appota Tech) | 7 ngày |

Chi tiết quyết định: `docs/CAU_TRA_LOI_MISSION3.md`.

