"""SQS tools: queues, messages, and attributes."""
import asyncio
import json
import logging

from ..aws_client import get_client
from ..config import get_config
from . import COMMON_PROPERTIES, tool

logger = logging.getLogger("aws_mcp")


@tool(
    name="aws_sqs_list_queues",
    description="List SQS queues with optional name prefix filter.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "queue_name_prefix": {
                "type": "string",
                "description": "Filter queues by name prefix",
            },
        },
    },
    is_read_only=True,
)
async def list_queues(arguments: dict) -> str:
    def _execute():
        client = get_client("sqs", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "queue_name_prefix" in arguments:
            kwargs["QueueNamePrefix"] = arguments["queue_name_prefix"]

        response = client.list_queues(**kwargs)
        urls = response.get("QueueUrls", [])
        return urls

    urls = await asyncio.to_thread(_execute)
    return json.dumps({"queue_urls": urls, "count": len(urls)}, default=str)


@tool(
    name="aws_sqs_get_queue_attributes",
    description=(
        "Get attributes of an SQS queue: message count, delay, visibility timeout, "
        "dead-letter config, ARN, and more."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "queue_url": {
                "type": "string",
                "description": "SQS queue URL",
            },
            "attribute_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Attributes to retrieve (default: All). E.g., 'ApproximateNumberOfMessages', 'CreatedTimestamp'",
            },
        },
        "required": ["queue_url"],
    },
    is_read_only=True,
)
async def get_queue_attributes(arguments: dict) -> str:
    def _execute():
        client = get_client("sqs", arguments.get("profile"), arguments.get("region"))
        attrs = arguments.get("attribute_names", ["All"])
        response = client.get_queue_attributes(
            QueueUrl=arguments["queue_url"],
            AttributeNames=attrs,
        )
        return response.get("Attributes", {})

    attributes = await asyncio.to_thread(_execute)
    return json.dumps({"attributes": attributes}, default=str)


@tool(
    name="aws_sqs_receive_message",
    description=(
        "Receive (peek) messages from an SQS queue without deleting them. "
        "Uses a short visibility timeout so messages return to the queue quickly."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "queue_url": {
                "type": "string",
                "description": "SQS queue URL",
            },
            "max_number_of_messages": {
                "type": "integer",
                "description": "Max messages to receive (1-10, default: 1)",
            },
            "visibility_timeout": {
                "type": "integer",
                "description": "Seconds to hide message from other consumers (default: 5)",
            },
        },
        "required": ["queue_url"],
    },
    is_read_only=True,
)
async def receive_message(arguments: dict) -> str:
    def _execute():
        client = get_client("sqs", arguments.get("profile"), arguments.get("region"))
        response = client.receive_message(
            QueueUrl=arguments["queue_url"],
            MaxNumberOfMessages=arguments.get("max_number_of_messages", 1),
            VisibilityTimeout=arguments.get("visibility_timeout", 5),
            AttributeNames=["All"],
            MessageAttributeNames=["All"],
        )
        messages = response.get("Messages", [])
        return messages

    messages = await asyncio.to_thread(_execute)
    return json.dumps({"messages": messages, "count": len(messages)}, default=str)


@tool(
    name="aws_sqs_send_message",
    description="Send a message to an SQS queue. Blocked in --readonly mode.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "queue_url": {
                "type": "string",
                "description": "SQS queue URL",
            },
            "message_body": {
                "type": "string",
                "description": "Message body content",
            },
            "delay_seconds": {
                "type": "integer",
                "description": "Delay in seconds before message becomes visible (0-900)",
            },
            "message_group_id": {
                "type": "string",
                "description": "Message group ID (required for FIFO queues)",
            },
        },
        "required": ["queue_url", "message_body"],
    },
    is_read_only=False,
)
async def send_message(arguments: dict) -> str:
    config = get_config()
    if config.readonly:
        return json.dumps({
            "error": "BLOCKED by readonly mode: SQS SendMessage is not allowed. Remove --readonly to enable.",
            "readonly": True,
        })

    def _execute():
        client = get_client("sqs", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {
            "QueueUrl": arguments["queue_url"],
            "MessageBody": arguments["message_body"],
        }
        if "delay_seconds" in arguments:
            kwargs["DelaySeconds"] = arguments["delay_seconds"]
        if "message_group_id" in arguments:
            kwargs["MessageGroupId"] = arguments["message_group_id"]

        response = client.send_message(**kwargs)
        return {
            "MessageId": response.get("MessageId"),
            "MD5OfMessageBody": response.get("MD5OfMessageBody"),
            "SequenceNumber": response.get("SequenceNumber"),
        }

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)


@tool(
    name="aws_sqs_purge_queue",
    description="Purge all messages from an SQS queue. Blocked in --readonly mode.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "queue_url": {
                "type": "string",
                "description": "SQS queue URL",
            },
        },
        "required": ["queue_url"],
    },
    is_read_only=False,
)
async def purge_queue(arguments: dict) -> str:
    config = get_config()
    if config.readonly:
        return json.dumps({
            "error": "BLOCKED by readonly mode: SQS PurgeQueue is not allowed. Remove --readonly to enable.",
            "readonly": True,
        })

    def _execute():
        client = get_client("sqs", arguments.get("profile"), arguments.get("region"))
        client.purge_queue(QueueUrl=arguments["queue_url"])
        return {"message": f"Queue purged: {arguments['queue_url']}"}

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
