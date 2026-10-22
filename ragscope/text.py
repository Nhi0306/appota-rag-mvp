from __future__ import annotations

import re

STOPWORDS = {
    "quy", "định", "trình", "thế", "nào", "ra", "sao", "bao", "nhiêu",
    "của", "tôi", "như", "cho", "với", "để", "và", "là", "có", "theo",
    "được", "thì", "nếu", "hay", "nên", "đó", "này", "một", "không",
    "đang", "đã", "sẽ", "tại", "về", "thế", "tất", "cả", "mấy", "ông",
}


def substantive_words(query: str) -> set:
    words = [w.lower() for w in re.findall(r"[a-zà-ỹ0-9]+", query.lower())]
    return {w for w in words if len(w) >= 3 and w not in STOPWORDS}
