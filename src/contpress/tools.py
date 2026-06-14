from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from contpress.formatters import compact_json, drop_nulls


@dataclass(slots=True)
class ToolSchemaCompactor:
    drop_descriptions: bool = False

    def compact(self, schema: Mapping[str, Any]) -> str:
        return compact_json(self._compact_value(drop_nulls(dict(schema))))

    def _compact_value(self, value: Any) -> Any:
        if isinstance(value, Mapping):
            result = {}
            for key, item in value.items():
                if self.drop_descriptions and key in {"description", "title", "examples"}:
                    continue
                result[key] = self._compact_value(item)
            return result
        if isinstance(value, list):
            return [self._compact_value(item) for item in value]
        return value


@dataclass(slots=True)
class AgentTraceCompactor:
    keep_errors: bool = True
    keep_final: bool = True

    def compact(self, events: Sequence[Mapping[str, Any]]) -> str:
        compacted = []
        for event in events:
            event_type = str(event.get("type", ""))
            if self.keep_errors and event_type in {"error", "exception"}:
                compacted.append(event)
            elif self.keep_final and event_type in {"final", "result"}:
                compacted.append(event)
            elif event_type in {"tool_call", "tool_result", "decision"}:
                compacted.append({key: event.get(key) for key in ("type", "name", "summary", "status") if key in event})
        return compact_json(compacted)
