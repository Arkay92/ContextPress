from __future__ import annotations

from typing import Protocol


class BaseCompressor(Protocol):
    def compress(self, text: str, query: str = "", max_tokens: int = 1_000) -> str:
        ...
