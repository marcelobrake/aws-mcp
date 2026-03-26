"""ACM tools: certificate listing and details."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_acm_list_certificates",
    description="List ACM certificates in the account/region, optionally filtered by status.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "certificate_statuses": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [
                        "PENDING_VALIDATION",
                        "ISSUED",
                        "INACTIVE",
                        "REVOKED",
                        "EXPIRED",
                        "VALIDATION_TIMED_OUT",
                        "FAILED",
                    ],
                },
                "description": "Filter by status",
            },
        },
    },
    is_read_only=True,
)
async def list_certificates(arguments: dict) -> str:
    def _execute():
        client = get_client("acm", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "certificate_statuses" in arguments:
            kwargs["CertificateStatuses"] = arguments["certificate_statuses"]
        response = client.list_certificates(**kwargs)
        return response["CertificateSummaryList"]

    certificates = await asyncio.to_thread(_execute)
    return json.dumps({"certificates": certificates, "count": len(certificates)}, default=str)


@tool(
    name="aws_acm_describe_certificate",
    description="Describe an ACM certificate in detail.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "certificate_arn": {
                "type": "string",
                "description": "Certificate ARN",
            },
        },
        "required": ["certificate_arn"],
    },
    is_read_only=True,
)
async def describe_certificate(arguments: dict) -> str:
    def _execute():
        client = get_client("acm", arguments.get("profile"), arguments.get("region"))
        response = client.describe_certificate(CertificateArn=arguments["certificate_arn"])
        return response["Certificate"]

    certificate = await asyncio.to_thread(_execute)
    return json.dumps({"certificate": certificate}, default=str)
