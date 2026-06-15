from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CacheStats:
    path: str
    namespace: str
    entries: int
    hits: int
    misses: int

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "namespace": self.namespace,
            "entries": self.entries,
            "hits": self.hits,
            "misses": self.misses,
        }


class ExactPromptCache:
    def __init__(
        self,
        path: str = ".contpress-cache",
        ttl_seconds: int | None = None,
        namespace: str = "contpress",
    ) -> None:
        self.path = Path(path)
        self.ttl_seconds = ttl_seconds
        self.namespace = namespace
        self.path.mkdir(parents=True, exist_ok=True)
        self._stats_file = self.path / "_stats.json"

    def make_key(self, model: str, prompt: str, **settings: Any) -> str:
        payload = {
            "model": model,
            "namespace": self.namespace,
            "prompt": prompt or "",
            "settings": settings,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"{self.namespace}:{digest}"

    def get(self, key: str) -> Any | None:
        file = self._file_for_key(key)
        if not file.exists():
            self._bump("misses")
            return None
        payload = json.loads(file.read_text(encoding="utf-8"))
        if self._expired(payload):
            file.unlink(missing_ok=True)
            self._bump("misses")
            return None
        self._bump("hits")
        return payload.get("value")

    def set(self, key: str, value: Any) -> None:
        payload = {
            "key": key,
            "namespace": self.namespace,
            "created_at": time.time(),
            "ttl_seconds": self.ttl_seconds,
            "value": value,
        }
        self._file_for_key(key).write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    def lookup(self, prompt: str, model: str = "default", **settings: Any) -> Any | None:
        return self.get(self.make_key(model=model, prompt=prompt, **settings))

    def add(self, prompt: str, value: Any, model: str = "default", **settings: Any) -> None:
        self.set(self.make_key(model=model, prompt=prompt, **settings), value)

    def list(self) -> list[dict[str, object]]:
        entries = []
        for file in sorted(self.path.glob("*.json")):
            if file.name == self._stats_file.name:
                continue
            payload = json.loads(file.read_text(encoding="utf-8"))
            if not self._expired(payload):
                entries.append(
                    {
                        "key": payload.get("key"),
                        "namespace": payload.get("namespace"),
                        "created_at": payload.get("created_at"),
                        "ttl_seconds": payload.get("ttl_seconds"),
                    }
                )
        return entries

    def clear(self) -> int:
        count = 0
        for file in self.path.glob("*.json"):
            file.unlink(missing_ok=True)
            count += 1
        return count

    def stats(self) -> CacheStats:
        stats = self._read_stats()
        return CacheStats(
            path=str(self.path),
            namespace=self.namespace,
            entries=len(self.list()),
            hits=int(stats.get("hits", 0)),
            misses=int(stats.get("misses", 0)),
        )

    def _file_for_key(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.path / f"{digest}.json"

    def _expired(self, payload: dict[str, Any]) -> bool:
        ttl = payload.get("ttl_seconds")
        if ttl is None:
            return False
        return time.time() - float(payload.get("created_at", 0)) > int(ttl)

    def _read_stats(self) -> dict[str, int]:
        if not self._stats_file.exists():
            return {"hits": 0, "misses": 0}
        return json.loads(self._stats_file.read_text(encoding="utf-8"))

    def _bump(self, name: str) -> None:
        stats = self._read_stats()
        stats[name] = int(stats.get(name, 0)) + 1
        self._stats_file.write_text(json.dumps(stats, indent=2), encoding="utf-8")
