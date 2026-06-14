from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from contextpress.compressors.extractive import ExtractiveCompressor
from contextpress.rag.rerank import keyword_rerank
from contextpress.tokenizer import TokenCounter


@dataclass(slots=True)
class ContextFilter:
    model: str = "gpt-4o-mini"
    mode: str = "keyword"
    counter: TokenCounter = field(init=False, repr=False)
    compressor: ExtractiveCompressor = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.counter = TokenCounter(self.model)
        self.compressor = ExtractiveCompressor(self.model)

    def filter(self, query: str, chunks: Sequence[str], max_tokens: int = 2_500, mode: str | None = None) -> str:
        selected_mode = mode or self.mode
        if selected_mode not in {"keyword", "sentence", "embedding", "llmlingua"}:
            raise ValueError("mode must be keyword, sentence, embedding, or llmlingua")
        if selected_mode == "embedding":
            self._require_extra("semantic")
        if selected_mode == "llmlingua":
            self._require_extra("compress")

        ranked = keyword_rerank(query, chunks)
        chosen: list[str] = []
        used = 0
        for _, chunk in ranked:
            candidate = self.compressor.compress(chunk, query=query, max_tokens=max_tokens)
            tokens = self.counter.count(candidate)
            if tokens == 0:
                continue
            if used + tokens <= max_tokens:
                chosen.append(candidate)
                used += tokens
        return "\n\n".join(chosen)

    def _require_extra(self, extra: str) -> None:
        raise ImportError(f"Install with: pip install contextpress[{extra}]")
