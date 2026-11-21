---
name: ai-rules-decision
description: >-
  Introduce a new architectural pattern or record an explicit exception in docs/decisions.md
  using the AI Rules ADR template (problem, decision, rejected alternatives, consequences). Use
  whenever no existing repository pattern fits or when documenting a project-wide trade-off such
  as skipping E2E tests or choosing a stack convention.
---

# Record an Architectural Pattern Decision

Use this runbook whenever introducing a pattern that does not yet exist in the repository,
changing an existing pattern, or documenting a deliberate exception (for example, choosing not to
set up E2E tests for a specific project boundary).

## Step 1: Search for an Existing Pattern First

1. Search the repository for how similar problems are already solved.
2. If an existing pattern fits, **repeat it** instead of inventing a new one — consistency with
   the local idiom lowers context cost more than a marginally better alternative.
3. Proceed to Step 2 only when no existing pattern fits, an existing pattern is being replaced, or
   an alternative keeps recurring and must be explicitly rejected.

## Step 2: Evaluate Against the Three Measures

Before accepting a new pattern, check it against:

- **Context cost:** how many files must an agent read to make one safe change?
- **Change locality:** how many places must be edited when one requirement changes?
- **Error detectability:** will a forgotten case fail the compiler or a test, or slip silently into
  runtime?

Reject patterns that look elegant to humans but require holding implicit invariants across many
files.

## Step 3: Append the Entry to `docs/decisions.md`

Create `docs/decisions.md` if it does not exist, and add the decision **in the same change** as the
code or rule update using this exact structure:

```markdown
### <Short decision name>

**Status:** accepted | rejected | to revise

**Problem:** one sentence stating what required a decision.

**Decision:** what was decided, written in the imperative.

**Rejected alternatives:** concrete alternatives considered and why each was dropped.

**Consequences:** what future changes must follow or avoid because of this decision.
```

An entry without **Rejected alternatives** is incomplete: without recording why alternatives were
dropped, rejected ideas keep returning in future sessions.

## Step 4: Verify Consistency

1. Check that any superseded decision is marked `superseded by "<new decision>"` instead of being
   silently deleted.
2. Check whether `README.md`, `AGENTS.md`, or `docs/rules.md` needs a matching summary update.
3. Run the project's single check command and paste the raw output in your reply.
