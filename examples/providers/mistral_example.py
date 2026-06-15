from contpress import ContextPress

cp = ContextPress(model="mistral-small-latest", max_input_tokens=4000)
optimized = cp.optimize(task="Find action items.", context="...")

# client.chat.complete(model="mistral-small-latest", messages=[{"role": "user", "content": optimized.text}])
print(optimized.text)
