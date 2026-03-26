"""CloudTrail tools: trails, event history, and lookup."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_cloudtrail_describe_trails",
    description="Describe CloudTrail trails in the account.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "trail_name_list": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific trail names or ARNs (optional — returns all if omitted)",
            },
            "include_shadow_trails": {
                "type": "boolean",
                "description": "Include shadow trails from other regions (default: true)",
            },
        },
    },
    is_read_only=True,
)
async def describe_trails(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "cloudtrail", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "trail_name_list" in arguments:
            kwargs["trailNameList"] = arguments["trail_name_list"]
        if "include_shadow_trails" in arguments:
            kwargs["includeShadowTrails"] = arguments["include_shadow_trails"]

        response = client.describe_trails(**kwargs)
        return response.get("trailList", [])

    trails = await asyncio.to_thread(_execute)
    return json.dumps({"trails": trails, "count": len(trails)}, default=str)


@tool(
    name="aws_cloudtrail_get_trail_status",
    description="Get logging status for a CloudTrail trail.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "name": {
                "type": "string",
                "description": "Trail name or ARN",
            },
        },
        "required": ["name"],
    },
    is_read_only=True,
)
async def get_trail_status(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "cloudtrail", arguments.get("profile"), arguments.get("region")
        )
        response = client.get_trail_status(Name=arguments["name"])
        response.pop("ResponseMetadata", None)
        return response

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)


@tool(
    name="aws_cloudtrail_lookup_events",
    description=(
        "Look up recent CloudTrail management events. Filter by event name, "
        "resource type, user name, etc. Returns the last 90 days by default."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "lookup_attributes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "AttributeKey": {
                            "type": "string",
                            "enum": [
                                "EventId", "EventName", "ReadOnly", "Username",
                                "ResourceType", "ResourceName", "EventSource", "AccessKeyId",
                            ],
                        },
                        "AttributeValue": {"type": "string"},
                    },
                    "required": ["AttributeKey", "AttributeValue"],
                },
                "description": "Lookup filters (e.g., [{\"AttributeKey\": \"EventName\", \"AttributeValue\": \"ConsoleLogin\"}])",
            },
            "start_time": {
                "type": "string",
                "description": "Start time (ISO 8601 format)",
            },
            "end_time": {
                "type": "string",
                "description": "End time (ISO 8601 format)",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum events to return (default: 50)",
            },
        },
    },
    is_read_only=True,
)
async def lookup_events(arguments: dict) -> str:
    from datetime import datetime

    def _execute():
        client = get_client(
            "cloudtrail", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {"MaxResults": arguments.get("max_results", 50)}
        if "lookup_attributes" in arguments:
            kwargs["LookupAttributes"] = arguments["lookup_attributes"]
        if "start_time" in arguments:
            kwargs["StartTime"] = datetime.fromisoformat(arguments["start_time"])
        if "end_time" in arguments:
            kwargs["EndTime"] = datetime.fromisoformat(arguments["end_time"])

        response = client.lookup_events(**kwargs)
        events = response.get("Events", [])
        return events

    events = await asyncio.to_thread(_execute)
    return json.dumps({"events": events, "count": len(events)}, default=str)
