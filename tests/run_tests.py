# -*- coding: utf-8 -*-
"""Suite kiểm thử Mission 2 — tự chạy bằng Python thuần, không cần pytest.

Cách dùng:
    python tests/run_tests.py

Sinh ra tests/report.md theo đúng format bắt buộc:
    Kỳ vọng → Kết quả thực tế → Đạt/Chưa đạt → Điều học được

Bộ case bao phủ các loại bắt buộc:
    - tốt (cùng câu hỏi, hai bối cảnh khác nhau → kết quả khác nhau)
    - khó / dữ liệu mơ hồ (mâu thuẫn phiên bản, loại bản hết hạn/bản nháp)
    - chưa xử lý tốt / thất bại (trả lời thiếu tính đầy đủ, từ chối ngoài phạm vi)
"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ragscope import Engine  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
REPORT = os.path.join(BASE, "tests", "report.md")

engine = Engine(DATA)

Q_CTY_TV = "Nhân viên được cử sang làm việc tại công ty thành viên khác tối đa bao nhiêu ngày?"


def u(user_id):
    return engine.user_by_id(user_id)


def ok(text):
    return text


def no(text):
    return text not in text  # placeholder, không dùng


CASES = [
    dict(
        id="T1",
        group="tốt",
        name="Cùng một câu hỏi, hai bối cảnh khác nhau phải cho kết quả khác nhau",
        user="u_nguyen_anh",
        question="Quy định nghỉ phép của tôi như thế nào?",
        expect={
            "kind": "OK",
            "chosen": "qd-nghi-phep-phu-luc-nd",
            "contains": ["16 ngày"],
            "not_contains": ["12 ngày"],
            "has_source": True,
        },
        lesson=(
            "Phần lõi hoạt động: cùng câu hỏi, nhân sự Phòng Nội Dung nhận phụ lục riêng 16 ngày. "
            "Bản đặc thù (phạm vi sâu hơn) thắng bản chung. Đây chính là thứ giả thuyết cần chứng minh."
        ),
    ),
    dict(
        id="T2",
        group="tốt",
        name="Nhân sự đơn vị khác (Kế Toán) nhận đúng bản chung của mình",
        user="u_tran_binh",
        question="Quy định nghỉ phép của tôi như thế nào?",
        expect={
            "kind": "OK",
            "chosen": "qd-nghi-phep-2025",
            "contains": ["14 ngày"],
            "not_contains": ["16 ngày", "16 ngày phép"],
            "has_source": True,
        },
        lesson=(
            "Phụ lục của Phòng Nội Dung không lọt vào ngữ cảnh của người ngoài phòng: "
            "lọc phạm vi chạy trước khi tìm kiếm nên không cần dựa vào AI để ‘tự biết’."
        ),
    ),
    dict(
        id="T3",
        group="tốt",
        name="Văn bản áp dụng chung toàn Tập đoàn",
        user="u_pham_duc",
        question="Nghỉ lễ năm 2026 có bao nhiêu ngày?",
        expect={"kind": "OK", "chosen": "qd-nghi-le-2026", "contains": ["11 ngày"], "has_source": True},
        lesson="Tài liệu phạm vi appota (toàn Tập đoàn) nhân viên bất kỳ đơn vị nào cũng truy cập được.",
    ),
    dict(
        id="T4",
        group="tốt",
        name="Người quản lý được truy cập tài liệu nhạy cảm theo nhóm quyền manager",
        user="u_le_chi",
        question="Ngân sách quý 1 của công ty là bao nhiêu?",
        expect={
            "kind": "OK",
            "chosen": "qd-ngan-sach-q1-media",
            "contains": ["1,2 tỷ"],
            "not_contains": ["quyền"],
            "has_source": True,
        },
        lesson=(
            "Nhóm quyền quản lý mở thêm tài liệu nhạy cảm. Điều kiện là AND (đơn vị media VÀ nhóm manager) "
            "nên không xảy ra tình trạng ‘đúng đơn vị nhưng thiếu nhóm’."
        ),
    ),
    dict(
        id="T5",
        group="khó",
        name="Mâu thuẫn phiên bản cùng hiệu lực → KHÔNG tự chọn",
        user="u_nguyen_anh",
        question="Chính sách làm việc từ xa cho tối đa mấy ngày 1 tuần?",
        expect={"kind": "CONFLICT", "n_sources": 2, "contains": ["2 ngày", "3 ngày"]},
        lesson=(
            "Hai văn bản cùng hiệu lực nội dung khác nhau (2 vs 3 ngày). Hệ thống nêu cả hai và yêu cầu xác nhận "
            "thay vì đoán bừa. Kết luận: để con người chốt, không để AI quyết thay."
        ),
    ),
    dict(
        id="T6",
        group="khó",
        name="Bản hết hạn (2024) và bản nháp (2026) không bao giờ được dùng để trả lời",
        user="u_nguyen_anh",
        question="Quy định nghỉ phép của tôi như thế nào?",
        expect={
            "kind": "OK",
            "not_contains": ["12 ngày", "15 ngày phép", "bản nháp"],
            "no_source_ids": ["qd-nghi-phep-2024", "ban-nhap-qd-nghi-phep-2026"],
        },
        lesson=(
            "Trạng thái hiệu lực và trạng thái bản nháp được lọc ở tầng dữ liệu (usable) nên model/đoạn mã không bao "
            "giờ nhìn thấy chúng. Nguyên tắc: sai metadata/hiệu lực thì sai ngay ở tầng truy vấn, không phải ở câu trả lời."
        ),
    ),
    dict(
        id="T7",
        group="an-toan",
        name="Câu hỏi nhạy cảm ngoài quyền → từ chối và KHÔNG lộ số liệu",
        user="u_tran_binh",
        question="Ngân sách quý 1 của công ty là bao nhiêu?",
        expect={
            "kind": "REFUSE",
            "reason": "out_of_scope",
            "not_contains": ["1,2 tỷ", "45%", "500 triệu"],
        },
        lesson=(
            "Khi văn bản đúng chủ đề nằm ngoài quyền, hệ thống từ chối với câu trả lời chung chung — "
            "không hề lộ việc ‘có tồn tại một con số ngân sách’. Lý do chi tiết chỉ ghi ở log nội bộ."
        ),
    ),
    dict(
        id="T8",
        group="an-toan",
        name="Câu hỏi đúng chủ đề nhưng văn bản thuộc đơn vị khác → từ chối, không trả nhầm",
        user="u_tran_binh",
        question="Quy trình triển khai Backend của nhóm kỹ thuật thế nào?",
        expect={"kind": "REFUSE", "reason": "out_of_scope"},
        lesson=(
            "Từ khóa ‘triển khai’ rất khớp với quy trình Backend nhưng bản đó chỉ cho nhóm Backend. "
            "Nhờ kiểm tra ‘văn bản đúng nhất thế giới có nằm trong quyền không’ trước khi trả lời, "
            "hệ thống chọn từ chối thay vì đoán." 
        ),
    ),
    dict(
        id="T9",
        group="thất-bại",
        name="Thiếu dữ liệu hoàn toàn → từ chối sạch",
        user="u_nguyen_anh",
        question="Quy trình mua sắm của công ty như thế nào?",
        expect={"kind": "REFUSE", "reason": "no_source"},
        lesson=(
            "Không tồn tại văn bản nào về mua sắm. Có ít nhất một từ đặc tả (‘mua sắm’) không trùng bất kỳ văn bản "
            "nào trong quyền → chặn để không đoán bừa ‘theo quy trình…’."
        ),
    ),
    dict(
        id="T10",
        group="thất-bại",
        name="Tăng ca: trả lời đúng quy trình nhưng THIẾU hệ số lương vì bản hệ số ngoài quyền",
        user="u_nguyen_anh",
        question="Tăng ca được tính thế nào?",
        expect={
            "kind": "OK",
            "contains": ["Quy trình đăng ký tăng ca", "trưởng phòng"],
            "misses": ["1,5 lần lương", "1.5 lần lương", "2 lần vào cuối tuần"],
        },
        lesson=(
            "Trả lời đúng phần thuộc quyền (quy trình đăng ký của Phòng Nội Dung) nhưng không trả lời được hệ số lương "
            "vì bản quy định hệ số là của Appota Tech. Đây là hạn chế thật của MVP: chưa có cơ chế nói với người dùng "
            "rằng câu trả lời có thể chưa đầy đủ. Hướng khắc phục ở Mission 3: thêm trạng thái mức tin cậy + đường dẫn hỏi HR."
        ),
    ),
    dict(
        id="T11",
        group="an-toan",
        name="Tài liệu nội bộ của một nhóm không lọt sang người khác",
        user="u_tran_binh",
        question="Kế hoạch nội dung SEO của Nhóm Nội Dung 1 tháng 1 là gì?",
        expect={"kind": "REFUSE"},
        lesson="Biên bản họp nhóm g1 là tài liệu chỉ nhóm ấy xem; người phòng khác bị từ chối đồng nhất với mọi trường hợp từ chối khác.",
    ),
    # ---- CHANGE REQUEST B3: xung đột giữa các cấp ----
    dict(
        id="T12",
        group="tốt",
        name="B3 — cấp Group áp dụng quy định của Tập đoàn (10 ngày)",
        user="u_hoang_minh",
        question=Q_CTY_TV,
        expect={
            "kind": "OK",
            "chosen": "qd-cty-tv-appota",
            "contains": ["10 ngày"],
            "not_contains": ["5 ngày", "7 ngày"],
            "has_source": True,
        },
        lesson=(
            "Người hỏi ở cấp Group không được tự động dùng quy định của công ty thành viên. "
            "Mức áp dụng phải theo đúng cấp của người hỏi."
        ),
    ),
    dict(
        id="T13",
        group="tốt",
        name="B3 — cấp công ty thành viên dùng quy định riêng (Media 5 ngày), không phải mức chung 10 ngày",
        user="u_nguyen_anh",
        question=Q_CTY_TV,
        expect={
            "kind": "OK",
            "chosen": "qd-cty-tv-media",
            "contains": ["5 ngày"],
            "not_contains": ["10 ngày", "7 ngày"],
            "has_source": True,
        },
        lesson=(
            "Bản đặc thù của công ty thay bản chung của Tập đoàn. Trước B3, hệ thống so độ sâu tuyệt đối "
            "(appota và media cùng depth 1) nên báo CONFLICT giả cho câu hỏi này."
        ),
    ),
    dict(
        id="T14",
        group="khó",
        name="B3 — hai bản CÙNG cấp, cùng hiệu lực, khác nội dung → vẫn phải báo CONFLICT",
        user="u_hoang_minh",
        question="Chính sách làm việc từ xa cho tôi được bao nhiêu ngày?",
        expect={"kind": "CONFLICT", "n_sources": 2, "contains": ["2 ngày", "3 ngày"]},
        lesson=(
            "B3 chỉ giải quyết mâu thuẫn GIỮA các cấp. Mâu thuẫn trong cùng một cấp vẫn phải đưa ra "
            "cho người dùng xác nhận — không tự chọn."
        ),
    ),
    dict(
        id="T15",
        group="an-toan",
        name="B3 — câu trả lời không lộ nội dung của bản ở cấp khác (không rò số ngày của Tập đoàn)",
        user="u_nguyen_anh",
        question=Q_CTY_TV,
        expect={"kind": "OK", "not_contains": ["10 ngày"], "has_source": True},
        lesson=(
            "Khi nêu đối chiếu các cấp, hệ thống chỉ nêu TÊN văn bản và cấp của bản không áp dụng, "
            "không trích số liệu của bản đó — tránh gây hiểu nhầm là nhiều mức áp dụng cùng lúc."
        ),
    ),
]


def run_case(c):
    u = engine.user_by_id(c["user"])
    a = engine.answer(c["question"], u)
    exp = c["expect"]
    checks = []
    results = []

    checks.append(("kind", a.kind == exp["kind"], exp["kind"], a.kind))
    if "reason" in exp:
        checks.append(("reason", a.reason == exp["reason"], exp["reason"], a.reason))
    if "chosen" in exp:
        checks.append(("chosen", a.debug["chosen"] == exp["chosen"], exp["chosen"], a.debug["chosen"]))
    for s in exp.get("contains", []):
        checks.append(("contains: " + s, s in a.text, s, a.text[:200]))
    for s in exp.get("not_contains", []):
        checks.append(("not_contains: " + s, s not in a.text, s, a.text[:200]))
    if "n_sources" in exp:
        checks.append(("n_sources", len(a.sources) == exp["n_sources"], exp["n_sources"], len(a.sources)))
    if "has_source" in exp:
        checks.append(("has_source", len(a.sources) >= 1, ">=1", len(a.sources)))
    if "no_source_ids" in exp:
        ids = {s.doc_id for s in a.sources}
        checks.append(("no_source_ids", not set(exp["no_source_ids"]) & ids, exp["no_source_ids"], sorted(ids)))
    if "misses" in exp:
        checks.append(("misses (những thứ CHƯA có)", all(x not in a.text for x in exp["misses"]), exp["misses"], a.text[:160]))

    passed = all(p for _, p, _, _ in checks)
    actual = " | ".join(f"{k}: {'DUNG' if p else 'SAI'} ({e} -> {g})" for k, p, e, g in checks)
    return passed, actual


def main():
    lines = []
    lines.append("# Bộ kiểm thử Mission 2")
    lines.append("")
    lines.append("Số case: %d (yêu cầu tối thiểu 5)." % len(CASES))
    lines.append("")
    lines.append("| ID | Kỳ vọng | Kết quả thực tế | Đạt/Chưa đạt | Điều học được |")
    lines.append("|---|---|---|---|---|")
    npass = 0
    for c in CASES:
        passed, actual = run_case(c)
        lines.append(
            "| %s (%s) | %s | %s | %s | %s |"
            % (c["id"], c["group"], c["name"], actual, "Đạt" if passed else "Chưa đạt", c["lesson"])
        )
        npass += int(passed)
    lines.append("")
    lines.append("**Tổng kết: %d/%d case đạt.**" % (npass, len(CASES)))
    lines.append("")
    lines.append("Danh mục nhóm case: tốt · khó · an-toàn · thất-bại (để trung thực về giới hạn MVP).")
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))
    print("\nSaved:", REPORT)


if __name__ == "__main__":
    main()