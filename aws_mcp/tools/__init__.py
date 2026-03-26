"""Tool registry for AWS MCP Server.

Each tool module uses the @tool decorator to self-register.
Call load_all() once at startup to import every module and populate the registry.
"""
import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

import mcp.types as types

logger = logging.getLogger("aws_mcp")

# Common input properties shared by most tools
COMMON_PROPERTIES: dict[str, Any] = {
    "profile": {
        "type": "string",
        "description": "AWS profile name from ~/.aws/config (e.g., 'default', 'production')",
    },
    "region": {
        "type": "string",
        "description": "AWS region override (e.g., 'us-east-1', 'sa-east-1')",
    },
}


@dataclass
class ToolEntry:
    """A registered tool with its MCP definition and handler."""

    definition: types.Tool
    handler: Callable[..., Awaitable[str]]
    is_read_only: bool


_registry: dict[str, ToolEntry] = {}


def tool(
    name: str,
    description: str,
    input_schema: dict,
    is_read_only: bool = True,
):
    """Decorator that registers an async handler as an MCP tool.

    Args:
        name: Unique tool name (e.g., "aws_ec2_describe_instances").
        description: Human-readable description shown to Claude.
        input_schema: JSON Schema for the tool's input arguments.
        is_read_only: True if this tool never mutates AWS state.
    """

    def decorator(func: Callable[..., Awaitable[str]]):
        _registry[name] = ToolEntry(
            definition=types.Tool(
                name=name,
                description=description,
                inputSchema=input_schema,
            ),
            handler=func,
            is_read_only=is_read_only,
        )
        return func

    return decorator


def get_all_tools() -> list[types.Tool]:
    """Return MCP definitions for all registered tools."""
    return [entry.definition for entry in _registry.values()]


def get_tool_entry(name: str) -> ToolEntry | None:
    """Look up a tool registration by name."""
    return _registry.get(name)


def load_all() -> None:
    """Import every tool module to trigger @tool registration."""
    from . import (  # noqa: F401
        acm,
        apigateway,
        athena,
        autoscaling,
        backup,
        cloudformation,
        cloudfront,
        cloudtrail,
        cloudwatch,
        codebuild,
        codedeploy,
        codepipeline,
        cognito,
        cost_explorer,
        documentdb,
        dynamodb,
        ec2,
        ecr,
        ecs,
        efs,
        eks,
        elasticache,
        elbv2,
        emr,
        eventbridge,
        firehose,
        general,
        glue,
        guardduty,
        iam,
        kinesis,
        kms,
        lakeformation,
        lambda_tool,
        memorydb,
        mwaa,
        opensearch,
        organizations,
        profiles,
        rds,
        redshift,
        resourcegroups,
        route53,
        s3,
        sagemaker,
        secretsmanager,
        securityhub,
        ses,
        sns,
        sqs,
        ssm,
        stepfunctions,
        vpc,
        wafv2,
    )

    logger.info(
        f"Loaded {len(_registry)} tools",
        extra={"tool_name": "registry"},
    )
