"""Run the Prowler CLI with dynamically selected Prowler options."""

import asyncio
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import TypedDict
from uuid import uuid4

from app.core.config import Settings
from app.core.errors import AppError


class ScanResult(TypedDict):
    operation_id: str
    region: str
    findings: list[dict[str, object]]
    findings_count: int


async def run_prowler_scan(
    settings: Settings,
    *,
    region: str | None = None,
    services: list[str] | None = None,
    prowler_args: list[str] | None = None,
) -> ScanResult:
    """Run Prowler without invoking a shell and parse its JSON-OCSF report."""
    scan_region = region or settings.aws_region
    extra_args = prowler_args or []
    if len(extra_args) > 50 or any(
        not isinstance(arg, str)
        or not arg
        or len(arg) > 256
        or "\x00" in arg
        or arg.partition("=")[0]
        in {
            "--output-formats",
            "--output-directory",
            "--output-filename",
            "--region",
            "--services",
            "--profile",
            "--provider",
        }
        for arg in extra_args
    ):
        raise AppError(422, "invalid_prowler_args", "Additional Prowler arguments are invalid.")

    with tempfile.TemporaryDirectory(prefix="indra-prowler-") as output_dir:
        command = [
            settings.prowler_bin,
            "aws",
            "--output-formats",
            "json-ocsf",
            "--output-directory",
            output_dir,
            "--region",
            scan_region,
            "--ignore-exit-code-3",
        ]
        if services:
            command.extend(["--services", *services])
        command.extend(extra_args)
        try:
            process = await asyncio.to_thread(
                subprocess.run,
                command,
                shell=False,
                cwd=output_dir,
                env=_aws_environment(),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=settings.prowler_timeout_seconds,
                check=False,
            )
        except FileNotFoundError as exc:
            raise AppError(503, "prowler_unavailable", "Prowler executable was not found.") from exc
        except subprocess.TimeoutExpired as exc:
            raise AppError(504, "prowler_timeout", "Prowler scan timed out.") from exc
        if process.returncode != 0:
            raise AppError(502, "prowler_scan_failed", "Prowler scan did not complete.")
        findings = _read_findings(Path(output_dir))

    return {
        "operation_id": str(uuid4()),
        "region": scan_region,
        "findings": findings,
        "findings_count": len(findings),
    }


def _read_findings(output_dir: Path) -> list[dict[str, object]]:
    report_files = sorted(output_dir.rglob("*.json"))
    if not report_files:
        raise AppError(502, "prowler_output_missing", "Prowler did not produce a JSON report.")
    findings: list[dict[str, object]] = []
    total_bytes = 0
    for report in report_files:
        total_bytes += report.stat().st_size
        if total_bytes > 5_000_000:
            raise AppError(413, "prowler_report_too_large", "Prowler report is too large.")
        try:
            parsed = json.loads(report.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise AppError(
                502, "prowler_output_invalid", "Prowler JSON report is invalid."
            ) from exc
        if isinstance(parsed, dict):
            parsed = parsed.get("findings", parsed.get("items", [parsed]))
        if not isinstance(parsed, list) or any(not isinstance(item, dict) for item in parsed):
            raise AppError(502, "prowler_output_invalid", "Prowler report has an invalid shape.")
        findings.extend(parsed)
        if len(findings) > 5_000:
            raise AppError(413, "prowler_report_too_large", "Prowler report has too many findings.")
    return findings


def _aws_environment() -> dict[str, str]:
    allowed = {
        "PATH", "HOME", "TMPDIR", "TEMP", "TMP", "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "AWS_PROFILE",
        "AWS_DEFAULT_PROFILE", "AWS_REGION", "AWS_DEFAULT_REGION",
        "AWS_CONFIG_FILE", "AWS_SHARED_CREDENTIALS_FILE", "AWS_EC2_METADATA_DISABLED",
        "AWS_ROLE_ARN", "AWS_WEB_IDENTITY_TOKEN_FILE", "AWS_ROLE_SESSION_NAME",
        "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI", "AWS_CONTAINER_CREDENTIALS_FULL_URI",
        "AWS_CONTAINER_AUTHORIZATION_TOKEN", "AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE",
        "AWS_CA_BUNDLE", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY",
        "SSL_CERT_FILE", "SSL_CERT_DIR",
    }
    return {key: value for key, value in os.environ.items() if key in allowed}
