"""Tests for audit invocation and evidence-bound cloud responses."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.core.config import Settings
from app.core.errors import AppError
from app.schemas.audit_schema import AuditReport
from app.services.llm import workflow
from app.services.llm.cloud_agent import CloudAgent
from app.services.rag import RetrievedPassage


def configured_settings() -> Settings:
    return Settings(
        _env_file=None,
        NVIDIA_API_KEY="test-secret",
        NVIDIA_BASE_URL="https://provider.invalid/v1",
        NVIDIA_MODEL="test-model",
        NVIDIA_API_FORMAT="openai-chat-completions",
        AWS_REGION="eu-west-1",
    )


def tool_call(name: str, arguments: str = "{}") -> SimpleNamespace:
    return SimpleNamespace(
        type="function",
        function=SimpleNamespace(name=name, arguments=arguments),
    )


def test_cloud_agent_selects_and_executes_audit_tools():
    client = Mock()
    client.chat.completions.create = AsyncMock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        tool_calls=[tool_call("audit_s3"), tool_call("audit_vpc")]
                    )
                )
            ]
        )
    )
    auditor = Mock()
    auditor.audit_s3.return_value = [
        {
            "service": "s3",
            "region": "global",
            "resource": "example-bucket",
            "severity": "HIGH",
            "title": "S3 Public Access Block Disabled",
        }
    ]
    auditor.audit_vpc.return_value = []
    agent = CloudAgent(configured_settings(), client=client, auditor=auditor)

    result = asyncio.run(agent.run_audit("Check S3 public access and VPC flow logs."))

    assert result.audited_services == ["s3", "vpc"]
    assert result.audited_regions == ["eu-west-1"]
    assert result.total_issues == 1
    assert result.high_count == 1
    assert result.findings[0].title == "S3 Public Access Block Disabled"
    auditor.audit_s3.assert_called_once_with()
    auditor.audit_vpc.assert_called_once_with("eu-west-1")
    auditor.audit_iam.assert_not_called()
    client.chat.completions.create.assert_awaited_once()
    request = client.chat.completions.create.call_args.kwargs
    assert request["tool_choice"] == "auto"
    assert request["parallel_tool_calls"] is False
    assert {tool["function"]["name"] for tool in request["tools"]} == {
        "audit_s3",
        "audit_iam",
        "audit_ec2",
        "audit_vpc",
        "audit_databases",
        "audit_cloudtrail",
        "audit_guardduty",
    }


def test_cloud_agent_rejects_invalid_tool_arguments_before_execution():
    client = Mock()
    client.chat.completions.create = AsyncMock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        tool_calls=[tool_call("audit_s3", '{"bucket":"other"}')]
                    )
                )
            ]
        )
    )
    auditor = Mock()
    agent = CloudAgent(configured_settings(), client=client, auditor=auditor)

    with pytest.raises(AppError) as error:
        asyncio.run(agent.run_audit("Audit the AWS account."))

    assert error.value.code == "provider_invalid_response"
    auditor.audit_s3.assert_not_called()


def test_cloud_agent_executes_cloudtrail_and_guardduty_with_report_schema():
    client = Mock()
    client.chat.completions.create = AsyncMock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        tool_calls=[
                            tool_call("audit_cloudtrail"),
                            tool_call("audit_guardduty"),
                        ]
                    )
                )
            ]
        )
    )
    auditor = Mock()
    auditor.audit_cloudtrail.return_value = []
    auditor.audit_guardduty.return_value = [
        {
            "service": "guardduty",
            "region": "eu-west-1",
            "check_id": "guardduty.detector_status",
            "severity": "HIGH",
            "title": "GuardDuty Detector Not Found",
            "evidence": {"detector_count": 0},
        }
    ]
    agent = CloudAgent(configured_settings(), client=client, auditor=auditor)

    result = asyncio.run(agent.run_audit("Check CloudTrail and GuardDuty status."))

    assert result.audited_services == ["cloudtrail", "guardduty"]
    assert result.audited_regions == ["all-enabled-regions", "eu-west-1"]
    assert result.findings[0].check_id == "guardduty.detector_status"
    assert result.findings[0].evidence == {"detector_count": 0}
    auditor.audit_cloudtrail.assert_called_once_with()
    auditor.audit_guardduty.assert_called_once_with("eu-west-1")


def test_chat_workflow_invokes_cloud_agent_with_audit_context(monkeypatch):
    import asyncio

    audit_report = AuditReport(
        audited_regions=["eu-west-1"],
        total_issues=0,
        critical_count=0,
        high_count=0,
        medium_count=0,
        low_count=0,
        findings=[],
    )
    passage = RetrievedPassage(
        title="Security guidance",
        content="Enable encryption for stored data.",
        source_name="Security guidance",
        source_uri="https://example.invalid/security",
    )
    cloud_agent = Mock()
    calls: list[str] = []

    async def run_audit(**kwargs):
        calls.append("cloud")
        assert kwargs["question"] == "Audit my AWS configuration."
        assert kwargs["history"] == [{"role": "user", "content": "Prioritize urgent risks."}]
        return audit_report

    cloud_agent.run_audit = AsyncMock(side_effect=run_audit)
    compliance_agent = Mock()

    async def compliance_review(**kwargs):
        calls.append("compliance")
        assert kwargs["audit_result"] == audit_report
        assert kwargs["retrieved_passages"] == [passage]
        return "Compliance assessment."

    compliance_agent.review = AsyncMock(side_effect=compliance_review)
    senior_agent = Mock()

    async def senior_review(**kwargs):
        calls.append("senior")
        assert kwargs["audit_report"] == audit_report
        assert kwargs["compliance_assessment"] == "Compliance assessment."
        return "Senior review."

    senior_agent.review = AsyncMock(side_effect=senior_review)

    class AgentContext:
        def __init__(self, agent):
            self.agent = agent

        async def __aenter__(self):
            return self.agent

        async def __aexit__(self, exc_type, exc_value, traceback):
            return None

    monkeypatch.setattr(workflow, "CloudAgent", lambda _: AgentContext(cloud_agent))
    monkeypatch.setattr(workflow, "ComplianceAgent", lambda _: AgentContext(compliance_agent))
    monkeypatch.setattr(workflow, "SeniorAgent", lambda _: AgentContext(senior_agent))

    class Retriever:
        async def query(self, question):
            calls.append("retrieval")
            assert question == "Audit my AWS configuration."
            return [passage]

    monkeypatch.setattr(workflow, "RagService", lambda _: Retriever())

    result = asyncio.run(
        workflow.chat_workflow(
            configured_settings(),
            "Audit my AWS configuration.",
            [{"role": "user", "content": "Prioritize urgent risks."}],
        )
    )

    assert result["cloud_agent_response"] == audit_report.model_dump()
    assert result["compliance_agent_response"] == "Compliance assessment."
    assert result["senior_agent_response"] == "Senior review."
    assert result["sources"] == [
        {
            "title": "Security guidance",
            "source": "Security guidance",
            "uri": "https://example.invalid/security",
        }
    ]
    assert calls == ["cloud", "retrieval", "compliance", "senior"]
    cloud_agent.run_audit.assert_awaited_once()
    compliance_agent.review.assert_awaited_once_with(
        question="Audit my AWS configuration.",
        audit_result=audit_report,
        history=[{"role": "user", "content": "Prioritize urgent risks."}],
        retrieved_passages=[passage],
    )
    senior_agent.review.assert_awaited_once()
