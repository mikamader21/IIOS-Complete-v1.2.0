# ADR-0007 — Concrete Invariant Kernel

**Status:** Proposed for Owner ratification  
**Date:** 22 July 2026

## Decision

Define the Invariant Kernel as a machine-readable, versioned and checksum-verified policy bundle in `governance/invariant-kernel/`.

## Controls

- deny-by-default and fail-closed;
- read-only to runtimes;
- protected branch/path review;
- checksum validation at build/startup;
- Owner ratification metadata;
- no self-modification or autonomous promotion.

## Consequences

The Kernel becomes testable and deterministic. A checksum detects changes but does not replace authenticated Git review or Owner approval.
