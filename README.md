# contextpress

<p align="center">
  A practical Python toolkit for making every LLM token count.
</p>

<p align="center">
  <img width="256" height="256" alt="contextpress Logo" src="https://github.com/Arkay92/ContextPress/blob/main/contextpress.png?raw=true" />
</p>

<p align="center">
  <a href="https://github.com/Arkay92/ContextPress/actions/workflows/publish.yml"><img alt="Publish" src="https://github.com/Arkay92/ContextPress/actions/workflows/publish.yml/badge.svg" /></a>
  <a href="https://pypi.org/project/contextpress/"><img alt="PyPI" src="https://img.shields.io/pypi/v/contextpress.svg" /></a>
  <img alt="Python" src="https://img.shields.io/pypi/pyversions/contextpress.svg" />
  <img alt="Downloads" src="https://img.shields.io/pypi/dm/contextpress.svg" />
  <img alt="License" src="https://img.shields.io/pypi/l/contextpress.svg" />
</p>

**contextpress** combines:

- **Token counting and trimming** with model-aware encodings.
- **Token budget enforcement** for input, output reserve, system prompts, tools, RAG context, and history.
- **Compact prompt building** for consistent, low-waste prompt blocks.
- **Dependency-free extractive compression** for safe first-pass prompt reduction.
- **RAG context filtering** with keyword and sentence relevance modes.
- **Compact JSON, CSV, and table formatting** for reducing structured-data tokens.
- **Conversation memory pruning** that keeps system prompts, recent messages, decisions, constraints, and relevant context.
- **Output contract generation** for concise response schemas.
- **Prompt cache-aware formatting** to keep stable prompt blocks grouped.
- **Prompt and response caching surfaces** including exact cache and optional semantic cache support.
- **Usage reports** with original tokens, optimized tokens, saved tokens, ratios, and methods.
- **Optional dependencies** so the base package stays lightweight.

---

## Why Preflight Optimization for LLM Prompts?

LLM prompts often grow through repeated instructions, irrelevant retrieved chunks,
verbose JSON, oversized chat history, and unbounded output requests:

```text
Task, instructions, context, tools, and history
  -> Count tokens against the target model
  -> Reserve output budget
  -> Format prompt blocks compactly
  -> Filter retrieved context
  -> Compress or trim only when needed

  -> Return optimized text
  -> Report savings and methods
  -> Feed the result to any LLM client
```

`contextpress` is designed to reduce token usage before a request is sent:

- **Oversized prompts** from untrimmed documents, code, logs, and retrieved chunks.
- **Messy repeated instructions** that waste tokens and reduce prompt clarity.
- **Verbose structured data** where compact JSON or tables are enough.
- **RAG context bloat** from chunks that are only loosely related to the query.
- **Long conversation histories** with filler, confirmations, and stale context.
- **Unclear output budgets** where responses are allowed to grow without a contract.

---

## Architecture

```text
Prompt inputs
  - task
  - instructions
  - context
  - conversation history
  - output contract
    |
    v
Preflight optimization
  - token counting
  - budget enforcement
  - compact prompt layout
  - extractive compression
  - RAG context filtering
  - compact JSON / CSV / table formatting
  - memory pruning
    |
    v
OptimizedPrompt
  - text
  - report dict
  - original token count
  - optimized token count
  - saved tokens
  - methods used
```

---

## Install

```bash
pip install contextpress
```

For LLMLingua prompt compression:

```bash
pip install "contextpress[compress]"
```

For semantic cache support:

```bash
pip install "contextpress[semantic]"
```

For RAG ecosystem integrations:

```bash
pip install "contextpress[rag]"
```

For all optional integrations:

```bash
pip install "contextpress[all]"
```

For development:

```bash
pip install -e ".[dev,all]"
pytest -q
python -m build
```

---

## Quick Start

### Optimize a Prompt

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

### Token Counting

```python
from contextpress import TokenCounter

counter = TokenCounter(model="gpt-4o-mini")

print(counter.count("hello world"))
print(counter.fits("long text", budget=8000))
print(counter.trim("long text", max_tokens=1000))
```

