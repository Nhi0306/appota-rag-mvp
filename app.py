# -*- coding: utf-8 -*-
import os
import sys

import streamlit as st

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from ragscope import Engine  # noqa: E402

DATA = os.path.join(BASE, "data")


@st.cache_resource
def get_engine():
    return Engine(DATA)


engine = get_engine()

st.set_page_config(page_title="RAG theo quyền — MVP", page_icon=None, layout="wide")

st.title("RAG theo quyền truy cập — MVP (Mission 2)")
st.caption(
    "Core loop: Câu hỏi + bối cảnh người dùng → tìm đúng tri thức → dùng đúng phạm vi → "
    "trả lời có nguồn kiểm chứng. Dữ liệu là giả lập, không phải dữ liệu thật của Appota."
)

users = {u.id: u for u in engine.users}
user_ids = list(users.keys())

with st.sidebar:
    st.header("Bối cảnh người dùng")
    uid = st.selectbox("Bạn đang là ai?", user_ids, format_func=lambda x: users[x].name)
    user = users[uid]
    st.markdown(
        f"**Đơn vị:** {user.unit}\n\n**Chức danh:** {user.role}\n\n"
        f"**Nhóm quyền:** {', '.join(user.groups) if user.groups else 'không có'}"
    )
    st.divider()
    st.caption("MVP chạy hoàn toàn offline, không gọi API ngoài, không chứa key.")


def show_answer(answer):
    color = {"OK": "#1b7f4b", "CONFLICT": "#b45309", "REFUSE": "#b32d2d"}[answer.kind]
    st.markdown(f"### Kết quả: **{answer.kind}**")
    st.markdown(
        f"<div style='background:{color};color:white;padding:2px 10px;border-radius:6px;"
        f"display:inline-block'>{answer.kind}</div>",
        unsafe_allow_html=True,
    )
    st.write(answer.text)
    if answer.sources:
        rows = [
            {
                "Tài liệu": s.title,
                "Phiên bản": s.version,
                "Hiệu lực": f"{s.effective_from} → {s.effective_to if s.effective_to else 'hiện hành'}",
                "Đơn vị ban hành": s.unit_name,
                "ID": s.doc_id,
            }
            for s in answer.sources
        ]
        st.markdown("**Nguồn (để kiểm chứng):**")
        st.dataframe(rows, width=980, hide_index=True)
    with st.expander("Xem lý do nội bộ (debug)"):
        st.write("reason:", answer.reason)
        st.write("top matches:", answer.debug)


q_quick = st.pills(
    "Câu hỏi gợi ý",
    [
        "Quy định nghỉ phép của tôi như thế nào?",
        "Chính sách làm việc từ xa cho tối đa mấy ngày 1 tuần?",
        "Ngân sách quý 1 của công ty là bao nhiêu?",
        "Quy trình mua sắm của công ty như thế nào?",
        "Tăng ca được tính thế nào?",
        "Quy trình triển khai Backend của nhóm kỹ thuật thế nào?",
    ],
    selection_mode="single",
    accept_new_options=True,
)

st.divider()
st.subheader("Thử ngay")
q = st.text_input("Câu hỏi của bạn:", value=q_quick if q_quick else "")
if q.strip():
    show_answer(engine.answer(q, user))
else:
    st.info("Gõ câu hỏi hoặc chọn một gợi ý bên trên. Đổi người dùng ở khung trái để thấy cùng một câu hỏi trả về kết quả khác nhau theo quyền.")

st.divider()
st.subheader("Demo bắt buộc: cùng câu hỏi, hai bối cảnh khác nhau")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**1) Nghỉ phép — Phòng Nội Dung vs Phòng Kế Toán**")
    if st.button("Chạy demo nghỉ phép"):
        a1 = engine.answer("Quy định nghỉ phép của tôi như thế nào?", users["u_nguyen_anh"])
        a2 = engine.answer("Quy định nghỉ phép của tôi như thế nào?", users["u_tran_binh"])
        st.markdown(f"**{users['u_nguyen_anh'].name}** ({users['u_nguyen_anh'].unit}):")
        st.info(a1.text)
        st.markdown(f"**{users['u_tran_binh'].name}** ({users['u_tran_binh'].unit}):")
        st.info(a2.text)
        st.caption("Phụ lục riêng của Phòng Nội Dung (16 ngày) thắng bản chung (14 ngày) — người Phòng Kế Toán chỉ thấy bản chung.")
with c2:
    st.markdown("**2) Ngân sách quý 1 — Nhân viên vs Quản lý**")
    if st.button("Chạy demo ngân sách"):
        a1 = engine.answer("Ngân sách quý 1 của công ty là bao nhiêu?", users["u_tran_binh"])
        a2 = engine.answer("Ngân sách quý 1 của công ty là bao nhiêu?", users["u_le_chi"])
        st.markdown(f"**{users['u_tran_binh'].name}** (nhân viên, không nhóm quyền):")
        st.info(a1.text)
        st.markdown(f"**{users['u_le_chi'].name}** (trưởng phòng, nhóm manager):")
        st.info(a2.text)
        st.caption("Nhân viên bị từ chối với câu trả lời chung chung (không lộ việc có số liệu ngân sách); quản lý nhận số liệu hợp lệ.")

st.divider()
st.caption("Xem bộ kiểm thử đầy đủ (11 case, kèm nhận định Đạt/Chưa đạt và bài học): `tests/report.md`.")