---
name: ai-rules-adopt
description: >-
  Adopt AI Rules in a new or existing repository by setting up AGENTS.md, thin harness adapters
  (such as CLAUDE.md), a single check command, docs/decisions.md, an in-process test harness,
  and the commit-msg evidence hook. Use when the user asks to configure, bootstrap, or onboard
  AI Rules into a project.
---

# Adopt AI Rules in a Repository

Use this runbook to onboard a repository onto the AI Rules workflow while respecting the project's
existing language and toolchain.

## Step 1: Inspect the Project

Before creating or editing files, read:

- Existing instruction files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/rules/`,
  `.github/copilot-instructions.md`) to avoid duplicating or clobbering local rules.
- The existing codebase architecture (greenfield vs. established or legacy structure). On a
  greenfield repository, adopt the full AI Rules architectural defaults (including vertical slices
  where appropriate). On an existing or legacy repository, respect the established architecture —
  do not force vertical slices or a disruptive rewrite unless the user explicitly asks to migrate
  and records that decision in `docs/decisions.md`.
- Build, lint, typecheck, and test configuration (`pyproject.toml`, `package.json`, `*.sln`,
  `go.mod`, `Cargo.toml`, `build.gradle*`, etc.).
- Existing `docs/` directory and `.githooks/` or CI workflows.

Never introduce a second toolchain for a project that already has one.

## Step 2: Create One Source of Rules and Thin Adapters

1. Create or update `AGENTS.md` at the repository root using the fixed section order:
   - Short repository summary and links to canonical docs in the first section.
   - `## Verification and tests` (test-before-code, observed red phase, BDD + in-process test
     harness, deliberate E2E evaluation, no claims without tests, exact check command).
   - `## Design rules` (concise imperatives, never a copy of full prose).
   - `## Working process` (repeat existing pattern, record new patterns in `docs/decisions.md`,
     one change per purpose, ask instead of guessing).
   - `## Structure and commands` (exact, verified commands and source layout).
   - `## Precedence` (global instructions provide defaults; repository rules tighten and may not
     loosen them).
2. If the team uses Claude Code or another harness that reads its own filename, create a **thin
   adapter** with zero duplicated rules (for example, `CLAUDE.md` containing only `@AGENTS.md`).
3. Create `docs/decisions.md` with the 5-part entry template (`Status`, `Problem`, `Decision`,
   `Rejected alternatives`, `Consequences`) if it does not exist yet.

## Step 3: Make Verification Executable

Move high-stakes rules up the enforcement ladder from prose to commands and hooks:

1. **Single check command:** ensure one command runs formatting/lint, typecheck, unit TDD tests,
   and in-process BDD tests quickly (and wire an explicit E2E command or CI stage when UI or real
   runtime boundaries warrant E2E coverage).
2. **In-process test harness:** if the project has an application host, HTTP boundary, or CLI
   entrypoint and lacks a test harness, scaffold a minimal reusable harness (`WebApplicationFactory`
   for ASP.NET Core, `TestClient` for Python ASGI/WSGI, `httptest.Server` for Go, `supertest` /
   `app.inject` for Node.js, or an in-memory CLI runner) with one behavioral smoke test.
3. **Commit evidence hook:** add `.githooks/commit-msg` requiring a `Test: <name>` or
   `Unverified: <reason>` trailer, and document `git config core.hooksPath .githooks`.
4. **Pull request template:** add `.github/pull_request_template.md` with the definition-of-done
   checklist and raw check-output evidence block.

## Step 4: Verify Before Finishing

1. Run the project's single check command in full and confirm every command documented in
   `AGENTS.md` exists and passes.
2. Check that no full rule prose was duplicated across `AGENTS.md`, adapters, and `docs/`.
3. Paste the raw check command output in your response and explicitly list anything left
   `unverified` (for example, running probes in a fresh session).
