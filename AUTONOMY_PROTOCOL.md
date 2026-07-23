# IIOS Autonomy Protocol

**Version:** 0.1.0
**Status:** Specified, governs Claude's operating behavior in this repository from Phase 2 onward
**Parent authority:** `docs/00_MASTER_CHARTER.md`, `docs/01_CONSTITUTION.md`, `governance/invariant-kernel/`, `AGENTS.md`

## Purpose

Let Claude select, execute, validate, and deliver the next authorized unit of work in `BACKLOG.md` without requiring a manual, file-by-file prompt from the Owner — while never expanding its own authority, never touching constitutional documents, and never taking an irreversible or financial action without explicit Owner authorization. Autonomy is about *pacing and task selection*, not about *authority*. Nothing in this protocol overrides `docs/01_CONSTITUTION.md` Article IV's action classes or the fail-closed rule in `docs/03_GOVERNANCE_SECURITY.md`.

## Normal cycle

```text
Read state
  → select next authorized task
  → verify dependencies
  → classify risk
  → create branch
  → plan
  → implement or specify
  → test
  → security review
  → documentation review
  → commit
  → push
  → open Pull Request
  → observe CI
  → update work state
  → select next authorized task
```

- **Read state**: `PROJECT_STATE.md`, `work/NOW.md`, `BACKLOG.md`, and any document the selected task's `deliverables` reference.
- **Select next authorized task**: the highest-priority `ready` task in `BACKLOG.md` whose `dependencies` are all `done` and whose `owner_decision_required` is empty or already resolved.
- **Verify dependencies**: confirm every listed dependency task is actually `done`, not just assumed.
- **Classify risk**: map the task to a Constitution Article IV action class (A/B/C/D) and to the risk_class already recorded on the backlog item; a mismatch between the two is itself a reason to stop (see Stop conditions).
- **Plan**: for anything touching more than three files or an architectural decision, this still means using Plan mode per `CLAUDE.md`, not skipping planning — autonomy removes the need to ask permission to plan, not the need to plan.
- **Implement or specify**: code changes are Class B (feature branch, sandboxed); this phase (Phase 2) produces specification and governance artifacts only, per `docs/13_IMPLEMENTATION_ROADMAP.md`-style phased build-out.
- **Test / security review / documentation review**: run the narrow tests relevant to the change, then the broad suite; self-review for security per `.claude/rules/security.md`; confirm documentation matches what was actually built (`AGENTS.md` — Definition of done).
- **Commit / push / open PR**: per the permitted-without-asking list below.
- **Observe CI**: check Ubuntu and Windows workflow results with real evidence before reporting a task complete — never claim a check passed without having read it.
- **Update work state**: move the task in `BACKLOG.md` to `review` or `done` as appropriate, update `work/NOW.md`/`work/NEXT.md`/`work/DONE.md`.
- **Select next authorized task**: loop, without asking the Owner what to do next, as long as an authorized `ready` task remains.

## Claude does not need to ask authorization for

- creating working branches;
- drafting derived documentation;
- creating tests;
- fixing lint or whitespace;
- reversible internal refactors;
- updating state files and the changelog;
- using review subagents;
- making commits;
- publishing branches;
- opening Pull Requests;
- checking CI results;
- deleting branches that have already been merged;
- selecting the next unblocked task from the backlog.

## Claude must stop for

- a change to the Master Charter;
- a change to the Constitution;
- a change to the Invariant Kernel;
- modification of financial permissions;
- credentials or secrets;
- new spend or subscription;
- production deployment;
- a destructive migration;
- a financial operation;
- an irreversible action;
- a merge to `main`, unless expressly authorized for that specific merge;
- a release tag, unless expressly authorized;
- a contradiction between ratified documents;
- a business decision that belongs only to the Owner;
- a high risk not covered by existing policy;
- a real technical blocker (dependency missing, test failing for a reason outside the current task's control, ambiguous spec).

These are hard gates, not judgment calls made lighter by "autonomy." A stop condition firing means: stop, document the exact condition, and wait for the Owner — do not work around it, do not reinterpret it as in-scope, do not proceed on a plausible guess.

## Continuity rule

Claude does not stop after each file. Claude completes one coherent deliverable, validates it, commits, pushes, and opens a PR. Claude asks for intervention only when a stop condition above actually fires — not preemptively, and not out of caution alone once a task is already authorized and `ready`.

## Relationship to documentation vs. implementation status

A document that specifies a Brain, Agent, Skill, or capability is **not** evidence that it is built or running. `docs/BRAIN_REGISTRY.md`, `docs/AGENT_REGISTRY.md`, and `docs/SKILL_CATALOG.md` entries are `specified` / `not_implemented` until a separate, explicitly authorized implementation phase changes that status with running-system evidence (test output, CI logs, a working endpoint) — never by editing a status field alone. See `AGENTS.md` — "Do not interpret documentation status as implementation status."

## Relationship to Governance Core

This protocol governs Claude's own pacing inside this repository. It does not replace, pre-empt, or substitute for the Governance Core specified in `docs/21_GOVERNANCE_CORE_SPEC.md` through `docs/26_KILL_SWITCH_SPEC.md` — when Governance Core is implemented (Phase 3), any action it classifies as B/C/D is subject to its Policy Engine, Approval Service, and Capability model, in addition to (not instead of) this protocol's stop conditions.
