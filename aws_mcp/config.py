"""Application configuration management."""
import argparse
import logging
from dataclasses import dataclass

logger = logging.getLogger("aws_mcp")


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration."""

    readonly: bool = True
    log_dir: str = "logs"
    log_level: str = "INFO"

    @classmethod
    def from_args(cls) -> "AppConfig":
        """Parse CLI arguments and return configuration."""
        parser = argparse.ArgumentParser(
            description="AWS MCP Server for Claude Desktop"
        )
        mode_group = parser.add_mutually_exclusive_group()
        mode_group.add_argument(
            "--readonly",
            dest="readonly",
            action="store_true",
            default=True,
            help="Run in readonly mode (default): blocks mutating operations and uses DryRun where supported",
        )
        mode_group.add_argument(
            "--write",
            dest="readonly",
            action="store_false",
            help="Allow mutating operations. Use only with trusted AWS profiles and environments.",
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
