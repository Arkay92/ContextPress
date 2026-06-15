# Cost Estimation

```python
from contpress import CostEstimator

report = CostEstimator("openai", "gpt-4o-mini").estimate(
    input_tokens_before=12000,
    input_tokens_after=3500,
    output_tokens=500,
)
print(report.summary())
```

Prices are bundled estimates. Use a custom pricing file when billing precision
matters.
