from __future__ import annotations

import csv
import io
import json
from collections.abc import Mapping, Sequence
from typing import Any


def compact_json(data: Any, ensure_ascii: bool = False) -> str:
    return json.dumps(data, separators=(",", ":"), ensure_ascii=ensure_ascii)


def drop_nulls(data: Any) -> Any:
    if isinstance(data, Mapping):
        return {key: drop_nulls(value) for key, value in data.items() if value is not None}
    if isinstance(data, list):
        return [drop_nulls(item) for item in data if item is not None]
    return data


def shorten_keys(data: Any, mapping: Mapping[str, str]) -> Any:
    if isinstance(data, Mapping):
        return {mapping.get(str(key), key): shorten_keys(value, mapping) for key, value in data.items()}
    if isinstance(data, list):
        return [shorten_keys(item, mapping) for item in data]
    return data


def json_to_csv_if_tabular(data: Any) -> str | None:
    if not isinstance(data, Sequence) or isinstance(data, (str, bytes)) or not data:
        return None
    if not all(isinstance(row, Mapping) for row in data):
        return None

    headers: list[str] = []
    for row in data:
        for key in row:
            if str(key) not in headers:
                headers.append(str(key))

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue().strip()


def compact_table(rows: Sequence[Mapping[str, Any]], headers: Sequence[str] | None = None) -> str:
    if not rows:
        return ""
    selected_headers = list(headers or rows[0].keys())
    lines = ["|".join(str(header) for header in selected_headers)]
    for row in rows:
        lines.append("|".join("" if row.get(header) is None else str(row.get(header)) for header in selected_headers))
    return "\n".join(lines)
