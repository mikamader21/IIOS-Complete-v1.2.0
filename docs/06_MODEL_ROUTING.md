# IIOS Model Routing and Capability Registry

**Version:** 1.2.0

## Principle

Models are replaceable providers selected by measurable requirements. Concrete model IDs, availability, prices and verification dates live only in `config/model-registry.json`.

## Routing tiers

- **Tier 0 — No LLM:** rules, calculations, validation, backups, health checks and templated reports.
- **Tier 1 — Economical:** classification, extraction, normalization and low-risk summaries.
- **Tier 2 — Standard agentic:** primary coding, research, tool use and multi-step implementation.
- **Tier 3 — Frontier:** exceptional architecture, ambiguous failures and critical audits.
- **Tier 4 — Review/Council:** independent solution plus verifier/synthesizer when risk justifies additional calls.

## Routing inputs

Action class, complexity, sensitivity, reversibility, uncertainty, latency, expected tokens, remaining budget, provider health, tool/context needs and previous validation failures.

## Registry policy

- Provider/model entries are operational configuration, never constitutional truth.
- Pricing must have source, currency, verification timestamp and effective dates.
- An unverified or stale price cannot be used for an approved budget calculation.
- The registry may name current candidates, but routing code uses stable internal aliases.
- Provider failure retries once only when safe; then downgrade, alternate or pause.
- Budget exhaustion pauses or downgrades; it never bypasses a hard limit.

## Required telemetry

Requested alias, provider/model used, input/output/cache tokens, cost, latency, tools, retries, validation result, task value and correlation ID.

## Promotion

A new default requires benchmark set, cost analysis, safety review, shadow test, rollback and ADR.
