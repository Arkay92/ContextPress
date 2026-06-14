from contextpress import TokenCounter


def test_token_counter_counts_and_trims():
    counter = TokenCounter()

    assert counter.count("hello world") >= 2
    assert counter.fits("hello world", budget=10)
    assert counter.trim("one two three", max_tokens=2)
