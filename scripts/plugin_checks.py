"""Validate multi-harness plugin manifests, bundled rules, and Agent Skills.

Inputs: repository root Path containing plugin manifests and a skills/ directory.
Guarantees: reports missing manifests, invalid JSON, unknown Antigravity top-level keys,
version drift across manifests and pyproject.toml, invalid skill frontmatter, and
unexpected frontmatter in rules/AGENTS.md. Pure validation lives above the I/O adapter.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

MANIFEST_PATHS = (
    ".antigravity-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".codex-plugin/plugin.json",
    ".agents/plugins/marketplace.json",
)
PLUGIN_RULES_PATH = "rules/AGENTS.md"
COMMIT_MSG_HOOK_PATH = ".githooks/commit-msg"
ANTIGRAVITY_ALLOWED_KEYS = frozenset(
    {
        "$schema",
        "name",
        "displayName",
        "version",
        "description",
        "logo",
        "suggestedPrompts",
        "author",
        "homepage",
        "repository",
        "disabled",
    }
)
KEBAB_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Parse leading YAML frontmatter key/value pairs using the standard library."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end_index = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end_index is None:
        return None

    fields: dict[str, str] = {}
    current_key: str | None = None
    for line in lines[1:end_index]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0].isspace() and current_key is not None:
            piece = line.strip()
            existing = fields[current_key]
            fields[current_key] = f"{existing} {piece}".strip() if existing else piece
            continue
        if ":" not in line:
            return None
        key, raw_value = line.split(":", 1)
        current_key = key.strip()
        value = raw_value.strip()
        fields[current_key] = "" if value in (">", ">-", "|", "|-") else value.strip("\"'")
    return fields


def validate_antigravity_manifest(payload: dict) -> list[str]:
    problems: list[str] = []
    unknown = sorted(set(payload.keys()) - ANTIGRAVITY_ALLOWED_KEYS)
    for key in unknown:
        problems.append(f".antigravity-plugin/plugin.json unknown top-level key: {key}")
    for required in ("name", "description", "version"):
        if not str(payload.get(required, "")).strip():
            problems.append(f".antigravity-plugin/plugin.json missing required field: {required}")
    return problems


def validate_skill_markdown(relative_path: str, expected_name: str, text: str) -> list[str]:
    fields = parse_frontmatter(text)
    if fields is None:
        return [f"{relative_path} missing valid YAML frontmatter"]
    problems: list[str] = []
    name = fields.get("name", "").strip()
    if not name or not KEBAB_PATTERN.match(name):
        problems.append(f"{relative_path} invalid skill name: {name!r}")
    elif name != expected_name:
        problems.append(f"{relative_path} name {name!r} does not match directory {expected_name!r}")
    if not fields.get("description", "").strip():
        problems.append(f"{relative_path} missing frontmatter description")
    return problems


def validate_plugin_rules(text: str) -> list[str]:
    stripped = text.lstrip()
    if not stripped:
        return [f"{PLUGIN_RULES_PATH} is empty"]
    if stripped.startswith("---\n") or stripped.startswith("---\r\n"):
        return [f"{PLUGIN_RULES_PATH} must be plain Markdown without YAML frontmatter"]
    return []


def collect_versions(
    manifests: dict[str, dict], pyproject_version: str | None
) -> dict[str, str]:
    versions: dict[str, str] = {}
    if pyproject_version:
        versions["pyproject.toml"] = pyproject_version
    for rel in (
        ".antigravity-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        ".codex-plugin/plugin.json",
    ):
        payload = manifests.get(rel)
        if payload and isinstance(payload.get("version"), str):
            versions[rel] = payload["version"]
    claude_market = manifests.get(".claude-plugin/marketplace.json")
    if claude_market and isinstance(claude_market.get("plugins"), list):
        for entry in claude_market["plugins"]:
            if isinstance(entry, dict) and isinstance(entry.get("version"), str):
                versions[".claude-plugin/marketplace.json"] = entry["version"]
                break
    return versions


def validate_version_sync(versions: dict[str, str]) -> list[str]:
    if len(set(versions.values())) <= 1:
        return []
    summary = ", ".join(f"{path}={ver}" for path, ver in sorted(versions.items()))
    return [f"version mismatch across manifests: {summary}"]


def collect_plugin_names(manifests: dict[str, dict]) -> dict[str, str]:
    names: dict[str, str] = {}
    for rel in (
        ".antigravity-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        ".codex-plugin/plugin.json",
    ):
        payload = manifests.get(rel)
        if payload and isinstance(payload.get("name"), str):
            names[rel] = payload["name"]
    for rel in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
        market = manifests.get(rel)
        if market and isinstance(market.get("plugins"), list):
            for entry in market["plugins"]:
                if isinstance(entry, dict) and isinstance(entry.get("name"), str):
                    names[rel] = entry["name"]
                    break
    return names


def validate_name_sync(names: dict[str, str]) -> list[str]:
    if len(set(names.values())) <= 1:
        return []
    summary = ", ".join(f"{path}={name}" for path, name in sorted(names.items()))
    return [f"plugin name mismatch across manifests: {summary}"]


def collect_manifest_paths(manifests: dict[str, dict]) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    codex = manifests.get(".codex-plugin/plugin.json")
    if codex and isinstance(codex.get("skills"), str):
        refs.append((".codex-plugin/plugin.json", codex["skills"]))
    claude_market = manifests.get(".claude-plugin/marketplace.json")
    if claude_market and isinstance(claude_market.get("plugins"), list):
        for entry in claude_market["plugins"]:
            if isinstance(entry, dict) and isinstance(entry.get("source"), str):
                refs.append((".claude-plugin/marketplace.json", entry["source"]))
    agents_market = manifests.get(".agents/plugins/marketplace.json")
    if agents_market and isinstance(agents_market.get("plugins"), list):
        for entry in agents_market["plugins"]:
            source = entry.get("source") if isinstance(entry, dict) else None
            if isinstance(source, dict) and isinstance(source.get("path"), str):
                refs.append((".agents/plugins/marketplace.json", source["path"]))
    return refs


def validate_hook_line_endings(relative_path: str, raw_bytes: bytes) -> list[str]:
    if b"\r\n" in raw_bytes:
        return [f"{relative_path} must use LF line endings (CRLF breaks sh hooks)"]
    return []


# --- Filesystem adapter ---


def has_plugin_layout(root: Path) -> bool:
    return any((root / rel).exists() for rel in MANIFEST_PATHS) or (root / "skills").is_dir()


def read_pyproject_version(root: Path) -> str | None:
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return None
    parsed = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    version = parsed.get("project", {}).get("version")
    return str(version) if isinstance(version, str) else None


def find_plugin_problems(root: Path) -> list[str] | None:
    """Return None when no plugin layout exists, or a list of validation problems."""
    if not has_plugin_layout(root):
        return None

    problems: list[str] = []
    loaded: dict[str, dict] = {}
    for rel in MANIFEST_PATHS:
        path = root / rel
        if not path.exists():
            problems.append(f"missing manifest: {rel}")
            continue
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"{rel} invalid JSON: {exc.msg}")
            continue
        if not isinstance(parsed, dict):
            problems.append(f"{rel} must contain a JSON object")
            continue
        loaded[rel] = parsed

    if ".antigravity-plugin/plugin.json" in loaded:
        problems.extend(validate_antigravity_manifest(loaded[".antigravity-plugin/plugin.json"]))

    rules_file = root / PLUGIN_RULES_PATH
    if not rules_file.exists():
        problems.append(f"missing plugin rules file: {PLUGIN_RULES_PATH}")
    else:
        problems.extend(validate_plugin_rules(rules_file.read_text(encoding="utf-8")))

    skills_dir = root / "skills"
    skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir()) if skills_dir.is_dir() else []
    if not skill_dirs:
        problems.append("skills/ must contain at least one skill directory")
    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        relative = skill_file.relative_to(root).as_posix()
        if not skill_file.exists():
            problems.append(f"missing skill entrypoint: {relative}")
            continue
        problems.extend(
            validate_skill_markdown(
                relative, skill_dir.name, skill_file.read_text(encoding="utf-8")
            )
        )

    versions = collect_versions(loaded, read_pyproject_version(root))
    problems.extend(validate_version_sync(versions))
    problems.extend(validate_name_sync(collect_plugin_names(loaded)))

    for manifest_rel, target in collect_manifest_paths(loaded):
        if not (root / target).exists():
            problems.append(f"{manifest_rel} points to missing path: {target}")

    hook_file = root / COMMIT_MSG_HOOK_PATH
    if hook_file.exists():
        problems.extend(validate_hook_line_endings(COMMIT_MSG_HOOK_PATH, hook_file.read_bytes()))

    return problems
