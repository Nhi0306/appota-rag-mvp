from __future__ import annotations

import re

from .text import substantive_words

# Từ/dấu hiệu câu hỏi tiếp nối, cần dựa vào lượt hỏi trước để hiểu đề tài.
# Chỉ giữ các từ nối/đại từ thật sự trỏ ngược ("vậy", "còn", "nó"...).
# Tránh các từ quá chung như "về", "của", "thế" vì gần như mọi câu hỏi đều chứa.
ANAPHORA = {
    "vậy", "va", "còn", "con", "nó", "no", "ấy", "ấy", "kia", "ki",
    "chứ", "chua", "nữa", "nua", "vẫn", "van", "luôn", "luon", "rồi", "roi",
}

FOLLOWUP_MIN_TERMS = 2
FOLLOWUP_MAX_TERMS_WITH_ANAPHORA = 4


def _norm(text: str) -> str:
    return re.sub(r"[^\w\s]", " ", text.lower())


def is_followup(question: str, context=None) -> bool:
    """Câu hỏi có phụ thuộc lượt hỏi trước không.

    Ba dấu hiệu:
      1. Rất ít từ khóa riêng (<= FOLLOWUP_MIN_TERMS) → chắc chắn là nối tiếp.
      2. Chứa từ/đại từ trỏ ngược (ANAPHORA) → nối tiếp.
      3. Có từ trỏ ngược nhưng số từ khóa riêng vẫn nhiều
         (FOLLOWUP_MIN_TERMS < số từ <= FOLLOWUP_MAX_TERMS_WITH_ANAPHORA)
         → vẫn coi là nối tiếp, vì câu hỏi chưa đủ thông tin riêng.
    """
    terms = substantive_words(question)
    if len(terms) <= FOLLOWUP_MIN_TERMS:
        return True
    norm = _norm(question)
    has_anaphora = any(
        re.search(rf"(?<!\w){re.escape(token)}(?!\w)", norm) for token in ANAPHORA
    )
    if not has_anaphora:
        return False
    return len(terms) <= FOLLOWUP_MAX_TERMS_WITH_ANAPHORA



def _previous_question(context) -> str:
    """Lấy câu hỏi của lượt gần nhất đã trả lời được (bỏ qua lượt bị từ chối)."""
    if not context:
        return ""
    for turn in reversed(list(context)):
        kind = turn.get("answer_kind") if isinstance(turn, dict) else None
        if kind == "REFUSE":
            continue
        q = turn.get("question") if isinstance(turn, dict) else str(turn)
        if q:
            return q
    return ""


def expand_with_context(question: str, context=None) -> tuple:
    """Trả về (câu hỏi dùng để tìm kiếm, danh sách câu hỏi đã dùng làm ngữ cảnh)."""
    if not context:
        return question, []
    if not is_followup(question, context):
        return question, []
    prev = _previous_question(context)
    if not prev:
        return question, []
    return f"{question} {prev}", [prev]
