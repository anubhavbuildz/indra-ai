"""LLM tool-calling agent for configured-region read-only AWS audits."""

import asyncio
import json
from collections.abc import Callable
from typing import Any

from botocore.exceptions import BotoCoreError, ClientError
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionToolUnionParam
from pydantic import ValidationError

from app.core.config import Settings
from app.core.errors import AppError
from app.schemas.audit_schema import AUDIT_REPORT_JSON_SCHEMA, AuditReport
from app.services.llm.base import BaseLLM
from app.services.llm.role_prompts import load_role_prompt
from app.tools.audit.aws_audit import AWSAuditor

AUDIT_TOOLS: list[ChatCompletionToolUnionParam] = [
    {
        "type": "function",
        "function": {
            "name": "audit_s3",
            "description": (
                "Audit S3 public-access-block, public bucket policy and ACL, default encryption, "
                "versioning, TLS-only policy, and server access logging."
            ),
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "audit_iam",
            "description": "Check whether root-account access keys are present.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "audit_ec2",
            "description": (
                "Audit EC2 security groups, running instance public IPs, EBS default encryption, "
                "and public EBS snapshots in the configured AWS region."
            ),
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "audit_vpc",
            "description": "Audit VPC defaults and flow logging in the configured AWS region.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "audit_cloudtrail",
            "description": (
                "Audit CloudTrail multi-region coverage, logging status, log-file validation, "
                "and log bucket public-access-block and encryption across enabled regions."
            ),
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "audit_guardduty",
            "description": (
                "Check GuardDuty detector presence and enabled status in the configured AWS region."
            ),
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "audit_databases",
            "description": (
                "Audit RDS public accessibility, storage encryption, and Multi-AZ in the "
                "configured AWS region, plus backup retention, deletion protection, and public "
                "manual snapshots."
            ),
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
]


class CloudAgent(BaseLLM):
    """Interpret audit requests and execute only the supplied read-only tools."""

    def __init__(
        self,
        settings: Settings,
        timeout_seconds: float | None = None,
        client: AsyncOpenAI | None = None,
        *,
        auditor: AWSAuditor | None = None,
    ) -> None:
        super().__init__(settings, timeout_seconds, client)
        self.settings = settings
        self.auditor = auditor or AWSAuditor(primary_region=settings.aws_region)

    async def run_audit(
        self,
        question: str,
        history: list[dict[str, str]] | None = None,
    ) -> AuditReport:
        """Select relevant audit tools with the LLM, execute them, and validate results."""
        tool_calls = await self.request_tool_calls(
            message=(
                f"User request:\n<request>{question}</request>\n\n"
                f"Available audit report schema:\n{json.dumps(AUDIT_REPORT_JSON_SCHEMA)}"
            ),
            tools=AUDIT_TOOLS,
            history=history,
            system_prompt=load_role_prompt("cloud_role.md"),
        )

        tool_functions: dict[
            str, tuple[str, Callable[..., list[dict[str, Any]]], tuple[Any, ...]]
        ] = {
            "audit_s3": ("s3", self.auditor.audit_s3, ()),
            "audit_iam": ("iam", self.auditor.audit_iam, ()),
            "audit_ec2": ("ec2", self.auditor.audit_ec2, (self.settings.aws_region,)),
            "audit_vpc": ("vpc", self.auditor.audit_vpc, (self.settings.aws_region,)),
            "audit_databases": ("rds", self.auditor.audit_databases, (self.settings.aws_region,)),
            "audit_cloudtrail": ("cloudtrail", self.auditor.audit_cloudtrail, ()),
            "audit_guardduty": (
                "guardduty",
                self.auditor.audit_guardduty,
                (self.settings.aws_region,),
            ),
        }
        selected_services: list[str] = []
        findings: list[dict[str, Any]] = []
        seen_tools: set[str] = set()
        try:
            if len(tool_calls) > len(AUDIT_TOOLS):
                raise AppError(
                    502,
                    "provider_invalid_response",
                    "The inference provider selected an invalid set of audit tools.",
                )
            for call in tool_calls:
                function_name = call.function.name
                tool = tool_functions.get(function_name)
                if tool is None or function_name in seen_tools:
                    raise AppError(
                        502,
                        "provider_invalid_response",
                        "The inference provider selected an invalid set of audit tools.",
                    )
                seen_tools.add(function_name)
                try:
                    arguments = json.loads(call.function.arguments)
                except json.JSONDecodeError as exc:
                    raise AppError(
                        502,
                        "provider_invalid_response",
                        "The inference provider returned invalid tool arguments.",
                    ) from exc
                if not isinstance(arguments, dict) or arguments:
                    raise AppError(
                        502,
                        "provider_invalid_response",
                        "The inference provider returned invalid tool arguments.",
                    )
                service, audit_function, audit_arguments = tool
                selected_services.append(service)
                findings.extend(await asyncio.to_thread(audit_function, *audit_arguments))
        except (BotoCoreError, ClientError) as exc:
            raise AppError(
                502,
                "aws_audit_failed",
                "The AWS audit could not be completed.",
            ) from exc
        audit_data = {
            "audited_regions": (
                (["all-enabled-regions"] if "cloudtrail" in selected_services else [])
                + (
                    [self.settings.aws_region]
                    if any(
                        service in {"ec2", "vpc", "rds", "guardduty"}
                        for service in selected_services
                    )
                    else []
                )
            ),
            "audited_services": selected_services,
            "total_issues": len(findings),
            "critical_count": sum(
                1 for finding in findings if finding.get("severity") == "CRITICAL"
            ),
            "high_count": sum(1 for finding in findings if finding.get("severity") == "HIGH"),
            "medium_count": sum(1 for finding in findings if finding.get("severity") == "MEDIUM"),
            "low_count": sum(1 for finding in findings if finding.get("severity") == "LOW"),
            "findings": findings,
        }
        try:
            return AuditReport.model_validate(audit_data)
        except ValidationError as exc:
            raise AppError(
                502,
                "aws_audit_invalid_response",
                "The AWS audit returned data in an invalid format.",
            ) from exc
