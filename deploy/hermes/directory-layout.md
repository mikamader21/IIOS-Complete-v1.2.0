# Hermes directory layout

Target tree on the VPS, created by `scripts/bootstrap-directories.sh`. All paths owned `hermes:hermes` unless noted.

```text
/opt/hermes/
  core/
    compose/                 0750  — docker-compose.yml, pinned image tags, no secrets
    secrets/                 0700  — .env (git-ignored, 0600, real values only on the host)
  profiles/
    <profile>/               0750  — one directory per Hermes profile
      workspace/              0750  — terminal.cwd target for this profile
      state/                  0750  — Hermes profile state (sessions, skills, cron)
  backups/                   0750  — local staging before external/encrypted sync
  logs/                      0750  — journald covers systemd units; this holds anything
                                      a container writes outside the Docker log driver
```

Rules:

- No path under `/opt/hermes/` is world-readable or group-writable by a group other than `hermes`.
- `core/secrets/` is `0700` — even the `hermes` group (if one existed beyond the single user) cannot list it.
- A profile's Compose service bind-mounts only its own `profiles/<profile>/` subtree, never `core/secrets/` and never another profile's directory (`docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md`, decision 6).
- Nothing under `/opt/hermes/` is owned by `root` except the directory itself if created by the provisioning script before `chown` — the bootstrap script chowns immediately after creation.
