# -*- coding: utf-8 -*-
"""Mission 3 tests: improvements + change request + edge cases + regression."""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ragscope import Engine

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

engine = Engine(DATA)


def U(uid):
    return engine.user_by_id(uid)


def test_regression_same_question_different_users():
    a1 = engine.answer("Quy định nghỉ phép của tôi như thế nào?", U("u_nguyen_anh"))
    a2 = engine.answer("Quy định nghỉ phép của tôi như thế nào?", U("u_tran_binh"))
    assert a1.kind == "OK" and a2.kind == "OK"
    assert "16 ngày" in a1.text
    assert "14 ngày" in a2.text
    assert "16 ngày" not in a2.text


def test_change_request_as_of_effective_date():
    u = U("u_nguyen_anh")
    past = engine.answer("Quy định nghỉ phép của tôi như thế nào?", u, as_of=date(2024, 6, 1))
    assert past.kind == "OK", past.kind
    assert "12 ngày" in past.text
    assert any(s.version == "2024.1" for s in past.sources)
    assert past.as_of == date(2024, 6, 1)

    current = engine.answer("Quy định nghỉ phép của tôi như thế nào?", u, as_of=date(2025, 6, 1))
    assert current.kind == "OK"
    assert "16 ngày" in current.text
    assert any(s.version == "2025.1" for s in current.sources)


def test_edge_case_conflict_unresolved():
    u = U("u_nguyen_anh")
    a = engine.answer("Chính sách làm việc từ xa cho tôi được bao nhiêu ngày?", u)
    assert a.kind == "CONFLICT"
    assert len(a.sources) == 2
    assert "2 ngày" in a.text
    assert "3 ngày" in a.text


def test_citation_has_version_and_effective_window():
    u = U("u_le_chi")
    a = engine.answer("Ngân sách quý 1 của công ty là bao nhiêu?", u)
    assert a.kind == "OK"
    assert len(a.sources) >= 1
    s = a.sources[0]
    assert s.version
    assert s.effective_from is not None
    assert s.unit_name
    assert s.snippet
    assert s.score >= 0
    assert s.as_of == a.as_of


def test_refusal_out_of_scope_no_leak():
    u = U("u_tran_binh")
    a = engine.answer("Ngân sách quý 1 của công ty là bao nhiêu?", u)
    assert a.kind == "REFUSE"
    assert a.reason == "out_of_scope"
    assert "1,2 tỷ" not in a.text


def test_refusal_missing_data():
    u = U("u_nguyen_anh")
    a = engine.answer("Quy trình mua sắm của công ty như thế nào?", u)
    assert a.kind == "REFUSE"
    assert a.reason == "no_source"


def test_access_explanation():
    u = U("u_tran_binh")
    r = engine.explain("qd-ngan-sach-q1-media", u.id)
    assert r["visible"] is False
    assert "out_of_scope_unit" in r["reasons"] or "out_of_scope_group" in r["reasons"]

    r2 = engine.explain("qd-ngan-sach-q1-media", U("u_le_chi").id)
    assert r2["visible"] is True
    assert r2["reasons"] == []


def test_version_diff():
    d = engine.version_diff("qd-wfh-a", "qd-wfh-b")
    assert d["doc_a"] == "qd-wfh-a"
    assert d["doc_b"] == "qd-wfh-b"
    assert "2 ngày" in " ".join(d["removed"]) or "3 ngày" in " ".join(d["added"]) or not d["identical"]
    assert d["identical"] is False


def test_audit_log_written():
    before = 0
    if os.path.exists(engine.audit.path):
        with open(engine.audit.path, encoding="utf-8") as f:
            before = sum(1 for _ in f)
    engine.answer("Nghỉ lễ năm 2026 có bao nhiêu ngày?", U("u_pham_duc"))
    with open(engine.audit.path, encoding="utf-8") as f:
        after = sum(1 for _ in f)
    assert after == before + 1


def test_partial_coverage_note():
    u = U("u_nguyen_anh")
    a = engine.answer("Tăng ca được tính như thế nào?", u)
    assert a.kind == "OK"
    # coverage recorded
    assert isinstance(a.coverage, dict)
    assert "found" in a.coverage


