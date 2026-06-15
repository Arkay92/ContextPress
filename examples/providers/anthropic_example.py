from contpress import ContextPress

cp = ContextPress(model="claude-3-5-haiku", max_input_tokens=4000)
optimized = cp.optimize(task="Extract risks from this context.", context="...")

# client.messages.create(model="claude-3-5-haiku-latest", max_tokens=500, messages=[{"role": "user", "content": optimized.text}])
print(optimized.text)
