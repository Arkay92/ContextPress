from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console

from contpress.core import ContextPress
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

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
