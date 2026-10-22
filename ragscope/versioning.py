from __future__ import annotations

from .models import Document


def diff_documents(a: Document, b: Document) -> dict:
    la = [x.strip() for x in a.content.splitlines() if x.strip()]
    lb = [x.strip() for x in b.content.splitlines() if x.strip()]
    seta, setb = set(la), set(lb)
    return {
        "doc_a": a.id,
        "doc_b": b.id,
        "version_a": a.version,
        "version_b": b.version,
        "added": [x for x in lb if x not in seta],
        "removed": [x for x in la if x not in setb],
        "unchanged": [x for x in la if x in setb],
        "identical": la == lb,
    }


def sort_versions(docs: list) -> list:
    def key(d):
        parts = []
        for chunk in str(d.version).replace("-", ".").split("."):
            try:
                parts.append((0, int(chunk)))
            except ValueError:
                parts.append((1, chunk))
        return parts
    return sorted(docs, key=key)