### Usage Report

```python
from contextpress import UsageReport

report = UsageReport(
    model="gpt-4o-mini",
    input_tokens_before=10200,
    input_tokens_after=3400,
    output_tokens_limit=500,
    methods=["sentence_filter", "compact_json", "trim"],
)

print(report.summary())
```

---

## CLI

Count tokens in a file:

```bash
contextpress count README.md --model gpt-4o-mini
```

Trim a file to a maximum token count:

```bash
contextpress trim prompt.txt --max-tokens 2000
```

Compress a prompt:

```bash
contextpress compress prompt.txt --target-tokens 1000
```

Compact JSON:

```bash
contextpress compact data.json
```

Generate a budget report:

```bash
contextpress report prompt.txt --budget 8000
```

---

## Main Features

### 1. **Token Counting**

Count, fit-check, and trim text using the target model encoding:

```python
from contextpress import TokenCounter

counter = TokenCounter(model="gpt-4o-mini")
tokens = counter.count(prompt)
```

### 2. **Budget Enforcement**

Reserve output tokens and account for system prompt or tool schema overhead:

```python
from contextpress import TokenBudget

budget = TokenBudget(
    model="gpt-4o-mini",
    max_input_tokens=8000,
    reserve_output_tokens=1000,
    system_prompt="You are concise.",
)

print(budget.input_budget)
```

### 3. **Compact Prompt Builder**

Build repeatable prompt blocks without verbose formatting:

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

### 4. **Compact Structured Data**

Reduce JSON and tabular context before sending it to an LLM:

```python
from contextpress import compact_json, compact_table, drop_nulls, shorten_keys

payload = drop_nulls(data)
payload = shorten_keys(payload, {"description": "d", "priority": "p"})
text = compact_json(payload)
```

### 5. **Extractive Compression**

Dependency-free compression keeps query-relevant sentences and preserves useful
signals such as numbers, URLs, headings, code identifiers, and requirements:

```python
from contextpress import ExtractiveCompressor

short = ExtractiveCompressor().compress(
    text=long_context,
    query="How do I reduce LLM token usage?",
    max_tokens=1200,
)
```

### 6. **LLMLingua Compression**

Use Microsoft LLMLingua when you install the compression extra:

```python
from contextpress.compressors import LLMLinguaCompressor

compressed = LLMLinguaCompressor().compress(
    prompt=long_prompt,
    instruction="Preserve code, numbers, entities, requirements, and constraints.",
    target_tokens=1000,
)
```

Prompt compression can harm exact reasoning, code, legal wording, medical text,
or maths. It is not always a free speedup; preprocessing overhead can outweigh
gains for shorter prompts or mismatched model and hardware conditions.

### 7. **RAG Context Filtering**

Filter retrieved chunks before building the final prompt:

```python
from contextpress import ContextFilter

filtered = ContextFilter(model="gpt-4o-mini").filter(
    query=user_question,
    chunks=retrieved_chunks,
    max_tokens=2500,
)
```

### 8. **Conversation Memory Pruning**

Keep system prompts, recent messages, relevant history, constraints, decisions,
preferences, and file names:

```python
from contextpress import ConversationPruner

messages = ConversationPruner().prune(
    messages=chat_history,
    current_query="What changed in the latest code?",
    max_tokens=3000,
)
```

### 9. **Output Contracts**

Generate compact response contracts:

```python
from contextpress import OutputContract

contract = OutputContract(
    fields={"summary": "one sentence", "risks": "short list"},
).prompt()
```

### 10. **Prompt Cache Layout**

Group stable and volatile blocks to improve prompt-cache friendliness:

```python
from contextpress import PromptCacheLayout

prompt = (
    PromptCacheLayout()
    .stable("System", "You are a concise assistant.")
    .stable("Rules", "Use only provided context.")
    .volatile("User", user_question)
    .build()
)
```

### 11. **Tool and Agent Trace Compaction**

Compact tool schemas and agent traces before placing them in context:

```python
from contextpress import AgentTraceCompactor, ToolSchemaCompactor

compact_schema = ToolSchemaCompactor(drop_descriptions=True).compact(tool_schema)
compact_trace = AgentTraceCompactor().compact(events)
```

