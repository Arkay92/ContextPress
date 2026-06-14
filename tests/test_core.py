from contextpress import ContextPress


def test_contextpress_optimizes_and_reports():
    cp = ContextPress(max_input_tokens=80, max_output_tokens=10)

    optimized = cp.optimize(
        task="Answer using token usage facts.",
        context=[
            "Unrelated text about cooking.",
            "Token usage can be reduced with trimming, filtering, and compact formatting.",
        ],
        instructions=["Be concise"],
    )

    assert "Task:" in optimized.text
    assert optimized.report["optimized_tokens"] <= optimized.report["original_tokens"]
    assert "methods" in optimized.report
