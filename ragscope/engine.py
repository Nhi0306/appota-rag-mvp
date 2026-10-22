from __future__ import annotations

import os
import re
from datetime import date

import yaml

from .audit import AuditLogger
from .bm25 import BM25, _tokens
from .data_loader import load_documents, load_users, scope_depth, usable, visible, visibility_reason
from .models import Answer, Source
from .org import ancestors, load_units, unit_level_name
from .versioning import diff_documents, sort_versions


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


def _eff_text(d):
    fr = d.effective_from.isoformat()
    to = d.effective_to.isoformat() if d.effective_to else "hiện hành"
    return f"{fr} → {to}"


def _unit_name(d, units):
    info = units.get(d.unit)
    return info["name"] if info else d.unit


def source_of(d, units, score=0.0, snippet="", as_of=None) -> Source:
    return Source(
        doc_id=d.id,
        title=d.title,
        version=d.version,
        unit_name=_unit_name(d, units),
        effective_from=d.effective_from,
        effective_to=d.effective_to,
        unit_id=d.unit,
        level=unit_level_name(d.unit),
        score=round(float(score), 4),
        snippet=snippet,
        as_of=as_of,
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
        self.audit = AuditLogger(os.path.join(data_dir, "audit.jsonl"))

    def user_by_id(self, user_id):
        for u in self.users:
            if u.id == user_id:
                return u
        raise KeyError(user_id)

    def _doc_by_id(self, doc_id):
        for d in self.documents:
            if d.id == doc_id:
                return d
        raise KeyError(doc_id)

    def _select(self, top):
        if not top:
            return None, [], False
        best = top[0][0]
        fam = best.family or best.id
        cands = [d for d, s in top if (d.family or d.id) == fam]
        if len(cands) < 2:
            return best, cands, False
        depths = [scope_depth(d) for d in cands]
        mx = max(depths)
        deepest = [d for d in cands if scope_depth(d) == mx]
        if len(deepest) == 1:
            return deepest[0], cands, False
        contents = {d.content.strip() for d in deepest}
        if len(contents) > 1:
            return None, deepest, True
        return deepest[0], deepest, False

    def _coverage(self, question, chosen):
        qtoks = substantive_words(question)
        text = (chosen.title + " " + chosen.content).lower()
        found = {w for w in qtoks if w in text}
        missing = sorted(qtoks - found)
        return {"found": sorted(found), "missing": missing, "partial": bool(missing)}

    def answer(self, question: str, user, as_of=None) -> Answer:
        as_of = as_of or self.today
        anc = ancestors(user.unit, self.units)
        usable_docs = [d for d in self.documents if usable(d, as_of, self.units)]
        bm25 = BM25(usable_docs) if usable_docs else None
        all_res = bm25.search(question) if bm25 else []
        top_all = all_res[:8]

        def _refuse(reason, detail=""):
            srcs = []
            audit_id = self.audit.log({
                "user_id": user.id, "user_unit": user.unit, "question": question,
                "as_of": as_of, "result": "REFUSE", "reason": reason, "detail": detail,
                "chosen": None, "sources": [],
            })
            return Answer(kind="REFUSE", text=REFUSAL_TEXT, sources=srcs, reason=reason,
                          debug={"top_all": [(d.id, round(s, 3)) for d, s in top_all[:5]],
                                 "detail": detail, "as_of": as_of},
                          as_of=as_of, audit_id=audit_id)

        if not all_res or all_res[0][1] < self.threshold:
            return _refuse("no_source", "no usable document matched query")

        best_all_doc, best_all_s = all_res[0]
        vis_res = [(d, s) for d, s in all_res if visible(d, anc, user.groups)]
        if not vis_res or vis_res[0][1] < self.threshold:
            return _refuse("out_of_scope", "best match outside user scope")

        if not visible(best_all_doc, anc, user.groups) and vis_res[0][1] < 0.5 * best_all_s:
            return _refuse("out_of_scope", "best global match not visible and in-scope score too low")

        top = vis_res[:6]
        chosen, cands, conflict = self._select(top)

        substantives = substantive_words(question)
        candidates_for_answer = [chosen] if chosen else cands
        if substantives and not any(
            substantives & set(w.lower() for w in re.findall(r"[a-zà-ỹ0-9]+", d.title + " " + d.content))
            for d in candidates_for_answer
        ):
            return _refuse("no_source", "substantive terms absent from candidate text")

        if conflict:
            score_map = {d.id: s for d, s in top}
            srcs = [source_of(d, self.units, score=score_map.get(d.id, 0.0),
                              snippet=_snippet(d, question, radius=0), as_of=as_of) for d in cands]
            lines = []
            for i, d in enumerate(cands, 1):
                snip = _snippet(d, question, radius=0)
                lines.append(f'{i}. {d.title} (bản {d.version}): "{snip}"')
            text = (
                "Lưu ý: hiện có hai văn bản cùng giai đoạn hiệu lực nhưng nội dung khác nhau về chủ đề này:\n\n"
                + "\n\n".join(lines) +
                "\n\nHệ thống không tự chọn. Bạn hãy xác nhận văn bản nào được áp dụng, "
                "hoặc liên hệ Phòng Nhân Sự để chốt hiệu lực."
            )
            audit_id = self.audit.log({
                "user_id": user.id, "user_unit": user.unit, "question": question,
                "as_of": as_of, "result": "CONFLICT", "reason": "conflict",
                "chosen": None, "sources": [d.id for d in cands],
            })
            return Answer(kind="CONFLICT", text=text, sources=srcs, reason="conflict",
                          debug={"top_all": [(d.id, round(s, 3)) for d, s in top_all[:5]],
                                 "visible_ids": [d.id for d in cands], "as_of": as_of},
                          as_of=as_of, confidence="low", audit_id=audit_id)

        snip = _snippet(chosen, question)
        fr = chosen.effective_from.isoformat()
        to = chosen.effective_to.isoformat() if chosen.effective_to else "hiện hành"
        text = (
            f"Được. Theo {chosen.title} (bản {chosen.version}, hiệu lực {fr} → {to}):\n\n"
            f'"{snip}"'
        )
        score_map = {d.id: s for d, s in top}
        srcs = [source_of(d, self.units, score=score_map.get(d.id, 0.0),
                          snippet=_snippet(d, question, radius=0), as_of=as_of) for d in cands]
        coverage = self._coverage(question, chosen)
        if coverage.get("partial") and coverage.get("missing"):
            text += ("\n\nLưu ý: câu trả lời có thể chưa đầy đủ về: "
                     + ", ".join(coverage["missing"]) + ". "
                     "Bạn có thể liên hệ Phòng Nhân Sự để được hỗ trợ thêm.")
        audit_id = self.audit.log({
            "user_id": user.id, "user_unit": user.unit, "question": question,
            "as_of": as_of, "result": "OK", "reason": "ok",
            "chosen": chosen.id, "sources": [d.id for d in cands],
            "coverage": coverage,
        })
        return Answer(kind="OK", text=text, sources=srcs, reason="ok",
                      debug={"chosen": chosen.id, "visible_ids": [d.id for d in cands],
                             "top_all": [(d.id, round(s, 3)) for d, s in top_all[:5]],
                             "as_of": as_of},
                      as_of=as_of, confidence="high" if not coverage.get("partial") else "medium",
                      coverage=coverage, audit_id=audit_id)

    def explain(self, doc_id: str, user_id: str, as_of=None) -> dict:
        as_of = as_of or self.today
        user = self.user_by_id(user_id)
        doc = self._doc_by_id(doc_id)
        anc = ancestors(user.unit, self.units)
        ok, reasons = visibility_reason(doc, anc, user.groups, as_of)
        return {
            "doc_id": doc_id,
            "user_id": user_id,
            "as_of": as_of,
            "visible": ok,
            "reasons": reasons,
            "unit": doc.unit,
            "level": unit_level_name(doc.unit),
        }

    def version_diff(self, doc_id_a: str, doc_id_b: str) -> dict:
        return diff_documents(self._doc_by_id(doc_id_a), self._doc_by_id(doc_id_b))

    def versions_of(self, family: str, as_of=None) -> list:
        as_of = as_of or self.today
        docs = [d for d in self.documents if (d.family or d.id) == family and usable(d, as_of, self.units)]
        return sort_versions(docs)
