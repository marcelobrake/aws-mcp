"""Route53 tools: hosted zones and DNS record sets."""
import asyncio
import json
import logging

from ..aws_client import get_client
from ..config import get_config
from . import COMMON_PROPERTIES, tool

logger = logging.getLogger("aws_mcp")


@tool(
    name="aws_route53_list_hosted_zones",
    description="List Route53 hosted zones (DNS domains managed by this account).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_items": {
                "type": "string",
                "description": "Maximum zones to return (as string)",
            },
        },
    },
    is_read_only=True,
)
async def list_hosted_zones(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "route53", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "max_items" in arguments:
            kwargs["MaxItems"] = arguments["max_items"]

        response = client.list_hosted_zones(**kwargs)
        zones = [
            {
                "Id": z["Id"],
                "Name": z["Name"],
                "ResourceRecordSetCount": z.get("ResourceRecordSetCount"),
                "Config": z.get("Config", {}),
            }
            for z in response.get("HostedZones", [])
        ]
        return zones

    zones = await asyncio.to_thread(_execute)
    return json.dumps({"hosted_zones": zones, "count": len(zones)}, default=str)


@tool(
    name="aws_route53_list_resource_record_sets",
    description=(
        "List DNS records in a Route53 hosted zone. "
        "Returns record name, type, TTL, and values."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "hosted_zone_id": {
                "type": "string",
                "description": "Hosted zone ID (e.g., '/hostedzone/Z1234' or just 'Z1234')",
            },
            "start_record_name": {
                "type": "string",
                "description": "Start listing from this record name (for pagination)",
            },
            "start_record_type": {
                "type": "string",
                "enum": ["A", "AAAA", "CNAME", "MX", "NS", "SOA", "TXT", "SRV", "CAA"],
                "description": "Start listing from this record type (use with start_record_name)",
            },
            "max_items": {
                "type": "string",
                "description": "Maximum records to return (as string)",
            },
        },
        "required": ["hosted_zone_id"],
    },
    is_read_only=True,
)
async def list_resource_record_sets(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "route53", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {"HostedZoneId": arguments["hosted_zone_id"]}
        if "start_record_name" in arguments:
            kwargs["StartRecordName"] = arguments["start_record_name"]
        if "start_record_type" in arguments:
            kwargs["StartRecordType"] = arguments["start_record_type"]
        if "max_items" in arguments:
            kwargs["MaxItems"] = arguments["max_items"]

        response = client.list_resource_record_sets(**kwargs)
        records = response.get("ResourceRecordSets", [])
        result: dict = {"records": records, "count": len(records)}
        if response.get("IsTruncated"):
            result["next_record_name"] = response.get("NextRecordName")
            result["next_record_type"] = response.get("NextRecordType")
        return result

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)


@tool(
    name="aws_route53_get_hosted_zone",
    description="Get detailed information about a Route53 hosted zone including NS records and VPCs.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "hosted_zone_id": {
                "type": "string",
                "description": "Hosted zone ID",
            },
        },
        "required": ["hosted_zone_id"],
    },
    is_read_only=True,
)
async def get_hosted_zone(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "route53", arguments.get("profile"), arguments.get("region")
        )
        response = client.get_hosted_zone(Id=arguments["hosted_zone_id"])
        response.pop("ResponseMetadata", None)
        return response

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)


@tool(
    name="aws_route53_change_resource_record_sets",
    description=(
        "Create, update, or delete DNS records in a Route53 hosted zone. "
        "Blocked in --readonly mode."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "hosted_zone_id": {
                "type": "string",
                "description": "Hosted zone ID",
            },
            "changes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Action": {
                            "type": "string",
                            "enum": ["CREATE", "DELETE", "UPSERT"],
                        },
                        "ResourceRecordSet": {
                            "type": "object",
                            "properties": {
                                "Name": {"type": "string"},
                                "Type": {"type": "string"},
                                "TTL": {"type": "integer"},
                                "ResourceRecords": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "Value": {"type": "string"},
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                "description": (
                    "List of changes. Example: "
                    "[{\"Action\": \"UPSERT\", \"ResourceRecordSet\": "
                    "{\"Name\": \"app.example.com\", \"Type\": \"A\", \"TTL\": 300, "
                    "\"ResourceRecords\": [{\"Value\": \"1.2.3.4\"}]}}]"
                ),
            },
            "comment": {
                "type": "string",
                "description": "Optional comment for the change batch",
            },
        },
        "required": ["hosted_zone_id", "changes"],
    },
    is_read_only=False,
)
async def change_resource_record_sets(arguments: dict) -> str:
    config = get_config()
    if config.readonly:
        return json.dumps({
            "error": "BLOCKED by readonly mode: Route53 ChangeResourceRecordSets is not allowed. Remove --readonly to enable.",
            "readonly": True,
        })

    def _execute():
        client = get_client(
            "route53", arguments.get("profile"), arguments.get("region")
        )
        change_batch: dict = {"Changes": arguments["changes"]}
        if "comment" in arguments:
            change_batch["Comment"] = arguments["comment"]

        response = client.change_resource_record_sets(
            HostedZoneId=arguments["hosted_zone_id"],
            ChangeBatch=change_batch,
        )
        change_info = response.get("ChangeInfo", {})
        return {
            "Id": change_info.get("Id"),
            "Status": change_info.get("Status"),
            "SubmittedAt": change_info.get("SubmittedAt"),
            "Comment": change_info.get("Comment"),
        }

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
