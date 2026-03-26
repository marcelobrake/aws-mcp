"""KMS tools: keys, key metadata, and aliases."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_kms_list_keys",
    description="List KMS keys in the account.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
        },
    },
    is_read_only=True,
)
async def list_keys(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "kms", arguments.get("profile"), arguments.get("region")
        )
        response = client.list_keys()
        return response["Keys"]

    keys = await asyncio.to_thread(_execute)
    return json.dumps({"keys": keys, "count": len(keys)}, default=str)


@tool(
    name="aws_kms_describe_key",
    description="Describe a KMS key.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "key_id": {
                "type": "string",
                "description": "Key ID, ARN, or alias",
            },
        },
        "required": ["key_id"],
    },
    is_read_only=True,
)
async def describe_key(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "kms", arguments.get("profile"), arguments.get("region")
        )
        response = client.describe_key(KeyId=arguments["key_id"])
        return response["KeyMetadata"]

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)


@tool(
    name="aws_kms_list_aliases",
    description="List KMS key aliases.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "key_id": {
                "type": "string",
                "description": "Filter aliases by key ID",
            },
        },
    },
    is_read_only=True,
)
async def list_aliases(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "kms", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "key_id" in arguments:
            kwargs["KeyId"] = arguments["key_id"]
        response = client.list_aliases(**kwargs)
        return response["Aliases"]

    aliases = await asyncio.to_thread(_execute)
    return json.dumps({"aliases": aliases, "count": len(aliases)}, default=str)
