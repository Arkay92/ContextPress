# Prompt Cache Layout

```python
from contpress import CacheAwarePrompt

prompt = CacheAwarePrompt(
    stable=["system rules", "tool schema"],
    dynamic=["current user question", "retrieved context"],
).build()
```

Stable content should be long-lived. Timestamps, request IDs, and retrieved
context belong in the dynamic tail.
