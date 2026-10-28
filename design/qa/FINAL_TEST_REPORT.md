# Final consolidated test report

## Executive summary

Actual fixture-backed tests and local scanner execution are summarized below. Application architecture was preserved; documentation was consolidated into design/qa and design/diagrams. No production deployment, real AWS changes, Terraform execution or paid inference was performed. Docker runtime and real model semantics remain outside the validated scope.

## Environment

Generated: 2026-10-28T19:13:48.818856+05:30 (Asia/Kolkata). Commit: `e65b14c5b7051d0289870dfaa999d2d1d2ac4d94`; uncommitted working tree changes included.

- OS: Linux-6.12.113+deb13-amd64-x86_64-with-glibc2.41
- Python: 3.13.5; pytest 9.2.0; pytest-asyncio 1.4.1; pytest-cov 6.3.0
- Node: v20.19.2; npm: 9.2.0
- Docker: Unavailable; Playwright: npm-lock 1.56.1; Vitest: npm-lock 4.1.12

## Execution summary

Counts are executed test instances, plus explicit inventory blockers. Security includes six scanner gate commands. Initial failures and their retests are retained in diagnostic logs; the table uses latest completed runs. Logical inventory counts differ from parameterized execution counts.

| Category | Total | Passed | Failed | Skipped | Blocked |
|---|---:|---:|---:|---:|---:|
| Unit | 55 | 55 | 0 | 0 | 0 |
| Integration | 40 | 40 | 0 | 0 | 0 |
| E2E | 11 | 9 | 0 | 0 | 2 |
| Security | 14 | 13 | 0 | 0 | 1 |
| Performance | 1 | 1 | 0 | 0 | 0 |

Documented logical cases: unit: 30, integration: 33, e2e: 3, security: 3, performance: 1.

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
- **Transport configuration observation** — current frontend default is `http://localhost:8000`. A public HTTP origin appeared during concurrent edits and was later reverted externally; it is not reported as a current source defect. Remote environments require a trusted HTTPS origin. QA explicitly selects isolated local services.
- **Medium for a multi-user deployment — no tenant ownership model**. The application is one configured account with shared assessment history. Do not advertise tenant isolation; a multi-user extension requires an authorized design change.

Scanner warnings: Bandit B104 on the CORS default is a heuristic; this field configures CORS origins rather than a listening socket. It is not proof of a public bind. B403 is the pickle import warning. Full Bandit findings are in bandit.json. Gitleaks reported the exact public test JWT fixture and, in generated documentation, the stable s3.default_encryption check identifier. .gitleaks.toml allows only those two exact public literals. Final history/source scans pass. Dependency audits are point-in-time advisories, not proof of absence of vulnerabilities.

Configured gates: Bandit HIGH, Python dependency advisories, npm HIGH/CRITICAL, unallowlisted secrets, and Trivy HIGH/CRITICAL. All six latest gate commands pass when scanner-results.json contains zero exit codes. Checkov/Terraform is N/A because no Terraform implementation exists. Container-image scan is blocked by unavailable Docker; Trivy filesystem results do not substitute for image inspection.

## Performance

```json
{
  "requests": 100,
  "workers": 8,
  "p95_ms": 26.44922699982999,
  "total_seconds": 0.2656538459996227,
  "transport": "in-process ASGI TestClient",
  "scope": "health endpoint only; excludes real network, cloud, inference and retrieval"
}
```

This is an in-process health endpoint smoke workload, not a production latency baseline. FAISS throughput, orchestration latency under load, memory consumption and real inference performance remain unmeasured.

## Coverage

See [CODE_COVERAGE.md](CODE_COVERAGE.md) for line/branch metrics, per-module missing lines and branches, exact commands, exclusions and artifact locations. Backend 80% line and frontend 80% line are enforced independently; 90% on critical groups is preferred and reported without inventing compliance.

## CI/CD

Existing ci.yml is untouched. Added qa.yml provides ordered unit → integration → E2E gates, dependency caches keyed to locks, least-privilege permissions, immutable action references and always-uploaded artifacts. Added delivery-review.yml is manual and only creates commit/checksum manifests; it never deploys. actionlint ran locally; see actionlint.log. No GitHub-hosted workflow result is claimed. Required reviewers on production-review are an administrator configuration prerequisite, not configured through this repository change. Hosting, OIDC trust policy, signed release builds and post-deployment health checks remain unconfigured.

## Architecture documentation

All new diagrams and SVG previews are under design/diagrams/. Source review links are in design/diagrams/README.md. Render validation results:

| Diagram | Render exit code |
|---|---:|
| aws-audit-sequence.mmd | 0 |
| ci-cd-pipeline.mmd | 0 |
| data-model.mmd | 0 |
| deployment-architecture.mmd | 0 |
| frontend-data-flow.mmd | 0 |
| frontend-state-machine.mmd | 0 |
| multi-agent-workflow.mmd | 0 |
| system-architecture.mmd | 0 |
| system-data-flow.mmd | 0 |

## Preservation and remaining work

Baseline tracked files missing now: None. Documentation was consolidated under design/qa and design/diagrams at the user’s request; relocations.json records the approved moves. See qa-change-manifest.md for added files and explanations of existing modifications.

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
