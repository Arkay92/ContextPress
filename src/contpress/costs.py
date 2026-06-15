from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path


@dataclass(slots=True)
class ModelPrice:
    provider: str
    model: str
    input_per_1m: float
    output_per_1m: float


class PricingRegistry:
    def __init__(self, override_file: str | None = None) -> None:
        self._prices = self._load_bundled()
        if override_file:
            self._prices.update(self._load_file(Path(override_file)))

    def get(self, provider: str, model: str) -> ModelPrice:
        key = f"{provider.lower()}:{model}"
        price = self._prices.get(key)
        if not price:
            known = ", ".join(sorted(self._prices))
            raise ValueError(f"Unknown provider/model price: {key}. Known prices: {known}")
        return ModelPrice(provider.lower(), model, float(price["input_per_1m"]), float(price["output_per_1m"]))

    def list(self) -> dict[str, dict[str, float]]:
        return dict(sorted(self._prices.items()))

    def _load_bundled(self) -> dict[str, dict[str, float]]:
        data = files("contpress.pricing").joinpath("models.json").read_text(encoding="utf-8")
        return json.loads(data)

    def _load_file(self, path: Path) -> dict[str, dict[str, float]]:
        return json.loads(path.read_text(encoding="utf-8"))


@dataclass(slots=True)
class CostEstimate:
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    price_warning: str = "Prices are bundled estimates and may differ from current provider billing."

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
            "price_warning": self.price_warning,
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
                f"Warning: {self.price_warning}",
            ]
        )


@dataclass(slots=True)
class CostReport:
    provider: str
    model: str
    input_tokens_before: int
    input_tokens_after: int
    output_tokens: int
    original_cost_usd: float
    optimized_cost_usd: float
    saved_usd: float
    saving_percent: float
    price_warning: str = "Prices are bundled estimates and may differ from current provider billing."

    def as_dict(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "model": self.model,
            "input_tokens_before": self.input_tokens_before,
            "input_tokens_after": self.input_tokens_after,
            "output_tokens": self.output_tokens,
            "original_cost_usd": round(self.original_cost_usd, 6),
            "optimized_cost_usd": round(self.optimized_cost_usd, 6),
            "saved_usd": round(self.saved_usd, 6),
            "saving_percent": round(self.saving_percent, 1),
            "price_warning": self.price_warning,
        }

    def summary(self) -> str:
        return "\n".join(
            [
                f"Original estimated cost: ${self.original_cost_usd:.6f}",
                f"Optimized estimated cost: ${self.optimized_cost_usd:.6f}",
                f"Estimated saving: ${self.saved_usd:.6f}",
                f"Reduction: {self.saving_percent:.1f}%",
                f"Warning: {self.price_warning}",
            ]
        )


class CostEstimator:
    def __init__(self, provider: str, model: str, pricing_file: str | None = None) -> None:
        self.provider = provider
        self.model = model
        self.registry = PricingRegistry(pricing_file)

    def estimate(
        self,
        input_tokens_before: int,
        input_tokens_after: int,
        output_tokens: int = 0,
    ) -> CostReport:
        original = estimate_cost(self.provider, self.model, input_tokens_before, output_tokens, self.registry)
        optimized = estimate_cost(self.provider, self.model, input_tokens_after, output_tokens, self.registry)
        saved = max(0.0, original.total_cost_usd - optimized.total_cost_usd)
        percent = 0.0 if original.total_cost_usd == 0 else (saved / original.total_cost_usd) * 100
        return CostReport(
            provider=self.provider.lower(),
            model=self.model,
            input_tokens_before=input_tokens_before,
            input_tokens_after=input_tokens_after,
            output_tokens=output_tokens,
            original_cost_usd=original.total_cost_usd,
            optimized_cost_usd=optimized.total_cost_usd,
            saved_usd=saved,
            saving_percent=percent,
        )


def estimate_cost(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int = 0,
    registry: PricingRegistry | None = None,
) -> CostEstimate:
    price = (registry or PricingRegistry()).get(provider, model)
    return CostEstimate(
        provider=price.provider,
        model=price.model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_cost_usd=(input_tokens / 1_000_000) * price.input_per_1m,
        output_cost_usd=(output_tokens / 1_000_000) * price.output_per_1m,
    )
