"""JSONL structured logging configuration.

All logs are emitted in JSON Lines format for structured analysis and monitoring.
Logs are written to both a file and stderr (compatible with MCP stdio transport).
"""
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path


class JsonlFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects (JSONL)."""

    EXTRA_FIELDS = (
        "tool_name",
        "aws_service",
        "aws_operation",
        "aws_profile",
        "aws_region",
        "duration_ms",
        "readonly",
        "dry_run",
        "request_id",
    )

    def format(self, record: logging.LogRecord) -> str:
        entry: dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for field in self.EXTRA_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                entry[field] = value

        if record.exc_info and record.exc_info[1]:
            entry["error"] = str(record.exc_info[1])
            entry["error_type"] = type(record.exc_info[1]).__name__

        return json.dumps(entry, default=str, ensure_ascii=False)


def setup_logging(log_dir: str = "logs", log_level: str = "INFO") -> logging.Logger:
    """Configure structured JSONL logging.

    Args:
        log_dir: Directory for log files.
        log_level: Minimum log level.

    Returns:
        The configured root logger for aws_mcp.
    """
    # Resolve relative paths against the project root (not the cwd,
    # which may differ when launched by Claude Desktop or another host).
    project_root = Path(__file__).resolve().parent.parent
    log_path = Path(log_dir)
    if not log_path.is_absolute():
        log_path = project_root / log_path
    log_path.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("aws_mcp")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logger.handlers.clear()

    formatter = JsonlFormatter()

    # File handler: persistent JSONL log
    file_handler = logging.FileHandler(
        log_path / "aws_mcp.jsonl", encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Stderr handler: visible in MCP host logs (does not interfere with stdio)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)

    return logger
