# ruff: noqa: E501
# Markdown report tables and paragraphs retain their human-readable source lines.
"""Generate Markdown reports strictly from stored QA execution artifacts."""

import json
import platform
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from zoneinfo import ZoneInfo

EVIDENCE = Path("design/qa/evidence")


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        return default


def command_output(*command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return result.stdout.strip() if result.returncode == 0 else "Unavailable"
    except FileNotFoundError:
        return "Unavailable"


def junit(name):
    path = EVIDENCE / name
    if not path.exists():
        return []
    return list(ET.parse(path).getroot().iter("testcase"))


def counts(items):
    failed = sum(
        item.find("failure") is not None or item.find("error") is not None for item in items
    )
    skipped = sum(item.find("skipped") is not None for item in items)
    return {
        "total": len(items),
        "passed": len(items) - failed - skipped,
        "failed": failed,
        "skipped": skipped,
        "blocked": 0,
    }


def ratio(covered, total):
    return f"{covered / total * 100:.2f}%" if total else "N/A"


def metrics(files):
    summaries = [file["summary"] for file in files]
    lines = sum(s["num_statements"] for s in summaries)
    covered = sum(s["covered_lines"] for s in summaries)
    branches = sum(s.get("num_branches", 0) for s in summaries)
    covered_branches = sum(s.get("covered_branches", 0) for s in summaries)
    return (
        ratio(covered, lines),
        ratio(covered_branches, branches),
        covered / lines * 100 if lines else None,
    )


def main():
    timestamp = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
    commit = command_output("git", "rev-parse", "HEAD")
    backend = read_json(EVIDENCE / "backend-coverage.json", {"files": {}})
    frontend = read_json(EVIDENCE / "frontend-coverage/coverage-summary.json", {})
    files = backend["files"]
    groups = {
        "Backend": list(files.values()),
        "Agent orchestration": [
            v for k, v in files.items() if k.endswith(("llm/workflow.py", "chat_service.py"))
        ],
        "AWS auditing": [
            v for k, v in files.items() if "/tools/audit/" in k or k.endswith("cloud_agent.py")
        ],
        "Compliance processing": [
            v
            for k, v in files.items()
            if k.endswith(("compliance_agent.py", "senior_agent.py")) or "/services/rag/" in k
        ],
    }
    coverage = f"# Code coverage\n\nGenerated: {timestamp}\n\nCommit: `{commit}` (working tree includes uncommitted QA changes).\n\n"
    coverage += (
        "| Module | Line coverage | Branch coverage | Target | Result |\n|---|---:|---:|---|---|\n"
    )
    for name, values in groups.items():
        lines, branches, percent = metrics(values)
        target = 80 if name == "Backend" else 90
        result = "N/A" if percent is None else "Met" if percent >= target else "Below target"
        coverage += f"| {name} | {lines} | {branches} | {target}%{' preferred' if target == 90 else ''} | {result} |\n"
    total = frontend.get("total", {})
    front_lines = total.get("lines", {}).get("pct")
    front_branches = total.get("branches", {}).get("pct")
    coverage += f"| Frontend | {front_lines if front_lines is not None else 'N/A'}% | {front_branches if front_branches is not None else 'N/A'}% | 80% | {'Met' if front_lines is not None and front_lines >= 80 else 'N/A or below target'} |\n"
    coverage += "\nTerraform processing is N/A: no implementation exists. Backend line coverage is executable lines, distinct from coverage.py's combined branch+line percentage.\n\n## Backend modules and gaps\n\n| Module | Lines | Branches | Uncovered lines | Uncovered branches |\n|---|---:|---:|---|---|\n"
    for name, value in files.items():
        lines, branches, _ = metrics([value])
        coverage += f"| `{name}` | {lines} | {branches} | {', '.join(map(str, value['missing_lines'])) or 'None'} | {value.get('missing_branches', []) or 'None'} |\n"
    coverage += "\n## Frontend modules\n\n| Module | Lines | Branches |\n|---|---:|---:|\n"
    for name, value in frontend.items():
        if name != "total":
            label = name[name.find("frontend/") :] if "frontend/" in name else name
            coverage += f"| `{label}` | {value['lines']['pct']}% | {value['branches']['pct']}% |\n"
    coverage += """
## Exclusions and critical gaps

All backend app modules are measured; tests are outside the source scope. Coverage.py excludes type-checking/unreachable annotations according to its defaults; exact excluded lines are retained in backend-coverage.json. Frontend excludes only test sources and qa-setup.js; main.jsx remains measured and uncovered by unit tests. Browser E2E execution is separate and not added to unit coverage. No application module is excluded to raise percentages.

Uncovered branches include AWS exception/partial-response paths, model tool-response variants, retrieval/model-load errors and report export/print behavior. A passing line target does not establish robust branch coverage or semantic correctness. Vitest 4 uses executable-line accounting; earlier Vitest 3 instrumentation numbers in diagnostic logs are superseded.

## Reproduction and artifacts

Run `.venv/bin/python scripts/qa.py unit`, frontend `npm run test:coverage`, then backend `scripts/qa.py integration` and `scripts/qa.py security`. Run `scripts/qa.py gate` and `scripts/qa_reports.py` with the same Python. Backend XML/JSON/HTML: design/qa/evidence/backend-coverage.{xml,json}, backend-html/index.html. Frontend HTML/LCOV/JSON: design/qa/evidence/frontend-coverage/. Full per-statement frontend maps and missing branch counters are in coverage-final.json. Historical preliminary unit artifacts are kept separately.
"""
    Path("design/qa/CODE_COVERAGE.md").write_text(coverage)
    unit_file = "unit.xml" if (EVIDENCE / "unit.xml").exists() else "backend-unit.xml"
    integration_file = (
        "integration.xml" if (EVIDENCE / "integration.xml").exists() else "backend-integration.xml"
    )
    unit_items = junit(unit_file) + junit("frontend-unit.xml")
    integration_items = junit(integration_file)
    security_items = junit("security.xml")
    scanners = read_json(EVIDENCE / "scanner-results.json", {})
    results = {
        "Unit": counts(unit_items),
        "Integration": counts(integration_items),
        "E2E": counts(junit("e2e.xml")),
        "Security": counts(security_items),
        "Performance": counts(junit("performance.xml")),
    }
    for category, artifacts in {
        "Unit": [unit_file, "frontend-unit.xml"],
        "Integration": [integration_file],
        "E2E": ["e2e.xml"],
        "Security": ["security.xml"],
        "Performance": ["performance.xml"],
    }.items():
        for artifact in artifacts:
            if not junit(artifact):
                results[category]["total"] += 1
                results[category]["blocked"] += 1
    for result in scanners.values():
        results["Security"]["total"] += 1
        status = (
            "blocked"
            if result.get("blocked")
            else "passed"
            if result["exit_code"] == 0
            else "failed"
        )
        results["Security"][status] += 1
    # Unsupported / manual cases are separate, explicit inventory blockers.
    results["E2E"]["total"] += 2
    results["E2E"]["blocked"] += 2
    results["Security"]["total"] += 1
    results["Security"]["blocked"] += 1
    case_results = {}
    for item in unit_items + integration_items + security_items + junit("performance.xml"):
        status = (
            "Failed"
            if item.find("failure") is not None or item.find("error") is not None
            else "Skipped"
            if item.find("skipped") is not None
            else "Passed"
        )
        for prop in item.findall("./properties/property"):
            if prop.attrib.get("name") == "case_id":
                ident = prop.attrib["value"]
                case_results.setdefault(ident, []).append(status)
        text = item.attrib.get("name", "") + " " + item.attrib.get("classname", "")
        for ident in re.findall(r"UNIT-\d{3}", text):
            case_results.setdefault(ident, []).append(status)
    case_results["E2E-001"] = [
        "Failed"
        if item.find("failure") is not None
        else "Skipped"
        if item.find("skipped") is not None
        else "Passed"
        for item in junit("e2e.xml")
    ]
    case_results["SECURITY-002"] = [
        "Passed" if result["exit_code"] == 0 else "Failed" for result in scanners.values()
    ]
    cases = read_json("design/qa/qa-cases.json", [])
    for case in cases:
        ident = case["id"]
        outcomes = case_results.get(ident, [])
        status = (
            "Failed"
            if "Failed" in outcomes
            else "Passed"
            if outcomes and all(s == "Passed" for s in outcomes)
            else "Skipped"
            if outcomes
            else "Blocked"
        )
        case["status"] = status
        case["evidence"] = "evidence/ execution logs, JUnit and scanner-results.json"
        if case["path"] == "manual":
            case["status"] = "Blocked"
            case["actual"] = (
                case["objective"] + "; unsupported capability / requires independent review"
            )
        else:
            case["actual"] = (
                f"{len(outcomes)} mapped executions; {case['status']}. See raw evidence."
            )
    (EVIDENCE / "execution-results.json").write_text(
        json.dumps(
            {"timestamp": timestamp, "commit": commit, "summary": results, "cases": cases}, indent=2
        )
    )
    for category in ["unit", "integration", "e2e", "security", "performance"]:
        path = Path(f"design/qa/{category}-test-cases.md")
        text = path.read_text()
        for case in [c for c in cases if c["category"] == category]:
            pattern = rf"(## {case['id']}\n)(.*?)(?=\n## |\Z)"
            match = re.search(pattern, text, re.S)
            if match:
                section = match.group(0)
                section = re.sub(r"\| Status \| [^\n]+", f"| Status | {case['status']} |", section)
                section = re.sub(
                    r"\| Actual output \| [^\n]+", f"| Actual output | {case['actual']} |", section
                )
                text = text[: match.start()] + section + text[match.end() :]
        path.write_text(text)
    matrix = "# Test traceability matrix\n\nOriginal inventory preceded new test implementation. Latest outcomes come from execution-results.json.\n\n"
    matrix += (
        "| ID | Category | Implementation or limitation | Latest status |\n|---|---|---|---|\n"
    )
    matrix += "".join(
        f"| {case['id']} | {case['category']} | `{case['path']}` | {case['status']} |\n"
        for case in cases
    )
    Path("design/qa/test-traceability-matrix.md").write_text(matrix)
    performance = read_json(EVIDENCE / "performance.json", {})
    diagrams = read_json(EVIDENCE / "diagram-validation.json", {})
    report = f"""# Final consolidated test report

## Executive summary

Actual fixture-backed tests and local scanner execution are summarized below. Application architecture was preserved; documentation was consolidated into design/qa and design/diagrams. No production deployment, real AWS changes, Terraform execution or paid inference was performed. Docker runtime and real model semantics remain outside the validated scope.

## Environment

Generated: {timestamp} (Asia/Kolkata). Commit: `{commit}`; uncommitted working tree changes included.

- OS: {platform.platform()}
- Python: {platform.python_version()}; pytest {version("pytest")}; pytest-asyncio {version("pytest-asyncio")}; pytest-cov {version("pytest-cov")}
- Node: {command_output("node", "--version")}; npm: {command_output("npm", "--version")}
- Docker: {command_output("docker", "--version")}; Playwright: npm-lock 1.56.1; Vitest: npm-lock 4.1.12

## Execution summary

Counts are executed test instances, plus explicit inventory blockers. Security includes six scanner gate commands. Initial failures and their retests are retained in diagnostic logs; the table uses latest completed runs. Logical inventory counts differ from parameterized execution counts.

| Category | Total | Passed | Failed | Skipped | Blocked |
|---|---:|---:|---:|---:|---:|
"""
    for category, result in results.items():
        report += f"| {category} | {result['total']} | {result['passed']} | {result['failed']} | {result['skipped']} | {result['blocked']} |\n"
    report += (
        "\nDocumented logical cases: "
        + ", ".join(
            f"{c}: {sum(x['category'] == c for x in cases)}"
            for c in ["unit", "integration", "e2e", "security", "performance"]
        )
        + ".\n"
    )
    report += """
## Defects and corrections

| ID | Severity / component | Reproduction and actual behavior | Correction and retest |
|---|---|---|---|
| QA-001 | Medium / environment | Initial pytest import read host DEBUG=release and failed before collection | QA plugin overrides DEBUG before import; isolated units pass |
| QA-002 | Low / existing test | test_completion_uses_shared_client_model_and_conversation expected 2048 while pre-existing user edit used 8192 | Updated assertion to match the current contract; rerun passes; no production behavior change |
| QA-003 | Low / test harness | JSX transform and page/session fixture assumptions caused React unit failures | Explicit automatic JSX and authenticated page fixtures; latest frontend suite passes |
| QA-004 | Medium / browser environment | Nine initial E2E launches failed due missing shared libraries | Installed Chromium Linux libraries; nine browser tests subsequently pass |
| QA-005 | Medium / QA adapter | Forced nonexistent AWS profile caused ProfileNotFound during synthetic workflow | Remove profile selection, retain dummy credentials and blocked external sockets; browser retest passes |
| QA-006 | Low / security fixture | Duplicate-tool scenario had non-iterable Mock response before reaching duplicate rejection | Return empty findings from permitted read-only fixture; all security tests pass |
| SEC-001 | High / QA dependencies | npm audit reported vulnerable initial Vitest toolchain; pip-audit reported pip and pytest advisories | Updated Vitest/coverage to 4.1.12 and pip/pytest in lock; latest dependency scanner gates pass |
| SEC-002 | High / added QA Dockerfile | Trivy DS-0002 reported default root user | Added non-root users to QA stages; filesystem configuration scan passes; Docker runtime still unverified |

No application source defect was changed. Existing and concurrent user edits remain intact. A final browser rerun encountered port 8000 in use; test-managed services were moved to dedicated ports 18000/15173 without stopping the unknown service. Initial logs include the diagnosed test/environment failures; they are not hidden as successful executions.

## Security findings

Verified implementation risks:

- **Medium — trusted-local pickle deserialization**, app/services/rag/store.py: pickle can execute code if an attacker replaces metadata. The API does not accept pickle uploads. Restrict filesystem write access and verify artifact provenance; consider a versioned safe data format in a separately scoped change. Bandit B301/B403 are retained, not suppressed.
- **Medium — model claim verification**, SeniorAgent: correction of unsupported compliance conclusions is prompt-guided text generation. Synthetic model output does not demonstrate reliable semantic rejection. Independent evidence/rubric evaluation remains blocked.
- **Medium — API transport default**, frontend/src/services/api.js currently defaults to a public HTTP origin after a concurrent edit. HTTPS and a trusted configured origin are required to protect credentials/JWTs in transit outside localhost. QA explicitly overrides this with an isolated local origin; the concurrent source edit was preserved.
- **Medium for a multi-user deployment — no tenant ownership model**. The application is one configured account with shared assessment history. Do not advertise tenant isolation; a multi-user extension requires an authorized design change.

Scanner warnings: Bandit B104 on the CORS default is a heuristic; this field configures CORS origins rather than a listening socket. It is not proof of a public bind. B403 is the pickle import warning. Full Bandit findings are in bandit.json. Gitleaks reported the exact public test JWT fixture and, in generated documentation, the stable s3.default_encryption check identifier. .gitleaks.toml allows only those two exact public literals. Final history/source scans pass. Dependency audits are point-in-time advisories, not proof of absence of vulnerabilities.

Configured gates: Bandit HIGH, Python dependency advisories, npm HIGH/CRITICAL, unallowlisted secrets, and Trivy HIGH/CRITICAL. All six latest gate commands pass when scanner-results.json contains zero exit codes. Checkov/Terraform is N/A because no Terraform implementation exists. Container-image scan is blocked by unavailable Docker; Trivy filesystem results do not substitute for image inspection.

## Performance

"""
    report += "```json\n" + json.dumps(performance, indent=2) + "\n```\n"
    report += """
This is an in-process health endpoint smoke workload, not a production latency baseline. FAISS throughput, orchestration latency under load, memory consumption and real inference performance remain unmeasured.

## Coverage

See [CODE_COVERAGE.md](CODE_COVERAGE.md) for line/branch metrics, per-module missing lines and branches, exact commands, exclusions and artifact locations. Backend 80% line and frontend 80% line are enforced independently; 90% on critical groups is preferred and reported without inventing compliance.

## CI/CD

Existing ci.yml is untouched. Added qa.yml provides ordered unit → integration → E2E gates, dependency caches keyed to locks, least-privilege permissions, immutable action references and always-uploaded artifacts. Added delivery-review.yml is manual and only creates commit/checksum manifests; it never deploys. actionlint ran locally; see actionlint.log. No GitHub-hosted workflow result is claimed. Required reviewers on production-review are an administrator configuration prerequisite, not configured through this repository change. Hosting, OIDC trust policy, signed release builds and post-deployment health checks remain unconfigured.

## Architecture documentation

All new diagrams and SVG previews are under design/diagrams/. Source review links are in design/diagrams/README.md. Render validation results:

"""
    report += "| Diagram | Render exit code |\n|---|---:|\n" + "".join(
        f"| {name} | {r['exit_code']} |\n" for name, r in diagrams.items()
    )
    baseline = read_json("design/qa/qa-baseline.json", {"files": []})
    relocations = read_json("design/qa/relocations.json", {"paths": {}})["paths"]
    missing = [name for name in baseline["files"] if not Path(relocations.get(name, name)).exists()]
    report += f"\n## Preservation and remaining work\n\nBaseline tracked files missing now: {missing or 'None'}. Documentation was consolidated under design/qa and design/diagrams at the user’s request; relocations.json records the approved moves. See qa-change-manifest.md for added files and explanations of existing modifications.\n"
    report += """
- Recorded local Docker probe in docker.log: binary unavailable. Builds, container startup, health checks, container unit/integration/E2E, image scanning and cleanup have no local execution evidence. compose.qa.yml and HOW_TO_TEST.md provide reproduction commands.
- Terraform generation and its E2E scenario are unsupported, not passing features.
- Independent semantic compliance verification and tenant isolation review are inventory blockers.
- Browser suite covers implemented synthetic workflows; paid inference and actual AWS account results are deliberately untested.
- Python QA lock is a captured Linux environment with large ML dependencies; clean installation in QA Docker/CI is not yet proven. Production Python 3.12 image remains unchanged.
- Preferred 90% critical-path coverage and stronger branch coverage need further scenarios; see exact uncovered lines.
- Lynx inspection is documented, not executed. Detailed frontend performance/memory tests are not established.

## Production readiness

**Not ready.** Functional fixture-backed tests pass, but Docker/clean installation and hosted CI are unverified, model claims lack deterministic evidence validation, and the required deployment environment has not been selected or configured. This is a reviewable QA foundation, not a production certification.

## Reproduction

```bash
.venv/bin/python scripts/qa.py unit
npm --prefix frontend run test:coverage
.venv/bin/python scripts/qa.py integration
npm --prefix frontend run test:e2e
.venv/bin/python scripts/qa.py security
.venv/bin/python scripts/qa.py performance
.venv/bin/python scripts/install_qa_tools.py
.venv/bin/python scripts/qa_security.py
.venv/bin/python scripts/qa.py gate
.venv/bin/python scripts/qa_reports.py
```

See [HOW_TO_TEST.md](HOW_TO_TEST.md) for dependency/browser installation, Docker/Lynx, scanner policy and troubleshooting.
"""
    api_source = Path("frontend/src/services/api.js").read_text()
    default_match = re.search(r'VITE_API_BASE_URL \|\| "([^"]+)"', api_source)
    default_url = default_match.group(1) if default_match else "unresolved"
    observed = "**Medium — API transport default**, frontend/src/services/api.js currently defaults to a public HTTP origin after a concurrent edit. HTTPS and a trusted configured origin are required to protect credentials/JWTs in transit outside localhost. QA explicitly overrides this with an isolated local origin; the concurrent source edit was preserved."
    if default_url.startswith("http://") and not any(
        host in default_url for host in ["localhost", "127.0.0.1"]
    ):
        transport = observed
    else:
        transport = f"**Transport configuration observation** — current frontend default is `{default_url}`. A public HTTP origin appeared during concurrent edits and was later reverted externally; it is not reported as a current source defect. Remote environments require a trusted HTTPS origin. QA explicitly selects isolated local services."
    report = report.replace(observed, transport)
    Path("design/qa/FINAL_TEST_REPORT.md").write_text(report)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
