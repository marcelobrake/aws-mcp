"""Kinesis tools: data streams and shards."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_kinesis_list_streams",
    description="List Kinesis data streams.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
        },
    },
    is_read_only=True,
)
async def list_streams(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "kinesis", arguments.get("profile"), arguments.get("region")
        )
        response = client.list_streams()
        streams = response.get("StreamSummaries", response.get("StreamNames", []))
        return streams

    streams = await asyncio.to_thread(_execute)
    return json.dumps({"streams": streams, "count": len(streams)}, default=str)


@tool(
    name="aws_kinesis_describe_stream",
    description="Describe a Kinesis stream.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "stream_name": {
                "type": "string",
                "description": "Stream name",
            },
        },
        "required": ["stream_name"],
    },
    is_read_only=True,
)
async def describe_stream(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "kinesis", arguments.get("profile"), arguments.get("region")
        )
        response = client.describe_stream_summary(
            StreamName=arguments["stream_name"]
        )
        return response["StreamDescriptionSummary"]

    result = await asyncio.to_thread(_execute)
    return json.dumps({"stream": result}, default=str)


@tool(
    name="aws_kinesis_list_shards",
    description="List shards in a Kinesis stream.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "stream_name": {
                "type": "string",
                "description": "Stream name",
            },
        },
        "required": ["stream_name"],
    },
    is_read_only=True,
)
async def list_shards(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "kinesis", arguments.get("profile"), arguments.get("region")
        )
        response = client.list_shards(StreamName=arguments["stream_name"])
        return response["Shards"]

    shards = await asyncio.to_thread(_execute)
    return json.dumps({"shards": shards, "count": len(shards)}, default=str)
