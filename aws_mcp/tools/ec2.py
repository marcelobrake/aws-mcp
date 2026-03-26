"""EC2 tools: instance management, security groups, and more."""
import asyncio
import json
import logging

from ..aws_client import get_client
from ..config import get_config
from . import COMMON_PROPERTIES, tool

logger = logging.getLogger("aws_mcp")


@tool(
    name="aws_ec2_describe_instances",
    description=(
        "Describe EC2 instances. Filter by instance IDs, state, tags, or custom filters. "
        "Returns instance details including ID, type, state, IPs, and tags."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "instance_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by specific instance IDs",
            },
            "filters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Name": {"type": "string"},
                        "Values": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["Name", "Values"],
                },
                "description": (
                    "EC2 API filters, e.g. "
                    "[{\"Name\": \"instance-state-name\", \"Values\": [\"running\"]}]"
                ),
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum instances to return (default: all)",
            },
        },
    },
    is_read_only=True,
)
async def describe_instances(arguments: dict) -> str:
    def _execute():
        client = get_client("ec2", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "instance_ids" in arguments:
            kwargs["InstanceIds"] = arguments["instance_ids"]
        if "filters" in arguments:
            kwargs["Filters"] = arguments["filters"]
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.describe_instances(**kwargs)
        instances = [
            inst
            for res in response.get("Reservations", [])
            for inst in res.get("Instances", [])
        ]
        return instances

    instances = await asyncio.to_thread(_execute)
    return json.dumps({"instances": instances, "count": len(instances)}, default=str)


@tool(
    name="aws_ec2_describe_security_groups",
    description=(
        "Describe EC2 security groups. Filter by group IDs, names, or VPC."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "group_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Security group IDs to describe",
            },
            "filters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Name": {"type": "string"},
                        "Values": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["Name", "Values"],
                },
                "description": "EC2 API filters for security groups",
            },
        },
    },
    is_read_only=True,
)
async def describe_security_groups(arguments: dict) -> str:
    def _execute():
        client = get_client("ec2", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "group_ids" in arguments:
            kwargs["GroupIds"] = arguments["group_ids"]
        if "filters" in arguments:
            kwargs["Filters"] = arguments["filters"]

        response = client.describe_security_groups(**kwargs)
        groups = response.get("SecurityGroups", [])
        return groups

    groups = await asyncio.to_thread(_execute)
    return json.dumps({"security_groups": groups, "count": len(groups)}, default=str)


@tool(
    name="aws_ec2_manage_instances",
    description=(
        "Start, stop, or reboot EC2 instances. "
        "In --readonly mode, this executes with DryRun=True to validate "
        "permissions without making changes."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "instance_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Instance IDs to act on",
            },
            "action": {
                "type": "string",
                "enum": ["start", "stop", "reboot"],
                "description": "Action to perform",
            },
        },
        "required": ["instance_ids", "action"],
    },
    is_read_only=False,
)
async def manage_instances(arguments: dict) -> str:
    config = get_config()
    action = arguments["action"]
    instance_ids = arguments["instance_ids"]

    def _execute():
        client = get_client("ec2", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {"InstanceIds": instance_ids}

        if config.readonly:
            kwargs["DryRun"] = True

        method_map = {
            "start": client.start_instances,
            "stop": client.stop_instances,
            "reboot": client.reboot_instances,
        }

        method = method_map.get(action)
        if not method:
            return {"error": f"Unknown action: {action}. Use start, stop, or reboot."}

        try:
            response = method(**kwargs)
            response.pop("ResponseMetadata", None)
            if config.readonly:
                return {
                    "dry_run": True,
                    "message": f"DryRun succeeded: '{action}' on {instance_ids} would be allowed",
                    "response": response,
                }
            return response
        except client.exceptions.ClientError as e:
            if "DryRunOperation" in str(e):
                return {
                    "dry_run": True,
                    "message": f"DryRun succeeded: '{action}' on {instance_ids} would be allowed",
                }
            raise

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
