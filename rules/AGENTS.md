# Agent Instructions

Global software engineering, architecture, and agent working rules based on AI-Rules (https://github.com/JonasWit/AI-Rules).
Repository-level instructions and `docs/rules.md` tighten these defaults; repository rules may not loosen them.

## Verification and tests

- Test before code, without exceptions. Closed list of exceptions (no executable behavior only): documentation content, comments, commit messages, tool-enforced formatting. Name the list item when using an exception; never invent new ones.
- Observe the red phase before implementing. A test written after the implementation proves nothing; revert, observe red, then implement.
- Pair TDD with behavioral tests (BDD) across the real application boundary (HTTP, CLI, message handler, public workflow) in domain language (`Given / When / Then`), not internal call assertions. Pure libraries may rely on core tests alone.
- Build a reusable in-process test harness in every project with a host, runtime boundary, or composition root (e.g., `WebApplicationFactory` in .NET, `TestClient` in Python, `httptest.Server` in Go, `supertest` in Node.js, or an in-memory CLI runner).
- Run the in-process test harness with deterministic fakes only at external I/O edges, isolated per test, inside the single check command.
- Evaluate end-to-end (E2E) tests deliberately for every project with UI, visual output, packaging, or real-runtime boundaries; never dismiss them by default.
- When E2E adds real confidence, set up idiomatic E2E tests (Playwright, UI automation, compiled CLI execution, or isolated local runtime) for critical flows as an additive layer alongside unit TDD and in-process BDD.
- When skipping E2E for a project with a UI or runtime boundary, state the concrete trade-off explicitly (and record project-wide decisions in `docs/decisions.md`).
- Write a characterization test before changing legacy or untested code.
- No claim without a test. Words like "works", "fixed", "done", "safe", or "does not affect anything else" require the name of the proving test; otherwise mark as `unverified` and state what check is missing.
- Label judgments ("cleaner", "clearer", "less code") as judgments, never as proof of correctness.
- Numbers (timings, sizes, coverage, counts) must come from an actual run, never estimates.
- Waiving a rule requires an explicit user instruction (never inferred from hurry). Name the waived rule and its risk, and record `Rule waived: <rule> (<reason>)` in the reply and commit. Waiving a test rule never waives the ban on claims — untested code stays `unverified`.
- One test, one rule. Test names are full sentences in domain language stating the guaranteed behavior.
- Keep tests deterministic (no real clock, network, or randomness). Test core logic without mocks; use mocks only at external boundaries you defined. Use property or snapshot tests when cases are too numerous to enumerate.

## Architecture and code design

- Functional core, thin I/O shell. Logic must not know network, filesystem, clock, randomness, or environment exist; inject them at the edges.
- Dependencies point inward. Adapters and UI know the core; the core never knows adapters or UI.
- Validate once at the boundary into narrow types; trust them deeply.
- One source of truth per business rule; never duplicate logic or validation across modules.
- In greenfield applications (or repos already using them), prefer vertical slices by feature inside domain boundaries (`orders/create_order`, `orders/cancel_order`) with explicit registration and direct calls — not horizontal layers (`controllers/` + `services/` + `repositories/`), god-services, or mediator/reflection magic.
- In existing or legacy repositories, respect the established architecture instead of forcing vertical slices in; change architecture only through an explicit decision in `docs/decisions.md`.
- Keep slice-specific DTOs, wiring, and queries local; keep business rules shared by two or more slices in one pure domain core. Pure libraries stay organized around domain types and pure functions.
- Closed variants with exhaustive matching (sealed classes, discriminated unions, or enums). In languages without sum types, write a test iterating every variant.
- Errors as values in the core (`Result`, `Either`, or explicit error types). Exceptions stay at the boundary.
- Explicit immutable state passed as argument and returned as a new value. No mutable global state, singletons, or input mutation.
- Load configuration once at startup and pass it explicitly.
- Composition over inheritance (use inheritance only where the platform or framework requires it); at most 2–3 layers of abstraction. No DI containers, behavior-changing decorators, or metaprogramming magic.
- No abstractions "for the future", no extra layers without a proven problem, and no shared extraction until two real uses exist.
- One file, one topic (convention: ~300 lines/file, ~30 lines/function). Fixed layout: types, pure functions, adapters at bottom. Narrow module API: few public functions, rest private.
- Build complex transformations as a pipeline of small pure steps; use early exits with at most 2 levels of nesting; prefer data (tables/mappings) over `if`/`else` chains; keep collection and output ordering deterministic.
- One concept, one name across the codebase. Never use `data`, `manager`, `utils`, `helper`, `handler`, or `process`.
- No boolean flags or long positional parameter lists. Use separate functions or a named options object.
- Comments explain traps and "why", never what the code does. Every module starts with a brief header stating why it exists, inputs, and guarantees.
- Minimal, pinned dependencies: prefer the standard library, justify every new package, and keep the lockfile committed.

## Working process

- Find the existing pattern in the repository first and repeat it.
- Record every new pattern in `docs/decisions.md` in the same change.
- One change, one purpose. No drive-by refactorings, unrelated renames, or leftover `TODO`s; report unrelated issues separately.
- For broad cleanup requests, confirm scope and split into small changes instead of one large diff.
- Do not guess intent. When requirements are ambiguous, ask with concrete options and the recommended option first.
- Do not guess APIs. Read repository types or official documentation before writing calls; report unconfirmed signatures instead of guessing.
- Report uncertainty explicitly. Silence about uncertainty is a false claim.
- Run the project's single check command and paste the raw output before declaring work done.

## Language and communication

- Write code, documentation, instruction files, comments, commit messages, and repository metadata in English.
- Reply to the user in the user's language.
