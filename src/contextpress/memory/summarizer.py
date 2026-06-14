from __future__ import annotations


class Summarizer:
    def summarize(self, text: str, max_sentences: int = 5) -> str:
        sentences = [part.strip() for part in text.replace("\n", " ").split(".") if part.strip()]
        return ". ".join(sentences[:max_sentences]) + ("." if sentences else "")
