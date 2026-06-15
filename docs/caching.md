# Exact Cache

```python
from contpress.cache import ExactPromptCache

cache = ExactPromptCache(path=".contpress-cache", ttl_seconds=86400, namespace="support-bot")
key = cache.make_key(model="gpt-4o-mini", prompt=prompt, temperature=0)
cached = cache.get(key)
```

CLI:

```bash
contpress cache stats
contpress cache list
contpress cache clear
```
