from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field


@dataclass(slots=True)
class PromptDiff:
    original: str
    optimized: str
    unified: str
    removed: list[str] = field(default_factory=list)
    preserved: list[str] = field(default_factory=list)

    @classmethod
    def compare(cls, original: str, optimized: str) -> "PromptDiff":
        unified = "\n".join(
            difflib.unified_diff(
                original.splitlines(),
                optimized.splitlines(),
                fromfile="original",
                tofile="optimized",
                lineterm="",
            )
        )
        removed = _removed_categories(original, optimized)
        preserved = _preserved_categories(original, optimized)
        return cls(original=original, optimized=optimized, unified=unified, removed=removed, preserved=preserved)

    def to_markdown(self) -> str:
        lines = ["Prompt Diff", "-----------", "", "Removed:"]
        lines.extend(f"- {item}" for item in (self.removed or ["No obvious category removals detected."]))
        lines.append("")
        lines.append("Preserved:")
        lines.extend(f"- {item}" for item in (self.preserved or ["No preservation signals detected."]))
        lines.append("")
        lines.append("Unified diff:")
        lines.append("```diff")
        lines.append(self.unified)
        lines.append("```")
        return "\n".join(lines)


def _removed_categories(original: str, optimized: str) -> list[str]:
    removed = []
    lower_original = original.lower()
    lower_optimized = optimized.lower()
    if lower_original.count("be concise") > lower_optimized.count("be concise"):
        removed.append("duplicated instructions")
    if len(optimized) < len(original) * 0.8:
        removed.append("low-relevance or excess context")
    if "context:" in lower_original and "context:" not in lower_optimized:
        removed.append("unrelated context block")
    return removed


def _preserved_categories(original: str, optimized: str) -> list[str]:
    checks = [
        ("IDs", r"\b[A-Z]{1,5}-?\d{2,}\b"),
        ("numbers", r"\b\d+(?:\.\d+)?\b"),
        ("URLs", r"https?://\S+"),
        ("code blocks", r"```"),
        ("constraints", r"\b(must|should|required|preserve|constraint)\b"),
    ]
    preserved = []
    for label, pattern in checks:
        if re.search(pattern, original, re.IGNORECASE) and re.search(pattern, optimized, re.IGNORECASE):
            preserved.append(label)
    return preserved
