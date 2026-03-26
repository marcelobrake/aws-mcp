#!/usr/bin/env python3
"""AWS MCP Server entry point.

Usage:
    python main.py                  # Normal mode (read + write)
    python main.py --readonly       # Readonly mode (blocks mutations, uses DryRun)
    python main.py --log-level DEBUG
"""
from aws_mcp import run

if __name__ == "__main__":
    run()
