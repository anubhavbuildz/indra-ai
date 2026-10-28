"""Scanner policy: dependency/secret failures, Bandit HIGH, Trivy HIGH/CRITICAL block CI."""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    evidence = Path("design/qa/evidence")
    evidence.mkdir(parents=True, exist_ok=True)
    tools = Path("/tmp/indra-qa-bin")
    commands = {
        "bandit": [
            sys.executable,
            "-m",
            "bandit",
            "-r",
            "app",
            "-lll",
            "-f",
            "json",
            "-o",
            str(evidence / "bandit-gate.json"),
        ],
        "pip-audit": [
            sys.executable,
            "-m",
            "pip_audit",
            "--format",
            "json",
            "--output",
            str(evidence / "pip-audit.json"),
        ],
        "npm-audit": ["npm", "--prefix", "frontend", "audit", "--audit-level=high", "--json"],
        "gitleaks-history": [
            str(tools / "gitleaks"),
            "git",
            "--config",
            ".gitleaks.toml",
            "--redact",
            "--report-format",
            "json",
            "--report-path",
            str(evidence / "gitleaks-history.json"),
        ],
        "trivy": [
            str(tools / "trivy"),
            "fs",
            "--scanners",
            "vuln,misconfig",
            "--severity",
            "HIGH,CRITICAL",
            "--exit-code",
            "1",
            "--skip-dirs",
            ".venv",
            "--skip-dirs",
            "frontend/node_modules",
            "--skip-dirs",
            str(evidence),
            "--format",
            "json",
            "--output",
            str(evidence / "trivy.json"),
            ".",
        ],
    }
    with (evidence / "bandit.log").open("w") as advisory_log:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "bandit",
                "-r",
                "app",
                "-f",
                "json",
                "-o",
                str(evidence / "bandit.json"),
            ],
            stdout=advisory_log,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=600,
        )
    with tempfile.TemporaryDirectory(prefix="indra-scan-") as directory:
        paths = subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"], text=True
        ).splitlines()
        for filename in paths:
            path = Path(filename)
            if not path.is_file() or filename.startswith("design/qa/evidence/"):
                continue
            if path.name.startswith(".env") and path.name != ".env.example":
                continue
            target = Path(directory) / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        commands["gitleaks-worktree"] = [
            str(tools / "gitleaks"),
            "dir",
            directory,
            "--config",
            ".gitleaks.toml",
            "--redact",
            "--report-format",
            "json",
            "--report-path",
            str(evidence / "gitleaks-worktree.json"),
        ]
        results = {}
        for name, command in commands.items():
            with (evidence / f"{name}.log").open("w") as log:
                try:
                    result = subprocess.run(
                        command, stdout=log, stderr=subprocess.STDOUT, check=False, timeout=600
                    )
                    results[name] = {"exit_code": result.returncode, "command": command}
                except (OSError, subprocess.TimeoutExpired) as error:
                    log.write(f"BLOCKED: {type(error).__name__}\n")
                    results[name] = {"exit_code": 127, "command": command, "blocked": True}
            if name == "npm-audit":
                shutil.copyfile(evidence / "npm-audit.log", evidence / "npm-audit.json")
    (evidence / "scanner-results.json").write_text(json.dumps(results, indent=2))
    print(json.dumps({name: result["exit_code"] for name, result in results.items()}, indent=2))
    return int(any(result["exit_code"] for result in results.values()))


if __name__ == "__main__":
    raise SystemExit(main())
