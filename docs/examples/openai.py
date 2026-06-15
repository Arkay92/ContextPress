from __future__ import annotations

from contpress import ContextPress


def main() -> None:
    cp = ContextPress(model="gpt-4o-mini", max_input_tokens=4_000, max_output_tokens=500)

    optimized = cp.optimize(
        task="Summarise this support log.",
        context="Paste or load your support log here.",
        instructions=["Keep only actions, errors, IDs, and risks."],
    )

    # from openai import OpenAI
    # client = OpenAI()
    # response = client.responses.create(
    #     model="gpt-4o-mini",
    #     input=optimized.text,
    #     max_output_tokens=500,
    # )
    # print(response.output_text)

    print(optimized.text)
    print(optimized.report)


if __name__ == "__main__":
    main()
