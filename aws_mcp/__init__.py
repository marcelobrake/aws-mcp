"""AWS MCP Server - Model Context Protocol server for AWS services.

Provides Claude Desktop with tools to interact with AWS services
using the machine's configured AWS profiles.
"""
import asyncio

from .config import init_config
from .logging_config import setup_logging
from .server import serve
from .telemetry import init_telemetry


def run() -> None:
    """Application entry point: initialize config, logging, telemetry, and start server."""
    config = init_config()
    logger = setup_logging(config.log_dir, config.log_level)
    init_telemetry()

    logger.info(
        "AWS MCP Server initialized",
        extra={"readonly": config.readonly, "log_level": config.log_level},
    )

    asyncio.run(serve(config))


__all__ = ["run"]
