"""Terraform execution boundary tests."""

import asyncio
import os
import subprocess
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from app.api.routes import terraform as terraform_route
from app.core.config import Settings
from app.core.errors import AppError
from app.services.terraform_service import TerraformService


def service_at(tmp_path: Path, binary: str = "terraform") -> TerraformService:
    settings = Settings(
        _env_file=None,
        TERRAFORM_BIN=binary,
        TERRAFORM_WORKSPACE_ROOT=tmp_path,
    )
    return TerraformService(settings, timeout_seconds=1)


def test_unsupported_command_is_refused(tmp_path):
    service = service_at(tmp_path)
    _, workspace = service.create_workspace(str(uuid4()))

    with pytest.raises(AppError) as error:
        service._run("apply", workspace)

    assert error.value.code == "terraform_command_not_allowed"


def test_subprocess_is_shell_free_and_fixed_arguments(tmp_path):
    service = service_at(tmp_path)
    _, workspace = service.create_workspace(str(uuid4()))
    process = Mock()
    process.stdout = BytesIO(b"version details")
    process.stderr = BytesIO()
    process.wait.return_value = 0

    with (
        patch.dict(os.environ, {"NVIDIA_API_KEY": "sensitive-test-value"}),
        patch("app.services.terraform_service.subprocess.Popen", return_value=process) as popen,
    ):
        result = service._run("fmt", workspace)

    assert result[0] == 0
    arguments = popen.call_args.args[0]
    assert arguments == ["terraform", "fmt", "-check", "-no-color"]
    assert popen.call_args.kwargs["shell"] is False
    assert popen.call_args.kwargs["stdin"] is subprocess.DEVNULL
    assert "NVIDIA_API_KEY" not in popen.call_args.kwargs["env"]


def test_missing_terraform_binary_is_reported(tmp_path):
    service = service_at(tmp_path)
    _, workspace = service.create_workspace(str(uuid4()))

    with (
        patch("app.services.terraform_service.subprocess.Popen", side_effect=FileNotFoundError),
        pytest.raises(AppError) as error,
    ):
        service._run("version", workspace)

    assert error.value.code == "terraform_unavailable"


def test_terraform_timeout_is_reported(tmp_path):
    service = service_at(tmp_path)
    _, workspace = service.create_workspace(str(uuid4()))

    process = Mock()
    process.stdout = BytesIO()
    process.stderr = BytesIO()
    process.wait.side_effect = [subprocess.TimeoutExpired("terraform", 1), -9]
    with (
        patch("app.services.terraform_service.subprocess.Popen", return_value=process),
        pytest.raises(AppError) as error,
    ):
        service._run("plan", workspace)

    assert error.value.code == "terraform_timeout"
    process.kill.assert_called_once()


def test_policy_rejects_execution_constructs(tmp_path):
    with pytest.raises(AppError) as error:
        service_at(tmp_path).validate_code('resource "x" "y" { provisioner "local-exec" {} }')

    assert error.value.code == "terraform_policy_rejected"


def test_policy_rejects_non_aws_provider_source(tmp_path):
    with pytest.raises(AppError) as error:
        service_at(tmp_path).validate_code(
            'terraform { required_providers { custom = { source = "attacker/provider" } } }'
        )

    assert error.value.code == "terraform_policy_rejected"


def test_policy_rejects_provider_endpoint_overrides_and_inline_credentials(tmp_path):
    for code in (
        'provider "aws" { endpoints { s3 = "http://localhost" } }',
        'provider "aws" { access_key = "not-a-real-key" }',
    ):
        with pytest.raises(AppError) as error:
            service_at(tmp_path).validate_code(code)

        assert error.value.code == "terraform_policy_rejected"


def test_repair_returns_proposal_without_running_terraform(tmp_path, monkeypatch):
    service = service_at(tmp_path)
    repaired = 'resource "aws_s3_bucket" "assets" {}'
    seen: dict[str, object] = {}

    class FakeSeniorAgent:
        def __init__(self, settings):
            seen["settings"] = settings

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return None

        async def repair(self, code, errors):
            seen["code"] = code
            seen["errors"] = errors
            return repaired

    monkeypatch.setattr("app.services.terraform_service.SeniorAgent", FakeSeniorAgent)
    monkeypatch.setattr(
        service, "_run", Mock(side_effect=AssertionError("repair must not run Terraform"))
    )
    code = 'resource "aws_s3_bucket" "assets" { acl = "private" }'
    errors = ["The acl argument is deprecated."]

    result = asyncio.run(service.repair(str(uuid4()), code, errors))

    assert result["status"] == "proposed"
    assert result["code"] == repaired
    assert result["executed"] is False
    assert seen["code"] == code
    assert seen["errors"] == errors


def test_repair_endpoint_passes_code_and_diagnostics(client, monkeypatch):
    seen: dict[str, object] = {}

    class FakeTerraformService:
        def __init__(self, settings):
            pass

        async def repair(self, project_id, code, errors):
            seen["project_id"] = project_id
            seen["code"] = code
            seen["errors"] = errors
            return {
                "status": "proposed",
                "code": code,
                "executed": False,
                "project_id": project_id,
            }

    monkeypatch.setattr(terraform_route, "TerraformService", FakeTerraformService)
    project_id = str(uuid4())
    code = 'resource "aws_s3_bucket" "assets" {}'
    errors = ["Correct an invalid argument."]

    response = client.post(
        "/api/v1/terraform/repair",
        json={"project_id": project_id, "code": code, "errors": errors},
    )

    assert response.status_code == 200
    assert response.json()["code"] == code
    assert response.json()["executed"] is False
    assert seen == {"project_id": project_id, "code": code, "errors": errors}
