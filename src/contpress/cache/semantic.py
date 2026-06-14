from __future__ import annotations


class SemanticCache:
    def __init__(self, *args, **kwargs) -> None:
        try:
            import diskcache  # noqa: F401
            import faiss  # noqa: F401
            from sentence_transformers import SentenceTransformer  # noqa: F401
        except ImportError as exc:
            raise ImportError("Install with: pip install contpress[semantic]") from exc
        raise NotImplementedError("SemanticCache requires a vector store implementation; install extras and configure a store.")
