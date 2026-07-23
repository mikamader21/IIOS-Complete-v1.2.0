# IIOS Domain Catalog

**Status:** Specified
**Parent authority:** `OWNER_PROFILE.md`, `MASTER_IMPLEMENTATION_PROGRAM.md`

## Purpose

Enumerate the operational domains IIOS is meant to eventually serve, derived from `OWNER_PROFILE.md` — Primary domains, Objectives, and Related projects. Each domain maps to one or more future Brains (`docs/BRAIN_REGISTRY.md`) and is a planning unit for `MASTER_IMPLEMENTATION_PROGRAM.md` phases, not an active capability.

| Domain | Description | Primary Brain(s) | Status |
|---|---|---|---|
| Institutional / ICT Trading | Chart analysis, bias, liquidity mapping, session/PO3 structure per the Owner's ICT methodology | Trading Brain | not_implemented |
| Prop Firms | Funded-account observability, drawdown/rule tracking, portfolio-of-accounts risk | Prop Firm Brain | not_implemented |
| Risk & Portfolio Management | Cross-account risk aggregation, exposure limits | Risk and Audit Brain | not_implemented |
| Blockchain & Tokenization | On-chain research, stablecoins, CBDCs, audit | Blockchain Brain | not_implemented |
| ISO 20022 | Payment-messaging standard research and mapping | Blockchain Brain, Regulation Brain | not_implemented |
| AML/KYC & Compliance | Regulatory monitoring and compliance research | Regulation Brain | not_implemented |
| LATAM Consulting | Institutional/blockchain consulting engagements | Blockchain Brain, Finance Brain | not_implemented |
| AI & Multi-Agent Systems | IIOS's own build-out (this repository) | Governance Brain, Developer Brain, COO Brain | in_progress (specification only) |
| Enterprise Automation | Workflow/process automation for the Owner's ventures | Developer Brain, COO Brain | not_implemented |
| Health, Training & Performance | Personal health/performance tracking and planning | Health and Performance Brain | not_implemented |
| Gnosis & Philosophical Research | Gnosis and philosophical/spiritual knowledge research | Gnosis Brain | not_implemented |
| Personal Operations | Non-business personal operational support | Personal Operations Brain | not_implemented |
| Finance (general) | Non-trading financial planning/analysis | Finance Brain | not_implemented |
| Knowledge Management | Cross-domain research retrieval and curation | Knowledge Brain | not_implemented |

## Related project mapping

| Project (`OWNER_PROFILE.md`) | Domain(s) served |
|---|---|
| MOYM | Institutional / ICT Trading |
| PropOS | Prop Firms, Risk & Portfolio Management |
| IGNIS | Knowledge Management |
| ONYX-OS | Superseded concept — see `MASTER_IMPLEMENTATION_PROGRAM.md` for the current architecture |
| Control Center | Cross-domain (Owner-facing surface, `docs/11_CONTROL_CENTER_PRD.md`) |
| Blockchain Intelligence Terminal | Blockchain & Tokenization |

## Status discipline

A domain's `Status` column reflects whether any Brain serving it has moved past `specified`/`not_implemented` in `docs/BRAIN_REGISTRY.md`. This catalog is a planning index, not a claim that any domain is operational.
