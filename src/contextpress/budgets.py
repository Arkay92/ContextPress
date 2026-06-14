from __future__ import annotations

from dataclasses import dataclass

from contextpress.tokenizer import TokenCounter


MODEL_CONTEXT_WINDOWS = {
    "gpt-4o": 128_000,
    "gpt-4o-mini": 128_000,
    "gpt-4.1": 1_047_576,
    "gpt-4.1-mini": 1_047_576,
    "gpt-4.1-nano": 1_047_576,
    "o3": 200_000,
    "o4-mini": 200_000,
}


@dataclass(slots=True)
class TokenBudget:
    model: str = "gpt-4o-mini"
    max_input_tokens: int | None = None
    reserve_output_tokens: int = 0
    system_prompt: str = ""
    tool_schema: str = ""
    rag_context_ratio: float = 0.6
    history_ratio: float = 0.3

    def __post_init__(self) -> None:
        if self.reserve_output_tokens < 0:
            raise ValueError("reserve_output_tokens must be >= 0")
        if self.max_input_tokens is not None and self.max_input_tokens < 0:
            raise ValueError("max_input_tokens must be >= 0")
        if not 0 <= self.rag_context_ratio <= 1:
            raise ValueError("rag_context_ratio must be between 0 and 1")
        if not 0 <= self.history_ratio <= 1:
            raise ValueError("history_ratio must be between 0 and 1")
        self.counter = TokenCounter(self.model)

    @property
    def context_window(self) -> int:
        return MODEL_CONTEXT_WINDOWS.get(self.model, 128_000)

    @property
    def overhead_tokens(self) -> int:
        return self.counter.count(self.system_prompt) + self.counter.count(self.tool_schema)

    @property
    def input_budget(self) -> int:
        ceiling = self.max_input_tokens if self.max_input_tokens is not None else self.context_window
        return max(0, ceiling - self.reserve_output_tokens - self.overhead_tokens)

    @property
    def rag_context_budget(self) -> int:
        return int(self.input_budget * self.rag_context_ratio)

    @property
    def conversation_history_budget(self) -> int:
        return int(self.input_budget * self.history_ratio)

    def enforce(self, text: str) -> str:
        return self.counter.trim(text, self.input_budget)
