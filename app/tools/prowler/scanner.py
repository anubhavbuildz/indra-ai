"""Agent-callable Prowler scan tool."""

import asyncio
import shlex
from typing import Any

from app.core.config import Settings


class Scanner:
    """Run a bounded Prowler scan using scope supplied by the request."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def run_scan(self, command_string: str) -> dict[str, Any]:
        """Run only a Prowler AWS command, treating every argument as data."""
        try:
            arguments = shlex.split(command_string)
        except ValueError:
            return {"status": "error", "message": "Invalid Prowler command."}

        if (
            len(arguments) < 2
            or arguments[0].rsplit("/", 1)[-1] != self.settings.prowler_bin.rsplit("/", 1)[-1]
            or arguments[1] != "aws"
            or any(any(char in argument for char in ";|&<>`$") for argument in arguments)
        ):
            return {"status": "error", "message": "Only Prowler AWS commands are allowed."}

        try:
            process = await asyncio.create_subprocess_exec(
                self.settings.prowler_bin,
                *arguments[1:],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.settings.prowler_timeout_seconds,
            )

            stdout_str = stdout.decode().strip()
            stderr_str = stderr.decode().strip()

            if process.returncode == 0:
                return {"status": "success", "exit_code": process.returncode, "output": stdout_str}

            return {
                "status": "failed",
                "exit_code": process.returncode,
                "error": stderr_str,
                "partial_output": stdout_str,
            }

        except TimeoutError:
            if process.returncode is None:
                process.kill()
                await process.wait()
            return {"status": "error", "message": "The Prowler command timed out."}
        except FileNotFoundError:
            return {"status": "error", "message": "Prowler executable was not found."}
