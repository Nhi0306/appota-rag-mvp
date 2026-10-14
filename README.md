# RAG Theo Quyền Truy Cập — MVP (Mission 2)

MVP cho **Mission 2 — Appota NextGen AI Talent 2026**: chứng minh phần quan trọng nhất của giải pháp
"mỗi nhân sự nhận đúng tri thức, đúng bối cảnh, đúng phạm vi được phép" thực sự chạy.

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

Giao diện: chọn người dùng ở khung trái → gợi ý nhanh hoặc tự gõ câu hỏi → nhấn Enter. **5 lượt hỏi
gần nhất** được giữ lại (có nút xóa lịch sử) để không mất kết quả cũ khi hỏi câu mới.

Chạy bộ kiểm thử (sinh `tests/report.md`):

```bash
python tests/run_tests.py
```

## 3. Cấu trúc

```
appota-rag-mvp/
├─ app.py                  # giao diện Streamlit (chọn người dùng + ô nhập câu hỏi tự do)
├─ data/
│  ├─ org.yaml             # sơ đồ tổ chức 4 cấp: Tập đoàn → Công ty → Phòng → Nhóm
│  ├─ users.yaml           # 4 người dùng giả lập (2 phòng, 1 quản lý, 1 công ty khác)
│  └─ documents.yaml       # 16 văn bản giả lập kèm metadata đầy đủ
├─ ragscope/               # engine thuần Python, không gọi API ngoài
│  ├─ data_loader.py       # load dữ liệu, lọc hiệu lực (usable), lọc phạm vi (visible)
│  ├─ org.py               # phân giải sơ đồ tổ chức, chuỗi cấp trên
│  ├─ bm25.py              # BM25 tự viết: word + char-bigram (hợp tiếng Việt, không cần segmenter)
│  ├─ engine.py            # vòng lặp trả lời + phát hiện mâu thuẫn + từ chối
│  └─ models.py
├─ tests/
│  ├─ run_tests.py         # 11 tình huống, tự sinh báo cáo
│  └─ report.md            # Kỳ vọng → Kết quả thực tế → Đạt/Chưa đạt → Điều học được
├─ docs/
│  ├─ CAU_TRA_LOI_MISSION2.md
│  └─ VIDEO_SCRIPT.md
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
6. **Chọn bản** — trong cùng chủ đề (`family`): bản đặc thù (phạm vi sâu hơn) thắng bản chung;
   nếu hai bản cùng hiệu lực, cùng phạm vi mà nội dung khác nhau → **CONFLICT**, nêu cả hai, không tự chọn.
7. **Trả lời có nguồn** — câu trả lời kèm tài liệu, phiên bản, ngày hiệu lực để người dùng tự kiểm chứng.
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

`tests/report.md` — **11/11 case đạt**, bao gồm: 4 case "tốt", 2 case "khó/mơ hồ", 4 case "an toàn",
1 case "chưa xử lý tốt" (thất bại trung thực).