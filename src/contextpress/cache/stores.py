from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class InMemoryStore:
    data: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str) -> Any:
        return self.data.get(key)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value


class RedisStore:
    def __init__(self, url: str = "redis://localhost:6379/0", prefix: str = "contpress") -> None:
        try:
            import redis
        except ImportError as exc:
            raise ImportError("Install redis separately to use RedisStore: pip install redis") from exc
        self.client = redis.Redis.from_url(url)
        self.prefix = prefix

    def get(self, key: str) -> bytes | None:
        return self.client.get(f"{self.prefix}:{key}")

    def set(self, key: str, value: bytes | str) -> None:
        self.client.set(f"{self.prefix}:{key}", value)
