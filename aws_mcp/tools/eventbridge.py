"""EventBridge tools: event buses, rules, and targets."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_events_list_event_buses",
    description="List EventBridge event buses (default, custom, and partner).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "name_prefix": {
                "type": "string",
                "description": "Filter by name prefix",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum event buses to return",
            },
        },
    },
    is_read_only=True,
)
async def list_event_buses(arguments: dict) -> str:
    def _execute():
        client = get_client("events", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "name_prefix" in arguments:
            kwargs["NamePrefix"] = arguments["name_prefix"]
        if "limit" in arguments:
            kwargs["Limit"] = arguments["limit"]
        response = client.list_event_buses(**kwargs)
        return response.get("EventBuses", [])

    buses = await asyncio.to_thread(_execute)
    return json.dumps({"event_buses": buses, "count": len(buses)}, default=str)


@tool(
    name="aws_events_list_rules",
    description="List EventBridge rules, optionally on a specific event bus.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "event_bus_name": {
                "type": "string",
                "description": "Event bus name or ARN (default: 'default')",
            },
            "name_prefix": {
                "type": "string",
                "description": "Filter by rule name prefix",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum rules to return",
            },
        },
    },
    is_read_only=True,
)
async def list_rules(arguments: dict) -> str:
    def _execute():
        client = get_client("events", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "event_bus_name" in arguments:
            kwargs["EventBusName"] = arguments["event_bus_name"]
        if "name_prefix" in arguments:
            kwargs["NamePrefix"] = arguments["name_prefix"]
        if "limit" in arguments:
            kwargs["Limit"] = arguments["limit"]
        response = client.list_rules(**kwargs)
        return response.get("Rules", [])

    rules = await asyncio.to_thread(_execute)
    return json.dumps({"rules": rules, "count": len(rules)}, default=str)


@tool(
    name="aws_events_describe_rule",
    description="Get full configuration for an EventBridge rule.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "name": {
                "type": "string",
                "description": "Rule name",
            },
            "event_bus_name": {
                "type": "string",
                "description": "Event bus name or ARN (default: 'default')",
            },
        },
        "required": ["name"],
    },
    is_read_only=True,
)
async def describe_rule(arguments: dict) -> str:
    def _execute():
        client = get_client("events", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {"Name": arguments["name"]}
        if "event_bus_name" in arguments:
            kwargs["EventBusName"] = arguments["event_bus_name"]
        response = client.describe_rule(**kwargs)
        response.pop("ResponseMetadata", None)
        return response

    rule = await asyncio.to_thread(_execute)
    return json.dumps({"rule": rule}, default=str)


@tool(
    name="aws_events_list_targets_by_rule",
    description="List targets (Lambda, SQS, etc.) attached to an EventBridge rule.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "rule": {
                "type": "string",
                "description": "Rule name",
            },
            "event_bus_name": {
                "type": "string",
                "description": "Event bus name or ARN (default: 'default')",
            },
        },
        "required": ["rule"],
    },
    is_read_only=True,
)
async def list_targets_by_rule(arguments: dict) -> str:
    def _execute():
        client = get_client("events", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {"Rule": arguments["rule"]}
        if "event_bus_name" in arguments:
            kwargs["EventBusName"] = arguments["event_bus_name"]
        response = client.list_targets_by_rule(**kwargs)
        return response.get("Targets", [])

    targets = await asyncio.to_thread(_execute)
    return json.dumps({"targets": targets, "count": len(targets)}, default=str)
