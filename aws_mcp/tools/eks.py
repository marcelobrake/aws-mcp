"""EKS tools: clusters, nodegroups, and Fargate profiles."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_eks_list_clusters",
    description="List EKS clusters in the account/region.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_results": {
                "type": "integer",
                "description": "Maximum clusters to return",
            },
        },
    },
    is_read_only=True,
)
async def list_clusters(arguments: dict) -> str:
    def _execute():
        client = get_client("eks", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "max_results" in arguments:
            kwargs["maxResults"] = arguments["max_results"]

        response = client.list_clusters(**kwargs)
        return response.get("clusters", [])

    clusters = await asyncio.to_thread(_execute)
    return json.dumps({"clusters": clusters, "count": len(clusters)}, default=str)


@tool(
    name="aws_eks_describe_cluster",
    description=(
        "Get detailed EKS cluster info: version, endpoint, VPC config, "
        "logging, status, and platform version."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "name": {
                "type": "string",
                "description": "EKS cluster name",
            },
        },
        "required": ["name"],
    },
    is_read_only=True,
)
async def describe_cluster(arguments: dict) -> str:
    def _execute():
        client = get_client("eks", arguments.get("profile"), arguments.get("region"))
        response = client.describe_cluster(name=arguments["name"])
        return response.get("cluster", {})

    cluster = await asyncio.to_thread(_execute)
    return json.dumps({"cluster": cluster}, default=str)


@tool(
    name="aws_eks_list_nodegroups",
    description="List managed node groups for an EKS cluster.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "cluster_name": {
                "type": "string",
                "description": "EKS cluster name",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum nodegroups to return",
            },
        },
        "required": ["cluster_name"],
    },
    is_read_only=True,
)
async def list_nodegroups(arguments: dict) -> str:
    def _execute():
        client = get_client("eks", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {"clusterName": arguments["cluster_name"]}
        if "max_results" in arguments:
            kwargs["maxResults"] = arguments["max_results"]

        response = client.list_nodegroups(**kwargs)
        return response.get("nodegroups", [])

    nodegroups = await asyncio.to_thread(_execute)
    return json.dumps(
        {"nodegroups": nodegroups, "count": len(nodegroups)}, default=str
    )


@tool(
    name="aws_eks_describe_nodegroup",
    description="Get details for an EKS managed node group.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "cluster_name": {
                "type": "string",
                "description": "EKS cluster name",
            },
            "nodegroup_name": {
                "type": "string",
                "description": "Node group name",
            },
        },
        "required": ["cluster_name", "nodegroup_name"],
    },
    is_read_only=True,
)
async def describe_nodegroup(arguments: dict) -> str:
    def _execute():
        client = get_client("eks", arguments.get("profile"), arguments.get("region"))
        response = client.describe_nodegroup(
            clusterName=arguments["cluster_name"],
            nodegroupName=arguments["nodegroup_name"],
        )
        return response.get("nodegroup", {})

    nodegroup = await asyncio.to_thread(_execute)
    return json.dumps({"nodegroup": nodegroup}, default=str)


@tool(
    name="aws_eks_list_fargate_profiles",
    description="List Fargate profiles for an EKS cluster.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "cluster_name": {
                "type": "string",
                "description": "EKS cluster name",
            },
        },
        "required": ["cluster_name"],
    },
    is_read_only=True,
)
async def list_fargate_profiles(arguments: dict) -> str:
    def _execute():
        client = get_client("eks", arguments.get("profile"), arguments.get("region"))
        response = client.list_fargate_profiles(
            clusterName=arguments["cluster_name"]
        )
        return response.get("fargateProfileNames", [])

    profiles = await asyncio.to_thread(_execute)
    return json.dumps(
        {"fargate_profiles": profiles, "count": len(profiles)}, default=str
    )
