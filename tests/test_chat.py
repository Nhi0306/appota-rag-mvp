# -*- coding: utf-8 -*-
"""Mission 3 — kiểm thử lưu phiên theo người dùng (SQLite)."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ragscope.chat_store import ChatStore
from ragscope.conversation import expand_with_context, is_followup
from ragscope import Engine

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

engine = Engine(DATA)


def _store():
    tmpdir = tempfile.mkdtemp(prefix="ragscope-chat-")
    return ChatStore(os.path.join(tmpdir, "chat.db"))


def test_turns_are_isolated_per_user():
    store = _store()
    store.add_turn("u_a", "A", "media", "Câu hỏi của A", "Câu hỏi của A",
                   "OK", "trả lời A", "ok", [], None, [])
    store.add_turn("u_b", "B", "tech", "Câu hỏi của B", "Câu hỏi của B",
                   "OK", "trả lời B", "ok", [], None, [])
    assert store.count("u_a") == 1
    assert store.count("u_b") == 1
    turns_a = store.recent_turns("u_a")
    assert len(turns_a) == 1
    assert turns_a[0]["question"] == "Câu hỏi của A"
    assert "B" not in turns_a[0]["answer_text"]
    store.close()


def test_recent_turns_order_and_limit():
    store = _store()
    for i in range(5):
        store.add_turn("u_a", "A", "media", f"Q{i}", f"Q{i}", "OK", f"A{i}", "ok", [], None, [])
    turns = store.recent_turns("u_a", limit=3)
    assert [t["question"] for t in turns] == ["Q2", "Q3", "Q4"]
    store.close()


def test_scope_is_persisted_and_readable():
    store = _store()
    scope = {"family": "cong-vi-cong-bo", "chosen": {"doc_id": "qd-cty-tv-media"},
             "applied": [{"doc_id": "qd-cty-tv-media"}], "other_levels": [], "conflict": False}
    store.add_turn("u_a", "A", "media.nd", "Q", "Q", "OK", "A", "ok", [], None, [], scope=scope)
    turn = store.recent_turns("u_a")[0]
    assert turn["scope"]["family"] == "cong-vi-cong-bo"
    assert turn["scope"]["chosen"]["doc_id"] == "qd-cty-tv-media"
    store.close()


def test_clear_only_removes_own_user():
    store = _store()
    store.add_turn("u_a", "A", "media", "Q", "Q", "OK", "A", "ok", [], None, [])
    store.add_turn("u_b", "B", "tech", "Q", "Q", "OK", "B", "ok", [], None, [])
    removed = store.clear("u_a")
    assert removed == 1
    assert store.count("u_a") == 0
    assert store.count("u_b") == 1
    store.close()


def test_persistence_across_reopen():
    tmpdir = tempfile.mkdtemp(prefix="ragscope-chat-")
    path = os.path.join(tmpdir, "chat.db")
    s1 = ChatStore(path)
    s1.add_turn("u_a", "A", "media", "Q", "Q", "OK", "A", "ok", [], None, [])
    s1.close()
    s2 = ChatStore(path)
    assert s2.count("u_a") == 1
    s2.close()


def test_followup_uses_previous_turn_as_context():
    store = _store()
    ctx = [{"question": "Quy định nghỉ phép của tôi như thế nào?",
            "answer_kind": "OK", "answer_text": "..."}]
    eff, used = expand_with_context("Vậy còn bao nhiêu ngày?", ctx)
    assert used == ["Quy định nghỉ phép của tôi như thế nào?"]
    assert "nghỉ phép" in eff.lower()
    store.close()


def test_standalone_question_is_not_expanded():
    ctx = [{"question": "Quy định nghỉ phép của tôi như thế nào?",
            "answer_kind": "OK", "answer_text": "..."}]
    eff, used = expand_with_context("Ngân sách quý 1 của công ty là bao nhiêu?", ctx)
    assert used == []
    assert eff == "Ngân sách quý 1 của công ty là bao nhiêu?"


def test_is_followup_rules():
    assert is_followup("Vậy thì sao?") is True
    assert is_followup("Còn nghỉ phép thì sao?") is True
    assert is_followup("Quy trình triển khai Backend của nhóm kỹ thuật thế nào?") is False
    assert is_followup("Ngân sách quý 1 của công ty là bao nhiêu?") is False
