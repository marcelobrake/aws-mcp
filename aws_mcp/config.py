"""Application configuration management."""
import argparse
import logging
from dataclasses import dataclass

logger = logging.getLogger("aws_mcp")


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration."""

    readonly: bool = False
    log_dir: str = "logs"
    log_level: str = "INFO"

    @classmethod
    def from_args(cls) -> "AppConfig":
        """Parse CLI arguments and return configuration."""
        parser = argparse.ArgumentParser(
            description="AWS MCP Server for Claude Desktop"
        )
        parser.add_argument(
            "--readonly",
            action="store_true",
            default=False,
            help="Enable readonly mode: blocks mutating operations, uses DryRun where supported",
        )
        parser.add_argument(
            "--log-dir",
            default="logs",
            help="Directory for JSONL log files (default: logs)",
        )
        parser.add_argument(
            "--log-level",
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Log level (default: INFO)",
        )
        args, _ = parser.parse_known_args()
        return cls(
            readonly=args.readonly,
            log_dir=args.log_dir,
            log_level=args.log_level,
        )


_config: AppConfig | None = None


def init_config() -> AppConfig:
    """Initialize global configuration from CLI arguments."""
    global _config
    _config = AppConfig.from_args()
    return _config


def get_config() -> AppConfig:
    """Get the current application configuration."""
    if _config is None:
        raise RuntimeError("Configuration not initialized. Call init_config() first.")
    return _config
