from __future__ import annotations

from .org import unit_level_name

# Cấp tổ chức dùng để mô tả kết quả đối chiếu cho người dùng.
LEVEL_ORDER = ["Tập đoàn", "Công ty", "Phòng ban", "Nhóm"]


def matched_unit(doc, anc):
    """Đơn vị cụ thể nhất trong scope của tài liệu mà người hỏi thuộc về.

    anc = đường dẫn đơn vị của người hỏi, anc[0] là đơn vị trực tiếp.
    Trả về None nếu tài liệu không áp dụng cho người hỏi (ngoài phạm vi).
    """
    for unit in anc:
        if unit in doc.scope_units:
            return unit
    return None


def distance(doc, anc):
    """Số cấp từ đơn vị của người hỏi tới đơn vị áp dụng của tài liệu.

    0 = đúng đơn vị của người hỏi, số lớn hơn = áp dụng chung hơn.
    None = không áp dụng.
    """
    unit = matched_unit(doc, anc)
    if unit is None:
        return None
    return anc.index(unit)


def level_name(unit):
    return unit_level_name(unit) if unit else "Đơn vị"


def resolve_scope(candidates, anc):
    """Chọn tài liệu áp dụng cho người hỏi trong một nhóm tài liệu cùng chủ đề.

    Quy tắc (Change Request B3 — xung đột giữa các cấp):
      1. Tài liệu không áp dụng cho người hỏi (ngoài phạm vi đơn vị/nhóm quyền) bị loại.
      2. Trong các tài liệu còn lại, tài liệu áp dụng ở cấp GẦN người hỏi nhất thắng
         (bản đặc thù theo đơn vị thay bản chung của cấp trên).
      3. Nếu hai tài liệu cùng cấp áp dụng có nội dung khác nhau → không tự chọn
         (CONFLICT), vì không có căn cứ để biết cái nào đúng.

    Trả về dict:
      status   : "ok" | "conflict" | "none"
      chosen   : tài liệu được chọn (None nếu conflict/none)
      applied  : danh sách tài liệu cùng cấp đã dùng để đối chiếu
      conflict : danh sách tài liệu cùng cấp nhưng nội dung khác nhau
      levels   : mọi tài liệu kèm khoảng cách cấp (để giải thích cho người dùng)
    """
    entries = []
    for doc in candidates:
        unit = matched_unit(doc, anc)
        if unit is None:
            continue
        entries.append({
            "doc": doc,
            "unit": unit,
            "dist": anc.index(unit),
            "level": level_name(unit),
        })

    if not entries:
        return {"status": "none", "chosen": None, "applied": [], "conflict": [], "levels": []}

    best_dist = min(e["dist"] for e in entries)
    at_level = [e for e in entries if e["dist"] == best_dist]
    contents = {e["doc"].content.strip() for e in at_level}

    ordered = sorted(entries, key=lambda e: (e["dist"], e["doc"].id))
    for e in ordered:
        e["applied"] = e["dist"] == best_dist

    if len(at_level) > 1 and len(contents) > 1:
        return {
            "status": "conflict",
            "chosen": None,
            "applied": [e["doc"] for e in at_level],
            "conflict": [e["doc"] for e in at_level],
            "levels": ordered,
        }

    # Nội dung giống nhau ở cùng cấp → lấy bản có hiệu lực mới nhất.
    chosen = max(at_level, key=lambda e: (e["doc"].effective_from, e["doc"].id))
    return {
        "status": "ok",
        "chosen": chosen["doc"],
        "applied": [chosen["doc"]],
        "conflict": [],
        "levels": ordered,
    }


def general_levels(levels, best_dist):
    """Các tài liệu ở cấp chung hơn so với bản áp dụng (dùng để đối chiếu)."""
    return [e for e in levels if e["dist"] > best_dist]


def scope_report(levels, best_dist, unit_names, conflict=False):
    """Diễn giải kết quả đối chiếu cấp cho người dùng và cho giao diện.

    best_dist = khoảng cách của bản được áp dụng (None nếu không có).
    conflict = True khi các bản cùng cấp mâu thuẫn nhau, chưa chọn được bản áp dụng.
    """
    applied, others = [], []
    for e in levels:
        item = {
            "doc_id": e["doc"].id,
            "title": e["doc"].title,
            "version": e["doc"].version,
            "unit": e["unit"],
            "unit_name": unit_names.get(e["unit"], e["unit"]),
            "level": e["level"],
            "distance": e["dist"],
        }
        if best_dist is not None and e["dist"] == best_dist:
            if conflict:
                item["reason"] = "cùng cấp, nội dung khác nhau — chưa xác định được bản áp dụng"
                others.append(item)
            else:
                applied.append(item)
        elif best_dist is not None:
            item["reason"] = "cấp %s chung hơn — bản đặc thù của cấp gần bạn hơn được ưu tiên" % e["level"]
            others.append(item)
    return applied, others
