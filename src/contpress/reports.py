from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class UsageReport:
    model: str
    input_tokens_before: int
    input_tokens_after: int
    output_tokens_limit: int = 0
    methods: list[str] = field(default_factory=list)
    estimated_cost_before: float | None = None
    estimated_cost_after: float | None = None
    cache_status: str = "not_checked"
    warnings: list[str] = field(default_factory=list)
    truncation_notes: list[str] = field(default_factory=list)

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

    @property
    def estimated_saving(self) -> float | None:
        if self.estimated_cost_before is None or self.estimated_cost_after is None:
            return None
        return max(0.0, self.estimated_cost_before - self.estimated_cost_after)

    def as_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "original_tokens": self.input_tokens_before,
            "optimized_tokens": self.input_tokens_after,
            "saved_tokens": self.saved_tokens,
            "compression_ratio": round(self.compression_ratio, 3),
            "reduction_percent": round(self.reduction_percent, 1),
            "output_tokens_limit": self.output_tokens_limit,
            "estimated_cost_before": self.estimated_cost_before,
            "estimated_cost_after": self.estimated_cost_after,
            "estimated_saving": self.estimated_saving,
            "cache_status": self.cache_status,
            "methods": self.methods,
            "warnings": self.warnings,
            "truncation_notes": self.truncation_notes,
        }

    def __getitem__(self, key: str) -> Any:
        return self.as_dict()[key]

    def __contains__(self, key: str) -> bool:
        return key in self.as_dict()

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), indent=2)

    def to_markdown(self) -> str:
        lines = [
            "ContextPress Report",
            "-------------------",
            f"Original tokens: {self.input_tokens_before:,}",
            f"Optimized tokens: {self.input_tokens_after:,}",
            f"Saved tokens: {self.saved_tokens:,}",
            f"Reduction: {self.reduction_percent:.1f}%",
            "",
        ]
        if self.estimated_cost_before is not None and self.estimated_cost_after is not None:
            lines.extend(
                [
                    f"Estimated cost before: ${self.estimated_cost_before:.6f}",
                    f"Estimated cost after:  ${self.estimated_cost_after:.6f}",
                    f"Estimated saving:      ${self.estimated_saving or 0:.6f}",
                    "",
                ]
            )
        lines.append(f"Cache status: {self.cache_status}")
        lines.append("")
        if self.methods:
            lines.append("Methods:")
            lines.extend(f"- {method}" for method in self.methods)
            lines.append("")
        if self.warnings:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in self.warnings)
            lines.append("")
        if self.truncation_notes:
            lines.append("Truncation notes:")
            lines.extend(f"- {note}" for note in self.truncation_notes)
        return "\n".join(lines).rstrip()

    def summary(self) -> str:
        return self.to_markdown()
