from __future__ import annotations

from contpress import ContextFilter, ContextPress


def main() -> None:
    question = "Which account IDs had failed payments and what actions are required?"
    chunks = [
        "Marketing notes for next quarter.",
        "Account A-104 had failed payment ERR_CARD_DECLINED. Retry required.",
        "Account B-222 opened a normal support ticket with no payment issue.",
        "Account C-981 had failed payment ERR_BANK_TIMEOUT. Manual review required.",
    ]

    filtered = ContextFilter(model="gpt-4o-mini").filter(
        query=question,
        chunks=chunks,
        max_tokens=500,
    )

    optimized = ContextPress(model="gpt-4o-mini", max_input_tokens=1_000).optimize(
        task=question,
        context=filtered,
        instructions=["Return account IDs, errors, and next actions only."],
    )

    print(optimized.text)
    print(optimized.report)


if __name__ == "__main__":
    main()
