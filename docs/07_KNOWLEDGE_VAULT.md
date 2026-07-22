# IIOS Obsidian Knowledge Vault

**Version:** 1.0.0

## Purpose

The Vault is the human-readable institutional memory of IIOS. Obsidian stores Markdown files locally and refreshes when external tools edit them.

## Boundaries

Store research, sources, ideas, decisions, people, entities, project notes, playbooks, reviews and lessons.

Do not store secrets, raw credentials, high-volume logs, transaction state or data requiring database consistency.

## Vault structure

```text
00-Inbox
01-Dashboard
10-Projects
20-Domains
30-Decisions
40-Sources
50-Playbooks
60-People
70-Entities
80-Reviews
90-Archive
_Generated/Graphify
_Templates
```

## Metadata standard

```yaml
---
id: IIOS-DEC-0001
type: decision
domain: architecture
status: proposed
authority: owner
created: 2026-07-21
updated: 2026-07-21
confidence: high
sensitivity: internal
sources: []
---
```

Required fields vary by type, but every note needs ID, type, status, dates, confidence, sensitivity and source linkage where factual.

## Authority levels

- `constitutional`: ratified governed document; normally referenced, not duplicated.
- `approved`: reviewed Owner/authorized decision.
- `reviewed`: checked but non-binding knowledge.
- `draft`: work in progress.
- `generated`: machine-derived, never authoritative.

## Sync and backup

Sync is not backup. Use a one-way backup to a separate destination, version history and periodic restore tests. Git may version suitable Markdown, but sensitive attachments need separate controls.

## Agent access

- Claude/Hermes read only the relevant folders.
- Writes go to Inbox or Draft unless explicitly permitted.
- Agents cannot mark a note `approved` or `constitutional`.
- Generated output goes to `_Generated` or `00-Inbox` for review.
- Deletion and bulk rename require human approval.

## Repository separation

Maintain the Vault as a separate private folder/repository from application code. Link through stable note IDs and URIs, not by nesting Vaults.
