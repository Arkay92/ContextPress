from __future__ import annotations

import difflib
from dataclasses import dataclass

from contpress.tokenizer import TokenCounter


@dataclass(slots=True)
class CompressionReport:
    original_tokens: int
    compressed_tokens: int
    method: str

    @property
    def saved_tokens(self) -> int:
        return max(0, self.original_tokens - self.compressed_tokens)

    @property
    def compression_ratio(self) -> float:
        if self.original_tokens == 0:
            return 1.0
        return self.compressed_tokens / self.original_tokens

    def as_dict(self) -> dict[str, object]:
        return {
            "original_tokens": self.original_tokens,
            "compressed_tokens": self.compressed_tokens,
            "saved_tokens": self.saved_tokens,
            "compression_ratio": round(self.compression_ratio, 3),
            "method": self.method,
        }


def compression_report(original: str, compressed: str, method: str = "extractive", model: str = "gpt-4o-mini") -> CompressionReport:
    counter = TokenCounter(model)
    return CompressionReport(counter.count(original), counter.count(compressed), method)


def compression_diff(original: str, compressed: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            original.splitlines(),
            compressed.splitlines(),
            fromfile="original",
            tofile="compressed",
            lineterm="",
        )
    )