# ------------------------------------------------------------------
# CHANGE REQUEST B3 — xung đột giữa các cấp (Group vs công ty thành viên)
# ------------------------------------------------------------------

Q_CTY_TV = "Nhân viên được cử sang làm việc tại công ty thành viên khác tối đa bao nhiêu ngày?"


def test_b3_group_level_uses_group_rule():
    """Cấp Group (appota) → áp dụng quy định của Tập đoàn (10 ngày)."""
    a = engine.answer(Q_CTY_TV, U("u_hoang_minh"))
    assert a.kind == "OK", a.kind
    assert "10 ngày" in a.text
    assert "5 ngày" not in a.text
    assert "7 ngày" not in a.text
    assert a.debug["chosen"] == "qd-cty-tv-appota"


def test_b3_company_level_uses_company_rule():
    """Cấp công ty thành viên → áp dụng quy định riêng của công ty (Media 5 ngày)."""
    a = engine.answer(Q_CTY_TV, U("u_nguyen_anh"))
    assert a.kind == "OK", a.kind
    assert "5 ngày" in a.text
    assert "10 ngày" not in a.text
    assert a.debug["chosen"] == "qd-cty-tv-media"


def test_b3_other_company_uses_its_own_rule():
    """Cấu trúc khác (tech) vẫn dùng đúng quy định của công ty mình (7 ngày)."""
    a = engine.answer(Q_CTY_TV, U("u_pham_duc"))
    assert a.kind == "OK", a.kind
    assert "7 ngày" in a.text
    assert "10 ngày" not in a.text
    assert a.debug["chosen"] == "qd-cty-tv-tech"


def test_b3_same_level_conflict_is_not_silently_chosen():
    """Hai bản CÙNG cấp cùng hiệu lực nhưng khác nội dung → CONFLICT, không tự chọn."""
    a = engine.answer("Chính sách làm việc từ xa cho tôi được bao nhiêu ngày?", U("u_hoang_minh"))
    assert a.kind == "CONFLICT", a.kind
    assert len(a.sources) == 2
    assert "2 ngày" in a.text and "3 ngày" in a.text
    assert a.scope["conflict"] is True


def test_b3_scope_reports_applied_and_other_levels():
    """Bản đối chiếu cấp cho biết bản nào áp dụng, bản nào bị thay thế."""
    a = engine.answer(Q_CTY_TV, U("u_nguyen_anh"))
    applied = {x["doc_id"] for x in a.scope["applied"]}
    others = {x["doc_id"] for x in a.scope["other_levels"]}
    assert applied == {"qd-cty-tv-media"}
    assert "qd-cty-tv-appota" in others
    # Không lộ nội dung (số ngày) của bản không áp dụng trong câu trả lời.
    assert "10 ngày" not in a.text


def test_b3_scope_levels_api():
    """API đối chiếu cấp: bản gần người hỏi nhất được đánh dấu áp dụng."""
    rows = engine.scope_levels("u_nguyen_anh", family="cong-vi-cong-bo")
    ids = [r["doc_id"] for r in rows]
    assert "qd-cty-tv-media" in ids
    on = [r for r in rows if r["applies"]]
    assert [r["doc_id"] for r in on] == ["qd-cty-tv-media"]
    assert on[0]["distance"] == 2  # media.nd.g1 → media.nd → media
    others = [r for r in rows if not r["applies"]]
    assert others and "gần bạn hơn" in others[0]["reason"]


def test_b3_regression_same_question_same_family_different_levels():
    """Regression: cùng câu hỏi, mức áp dụng khác nhau theo đơn vị của người hỏi."""
    a_group = engine.answer(Q_CTY_TV, U("u_hoang_minh"))
    a_media = engine.answer(Q_CTY_TV, U("u_nguyen_anh"))
    a_tech = engine.answer(Q_CTY_TV, U("u_pham_duc"))
    assert "10 ngày" in a_group.text
    assert "5 ngày" in a_media.text
    assert "7 ngày" in a_tech.text
    for a in (a_group, a_media, a_tech):
        assert a.kind == "OK"
        assert a.scope["family"] == "cong-vi-cong-bo"
        assert a.scope["chosen"]["doc_id"] in a.scope["applied"][0]["doc_id"]
