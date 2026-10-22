from __future__ import annotations

import os
import re
from datetime import date

import yaml

from .audit import AuditLogger
from .bm25 import BM25, _tokens
from .conversation import expand_with_context
from .data_loader import load_documents, load_users, usable, visible, visibility_reason
from .models import Answer, Source
from .org import ancestors, load_units, unit_level_name
from .scope_resolver import matched_unit, resolve_scope, scope_report
from .text import STOPWORDS, substantive_words
from .versioning import diff_documents, sort_versions


def _split_sentences(text: str) -> list:
    parts = re.split(r"(?<=[.])\s+(?=[^\d\s])", text.strip())
    return [p.strip() for p in parts if p.strip()]


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

    def _select(self, candidates, anc):
        """Chọn tài liệu áp dụng cho người hỏi trong nhóm tài liệu cùng chủ đề.

        Change Request B3: tài liệu cùng chủ đề có thể nằm ở nhiều cấp
        (Tập đoàn / Công ty / Phòng ban). Quy tắc: bản áp dụng ở cấp GẦN người hỏi
        nhất thắng; hai bản cùng cấp mà nội dung khác nhau thì không tự chọn.
        """
        res = resolve_scope(candidates, anc)
        return res["chosen"], res["applied"], res["conflict"], res["levels"]

    def _coverage(self, question, chosen):
        qtoks = substantive_words(question)
        text = (chosen.title + " " + chosen.content).lower()
        found = {w for w in qtoks if w in text}
        missing = sorted(qtoks - found)
        return {"found": sorted(found), "missing": missing, "partial": bool(missing)}

    def answer(self, question: str, user, as_of=None, context=None) -> Answer:
        as_of = as_of or self.today
        anc = ancestors(user.unit, self.units)
        effective_question, used_context = expand_with_context(question, context)
        usable_docs = [d for d in self.documents if usable(d, as_of, self.units)]
        bm25 = BM25(usable_docs) if usable_docs else None
        all_res = bm25.search(effective_question) if bm25 else []
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
                                 "detail": detail, "as_of": as_of,
                                 "effective_question": effective_question,
                                 "context_used": used_context},
                          as_of=as_of, audit_id=audit_id)

        if not all_res or all_res[0][1] < self.threshold:
            return _refuse("no_source", "no usable document matched query")

        best_all_doc, best_all_s = all_res[0]
        vis_res = [(d, s) for d, s in all_res if visible(d, anc, user.groups)]
        if not vis_res or vis_res[0][1] < self.threshold:
            return _refuse("out_of_scope", "best match outside user scope")

        if not visible(best_all_doc, anc, user.groups) and vis_res[0][1] < 0.5 * best_all_s:
            return _refuse("out_of_scope", "best global match not visible and in-scope score too low")

        # Change Request B3: cùng một chủ đề có thể có bản ở nhiều cấp tổ chức.
        # Gom TOÀN BỘ văn bản cùng family mà người hỏi được phép xem (không chỉ
        # top-6 theo điểm BM25) rồi mới quyết định bản nào áp dụng.
        best_vis_doc, best_vis_score = vis_res[0]
        fam = best_vis_doc.family or best_vis_doc.id
        score_map = {d.id: s for d, s in all_res}
        fam_docs = [d for d in usable_docs
                    if (d.family or d.id) == fam and visible(d, anc, user.groups)]
        relevant = [d for d in fam_docs if score_map.get(d.id, 0.0) > 0] or [best_vis_doc]

        chosen, applied_docs, conflict_docs, levels = self._select(relevant, anc)
        cands = conflict_docs or applied_docs or relevant

        substantives = substantive_words(effective_question)
        if substantives and not any(
            substantives & set(w.lower() for w in re.findall(r"[a-zà-ỹ0-9]+", d.title + " " + d.content))
            for d in relevant
        ):
            return _refuse("no_source", "substantive terms absent from candidate text")

        best_dist = None
        if levels:
            best_dist = min(e["dist"] for e in levels)
        unit_names = {k: v["name"] for k, v in self.units.items()}
        applied_report, other_report = scope_report(levels, best_dist, unit_names,
                                                   conflict=bool(conflict_docs))
        scope_info = {
            "family": fam,
            "chosen": {
                "doc_id": chosen.id,
                "title": chosen.title,
                "unit": chosen.unit,
                "unit_name": unit_names.get(chosen.unit, chosen.unit),
                "level": unit_level_name(chosen.unit),
                "version": chosen.version,
            } if chosen else None,
            "applied": applied_report,
            "other_levels": other_report,
            "conflict": bool(conflict_docs),
        }

        if conflict_docs:
            srcs = [source_of(d, self.units, score=score_map.get(d.id, 0.0),
                              snippet=_snippet(d, effective_question, radius=0), as_of=as_of)
                    for d in conflict_docs]
            lines = []
            for i, d in enumerate(conflict_docs, 1):
                snip = _snippet(d, effective_question, radius=0)
                lines.append(
                    f'{i}. {d.title} — cấp {unit_level_name(d.unit)} '
                    f'({_unit_name(d, self.units)}), bản {d.version}: "{snip}"'
                )
            text = (
                "Lưu ý: hiện có hai văn bản cùng cấp áp dụng và cùng giai đoạn hiệu lực "
                "nhưng nội dung khác nhau về chủ đề này:\n\n"
                + "\n\n".join(lines) +
                "\n\nHệ thống không tự chọn. Bạn hãy xác nhận văn bản nào được áp dụng, "
                "hoặc liên hệ Phòng Nhân Sự để chốt hiệu lực."
            )
            audit_id = self.audit.log({
                "user_id": user.id, "user_unit": user.unit, "question": question,
                "as_of": as_of, "result": "CONFLICT", "reason": "conflict",
                "chosen": None, "sources": [d.id for d in conflict_docs],
                "context_used": used_context, "scope": scope_info,
            })
            return Answer(kind="CONFLICT", text=text, sources=srcs, reason="conflict",
                          debug={"top_all": [(d.id, round(s, 3)) for d, s in top_all[:5]],
                                 "visible_ids": [d.id for d in fam_docs], "as_of": as_of,
                                 "effective_question": effective_question,
                                 "context_used": used_context},
                          as_of=as_of, confidence="low", audit_id=audit_id, scope=scope_info)

        snip = _snippet(chosen, effective_question)
        fr = chosen.effective_from.isoformat()
        to = chosen.effective_to.isoformat() if chosen.effective_to else "hiện hành"
        text = (
            f"Được. Theo {chosen.title} (bản {chosen.version}, hiệu lực {fr} → {to}):\n\n"
            f'"{snip}"'
        )
        srcs = [source_of(d, self.units, score=score_map.get(d.id, 0.0),
                          snippet=_snippet(d, effective_question, radius=0), as_of=as_of)
                for d in fam_docs]
        coverage = self._coverage(question, chosen)
        if used_context:
            text += ("\n\n(Câu hỏi này được hiểu theo ngữ cảnh các lượt hỏi trước của bạn "
                     "trong cùng phiên.)")
        if other_report:
            others = "; ".join(
                f'«{o["title"]}» (cấp {o["level"]})' for o in other_report
            )
            text += (
                f"\n\n(Đối chiếu theo cấp: hệ thống áp dụng «{chosen.title}» của "
                f"{scope_info['chosen']['unit_name']} — cấp {scope_info['chosen']['level']} — "
                f"vì đây là cấp gần đơn vị của bạn nhất. Cùng chủ đề nhưng ở cấp khác: "
                f"{others} — bản đặc thù của cấp gần bạn hơn được ưu tiên.)"
            )
        if coverage.get("partial") and coverage.get("missing"):
            text += ("\n\nLưu ý: câu trả lời có thể chưa đầy đủ về: "
                     + ", ".join(coverage["missing"]) + ". "
                     "Bạn có thể liên hệ Phòng Nhân Sự để được hỗ trợ thêm.")
        audit_id = self.audit.log({
            "user_id": user.id, "user_unit": user.unit, "question": question,
            "as_of": as_of, "result": "OK", "reason": "ok",
            "chosen": chosen.id, "sources": [d.id for d in fam_docs],
            "coverage": coverage, "context_used": used_context, "scope": scope_info,
        })
        return Answer(kind="OK", text=text, sources=srcs, reason="ok",
                      debug={"chosen": chosen.id, "visible_ids": [d.id for d in fam_docs],
                             "top_all": [(d.id, round(s, 3)) for d, s in top_all[:5]],
                             "as_of": as_of, "context_used": used_context,
                             "effective_question": effective_question},
                      as_of=as_of, confidence="high" if not coverage.get("partial") else "medium",
                      coverage=coverage, audit_id=audit_id, scope=scope_info)

    def scope_levels(self, user_id: str, family: str = None, as_of=None) -> list:
        """Đối chiếu các bản cùng chủ đề theo cấp tổ chức, từ góc nhìn người hỏi.

        Mỗi văn bản người hỏi được phép xem sẽ được gắn:
          - cấp áp dụng (level), đơn vị, khoảng cách tới đơn vị của người hỏi
          - applies = True nếu đây là bản sẽ được dùng để trả lời
          - reason: vì sao áp dụng / không áp dụng
        """
        as_of = as_of or self.today
        user = self.user_by_id(user_id)
        anc = ancestors(user.unit, self.units)
        docs = [d for d in self.documents if usable(d, as_of, self.units)]
        if family:
            docs = [d for d in docs if (d.family or d.id) == family]
        docs = [d for d in docs if visible(d, anc, user.groups)]
        unit_names = {k: v["name"] for k, v in self.units.items()}

        entries = []
        for d in docs:
            unit = matched_unit(d, anc)
            if unit is None:
                continue
            entries.append({
                "doc_id": d.id,
                "title": d.title,
                "version": d.version,
                "unit": unit,
                "unit_name": unit_names.get(unit, unit),
                "level": unit_level_name(unit),
                "distance": anc.index(unit),
                "effective_from": d.effective_from.isoformat() if d.effective_from else "",
                "effective_to": d.effective_to.isoformat() if d.effective_to else "",
            })
        if not entries:
            return []
        best = min(e["distance"] for e in entries)
        for e in entries:
            if e["distance"] == best:
                e["applies"] = True
                e["reason"] = "cấp gần đơn vị của bạn nhất — được áp dụng"
            else:
                e["applies"] = False
                e["reason"] = "cấp %s chung hơn — bị bản đặc thù của cấp gần bạn hơn thay thế" % e["level"]
        return sorted(entries, key=lambda e: (e["distance"], e["doc_id"]))

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
