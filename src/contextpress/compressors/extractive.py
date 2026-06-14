from __future__ import annotations

import re
from dataclasses import dataclass

from contextpress.tokenizer import TokenCounter


_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")
_WORD_RE = re.compile(r"[A-Za-z0-9_#./:-]+")


@dataclass(slots=True)
class ExtractiveCompressor:
    model: str = "gpt-4o-mini"

    def __post_init__(self) -> None:
        self.counter = TokenCounter(self.model)

    def compress(self, text: str, query: str = "", max_tokens: int = 1_000) -> str:
        if max_tokens < 0:
            raise ValueError("max_tokens must be >= 0")
        if self.counter.fits(text, max_tokens):
            return text

        sentences = [part.strip() for part in _SENTENCE_RE.split(text or "") if part.strip()]
        scored = [(self._score(sentence, query), index, sentence) for index, sentence in enumerate(sentences)]
        scored.sort(key=lambda item: (-item[0], item[1]))

        chosen: list[tuple[int, str]] = []
        used = 0
        for score, index, sentence in scored:
            sentence_tokens = self.counter.count(sentence)
            if sentence_tokens == 0 or used + sentence_tokens > max_tokens:
                continue
            if score > 0 or not chosen:
                chosen.append((index, sentence))
                used += sentence_tokens

        chosen.sort(key=lambda item: item[0])
        result = " ".join(sentence for _, sentence in chosen)
        return result if self.counter.fits(result, max_tokens) else self.counter.trim(result, max_tokens)

    def _score(self, sentence: str, query: str) -> float:
        lower = sentence.lower()
        sentence_terms = set(_WORD_RE.findall(lower))
        query_terms = set(_WORD_RE.findall((query or "").lower()))
        score = len(sentence_terms & query_terms) * 3

        if re.search(r"\d", sentence):
            score += 2
        if re.search(r"https?://|www\.", lower):
            score += 2
        if re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\(", sentence) or re.search(r"\b[A-Z][A-Za-z0-9]+[A-Z][A-Za-z0-9]*\b", sentence):
            score += 1.5
        if sentence.endswith(":") or sentence.startswith(("#", "-", "*")):
            score += 1.5
        if re.search(r"\b(must|should|required|preserve|constraint|risk|warning|error|security)\b", lower):
            score += 2
        if re.search(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b", sentence):
            score += 1
        return score
