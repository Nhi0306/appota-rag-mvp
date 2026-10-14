# -*- coding: utf-8 -*-
import html
import os
import sys

import streamlit as st

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from ragscope import Engine  # noqa: E402

DATA = os.path.join(BASE, "data")
HISTORY_LIMIT = 5


@st.cache_resource
def get_engine():
    return Engine(DATA)


engine = get_engine()

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

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("### Bối cảnh người dùng")
    st.caption("Người hỏi quyết định phạm vi tri thức được truy cập.")
    uid = st.selectbox("Bạn đang là ai?", user_ids, format_func=lambda x: users[x].name)
    user = users[uid]

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
            "4. Hai bản cùng hiệu lực khác nội dung → báo mâu thuẫn, không tự chọn.\n"
            "5. Không đủ căn cứ → từ chối bằng một câu chung (không lộ văn bản ngoài quyền)."
        )

# ---------------------------------------------------------------- hero
st.markdown(
    "<div class='app-hero'>"
    "<h1>Tri thức theo quyền truy cập</h1>"
    "<p>Hỏi một câu — nhận đúng tri thức trong phạm vi bạn được phép, kèm nguồn và phiên bản "
    "để kiểm chứng. Đổi người dùng ở khung trái rồi hỏi lại cùng câu để thấy kết quả thay đổi "
    "theo quyền. 5 lượt hỏi gần nhất được giữ lại bên dưới. Dữ liệu trong bản demo là giả lập.</p>"
    "</div>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- render
def render_sources(answer):
    if not answer.sources:
        return
    st.markdown("<div class='sec-label'>Nguồn để kiểm chứng</div>", unsafe_allow_html=True)
    for s in answer.sources:
        end = s.effective_to if s.effective_to else "hiện hành"
        st.markdown(
            "<div class='src-card'>"
            f"<div class='src-title'>{html.escape(s.title)}</div>"
            f"<div class='src-meta'>Phiên bản {html.escape(s.version)} · hiệu lực "
            f"{s.effective_from} → {end} · {html.escape(s.unit_name)}"
            f" · <span class='src-id'>{html.escape(s.doc_id)}</span></div>"
            "</div>",
            unsafe_allow_html=True,
        )


def render_answer(answer):
    cls, accent, label = STATUS.get(answer.kind, ("refuse", "#6b7280", answer.kind))
    st.markdown(
        f"<div class='answer-card' style='--accent:{accent}'>"
        f"<span class='badge badge-{cls}'>{html.escape(label)}</span>"
        f"<div class='answer-body'>{html.escape(answer.text)}</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    render_sources(answer)
    with st.expander("Chi tiết nội bộ (debug)"):
        st.write("reason:", answer.reason)
        st.write("top matches:", answer.debug)


def render_turn(index, item):
    with st.container(border=False):
        st.markdown(
            "<div class='hist-head'>"
            f"<div class='qmeta'><span class='who'>{html.escape(item['user_name'])}</span>"
            f" · {html.escape(item['user_unit'])}</div>"
            f"<div class='turn-tag'>Lượt {index}</div>"
            "</div>"
            f"<div class='qtext'>“{html.escape(item['question'])}”</div>",
            unsafe_allow_html=True,
        )
        render_answer(item["answer"])


# ---------------------------------------------------------------- ask box
SUGGESTIONS = [
    "Quy định nghỉ phép của tôi như thế nào?",
    "Chính sách làm việc từ xa cho tối đa mấy ngày 1 tuần?",
    "Ngân sách quý 1 của công ty là bao nhiêu?",
    "Quy trình mua sắm của công ty như thế nào?",
    "Tăng ca được tính thế nào?",
    "Quy trình triển khai Backend của nhóm kỹ thuật thế nào?",
]

st.markdown("<div class='sec-label'>Đặt câu hỏi</div>", unsafe_allow_html=True)

st.session_state.setdefault("question", "")
st.session_state.setdefault("last_quick", None)
st.session_state.setdefault("last_key", None)
st.session_state.setdefault("history", [])

q_quick = st.pills(
    "Gợi ý nhanh (chọn để hỏi ngay, hoặc tự gõ câu của bạn)",
    SUGGESTIONS,
    selection_mode="single",
)
if q_quick and q_quick != st.session_state["last_quick"]:
    st.session_state["question"] = q_quick
    st.session_state["last_quick"] = q_quick

col_q, col_btn = st.columns([6, 1], vertical_alignment="bottom")
with col_q:
    q = st.text_input(
        "Nhập câu hỏi của bạn",
        key="question",
        placeholder="Ví dụ: Quy định nghỉ phép của tôi như thế nào?",
        label_visibility="collapsed",
    )
with col_btn:
    st.button("Hỏi", type="primary", use_container_width=True)

# Ghi lượt hỏi mới vào lịch sử (tối đa 5, không trùng theo người dùng + câu hỏi)
q_clean = q.strip()
if q_clean:
    key = (uid, q_clean)
    if key != st.session_state["last_key"]:
        answer = engine.answer(q_clean, user)
        history = [
            h for h in st.session_state["history"]
            if (h["uid"], h["question"]) != key
        ]
        history.insert(
            0,
            {
                "uid": uid,
                "user_name": user.name,
                "user_unit": user.unit,
                "question": q_clean,
                "answer": answer,
            },
        )
        st.session_state["history"] = history[:HISTORY_LIMIT]
        st.session_state["last_key"] = key

# ---------------------------------------------------------------- history
history = st.session_state["history"]
head_l, head_r = st.columns([5, 1], vertical_alignment="bottom")
with head_l:
    st.markdown(
        f"<div class='sec-label'>Kết quả · {len(history)}/{HISTORY_LIMIT} lượt gần nhất</div>",
        unsafe_allow_html=True,
    )
with head_r:
    if history and st.button("Xóa lịch sử", use_container_width=True):
        st.session_state["history"] = []
        st.session_state["last_key"] = None
        st.rerun()

if history:
    for i, item in enumerate(history, start=1):
        render_turn(i, item)
else:
    st.info("Gõ câu hỏi rồi nhấn Enter (hoặc bấm Hỏi). Kết quả 5 lượt gần nhất sẽ được giữ lại ở đây.")

st.divider()
st.markdown(
    "<div class='foot'>Bộ kiểm thử: 11 tình huống, kèm nhận định Đạt/Chưa đạt và bài học "
    "— xem <code>tests/report.md</code>.</div>",
    unsafe_allow_html=True,
)
