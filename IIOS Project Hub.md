# IIOS Invariant Kernel

This directory is the machine-readable baseline for non-negotiable IIOS policy.

- `invariants.json`: deterministic policy statements.
- `manifest.json`: expected SHA-256 and ratification metadata.
- `schema.json`: structural contract.

The checksum detects modification but is not a digital signature. Trust also requires protected branches, reviewed commits, restricted deployment roles and Owner ratification.

Runtime agents receive read-only access. Invalid, missing or mismatched Kernel state must fail closed.
