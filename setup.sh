#!/usr/bin/env bash
# AWS MCP Server - Setup Script
# Works on Linux (Ubuntu 24.04+), macOS, and Windows (Git Bash / WSL)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== AWS MCP Server Setup ==="

# Detect Python
PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" &>/dev/null; then
        version=$("$candidate" --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 12 ]; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.12+ is required but not found."
    echo "Install it from https://www.python.org/downloads/"
    exit 1
fi

echo "Using Python: $PYTHON ($($PYTHON --version))"

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in .venv ..."
    $PYTHON -m venv .venv
else
    echo "Virtual environment .venv already exists"
fi

# Activate and install
if [ -f ".venv/bin/activate" ]; then
    # Linux / macOS
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    # Windows (Git Bash)
    source .venv/Scripts/activate
else
    echo "ERROR: Could not find venv activation script"
    exit 1
fi

echo "Installing dependencies ..."
pip install --upgrade pip --quiet
if [ "${INSTALL_DEV_TOOLS:-1}" = "1" ]; then
    pip install -e ".[dev]" --quiet
else
    pip install -e . --quiet
fi

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git config core.hooksPath .githooks
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To run the server:"
echo "  .venv/bin/python main.py              # Default safe mode (readonly)"
echo "  .venv/bin/python main.py --write      # Allow mutating operations"
echo ""
echo "Pre-push security hook enabled via .githooks/pre-push"
echo "Set INSTALL_DEV_TOOLS=0 to skip semgrep/bandit/pip-audit installation"
echo ""
echo "See README.md for Claude Desktop configuration."
