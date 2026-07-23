# IIOS Model Routing — Functional Roles

**Status:** Specified
**Parent authority:** `docs/06_MODEL_ROUTING.md` (tier/registry mechanics — this document does not replace it), `config/model-registry.json`

## Purpose

`docs/06_MODEL_ROUTING.md` defines *how* IIOS routes by capability tier (0–4) and registry policy. This document defines *functional roles* — what each Brain/Agent asks for by purpose, not by tier or vendor — so a Brain spec (`docs/BRAIN_REGISTRY.md`) can say "strategic reasoning model" without hardcoding a tier number or a provider name. A role maps onto one or more tiers at routing time; the mapping is operational configuration, not constitutional text, exactly like the tier system itself.

## Roles

```text
Strategic reasoning model  — architecture decisions, ambiguous synthesis, high-stakes review
Implementation model       — day-to-day coding, tool use, multi-step agentic work
Fast utility model         — classification, extraction, routine status checks
Research model             — cited multi-source synthesis, longer-context retrieval tasks
Local/private model        — on-premises inference for sensitive corpora, no hosted call
Embeddings model           — vector representations for retrieval (docs/MEMORY_ARCHITECTURE.md)
Vision model                — image/document/chart understanding
```

Indicative mapping to `docs/06_MODEL_ROUTING.md` tiers (informational only, not a hard rule table):

| Role | Typical tier |
|---|---|
| Fast utility | Tier 1 |
| Implementation | Tier 2 |
| Strategic reasoning | Tier 3, occasionally Tier 4 for council review |
| Research | Tier 2–3 depending on synthesis depth |
| Local/private | Tier 0–1, no hosted call |
| Embeddings, Vision | Tier-independent — capability-specific, routed by task type not general reasoning tier |

## Rules

- Use the most economical model that satisfies the task — never default to the most capable role "to be safe."
- Escalate to a higher role only when complexity, risk, or a failed validation justifies it (mirrors `docs/06_MODEL_ROUTING.md` — Routing inputs).
- No model decides authority. A model producing a "strategic reasoning" output is still subject to the Action Classifier and Policy Engine (`docs/21_GOVERNANCE_CORE_SPEC.md`) — role selection is a cost/quality routing concern, not an authorization mechanism.
- No model may modify Governance, the Charter, the Constitution, or the Invariant Kernel, regardless of role.
- Every call records model, version, cost, and result, per `docs/06_MODEL_ROUTING.md` — Required telemetry.
- Roles must remain provider-swappable: a Brain spec referencing "Implementation model" must not need rewriting when the underlying provider/model changes — only `config/model-registry.json` and the tier mapping change.
- **Do not assert a specific model is available or verified unless it has actually been checked.** A role's intended binding may be documented (below) without claiming it is confirmed live.

## Documented intent (not a verified-availability claim)

```text
Strategic reasoning → Claude high-reasoning class
Implementation      → Claude Code / coding-oriented model
Persistent operation → Hermes-routed models (once Phase 6 exists)
```

These lines document *intent* for which family of model a role is expected to draw from — they do not hardcode a specific, time-sensitive model name or version, and they are not a claim that any of this is currently wired up. Concrete, verified model IDs live only in `config/model-registry.json`, per `docs/06_MODEL_ROUTING.md` — Principle.

## Roles not yet in `config/model-registry.json`

`Embeddings model` and `Vision model` have no corresponding entries yet — they are specified here for future Brains (e.g. Knowledge Brain's retrieval, a future document/chart-reading capability) but are not routed anywhere today.
