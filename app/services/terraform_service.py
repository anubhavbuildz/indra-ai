"""Constrained Terraform subprocess boundary."""

import os
import re
import subprocess
import tempfile
import threading
from pathlib import Path
from uuid import UUID, uuid4

from app.core.config import Settings
from app.core.errors import AppError
from app.services.llm_service import LLMService

MAX_OUTPUT_BYTES = 16_384
MAX_TERRAFORM_CODE_BYTES = 100_000
COMMANDS: dict[str, tuple[str, ...]] = {
    "version": ("version", "-json"),
    "fmt": ("fmt", "-check", "-no-color"),
    "init": ("init", "-backend=false", "-input=false", "-no-color"),
    "validate": ("validate", "-no-color"),
    "plan": ("plan", "-input=false", "-no-color", "-lock=false", "-refresh=false"),
}
UNSAFE_TERRAFORM = re.compile(
    r'^\s*(?:module|provisioner)\s+"|'
    r'^\s*backend\s+"|'
    r'^\s*(?:resource|data)\s+"(?!aws_)[^"]+"\s+"[^"]+"\s*\{|'
    r'^\s*provider\s+"(?!aws")[^"]+"\s*\{|'
    r'^\s*data\s+"external"\s+|'
    r"\bendpoints\s*\{|"
    r"\b(?:local-exec|remote-exec)\b|"
    r"\b(?:access_key|secret_key|secret_access_key|session_token|token|password|"
    r"client_secret|api_key|private_key)\s*=|"
    r'\bsource\s*=\s*["\'](?!hashicorp/aws["\'])[^"\']+["\']',
    re.IGNORECASE | re.MULTILINE,
)


