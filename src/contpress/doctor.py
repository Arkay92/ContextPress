from __future__ import annotations

from dataclasses import dataclass, field
from importlib.util import find_spec

from contpress.tokenizer import TokenCounter


@dataclass(slots=True)
class DoctorFinding:
    code: str
    severity: str
    message: str
    suggestion: str

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "suggestion": self.suggestion,
        }


@dataclass(slots=True)
class DoctorReport:
    model: str
    tokens: int
    budget: int
    findings: list[DoctorFinding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(finding.severity in {"high", "critical"} for finding in self.findings)

    def as_dict(self) -> dict[str, object]:
        return {
            "model": self.model,
            "tokens": self.tokens,
            "budget": self.budget,
            "ok": self.ok,
            "findings": [finding.as_dict() for finding in self.findings],
        }

    def summary(self) -> str:
        lines = [
            f"Model: {self.model}",
            f"Tokens: {self.tokens:,}",
            f"Budget: {self.budget:,}",
            f"Status: {'ok' if self.ok else 'needs attention'}",
        ]
        if self.findings:
            lines.append("Findings:")
            for finding in self.findings:
                lines.append(f"- [{finding.severity}] {finding.code}: {finding.message}")
                lines.append(f"  Suggestion: {finding.suggestion}")
        return "\n".join(lines)


def doctor_prompt(text: str, model: str = "gpt-4o-mini", budget: int = 8_000) -> DoctorReport:
    counter = TokenCounter(model)
    tokens = counter.count(text)
    findings: list[DoctorFinding] = []

    if tokens > budget:
        findings.append(
            DoctorFinding(
                code="OVER_BUDGET",
                severity="critical",
                message=f"Prompt is {tokens - budget:,} tokens over budget.",
                suggestion="Filter context, compress, or trim before sending the request.",
            )
        )
    elif tokens > int(budget * 0.85):
        findings.append(
            DoctorFinding(
                code="NEAR_BUDGET",
                severity="medium",
                message="Prompt is using more than 85% of the configured budget.",
                suggestion="Reserve space for tool calls, retrieved context, and output drift.",
            )
        )

    lower = text.lower()
    if lower.count("be concise") > 1 or lower.count("use only") > 1:
        findings.append(
            DoctorFinding(
                code="REPEATED_INSTRUCTIONS",
                severity="low",
                message="Common instruction text appears more than once.",
                suggestion="Move repeated rules into one stable prompt block.",
            )
        )

    if "```" in text and tokens > int(budget * 0.5):
        findings.append(
            DoctorFinding(
                code="LARGE_CODE_BLOCK",
                severity="medium",
                message="Large prompt includes fenced code blocks.",
                suggestion="Preserve exact code when compressing, or filter to relevant files first.",
            )
        )

    if not findings:
        findings.append(
            DoctorFinding(
                code="NO_MAJOR_ISSUES",
                severity="info",
                message="No major prompt budget issues detected.",
                suggestion="Use report or benchmark commands to measure practical savings.",
            )
        )

    return DoctorReport(model=model, tokens=tokens, budget=budget, findings=findings)


def install_health() -> str:
    checks = {
        "Base install": True,
        "tiktoken": find_spec("tiktoken") is not None,
        "rich": find_spec("rich") is not None,
        "semantic extras": all(find_spec(name) is not None for name in ("sentence_transformers", "faiss", "diskcache", "numpy")),
        "llmlingua extras": find_spec("llmlingua") is not None,
        "rag extras": find_spec("langchain") is not None and find_spec("llama_index") is not None,
    }
    lines = ["ContextPress Doctor", "-------------------"]
    for name, ok in checks.items():
        lines.append(f"{name}: {'OK' if ok else 'missing'}")
    missing = [name for name, ok in checks.items() if not ok and name.endswith("extras")]
    if missing:
        lines.append("")
        lines.append("Suggestions:")
        if "semantic extras" in missing:
            lines.append('pip install "contpress[semantic]"')
        if "llmlingua extras" in missing:
            lines.append('pip install "contpress[compress]"')
        if "rag extras" in missing:
            lines.append('pip install "contpress[rag]"')
    return "\n".join(lines)
