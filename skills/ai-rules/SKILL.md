---
name: ai-rules
description: >-
  Apply the AI Rules engineering, testing, and verification discipline (TDD with observed red
  phase, BDD via an in-process test harness, deliberate E2E evaluation, pure functional core,
  closed variants, and evidence-backed claims) when writing, refactoring, or reviewing code in
  any programming language.
---

# AI Rules — Core Engineering & Testing Discipline

Use this skill whenever implementing features, fixing bugs, refactoring code, or reviewing changes
under the AI Rules methodology. If the repository contains `docs/rules.md` or a local `AGENTS.md`,
read it first — repository rules may tighten these defaults, never loosen them.

## Verification and Testing Order

Follow this sequence on every change that has executable behavior:

1. **Test before code, without exceptions.** The closed list of exceptions covers changes with no
   executable behavior only: documentation content, comments, commit messages, and tool-enforced
   formatting. Name the list item when relying on an exception; never invent new ones.
2. **Observe the red phase.** Run the new test before implementing and confirm it fails for the
   expected reason. For legacy or untested code, write a characterization test first.
3. **Pair unit TDD with behavioral tests (BDD).** Test pure core rules with mock-free unit tests,
   and test observable user-visible behavior across the real application boundary (HTTP, CLI,
   message handler, public workflow) in domain language (`Given / When / Then`), not internal call
   assertions.
4. **Use an in-process test harness.** In any project with a host, runtime boundary, or
   composition root, build and reuse an in-process test harness (`WebApplicationFactory` in
   ASP.NET Core / .NET, `TestClient` / ASGI in Python, `httptest.Server` in Go, `supertest` /
   `app.inject` in Node.js, `MockMvc` on JVM, or an in-memory CLI runner) that boots the real
   pipeline with deterministic fakes only at external I/O edges. Pure libraries without a host
   boundary may rely on core tests alone.
5. **Evaluate end-to-end (E2E) tests deliberately.** Never dismiss E2E tests by default. When UI
   rendering, visual behavior, packaging, or real runtime boundaries matter, set up idiomatic E2E
   tests for the stack (Playwright, UI automation, compiled CLI execution, or isolated local
   runtime) focused on critical journeys as an additive layer alongside fast in-process tests. If
   skipping E2E for such a project, state the concrete trade-off explicitly (and record
   project-wide decisions in `docs/decisions.md`).
6. **Prove every claim.** Do not use "works", "fixed", "done", or "safe" without naming the test
   that proves it; otherwise mark the behavior `unverified` and state what check is missing. Label
   judgments ("cleaner", "clearer") as judgments. Report only measured numbers.
7. **Run the single check command** and paste the raw output before declaring the task done.

## Architecture and Code Design

Translate these properties into the idioms of the project's language:

- **Functional core, thin I/O shell:** pure, deterministic logic receives state as an argument and
  returns a new value; network, filesystem, clock, randomness, and environment live at the edges.
- **Dependencies point inward:** adapters and UI depend on the core; the core never depends on
  them.
- **Validate once at the boundary** into narrow types; trust those types deeper in the core.
- **Closed variants with exhaustive matching** (sealed classes, discriminated unions, enums); if
  the language lacks sum types, write a test iterating every variant.
- **Errors as values in the core** (`Result`, `Either`, or explicit error types); exceptions stay
  at the boundary.
- **One source of truth per rule and one name per concept.** Never create `utils`, `helpers`,
  `manager`, `data`, `handler`, or `process` dumping grounds.
- **Small, readable units:** one file per topic (~300 lines), small functions (~30 lines), fixed
  section order (types, pure functions, adapters), early exits with at most two levels of nesting,
  data tables over `if`/`else` chains, no boolean flags in signatures.
- **Composition over inheritance** (inheritance only where the platform or framework requires it),
  at most 2–3 layers, no metaprogramming magic or speculative abstractions.
- **Minimal, pinned dependencies:** prefer the standard library, justify new packages, commit the
  lockfile.

## Working Process

- Find the existing pattern in the repository first and repeat it; record any new pattern in
  `docs/decisions.md` in the same change.
- One change, one purpose: no drive-by refactors, unrelated renames, or leftover `TODO` markers.
- Do not guess requirements or APIs: ask on ambiguous intent, read types/docs before calling APIs,
  and report uncertainty explicitly.
- Waiving a rule requires an explicit user instruction: name the waived rule and risk, record
  `Rule waived: <rule> (<reason>)` in reply and commit, and keep untested code `unverified`.
