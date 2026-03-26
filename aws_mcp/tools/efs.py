"""EFS tools: file systems and mount targets."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_efs_describe_file_systems",
    description="List EFS file systems with their size, throughput mode, and lifecycle state.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "file_system_id": {
                "type": "string",
                "description": "Specific file system ID or ARN (optional — returns all if omitted)",
            },
            "max_items": {
                "type": "integer",
                "description": "Maximum file systems to return",
            },
        },
    },
    is_read_only=True,
)
async def describe_file_systems(arguments: dict) -> str:
    def _execute():
        client = get_client("efs", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "file_system_id" in arguments:
            kwargs["FileSystemId"] = arguments["file_system_id"]
        if "max_items" in arguments:
            kwargs["MaxItems"] = arguments["max_items"]
        response = client.describe_file_systems(**kwargs)
        return response.get("FileSystems", [])

    file_systems = await asyncio.to_thread(_execute)
    return json.dumps({"file_systems": file_systems, "count": len(file_systems)}, default=str)


@tool(
    name="aws_efs_describe_mount_targets",
    description="List EFS mount targets for a file system or VPC subnet.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "file_system_id": {
                "type": "string",
                "description": "File system ID to list mount targets for",
            },
            "mount_target_id": {
                "type": "string",
                "description": "Specific mount target ID",
            },
            "vpc_id": {
                "type": "string",
                "description": "Filter by VPC ID",
            },
        },
    },
    is_read_only=True,
)
async def describe_mount_targets(arguments: dict) -> str:
    def _execute():
        client = get_client("efs", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "file_system_id" in arguments:
            kwargs["FileSystemId"] = arguments["file_system_id"]
        if "mount_target_id" in arguments:
            kwargs["MountTargetId"] = arguments["mount_target_id"]
        if "vpc_id" in arguments:
            kwargs["VpcId"] = arguments["vpc_id"]
        response = client.describe_mount_targets(**kwargs)
        return response.get("MountTargets", [])

    targets = await asyncio.to_thread(_execute)
    return json.dumps({"mount_targets": targets, "count": len(targets)}, default=str)


@tool(
    name="aws_efs_describe_access_points",
    description="List EFS access points (application-specific entry points with path and permissions).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "file_system_id": {
                "type": "string",
                "description": "Filter by file system ID",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum access points to return",
            },
        },
    },
    is_read_only=True,
)
async def describe_access_points(arguments: dict) -> str:
    def _execute():
        client = get_client("efs", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "file_system_id" in arguments:
            kwargs["FileSystemId"] = arguments["file_system_id"]
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]
        response = client.describe_access_points(**kwargs)
        return response.get("AccessPoints", [])

    access_points = await asyncio.to_thread(_execute)
    return json.dumps({"access_points": access_points, "count": len(access_points)}, default=str)
