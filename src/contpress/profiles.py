from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CompressionProfile:
    name: str
    context_ratio: float
    description: str
    warnings: tuple[str, ...] = ()


COMPRESSION_PROFILES = {
    "safe": CompressionProfile(
        "safe",
        0.85,
        "Preserves numbers, IDs, code, URLs, headings, and constraints.",
    ),
    "balanced": CompressionProfile(
        "balanced",
        0.75,
        "Stronger sentence filtering for general prompts.",
    ),
    "aggressive": CompressionProfile(
        "aggressive",
        0.45,
        "Maximum reduction with higher risk of losing nuance.",
        ("Aggressive compression may remove useful context.",),
    ),
    "code": CompressionProfile(
        "code",
        0.9,
        "Preserves code blocks, file paths, identifiers, and errors.",
    ),
    "rag": CompressionProfile(
        "rag",
        0.65,
        "Prioritizes query-relevant facts from retrieved chunks.",
    ),
    "legal": CompressionProfile(
        "legal",
        0.95,
        "Minimal rewriting; mostly filtering and trimming only.",
        ("Legal/profile-sensitive prompts should be manually reviewed.",),
    ),
}


def get_compression_profile(name: str | None) -> CompressionProfile:
    key = (name or "balanced").lower()
    if key not in COMPRESSION_PROFILES:
        known = ", ".join(sorted(COMPRESSION_PROFILES))
        raise ValueError(f"Unknown compression profile '{name}'. Known profiles: {known}")
    return COMPRESSION_PROFILES[key]
