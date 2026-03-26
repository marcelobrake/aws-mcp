"""CodeDeploy tools: applications, deployment groups, and deployments."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_codedeploy_list_applications",
    description="List CodeDeploy application names.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
        },
    },
    is_read_only=True,
)
async def list_applications(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "codedeploy", arguments.get("profile"), arguments.get("region")
        )
        response = client.list_applications()
        return response.get("applications", [])

    apps = await asyncio.to_thread(_execute)
    return json.dumps({"applications": apps, "count": len(apps)}, default=str)


@tool(
    name="aws_codedeploy_list_deployment_groups",
    description="List deployment groups for a CodeDeploy application.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "application_name": {
                "type": "string",
                "description": "CodeDeploy application name",
            },
        },
        "required": ["application_name"],
    },
    is_read_only=True,
)
async def list_deployment_groups(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "codedeploy", arguments.get("profile"), arguments.get("region")
        )
        response = client.list_deployment_groups(
            applicationName=arguments["application_name"]
        )
        return response.get("deploymentGroups", [])

    groups = await asyncio.to_thread(_execute)
    return json.dumps({"deployment_groups": groups, "count": len(groups)}, default=str)


@tool(
    name="aws_codedeploy_list_deployments",
    description="List CodeDeploy deployments, optionally filtered by application and status.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "application_name": {
                "type": "string",
                "description": "Filter by application name",
            },
            "deployment_group_name": {
                "type": "string",
                "description": "Filter by deployment group name",
            },
            "include_only_statuses": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["Created", "Queued", "InProgress", "Baking", "Succeeded", "Failed", "Stopped", "Ready"],
                },
                "description": "Filter by deployment status",
            },
        },
    },
    is_read_only=True,
)
async def list_deployments(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "codedeploy", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "application_name" in arguments:
            kwargs["applicationName"] = arguments["application_name"]
        if "deployment_group_name" in arguments:
            kwargs["deploymentGroupName"] = arguments["deployment_group_name"]
        if "include_only_statuses" in arguments:
            kwargs["includeOnlyStatuses"] = arguments["include_only_statuses"]
        response = client.list_deployments(**kwargs)
        return response.get("deployments", [])

    deployments = await asyncio.to_thread(_execute)
    return json.dumps({"deployments": deployments, "count": len(deployments)}, default=str)


@tool(
    name="aws_codedeploy_get_deployment",
    description="Get full details of a CodeDeploy deployment (status, duration, error info).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "deployment_id": {
                "type": "string",
                "description": "Deployment ID (e.g., d-XXXXXXXXX)",
            },
        },
        "required": ["deployment_id"],
    },
    is_read_only=True,
)
async def get_deployment(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "codedeploy", arguments.get("profile"), arguments.get("region")
        )
        response = client.get_deployment(deploymentId=arguments["deployment_id"])
        return response.get("deploymentInfo", {})

    deployment = await asyncio.to_thread(_execute)
    return json.dumps({"deployment": deployment}, default=str)
