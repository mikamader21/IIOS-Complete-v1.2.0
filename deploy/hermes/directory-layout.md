# Hermes directory layout

Target tree on the VPS, created by `scripts/bootstrap-directories.sh`. All paths owned `hermes:hermes` unless noted. Corrected for the single-container, multi-profile topology (`docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` Amendment 2) — an earlier draft used one directory tree per profile, matching a one-container-per-profile design that has been reversed.

```text
/opt/hermes/
  core/
    compose/                 0750  — docker-compose.yml (pinned by digest), no secrets
    secrets/                 0700  — .env (git-ignored, 0600, container-level flags only —
                                      see secrets/README.md; NOT Hermes' own secrets)
  data/                      0750  — the ONE shared Hermes HERMES_HOME, bind-mounted to
                                      /opt/data inside the container. Contains, once
                                      populated by Hermes itself: config.yaml, .env
                                      (Hermes' own secrets — see secrets/README.md),
                                      SOUL.md, sessions/, memories/, skills/, home/,
                                      cron/, hooks/, logs/gateways/<profile>/, skins/,
                                      and profiles/<name>/ for every named profile
                                      (onyx first; ict-trading and others are future).
  backups/                  0750  — tar.gz snapshots of data/, staged locally before
                                      external/encrypted sync
  logs/                      0750  — THIS package's own wrapper-script logs (backup and
                                      health-check run output). Hermes' own gateway logs
                                      live inside data/logs/gateways/<profile>/ instead —
                                      do not confuse the two.
```

Rules:

- No path under `/opt/hermes/` is world-readable or group-writable by a group other than `hermes`.
- `core/secrets/` is `0700` — even the `hermes` group (if one existed beyond the single user) cannot list it.
- `data/` is the **single** volume every co-located profile shares (`docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` decision 2, 6). There is no per-profile host directory or per-profile Compose bind mount — profile separation happens inside `data/profiles/<name>/`, at the application layer, not the filesystem-mount layer. **Never bind-mount `data/` into a second container** — the official docs warn explicitly against two Hermes gateway containers sharing one data directory (concurrent-write corruption of session/memory stores).
- Nothing under `/opt/hermes/` is owned by `root` except the directory itself if created by the provisioning script before `chown` — the bootstrap script chowns immediately after creation.
