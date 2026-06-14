from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from contpress.formatters import compact_json


@dataclass(slots=True)
class OutputContract:
    fields: dict[str, str]
    format: str = "json"
    required: list[str] = field(default_factory=list)
    additional_instructions: list[str] = field(default_factory=list)

    def prompt(self) -> str:
        if self.format == "json":
            schema = {
                "format": "json",
                "required": self.required or list(self.fields),
                "fields": self.fields,
            }
            body = compact_json(schema)
        else:
            body = f"Format: {self.format}\nFields: {', '.join(self.fields)}"
        extras = "\n".join(f"- {item}" for item in self.additional_instructions)
        return f"Output contract:\n{body}" + (f"\n{extras}" if extras else "")
