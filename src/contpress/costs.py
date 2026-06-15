from __future__ import annotations

from dataclasses import dataclass


# Prices are USD per 1M tokens. Treat these as configurable estimates, not billing authority.
PRICE_TABLE: dict[str, dict[str, tuple[float, float]]] = {
    "openai": {
        "gpt-4o-mini": (0.15, 0.60),
        "gpt-4o": (5.00, 15.00),
        "gpt-4.1": (2.00, 8.00),
        "gpt-4.1-mini": (0.40, 1.60),
        "gpt-4.1-nano": (0.10, 0.40),
    },
    "anthropic": {
        "claude-sonnet-4-20250514": (3.00, 15.00),
        "claude-3-5-haiku-latest": (0.80, 4.00),
    },
}


@dataclass(slots=True)
class CostEstimate:
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    input_cost_usd: float
    output_cost_usd: float

    @property
    def total_cost_usd(self) -> float:
        return self.input_cost_usd + self.output_cost_usd

    def as_dict(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "input_cost_usd": round(self.input_cost_usd, 6),
            "output_cost_usd": round(self.output_cost_usd, 6),
            "total_cost_usd": round(self.total_cost_usd, 6),
        }

    def summary(self) -> str:
        return "\n".join(
            [
                f"Provider: {self.provider}",
                f"Model: {self.model}",
                f"Input tokens: {self.input_tokens:,}",
                f"Output tokens: {self.output_tokens:,}",
                f"Estimated input cost: ${self.input_cost_usd:.6f}",
                f"Estimated output cost: ${self.output_cost_usd:.6f}",
                f"Estimated total cost: ${self.total_cost_usd:.6f}",
            ]
        )


def estimate_cost(provider: str, model: str, input_tokens: int, output_tokens: int = 0) -> CostEstimate:
    provider_key = provider.lower()
    model_prices = PRICE_TABLE.get(provider_key)
    if not model_prices or model not in model_prices:
        known = ", ".join(sorted(model_prices or PRICE_TABLE))
        raise ValueError(f"Unknown provider/model price. Known for {provider_key or 'providers'}: {known}")
    input_per_million, output_per_million = model_prices[model]
    return CostEstimate(
        provider=provider_key,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_cost_usd=(input_tokens / 1_000_000) * input_per_million,
        output_cost_usd=(output_tokens / 1_000_000) * output_per_million,
    )
