from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

from .models import Document, User


def load_users(path) -> list:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return [
        User(id=u["id"], name=u["name"], unit=u["unit"], role=u["role"], groups=list(u.get("groups", [])))
        for u in raw["users"]
    ]


def _d(value, default=None):
    if not value:
        return default
    return date.fromisoformat(str(value))


def load_documents(path) -> list:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    docs = []
    for d in raw["documents"]:
        docs.append(
            Document(
                id=d["id"],
                title=d["title"],
                family=d.get("family", ""),
                version=d.get("version", "1.0"),
                unit=d.get("unit", "appota"),
                scope_units=list(d.get("scope_units", ["appota"])),
                scope_groups=list(d.get("scope_groups", [])),
                effective_from=_d(d.get("effective_from")),
                effective_to=_d(d.get("effective_to")),
                status=d.get("status", "active"),
                category=d.get("category", ""),
                content=d["content"].strip(),
            )
        )
    return docs


def usable(doc: Document, today: date, all_units: dict) -> bool:
    if doc.status != "active":
        return False
    if doc.effective_from is None or doc.effective_from > today:
        return False
    if doc.effective_to is not None and doc.effective_to < today:
        return False
    return True


def visible(doc: Document, unit_ancestors: list, user_groups: list) -> bool:
    if not (set(doc.scope_units) & set(unit_ancestors)):
        return False
    if doc.scope_groups and not (set(doc.scope_groups) & set(user_groups)):
        return False
    return True


def scope_depth(doc: Document) -> int:
    depths = [len([p for p in u.split(".") if u]) for u in doc.scope_units]
    return max(depths) if depths else 0


def visibility_reason(doc: Document, unit_ancestors: list, user_groups: list, today: date) -> tuple:
    reasons = []
    if doc.status != "active":
        reasons.append("inactive_status")
    if doc.effective_from is None or doc.effective_from > today:
        reasons.append("not_yet_effective")
    if doc.effective_to is not None and doc.effective_to < today:
        reasons.append("expired")
    if not (set(doc.scope_units) & set(unit_ancestors)):
        reasons.append("out_of_scope_unit")
    if doc.scope_groups and not (set(doc.scope_groups) & set(user_groups)):
        reasons.append("out_of_scope_group")
    return (len(reasons) == 0, reasons)