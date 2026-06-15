from contpress import ContextPress

cp = ContextPress(model="gpt-4o-mini", max_input_tokens=4000)
optimized = cp.optimize(task="Summarise this support log.", context="...")

# client.responses.create(model="gpt-4o-mini", input=optimized.text)
print(optimized.report.to_markdown())
