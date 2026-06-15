from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SemanticCacheHit:
    answer: str
    score: float
    query: str
    metadata: dict[str, Any]

    def as_dict(self) -> dict[str, object]:
        return {
            "answer": self.answer,
            "score": round(self.score, 4),
            "query": self.query,
            "metadata": self.metadata,
        }


class SemanticCache:
    def __init__(
        self,
        path: str = ".contpress-semantic-cache",
        similarity_threshold: float = 0.88,
        namespace: str = "default",
        ttl_seconds: int | None = None,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        try:
            import faiss
            import numpy as np
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError('Install with: pip install "contpress[semantic]"') from exc

        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.similarity_threshold = similarity_threshold
        self.namespace = namespace
        self.ttl_seconds = ttl_seconds
        self._np = np
        self._faiss = faiss
        self._model = SentenceTransformer(embedding_model)
        self._data_file = self.path / "entries.json"
        self._entries: list[dict[str, Any]] = self._load_entries()
        self._index = None
        self._rebuild_index()

    def add(self, query: str, answer: str, metadata: dict[str, Any] | None = None) -> None:
        vector = self._embed(query)
        self._entries.append(
            {
                "query": query,
                "answer": answer,
                "metadata": {**(metadata or {}), "created_at": time.time(), "namespace": self.namespace},
                "vector": vector.tolist(),
                "ttl_seconds": self.ttl_seconds,
            }
        )
        self._save_entries()
        self._rebuild_index()

    def lookup(
        self,
        query: str,
        provider: str | None = None,
        model: str | None = None,
        namespace: str | None = None,
    ) -> SemanticCacheHit | None:
        if not self._entries or self._index is None:
            return None
        vector = self._embed(query).reshape(1, -1)
        scores, indexes = self._index.search(vector, min(10, len(self._entries)))
        for score, index in zip(scores[0], indexes[0]):
            if index < 0 or float(score) < self.similarity_threshold:
                continue
            entry = self._entries[int(index)]
            if self._expired(entry):
                continue
            metadata = dict(entry.get("metadata", {}))
            if namespace and metadata.get("namespace") != namespace:
                continue
            if provider and metadata.get("provider") != provider:
                continue
            if model and metadata.get("model") != model:
                continue
            return SemanticCacheHit(
                answer=str(entry.get("answer", "")),
                score=float(score),
                query=str(entry.get("query", "")),
                metadata=metadata,
            )
        return None

    def clear(self) -> int:
        count = len(self._entries)
        self._entries = []
        self._save_entries()
        self._rebuild_index()
        return count

    def stats(self) -> dict[str, object]:
        return {"path": str(self.path), "namespace": self.namespace, "entries": len(self._entries)}

    def _embed(self, text: str):
        vector = self._model.encode([text], normalize_embeddings=True)
        return self._np.asarray(vector, dtype="float32")[0]

    def _load_entries(self) -> list[dict[str, Any]]:
        if not self._data_file.exists():
            return []
        return json.loads(self._data_file.read_text(encoding="utf-8"))

    def _save_entries(self) -> None:
        self._data_file.write_text(json.dumps(self._entries, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    def _rebuild_index(self) -> None:
        active = [entry for entry in self._entries if not self._expired(entry)]
        self._entries = active
        if not active:
            self._index = None
            return
        vectors = self._np.asarray([entry["vector"] for entry in active], dtype="float32")
        self._index = self._faiss.IndexFlatIP(vectors.shape[1])
        self._index.add(vectors)
        self._save_entries()

    def _expired(self, entry: dict[str, Any]) -> bool:
        ttl = entry.get("ttl_seconds")
        if ttl is None:
            return False
        created = float(entry.get("metadata", {}).get("created_at", 0))
        return time.time() - created > int(ttl)
