---
name: ai-rules-audit
description: >-
  Audit a codebase, pull request, or agent instruction files against AI Rules (context cost,
  change locality, error detectability, TDD/BDD/E2E coverage, instruction-file hygiene, and
  behavioral probes). Use when the user asks to review, audit, or check compliance with AI Rules.
---

# Audit Against AI Rules

Use this runbook to audit instruction files, code architecture, and test verification discipline
without making drive-by refactors.

## Step 1: Confirm Scope

Clarify what is being audited:

- **Instruction files & enforcement** (`AGENTS.md`, adapters, `docs/`, check command, hooks, CI)
- **Code & tests** (a PR diff, a module, or the whole repository)
- **Behavioral probes** (checking whether the active rules actually bind the agent)

Do not edit production code during an audit unless the user explicitly asks for fixes in a
separate, scoped change.

## Step 2: Audit Instruction Files and Enforcement Ladder

Check every instruction file against these falsifiable criteria:

- Are the highest-cost prohibitions in the first dozen lines?
- Does every rule state how to recognize a violation (no vague adjectives like "clean" or "solid")?
- Are longer justifications kept in `docs/` with links at the top of the instruction file?
- Is there zero duplication of full rule text across `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and
  `docs/`?
- Do all documented test and check commands exist and pass?
- Is every high-stakes rule enforced at the right rung (command for tests/lint, hook for commit
  evidence, CI for merge gates) rather than left as prose?

## Step 3: Audit Code and Tests

Evaluate code through the three AI-failure measures — **context cost**, **change locality**, and
**error detectability** — checking specifically for:

- **Testing discipline:** pure core unit tests without mocks, behavioral tests (BDD) through an
  in-process test harness for host/entrypoint boundaries, deliberate E2E evaluation for UI or real
  runtime flows, deterministic execution (no real clock/network/randomness), and single-command run.
- **Core purity & boundaries:** side effects isolated in thin edge adapters, boundary validation
  into narrow types, explicit immutable state, configuration loaded once at startup.
- **Error detectability:** closed variants with exhaustive matching (or exhaustive variant tests),
  errors returned as values in the core, one source of truth per business rule.
- **Readability & locality:** vertical slices by feature with explicit wiring in applications (flag
  horizontal technical layers, god-services, duplicated business rules across slices, and
  unnecessary mediator/reflection indirection), one file per topic (~300 lines), small functions
  (~30 lines), max 2 levels of nesting, no boolean flags in signatures, no
  `utils`/`helper`/`manager`/`data` dumping grounds, no speculative layers, pinned minimal
  dependencies, no leftover `TODO` markers.
- **Pattern governance:** every non-standard pattern recorded in `docs/decisions.md` with rejected
  alternatives.

## Step 4: Report Findings Clearly

Structure the audit report into four sections:

1. **Verified defects** — concrete rule violations with exact file paths, line numbers, and
   observed command/test output.
2. **Enforcement gaps** — rules currently sitting only in prose that should move to a check
   command, hook, or CI (or be deleted if dead).
3. **Judgments** — stylistic or structural observations explicitly labeled as judgments, never
   presented as proof of bugs.
4. **Unverified** — anything not executed or checked (for example, live E2E runs or clean-session
   probes) and what is needed to verify it.
