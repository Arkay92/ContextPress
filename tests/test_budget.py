from contpress import TokenBudget


def test_budget_reserves_output_and_overhead():
    budget = TokenBudget(max_input_tokens=100, reserve_output_tokens=10, system_prompt="system")

    assert 0 < budget.input_budget < 100
    assert budget.rag_context_budget <= budget.input_budget
    assert budget.conversation_history_budget <= budget.input_budget
