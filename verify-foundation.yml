from pathlib import Path
import json
import re
import sys

try:
    event = json.load(sys.stdin)
except Exception:
    print("IIOS guard could not parse hook input", file=sys.stderr)
    sys.exit(2)

tool = event.get("tool_name", "")
data = event.get("tool_input") or {}
root = Path(event.get("cwd") or ".").resolve()

protected = [
    (root / "docs" / "00_MASTER_CHARTER.md").resolve(),
    (root / "docs" / "01_CONSTITUTION.md").resolve(),
    (root / "governance" / "invariant-kernel").resolve(),
]

def target_path():
    raw = data.get("file_path") or data.get("path")
    if not raw:
        return None
    p = Path(raw)
    return (p if p.is_absolute() else root / p).resolve()

if tool in {"Edit", "Write"}:
    target = target_path()
    if target:
        for item in protected:
            if target == item or item in target.parents:
                print(f"Blocked: protected IIOS authority path: {target}", file=sys.stderr)
                sys.exit(2)

if tool == "Bash":
    command = str(data.get("command", ""))
    patterns = [
        r"(^|[;&|]\s*)rm\s+-rf\b",
        r"\bgit\s+push\s+.*--force\b",
        r"\bterraform\s+apply\b",
        r"\bkubectl\s+(apply|delete|edit|patch)\b",
        r"\bdocker\s+push\b",
        r"\b(gh\s+pr\s+merge|gh\s+repo\s+delete)\b",
    ]
    if any(re.search(pattern, command, flags=re.I) for pattern in patterns):
        print(f"Blocked by IIOS PreToolUse guard: {command}", file=sys.stderr)
        sys.exit(2)

sys.exit(0)
