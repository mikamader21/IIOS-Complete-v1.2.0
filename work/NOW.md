# NOW

**Hermes topology reconciliation — `review`, branch `fix/hermes-upstream-topology`.**

`HERMES-DEP-001` merged to `main` (PR #10, merge commit `fff907f84a5917489c02447965ee78b8ad0ea25c`, CI verified green 5/5). Before any real VPS installation, the Owner ordered a second reconciliation: re-verify the exact upstream Hermes release/Docker-image pin (resolving the Owner's own "v0.18.2 appears latest" observation — a stale/pre-propagation read, not an error; v0.19.0/tag `v2026.7.20`/commit `3ef6bbd201263d354fd83ec55b3c306ded2eb72a` is confirmed current across three independent official sources) and correct the deployment topology from one-container-per-profile to **one container hosting multiple s6-supervised profiles**, matching the product's own current official recommendation.

`docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` updated with the verified pin, the corrected topology, an explicit "Real isolation boundaries" table (co-located-profile separation is application-layer only, not OS/container-layer), and a documented-but-unexercised "Future dedicated-container option" for high-risk profiles — then set to **Ratified** ("for controlled VPS deployment preparation... does not authorize financial execution or unrestricted agent activation").

Every affected file under `deploy/hermes/` was updated to match: Compose template (pinned by digest, no published ports, native healthcheck), `onyx`/`ict-trading` manifests (shared-volume paths), backup script (now a plain host-level tar, no `docker` group needed), health-check script (loops profiles), all five runbooks, `docs/14_ACCEPTANCE_TESTS.md`, `docs/31_HERMES_DEPLOYMENT_PACKAGE.md`.

`BACKLOG.md`: `HERMES-DEP-001` marked `done`; added `HERMES-INSTALL-001` (`blocked_by_owner_vps_details` — the Owner authorized VPS purchase, but installation itself waits on non-secret VPS metadata and confirmed SSH access); tightened `ONYX-CORE-001`'s dependencies (install completed, `hermes doctor` passed, container healthy, backup baseline, real Governance fail-closed test).

**No real VPS was provisioned, connected to, or modified. No script under `deploy/hermes/` was executed against a real host. No profile was activated.** Not marked `done` until merged and CI-verified.
