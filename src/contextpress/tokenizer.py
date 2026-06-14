from __future__ import annotations

import re
from dataclasses import dataclass


class _RegexEncoding:
    """Small fallback for local tests when tiktoken is not installed."""

    _pattern = re.compile(r"\w+|[^\w\s]", re.UNICODE)

    def encode(self, text: str) -> list[str]:
        return self._pattern.findall(text or "")

    def decode(self, tokens: list[str]) -> str:
        text = " ".join(tokens)
        return re.sub(r"\s+([,.;:!?%)\]}])", r"\1", text)


def _encoding_for_model(model: str):
    try:
        import tiktoken

        try:
            return tiktoken.encoding_for_model(model)
        except KeyError:
            return tiktoken.get_encoding("cl100k_base")
    except ImportError:
        return _RegexEncoding()


@dataclass(slots=True)
class TokenCounter:
    model: str = "gpt-4o-mini"

    def __post_init__(self) -> None:
        self.encoding = _encoding_for_model(self.model)

    def count(self, text: str) -> int:
        return len(self.encoding.encode(text or ""))

    def trim(self, text: str, max_tokens: int) -> str:
        if max_tokens < 0:
            raise ValueError("max_tokens must be >= 0")
        tokens = self.encoding.encode(text or "")
        return self.encoding.decode(tokens[:max_tokens])

    def fits(self, text: str, budget: int) -> bool:
        if budget < 0:
            raise ValueError("budget must be >= 0")
        return self.count(text) <= budget
