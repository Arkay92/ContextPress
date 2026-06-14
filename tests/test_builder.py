from contpress import PromptBuilder


def test_prompt_builder_outputs_compact_blocks():
    prompt = (
        PromptBuilder()
        .role("senior Python engineer")
        .task("Refactor this code")
        .constraints(["Preserve behaviour", "No new dependencies"])
        .context("print('hi')")
        .output(["patch", "risk notes"])
        .build()
    )

    assert "Role: senior Python engineer" in prompt
    assert "Constraints:\n- Preserve behaviour\n- No new dependencies" in prompt
    assert "Output:\n- patch\n- risk notes" in prompt
