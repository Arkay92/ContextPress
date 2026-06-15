from __future__ import annotations

import re
from dataclasses import dataclass, field

from contpress.tokenizer import TokenCounter


@dataclass(slots=True)
class CacheLayoutReport:
    stable_tokens: int
    dynamic_tokens: int
    cache_friendly: bool
    recommendations: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "stable_tokens": self.stable_tokens,
            "dynamic_tokens": self.dynamic_tokens,
            "cache_friendly": self.cache_friendly,
            "recommendations": self.recommendations,
        }


@dataclass
class PromptCacheLayout:
    stable_blocks: list[tuple[str, str]] = field(default_factory=list)
    volatile_blocks: list[tuple[str, str]] = field(default_factory=list)

    def stable(self, title: str, body: str) -> "PromptCacheLayout":
        self.stable_blocks.append((title, body))
        return self

    def volatile(self, title: str, body: str) -> "PromptCacheLayout":
        self.volatile_blocks.append((title, body))
        return self

    def build(self) -> str:
        blocks = self.stable_blocks + self.volatile_blocks
        return "\n\n".join(f"{title}:\n{body.strip()}" for title, body in blocks if body and body.strip())

    def report(self, model: str = "gpt-4o-mini") -> CacheLayoutReport:
        return _layout_report([body for _, body in self.stable_blocks], [body for _, body in self.volatile_blocks], model)


@dataclass(slots=True)
class CacheAwarePrompt:
    stable: list[str]
    dynamic: list[str]
    model: str = "gpt-4o-mini"

    def build(self) -> str:
        stable = "\n\n".join(block.strip() for block in self.stable if block and block.strip())
        dynamic = "\n\n".join(block.strip() for block in self.dynamic if block and block.strip())
        return f"[stable prefix]\n{stable}\n\n[dynamic tail]\n{dynamic}".strip()

    def report(self) -> CacheLayoutReport:
        return _layout_report(self.stable, self.dynamic, self.model)


def cache_layout_report(prompt: str, model: str = "gpt-4o-mini") -> CacheLayoutReport:
    stable, dynamic = _split_prompt(prompt)
    return _layout_report([stable], [dynamic], model)


def _split_prompt(prompt: str) -> tuple[str, str]:
    marker = "[dynamic tail]"
    if marker in prompt:
        stable, dynamic = prompt.split(marker, 1)
        return stable.replace("[stable prefix]", "").strip(), dynamic.strip()
    midpoint = len(prompt) // 2
    return prompt[:midpoint], prompt[midpoint:]


def _layout_report(stable: list[str], dynamic: list[str], model: str) -> CacheLayoutReport:
    counter = TokenCounter(model)
    stable_text = "\n".join(stable)
    dynamic_text = "\n".join(dynamic)
    recommendations: list[str] = []
    if re.search(r"\b\d{4}-\d{2}-\d{2}|timestamp|request[_ -]?id|uuid\b", stable_text, re.IGNORECASE):
        recommendations.append("Move timestamps and request IDs to the dynamic tail.")
    if counter.count(stable_text) < counter.count(dynamic_text):
        recommendations.append("Put long-lived system rules, schemas, and standards in the stable prefix.")
    if not recommendations:
        recommendations.append("Stable prefix and dynamic tail look cache-friendly.")
    return CacheLayoutReport(
        stable_tokens=counter.count(stable_text),
        dynamic_tokens=counter.count(dynamic_text),
        cache_friendly=not any("Move" in item for item in recommendations),
        recommendations=recommendations,
    )
