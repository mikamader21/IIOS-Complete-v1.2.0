# IIOS Infrastructure and Deployment

**Version:** 1.2.0

## Local operator station

Windows 10/11 may run Hermes natively. WSL2 is recommended for POSIX-heavy development or the dashboard embedded terminal, but not mandatory for most Hermes functions.

Suggested local tools:

- Git and private repository;
- Claude Code;
- Obsidian;
- Docker Desktop/Engine;
- Hermes Desktop/CLI;
- WSL2 Ubuntu for Linux parity;
- Tailscale client;
- optional Ollama only for justified local workloads.

## Hermes installation policy

- Verify release and checksum/signature.
- Pin the tested version.
- Run `hermes doctor` after setup/change.
- Keep `HERMES_HOME` backed up separately.
- Use a dedicated lab profile.
- Configure `terminal.backend: docker` for non-trivial commands.
- Do not forward environment variables by default.

## VPS MVP direction

- Ubuntu LTS;
- 4–8 vCPU and 8–16 GB RAM based on browser/concurrency tests;
- encrypted volume and external backup;
- Docker Compose;
- non-root services;
- private access through Tailscale/authenticated tunnel;
- no public database/Redis/Hermes ports;
- reverse proxy only if required;
- separate staging and production secrets.

These are planning ranges, not a vendor quote.

## Services

- Governance API;
- Hermes Core/gateway;
- PostgreSQL/Supabase;
- Control Center;
- audit/telemetry;
- optional worker service;
- backup job.

## Docker distinction

Running Hermes inside Docker isolates the application deployment. Docker terminal backend isolates agent command execution. Use both when appropriate; neither substitutes for the other.

## GPU policy

No mandatory GPU for Foundation/MVP. Add GPU only after benchmarked local-model workload, privacy requirement and total-cost analysis.

## Upgrade policy

Release watch → read notes/security → staging backup → pinned upgrade → tests → observation window → production approval → rollback readiness.
