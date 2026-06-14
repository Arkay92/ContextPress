from __future__ import annotations

import re
from collections.abc import Sequence


def keyword_rerank(query: str, chunks: Sequence[str]) -> list[tuple[float, str]]:
    terms = set(re.findall(r"[A-Za-z0-9_]+", (query or "").lower()))
    ranked = []
    for chunk in chunks:
        chunk_terms = set(re.findall(r"[A-Za-z0-9_]+", chunk.lower()))
        ranked.append((float(len(terms & chunk_terms)), chunk))
    return sorted(ranked, key=lambda item: item[0], reverse=True)
