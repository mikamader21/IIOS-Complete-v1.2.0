# NEXT

**`HERMES-INSTALL-001` — Install pinned Hermes base on authorized VPS**

`blocked_by_owner_vps_details`. The Owner has authorized VPS purchase and preparation; installation itself waits on: reconciled deployment package merged and CI green (this task), Ubuntu provisioned, the Owner supplying non-secret VPS metadata (IP/hostname, architecture, provider), and confirmed SSH public-key access. Creates the `onyx` profile (per `deploy/hermes/runbooks/INSTALL.md`) but does not activate it.

**`ONYX-CORE-001` — ONYX Executive Observer profile (activation)**

Blocked on `HERMES-INSTALL-001` completed, `hermes doctor` passed, the container healthy, a verified backup baseline, and a real (executed, not conceptual) Governance fail-closed test — tightened from the original dependency list in the topology reconciliation (23 July 2026).

Downstream, per the Owner's explicit sequence: `ONYX-CORE-001` -> `ONYX-GOV-001` (connect ONYX to Governance and Audit) -> `ONYX-BUILD-001` (Developer Brain delegation bridge) -> `ICT-KNOW-001` (reordered) -> `ICT-AGENT-001`.

**`ICT-KNOW-001` — ICT source inventory and canonical knowledge pack**

Reordered after `ONYX-BUILD-001`. Also still blocked on the Owner confirming where the existing ICT source projects/documents live — cannot be scoped until then, independent of the ONYX chain.

**`ICT-AGENT-001` — Hermes ICT Trading read-only profile**

Blocked on `HERMES-DEP-001` (done), `ICT-KNOW-001`, an authorized Hermes installation, and approved Governance tests. `ict-trading` is a future profile inside the same shared Hermes container as `onyx`, not activated by any task so far.

**`CONTROL-UI-001` — IIOS Mission Control MVP**

Blocked on Governance contracts, Hermes contracts, and approved Stitch designs. Must also include a minimal ONYX chat surface once scoped — see `BACKLOG.md` for a flagged naming discrepancy in the Owner's instruction ("CONTROL-UI-BOOT-001") needing confirmation.
