from contpress import ContextPress

cp = ContextPress(model="llama-3.1-8b-instant", max_input_tokens=4000)
optimized = cp.optimize(task="Summarise this incident.", context="...")

# client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": optimized.text}])
print(optimized.text)
