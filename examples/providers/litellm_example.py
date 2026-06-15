from contpress import ContextPress

cp = ContextPress(model="gpt-4o-mini", max_input_tokens=4000)
optimized = cp.optimize(task="Answer using this context.", context="...")

# completion(model="openai/gpt-4o-mini", messages=[{"role": "user", "content": optimized.text}])
print(optimized.report.to_json())
