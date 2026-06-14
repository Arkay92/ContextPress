from contextpress import ContextFilter, ExtractiveCompressor


def test_extractive_compressor_prefers_relevant_sentences():
    text = "Cats sleep. Token usage must be reduced by filtering context. Bananas are yellow."
    result = ExtractiveCompressor().compress(text, query="reduce token usage", max_tokens=12)

    assert "Token usage" in result


def test_context_filter_keeps_relevant_chunks():
    chunks = ["Unrelated weather notes.", "Reduce LLM token usage with compact formatting and trimming."]
    result = ContextFilter().filter("token usage", chunks, max_tokens=20)

    assert "token usage" in result.lower()
