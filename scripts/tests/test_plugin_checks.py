"""Behavioral tests for plugin manifest and skill validation in scripts/check.py.

Exercises the real check.py CLI entrypoint in-process against isolated temporary
repositories covering Antigravity, Claude Code, Codex, and Agent Skills layouts.

Run with: uv run pytest
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


def valid_plugin_files(version: str = "1.0.0") -> dict[str, str]:
    """Return a minimal valid multi-harness plugin layout."""
    core_concepts = (
        "Use an in-process test harness, evaluate end-to-end (E2E) tests, "
        "prefer vertical slice design in new apps, and respect legacy codebases.\n"
    )
    return {
        "pyproject.toml": f'[project]\nname = "ai-rules"\nversion = "{version}"\n',
        "README.md": f"# AI Rules\n\n{core_concepts}",
        "docs/rules.md": f"# Rules\n\n{core_concepts}",
        ".githooks/commit-msg": "#!/bin/sh\nexit 0\n",
        ".antigravity-plugin/plugin.json": json.dumps(
            {
                "$schema": "https://antigravity.google/schemas/v1/plugin.json",
                "name": "ai-rules",
                "displayName": "AI Rules",
                "version": version,
                "description": "Engineering and testing rules for AI agents.",
            }
        ),
        ".claude-plugin/plugin.json": json.dumps(
            {
                "name": "ai-rules",
                "version": version,
                "description": "Engineering and testing rules for AI agents.",
            }
        ),
        ".claude-plugin/marketplace.json": json.dumps(
            {
                "name": "ai-rules",
                "owner": {"name": "JonasWit"},
                "plugins": [
                    {
                        "name": "ai-rules",
                        "description": "Engineering and testing rules for AI agents.",
                        "version": version,
                        "source": "./",
                    }
                ],
            }
        ),
        ".codex-plugin/plugin.json": json.dumps(
            {
                "name": "ai-rules",
                "version": version,
                "description": "Engineering and testing rules for AI agents.",
                "skills": "./skills/",
            }
        ),
        ".agents/plugins/marketplace.json": json.dumps(
            {
                "name": "ai-rules",
                "interface": {"displayName": "AI Rules"},
                "plugins": [
                    {
                        "name": "ai-rules",
                        "source": {"source": "local", "path": "./"},
                        "policy": {
                            "installation": "AVAILABLE",
                            "authentication": "ON_INSTALL",
                        },
                        "category": "Productivity",
                    }
                ],
            }
        ),
        "rules/AGENTS.md": f"# Agent Instructions\n\n- Test before code.\n- {core_concepts}",
        "skills/ai-rules/SKILL.md": (
            "---\n"
            "name: ai-rules\n"
            "description: Core engineering and testing rules.\n"
            "---\n\n"
            f"# AI Rules\n\n{core_concepts}"
        ),
    }


@pytest.fixture()
def make_plugin_repo(tmp_path: Path, check_module):
    """Build an isolated repository with required docs and plugin bundle files."""

    def build(
        overrides: dict[str, str] | None = None,
        omit: tuple[str, ...] = (),
        version: str = "1.0.0",
    ) -> Path:
        root = tmp_path / "repo"
        root.mkdir()
        for name in check_module.REQUIRED_FILES:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# placeholder\n", encoding="utf-8")
        files = valid_plugin_files(version=version)
        for key in omit:
            files.pop(key, None)
        if overrides:
            files.update(overrides)
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content.encode("utf-8"))
        return root

    return build


@pytest.fixture()
def run(capsys, monkeypatch, check_module):
    def execute(root: Path) -> tuple[int, str]:
        monkeypatch.setenv("CHECK_SKIP_STACK", "1")
        code = check_module.main(["--root", str(root)])
        return code, capsys.readouterr().out

    return execute


def test_valid_plugin_bundle_passes(make_plugin_repo, run):
    root = make_plugin_repo()
    code, out = run(root)
    assert code == 0
    assert "PASS plugin manifests" in out


def test_missing_codex_manifest_fails(make_plugin_repo, run):
    root = make_plugin_repo(omit=(".codex-plugin/plugin.json",))
    code, out = run(root)
    assert code == 1
    assert ".codex-plugin/plugin.json" in out


def test_invalid_json_in_manifest_fails(make_plugin_repo, run):
    root = make_plugin_repo(overrides={".claude-plugin/plugin.json": "{not-json"})
    code, out = run(root)
    assert code == 1
    assert ".claude-plugin/plugin.json" in out


def test_version_mismatch_across_manifests_fails(make_plugin_repo, run):
    bad_claude = json.dumps(
        {"name": "ai-rules", "version": "0.9.0", "description": "Stale version."}
    )
    root = make_plugin_repo(overrides={".claude-plugin/plugin.json": bad_claude})
    code, out = run(root)
    assert code == 1
    assert "version" in out.lower()


def test_unknown_top_level_key_in_antigravity_manifest_fails(make_plugin_repo, run):
    bad_agy = json.dumps(
        {
            "name": "ai-rules",
            "version": "1.0.0",
            "description": "Has unknown key.",
            "skills": "./skills/",
        }
    )
    root = make_plugin_repo(overrides={".antigravity-plugin/plugin.json": bad_agy})
    code, out = run(root)
    assert code == 1
    assert "skills" in out


def test_skill_frontmatter_name_must_match_directory(make_plugin_repo, run):
    bad_skill = "---\nname: wrong-name\ndescription: Valid description.\n---\n\n# Body\n"
    root = make_plugin_repo(overrides={"skills/ai-rules/SKILL.md": bad_skill})
    code, out = run(root)
    assert code == 1
    assert "skills/ai-rules/SKILL.md" in out


def test_skill_without_frontmatter_fails(make_plugin_repo, run):
    root = make_plugin_repo(overrides={"skills/ai-rules/SKILL.md": "# No frontmatter\n"})
    code, out = run(root)
    assert code == 1
    assert "skills/ai-rules/SKILL.md" in out


def test_plugin_rules_file_rejects_yaml_frontmatter(make_plugin_repo, run):
    frontmatter_rules = "---\ntrigger: always_on\n---\n\n# Rules\n"
    root = make_plugin_repo(overrides={"rules/AGENTS.md": frontmatter_rules})
    code, out = run(root)
    assert code == 1
    assert "rules/AGENTS.md" in out


def test_manifest_pointing_to_missing_path_fails(make_plugin_repo, run):
    bad_codex = json.dumps(
        {
            "name": "ai-rules",
            "version": "1.0.0",
            "description": "Points to missing skills dir.",
            "skills": "./missing-skills/",
        }
    )
    root = make_plugin_repo(overrides={".codex-plugin/plugin.json": bad_codex})
    code, out = run(root)
    assert code == 1
    assert "missing-skills" in out


def test_plugin_name_mismatch_across_manifests_fails(make_plugin_repo, run):
    bad_codex = json.dumps(
        {
            "name": "wrong-plugin",
            "version": "1.0.0",
            "description": "Mismatched plugin name.",
            "skills": "./skills/",
        }
    )
    root = make_plugin_repo(overrides={".codex-plugin/plugin.json": bad_codex})
    code, out = run(root)
    assert code == 1
    assert "name mismatch" in out.lower()


def test_commit_msg_hook_with_crlf_fails(make_plugin_repo, run):
    root = make_plugin_repo(overrides={".githooks/commit-msg": "#!/bin/sh\r\nexit 0\r\n"})
    code, out = run(root)
    assert code == 1
    assert ".githooks/commit-msg" in out


def test_missing_core_concept_in_carrier_fails(make_plugin_repo, run):
    incomplete_skill = (
        "---\nname: ai-rules\ndescription: Incomplete skill.\n---\n\n"
        "Use an in-process test harness, end-to-end (E2E) tests, and respect legacy code.\n"
    )
    root = make_plugin_repo(overrides={"skills/ai-rules/SKILL.md": incomplete_skill})
    code, out = run(root)
    assert code == 1
    assert "vertical slice" in out
    assert "skills/ai-rules/SKILL.md" in out


def test_all_carriers_mention_every_concept_passes(make_plugin_repo, run):
    root = make_plugin_repo()
    code, out = run(root)
    assert code == 0
    assert "PASS concept sync" in out
