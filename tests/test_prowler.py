"""Prowler CLI and API boundary tests."""

import asyncio
import json
import os
import subprocess
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.api.routes import prowler as prowler_route
from app.core.config import Settings
from app.core.errors import AppError
from app.tools.prowler.scanner import Scanner


def service_at(binary: str = "prowler") -> Scanner:
    return Scanner(
        Settings(
            _env_file=None,
            PROWLER_BIN=binary,
            AWS_REGION="us-west-2",
            PROWLER_TIMEOUT_SECONDS=1,
        ),
    )


def test_scan_uses_fixed_shell_free_cli_and_reads_json_report():
    findings = [{"finding_info": {"title": "Encryption disabled"}}]
    process = Mock(returncode=0)

    def create_report(command, **kwargs):
        output_directory = Path(command[command.index("--output-directory") + 1])
        (output_directory / "scan.ocsf.json").write_text(json.dumps(findings), encoding="utf-8")
        return process

    with (
        patch.dict(
            os.environ,
            {"NVIDIA_API_KEY": "private-test-value", "AWS_PROFILE": "test-profile"},
        ),
        patch("app.tools.prowler.scanner.subprocess.run", side_effect=create_report) as popen,
    ):
        result = asyncio.run(service_at().run_scan())

    assert result["region"] == "us-west-2"
    assert result["findings"] == findings
    assert result["findings_count"] == 1
    command = popen.call_args.args[0]
    assert command[:5] == [
        "prowler",
        "aws",
        "--output-formats",
        "json-ocsf",
        "--output-directory",
    ]
    assert command[command.index("--region") + 1] == "us-west-2"
    assert command[-1] == "--ignore-exit-code-3"
    assert popen.call_args.kwargs["shell"] is False
    assert popen.call_args.kwargs["stdin"] is subprocess.DEVNULL
    assert "NVIDIA_API_KEY" not in popen.call_args.kwargs["env"]
    assert popen.call_args.kwargs["env"]["AWS_PROFILE"] == "test-profile"


def test_scan_uses_request_region_and_service_scope():
    process = Mock(returncode=0)

    def create_report(command, **kwargs):
        output_directory = Path(command[command.index("--output-directory") + 1])
        (output_directory / "scan.ocsf.json").write_text("[]", encoding="utf-8")
        return process

    with patch("app.tools.prowler.scanner.subprocess.run", side_effect=create_report) as popen:
        result = asyncio.run(
            service_at().run_scan(
                region="eu-west-1", services=["s3", "iam"], prowler_args=["--checks", "check-a"]
            )
        )

    command = popen.call_args.args[0]
    assert result["region"] == "eu-west-1"
    assert command[command.index("--region") + 1] == "eu-west-1"
    services_index = command.index("--services")
    assert command[services_index + 1 : services_index + 3] == ["s3", "iam"]
    assert command[-2:] == ["--checks", "check-a"]


def test_scan_rejects_args_that_override_fixed_output_or_shell_boundary():
    with pytest.raises(AppError) as error:
        asyncio.run(service_at().run_scan(prowler_args=["--output-directory", "/tmp/elsewhere"]))
    assert error.value.code == "invalid_prowler_args"


@pytest.mark.parametrize(
    ("region", "services", "error_code"),
    [
        ("bad region; rm -rf", None, "invalid_scan_region"),
        (None, ["s3", "--output-directory"], "invalid_scan_services"),
        (None, ["s3", "s3"], "invalid_scan_services"),
    ],
)
def test_scan_rejects_invalid_scope(region, services, error_code):
    with pytest.raises(AppError) as error:
        asyncio.run(service_at().run_scan(region=region, services=services))

    assert error.value.code == error_code


def test_missing_cli_is_reported():
    with (
        patch("app.tools.prowler.scanner.subprocess.run", side_effect=FileNotFoundError),
        pytest.raises(AppError) as error,
    ):
        asyncio.run(service_at().run_scan())

    assert error.value.code == "prowler_unavailable"


def test_scan_timeout_kills_process():
    with (
        patch(
            "app.tools.prowler.scanner.subprocess.run",
            side_effect=subprocess.TimeoutExpired("prowler", 1),
        ),
        pytest.raises(AppError) as error,
    ):
        asyncio.run(service_at().run_scan())

    assert error.value.code == "prowler_timeout"


def test_failed_scan_does_not_expose_cli_output():
    with (
        patch(
            "app.tools.prowler.scanner.subprocess.run",
            return_value=Mock(returncode=1),
        ),
        pytest.raises(AppError) as error,
    ):
        asyncio.run(service_at().run_scan())

    assert error.value.code == "prowler_scan_failed"
    assert "private" not in error.value.message


def test_report_reader_accepts_json_lines(tmp_path):
    report = tmp_path / "findings.json"
    report.write_text('{"check_id":"one"}\n{"check_id":"two"}\n', encoding="utf-8")

    assert Scanner._read_findings(tmp_path) == [
        {"check_id": "one"},
        {"check_id": "two"},
    ]


def test_report_reader_rejects_invalid_json(tmp_path):
    (tmp_path / "findings.json").write_text("not json", encoding="utf-8")

    with pytest.raises(AppError) as error:
        Scanner._read_findings(tmp_path)

    assert error.value.code == "prowler_output_invalid"


def test_report_reader_rejects_missing_json_report(tmp_path):
    with pytest.raises(AppError) as error:
        Scanner._read_findings(tmp_path)

    assert error.value.code == "prowler_output_missing"


def test_report_reader_enforces_finding_limit(tmp_path, monkeypatch):
    (tmp_path / "findings.json").write_text('[{"id":"one"},{"id":"two"}]', encoding="utf-8")
    monkeypatch.setattr("app.tools.prowler.scanner.MAX_FINDINGS", 1)

    with pytest.raises(AppError) as error:
        Scanner._read_findings(tmp_path)

    assert error.value.code == "prowler_report_too_large"


def test_scan_endpoint_passes_findings_to_agent(client, monkeypatch):
    findings = [{"finding_info": {"title": "Encryption disabled"}}]
    workflow_result = {
        "operation_id": "operation-1",
        "region": "us-west-2",
        "findings": findings,
        "findings_count": 1,
        "prowler_summary": "Prowler scan summary.",
        "compliance": "Evidence-based compliance assessment.",
        "response": "Senior review of both assessments.",
        "sources": [{"chunk_id": "aws-guidance-1", "source_title": "Storage guidance"}],
    }
    scan_workflow = AsyncMock(return_value=workflow_result)
    monkeypatch.setattr(prowler_route, "scan_workflow", scan_workflow)

    response = client.post(
        "/api/v1/prowler/scan",
        json={
            "region": "eu-west-1",
            "services": ["s3"],
            "prowler_args": ["--checks", "check-a"],
        },
    )

    assert response.status_code == 200
    assert response.json()["assistant_response"] == "Senior review of both assessments."
    assert response.json()["prowler_summary"] == "Prowler scan summary."
    assert response.json()["compliance"] == "Evidence-based compliance assessment."
    assert response.json()["findings"] == findings
    assert response.json()["sources"] == workflow_result["sources"]
    scan_workflow.assert_awaited_once()
    assert scan_workflow.await_args.kwargs == {
        "region": "eu-west-1",
        "services": ["s3"],
        "prowler_args": ["--checks", "check-a"],
    }
