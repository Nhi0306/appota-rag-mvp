# -*- coding: utf-8 -*-
import html
import os
import sys
from dataclasses import asdict

import streamlit as st

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from ragscope import Engine  # noqa: E402
from ragscope.chat_store import ChatStore  # noqa: E402

DATA = os.path.join(BASE, "data")
CONTEXT_TURNS = 5  # số lượt hỏi gần nhất dùng làm ngữ cảnh cho câu hỏi tiếp theo


@st.cache_resource
def get_engine():
    return Engine(DATA)


@st.cache_resource
def get_store():
    return ChatStore(os.path.join(DATA, "chat.db"))


engine = get_engine()
store = get_store()

st.set_page_config(
    page_title="Tri thức theo quyền — MVP",
    page_icon=":material/shield_person:",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
:root {
  --ink: #111827;
  --muted: #6b7280;
  --line: #e5e7eb;
  --primary: #4f46e5;
}
.block-container {padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1080px;}

.app-hero {
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 22px 26px;
  background: linear-gradient(135deg, #eef2ff 0%, #ffffff 60%);
  margin-bottom: 6px;
}
.app-hero h1 {font-size: 1.75rem; margin: 0 0 6px 0; color: var(--ink); letter-spacing: -0.02em;}
.app-hero p {margin: 0; color: var(--muted); font-size: 0.95rem; line-height: 1.5;}

.persona {
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 16px 16px 14px 16px;
  background: #ffffff;
}
.persona .avatar {
  width: 44px; height: 44px; border-radius: 12px;
  background: var(--primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1.05rem; margin-bottom: 10px;
}
.persona .name {font-weight: 700; color: var(--ink); font-size: 1.02rem;}
.persona .role {color: var(--muted); font-size: 0.86rem; margin-bottom: 10px;}
.chip {
  display: inline-block; padding: 3px 10px; border-radius: 999px;
  font-size: 0.75rem; font-weight: 600; margin: 2px 4px 2px 0;
}
.chip-unit {background: #eef2ff; color: #3730a3;}
.chip-group {background: #ecfdf5; color: #047857;}
.chip-none {background: #f3f4f6; color: #6b7280;}

.qmeta {font-size: 0.8rem; color: var(--muted); margin-bottom: 2px;}
.qmeta .who {font-weight: 700; color: var(--primary);}
.qtext {font-size: 0.98rem; color: var(--ink); font-weight: 600; margin-bottom: 10px;}
.hist-item {
  border: 1px solid var(--line); border-radius: 16px; padding: 16px 18px;
  background: #ffffff; margin-bottom: 12px;
}
.hist-head {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; margin-bottom: 8px;
}
.turn-tag {
  font-size: 0.72rem; font-weight: 700; letter-spacing: 0.04em;
  text-transform: uppercase; color: #9ca3af;
}

.answer-card {
  border: 1px solid var(--line);
  border-left: 5px solid var(--accent, #6b7280);
  border-radius: 12px;
  padding: 14px 16px;
  background: #ffffff;
  margin-bottom: 12px;
}
.answer-body {white-space: pre-wrap; color: var(--ink); font-size: 0.98rem; line-height: 1.6;}
.badge {
  display: inline-block; padding: 4px 12px; border-radius: 999px;
  font-size: 0.72rem; font-weight: 700; letter-spacing: 0.03em;
  text-transform: uppercase; margin-bottom: 10px;
}
.badge-ok {background: #e7f6ee; color: #0f7a43;}
.badge-conflict {background: #fdf1e0; color: #a15c07;}
.badge-refuse {background: #fdeaea; color: #a52020;}

.sec-label {
  font-size: 0.75rem; font-weight: 700; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--muted); margin: 6px 0 10px 0;
}
.src-card {
  border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px;
  background: #fafafa; margin-bottom: 8px;
}
.src-title {font-weight: 600; color: var(--ink); font-size: 0.94rem;}
.src-meta {color: var(--muted); font-size: 0.82rem; margin-top: 4px;}
.src-id {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.75rem; color: #9ca3af;
}
.foot {color: var(--muted); font-size: 0.82rem; margin-top: 8px;}
.ctx-note {
    border: 1px dashed var(--line); border-radius: 12px; padding: 10px 14px;
    background: #fbfbfd; color: var(--muted); font-size: 0.84rem; margin-bottom: 12px;
}
.scope-table {
    width: 100%; border-collapse: collapse; margin-bottom: 10px;
    border: 1px solid var(--line); border-radius: 12px; overflow: hidden;
}
.scope-table th {
    text-align: left; font-size: 0.72rem; text-transform: uppercase;
    letter-spacing: 0.06em; color: var(--muted); background: #fafafa;
    padding: 9px 12px; border-bottom: 1px solid var(--line);
}
.scope-table td {padding: 9px 12px; font-size: 0.88rem; color: var(--ink); border-bottom: 1px solid #f3f4f6;}
.scope-table tr:last-child td {border-bottom: none;}
.scope-table tr.scope-on {background: #f0fdf4;}
.scope-table tr.scope-on td {color: #0f7a43; font-weight: 600;}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

users = {u.id: u for u in engine.users}
user_ids = list(users.keys())

STATUS = {
    "OK": ("ok", "#0f7a43", "OK · Trả lời có nguồn"),
    "CONFLICT": ("conflict", "#a15c07", "CONFLICT · Có mâu thuẫn"),
    "REFUSE": ("refuse", "#a52020", "REFUSE · Từ chối"),
}

PILL_KEY = "quick_pick"
INPUT_KEY = "question_input"
LAST_USER_KEY = "last_user"

# Ô nhập được xóa ở lượt chạy kế tiếp (không sửa trực tiếp sau khi widget đã tạo).
if st.session_state.pop("clear_input", False):
    st.session_state[INPUT_KEY] = ""
    st.session_state[PILL_KEY] = None

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("### Bối cảnh người dùng")
    st.caption("Người hỏi quyết định phạm vi tri thức được truy cập.")
    uid = st.selectbox("Bạn đang là ai?", user_ids, format_func=lambda x: users[x].name)
    user = users[uid]

    if st.session_state.get(LAST_USER_KEY) not in (None, uid):
        # Đổi người dùng → phiên tách biệt, ô nhập phải trống lại.
        st.session_state[INPUT_KEY] = ""
        st.session_state[PILL_KEY] = None
    st.session_state[LAST_USER_KEY] = uid

    initials = "".join(part[0] for part in user.name.split() if part)[:2].upper()
    groups = "".join(
        f"<span class='chip chip-group'>{html.escape(g)}</span>" for g in user.groups
    ) or "<span class='chip chip-none'>không nhóm quyền</span>"
    st.markdown(
        "<div class='persona'>"
        f"<div class='avatar'>{html.escape(initials)}</div>"
        f"<div class='name'>{html.escape(user.name)}</div>"
        f"<div class='role'>{html.escape(user.role)}</div>"
        f"<span class='chip chip-unit'>{html.escape(user.unit)}</span>{groups}"
        "</div>",
        unsafe_allow_html=True,
    )
    st.write("")
    st.caption("Chạy hoàn toàn offline · không gọi API ngoài · không chứa key.")
    with st.expander("Cách hệ thống lọc quyền"):
        st.markdown(
            "1. Loại bản nháp và bản hết hiệu lực.\n"
            "2. Chỉ giữ văn bản mà **đơn vị** của bạn nằm trong phạm vi "
            "**và** đúng **nhóm quyền** (điều kiện AND).\n"
            "3. Tìm kiếm trong phần còn lại, chọn bản đặc thù mới nhất.\n"
            "4. Cùng chủ đề có nhiều cấp → áp dụng bản của **cấp gần bạn nhất** "
            "(công ty riêng thay quy định chung của Tập đoàn).\n"
            "5. Hai bản **cùng cấp** cùng hiệu lực nhưng khác nội dung → báo mâu thuẫn, không tự chọn.\n"
            "6. Không đủ căn cứ → từ chối bằng một câu chung (không lộ văn bản ngoài quyền)."
        )

# ---------------------------------------------------------------- hero
st.markdown(
    "<div class='app-hero'>"
    "<h1>Tri thức theo quyền truy cập</h1>"
    "<p>Hỏi một câu — nhận đúng tri thức trong phạm vi bạn được phép, kèm nguồn và phiên bản "
    "để kiểm chứng. Đổi người dùng ở khung trái rồi hỏi lại cùng câu để thấy kết quả thay đổi "
    "theo quyền. Mỗi người dùng là một phiên riêng; câu hỏi đã hỏi được lưu trong "
    "<code>data/chat.db</code> (không hiện lại trên giao diện) để giữ ngữ cảnh cho các lần hỏi "
    "tiếp theo. Dữ liệu trong bản demo là giả lập.</p>"
    "</div>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- render
def render_sources(sources):
    if not sources:
        return
    st.markdown("<div class='sec-label'>Nguồn để kiểm chứng</div>", unsafe_allow_html=True)
    for s in sources:
        end = s.get("effective_to") or "hiện hành"
        st.markdown(
            "<div class='src-card'>"
            f"<div class='src-title'>{html.escape(s.get('title', ''))}</div>"
            f"<div class='src-meta'>Phiên bản {html.escape(str(s.get('version', '')))} · hiệu lực "
            f"{s.get('effective_from')} → {end} · {html.escape(s.get('unit_name', ''))}"
            f" · <span class='src-id'>{html.escape(s.get('doc_id', ''))}</span></div>"
            "</div>",
            unsafe_allow_html=True,
        )


def render_scope(scope):
    """Bảng đối chiếu các cấp (Change Request B3)."""
    if not scope:
        return
    chosen = scope.get("chosen") or {}
    applied = scope.get("applied") or []
    others = scope.get("other_levels") or []
    if not applied and not others:
        return
    st.markdown("<div class='sec-label'>Đối chiếu giữa các cấp</div>", unsafe_allow_html=True)
    rows = []
    for item in applied:
        rows.append(
            f"<tr class='scope-on'><td><b>{html.escape(item['level'])}</b></td>"
            f"<td>{html.escape(item['title'])}</td>"
            f"<td>{html.escape(item['unit_name'])}</td>"
            f"<td>Đang áp dụng</td></tr>"
        )
    for item in others:
        rows.append(
            f"<tr><td>{html.escape(item['level'])}</td>"
            f"<td>{html.escape(item['title'])}</td>"
            f"<td>{html.escape(item['unit_name'])}</td>"
            f"<td>{html.escape(item.get('reason', ''))}</td></tr>"
        )
    st.markdown(
        "<table class='scope-table'>"
        "<thead><tr><th>Cấp</th><th>Văn bản</th><th>Đơn vị</th><th>Trạng thái</th></tr></thead>"
        "<tbody>" + "".join(rows) + "</tbody></table>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='ctx-note'>Hệ thống chọn bản của cấp gần đơn vị của bạn nhất. "
        "Bản ở cấp xa hơn chỉ là quy định chung, bị bản đặc thù thay thế — "
        "nếu cần áp dụng bản chung, hãy liên hệ Phòng Nhân Sự.</div>",
        unsafe_allow_html=True,
    )


def render_answer(payload):
    cls, accent, label = STATUS.get(payload.get("kind"), ("refuse", "#6b7280", payload.get("kind", "")))
    st.markdown(
        f"<div class='answer-card' style='--accent:{accent}'>"
        f"<span class='badge badge-{cls}'>{html.escape(label)}</span>"
        f"<div class='answer-body'>{html.escape(payload.get('text', ''))}</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    render_scope(payload.get("scope") or {})
    render_sources(payload.get("sources") or [])
    with st.expander("Chi tiết nội bộ (debug)"):
        st.write("reason:", payload.get("reason", ""))
        st.write("hiệu lực tại:", payload.get("as_of", ""))


def answer_to_payload(answer):
    return {
        "kind": answer.kind,
        "text": answer.text,
        "reason": answer.reason,
        "as_of": answer.as_of.isoformat() if answer.as_of else "",
        "sources": [asdict(s) for s in answer.sources],
        "scope": answer.scope or {},
    }


# ---------------------------------------------------------------- ask box
SUGGESTIONS = [
    "Quy định nghỉ phép của tôi như thế nào?",
    "Chính sách làm việc từ xa cho tối đa mấy ngày 1 tuần?",
    "Nhân viên được cử sang làm việc tại công ty thành viên khác tối đa bao nhiêu ngày?",
    "Ngân sách quý 1 của công ty là bao nhiêu?",
    "Quy trình mua sắm của công ty như thế nào?",
    "Tăng ca được tính thế nào?",
    "Quy trình triển khai Backend của nhóm kỹ thuật thế nào?",
]

st.markdown("<div class='sec-label'>Đặt câu hỏi</div>", unsafe_allow_html=True)

st.session_state.setdefault(INPUT_KEY, "")
st.session_state.setdefault(PILL_KEY, None)

q_quick = st.pills(
    "Gợi ý nhanh (chọn để điền vào ô hỏi, rồi nhấn Hỏi)",
    SUGGESTIONS,
    selection_mode="single",
    key=PILL_KEY,
)
if q_quick:
    st.session_state[INPUT_KEY] = q_quick

# st.form(clear_on_submit=True) tự xóa ô nhập sau khi gửi — không cần hack session_state.
with st.form("ask_form", clear_on_submit=True):
    q = st.text_input(
        "Nhập câu hỏi của bạn",
        key=INPUT_KEY,
        placeholder="Ví dụ: Quy định nghỉ phép của tôi như thế nào?",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Hỏi", type="primary")

q_clean = (q or "").strip()
if submitted and q_clean:
    # Ngữ cảnh chỉ lấy từ phiên của chính người hỏi này (lưu trong SQLite).
    context = store.recent_turns(uid, limit=CONTEXT_TURNS)
    answer = engine.answer(q_clean, user, context=context)
    store.add_turn(
        user_id=uid,
        user_name=user.name,
        unit=user.unit,
        question=q_clean,
        effective_question=answer.debug.get("effective_question", q_clean),
        answer_kind=answer.kind,
        answer_text=answer.text,
        reason=answer.reason,
        sources=answer_to_payload(answer)["sources"],
        as_of=answer.as_of,
        used_context=answer.debug.get("context_used", []),
        scope=answer.scope or {},
    )
    st.session_state["clear_input"] = True
    st.rerun()

# ---------------------------------------------------------------- result
turns = store.recent_turns(uid, limit=1)
if turns:
    last = turns[0]
    payload = {
        "kind": last["answer_kind"],
        "text": last["answer_text"],
        "reason": last["reason"],
        "as_of": last["as_of"],
        "sources": last["sources"],
        "scope": last.get("scope") or {},
    }
    st.markdown(
        f"<div class='qmeta'><span class='who'>{html.escape(user.name)}</span>"
        f" · {html.escape(user.unit)}</div>"
        f"<div class='qtext'>“{html.escape(last['question'])}”</div>",
        unsafe_allow_html=True,
    )
    render_answer(payload)

    saved = store.count(uid)
    st.markdown(
        "<div class='ctx-note'>"
        f"Phiên của bạn đã lưu <b>{saved}</b> lượt hỏi trong <code>data/chat.db</code>. "
        "Các lượt này không hiện lại trên giao diện nhưng được dùng làm ngữ cảnh để hiểu "
        "câu hỏi tiếp theo (ví dụ: “vậy còn …?”). Phiên của người dùng khác tách biệt hoàn toàn."
        "</div>",
        unsafe_allow_html=True,
    )

    if st.button("Xóa lịch sử phiên của tôi", use_container_width=False):
        store.clear(uid)
        st.rerun()
else:
    st.info("Gõ câu hỏi rồi nhấn Enter (hoặc bấm Hỏi). Sau khi hỏi, ô nhập sẽ trống lại.")

st.divider()
st.markdown(
    "<div class='foot'>Bộ kiểm thử: 11 tình huống Mission 2 + 10 test Mission 3, "
    "kèm nhận định Đạt/Chưa đạt và bài học — xem <code>tests/report.md</code>.</div>",
    unsafe_allow_html=True,
)
