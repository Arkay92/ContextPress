from pathlib import Path

from contpress import benchmark_path, doctor_prompt, estimate_cost


def test_estimate_cost_known_model():
    estimate = estimate_cost("openai", "gpt-4o-mini", input_tokens=1_000, output_tokens=500)

    assert estimate.total_cost_usd > 0
    assert estimate.as_dict()["provider"] == "openai"


def test_doctor_prompt_flags_over_budget():
    report = doctor_prompt("one two three four five", budget=2)

    assert not report.ok
    assert report.findings[0].code == "OVER_BUDGET"


def test_benchmark_path_summarizes_text_files(tmp_path: Path):
    (tmp_path / "one.txt").write_text("Token usage should be reduced. Keep IDs and risks.", encoding="utf-8")
    (tmp_path / "two.md").write_text("Support log error ID 123. Action required.", encoding="utf-8")

    result = benchmark_path(str(tmp_path), max_input_tokens=20)

    assert result.files == 2
    assert result.average_original_tokens >= result.average_optimized_tokens
