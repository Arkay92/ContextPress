# ContextPress

<p align="center">
  A practical Python toolkit for making every LLM token count.
</p>

<p align="center">
  <img width="256" height="256" alt="contpress Logo" src="https://raw.githubusercontent.com/Arkay92/ContextPress/refs/heads/main/contextpress.png" />
</p>

<p align="center">
  <a href="https://github.com/Arkay92/ContextPress/actions/workflows/publish.yml"><img alt="Publish" src="https://github.com/Arkay92/ContextPress/actions/workflows/publish.yml/badge.svg" /></a>
  <a href="https://pypi.org/project/contpress/"><img alt="PyPI" src="https://img.shields.io/pypi/v/contpress.svg" /></a>
  <img alt="Python" src="https://img.shields.io/pypi/pyversions/contpress.svg" />
  <img alt="Downloads" src="https://img.shields.io/pypi/dm/contpress.svg" />
  <img alt="License" src="https://img.shields.io/pypi/l/contpress.svg" />
</p>

> **Package name:** `contpress`  
> **Project name:** ContextPress  
> **Install:** `pip install contpress`  
> **Import:** `from contpress import ContextPress`

**ContextPress** combines:

- **Token counting and trimming** with model-aware encodings.
- **Exact and semantic caching** to reduce repeated model calls.
- **Provider-aware cost estimation** with bundled pricing estimates.
- **Token budget enforcement** for input, output reserve, system prompts, tools, RAG context, and history.
- **Compact prompt building** for consistent, low-waste prompt blocks.
- **Dependency-free extractive compression** for safe first-pass prompt reduction.
- **Compression profiles** for safe, balanced, aggressive, code, RAG, and legal prompts.
- **RAG context filtering** with keyword and sentence relevance modes.
- **Compact JSON, CSV, and table formatting** for reducing structured-data tokens.
- **Conversation memory pruning** that keeps system prompts, recent messages, decisions, constraints, and relevant context.
- **Output contract generation** for concise response schemas.
- **Prompt cache-aware formatting** to keep stable prompt blocks grouped.
- **Enhanced usage reports** with token savings, estimated cost savings, cache status, warnings, and truncation notes.
- **Optional dependencies** so the base package stays lightweight.

---

## Before / After

```python
from contpress import ContextPress

cp = ContextPress(model="gpt-4o-mini", max_input_tokens=4000)

optimized = cp.optimize(
    task="Summarise this support log.",
    context=long_log,
    instructions=["Keep only actions, errors, IDs, and risks."],
)

print(optimized.report)
```

Example output:

```text
Original: 9,842 tokens
Optimized: 2,914 tokens
Saved: 6,928 tokens
Reduction: 70.4%
Methods: compact_layout, extractive_compression, budget_trim
```

That is the core job: shrink the prompt before the model call, while reporting
what changed.

ContextPress v0.4.0 also helps reduce repeated model calls through exact and
semantic caching, and estimate savings with provider-aware pricing.

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

`ContextPress` is designed to reduce token usage before a request is sent:

- **Oversized prompts** from untrimmed documents, code, logs, and retrieved chunks.
- **Messy repeated instructions** that waste tokens and reduce prompt clarity.
- **Verbose structured data** where compact JSON or tables are enough.
- **RAG context bloat** from chunks that are only loosely related to the query.
- **Long conversation histories** with filler, confirmations, and stale context.
- **Unclear output budgets** where responses are allowed to grow without a contract.

---

## Why Not Just Use LLMLingua?

LLMLingua compresses prompts. ContextPress manages the full preflight pipeline:
counting, budgets, compact formatting, context filtering, compression, memory
pruning, output contracts, cache-aware layout, and reporting.

That makes ContextPress a practical token-optimization toolkit, not a wrapper
around one compressor.

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
pip install contpress
```

For LLMLingua prompt compression:

```bash
pip install "contpress[compress]"
```

For semantic cache support:

```bash
pip install "contpress[semantic]"
```

For RAG ecosystem integrations:

```bash
pip install "contpress[rag]"
```

For all optional integrations:

```bash
pip install "contpress[all]"
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
from contpress import ContextPress

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

