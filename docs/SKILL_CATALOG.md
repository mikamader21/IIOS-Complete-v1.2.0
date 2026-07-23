# IIOS Skill Catalog

**Status:** Cataloged — no skill below is implemented
**Parent authority:** `docs/BRAIN_REGISTRY.md`, `docs/AGENT_REGISTRY.md`

## Purpose

Catalog the skills IIOS Brains/Agents will eventually use, one representative entry per required category. This is a catalog, not an implementation — no skill file exists yet. Additional skills within a category may be proposed later (`AUTONOMY_PROTOCOL.md` permits drafting derived documentation without asking).

## Fields

`skill_id`, `version`, `owner_brain`, `purpose`, `inputs`, `outputs`, `tools`, `prerequisites`, `risks`, `tests`, `status` (`cataloged` for all entries below — no skill has moved to `implemented`).

---

```text
skill_id: SKILL-GOV-POLICY-EVAL
category: governance
version: 0.1.0 (cataloged)
owner_brain: BRAIN-GOVERNANCE
purpose: Evaluate a candidate policy bundle against the mandatory test suite.
inputs: Candidate policy bundle, Invariant Kernel.
outputs: Pass/fail report with reason codes.
tools: Policy bundle test harness (not yet implemented).
prerequisites: Governance Core Phase 3 implemented.
risks: False pass could let an unsafe policy version activate.
tests: docs/22_POLICY_ENGINE_EVALUATION.md mandatory test suite.
status: cataloged
```

```text
skill_id: SKILL-ENG-IMPLEMENT-CHANGE
category: software engineering
version: 0.1.0 (cataloged)
owner_brain: BRAIN-DEVELOPER
purpose: Implement a scoped code/documentation change on a feature branch.
inputs: BACKLOG.md task, existing codebase.
outputs: Diff, PR.
tools: Claude Code, Git.
prerequisites: Task is `ready` with resolved dependencies.
risks: Scope creep beyond the task's stated deliverables.
tests: Narrow tests for the change, then broad suite.
status: cataloged
```

```text
skill_id: SKILL-TEST-WRITE-RUN
category: testing
version: 0.1.0 (cataloged)
owner_brain: BRAIN-DEVELOPER
purpose: Author and execute tests for a change.
inputs: Code diff, acceptance criteria.
outputs: Test files, pass/fail results.
tools: Test runners, CI.
prerequisites: None.
risks: Weakening an existing test to force a pass.
tests: Self-verifying (tests testing tests are out of scope; CI is the check).
status: cataloged
```

```text
skill_id: SKILL-SEC-REVIEW
category: cybersecurity
version: 0.1.0 (cataloged)
owner_brain: BRAIN-RISK-AUDIT
purpose: Review a change for security findings before merge.
inputs: PR diff, `.claude/rules/security.md`.
outputs: Findings report.
tools: Static analysis (not yet implemented).
prerequisites: None.
risks: Missed finding due to shallow review depth.
tests: No Critical/High finding unresolved at merge time.
status: cataloged
```

```text
skill_id: SKILL-DOC-CONSISTENCY
category: documentation
version: 0.1.0 (cataloged)
owner_brain: BRAIN-DEVELOPER
purpose: Confirm documentation matches implementation for a change.
inputs: PR diff, affected docs.
outputs: Consistency report.
tools: Repository read access.
prerequisites: None.
risks: Documentation claiming implementation status a change did not earn.
tests: docs/14_ACCEPTANCE_TESTS.md, docs/AUTONOMY_ACCEPTANCE_TESTS.md.
status: cataloged
```

```text
skill_id: SKILL-GIT-BRANCH-PR
category: Git/GitHub
version: 0.1.0 (cataloged)
owner_brain: BRAIN-DEVELOPER
purpose: Create branches, commits, and Pull Requests following repository conventions.
inputs: Task scope, commit message conventions.
outputs: Branch, commit(s), PR.
tools: Git, GitHub, GitHub CLI (when available).
prerequisites: None.
risks: Force push or branch deletion without confirming merge status.
tests: `git status`/`git diff --check` clean before commit.
status: cataloged
```

```text
skill_id: SKILL-RESEARCH-CITED
category: research
version: 0.1.0 (cataloged)
owner_brain: BRAIN-RESEARCH
purpose: Answer a bounded question with cited, source-attributed findings.
inputs: Research question, allowlisted sources.
outputs: Cited summary with confidence/inference labeling.
tools: Browser/web research (allowlisted).
prerequisites: None.
risks: Treating retrieved content as authoritative instruction.
tests: Every material claim carries a source or inference label.
status: cataloged
```

```text
skill_id: SKILL-KNOW-INGEST
category: knowledge ingestion
version: 0.1.0 (cataloged)
owner_brain: BRAIN-KNOWLEDGE
purpose: Convert a source document into a tagged, provenance-carrying Vault note.
inputs: Source document.
outputs: Vault note draft (not self-approved).
tools: Obsidian.
prerequisites: None.
risks: Losing source provenance during summarization.
tests: Note carries type, authority, date, confidence, sensitivity metadata.
status: cataloged
```

```text
skill_id: SKILL-MEM-RETRIEVE
category: memory retrieval
version: 0.1.0 (cataloged)
owner_brain: BRAIN-KNOWLEDGE
purpose: Retrieve relevant context from Vault/Graphify for a task without loading the
  entire knowledge base.
inputs: Task context, query.
outputs: Scoped relevant notes/graph results.
tools: Graphify.
prerequisites: Graphify index exists (Phase 4).
risks: Treating a derived graph result as authoritative over source.
tests: Every graph result links back to a checkable source.
status: cataloged
```

