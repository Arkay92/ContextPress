from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path

from rich.console import Console

from contpress.benchmark import benchmark_path
from contpress.core import ContextPress
from contpress.costs import estimate_cost
from contpress.doctor import doctor_prompt
from contpress.formatters import compact_json
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

    compact = sub.add_parser("compact")
    compact.add_argument("file")

    report = sub.add_parser("report")
    report.add_argument("file")
    report.add_argument("--model", default="gpt-4o-mini")
    report.add_argument("--budget", type=int, default=8_000)

    diff = sub.add_parser("diff")
    diff.add_argument("file")
    diff.add_argument("--model", default="gpt-4o-mini")
    diff.add_argument("--target-tokens", type=int, default=1_000)
    diff.add_argument("--task", default="Compress this prompt.")

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
        cp = ContextPress(model=args.model, max_input_tokens=args.target_tokens)
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
        console.print(UsageReport(args.model, before, after).summary())
        return 0

    if args.command == "diff":
        text = _read(args.file)
        cp = ContextPress(model=args.model, max_input_tokens=args.target_tokens)
        optimized = cp.optimize(task=args.task, context=text)
        console.print(
            "\n".join(
                difflib.unified_diff(
                    text.splitlines(),
                    optimized.text.splitlines(),
                    fromfile=args.file,
                    tofile="optimized",
                    lineterm="",
                )
            )
        )
        return 0

    if args.command == "benchmark":
        result = benchmark_path(
            args.path,
            model=args.model,
            max_input_tokens=args.max_input_tokens,
            task=args.task,
        )
        console.print(json.dumps(result.as_dict(), indent=2) if args.json else result.summary())
        return 0

    if args.command == "doctor":
        text = _read(args.file) if args.file else ""
        result = doctor_prompt(text, model=args.model, budget=args.budget)
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

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
