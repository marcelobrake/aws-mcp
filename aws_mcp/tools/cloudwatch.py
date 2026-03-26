"""CloudWatch tools: logs, metrics, and alarms."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_logs_describe_log_groups",
    description="List CloudWatch Log groups with optional prefix filter.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "log_group_prefix": {
                "type": "string",
                "description": "Filter by log group name prefix (e.g., '/aws/lambda/')",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of log groups to return (default: 50)",
            },
        },
    },
    is_read_only=True,
)
async def describe_log_groups(arguments: dict) -> str:
    def _execute():
        client = get_client("logs", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "log_group_prefix" in arguments:
            kwargs["logGroupNamePrefix"] = arguments["log_group_prefix"]
        if "limit" in arguments:
            kwargs["limit"] = arguments["limit"]

        response = client.describe_log_groups(**kwargs)
        groups = [
            {
                "logGroupName": g["logGroupName"],
                "storedBytes": g.get("storedBytes"),
                "retentionInDays": g.get("retentionInDays"),
                "creationTime": g.get("creationTime"),
            }
            for g in response.get("logGroups", [])
        ]
        return groups

    groups = await asyncio.to_thread(_execute)
    return json.dumps({"log_groups": groups, "count": len(groups)}, default=str)


@tool(
    name="aws_logs_get_log_events",
    description=(
        "Retrieve log events from a specific CloudWatch log stream. "
        "Provide both log_group_name and log_stream_name."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "log_group_name": {
                "type": "string",
                "description": "Log group name",
            },
            "log_stream_name": {
                "type": "string",
                "description": "Log stream name",
            },
            "start_time": {
                "type": "integer",
                "description": "Start timestamp in milliseconds since epoch",
            },
            "end_time": {
                "type": "integer",
                "description": "End timestamp in milliseconds since epoch",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of events to return (default: 100)",
            },
        },
        "required": ["log_group_name", "log_stream_name"],
    },
    is_read_only=True,
)
async def get_log_events(arguments: dict) -> str:
    def _execute():
        client = get_client("logs", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {
            "logGroupName": arguments["log_group_name"],
            "logStreamName": arguments["log_stream_name"],
        }
        if "start_time" in arguments:
            kwargs["startTime"] = arguments["start_time"]
        if "end_time" in arguments:
            kwargs["endTime"] = arguments["end_time"]
        if "limit" in arguments:
            kwargs["limit"] = arguments["limit"]

        response = client.get_log_events(**kwargs)
        events = [
            {
                "timestamp": e["timestamp"],
                "message": e["message"],
            }
            for e in response.get("events", [])
        ]
        return events

    events = await asyncio.to_thread(_execute)
    return json.dumps({"events": events, "count": len(events)}, default=str)


@tool(
    name="aws_logs_filter_log_events",
    description=(
        "Search CloudWatch log events using a filter pattern across one or more "
        "log streams. Useful for searching logs by keyword or pattern."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "log_group_name": {
                "type": "string",
                "description": "Log group name to search in",
            },
            "filter_pattern": {
                "type": "string",
                "description": "CloudWatch filter pattern (e.g., 'ERROR', '{ $.level = \"error\" }')",
            },
            "log_stream_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific log streams to search (optional, searches all if omitted)",
            },
            "start_time": {
                "type": "integer",
                "description": "Start timestamp in milliseconds since epoch",
            },
            "end_time": {
                "type": "integer",
                "description": "End timestamp in milliseconds since epoch",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum events to return (default: 100)",
            },
        },
        "required": ["log_group_name"],
    },
    is_read_only=True,
)
async def filter_log_events(arguments: dict) -> str:
    def _execute():
        client = get_client("logs", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {
            "logGroupName": arguments["log_group_name"],
        }
        if "filter_pattern" in arguments:
            kwargs["filterPattern"] = arguments["filter_pattern"]
        if "log_stream_names" in arguments:
            kwargs["logStreamNames"] = arguments["log_stream_names"]
        if "start_time" in arguments:
            kwargs["startTime"] = arguments["start_time"]
        if "end_time" in arguments:
            kwargs["endTime"] = arguments["end_time"]
        if "limit" in arguments:
            kwargs["limit"] = arguments["limit"]

        response = client.filter_log_events(**kwargs)
        events = [
            {
                "timestamp": e["timestamp"],
                "message": e["message"],
                "logStreamName": e.get("logStreamName"),
            }
            for e in response.get("events", [])
        ]
        return events

    events = await asyncio.to_thread(_execute)
    return json.dumps({"events": events, "count": len(events)}, default=str)


@tool(
    name="aws_cloudwatch_describe_alarms",
    description="List CloudWatch alarms with their state and threshold configuration.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "alarm_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific alarm names (optional — returns all if omitted)",
            },
            "state_value": {
                "type": "string",
                "enum": ["OK", "ALARM", "INSUFFICIENT_DATA"],
                "description": "Filter by alarm state",
            },
            "alarm_name_prefix": {
                "type": "string",
                "description": "Filter by alarm name prefix",
            },
            "max_records": {
                "type": "integer",
                "description": "Maximum alarms to return",
            },
        },
    },
    is_read_only=True,
)
async def describe_alarms(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "cloudwatch", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "alarm_names" in arguments:
            kwargs["AlarmNames"] = arguments["alarm_names"]
        if "state_value" in arguments:
            kwargs["StateValue"] = arguments["state_value"]
        if "alarm_name_prefix" in arguments:
            kwargs["AlarmNamePrefix"] = arguments["alarm_name_prefix"]
        if "max_records" in arguments:
            kwargs["MaxRecords"] = arguments["max_records"]
        response = client.describe_alarms(**kwargs)
        alarms = response.get("MetricAlarms", []) + response.get("CompositeAlarms", [])
        return alarms

    alarms = await asyncio.to_thread(_execute)
    return json.dumps({"alarms": alarms, "count": len(alarms)}, default=str)


@tool(
    name="aws_cloudwatch_list_metrics",
    description="List available CloudWatch metrics for a namespace or resource.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "namespace": {
                "type": "string",
                "description": "Metric namespace (e.g., 'AWS/EC2', 'AWS/Lambda', 'AWS/RDS')",
            },
            "metric_name": {
                "type": "string",
                "description": "Filter by metric name (e.g., 'CPUUtilization')",
            },
            "dimensions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Name": {"type": "string"},
                        "Value": {"type": "string"},
                    },
                    "required": ["Name", "Value"],
                },
                "description": "Filter by dimensions (e.g., [{\"Name\": \"InstanceId\", \"Value\": \"i-xxx\"}])",
            },
        },
    },
    is_read_only=True,
)
async def list_metrics(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "cloudwatch", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "namespace" in arguments:
            kwargs["Namespace"] = arguments["namespace"]
        if "metric_name" in arguments:
            kwargs["MetricName"] = arguments["metric_name"]
        if "dimensions" in arguments:
            kwargs["Dimensions"] = arguments["dimensions"]
        response = client.list_metrics(**kwargs)
        return response.get("Metrics", [])

    metrics = await asyncio.to_thread(_execute)
    return json.dumps({"metrics": metrics, "count": len(metrics)}, default=str)


@tool(
    name="aws_cloudwatch_get_metric_data",
    description=(
        "Retrieve time-series metric data for one or more CloudWatch metrics. "
        "Supports multiple metrics and math expressions in a single call."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "metric_data_queries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Id": {"type": "string"},
                        "MetricStat": {"type": "object"},
                        "Expression": {"type": "string"},
                        "Label": {"type": "string"},
                        "ReturnData": {"type": "boolean"},
                    },
                    "required": ["Id"],
                },
                "description": (
                    "Metric queries. Example: [{\"Id\": \"m1\", \"MetricStat\": {"
                    "\"Metric\": {\"Namespace\": \"AWS/EC2\", \"MetricName\": \"CPUUtilization\","
                    " \"Dimensions\": [{\"Name\": \"InstanceId\", \"Value\": \"i-xxx\"}]},"
                    " \"Period\": 300, \"Stat\": \"Average\"}}]"
                ),
            },
            "start_time": {
                "type": "string",
                "description": "Start time (ISO 8601, e.g., '2024-01-01T00:00:00Z')",
            },
            "end_time": {
                "type": "string",
                "description": "End time (ISO 8601)",
            },
            "max_datapoints": {
                "type": "integer",
                "description": "Maximum data points to return (default: 100)",
            },
        },
        "required": ["metric_data_queries", "start_time", "end_time"],
    },
    is_read_only=True,
)
async def get_metric_data(arguments: dict) -> str:
    from datetime import datetime

    def _execute():
        client = get_client(
            "cloudwatch", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {
            "MetricDataQueries": arguments["metric_data_queries"],
            "StartTime": datetime.fromisoformat(arguments["start_time"].replace("Z", "+00:00")),
            "EndTime": datetime.fromisoformat(arguments["end_time"].replace("Z", "+00:00")),
            "MaxDatapoints": arguments.get("max_datapoints", 100),
        }
        response = client.get_metric_data(**kwargs)
        return response.get("MetricDataResults", [])

    results = await asyncio.to_thread(_execute)
    return json.dumps({"results": results}, default=str)


@tool(
    name="aws_cloudwatch_get_metric_statistics",
    description=(
        "Get statistics (Average, Sum, Min, Max) for a single CloudWatch metric over a time period."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "namespace": {
                "type": "string",
                "description": "Metric namespace (e.g., 'AWS/EC2')",
            },
            "metric_name": {
                "type": "string",
                "description": "Metric name (e.g., 'CPUUtilization')",
            },
            "dimensions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Name": {"type": "string"},
                        "Value": {"type": "string"},
                    },
                    "required": ["Name", "Value"],
                },
                "description": "Dimensions (e.g., [{\"Name\": \"InstanceId\", \"Value\": \"i-xxx\"}])",
            },
            "start_time": {
                "type": "string",
                "description": "Start time (ISO 8601)",
            },
            "end_time": {
                "type": "string",
                "description": "End time (ISO 8601)",
            },
            "period": {
                "type": "integer",
                "description": "Granularity in seconds (e.g., 300 = 5 minutes)",
            },
            "statistics": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["SampleCount", "Average", "Sum", "Minimum", "Maximum"],
                },
                "description": "Statistics to retrieve (e.g., ['Average', 'Maximum'])",
            },
        },
        "required": ["namespace", "metric_name", "start_time", "end_time", "period", "statistics"],
    },
    is_read_only=True,
)
async def get_metric_statistics(arguments: dict) -> str:
    from datetime import datetime

    def _execute():
        client = get_client(
            "cloudwatch", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {
            "Namespace": arguments["namespace"],
            "MetricName": arguments["metric_name"],
            "StartTime": datetime.fromisoformat(arguments["start_time"].replace("Z", "+00:00")),
            "EndTime": datetime.fromisoformat(arguments["end_time"].replace("Z", "+00:00")),
            "Period": arguments["period"],
            "Statistics": arguments["statistics"],
        }
        if "dimensions" in arguments:
            kwargs["Dimensions"] = arguments["dimensions"]
        response = client.get_metric_statistics(**kwargs)
        datapoints = sorted(response.get("Datapoints", []), key=lambda x: x["Timestamp"])
        return datapoints

    datapoints = await asyncio.to_thread(_execute)
    return json.dumps({"datapoints": datapoints, "count": len(datapoints)}, default=str)
