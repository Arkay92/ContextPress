from __future__ import annotations

from dataclasses import dataclass, field


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
