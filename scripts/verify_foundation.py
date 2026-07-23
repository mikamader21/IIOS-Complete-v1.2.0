from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
required = [
    "AGENTS.md", "CLAUDE.md", "PROJECT_STATE.md",
    "docs/00_MASTER_CHARTER.md", "docs/01_CONSTITUTION.md",
    "docs/02_SYSTEM_ARCHITECTURE.md", "docs/03_GOVERNANCE_SECURITY.md",
    "docs/18_AUDIT_DISPOSITION.md", "docs/20_OWNER_RATIFICATION.md",
    "config/model-registry.json", ".claude/settings.json",
    ".github/workflows/verify-foundation.yml",
    "governance/invariant-kernel/invariants.json",
    "governance/invariant-kernel/manifest.json",
    ".gitattributes",
    "docs/21_GOVERNANCE_CORE_SPEC.md",
    "docs/22_POLICY_ENGINE_EVALUATION.md",
    "docs/23_CAPABILITY_MODEL.md",
    "docs/24_APPROVAL_MODEL.md",
    "docs/25_AUDIT_EVENT_MODEL.md",
    "docs/26_KILL_SWITCH_SPEC.md",
    "docs/ADR/ADR-0010-GOVERNANCE-CORE-BOUNDARIES.md",
    "governance/schemas/action-request.schema.json",
    "governance/schemas/policy-decision.schema.json",
    "governance/schemas/approval.schema.json",
    "governance/schemas/capability-claims.schema.json",
    "governance/schemas/capability-protected-header.schema.json",
    "governance/schemas/capability-token.schema.json",
    "governance/schemas/audit-event.schema.json",
    "governance/schemas/kill-switch-event.schema.json",
    "docs/ADR/ADR-0011-GOVERNANCE-MVP-OWNER-DECISIONS.md",
]
errors = []
for rel in required:
    if not (root / rel).exists():
        errors.append(f"missing: {rel}")

gitattributes = (root / ".gitattributes").read_text(encoding="utf-8") if (root / ".gitattributes").exists() else ""
if not re.search(r"^governance/invariant-kernel/\*\.json\s+text\s+eol=lf\s*$", gitattributes, flags=re.M):
    errors.append(".gitattributes missing explicit eol=lf rule for governance/invariant-kernel/*.json")

if (root / ".hermes.md").exists() or (root / "HERMES.md").exists():
    errors.append("root Hermes context overrides AGENTS.md")

claude = (root / "CLAUDE.md").read_text(encoding="utf-8") if (root / "CLAUDE.md").exists() else ""
if "@AGENTS.md" not in claude:
    errors.append("CLAUDE.md does not import AGENTS.md")

agents = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").exists() else ""
if len(agents) > 20000:
    errors.append("AGENTS.md exceeds 20,000 characters")

# Structural schema validation only: valid JSON and (for governance/schemas/*)
# a declared Draft 2020-12 $schema. This is NOT full JSON Schema Draft 2020-12
# conformance validation, NOT meta-schema validation, and does NOT check that
# any real instance validates against these schemas. See
# governance/schemas/README.md "Validation scope: what 'verified' means today"
# for the full statement and the future implementation requirement (pinned
# Draft 2020-12 validation library, meta-schema validation, positive/negative
# tests per schema — none added in this change).
json_required = [
    "config/model-registry.json", ".claude/settings.json",
    "governance/schemas/action-request.schema.json",
    "governance/schemas/policy-decision.schema.json",
    "governance/schemas/approval.schema.json",
    "governance/schemas/capability-claims.schema.json",
    "governance/schemas/capability-protected-header.schema.json",
    "governance/schemas/capability-token.schema.json",
    "governance/schemas/audit-event.schema.json",
    "governance/schemas/kill-switch-event.schema.json",
]
schema_files = {f for f in json_required if f.startswith("governance/schemas/")}
for rel in json_required:
    try:
        parsed = json.loads((root / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON in {rel}: {exc}")
        continue
    if rel in schema_files and parsed.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append(f"{rel} does not declare Draft 2020-12 $schema")

for path in root.rglob("*"):
    if path.resolve() == Path(__file__).resolve() or not path.is_file() or path.stat().st_size >= 2_000_000:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        continue
    if re.search(r"(?i)(sk-ant-|sk-or-|api[_-]?key\s*=\s*[^<\s])", text):
        errors.append(f"possible secret in {path.relative_to(root)}")

kernel_check = subprocess.run(
    [sys.executable, str(root / "scripts" / "verify_invariant_kernel.py")],
    capture_output=True, text=True
)
if kernel_check.returncode != 0:
    errors.append(kernel_check.stdout.strip() or kernel_check.stderr.strip() or "Invariant Kernel check failed")

if errors:
    print("\n".join("ERROR: " + error for error in errors))
    sys.exit(1)
print("Foundation verification passed")
