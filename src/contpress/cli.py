from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console

from contpress.benchmark import benchmark_path
from contpress.cache import ExactPromptCache, SemanticCache
from contpress.core import ContextPress
from contpress.costs import CostEstimator, PricingRegistry, estimate_cost
from contpress.diff import PromptDiff
from contpress.doctor import doctor_prompt, install_health
from contpress.formatters import compact_json
from contpress.prompt_cache import cache_layout_report
from contpress.reports import UsageReport
from contpress.tokenizer import TokenCounter


console = Console()


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="contpress")
    sub = parser.add_subparsers(dest="command", required=True)

    count = sub.add_parser("count")
    count.add_argument("file")
    count.add_argument("--model", default="gpt-4o-mini")
    count.add_argument("--budget", type=int, default=8_000)

    trim = sub.add_parser("trim")
    trim.add_argument("file")
    trim.add_argument("--model", default="gpt-4o-mini")
    trim.add_argument("--max-tokens", type=int, required=True)

    compress = sub.add_parser("compress")
    compress.add_argument("file")
    compress.add_argument("--model", default="gpt-4o-mini")
    compress.add_argument("--target-tokens", type=int, default=1_000)
    compress.add_argument("--task", default="")
    compress.add_argument("--profile", default="balanced")

    compact = sub.add_parser("compact")
    compact.add_argument("file")

    report = sub.add_parser("report")
    report.add_argument("file")
    report.add_argument("--model", default="gpt-4o-mini")
    report.add_argument("--budget", type=int, default=8_000)

    diff = sub.add_parser("diff")
    diff.add_argument("original")
    diff.add_argument("optimized", nargs="?")
    diff.add_argument("--model", default="gpt-4o-mini")
    diff.add_argument("--target-tokens", type=int, default=1_000)
    diff.add_argument("--task", default="Compress this prompt.")
    diff.add_argument("--profile", default="balanced")

    benchmark = sub.add_parser("benchmark")
    benchmark.add_argument("path")
    benchmark.add_argument("--model", default="gpt-4o-mini")
    benchmark.add_argument("--max-input-tokens", type=int, default=4_000)
    benchmark.add_argument("--task", default="Optimize this prompt.")
    benchmark.add_argument("--json", action="store_true")

    doctor = sub.add_parser("doctor")
    doctor.add_argument("file", nargs="?")
    doctor.add_argument("--model", default="gpt-4o-mini")
    doctor.add_argument("--budget", type=int, default=8_000)
    doctor.add_argument("--json", action="store_true")

    estimate = sub.add_parser("estimate-cost")
    estimate.add_argument("file", nargs="?")
    estimate.add_argument("--provider", required=True)
    estimate.add_argument("--model", required=True)
    estimate.add_argument("--input-tokens", type=int)
    estimate.add_argument("--output-tokens", type=int, default=0)
    estimate.add_argument("--json", action="store_true")

    cost = sub.add_parser("cost")
    cost.add_argument("before")
    cost.add_argument("after", nargs="?")
    cost.add_argument("--provider", required=True)
    cost.add_argument("--model", required=True)
    cost.add_argument("--output-tokens", type=int, default=0)
    cost.add_argument("--json", action="store_true")

    pricing = sub.add_parser("pricing")
    pricing_sub = pricing.add_subparsers(dest="pricing_command", required=True)
    pricing_sub.add_parser("list")

    cache = sub.add_parser("cache")
    cache.add_argument("--path", default=".contpress-cache")
    cache_sub = cache.add_subparsers(dest="cache_command", required=True)
    cache_sub.add_parser("stats")
    cache_sub.add_parser("clear")
    cache_sub.add_parser("list")

    semantic = sub.add_parser("semantic-cache")
    semantic.add_argument("--path", default=".contpress-semantic-cache")
    semantic.add_argument("--threshold", type=float, default=0.88)
    semantic_sub = semantic.add_subparsers(dest="semantic_command", required=True)
    semantic_add = semantic_sub.add_parser("add")
    semantic_add.add_argument("question_file")
    semantic_add.add_argument("answer_file")
    semantic_add.add_argument("--provider")
    semantic_add.add_argument("--model")
    semantic_lookup = semantic_sub.add_parser("lookup")
    semantic_lookup.add_argument("query")
    semantic_lookup.add_argument("--provider")
    semantic_lookup.add_argument("--model")
    semantic_sub.add_parser("stats")
    semantic_sub.add_parser("clear")

    layout = sub.add_parser("cache-layout")
    layout.add_argument("file")
    layout.add_argument("--model", default="gpt-4o-mini")
    layout.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "count":
        counter = TokenCounter(args.model)
        tokens = counter.count(_read(args.file))
        console.print(f"File: {args.file}")
        console.print(f"Model: {args.model}")
        console.print(f"Tokens: {tokens:,}")
        console.print(f"Fits {args.budget // 1000}k: {'yes' if tokens <= args.budget else 'no'}")
        return 0

    if args.command == "trim":
        console.print(TokenCounter(args.model).trim(_read(args.file), args.max_tokens))
        return 0

    if args.command == "compress":
        cp = ContextPress(model=args.model, max_input_tokens=args.target_tokens, compression_profile=args.profile)
        console.print(cp.optimize(task=args.task or "Compress this prompt.", context=_read(args.file)).text)
        return 0

    if args.command == "compact":
        console.print(compact_json(json.loads(_read(args.file))))
        return 0

    if args.command == "report":
        counter = TokenCounter(args.model)
        text = _read(args.file)
        before = counter.count(text)
        after = min(before, args.budget)
        console.print(UsageReport(args.model, before, after).to_markdown())
        return 0

    if args.command == "diff":
        original = _read(args.original)
        if args.optimized:
            optimized = _read(args.optimized)
        else:
            cp = ContextPress(model=args.model, max_input_tokens=args.target_tokens, compression_profile=args.profile)
            optimized = cp.optimize(task=args.task, context=original).text
        console.print(PromptDiff.compare(original, optimized).to_markdown())
        return 0

    if args.command == "benchmark":
        result = benchmark_path(args.path, model=args.model, max_input_tokens=args.max_input_tokens, task=args.task)
        console.print(json.dumps(result.as_dict(), indent=2) if args.json else result.summary())
        return 0

    if args.command == "doctor":
        if not args.file:
            console.print(install_health())
            return 0
        result = doctor_prompt(_read(args.file), model=args.model, budget=args.budget)
        console.print(json.dumps(result.as_dict(), indent=2) if args.json else result.summary())
        return 0

    if args.command == "estimate-cost":
        input_tokens = args.input_tokens
        if input_tokens is None:
            if not args.file:
                parser.error("estimate-cost requires a file or --input-tokens")
            input_tokens = TokenCounter(args.model).count(_read(args.file))
        result = estimate_cost(args.provider, args.model, input_tokens, args.output_tokens)
        console.print(json.dumps(result.as_dict(), indent=2) if args.json else result.summary())
        return 0

    if args.command == "cost":
        counter = TokenCounter(args.model)
        before = counter.count(_read(args.before))
        after = counter.count(_read(args.after)) if args.after else before
        result = CostEstimator(args.provider, args.model).estimate(before, after, args.output_tokens)
        console.print(json.dumps(result.as_dict(), indent=2) if args.json else result.summary())
        return 0

    if args.command == "pricing":
        console.print(json.dumps(PricingRegistry().list(), indent=2))
        return 0

    if args.command == "cache":
        cache_obj = ExactPromptCache(path=args.path)
        if args.cache_command == "stats":
            console.print(json.dumps(cache_obj.stats().as_dict(), indent=2))
        elif args.cache_command == "clear":
            console.print(f"Cleared {cache_obj.clear()} cache files.")
        elif args.cache_command == "list":
            console.print(json.dumps(cache_obj.list(), indent=2))
        return 0

    if args.command == "semantic-cache":
        semantic_obj = SemanticCache(path=args.path, similarity_threshold=args.threshold)
        if args.semantic_command == "add":
            semantic_obj.add(
                query=_read(args.question_file),
                answer=_read(args.answer_file),
                metadata={"provider": args.provider, "model": args.model},
            )
            console.print("Added semantic cache entry.")
        elif args.semantic_command == "lookup":
            hit = semantic_obj.lookup(args.query, provider=args.provider, model=args.model)
            console.print(json.dumps(hit.as_dict(), indent=2) if hit else "No semantic cache hit.")
        elif args.semantic_command == "stats":
            console.print(json.dumps(semantic_obj.stats(), indent=2))
        elif args.semantic_command == "clear":
            console.print(f"Cleared {semantic_obj.clear()} semantic cache entries.")
        return 0

    if args.command == "cache-layout":
        result = cache_layout_report(_read(args.file), model=args.model)
        console.print(json.dumps(result.as_dict(), indent=2) if args.json else "\n".join(f"{k}: {v}" for k, v in result.as_dict().items()))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
