"""MCP Server implementation for AWS.

Handles tool listing, tool dispatch, error handling, and telemetry integration.
Communicates with Claude Desktop via the MCP stdio transport.
"""
import json
import logging
import time

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

from .config import AppConfig
from .telemetry import trace_tool_call
from .tools import get_all_tools, get_tool_entry, load_all

logger = logging.getLogger("aws_mcp")

server = Server("aws-mcp")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Return all registered tool definitions to the MCP client."""
    return get_all_tools()


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    """Dispatch a tool call to the appropriate handler."""
    args = arguments or {}

    entry = get_tool_entry(name)
    if entry is None:
        error_msg = f"Unknown tool: '{name}'"
        logger.error(error_msg, extra={"tool_name": name})
        return [types.TextContent(type="text", text=json.dumps({"error": error_msg}))]

    trace_attrs = {
        "profile": args.get("profile"),
        "region": args.get("region"),
        "service": args.get("service"),
        "readonly": str(entry.is_read_only),
    }

    with trace_tool_call(name, **trace_attrs):
        start = time.monotonic()
        try:
            result = await entry.handler(args)
            duration_ms = round((time.monotonic() - start) * 1000, 2)

            logger.info(
                f"Tool '{name}' completed successfully",
                extra={
                    "tool_name": name,
                    "duration_ms": duration_ms,
                    "aws_profile": args.get("profile"),
                    "aws_region": args.get("region"),
                },
            )

            return [types.TextContent(type="text", text=result)]

        except Exception as exc:
            duration_ms = round((time.monotonic() - start) * 1000, 2)
            error_msg = f"Tool '{name}' failed: {exc}"

            logger.error(
                error_msg,
                extra={
                    "tool_name": name,
                    "duration_ms": duration_ms,
                    "aws_profile": args.get("profile"),
                    "aws_region": args.get("region"),
                },
                exc_info=True,
            )

            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {"error": str(exc), "tool": name}, default=str
                    ),
                )
            ]


async def serve(config: AppConfig) -> None:
    """Start the MCP server on stdio transport.

    Args:
        config: Application configuration (readonly mode, log settings, etc.).
    """
    load_all()

    logger.info(
        f"AWS MCP Server starting (readonly={config.readonly})",
        extra={"readonly": config.readonly},
    )

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
