"""Cost Explorer tools: cost analysis, forecasts, and usage."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_ce_get_cost_and_usage",
    description=(
        "Get cost and usage data for a time period. Group by service, account, region, "
        "tag, etc. TimePeriod format: {'Start': 'YYYY-MM-DD', 'End': 'YYYY-MM-DD'}."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "time_period": {
                "type": "object",
                "properties": {
                    "Start": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "End": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                },
                "required": ["Start", "End"],
                "description": "Time period for the cost query",
            },
            "granularity": {
                "type": "string",
                "enum": ["DAILY", "MONTHLY", "HOURLY"],
                "description": "Time granularity (default: MONTHLY)",
            },
            "metrics": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Metrics to return (default: ['UnblendedCost']). Options: UnblendedCost, BlendedCost, AmortizedCost, UsageQuantity",
            },
            "group_by": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Type": {"type": "string", "enum": ["DIMENSION", "TAG", "COST_CATEGORY"]},
                        "Key": {"type": "string"},
                    },
                },
                "description": "Group results by dimension (e.g., [{\"Type\": \"DIMENSION\", \"Key\": \"SERVICE\"}])",
            },
            "filter": {
                "type": "object",
                "description": "Cost Explorer filter expression",
            },
        },
        "required": ["time_period"],
    },
    is_read_only=True,
)
async def get_cost_and_usage(arguments: dict) -> str:
    def _execute():
        client = get_client("ce", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {
            "TimePeriod": arguments["time_period"],
            "Granularity": arguments.get("granularity", "MONTHLY"),
            "Metrics": arguments.get("metrics", ["UnblendedCost"]),
        }
        if "group_by" in arguments:
            kwargs["GroupBy"] = arguments["group_by"]
        if "filter" in arguments:
            kwargs["Filter"] = arguments["filter"]

        response = client.get_cost_and_usage(**kwargs)
        response.pop("ResponseMetadata", None)
        return response

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)


@tool(
    name="aws_ce_get_cost_forecast",
    description="Get a cost forecast for a future time period.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "time_period": {
                "type": "object",
                "properties": {
                    "Start": {"type": "string"},
                    "End": {"type": "string"},
                },
                "required": ["Start", "End"],
                "description": "Future time period (YYYY-MM-DD)",
            },
            "metric": {
                "type": "string",
                "enum": ["UNBLENDED_COST", "BLENDED_COST", "AMORTIZED_COST", "NET_UNBLENDED_COST"],
                "description": "Cost metric to forecast (default: UNBLENDED_COST)",
            },
            "granularity": {
                "type": "string",
                "enum": ["DAILY", "MONTHLY"],
                "description": "Forecast granularity (default: MONTHLY)",
            },
        },
        "required": ["time_period"],
    },
    is_read_only=True,
)
async def get_cost_forecast(arguments: dict) -> str:
    def _execute():
        client = get_client("ce", arguments.get("profile"), arguments.get("region"))
        response = client.get_cost_forecast(
            TimePeriod=arguments["time_period"],
            Metric=arguments.get("metric", "UNBLENDED_COST"),
            Granularity=arguments.get("granularity", "MONTHLY"),
        )
        response.pop("ResponseMetadata", None)
        return response

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
