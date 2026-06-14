from __future__ import annotations

from contpress.tokenizer import TokenCounter


def chunk_text(text: str, max_tokens: int = 500, model: str = "gpt-4o-mini") -> list[str]:
    counter = TokenCounter(model)
    paragraphs = [part.strip() for part in (text or "").split("\n\n") if part.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0
    for paragraph in paragraphs:
        tokens = counter.count(paragraph)
        if current and current_tokens + tokens > max_tokens:
            chunks.append("\n\n".join(current))
            current = []
            current_tokens = 0
        if tokens > max_tokens:
            chunks.append(counter.trim(paragraph, max_tokens))
        else:
            current.append(paragraph)
            current_tokens += tokens
    if current:
        chunks.append("\n\n".join(current))
    return chunks
