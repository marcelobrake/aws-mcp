"""S3 tools: bucket and object operations."""
import asyncio
import base64
import json
import logging

from ..aws_client import get_client
from ..config import get_config
from . import COMMON_PROPERTIES, tool

logger = logging.getLogger("aws_mcp")


@tool(
    name="aws_s3_list_buckets",
    description="List all S3 buckets in the account.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
        },
    },
    is_read_only=True,
)
async def list_buckets(arguments: dict) -> str:
    def _execute():
        client = get_client("s3", arguments.get("profile"), arguments.get("region"))
        response = client.list_buckets()
        buckets = [
            {"Name": b["Name"], "CreationDate": b["CreationDate"]}
            for b in response.get("Buckets", [])
        ]
        return buckets

    buckets = await asyncio.to_thread(_execute)
    return json.dumps({"buckets": buckets, "count": len(buckets)}, default=str)


@tool(
    name="aws_s3_list_objects",
    description=(
        "List objects in an S3 bucket with optional prefix filter. "
        "Returns up to 1000 objects per call; use continuation_token for pagination."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "bucket": {
                "type": "string",
                "description": "S3 bucket name",
            },
            "prefix": {
                "type": "string",
                "description": "Key prefix filter (e.g., 'logs/2024/')",
            },
            "max_keys": {
                "type": "integer",
                "description": "Maximum number of keys to return (default: 1000)",
            },
            "continuation_token": {
                "type": "string",
                "description": "Token for paginating through results",
            },
        },
        "required": ["bucket"],
    },
    is_read_only=True,
)
async def list_objects(arguments: dict) -> str:
    def _execute():
        client = get_client("s3", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {"Bucket": arguments["bucket"]}
        if "prefix" in arguments:
            kwargs["Prefix"] = arguments["prefix"]
        if "max_keys" in arguments:
            kwargs["MaxKeys"] = arguments["max_keys"]
        if "continuation_token" in arguments:
            kwargs["ContinuationToken"] = arguments["continuation_token"]

        response = client.list_objects_v2(**kwargs)
        objects = [
            {
                "Key": obj["Key"],
                "Size": obj["Size"],
                "LastModified": obj["LastModified"],
            }
            for obj in response.get("Contents", [])
        ]
        result: dict = {"objects": objects, "count": len(objects)}
        if response.get("IsTruncated"):
            result["next_continuation_token"] = response.get(
                "NextContinuationToken"
            )
        return result

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)


@tool(
    name="aws_s3_get_object",
    description=(
        "Download and return the content of an S3 object. "
        "Text files are returned as strings; binary files as base64. "
        "Use 'range' for partial downloads of large files."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "bucket": {
                "type": "string",
                "description": "S3 bucket name",
            },
            "key": {
                "type": "string",
                "description": "Object key (path)",
            },
            "range": {
                "type": "string",
                "description": "Byte range (e.g., 'bytes=0-1023') for partial download",
            },
        },
        "required": ["bucket", "key"],
    },
    is_read_only=True,
)
async def get_object(arguments: dict) -> str:
    def _execute():
        client = get_client("s3", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {
            "Bucket": arguments["bucket"],
            "Key": arguments["key"],
        }
        if "range" in arguments:
            kwargs["Range"] = arguments["range"]

        response = client.get_object(**kwargs)
        body = response["Body"].read()
        content_type = response.get("ContentType", "application/octet-stream")

        result = {
            "key": arguments["key"],
            "content_type": content_type,
            "content_length": response.get("ContentLength"),
            "last_modified": response.get("LastModified"),
        }

        # Try text decoding for text-like content types
        text_types = ("text/", "application/json", "application/xml", "application/yaml")
        if any(content_type.startswith(t) for t in text_types):
            try:
                result["content"] = body.decode("utf-8")
                result["encoding"] = "utf-8"
                return result
            except UnicodeDecodeError:
                pass

        # Fallback to base64 for binary content
        if len(body) > 1_000_000:
            result["content"] = "(binary content too large, use 'range' parameter)"
            result["encoding"] = "truncated"
        else:
            result["content"] = base64.b64encode(body).decode("ascii")
            result["encoding"] = "base64"
        return result

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)


@tool(
    name="aws_s3_put_object",
    description=(
        "Upload content to an S3 object. Blocked in --readonly mode."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "bucket": {
                "type": "string",
                "description": "S3 bucket name",
            },
            "key": {
                "type": "string",
                "description": "Object key (path)",
            },
            "content": {
                "type": "string",
                "description": "Text content to upload",
            },
            "content_type": {
                "type": "string",
                "description": "MIME type (default: text/plain)",
            },
        },
        "required": ["bucket", "key", "content"],
    },
    is_read_only=False,
)
async def put_object(arguments: dict) -> str:
    config = get_config()
    if config.readonly:
        return json.dumps({
            "error": "BLOCKED by readonly mode: S3 PutObject is not allowed. Remove --readonly to enable writes.",
            "readonly": True,
        })

    def _execute():
        client = get_client("s3", arguments.get("profile"), arguments.get("region"))
        response = client.put_object(
            Bucket=arguments["bucket"],
            Key=arguments["key"],
            Body=arguments["content"].encode("utf-8"),
            ContentType=arguments.get("content_type", "text/plain"),
        )
        return {
            "bucket": arguments["bucket"],
            "key": arguments["key"],
            "etag": response.get("ETag"),
            "version_id": response.get("VersionId"),
        }

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)


@tool(
    name="aws_s3_delete_objects",
    description=(
        "Delete one or more objects from an S3 bucket. Blocked in --readonly mode."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "bucket": {
                "type": "string",
                "description": "S3 bucket name",
            },
            "keys": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Object keys to delete",
            },
        },
        "required": ["bucket", "keys"],
    },
    is_read_only=False,
)
async def delete_objects(arguments: dict) -> str:
    config = get_config()
    if config.readonly:
        return json.dumps({
            "error": "BLOCKED by readonly mode: S3 DeleteObjects is not allowed. Remove --readonly to enable deletes.",
            "readonly": True,
        })

    def _execute():
        client = get_client("s3", arguments.get("profile"), arguments.get("region"))
        objects = [{"Key": k} for k in arguments["keys"]]
        response = client.delete_objects(
            Bucket=arguments["bucket"],
            Delete={"Objects": objects},
        )
        return {
            "deleted": response.get("Deleted", []),
            "errors": response.get("Errors", []),
        }

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
