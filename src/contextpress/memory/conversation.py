from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from contextpress.tokenizer import TokenCounter


FILLER_RE = re.compile(r"^(thanks|thank you|ok|okay|cool|great|sounds good)[.! ]*$", re.IGNORECASE)


@dataclass(slots=True)
class ConversationPruner:
    model: str = "gpt-4o-mini"
    keep_latest: int = 6

    def __post_init__(self) -> None:
        self.counter = TokenCounter(self.model)

    def prune(self, messages: Sequence[dict[str, Any]], current_query: str = "", max_tokens: int = 3_000) -> list[dict[str, Any]]:
        if max_tokens < 0:
            raise ValueError("max_tokens must be >= 0")
        system = [msg for msg in messages if msg.get("role") == "system"]
        non_system = [msg for msg in messages if msg.get("role") != "system"]
        latest = non_system[-self.keep_latest :]
        older = [msg for msg in non_system[: -self.keep_latest] if self._is_relevant(msg, current_query)]
        candidates = system + older + latest

        kept: list[dict[str, Any]] = []
        used = 0
        for msg in reversed(candidates):
            tokens = self.counter.count(str(msg.get("content", "")))
            if used + tokens <= max_tokens:
                kept.append(dict(msg))
                used += tokens
        return list(reversed(kept))

    def _is_relevant(self, message: dict[str, Any], query: str) -> bool:
        content = str(message.get("content", "")).strip()
        if not content or FILLER_RE.match(content):
            return False
        lower = content.lower()
        query_terms = set(re.findall(r"[A-Za-z0-9_./-]+", (query or "").lower()))
        content_terms = set(re.findall(r"[A-Za-z0-9_./-]+", lower))
        if query_terms & content_terms:
            return True
        return bool(re.search(r"\b(decision|constraint|must|prefer|file|path|bug|risk|todo)\b", lower))
