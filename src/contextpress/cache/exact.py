from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExactPromptCache:
    namespace: str = "contpress"
    _data: dict[str, Any] = field(default_factory=dict)

    def lookup(self, prompt: str) -> Any:
        return self._data.get(self._key(prompt))

    def add(self, prompt: str, value: Any) -> None:
        self._data[self._key(prompt)] = value

    def _key(self, prompt: str) -> str:
        digest = hashlib.sha256((prompt or "").encode("utf-8")).hexdigest()
        return f"{self.namespace}:{digest}"
