#!/usr/bin/env python3
"""AWS MCP Server entry point.

Usage:
    python main.py                  # Default safe mode (readonly)
    python main.py --readonly       # Explicit readonly mode
    python main.py --write          # Allow mutating operations
    python main.py --log-level DEBUG
"""
from aws_mcp import run

if __name__ == "__main__":
    run()
