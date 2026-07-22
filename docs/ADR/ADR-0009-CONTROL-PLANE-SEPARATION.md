# ADR-0009 — Governance, Orchestrator and Audit Separation

**Status:** Proposed for Owner ratification  
**Date:** 22 July 2026

## Decision

The Orchestrator is subordinate to Governance/Policy. Audit Authority is independent: it receives evidence from execution and can request block/escalation through Governance. It is not the Orchestrator's command parent and is not a peer that can be bypassed.

## Reason

This avoids both a misleading linear hierarchy and a control plane where execution and audit are indistinguishable peers.
