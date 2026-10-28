"""Explicit test-only ASGI adapter. Never import from production entry points."""

import os
import socket
import tempfile
from pathlib import Path

# Override host credentials before importing application configuration.
os.environ.update(
    {
        "APP_ENV": "development",
        "DEBUG": "false",
        "API_V1_PREFIX": "/api/v1",
        "AUTH_USERNAME": "test-user",
        "AUTH_PASSWORD": "test-password",
        "JWT_SECRET_KEY": "test-signing-secret-with-at-least-32-bytes",
        "NVIDIA_API_KEY": "test-only-no-inference",
        "NVIDIA_BASE_URL": "https://invalid.test/v1",
        "NVIDIA_MODEL": "fixture-model",
        "NVIDIA_API_FORMAT": "openai-chat-completions",
        "AWS_ACCESS_KEY_ID": "testing",
        "AWS_SECRET_ACCESS_KEY": "testing",
        "AWS_SESSION_TOKEN": "",
        "AWS_PROFILE": "default",
        "AWS_SHARED_CREDENTIALS_FILE": "/dev/null",
        "AWS_CONFIG_FILE": "/dev/null",
        "AWS_EC2_METADATA_DISABLED": "true",
        "AWS_REGION": "us-east-1",
        "DATABASE_URL": "sqlite:///" + str(Path(tempfile.mkdtemp(prefix="indra-e2e-")) / "test.db"),
        "CORS_ORIGINS": "http://localhost:5173,http://127.0.0.1:5173,http://frontend:5173,http://localhost:15173,http://127.0.0.1:15173",
    }
)
os.environ.pop("AWS_PROFILE", None)
_original_connect = socket.socket.connect


def local_only(self, address):
    if isinstance(address, tuple) and address[0] not in {"127.0.0.1", "::1"}:
        raise RuntimeError("QA server blocks all outbound external network connections")
    return _original_connect(self, address)


socket.socket.connect = local_only
socket.socket.connect_ex = local_only

from app.main import app as app  # noqa: E402
from app.schemas.audit_schema import AuditReport  # noqa: E402
from app.services.aws.aws_service import AWSService  # noqa: E402
from app.services.llm.base import BaseLLM  # noqa: E402
from app.services.llm.cloud_agent import CloudAgent  # noqa: E402
from app.services.rag import RagService, RetrievedPassage  # noqa: E402


async def fixture_audit(self, question, history=None):
    return AuditReport(
        audited_regions=["us-east-1"],
        audited_services=["s3"],
        total_issues=1,
        critical_count=0,
        high_count=1,
        medium_count=0,
        low_count=0,
        findings=[
            {
                "service": "s3",
                "region": "us-east-1",
                "resource": "synthetic-bucket",
                "severity": "HIGH",
                "title": "Synthetic public bucket",
                "check_id": "s3.public",
                "evidence": {"fixture": True},
                "remediation": "Review public access",
            }
        ],
    )


async def fixture_complete(self, message, history=None, **kwargs):
    return "Synthetic fixture review. No real AWS evidence or compliance certification."


async def fixture_query(self, question):
    return [
        RetrievedPassage(
            "Fixture guidance", "Synthetic guidance only", "Fixture", "https://example.test"
        )
    ]


def fixture_identity(self):
    return {
        "status": "configured",
        "account": "000000000000",
        "arn": "arn:aws:iam::000000000000:user/test",
        "region": "us-east-1",
        "user_id": "fixture",
    }


CloudAgent.run_audit = fixture_audit
BaseLLM.complete = fixture_complete
RagService.query = fixture_query
AWSService.identity = fixture_identity
