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
]
errors = []
for rel in required:
    if not (root / rel).exists():
        errors.append(f"missing: {rel}")

if (root / ".hermes.md").exists() or (root / "HERMES.md").exists():
    errors.append("root Hermes context overrides AGENTS.md")

claude = (root / "CLAUDE.md").read_text(encoding="utf-8") if (root / "CLAUDE.md").exists() else ""
if "@AGENTS.md" not in claude:
    errors.append("CLAUDE.md does not import AGENTS.md")

agents = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").exists() else ""
if len(agents) > 20000:
    errors.append("AGENTS.md exceeds 20,000 characters")

for rel in ["config/model-registry.json", ".claude/settings.json"]:
    try:
        json.loads((root / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON in {rel}: {exc}")

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
