from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class User:
    id: str
    name: str
    unit: str
    role: str
    groups: list


@dataclass
class Document:
    id: str
    title: str
    family: str
    version: str
    unit: str
    scope_units: list
    scope_groups: list
    effective_from: date
    effective_to: Optional[date]
    status: str
    category: str
    content: str


@dataclass
class Source:
    doc_id: str
    title: str
    version: str
    unit_name: str
    effective_from: date
    effective_to: Optional[date]


@dataclass
class Answer:
    kind: str  # "OK" | "CONFLICT" | "REFUSE"
    text: str
    sources: list
    reason: str = ""  # nội bộ: ok | no_source | out_of_scope
    debug: dict = field(default_factory=dict)