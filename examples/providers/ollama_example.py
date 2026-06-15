from contpress import ContextPress

cp = ContextPress(model="llama3.1", max_input_tokens=4000)
optimized = cp.optimize(task="Summarise locally.", context="...")

# ollama.chat(model="llama3.1", messages=[{"role": "user", "content": optimized.text}])
print(optimized.text)
