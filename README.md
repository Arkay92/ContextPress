# contextpress

A practical Python toolkit for making every LLM token count.

`contextpress` is a preflight optimizer for LLM prompts. It helps developers reduce token usage before a request is sent by combining counting, budget enforcement, compact formatting, prompt compression, context filtering, caching, and reporting.

## Install

```bash
pip install contextpress
```

Optional extras:

```bash
pip install "contextpress[compress]"
pip install "contextpress[semantic]"
pip install "contextpress[rag]"
pip install "contextpress[all]"
```

The base package stays light: `tiktoken`, `pydantic`, and `rich`. Heavier integrations such as LLMLingua, embeddings, FAISS, LangChain, and LlamaIndex are optional.

## Quickstart

```python
from contextpress import ContextPress

cp = ContextPress(
    model="gpt-4o-mini",
    max_input_tokens=4000,
    max_output_tokens=500,
)

optimized = cp.optimize(
    task="Answer the user's question using the provided context.",
    context=long_context,
    instructions=[
        "Be concise.",
        "Use only relevant facts.",
        "Return risks if uncertain.",
    ],
)

print(optimized.text)
print(optimized.report)
```

Example report:

```python
{
    "original_tokens": 9820,
    "optimized_tokens": 3120,
    "saved_tokens": 6700,
    "compression_ratio": 0.317,
    "methods": ["sentence_filter", "compact_format", "trim"],
}
```

## Core API

```python
from contextpress import TokenCounter

counter = TokenCounter(model="gpt-4o-mini")
counter.count("hello world")
counter.fits("long text", budget=8000)
counter.trim("long text", max_tokens=1000)
```

```python
from contextpress import TokenBudget

budget = TokenBudget(
    model="gpt-4o-mini",
    max_input_tokens=8000,
    reserve_output_tokens=1000,
)

usable = budget.input_budget
```

```python
from contextpress import PromptBuilder

prompt = (
    PromptBuilder()
    .role("senior Python engineer")
    .task("Refactor this code")
    .constraints(["Preserve behaviour", "No new dependencies", "Keep diff small"])
    .context(code)
    .output(["patch", "risk notes", "test plan"])
    .build()
)
```

```python
from contextpress import compact_json, compact_table, drop_nulls, shorten_keys

compact_json({"description": "Fix bug", "priority": "high"})
drop_nulls({"a": 1, "b": None})
shorten_keys({"description": "Fix bug"}, {"description": "d"})
compact_table([{"file": "app.py", "risk": "low"}])
```

```python
from contextpress import ExtractiveCompressor

compressor = ExtractiveCompressor()
short = compressor.compress(
    text=long_context,
    query="How do I reduce LLM token usage?",
    max_tokens=1200,
)
```

```python
from contextpress import ContextFilter

filterer = ContextFilter(model="gpt-4o-mini")
compressed_context = filterer.filter(
    query=user_question,
    chunks=retrieved_chunks,
    max_tokens=2500,
)
```

```python
from contextpress import ConversationPruner

messages = ConversationPruner().prune(
    messages=chat_history,
    current_query="What changed in the latest code?",
    max_tokens=3000,
)
```

```python
from contextpress import OutputContract, PromptCacheLayout, ToolSchemaCompactor

contract = OutputContract(
    fields={"risks": "short list of risks", "summary": "one sentence"},
).prompt()

layout = (
    PromptCacheLayout()
    .stable("System", "You are a concise assistant.")
    .volatile("User", "Current user request")
    .build()
)

compact_schema = ToolSchemaCompactor(drop_descriptions=True).compact(tool_schema)
```

## Optional APIs

```python
from contextpress.compressors import LLMLinguaCompressor

compressor = LLMLinguaCompressor()
compressed = compressor.compress(
    prompt=long_prompt,
    instruction="Preserve code, numbers, entities, requirements, and constraints.",
    target_tokens=1000,
)
```

Install with `pip install "contextpress[compress]"`.

Prompt compression can harm exact reasoning, code, legal wording, medical text, or maths. It is also not always a free speedup; preprocessing overhead can outweigh gains for shorter prompts or mismatched model and hardware conditions.

## CLI

```bash
contextpress count README.md --model gpt-4o-mini
contextpress trim prompt.txt --max-tokens 2000
contextpress compress prompt.txt --target-tokens 1000
contextpress compact data.json
contextpress report prompt.txt --budget 8000
```

## Publishing

GitHub Actions includes:

- `CI`: runs tests and builds the package on pushes and pull requests.
- `Publish to PyPI`: builds and publishes distributions when a GitHub release is published, or when run manually.

The publish workflow uses PyPI trusted publishing. Configure the PyPI project with this GitHub repository, the `pypi` environment, and the `.github/workflows/publish.yml` workflow before publishing a release.

## Included Features

- Token counting and trimming
- Token budget enforcement
- Compact prompt building
- Compact JSON, CSV, and table formatting helpers
- Dependency-free extractive prompt compression
- Keyword and sentence RAG context filtering
- Exact prompt cache
- Optional LLMLingua wrapper
- Optional semantic cache placeholder with explicit extra install guidance
- Conversation memory pruning
- Output contract generation
- Prompt cache-aware prompt layout
- Tool schema and agent trace compaction
- Compression reports and before/after diffs
- Usage and savings reporting
- CLI for counting, trimming, compacting, compressing, and reporting
