"""Run one QA level with safe fixtures, evidence logs, and preserved exit status."""

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

EVIDENCE = Path("design/qa/evidence")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["unit", "integration", "security", "performance", "gate"])
    stage = parser.parse_args().stage
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    if stage == "gate":
        data = json.loads((EVIDENCE / "backend-coverage.json").read_text())["totals"]
        lines = data["covered_lines"] / data["num_statements"] * 100
        print(f"Backend line coverage: {lines:.2f}% (required 80%)")
        return int(lines < 80)
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-c",
        "pytest-qa.ini",
        "-p",
        "tests.qa_plugin",
        "-m",
        stage,
        f"--junitxml={EVIDENCE}/{stage}.xml",
    ]
    if stage != "performance":
        command += [
            "--cov=app",
            "--cov-fail-under=0",
            f"--cov-report=json:{EVIDENCE}/backend-coverage.json",
            f"--cov-report=xml:{EVIDENCE}/backend-coverage.xml",
            f"--cov-report=html:{EVIDENCE}/backend-html",
        ]
        if stage != "unit":
            command += ["--cov-append"]
    started = datetime.now(UTC).isoformat()
    with (EVIDENCE / f"{stage}.log").open("w") as stream:
        result = subprocess.run(
            command, stdout=stream, stderr=subprocess.STDOUT, check=False, env=os.environ.copy()
        )
    (EVIDENCE / f"{stage}-execution.json").write_text(
        json.dumps(
            {
                "stage": stage,
                "command": command,
                "started_utc": started,
                "finished_utc": datetime.now(UTC).isoformat(),
                "exit_code": result.returncode,
            },
            indent=2,
        )
    )
    print((EVIDENCE / f"{stage}.log").read_text())
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
