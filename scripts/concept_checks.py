"""Verify that core AI-Rules concepts stay synchronized across every rule carrier.

Inputs: repository root Path containing canonical docs, bundled plugin rules, and skills.
Guarantees: reports any core concept missing from any declared carrier file so rule updates
do not silently drift across docs/rules.md, rules/AGENTS.md, skills/ai-rules/SKILL.md, and
README.md. Pure validation lives above the filesystem adapter.
"""

from __future__ import annotations

from pathlib import Path

CARRIER_FILES = (
    "docs/rules.md",
    "rules/AGENTS.md",
    "skills/ai-rules/SKILL.md",
    "README.md",
)

CONCEPT_CARRIERS: dict[str, tuple[str, ...]] = {
    "in-process test harness": CARRIER_FILES,
    "end-to-end (E2E)": CARRIER_FILES,
    "vertical slice": CARRIER_FILES,
    "legacy": CARRIER_FILES,
}


def validate_concept_carriers(texts: dict[str, str]) -> list[str]:
    problems: list[str] = []
    for concept, carriers in CONCEPT_CARRIERS.items():
        needle = concept.lower()
        for carrier in carriers:
            body = texts.get(carrier)
            if body is None:
                problems.append(f"concept '{concept}' missing carrier file: {carrier}")
            elif needle not in body.lower():
                problems.append(f"concept '{concept}' missing in {carrier}")
    return problems


# --- Filesystem adapter ---


def find_concept_sync_problems(root: Path, active: bool) -> list[str] | None:
    """Return None when inactive (no plugin layout), or missing concept references."""
    if not active:
        return None
    carriers = sorted({carrier for paths in CONCEPT_CARRIERS.values() for carrier in paths})
    texts: dict[str, str] = {}
    for rel in carriers:
        path = root / rel
        if path.exists():
            texts[rel] = path.read_text(encoding="utf-8", errors="replace")
    return validate_concept_carriers(texts)
