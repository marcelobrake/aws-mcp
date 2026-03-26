"""Firehose (Kinesis Data Firehose) tools: delivery streams."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_firehose_list_delivery_streams",
    description="List Kinesis Data Firehose delivery streams.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "delivery_stream_type": {
                "type": "string",
                "enum": ["DirectPut", "KinesisStreamAsSource", "MSKAsSource"],
                "description": "Filter by stream source type",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum streams to return",
            },
        },
    },
    is_read_only=True,
)
async def list_delivery_streams(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "firehose", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "delivery_stream_type" in arguments:
            kwargs["DeliveryStreamType"] = arguments["delivery_stream_type"]
        if "limit" in arguments:
            kwargs["Limit"] = arguments["limit"]

        response = client.list_delivery_streams(**kwargs)
        return response.get("DeliveryStreamNames", [])

    streams = await asyncio.to_thread(_execute)
    return json.dumps(
        {"delivery_streams": streams, "count": len(streams)}, default=str
    )


@tool(
    name="aws_firehose_describe_delivery_stream",
    description=(
        "Get detailed config for a Firehose delivery stream: source, "
        "destination, buffering, compression, and status."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "delivery_stream_name": {
                "type": "string",
                "description": "Delivery stream name",
            },
        },
        "required": ["delivery_stream_name"],
    },
    is_read_only=True,
)
async def describe_delivery_stream(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "firehose", arguments.get("profile"), arguments.get("region")
        )
        response = client.describe_delivery_stream(
            DeliveryStreamName=arguments["delivery_stream_name"]
        )
        return response.get("DeliveryStreamDescription", {})

    desc = await asyncio.to_thread(_execute)
    return json.dumps({"delivery_stream": desc}, default=str)
