from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from contpress.budgets import TokenBudget
from contpress.builder import PromptBuilder
from contpress.compressors.extractive import ExtractiveCompressor
from contpress.costs import CostEstimator
from contpress.formatters import compact_json
from contpress.profiles import get_compression_profile
from contpress.rag.filter import ContextFilter
from contpress.reports import UsageReport
from contpress.tokenizer import TokenCounter


@dataclass(slots=True)
class OptimizedPrompt:
    text: str
    report: UsageReport


class ContextPress:
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        max_input_tokens: int = 4_000,
        max_output_tokens: int | None = None,
        reserve_output_tokens: int | None = None,
        compression: str = "extractive",
        compression_profile: str = "balanced",
        provider: str | None = None,
    ) -> None:
        self.model = model
        self.max_input_tokens = max_input_tokens
        self.max_output_tokens = max_output_tokens if max_output_tokens is not None else reserve_output_tokens or 0
        self.compression = compression
        self.profile = get_compression_profile(compression_profile)
        self.provider = provider
        self.counter = TokenCounter(model)
        self.budget = TokenBudget(
            model=model,
            max_input_tokens=max_input_tokens,
            reserve_output_tokens=self.max_output_tokens,
        )

    def optimize(
        self,
        task: str,
        context: str | Sequence[str] | dict[str, Any] | list[Any] = "",
        instructions: Iterable[str] | None = None,
        output: Iterable[str] | str | None = None,
        role: str | None = None,
    ) -> OptimizedPrompt:
        methods: list[str] = []
        warnings: list[str] = list(self.profile.warnings)
        truncation_notes: list[str] = []
        original_context = self._stringify_context(context)
        original_prompt = self._build_prompt(task, original_context, instructions, output, role)
        original_tokens = self.counter.count(original_prompt)

        context_budget = max(0, int(self.budget.input_budget * self.profile.context_ratio))
        optimized_context = original_context
        if isinstance(context, Sequence) and not isinstance(context, (str, bytes, dict)) and all(isinstance(item, str) for item in context):
            optimized_context = ContextFilter(self.model).filter(task, list(context), max_tokens=context_budget)
            methods.append("context_filter")
        elif self.compression in {"extractive", "sentence_filter"} and not self.counter.fits(original_prompt, self.budget.input_budget):
            optimized_context = ExtractiveCompressor(self.model).compress(original_context, query=task, max_tokens=context_budget)
            methods.append(f"{self.profile.name}_extractive_compression")

        prompt = self._build_prompt(task, optimized_context, instructions, output, role)
        methods.append("compact_format")
        if not self.counter.fits(prompt, self.budget.input_budget):
            prompt = self.counter.trim(prompt, self.budget.input_budget)
            methods.append("trim")
            truncation_notes.append("Prompt was trimmed to fit the configured input budget.")

        optimized_tokens = self.counter.count(prompt)
        cost_before = None
        cost_after = None
        if self.provider:
            try:
                cost = CostEstimator(self.provider, self.model).estimate(original_tokens, optimized_tokens, self.max_output_tokens)
                cost_before = cost.original_cost_usd
                cost_after = cost.optimized_cost_usd
            except ValueError as exc:
                warnings.append(str(exc))
        report = UsageReport(
            model=self.model,
            input_tokens_before=original_tokens,
            input_tokens_after=optimized_tokens,
            output_tokens_limit=self.max_output_tokens,
            estimated_cost_before=cost_before,
            estimated_cost_after=cost_after,
            methods=list(dict.fromkeys(methods)),
            warnings=warnings,
            truncation_notes=truncation_notes,
        )
        return OptimizedPrompt(text=prompt, report=report)

    def _build_prompt(
        self,
        task: str,
        context: str,
        instructions: Iterable[str] | None,
        output: Iterable[str] | str | None,
        role: str | None,
    ) -> str:
        builder = PromptBuilder()
        if role:
            builder.role(role)
        builder.task(task)
        if instructions:
            builder.instructions(instructions)
        if context:
            builder.context(context)
        if output:
            builder.output(output)
        return builder.build()

    def _stringify_context(self, context: str | Sequence[str] | dict[str, Any] | list[Any]) -> str:
        if isinstance(context, str):
            return context
        if isinstance(context, dict):
            return compact_json(context)
        if isinstance(context, list) and (not context or not all(isinstance(item, str) for item in context)):
            return compact_json(context)
        if isinstance(context, Sequence):
            return "\n\n".join(str(item) for item in context)
        return str(context)
