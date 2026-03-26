"""SES tools: identities, sending statistics, and email sending."""
import asyncio
import json
import logging

from ..aws_client import get_client
from ..config import get_config
from . import COMMON_PROPERTIES, tool

logger = logging.getLogger("aws_mcp")


@tool(
    name="aws_ses_list_identities",
    description="List SES verified identities (email addresses and domains).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "identity_type": {
                "type": "string",
                "enum": ["EmailAddress", "Domain"],
                "description": "Filter by identity type (optional)",
            },
            "max_items": {
                "type": "integer",
                "description": "Maximum number of identities to return",
            },
        },
    },
    is_read_only=True,
)
async def list_identities(arguments: dict) -> str:
    def _execute():
        client = get_client("ses", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "identity_type" in arguments:
            kwargs["IdentityType"] = arguments["identity_type"]
        if "max_items" in arguments:
            kwargs["MaxItems"] = arguments["max_items"]

        response = client.list_identities(**kwargs)
        return response.get("Identities", [])

    identities = await asyncio.to_thread(_execute)
    return json.dumps(
        {"identities": identities, "count": len(identities)}, default=str
    )


@tool(
    name="aws_ses_get_send_statistics",
    description="Get SES sending statistics: delivery attempts, bounces, complaints, and rejects.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
        },
    },
    is_read_only=True,
)
async def get_send_statistics(arguments: dict) -> str:
    def _execute():
        client = get_client("ses", arguments.get("profile"), arguments.get("region"))
        response = client.get_send_statistics()
        return response.get("SendDataPoints", [])

    data_points = await asyncio.to_thread(_execute)
    return json.dumps(
        {"send_data_points": data_points, "count": len(data_points)}, default=str
    )


@tool(
    name="aws_ses_get_send_quota",
    description="Get SES sending quota: max send rate, max 24h send, and sent in last 24h.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
        },
    },
    is_read_only=True,
)
async def get_send_quota(arguments: dict) -> str:
    def _execute():
        client = get_client("ses", arguments.get("profile"), arguments.get("region"))
        response = client.get_send_quota()
        response.pop("ResponseMetadata", None)
        return response

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)


@tool(
    name="aws_ses_get_identity_verification_attributes",
    description="Get verification status for SES identities (email addresses and domains).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "identities": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Email addresses or domains to check",
            },
        },
        "required": ["identities"],
    },
    is_read_only=True,
)
async def get_identity_verification_attributes(arguments: dict) -> str:
    def _execute():
        client = get_client("ses", arguments.get("profile"), arguments.get("region"))
        response = client.get_identity_verification_attributes(
            Identities=arguments["identities"]
        )
        return response.get("VerificationAttributes", {})

    attrs = await asyncio.to_thread(_execute)
    return json.dumps({"verification_attributes": attrs}, default=str)


@tool(
    name="aws_ses_send_email",
    description="Send an email via SES. Blocked in --readonly mode.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "source": {
                "type": "string",
                "description": "Sender email address (must be verified in SES)",
            },
            "to_addresses": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Recipient email addresses",
            },
            "subject": {
                "type": "string",
                "description": "Email subject",
            },
            "body_text": {
                "type": "string",
                "description": "Plain text body",
            },
            "body_html": {
                "type": "string",
                "description": "HTML body (optional)",
            },
            "cc_addresses": {
                "type": "array",
                "items": {"type": "string"},
                "description": "CC email addresses",
            },
        },
        "required": ["source", "to_addresses", "subject", "body_text"],
    },
    is_read_only=False,
)
async def send_email(arguments: dict) -> str:
    config = get_config()
    if config.readonly:
        return json.dumps({
            "error": "BLOCKED by readonly mode: SES SendEmail is not allowed. Remove --readonly to enable.",
            "readonly": True,
        })

    def _execute():
        client = get_client("ses", arguments.get("profile"), arguments.get("region"))
        body: dict = {"Text": {"Data": arguments["body_text"]}}
        if "body_html" in arguments:
            body["Html"] = {"Data": arguments["body_html"]}

        kwargs: dict = {
            "Source": arguments["source"],
            "Destination": {"ToAddresses": arguments["to_addresses"]},
            "Message": {
                "Subject": {"Data": arguments["subject"]},
                "Body": body,
            },
        }
        if "cc_addresses" in arguments:
            kwargs["Destination"]["CcAddresses"] = arguments["cc_addresses"]

        response = client.send_email(**kwargs)
        return {"MessageId": response.get("MessageId")}

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
