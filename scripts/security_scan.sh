#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if [ -f ".venv/bin/activate" ]; then
    # Linux / macOS
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    # Windows (Git Bash)
    source .venv/Scripts/activate
fi

require_tool() {
    local tool_name="$1"
    local install_hint="$2"
    if ! command -v "$tool_name" >/dev/null 2>&1; then
        echo "ERROR: Missing required tool '$tool_name'. $install_hint" >&2
        exit 1
    fi
}

echo "==> Running repository security checks"

require_tool semgrep "Install it with 'pip install -e .[dev]' or 'pip install semgrep'."
require_tool gitleaks "Install it from https://github.com/gitleaks/gitleaks/releases or your package manager."
require_tool trivy "Install it from https://trivy.dev/latest/getting-started/installation/."

echo "[1/5] semgrep"
semgrep --config auto --error --exclude .venv --exclude logs --exclude build --exclude dist .

echo "[2/5] gitleaks"
gitleaks detect --source . --no-banner --redact --exit-code 1

echo "[3/5] trivy"
trivy fs --scanners vuln,secret,misconfig --skip-dirs .venv --skip-dirs logs --exit-code 1 --no-progress .

echo "[4/5] bandit"
if command -v bandit >/dev/null 2>&1; then
    bandit -q -r aws_mcp main.py
else
    echo "WARNING: bandit not installed; skipping. Install with 'pip install -e .[dev]'." >&2
fi

echo "[5/5] pip-audit"
if command -v pip-audit >/dev/null 2>&1; then
    pip-audit
else
    echo "WARNING: pip-audit not installed; skipping. Install with 'pip install -e .[dev]'." >&2
fi

echo "==> Security checks completed successfully"