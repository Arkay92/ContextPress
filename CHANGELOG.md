# Changelog

## 0.4.0

### Added

- Disk-backed exact prompt cache with TTL, namespaces, hit/miss stats, list, and clear.
- Optional semantic cache with sentence-transformers, FAISS, metadata filtering, TTL, and score reporting.
- Cost estimation engine with bundled provider/model pricing registry and custom override support.
- Cache-aware prompt layout helper with stable/dynamic token reporting.
- Enhanced usage reports with markdown, JSON, cost fields, cache status, warnings, and truncation notes.
- CLI cache commands, semantic-cache commands, pricing list, cost, cache-layout, diff, and doctor health checks.
- Prompt diff report with removed/preserved categories.
- Compression profiles: safe, balanced, aggressive, code, rag, and legal.
- Provider examples for OpenAI, Anthropic, Ollama, LiteLLM, Groq, and Mistral.
- Benchmark sample prompts and expanded benchmark output.
- Documentation pages for quickstart, CLI, caching, semantic cache, cost estimation, prompt cache layout, compression profiles, providers, and benchmarks.

### Changed

- `ContextPress.optimize()` now returns a richer `UsageReport` object that remains dict-like for compatibility.
- Budget handling now records truncation notes and compression-profile warnings.

### Fixed

- More explicit optional-extra errors for semantic cache usage.
- Safer report rendering for empty or unpriced prompts.

## 0.3.0

- Added `contpress benchmark` for measuring average token reduction over files or folders.
- Added `contpress diff` to inspect what changed after optimization.
- Added `contpress doctor` for prompt budget and compression-risk checks.
- Added `contpress estimate-cost` for provider/model cost estimates.
- Added provider examples under `docs/examples/`.
- Updated README with package-name guidance, before/after demo, provider usage, and benchmark example.

## 0.2.1

- Completed the rename to the `contpress` import package and PyPI project.

## 0.2.0

- Added clean build handling in the publish workflow.
- Updated publishing documentation.

## 0.1.0

- Initial lightweight package with token counting, budgets, prompt building, formatting, extractive compression, context filtering, cache surfaces, reports, and CLI basics.
