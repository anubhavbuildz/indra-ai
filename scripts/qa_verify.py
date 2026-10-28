"""Read-only final checks: repository preservation, case traceability and generated evidence."""

import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    baseline = json.loads(Path("design/qa/qa-baseline.json").read_text())
    relocations = json.loads(Path("design/qa/relocations.json").read_text())["paths"]
    missing = [
        name for name in baseline["files"] if not Path(relocations.get(name, name)).is_file()
    ]
    changes = subprocess.check_output(
        ["git", "diff", "--name-status", "--diff-filter=DR"], text=True
    )
    assert not missing, f"Baseline paths missing: {missing}"
    unauthorized = [line for line in changes.splitlines() if line.split("\t")[1] not in relocations]
    assert not unauthorized, f"Unexpected move/delete: {unauthorized}"
    cases = json.loads(Path("design/qa/qa-cases.json").read_text())
    results = json.loads(Path("design/qa/evidence/execution-results.json").read_text())
    assert {c["id"] for c in cases} == {c["id"] for c in results["cases"]}
    for case in results["cases"]:
        assert case["status"] in {"Passed", "Failed", "Skipped", "Blocked"}
        assert case["actual"]
        if case["path"].startswith("tests/") and "::" in case["path"]:
            assert Path(case["path"].split("::")[0]).is_file()
    for stage in ["unit", "integration", "security", "performance"]:
        recorded = json.loads(Path(f"design/qa/evidence/{stage}-execution.json").read_text())
        assert recorded["exit_code"] == 0, f"Failed stage: {stage}"
        ET.parse(f"design/qa/evidence/{stage}.xml")
    unit = json.loads(Path("design/qa/evidence/unit-execution.json").read_text())
    integration = json.loads(Path("design/qa/evidence/integration-execution.json").read_text())
    assert unit["finished_utc"] < integration["started_utc"]
    diagrams = json.loads(Path("design/qa/evidence/diagram-validation.json").read_text())
    assert len(diagrams) == 9
    assert all(value["exit_code"] == 0 for value in diagrams.values())
    assert all(Path("design/diagrams", name).with_suffix(".svg").is_file() for name in diagrams)
    assert all(
        result["exit_code"] == 0
        for result in json.loads(
            Path("design/qa/evidence/scanner-results.json").read_text()
        ).values()
    )
    report = {
        "baseline_files_preserved": len(baseline["files"]),
        "unauthorized_moves_or_deletions": 0,
        "authorized_document_moves": len(relocations),
        "documented_cases": len(cases),
        "diagrams_rendered": len(diagrams),
        "unit_before_integration": True,
        "summary": results["summary"],
    }
    Path("design/qa/evidence/final-verification.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
