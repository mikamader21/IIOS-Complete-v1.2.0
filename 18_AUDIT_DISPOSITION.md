# IIOS Skill Evolution and Promotion Pipeline

**Version:** 1.0.0

## Principle

Hermes can create or improve procedural skills, but generation is not authorization. Skills are software/procedure assets governed by promotion stages.

## Lifecycle

```text
Execution trace
→ candidate insight
→ draft skill
→ isolated lab
→ automated tests
→ security/cost review
→ Claude Code implementation review
→ Fable 5 review only if critical
→ Owner/authorized approval
→ signed version
→ staging
→ production
→ monitoring/rollback
```

## Environments

- Draft: generated and untrusted.
- Lab: no production secrets or financial write access.
- Staging: representative data, constrained permissions.
- Production: approved version and manifest only.
- Retired: disabled, archived and traceable.

## Required skill contract

Name, version, owner, purpose, inputs, outputs, preconditions, tools, permissions, data classes, steps, validation, error behavior, retry/time/cost limits, tests, security notes, rollback and changelog.

## Prohibited autoevolution

No autonomous mutation or promotion of:

- Charter/Constitution;
- policy or approval rules;
- financial risk/trading logic;
- secret handling;
- kill switch;
- audit integrity;
- production deployment permissions.

## Runtime safeguards

Only allowlisted signed skills mount in production. Credentials are scoped and read-only where possible. Skill output is validated. Promotion and rollback emit audit events.
