"""ELB v2 tools: Application, Network, and Gateway Load Balancers."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_elbv2_describe_load_balancers",
    description="List ALB, NLB, and Gateway Load Balancers with their DNS names and state.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "load_balancer_arns": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific load balancer ARNs (optional — returns all if omitted)",
            },
            "names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by load balancer names",
            },
        },
    },
    is_read_only=True,
)
async def describe_load_balancers(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "elbv2", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "load_balancer_arns" in arguments:
            kwargs["LoadBalancerArns"] = arguments["load_balancer_arns"]
        if "names" in arguments:
            kwargs["Names"] = arguments["names"]
        response = client.describe_load_balancers(**kwargs)
        return response.get("LoadBalancers", [])

    lbs = await asyncio.to_thread(_execute)
    return json.dumps({"load_balancers": lbs, "count": len(lbs)}, default=str)


@tool(
    name="aws_elbv2_describe_target_groups",
    description="List target groups, optionally filtered by load balancer.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "load_balancer_arn": {
                "type": "string",
                "description": "Filter by load balancer ARN",
            },
            "target_group_arns": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific target group ARNs",
            },
            "names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by target group names",
            },
        },
    },
    is_read_only=True,
)
async def describe_target_groups(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "elbv2", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "load_balancer_arn" in arguments:
            kwargs["LoadBalancerArn"] = arguments["load_balancer_arn"]
        if "target_group_arns" in arguments:
            kwargs["TargetGroupArns"] = arguments["target_group_arns"]
        if "names" in arguments:
            kwargs["Names"] = arguments["names"]
        response = client.describe_target_groups(**kwargs)
        return response.get("TargetGroups", [])

    tgs = await asyncio.to_thread(_execute)
    return json.dumps({"target_groups": tgs, "count": len(tgs)}, default=str)


@tool(
    name="aws_elbv2_describe_target_health",
    description="Get health status of all targets registered in a target group.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "target_group_arn": {
                "type": "string",
                "description": "Target group ARN",
            },
        },
        "required": ["target_group_arn"],
    },
    is_read_only=True,
)
async def describe_target_health(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "elbv2", arguments.get("profile"), arguments.get("region")
        )
        response = client.describe_target_health(
            TargetGroupArn=arguments["target_group_arn"]
        )
        return response.get("TargetHealthDescriptions", [])

    health = await asyncio.to_thread(_execute)
    return json.dumps({"targets": health, "count": len(health)}, default=str)


@tool(
    name="aws_elbv2_describe_listeners",
    description="List listeners for a load balancer (ports, protocols, rules).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "load_balancer_arn": {
                "type": "string",
                "description": "Load balancer ARN",
            },
        },
        "required": ["load_balancer_arn"],
    },
    is_read_only=True,
)
async def describe_listeners(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "elbv2", arguments.get("profile"), arguments.get("region")
        )
        response = client.describe_listeners(
            LoadBalancerArn=arguments["load_balancer_arn"]
        )
        return response.get("Listeners", [])

    listeners = await asyncio.to_thread(_execute)
    return json.dumps({"listeners": listeners, "count": len(listeners)}, default=str)
