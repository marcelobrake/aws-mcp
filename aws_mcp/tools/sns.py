"""SNS tools: topics, subscriptions, and publishing."""
import asyncio
import json
import logging

from ..aws_client import get_client
from ..config import get_config
from . import COMMON_PROPERTIES, tool

logger = logging.getLogger("aws_mcp")


@tool(
    name="aws_sns_list_topics",
    description="List all SNS topics in the account/region.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
        },
    },
    is_read_only=True,
)
async def list_topics(arguments: dict) -> str:
    def _execute():
        client = get_client("sns", arguments.get("profile"), arguments.get("region"))
        topics: list[dict] = []
        paginator = client.get_paginator("list_topics")
        for page in paginator.paginate():
            topics.extend(page.get("Topics", []))
        return topics

    topics = await asyncio.to_thread(_execute)
    return json.dumps({"topics": topics, "count": len(topics)}, default=str)


@tool(
    name="aws_sns_get_topic_attributes",
    description="Get attributes of an SNS topic: ARN, display name, subscription count, policy, etc.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "topic_arn": {
                "type": "string",
                "description": "SNS topic ARN",
            },
        },
        "required": ["topic_arn"],
    },
    is_read_only=True,
)
async def get_topic_attributes(arguments: dict) -> str:
    def _execute():
        client = get_client("sns", arguments.get("profile"), arguments.get("region"))
        response = client.get_topic_attributes(TopicArn=arguments["topic_arn"])
        return response.get("Attributes", {})

    attributes = await asyncio.to_thread(_execute)
    return json.dumps({"attributes": attributes}, default=str)


@tool(
    name="aws_sns_list_subscriptions",
    description="List SNS subscriptions, optionally filtered by topic ARN.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "topic_arn": {
                "type": "string",
                "description": "Filter by topic ARN (optional — lists all if omitted)",
            },
        },
    },
    is_read_only=True,
)
async def list_subscriptions(arguments: dict) -> str:
    def _execute():
        client = get_client("sns", arguments.get("profile"), arguments.get("region"))
        subs: list[dict] = []
        if "topic_arn" in arguments:
            paginator = client.get_paginator("list_subscriptions_by_topic")
            for page in paginator.paginate(TopicArn=arguments["topic_arn"]):
                subs.extend(page.get("Subscriptions", []))
        else:
            paginator = client.get_paginator("list_subscriptions")
            for page in paginator.paginate():
                subs.extend(page.get("Subscriptions", []))
        return subs

    subs = await asyncio.to_thread(_execute)
    return json.dumps({"subscriptions": subs, "count": len(subs)}, default=str)


@tool(
    name="aws_sns_publish",
    description="Publish a message to an SNS topic or target ARN. Blocked in --readonly mode.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "topic_arn": {
                "type": "string",
                "description": "SNS topic ARN to publish to",
            },
            "message": {
                "type": "string",
                "description": "Message body",
            },
            "subject": {
                "type": "string",
                "description": "Message subject (used by email subscriptions)",
            },
        },
        "required": ["topic_arn", "message"],
    },
    is_read_only=False,
)
async def publish(arguments: dict) -> str:
    config = get_config()
    if config.readonly:
        return json.dumps({
            "error": "BLOCKED by readonly mode: SNS Publish is not allowed. Remove --readonly to enable.",
            "readonly": True,
        })

    def _execute():
        client = get_client("sns", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {
            "TopicArn": arguments["topic_arn"],
            "Message": arguments["message"],
        }
        if "subject" in arguments:
            kwargs["Subject"] = arguments["subject"]

        response = client.publish(**kwargs)
        return {"MessageId": response.get("MessageId")}

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
