# GitHub Repository Controls

**Version:** 1.2.0

## Required branch protection

Configure the `main` branch in GitHub UI:

- require a pull request before merging;
- require the `verify` job from **Verify IIOS Foundation**;
- require conversation resolution;
- block force pushes and branch deletion;
- require linear history if compatible with the team's workflow;
- restrict direct pushes to the Owner or approved maintainers.

Branch protection is a GitHub repository setting and cannot be guaranteed by a file committed inside the repository alone.

## Protected authority paths

Changes to these paths require explicit Owner review:

- `docs/00_MASTER_CHARTER.md`
- `docs/01_CONSTITUTION.md`
- `governance/invariant-kernel/**`
- `docs/ADR/**`
- `.claude/settings.json`
- `.github/workflows/**`

Add a valid `.github/CODEOWNERS` only after replacing the Owner placeholder with the real GitHub handle.

## Evidence

After configuration, capture:

- green workflow run;
- branch-rule screen;
- pull request showing required check;
- failed test demonstrating merge block.
