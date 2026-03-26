"""ElastiCache tools: Redis, Memcached clusters, and replication groups."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_elasticache_describe_cache_clusters",
    description=(
        "Describe ElastiCache clusters (Redis/Memcached). Returns engine, "
        "node type, status, endpoint, and configuration."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "cache_cluster_id": {
                "type": "string",
                "description": "Specific cluster ID to describe (optional)",
            },
            "show_cache_node_info": {
                "type": "boolean",
                "description": "Include individual cache node details (default: true)",
            },
            "max_records": {
                "type": "integer",
                "description": "Maximum clusters to return",
            },
        },
    },
    is_read_only=True,
)
async def describe_cache_clusters(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "elasticache", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {
            "ShowCacheNodeInfo": arguments.get("show_cache_node_info", True),
        }
        if "cache_cluster_id" in arguments:
            kwargs["CacheClusterId"] = arguments["cache_cluster_id"]
        if "max_records" in arguments:
            kwargs["MaxRecords"] = arguments["max_records"]

        response = client.describe_cache_clusters(**kwargs)
        return response.get("CacheClusters", [])

    clusters = await asyncio.to_thread(_execute)
    return json.dumps(
        {"cache_clusters": clusters, "count": len(clusters)}, default=str
    )


@tool(
    name="aws_elasticache_describe_replication_groups",
    description=(
        "Describe ElastiCache Redis replication groups (clusters with replicas). "
        "Returns primary/replica endpoints, node groups, and failover settings."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "replication_group_id": {
                "type": "string",
                "description": "Specific replication group ID (optional)",
            },
            "max_records": {
                "type": "integer",
                "description": "Maximum groups to return",
            },
        },
    },
    is_read_only=True,
)
async def describe_replication_groups(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "elasticache", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "replication_group_id" in arguments:
            kwargs["ReplicationGroupId"] = arguments["replication_group_id"]
        if "max_records" in arguments:
            kwargs["MaxRecords"] = arguments["max_records"]

        response = client.describe_replication_groups(**kwargs)
        return response.get("ReplicationGroups", [])

    groups = await asyncio.to_thread(_execute)
    return json.dumps(
        {"replication_groups": groups, "count": len(groups)}, default=str
    )


@tool(
    name="aws_elasticache_describe_serverless_caches",
    description="Describe ElastiCache Serverless caches (Redis/Memcached serverless).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "serverless_cache_name": {
                "type": "string",
                "description": "Specific serverless cache name (optional)",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum caches to return",
            },
        },
    },
    is_read_only=True,
)
async def describe_serverless_caches(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "elasticache", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "serverless_cache_name" in arguments:
            kwargs["ServerlessCacheName"] = arguments["serverless_cache_name"]
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        try:
            response = client.describe_serverless_caches(**kwargs)
            return response.get("ServerlessCaches", [])
        except client.exceptions.ClientError as e:
            if "InvalidParameterValue" in str(e):
                return []
            raise

    caches = await asyncio.to_thread(_execute)
    return json.dumps(
        {"serverless_caches": caches, "count": len(caches)}, default=str
    )


@tool(
    name="aws_elasticache_describe_events",
    description="Get recent ElastiCache events (maintenance, failover, scaling, etc.).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "source_identifier": {
                "type": "string",
                "description": "Filter by cluster/replication group ID",
            },
            "source_type": {
                "type": "string",
                "enum": [
                    "cache-cluster",
                    "cache-parameter-group",
                    "cache-security-group",
                    "cache-subnet-group",
                    "replication-group",
                    "serverless-cache",
                ],
                "description": "Filter by source type",
            },
            "duration": {
                "type": "integer",
                "description": "Events from the last N minutes (default: 60)",
            },
            "max_records": {
                "type": "integer",
                "description": "Maximum events to return",
            },
        },
    },
    is_read_only=True,
)
async def describe_events(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "elasticache", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {"Duration": arguments.get("duration", 60)}
        if "source_identifier" in arguments:
            kwargs["SourceIdentifier"] = arguments["source_identifier"]
        if "source_type" in arguments:
            kwargs["SourceType"] = arguments["source_type"]
        if "max_records" in arguments:
            kwargs["MaxRecords"] = arguments["max_records"]

        response = client.describe_events(**kwargs)
        return response.get("Events", [])

    events = await asyncio.to_thread(_execute)
    return json.dumps({"events": events, "count": len(events)}, default=str)
