# Quickstart

```python
from contpress import ContextPress

cp = ContextPress(model="gpt-4o-mini", max_input_tokens=4000, provider="openai")
optimized = cp.optimize(task="Summarise this support log.", context=long_log)

print(optimized.text)
print(optimized.report.to_markdown())
```