class TerraformService:
    """Run a fixed set of Terraform operations in server-created workspaces."""

    def __init__(self, settings: Settings, timeout_seconds: int = 60) -> None:
        self.settings = settings
        self.timeout_seconds = timeout_seconds

    def create_workspace(self, project_id: str) -> tuple[str, Path]:
        try:
            safe_project_id = str(UUID(project_id))
        except ValueError as exc:
            raise AppError(422, "invalid_project_id", "Project ID must be a UUID.") from exc
        root = self.settings.terraform_workspace_root.resolve()
        root.mkdir(parents=True, exist_ok=True)
        project_root = (root / safe_project_id).resolve()
        if not project_root.is_relative_to(root):
            raise AppError(400, "invalid_workspace", "Workspace path is not allowed.")
        project_root.mkdir(parents=True, exist_ok=True)
        workspace = Path(tempfile.mkdtemp(prefix="operation-", dir=project_root)).resolve()
        if not workspace.is_relative_to(root):
            raise AppError(400, "invalid_workspace", "Workspace path is not allowed.")
        return str(uuid4()), workspace

    @staticmethod
    def validate_code(code: str) -> None:
        if len(code.encode("utf-8")) > MAX_TERRAFORM_CODE_BYTES:
            raise AppError(
                413, "terraform_code_too_large", "Terraform code exceeds the size limit."
            )
        if UNSAFE_TERRAFORM.search(code):
            raise AppError(
                422,
                "terraform_policy_rejected",
                "Terraform code contains a construct disallowed by the V1 execution policy.",
            )

    def _run(self, operation: str, workspace: Path) -> tuple[int, str, bool]:
        command = COMMANDS.get(operation)
        if command is None:
            raise AppError(
                400, "terraform_command_not_allowed", "Terraform command is not allowed."
            )
        root = self.settings.terraform_workspace_root.resolve()
        working_directory = workspace.resolve()
        if not working_directory.is_relative_to(root) or not working_directory.is_dir():
            raise AppError(400, "invalid_workspace", "Terraform workspace is not allowed.")
        output: list[bytearray] = [bytearray(), bytearray()]
        output_sizes = [0, 0]
        try:
            try:
                process = subprocess.Popen(
                    [self.settings.terraform_bin, *command],
                    cwd=working_directory,
                    shell=False,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=self._terraform_environment(),
                )
            except FileNotFoundError as exc:
                raise AppError(
                    503, "terraform_unavailable", "Terraform executable was not found."
                ) from exc

            def drain(stream, index: int) -> None:
                while chunk := stream.read(4_096):
                    output_sizes[index] += len(chunk)
                    available = MAX_OUTPUT_BYTES - len(output[index])
                    if available > 0:
                        output[index].extend(chunk[:available])

            assert process.stdout is not None
            assert process.stderr is not None
            readers = [
                threading.Thread(target=drain, args=(process.stdout, 0), daemon=True),
                threading.Thread(target=drain, args=(process.stderr, 1), daemon=True),
            ]
            for reader in readers:
                reader.start()
            try:
                return_code = process.wait(timeout=self.timeout_seconds)
            except subprocess.TimeoutExpired as exc:
                process.kill()
                process.wait()
                for reader in readers:
                    reader.join()
                raise AppError(
                    504, "terraform_timeout", "Terraform operation exceeded its time limit."
                ) from exc
            for reader in readers:
                reader.join()
            text = (output[0] + output[1]).decode("utf-8", errors="replace")
            truncated = any(size > MAX_OUTPUT_BYTES for size in output_sizes)
            return return_code, text, truncated
        finally:
            if "process" in locals():
                if process.stdout:
                    process.stdout.close()
                if process.stderr:
                    process.stderr.close()

    @staticmethod
    def _terraform_environment() -> dict[str, str]:
        """Pass only runtime and AWS credential-chain variables to Terraform."""
        allowed = {
            "PATH",
            "HOME",
            "TMPDIR",
            "TEMP",
            "TMP",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_SESSION_TOKEN",
            "AWS_PROFILE",
            "AWS_DEFAULT_PROFILE",
            "AWS_REGION",
            "AWS_DEFAULT_REGION",
            "AWS_CONFIG_FILE",
            "AWS_SHARED_CREDENTIALS_FILE",
            "AWS_EC2_METADATA_DISABLED",
            "AWS_ROLE_ARN",
            "AWS_WEB_IDENTITY_TOKEN_FILE",
            "AWS_ROLE_SESSION_NAME",
            "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI",
            "AWS_CONTAINER_CREDENTIALS_FULL_URI",
            "AWS_CONTAINER_AUTHORIZATION_TOKEN",
            "AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE",
            "AWS_CA_BUNDLE",
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "NO_PROXY",
            "SSL_CERT_FILE",
            "SSL_CERT_DIR",
        }
        return {key: value for key, value in os.environ.items() if key in allowed}

    async def generate(self, project_id: str, requirements: str) -> dict[str, object]:
        answer = await LLMService(self.settings).complete(
            "Produce a minimal proposed Terraform configuration for the following requirements. "
            "Return only HCL in a single terraform code block. Do not include deployment commands, "
            "credentials, modules, provisioners, backend blocks, or remote sources.\n\n"
            f"Requirements:\n{requirements}",
            [],
        )
        code_match = re.search(
            r"```(?:terraform|hcl)?\s*(.*?)```", answer, re.IGNORECASE | re.DOTALL
        )
        code = code_match.group(1).strip() if code_match else answer.strip()
        self.validate_code(code)
        return {"status": "proposed", "code": code, "executed": False, "project_id": project_id}

    def validate(self, project_id: str, code: str) -> dict[str, object]:
        self.validate_code(code)
        operation_id, workspace = self.create_workspace(project_id)
        (workspace / "main.tf").write_text(code, encoding="utf-8")
        for operation in ("init", "fmt", "validate"):
            exit_code, _, truncated = self._run(operation, workspace)
            if exit_code != 0:
                return {
                    "status": "invalid",
                    "operation_id": operation_id,
                    "summary": f"Terraform {operation} did not succeed; raw output is withheld.",
                    "exit_code": exit_code,
                    "output_truncated": truncated,
                }
        return {
            "status": "valid",
            "operation_id": operation_id,
            "summary": "Terraform formatting and validation completed.",
            "exit_code": 0,
            "output_truncated": False,
        }

    def plan(self, project_id: str, code: str) -> dict[str, object]:
        self.validate_code(code)
        operation_id, workspace = self.create_workspace(project_id)
        (workspace / "main.tf").write_text(code, encoding="utf-8")
        for operation in ("init", "validate", "plan"):
            exit_code, _, truncated = self._run(operation, workspace)
            if exit_code != 0:
                return {
                    "status": "failed",
                    "operation_id": operation_id,
                    "summary": f"Terraform {operation} did not succeed; raw output is withheld.",
                    "exit_code": exit_code,
                    "output_truncated": truncated,
                }
        return {
            "status": "planned",
            "operation_id": operation_id,
            "summary": "Terraform plan completed; no changes were applied.",
            "exit_code": 0,
            "output_truncated": False,
        }
