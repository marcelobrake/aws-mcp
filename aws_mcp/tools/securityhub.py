"""Security Hub tools: findings, standards, and controls."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_securityhub_describe_hub",
    description="Get Security Hub configuration and subscription status for the account.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
        },
    },
    is_read_only=True,
)
async def describe_hub(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "securityhub", arguments.get("profile"), arguments.get("region")
        )
        response = client.describe_hub()
        response.pop("ResponseMetadata", None)
        return response

    result = await asyncio.to_thread(_execute)
    return json.dumps({"hub": result}, default=str)


@tool(
    name="aws_securityhub_get_findings",
    description=(
        "Retrieve Security Hub findings with optional filters. "
        "Aggregates findings from GuardDuty, Inspector, Macie, IAM Access Analyzer, and more."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "filters": {
                "type": "object",
                "description": (
                    "ASFF filter object. Example: {\"SeverityLabel\": [{\"Value\": \"HIGH\", \"Comparison\": \"EQUALS\"}], "
                    "\"RecordState\": [{\"Value\": \"ACTIVE\", \"Comparison\": \"EQUALS\"}]}"
                ),
            },
            "sort_criteria": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Field": {"type": "string"},
                        "SortOrder": {"type": "string", "enum": ["asc", "desc"]},
                    },
                },
                "description": "Sort results (e.g., [{\"Field\": \"LastObservedAt\", \"SortOrder\": \"desc\"}])",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum findings to return (default: 50, max: 100)",
            },
        },
    },
    is_read_only=True,
)
async def get_findings(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "securityhub", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {
            "MaxResults": min(arguments.get("max_results", 50), 100),
        }
        if "filters" in arguments:
            kwargs["Filters"] = arguments["filters"]
        if "sort_criteria" in arguments:
            kwargs["SortCriteria"] = arguments["sort_criteria"]
        response = client.get_findings(**kwargs)
        return response.get("Findings", [])

    findings = await asyncio.to_thread(_execute)
    return json.dumps({"findings": findings, "count": len(findings)}, default=str)


@tool(
    name="aws_securityhub_get_findings_summary",
    description="Get a count summary of Security Hub findings by severity (CRITICAL, HIGH, MEDIUM, LOW).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "record_state": {
                "type": "string",
                "enum": ["ACTIVE", "ARCHIVED"],
                "description": "Filter by record state (default: ACTIVE)",
            },
        },
    },
    is_read_only=True,
)
async def get_findings_summary(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "securityhub", arguments.get("profile"), arguments.get("region")
        )
        record_state = arguments.get("record_state", "ACTIVE")
        summary = {}
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL"]:
            resp = client.get_findings(
                Filters={
                    "SeverityLabel": [{"Value": severity, "Comparison": "EQUALS"}],
                    "RecordState": [{"Value": record_state, "Comparison": "EQUALS"}],
                    "WorkflowStatus": [{"Value": "NEW", "Comparison": "EQUALS"}],
                },
                MaxResults=1,
            )
            summary[severity] = resp.get("Total", 0)
        return summary

    result = await asyncio.to_thread(_execute)
    return json.dumps({"summary": result}, default=str)


@tool(
    name="aws_securityhub_list_standards_subscriptions",
    description="List security standards enabled in Security Hub (CIS, AWS Foundational, PCI DSS, etc.).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_results": {
                "type": "integer",
                "description": "Maximum standards to return",
            },
        },
    },
    is_read_only=True,
)
async def list_standards_subscriptions(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "securityhub", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]
        response = client.get_enabled_standards(**kwargs)
        return response.get("StandardsSubscriptions", [])

    standards = await asyncio.to_thread(_execute)
    return json.dumps({"standards": standards, "count": len(standards)}, default=str)


@tool(
    name="aws_securityhub_list_enabled_products_for_import",
    description="List Security Hub integrations (products) that are sending findings.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_results": {
                "type": "integer",
                "description": "Maximum integrations to return",
            },
        },
    },
    is_read_only=True,
)
async def list_enabled_products_for_import(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "securityhub", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]
        response = client.list_enabled_products_for_import(**kwargs)
        return response.get("ProductSubscriptions", [])

    products = await asyncio.to_thread(_execute)
    return json.dumps({"product_subscriptions": products, "count": len(products)}, default=str)