### Use Before Any Provider Call

ContextPress runs before the LLM request, so it works with any provider client.

```python
# OpenAI
optimized = cp.optimize(...)

client.responses.create(
    model="gpt-4o-mini",
    input=optimized.text,
    max_output_tokens=500,
)
```

```python
# Anthropic
optimized = cp.optimize(...)

client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=500,
    messages=[{"role": "user", "content": optimized.text}],
)
```

```python
# Ollama
optimized = cp.optimize(...)

ollama.chat(
    model="llama3.1",
    messages=[{"role": "user", "content": optimized.text}],
)
```

```python
# LiteLLM
optimized = cp.optimize(...)

completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": optimized.text}],
    max_tokens=500,
)
```

### Token Counting

```python
from contpress import TokenCounter

counter = TokenCounter(model="gpt-4o-mini")

print(counter.count("hello world"))
print(counter.fits("long text", budget=8000))
print(counter.trim("long text", max_tokens=1000))
```

### Usage Report

```python
from contpress import UsageReport

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
contpress count README.md --model gpt-4o-mini
```

Trim a file to a maximum token count:

```bash
contpress trim prompt.txt --max-tokens 2000
```

Compress a prompt:

```bash
contpress compress prompt.txt --target-tokens 1000
```

Compact JSON:

```bash
contpress compact data.json
```

Generate a budget report:

```bash
contpress report prompt.txt --budget 8000
```

Estimate before/after cost:

```bash
contpress cost before.txt after.txt --provider openai --model gpt-4o-mini --output-tokens 500
contpress pricing list
```

Manage exact cache:

```bash
contpress cache stats
contpress cache list
contpress cache clear
```

Use semantic cache:

```bash
contpress semantic-cache add question.txt answer.txt --provider openai --model gpt-4o-mini
contpress semantic-cache lookup "How do I reduce tokens?"
```

Show what optimization removed or changed:

```bash
contpress diff prompt.txt --target-tokens 1000
```

Run a small benchmark over prompt files:

```bash
contpress benchmark examples/
```

Check a prompt for budget and compression risks:

```bash
contpress doctor prompt.txt --budget 8000
```

Check install health:

```bash
contpress doctor
```

Estimate provider/model cost:

```bash
contpress estimate-cost prompt.txt --provider openai --model gpt-4o-mini --output-tokens 500
```

Inspect prompt cache layout:

```bash
contpress cache-layout prompt.txt
```

---

## Benchmark Example

A small practical benchmark is enough to make savings visible:

```text
Dataset: 20 synthetic support prompts
Average original tokens: 5,430
Average optimized tokens: 1,920
Average reduction: 64.6%
Answer quality: manually checked / unchanged for key facts
```

The current package focuses on practical preflight savings rather than academic
compression scores. Add your own dataset, run the same prompt before and after
optimization, and compare the report plus final answer quality.

---

## Main Features

### 1. **Token Counting**

Count, fit-check, and trim text using the target model encoding:

```python
from contpress import TokenCounter

counter = TokenCounter(model="gpt-4o-mini")
tokens = counter.count(prompt)
```

### 2. **Budget Enforcement**

Reserve output tokens and account for system prompt or tool schema overhead:

```python
from contpress import TokenBudget

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
from contpress import PromptBuilder

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
from contpress import compact_json, compact_table, drop_nulls, shorten_keys

payload = drop_nulls(data)
payload = shorten_keys(payload, {"description": "d", "priority": "p"})
text = compact_json(payload)
```

### 5. **Extractive Compression**

Dependency-free compression keeps query-relevant sentences and preserves useful
signals such as numbers, URLs, headings, code identifiers, and requirements:

```python
from contpress import ExtractiveCompressor

short = ExtractiveCompressor().compress(
    text=long_context,
    query="How do I reduce LLM token usage?",
    max_tokens=1200,
)
```

