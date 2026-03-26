"""ECS tools: clusters, services, and tasks."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_ecs_list_clusters",
    description="List ECS clusters in the account/region.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
        },
    },
    is_read_only=True,
)
async def list_clusters(arguments: dict) -> str:
    def _execute():
        client = get_client("ecs", arguments.get("profile"), arguments.get("region"))
        response = client.list_clusters()
        return response.get("clusterArns", [])

    arns = await asyncio.to_thread(_execute)
    return json.dumps({"cluster_arns": arns, "count": len(arns)}, default=str)


@tool(
    name="aws_ecs_describe_clusters",
    description="Get detailed information about one or more ECS clusters.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "clusters": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Cluster names or ARNs to describe",
            },
        },
        "required": ["clusters"],
    },
    is_read_only=True,
)
async def describe_clusters(arguments: dict) -> str:
    def _execute():
        client = get_client("ecs", arguments.get("profile"), arguments.get("region"))
        response = client.describe_clusters(
            clusters=arguments["clusters"],
            include=["STATISTICS", "TAGS"],
        )
        return response.get("clusters", [])

    clusters = await asyncio.to_thread(_execute)
    return json.dumps({"clusters": clusters, "count": len(clusters)}, default=str)


@tool(
    name="aws_ecs_list_services",
    description="List ECS services in a cluster.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "cluster": {
                "type": "string",
                "description": "Cluster name or ARN",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of services to return",
            },
        },
        "required": ["cluster"],
    },
    is_read_only=True,
)
async def list_services(arguments: dict) -> str:
    def _execute():
        client = get_client("ecs", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {"cluster": arguments["cluster"]}
        if "max_results" in arguments:
            kwargs["maxResults"] = arguments["max_results"]

        response = client.list_services(**kwargs)
        return response.get("serviceArns", [])

    arns = await asyncio.to_thread(_execute)
    return json.dumps({"service_arns": arns, "count": len(arns)}, default=str)


@tool(
    name="aws_ecs_describe_services",
    description="Get detailed information about ECS services including deployments and events.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "cluster": {
                "type": "string",
                "description": "Cluster name or ARN",
            },
            "services": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Service names or ARNs (max 10)",
            },
        },
        "required": ["cluster", "services"],
    },
    is_read_only=True,
)
async def describe_services(arguments: dict) -> str:
    def _execute():
        client = get_client("ecs", arguments.get("profile"), arguments.get("region"))
        response = client.describe_services(
            cluster=arguments["cluster"],
            services=arguments["services"],
        )
        return response.get("services", [])

    services = await asyncio.to_thread(_execute)
    return json.dumps({"services": services, "count": len(services)}, default=str)


@tool(
    name="aws_ecs_list_tasks",
    description="List ECS tasks in a cluster with optional service or status filter.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "cluster": {
                "type": "string",
                "description": "Cluster name or ARN",
            },
            "service_name": {
                "type": "string",
                "description": "Filter by service name",
            },
            "desired_status": {
                "type": "string",
                "enum": ["RUNNING", "PENDING", "STOPPED"],
                "description": "Filter by task status",
            },
        },
        "required": ["cluster"],
    },
    is_read_only=True,
)
async def list_tasks(arguments: dict) -> str:
    def _execute():
        client = get_client("ecs", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {"cluster": arguments["cluster"]}
        if "service_name" in arguments:
            kwargs["serviceName"] = arguments["service_name"]
        if "desired_status" in arguments:
            kwargs["desiredStatus"] = arguments["desired_status"]

        response = client.list_tasks(**kwargs)
        return response.get("taskArns", [])

    arns = await asyncio.to_thread(_execute)
    return json.dumps({"task_arns": arns, "count": len(arns)}, default=str)


@tool(
    name="aws_ecs_describe_tasks",
    description="Get detailed information about ECS tasks.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "cluster": {
                "type": "string",
                "description": "Cluster name or ARN",
            },
            "tasks": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Task IDs or ARNs to describe",
            },
        },
        "required": ["cluster", "tasks"],
    },
    is_read_only=True,
)
async def describe_tasks(arguments: dict) -> str:
    def _execute():
        client = get_client("ecs", arguments.get("profile"), arguments.get("region"))
        response = client.describe_tasks(
            cluster=arguments["cluster"],
            tasks=arguments["tasks"],
        )
        return response.get("tasks", [])

    tasks = await asyncio.to_thread(_execute)
    return json.dumps({"tasks": tasks, "count": len(tasks)}, default=str)