---

## Configuration

Tune prompt budgets with `TokenBudget`:

```python
from contextpress import TokenBudget

budget = TokenBudget(
    model="gpt-4o-mini",
    max_input_tokens=8000,
    reserve_output_tokens=1000,
    system_prompt="You are concise.",
    tool_schema=compact_schema,
    rag_context_ratio=0.6,
    history_ratio=0.3,
)
```

Tune optimization with `ContextPress`:

```python
from contextpress import ContextPress

cp = ContextPress(
    model="gpt-4o-mini",
    max_input_tokens=6000,
    reserve_output_tokens=800,
    compression="extractive",
)
```

---

## Examples

```python
from contextpress import ContextPress

cp = ContextPress(
    model="gpt-4o-mini",
    max_input_tokens=6000,
    reserve_output_tokens=800,
)

optimized = cp.optimize(
    task="Summarise the key issues in this codebase.",
    context=repo_summary,
    instructions=[
        "Focus on bugs, security, maintainability, and performance.",
        "Do not repeat obvious file names.",
        "Return concise bullet points.",
    ],
)

print(optimized.report)
```

```bash
contextpress count README.md
contextpress report prompt.txt --budget 8000
```

---

## Project Structure

```text
src/contextpress/
  __init__.py              # Public API
  core.py                  # ContextPress and OptimizedPrompt
  tokenizer.py             # TokenCounter
  budgets.py               # TokenBudget
  builder.py               # PromptBuilder
  formatters.py            # Compact JSON, CSV, and table helpers
  reports.py               # UsageReport
  contracts.py             # OutputContract
  prompt_cache.py          # PromptCacheLayout
  tools.py                 # ToolSchemaCompactor and AgentTraceCompactor
  cli.py                   # Command-line interface
  py.typed                 # Typing marker
  compressors/             # Extractive, sentence, LLMLingua, reports, diffs
  rag/                     # Chunking, reranking, context filtering
  cache/                   # Exact cache, semantic cache surface, stores
  memory/                  # Conversation pruning and summarization
tests/
  test_*.py                # Unit tests
.github/
  workflows/
    ci.yml                 # Tests and package build
    publish.yml            # PyPI publishing workflow
pyproject.toml             # Project metadata and dependencies
contextpress.png           # Project logo
```

---

## Development

```bash
# Install with dev extras
pip install -e ".[dev,all]"

# Run tests
pytest -q

# Build package
python -m build
```

---

## Publishing

GitHub Actions includes:

- `CI`: runs tests and builds the package on pushes and pull requests.
- `Publish to PyPI`: builds, checks, and publishes distributions when a `v*` tag is pushed.

The publish workflow uses PyPI trusted publishing. Configure the PyPI project
with this GitHub repository, the `pypi` environment, and the
`.github/workflows/publish.yml` workflow before pushing a version tag.

Trusted publishing settings on PyPI must match:

- PyPI project name: `contextpress`
- GitHub owner: `Arkay92`
- GitHub repository: `ContextPress`
- Workflow name: `publish.yml`
- Environment name: `pypi`

---

## License

MIT

---

## Contributing

Contributions are welcome. Open an issue with the model, prompt shape, expected
budget, and the optimization behavior you expected.

---

## Citation

If you use contextpress in research, please cite:

```bibtex
@software{contextpress2026,
  title={contextpress: A Practical Python Toolkit for Making Every LLM Token Count},
  author={Arkay92},
  url={https://github.com/Arkay92/ContextPress},
  year={2026},
  version={v0.1.4},
}
```

---

## Acknowledgments

- [tiktoken](https://github.com/openai/tiktoken) for fast model-aware tokenization.
- [LLMLingua](https://github.com/microsoft/LLMLingua) for optional prompt compression.
- [LangChain](https://www.langchain.com/) and [LlamaIndex](https://www.llamaindex.ai/) for RAG compression patterns.
- [FAISS](https://github.com/facebookresearch/faiss) and [sentence-transformers](https://www.sbert.net/) for semantic cache building blocks.