```text
skill_id: SKILL-ICT-ANALYSIS
category: ICT market analysis
version: 0.1.0 (cataloged)
owner_brain: BRAIN-TRADING
purpose: Produce bias, liquidity, and setup analysis per the Owner's ICT methodology.
inputs: Market data (read-only), symbol/timeframe.
outputs: Bias/setup/entry analysis.
tools: Market data providers (read-only, allowlisted).
prerequisites: Trading domain activated (Phase 8).
risks: Using non-ICT indicators when the Owner's methodology explicitly excludes them
  (OWNER_PROFILE.md).
tests: Analysis structure matches the documented ICT setup components.
status: cataloged
```

```text
skill_id: SKILL-PROPFIRM-DRAWDOWN
category: prop-firm risk
version: 0.1.0 (cataloged)
owner_brain: BRAIN-PROPFIRM
purpose: Monitor and report drawdown/rule-compliance status for a funded account.
inputs: Account data feed (read-only).
outputs: Status report, breach-risk alerts.
tools: MetaApi (read-only, not yet integrated).
prerequisites: Prop-firm domain activated (Phase 8).
risks: Missed alert before a rule breach.
tests: Alert fires before the documented breach threshold, not after.
status: cataloged
```

```text
skill_id: SKILL-CHAIN-ANALYTICS
category: blockchain analytics
version: 0.1.0 (cataloged)
owner_brain: BRAIN-BLOCKCHAIN
purpose: Analyze on-chain data for a research/audit report.
inputs: Blockchain explorer data.
outputs: Analysis report.
tools: Blockchain explorers (not yet integrated).
prerequisites: None.
risks: Misattributing on-chain activity without sufficient evidence.
tests: Findings traceable to specific transactions/addresses cited.
status: cataloged
```

```text
skill_id: SKILL-REG-MONITOR
category: regulatory monitoring
version: 0.1.0 (cataloged)
owner_brain: BRAIN-REGULATION
purpose: Track regulatory changes across monitored jurisdictions.
inputs: Monitored source list.
outputs: Regulatory update digest.
tools: Browser/web research, regulatory databases (not yet integrated).
prerequisites: None.
risks: Presenting a digest as licensed legal advice.
tests: Every digest entry carries jurisdiction, date, and source.
status: cataloged
```

```text
skill_id: SKILL-FIN-MODEL
category: financial modeling
version: 0.1.0 (cataloged)
owner_brain: BRAIN-FINANCE
purpose: Build a financial/cost model or scenario analysis.
inputs: Owner-provided or authorized financial data.
outputs: Model output, scenario report.
tools: Financial modeling tools (not yet implemented).
prerequisites: None.
risks: Presenting a model as personalized investment advice.
tests: Model documents its assumptions explicitly.
status: cataloged
```

```text
skill_id: SKILL-UIUX-COMPONENT
category: UI/UX
version: 0.1.0 (cataloged)
owner_brain: BRAIN-DEVELOPER
purpose: Design/implement a Control Center or dashboard component.
inputs: Design request, docs/11_CONTROL_CENTER_PRD.md UX principles.
outputs: Component implementation or mockup.
tools: Frontend tooling (not yet selected).
prerequisites: None.
risks: Decorative complexity over evidence-first clarity.
tests: Matches docs/11_CONTROL_CENTER_PRD.md UX principles.
status: cataloged
```

```text
skill_id: SKILL-DATA-PIPELINE
category: data engineering
version: 0.1.0 (cataloged)
owner_brain: BRAIN-DEVELOPER
purpose: Implement a data pipeline or schema change.
inputs: Schema/pipeline task.
outputs: Migration/pipeline code.
tools: PostgreSQL/Supabase tooling (not yet integrated).
prerequisites: None.
risks: Destructive migration without backup/rollback plan.
tests: Tested in a non-production environment first.
status: cataloged
```

```text
skill_id: SKILL-AUTOMATION-WORKFLOW
category: automation
version: 0.1.0 (cataloged)
owner_brain: BRAIN-COO
purpose: Define or refine a cross-Brain operational workflow.
inputs: Process description, `docs/WORKFLOW_REGISTRY.md`.
outputs: Workflow specification or refinement.
tools: None beyond documentation tooling.
prerequisites: None.
risks: Automating a step that should remain a human decision.
tests: Workflow's failure behavior and approvals are explicit.
status: cataloged
```

```text
skill_id: SKILL-HEALTH-TRACK
category: health and performance
version: 0.1.0 (cataloged)
owner_brain: BRAIN-HEALTH
purpose: Track/plan training or performance data on explicit Owner authorization.
inputs: Owner-provided data (opt-in only).
outputs: Tracking summary, plan suggestions.
tools: Not yet defined.
prerequisites: Explicit per-instance Owner authorization (OWNER_PROFILE.md — Scope).
risks: Storing health data without authorization.
tests: No data access without a logged authorization event.
status: cataloged
```

```text
skill_id: SKILL-GNOSIS-RESEARCH
category: Gnosis research
version: 0.1.0 (cataloged)
owner_brain: BRAIN-GNOSIS
purpose: Research and synthesize Gnosis/philosophical sources.
inputs: Research question, curated sources.
outputs: Synthesis report.
tools: Browser/web research, document readers.
prerequisites: None.
risks: Presenting speculative synthesis as settled fact.
tests: Distinguishes source material from synthesis/inference.
status: cataloged
```
