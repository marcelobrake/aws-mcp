"""GuardDuty tools: detectors, findings, and threat intelligence."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_guardduty_list_detectors",
    description="List GuardDuty detector IDs in the account (one per region).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
        },
    },
    is_read_only=True,
)
async def list_detectors(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "guardduty", arguments.get("profile"), arguments.get("region")
        )
        response = client.list_detectors()
        return response.get("DetectorIds", [])

    detectors = await asyncio.to_thread(_execute)
    return json.dumps({"detector_ids": detectors, "count": len(detectors)}, default=str)


@tool(
    name="aws_guardduty_get_detector",
    description="Get GuardDuty detector configuration and status.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "detector_id": {
                "type": "string",
                "description": "Detector ID (use aws_guardduty_list_detectors to get it)",
            },
        },
        "required": ["detector_id"],
    },
    is_read_only=True,
)
async def get_detector(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "guardduty", arguments.get("profile"), arguments.get("region")
        )
        response = client.get_detector(DetectorId=arguments["detector_id"])
        response.pop("ResponseMetadata", None)
        return response

    result = await asyncio.to_thread(_execute)
    return json.dumps({"detector": result}, default=str)


@tool(
    name="aws_guardduty_list_findings",
    description=(
        "List GuardDuty finding IDs, optionally filtered by severity or type. "
        "Use aws_guardduty_get_findings to retrieve full details."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "detector_id": {
                "type": "string",
                "description": "Detector ID",
            },
            "finding_criteria": {
                "type": "object",
                "description": (
                    "Filter criteria. Example: {\"Criterion\": {\"severity\": {\"Gte\": 7}}} "
                    "for high-severity findings, or {\"Criterion\": {\"service.archived\": {\"Eq\": [\"false\"]}}}"
                ),
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum finding IDs to return (default: 50)",
            },
        },
        "required": ["detector_id"],
    },
    is_read_only=True,
)
async def list_findings(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "guardduty", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {
            "DetectorId": arguments["detector_id"],
            "MaxResults": arguments.get("max_results", 50),
        }
        if "finding_criteria" in arguments:
            kwargs["FindingCriteria"] = arguments["finding_criteria"]
        response = client.list_findings(**kwargs)
        return response.get("FindingIds", [])

    finding_ids = await asyncio.to_thread(_execute)
    return json.dumps({"finding_ids": finding_ids, "count": len(finding_ids)}, default=str)


@tool(
    name="aws_guardduty_get_findings",
    description="Get full details for GuardDuty findings (severity, type, resource, action).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "detector_id": {
                "type": "string",
                "description": "Detector ID",
            },
            "finding_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Finding IDs to retrieve (max 50)",
            },
        },
        "required": ["detector_id", "finding_ids"],
    },
    is_read_only=True,
)
async def get_findings(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "guardduty", arguments.get("profile"), arguments.get("region")
        )
        response = client.get_findings(
            DetectorId=arguments["detector_id"],
            FindingIds=arguments["finding_ids"],
        )
        return response.get("Findings", [])

    findings = await asyncio.to_thread(_execute)
    return json.dumps({"findings": findings, "count": len(findings)}, default=str)


@tool(
    name="aws_guardduty_get_findings_statistics",
    description="Get a count of GuardDuty findings grouped by severity or finding type.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "detector_id": {
                "type": "string",
                "description": "Detector ID",
            },
            "finding_statistic_types": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["COUNT_BY_SEVERITY"],
                },
                "description": "Statistic types to retrieve (default: ['COUNT_BY_SEVERITY'])",
            },
        },
        "required": ["detector_id"],
    },
    is_read_only=True,
)
async def get_findings_statistics(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "guardduty", arguments.get("profile"), arguments.get("region")
        )
        response = client.get_findings_statistics(
            DetectorId=arguments["detector_id"],
            FindingStatisticTypes=arguments.get("finding_statistic_types", ["COUNT_BY_SEVERITY"]),
        )
        response.pop("ResponseMetadata", None)
        return response

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
