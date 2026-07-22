# IIOS Cost Governance

**Version:** 1.0.0

## Principle

Costs are operational data, not static assumptions. Every call is attributable to task, model, profile, workflow and domain.

## Hard controls

- daily and monthly spend caps;
- per-task token/cost limit;
- retry and delegation limit;
- concurrency limit;
- browser/runtime timeout;
- alert thresholds;
- provider-level limit where available;
- kill/disable on anomalous spend.

## Required cost event

Timestamp, provider, requested model, actual model, input/output/cache tokens, tool/service cost, task ID, workflow, domain, profile, retries, validation status and value category.

## Routing economics

1. Use no LLM when code suffices.
2. Use low-cost model for extraction/classification.
3. Use Sonnet-class for main work.
4. Escalate to Fable only from complexity/risk/failed validation.
5. Multi-model review only when expected value exceeds additional cost.

## Pricing registry

Store provider prices with source URL, effective date, currency, units and expiry/review date. Never copy prices into Constitution.

## Budget scenarios

Before implementation, calculate laboratory, hybrid MVP and personal production using actual provider quotes and three usage levels. NotebookLM estimates are research inputs only.

## KPIs

Cost/task, cost/accepted result, tokens/accepted result, cache hit rate, retries, escalations, duplicate work, model mix, domain spend and forecast variance.
