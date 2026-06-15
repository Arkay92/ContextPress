from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

from contpress.core import ContextPress


@dataclass(slots=True)
class BenchmarkResult:
    files: int
    average_original_tokens: float
    average_optimized_tokens: float
    average_reduction_percent: float
    average_processing_time: float = 0.0
    reports: list[dict[str, object]] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "files": self.files,
            "average_original_tokens": round(self.average_original_tokens, 1),
            "average_optimized_tokens": round(self.average_optimized_tokens, 1),
            "average_reduction_percent": round(self.average_reduction_percent, 1),
            "average_processing_time": round(self.average_processing_time, 4),
            "reports": self.reports,
        }

    def summary(self) -> str:
        return "\n".join(
            [
                f"Files: {self.files}",
                f"Average original tokens: {self.average_original_tokens:,.0f}",
                f"Average optimized tokens: {self.average_optimized_tokens:,.0f}",
                f"Average reduction: {self.average_reduction_percent:.1f}%",
                f"Average processing time: {self.average_processing_time:.2f}s",
            ]
        )


def benchmark_path(
    path: str,
    model: str = "gpt-4o-mini",
    max_input_tokens: int = 4_000,
    task: str = "Optimize this prompt.",
) -> BenchmarkResult:
    root = Path(path)
    files = [root] if root.is_file() else sorted(item for item in root.rglob("*") if item.is_file())
    text_files = [item for item in files if item.suffix.lower() in {"", ".txt", ".md", ".json", ".csv", ".log"}]
    if not text_files:
        raise ValueError("No benchmarkable text files found.")

    cp = ContextPress(model=model, max_input_tokens=max_input_tokens)
    reports: list[dict[str, object]] = []
    elapsed = 0.0
    for item in text_files:
        text = item.read_text(encoding="utf-8")
        started = perf_counter()
        optimized = cp.optimize(task=task, context=text)
        elapsed += perf_counter() - started
        report = optimized.report.as_dict()
        report["file"] = str(item)
        reports.append(report)

    original = sum(int(report["original_tokens"]) for report in reports)
    optimized_tokens = sum(int(report["optimized_tokens"]) for report in reports)
    count = len(reports)
    reduction = 0.0 if original == 0 else (1 - (optimized_tokens / original)) * 100
    return BenchmarkResult(
        files=count,
        average_original_tokens=original / count,
        average_optimized_tokens=optimized_tokens / count,
        average_reduction_percent=reduction,
        average_processing_time=elapsed / count,
        reports=reports,
    )
