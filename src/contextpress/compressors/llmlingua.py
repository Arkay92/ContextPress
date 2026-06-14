from __future__ import annotations


class LLMLinguaCompressor:
    def __init__(self, *args, **kwargs) -> None:
        try:
            from llmlingua import PromptCompressor
        except ImportError as exc:
            raise ImportError("Install with: pip install contpress[compress]") from exc
        self._compressor = PromptCompressor(*args, **kwargs)

    def compress(
        self,
        prompt: str | None = None,
        instruction: str = "Preserve code, numbers, entities, requirements, and constraints.",
        target_tokens: int = 1_000,
        **kwargs,
    ) -> str:
        source = prompt if prompt is not None else kwargs.pop("text", "")
        result = self._compressor.compress_prompt(
            source,
            instruction=instruction,
            target_token=target_tokens,
            **kwargs,
        )
        if isinstance(result, dict):
            return result.get("compressed_prompt", "")
        return str(result)
