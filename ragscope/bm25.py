from __future__ import annotations

import math


def _tokens(text: str) -> list:
    text = text.lower()
    words = [w for w in text.split() if w]
    nospace = "".join(ch for ch in text if not ch.isspace())
    bigrams = [nospace[i : i + 2] for i in range(len(nospace) - 1)]
    return list(words) + list(bigrams)


def _field_tokens(text: str) -> list:
    toks = _tokens(text)
    return toks


class BM25:
    def __init__(self, docs, k1=1.6, b=0.75, title_boost=3):
        self.docs = list(docs)
        self.k1 = k1
        self.b = b
        self.doc_tokens = []
        self.doc_len = []
        self.df = {}
        for d in self.docs:
            body = _field_tokens(d.content)
            title = _field_tokens(d.title) * title_boost
            tokens = body + title
            self.doc_tokens.append(tokens)
            self.doc_len.append(len(tokens))
            for t in set(tokens):
                self.df[t] = self.df.get(t, 0) + 1
        n = len(self.docs)
        self.avgdl = sum(self.doc_len) / n if n else 0.0
        self.idf = {}
        for t, df in self.df.items():
            self.idf[t] = math.log((n - df + 0.5) / (df + 0.5) + 1.0)

    def search(self, query: str) -> list:
        qtokens = _tokens(query)
        if not qtokens or not self.docs:
            return []
        scores = []
        for i, toks in enumerate(self.doc_tokens):
            dl = self.doc_len[i]
            score = 0.0
            for t in set(qtokens):
                tf = toks.count(t)
                if tf == 0:
                    continue
                idf = self.idf.get(t, 0.0)
                score += idf * (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
            scores.append((i, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return [(self.docs[i], s) for i, s in scores if s > 0]