### 6. **LLMLingua Compression**

Use Microsoft LLMLingua when you install the compression extra:

```python
from contpress.compressors import LLMLinguaCompressor

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
from contpress import ContextFilter

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
from contpress import ConversationPruner

messages = ConversationPruner().prune(
    messages=chat_history,
    current_query="What changed in the latest code?",
    max_tokens=3000,
)
```

### 9. **Output Contracts**

Generate compact response contracts:

```python
from contpress import OutputContract

contract = OutputContract(
    fields={"summary": "one sentence", "risks": "short list"},
).prompt()
```

### 10. **Prompt Cache Layout**

Group stable and volatile blocks to improve prompt-cache friendliness:

```python
from contpress import PromptCacheLayout

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
from contpress import AgentTraceCompactor, ToolSchemaCompactor

compact_schema = ToolSchemaCompactor(drop_descriptions=True).compact(tool_schema)
compact_trace = AgentTraceCompactor().compact(events)
```

### 12. **Caching and Cost Control**

```python
from contpress.cache import ExactPromptCache
from contpress import CostEstimator

cache = ExactPromptCache(path=".contpress-cache", ttl_seconds=86400)
key = cache.make_key(model="gpt-4o-mini", prompt=prompt, temperature=0)
cached = cache.get(key)

report = CostEstimator("openai", "gpt-4o-mini").estimate(
    input_tokens_before=12000,
    input_tokens_after=3500,
    output_tokens=500,
)
```

### 13. **Prompt Diff and Cache Layout**

```python
from contpress import CacheAwarePrompt, PromptDiff

prompt = CacheAwarePrompt(
    stable=["system rules", "tool schema"],
    dynamic=["current request", "retrieved context"],
).build()

diff = PromptDiff.compare(original, optimized)
print(diff.to_markdown())
```

---

## Configuration

Tune prompt budgets with `TokenBudget`:

```python
from contpress import TokenBudget

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
from contpress import ContextPress

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
from contpress import ContextPress

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
contpress count README.md
contpress report prompt.txt --budget 8000
```

---

## Project Structure

```text
src/contpress/
  __init__.py              # Public API
  benchmark.py             # Folder/file benchmark helpers
  core.py                  # ContextPress and OptimizedPrompt
  costs.py                 # Provider/model cost estimates
  diff.py                  # Prompt diff reports
  doctor.py                # Prompt budget and risk checks
  profiles.py              # Compression profiles
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
  pricing/
    models.json            # Bundled provider/model pricing estimates
tests/
  test_*.py                # Unit tests
docs/
  examples/
    openai.py              # OpenAI preflight optimization example
    rag_filter.py          # RAG context filtering example
.github/
  workflows/
    ci.yml                 # Tests and package build
    publish.yml            # PyPI publishing workflow
CHANGELOG.md               # Release history
pyproject.toml             # Project metadata and dependencies
examples/                  # Provider examples and benchmark prompts
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

## License

MIT

---

## Contributing

Contributions are welcome. Open an issue with the model, prompt shape, expected
budget, and the optimization behavior you expected.

---

## Citation

If you use ContextPress in research, please cite:

```bibtex
@software{ContextPress2026,
  title={ContextPress: A Practical Python Toolkit for Making Every LLM Token Count},
  author={Arkay92},
  url={https://github.com/Arkay92/ContextPress},
  year={2026},
  version={0.4.0},
}
```

---

## Acknowledgments

- [tiktoken](https://github.com/openai/tiktoken) for fast model-aware tokenization.
- [LLMLingua](https://github.com/microsoft/LLMLingua) for optional prompt compression.
- [LangChain](https://www.langchain.com/) and [LlamaIndex](https://www.llamaindex.ai/) for RAG compression patterns.
- [FAISS](https://github.com/facebookresearch/faiss) and [sentence-transformers](https://www.sbert.net/) for semantic cache building blocks.
