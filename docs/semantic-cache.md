# Semantic Cache

Install extras:

```bash
pip install "contpress[semantic]"
```

```python
from contpress.cache import SemanticCache

cache = SemanticCache(path=".contpress-semantic-cache", similarity_threshold=0.88)
cache.add("How do I reduce tokens?", "Use counting, filtering, compression, and caching.")
hit = cache.lookup("How can I reduce LLM token usage?")
```
