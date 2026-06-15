from contpress import CacheAwarePrompt, ContextPress, CostEstimator, PromptDiff, cache_layout_report
from contpress.cache import ExactPromptCache


def test_exact_prompt_cache_disk_roundtrip(tmp_path):
    cache = ExactPromptCache(path=str(tmp_path), namespace="test")
    key = cache.make_key(model="gpt-4o-mini", prompt="hello", temperature=0)

    assert cache.get(key) is None
    cache.set(key, {"answer": "world"})

    assert cache.get(key) == {"answer": "world"}
    assert cache.stats().entries == 1
    assert cache.clear() >= 1


def test_cost_estimator_reports_savings():
    report = CostEstimator("openai", "gpt-4o-mini").estimate(12_000, 3_500, 500)

    assert report.saved_usd > 0
    assert report.saving_percent > 0


def test_cache_aware_prompt_report():
    prompt = CacheAwarePrompt(stable=["system rules"], dynamic=["user request"])
    text = prompt.build()
    report = prompt.report()

    assert "[stable prefix]" in text
    assert report.stable_tokens > 0


def test_cache_layout_report_detects_timestamp_in_stable_prefix():
    report = cache_layout_report("[stable prefix]\ntimestamp 2026-01-01\n\n[dynamic tail]\nquestion")

    assert not report.cache_friendly


def test_prompt_diff_reports_preserved_numbers():
    diff = PromptDiff.compare("ID A-123 must be preserved. Extra context.", "ID A-123 must be preserved.")

    assert "numbers" in diff.preserved
    assert "Prompt Diff" in diff.to_markdown()


def test_contextpress_report_is_dict_like():
    optimized = ContextPress(max_input_tokens=20, compression_profile="safe").optimize(
        task="Summarise",
        context="ID A-123 must be preserved. " * 20,
    )

    assert optimized.report["optimized_tokens"] <= optimized.report["original_tokens"]
    assert "ContextPress Report" in optimized.report.to_markdown()
