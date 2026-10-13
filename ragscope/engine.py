from __future__ import annotations

import os
import re
from datetime import date

import yaml

from .bm25 import BM25, _tokens
from .data_loader import load_documents, load_users, scope_depth, usable, visible
from .models import Answer, Source
from .org import ancestors, load_units


def _split_sentences(text: str) -> list:
    parts = re.split(r"(?<=[.])\s+(?=[^\d\s])", text.strip())
    return [p.strip() for p in parts if p.strip()]


STOPWORDS = {
    "quy", "định", "trình", "thế", "nào", "ra", "sao", "bao", "nhiêu",
    "của", "tôi", "như", "cho", "với", "để", "và", "là", "có", "theo",
    "được", "thì", "nếu", "hay", "nên", "đó", "này", "một", "không",
    "đang", "đã", "sẽ", "tại", "về", "thế", "tất", "cả", "mấy", "ông",
}


def substantive_words(query: str) -> set:
    words = [w.lower() for w in re.findall(r"[a-zà-ỹ0-9]+", query.lower())]
    return {w for w in words if len(w) >= 3 and w not in STOPWORDS}


def _snippet(doc, question: str, radius=1) -> str:
    sents = _split_sentences(doc.content)
    if len(sents) <= 1:
        return doc.content
    qtoks = set(_tokens(question))
    scores = []
    for s in sents:
        stoks = set(_tokens(s))
        overlap = len(qtoks & stoks)
        scores.append(overlap / (1 + len(stoks)))
    best = max(range(len(scores)), key=lambda i: (scores[i], i))
    lo, hi = max(0, best - radius), min(len(sents), best + radius + 1)
    return " ".join(sents[lo:hi])


def _eff_text(d, units):
    fr = d.effective_from.isoformat()
    to = d.effective_to.isoformat() if d.effective_to else "hiện hành"
    return f"{fr} → {to}"


def _unit_name(d, units):
    info = units.get(d.unit)
    return info["name"] if info else d.unit


def source_of(d, units) -> Source:
    return Source(
        doc_id=d.id,
        title=d.title,
        version=d.version,
        unit_name=_unit_name(d, units),
        effective_from=d.effective_from,
        effective_to=d.effective_to,
    )


REFUSAL_TEXT = (
    "Xin lỗi, hệ thống không tìm thấy văn bản trong phạm vi quyền của bạn đủ để trả lời "
    "câu hỏi này. Bạn có thể liên hệ Phòng Nhân Sự để được hỗ trợ."
)


class Engine:
    def __init__(self, data_dir, today=None):
        self.data_dir = data_dir
        self.today = today or date(2026, 3, 20)
        with open(os.path.join(data_dir, "org.yaml"), encoding="utf-8") as f:
            self.units = load_units(yaml.safe_load(f)["units"])
        self.users = load_users(os.path.join(data_dir, "users.yaml"))
        self.documents = load_documents(os.path.join(data_dir, "documents.yaml"))
        self.usable_docs = [d for d in self.documents if usable(d, self.today, self.units)]
        self.bm25 = BM25(self.usable_docs)
        self.threshold = 1.5

    def user_by_id(self, user_id):
        for u in self.users:
            if u.id == user_id:
                return u
        raise KeyError(user_id)

    def _select(self, top):
        best = top[0][0]
        fam = best.family or best.id
        cands = [d for d, s in top if (d.family or d.id) == fam]
        if len(cands) >= 2:
            depths = [scope_depth(d) for d in cands]
            mx = max(depths)
            deepest = [d for d in cands if scope_depth(d) == mx]
            if len(deepest) == 1:
                return deepest[0], cands
            contents = {d.content for d in deepest}
            if len(contents) > 1:
                return None, deepest
            return deepest[0], cands
        return best, cands

    def answer(self, question: str, user) -> Answer:
        anc = ancestors(user.unit, self.units)
        all_res = self.bm25.search(question)
        top_all = all_res[:8]

        def _refuse(reason):
            return Answer(kind="REFUSE", text=REFUSAL_TEXT, sources=[], reason=reason,
                          debug=self._debug(top_all, [], reason))

        if not all_res or all_res[0][1] < self.threshold:
            return _refuse("no_source")

        best_all_doc, best_all_s = all_res[0]
        vis_res = [(d, s) for d, s in all_res if visible(d, anc, user.groups)]
        if not vis_res or vis_res[0][1] < self.threshold:
            return _refuse("out_of_scope")

        if not visible(best_all_doc, anc, user.groups) and vis_res[0][1] < 0.5 * best_all_s:
            return _refuse("out_of_scope")

        top = vis_res[:6]
        chosen, cands = self._select(top)

        substantives = substantive_words(question)
        candidates_for_answer = [chosen] if chosen else cands
        if substantives and not any(
            substantives & set(sv.lower() for sv in re.findall(r"[a-zà-ỹ0-9]+", d.title + " " + d.content))
            for d in candidates_for_answer
        ):
            return _refuse("no_source")

        if chosen is None:
            srcs = [source_of(d, self.units) for d in cands]
            lines = []
            for i, d in enumerate(cands, 1):
                snip = _snippet(d, question, radius=0)
                lines.append(f"{i}. {d.title} (bản {d.version}): “{snip}”")
            text = (
                "Lưu ý: hiện có hai văn bản cùng giai đoạn hiệu lực nhưng nội dung khác nhau về "
                "chủ đề này:\n\n" + "\n\n".join(lines) +
                "\n\nHệ thống không tự chọn. Bạn hãy xác nhận văn bản nào được áp dụng, "
                "hoặc liên hệ Phòng Nhân Sự để chốt bản hiệu lực."
            )
            return Answer(kind="CONFLICT", text=text, sources=srcs, reason="conflict",
                          debug=self._debug(top_all, [d.id for d in cands], "conflict"))

        snip = _snippet(chosen, question)
        fr = chosen.effective_from.isoformat()
        to = chosen.effective_to.isoformat() if chosen.effective_to else "hiện hành"
        text = (
            f"Được. Theo {chosen.title} (bản {chosen.version}, hiệu lực {fr} → {to}):\n\n"
            f"“{snip}”"
        )
        srcs = [source_of(d, self.units) for d in cands]
        return Answer(kind="OK", text=text, sources=srcs, reason="ok",
                      debug=self._debug(top_all, [d.id for d in cands], chosen.id))

    def _debug(self, top_all, visible_ids, chosen):
        return {
            "chosen": chosen,
            "visible_ids": visible_ids,
            "top_all": [(d.id, round(s, 3)) for d, s in top_all[:5]],
        }