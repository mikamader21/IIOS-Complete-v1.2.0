# IIOS Self-Evolution Protocol

**Status:** Specified, not activated (see `MASTER_IMPLEMENTATION_PROGRAM.md` Phase 11)
**Parent authority:** `docs/00_MASTER_CHARTER.md`, `docs/01_CONSTITUTION.md` Article III

## Purpose

Define how IIOS may improve itself — prompts, tests, skills, agents, model choices — without ever expanding its own authority. This is the protocol Constitution Article III.11 ("No agent approves its own privilege expansion") and III.12 ("Generated skills require tests, review and controlled promotion") exist to bound. Nothing here is active until Phase 11 is explicitly authorized; today this document is a contract, not a running loop.

## Permitted without additional authorization (within an already-authorized task)

- Proposing improvements.
- Creating experiments.
- Evaluating models.
- Optimizing prompts.
- Improving tests.
- Detecting missing skills.
- Proposing new agents.
- Measuring cost and performance.

Each of these produces a **proposal or a measurement** — never a self-executed authority change. "Proposing a new agent" is permitted; activating one with any new tool/permission scope is not (`docs/WORKFLOW_REGISTRY.md` — WF-AGENT-CREATION).

## Prohibited without the Owner

- Changing the Charter.
- Changing the Constitution.
- Changing the Kernel.
- Expanding permissions.
- Deleting audit records.
- Modifying action classes.
- Elevating its own authority.
- Deploying production changes.
- Executing financial operations.

These mirror `AUTONOMY_PROTOCOL.md`'s stop conditions exactly, because self-evolution is the one activity most likely to try to rationalize its way past them — "this change would make the system better" is never itself authorization.

## Every self-evolution proposal must produce

```text
1. Hypothesis   — what is expected to improve, and why
2. Evidence      — the data/observation motivating the hypothesis
3. Experiment    — the bounded, reversible test of the hypothesis
4. Results        — what actually happened, measured, not narrated
5. Impact         — cost/quality/risk delta, honestly stated (including negative results)
6. Rollback       — how to undo it if it does not hold up
7. Pull Request   — the artifact a human can review
8. Human decision — required whenever the change touches scope beyond the experiment
                     itself (a new default, a new skill promotion, a new agent activation)
```

A proposal missing any of these eight elements is incomplete, not merely light on documentation — it does not proceed to review.

## Relationship to the Skill Evolution Pipeline

This protocol governs *what* may be proposed and *how* it must be evidenced. `docs/09_SKILL_EVOLUTION_PIPELINE.md` (Foundation-era) governs the promotion mechanics for skills specifically — auto-generated skills cannot enter production without promotion controls (Constitution Article III.12). Self-evolution proposals that touch skills route through both documents, not one instead of the other.

## Relationship to Governance Core

Once Governance Core exists (Phase 3), a self-evolution proposal that would change an action's class, a policy rule, or a capability scope is itself a Class C request through the normal Policy Engine and Approval Service — self-evolution does not get a side channel around Governance just because the proposer is IIOS improving itself.

## Status

Not activated. `MASTER_IMPLEMENTATION_PROGRAM.md` Phase 11 requires Phase 3 through Phase 10 substantially complete before this loop may run, and even then requires explicit Owner authorization to begin.
