"""Auto Scaling tools: groups, policies, and activities."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_autoscaling_describe_auto_scaling_groups",
    description="List Auto Scaling Groups with their current capacity, health, and instance details.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "auto_scaling_group_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific ASG names (optional — returns all if omitted)",
            },
            "max_records": {
                "type": "integer",
                "description": "Maximum ASGs to return",
            },
        },
    },
    is_read_only=True,
)
async def describe_auto_scaling_groups(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "autoscaling", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "auto_scaling_group_names" in arguments:
            kwargs["AutoScalingGroupNames"] = arguments["auto_scaling_group_names"]
        if "max_records" in arguments:
            kwargs["MaxRecords"] = arguments["max_records"]
        response = client.describe_auto_scaling_groups(**kwargs)
        return response.get("AutoScalingGroups", [])

    groups = await asyncio.to_thread(_execute)
    return json.dumps({"auto_scaling_groups": groups, "count": len(groups)}, default=str)


@tool(
    name="aws_autoscaling_describe_scaling_policies",
    description="List scaling policies for Auto Scaling Groups.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "auto_scaling_group_name": {
                "type": "string",
                "description": "Filter policies by ASG name",
            },
            "policy_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific policy names",
            },
            "policy_types": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["SimpleScaling", "StepScaling", "TargetTrackingScaling", "PredictiveScaling"],
                },
                "description": "Filter by policy type",
            },
        },
    },
    is_read_only=True,
)
async def describe_scaling_policies(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "autoscaling", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "auto_scaling_group_name" in arguments:
            kwargs["AutoScalingGroupName"] = arguments["auto_scaling_group_name"]
        if "policy_names" in arguments:
            kwargs["PolicyNames"] = arguments["policy_names"]
        if "policy_types" in arguments:
            kwargs["PolicyTypes"] = arguments["policy_types"]
        response = client.describe_policies(**kwargs)
        return response.get("ScalingPolicies", [])

    policies = await asyncio.to_thread(_execute)
    return json.dumps({"scaling_policies": policies, "count": len(policies)}, default=str)


@tool(
    name="aws_autoscaling_describe_scaling_activities",
    description="Get recent scaling activities for an Auto Scaling Group (scale-out/in events, failures).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "auto_scaling_group_name": {
                "type": "string",
                "description": "ASG name",
            },
            "max_records": {
                "type": "integer",
                "description": "Maximum activities to return (default: 20)",
            },
        },
        "required": ["auto_scaling_group_name"],
    },
    is_read_only=True,
)
async def describe_scaling_activities(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "autoscaling", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {
            "AutoScalingGroupName": arguments["auto_scaling_group_name"],
            "MaxRecords": arguments.get("max_records", 20),
        }
        response = client.describe_scaling_activities(**kwargs)
        return response.get("Activities", [])

    activities = await asyncio.to_thread(_execute)
    return json.dumps({"activities": activities, "count": len(activities)}, default=str)


@tool(
    name="aws_autoscaling_describe_launch_configurations",
    description="List launch configurations used by Auto Scaling Groups.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "launch_configuration_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific launch configuration names",
            },
            "max_records": {
                "type": "integer",
                "description": "Maximum configurations to return",
            },
        },
    },
    is_read_only=True,
)
async def describe_launch_configurations(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "autoscaling", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "launch_configuration_names" in arguments:
            kwargs["LaunchConfigurationNames"] = arguments["launch_configuration_names"]
        if "max_records" in arguments:
            kwargs["MaxRecords"] = arguments["max_records"]
        response = client.describe_launch_configurations(**kwargs)
        return response.get("LaunchConfigurations", [])

    configs = await asyncio.to_thread(_execute)
    return json.dumps({"launch_configurations": configs, "count": len(configs)}, default=str)
