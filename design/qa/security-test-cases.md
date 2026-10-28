# Security test cases

Designed before new test code. Counts are logical cases; parameterized execution counts may differ. External AWS/model calls must be stubbed.

## SECURITY-001

| Field | Value |
|---|---|
| Test ID | SECURITY-001 |
| Feature | JWT forgery and destructive tool allowlist rejection |
| Test category | security |
| Priority | High |
| Objective | JWT forgery and destructive tool allowlist rejection |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Named test fixtures in `tests/test_qa_security.py`; invalid variants where named |
| Steps | Run the mapped test using HOW_TO_TEST.md commands; inspect assertions and evidence |
| Expected output | All mapped assertions pass; no live cloud or paid inference |
| Actual output | 7 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## SECURITY-002

| Field | Value |
|---|---|
| Test ID | SECURITY-002 |
| Feature | Ruff, Bandit, pip-audit, npm audit, Gitleaks, Checkov, Trivy |
| Test category | security |
| Priority | High |
| Objective | Ruff, Bandit, pip-audit, npm audit, Gitleaks, Checkov, Trivy |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Named test fixtures in `scanners`; invalid variants where named |
| Steps | Run the mapped test using HOW_TO_TEST.md commands; inspect assertions and evidence |
| Expected output | All mapped assertions pass; no live cloud or paid inference |
| Actual output | 6 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## SECURITY-003

| Field | Value |
|---|---|
| Test ID | SECURITY-003 |
| Feature | Tenant isolation unsupported by single-account model; deployment review required |
| Test category | security |
| Priority | High |
| Objective | Tenant isolation unsupported by single-account model; deployment review required |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Named test fixtures in `manual`; invalid variants where named |
| Steps | Run the mapped test using HOW_TO_TEST.md commands; inspect assertions and evidence |
| Expected output | All mapped assertions pass; no live cloud or paid inference |
| Actual output | Tenant isolation unsupported by single-account model; deployment review required; unsupported capability / requires independent review |
| Status | Blocked |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Manual: unsupported feature or review requirement |

