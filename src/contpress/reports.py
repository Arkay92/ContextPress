from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class UsageReport:
    model: str
    input_tokens_before: int
    input_tokens_after: int
    output_tokens_limit: int = 0
    methods: list[str] = field(default_factory=list)

    @property
    def saved_tokens(self) -> int:
        return max(0, self.input_tokens_before - self.input_tokens_after)

    @property
    def compression_ratio(self) -> float:
        if self.input_tokens_before == 0:
            return 1.0
        return self.input_tokens_after / self.input_tokens_before

    @property
    def reduction_percent(self) -> float:
        return (1 - self.compression_ratio) * 100

    def as_dict(self) -> dict[str, object]:
        return {
            "model": self.model,
            "original_tokens": self.input_tokens_before,
            "optimized_tokens": self.input_tokens_after,
            "saved_tokens": self.saved_tokens,
            "compression_ratio": round(self.compression_ratio, 3),
            "reduction_percent": round(self.reduction_percent, 1),
            "output_tokens_limit": self.output_tokens_limit,
            "methods": self.methods,
        }

    def summary(self) -> str:
        methods = ", ".join(self.methods) if self.methods else "none"
        return "\n".join(
            [
                f"Original input: {self.input_tokens_before:,} tokens",
                f"Optimized input: {self.input_tokens_after:,} tokens",
                f"Saved: {self.saved_tokens:,} tokens",
                f"Reduction: {self.reduction_percent:.1f}%",
                f"Methods: {methods}",
            ]
        )
