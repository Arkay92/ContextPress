from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


def _bullets(items: Iterable[str]) -> str:
    return "\n".join(f"- {item}" for item in items if str(item).strip())


@dataclass
class PromptBuilder:
    _blocks: list[tuple[str, str]] = field(default_factory=list)

    def role(self, value: str) -> "PromptBuilder":
        return self._add("Role", value)

    def task(self, value: str) -> "PromptBuilder":
        return self._add("Task", value)

    def constraints(self, values: Iterable[str]) -> "PromptBuilder":
        return self._add("Constraints", _bullets(values))

    def instructions(self, values: Iterable[str]) -> "PromptBuilder":
        return self._add("Instructions", _bullets(values))

    def context(self, value: str) -> "PromptBuilder":
        return self._add("Context", value)

    def output(self, values: Iterable[str] | str) -> "PromptBuilder":
        if isinstance(values, str):
            return self._add("Output", values)
        return self._add("Output", _bullets(values))

    def block(self, title: str, value: str | Iterable[str]) -> "PromptBuilder":
        if isinstance(value, str):
            body = value
        else:
            body = _bullets(value)
        return self._add(title, body)

    def build(self) -> str:
        return "\n".join(f"{title}:\n{body}" if "\n" in body else f"{title}: {body}" for title, body in self._blocks if body)

    def _add(self, title: str, body: str) -> "PromptBuilder":
        clean = (body or "").strip()
        if clean:
            self._blocks.append((title.strip(), clean))
        return self
