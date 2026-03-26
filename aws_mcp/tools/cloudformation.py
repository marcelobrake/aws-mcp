"""CloudFormation tools: stacks, resources, and templates."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_cfn_list_stacks",
    description="List CloudFormation stacks with optional status filter.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "stack_status_filter": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [
                        "CREATE_IN_PROGRESS", "CREATE_FAILED", "CREATE_COMPLETE",
                        "ROLLBACK_IN_PROGRESS", "ROLLBACK_FAILED", "ROLLBACK_COMPLETE",
                        "DELETE_IN_PROGRESS", "DELETE_FAILED",
                        "UPDATE_IN_PROGRESS", "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS",
                        "UPDATE_COMPLETE", "UPDATE_FAILED",
                        "UPDATE_ROLLBACK_IN_PROGRESS", "UPDATE_ROLLBACK_FAILED",
                        "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS",
                        "UPDATE_ROLLBACK_COMPLETE",
                    ],
                },
                "description": "Filter by stack status (default: all active stacks)",
            },
        },
    },
    is_read_only=True,
)
async def list_stacks(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "cloudformation", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "stack_status_filter" in arguments:
            kwargs["StackStatusFilter"] = arguments["stack_status_filter"]

        response = client.list_stacks(**kwargs)
        return response.get("StackSummaries", [])

    stacks = await asyncio.to_thread(_execute)
    return json.dumps({"stacks": stacks, "count": len(stacks)}, default=str)


@tool(
    name="aws_cfn_describe_stacks",
    description="Get detailed info for one or all CloudFormation stacks (parameters, outputs, tags).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "stack_name": {
                "type": "string",
                "description": "Stack name or ID (optional — describes all if omitted)",
            },
        },
    },
    is_read_only=True,
)
async def describe_stacks(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "cloudformation", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "stack_name" in arguments:
            kwargs["StackName"] = arguments["stack_name"]

        response = client.describe_stacks(**kwargs)
        return response.get("Stacks", [])

    stacks = await asyncio.to_thread(_execute)
    return json.dumps({"stacks": stacks, "count": len(stacks)}, default=str)


@tool(
    name="aws_cfn_list_stack_resources",
    description="List all resources in a CloudFormation stack.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "stack_name": {
                "type": "string",
                "description": "Stack name or ID",
            },
        },
        "required": ["stack_name"],
    },
    is_read_only=True,
)
async def list_stack_resources(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "cloudformation", arguments.get("profile"), arguments.get("region")
        )
        response = client.list_stack_resources(
            StackName=arguments["stack_name"]
        )
        return response.get("StackResourceSummaries", [])

    resources = await asyncio.to_thread(_execute)
    return json.dumps(
        {"resources": resources, "count": len(resources)}, default=str
    )


@tool(
    name="aws_cfn_get_template",
    description="Get the CloudFormation template body for a stack.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "stack_name": {
                "type": "string",
                "description": "Stack name or ID",
            },
            "template_stage": {
                "type": "string",
                "enum": ["Original", "Processed"],
                "description": "Template stage: Original or Processed (default: Original)",
            },
        },
        "required": ["stack_name"],
    },
    is_read_only=True,
)
async def get_template(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "cloudformation", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {"StackName": arguments["stack_name"]}
        if "template_stage" in arguments:
            kwargs["TemplateStage"] = arguments["template_stage"]

        response = client.get_template(**kwargs)
        return response.get("TemplateBody", "")

    template = await asyncio.to_thread(_execute)
    if isinstance(template, dict):
        return json.dumps({"template": template}, default=str)
    return json.dumps({"template": template}, default=str)


@tool(
    name="aws_cfn_describe_stack_events",
    description="Get recent events for a CloudFormation stack (useful for debugging deployments).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "stack_name": {
                "type": "string",
                "description": "Stack name or ID",
            },
        },
        "required": ["stack_name"],
    },
    is_read_only=True,
)
async def describe_stack_events(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "cloudformation", arguments.get("profile"), arguments.get("region")
        )
        response = client.describe_stack_events(
            StackName=arguments["stack_name"]
        )
        return response.get("StackEvents", [])

    events = await asyncio.to_thread(_execute)
    return json.dumps({"events": events, "count": len(events)}, default=str)
