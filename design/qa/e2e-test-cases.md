# E2E test cases

Designed before new test code. Counts are logical cases; parameterized execution counts may differ. External AWS/model calls must be stubbed.

## E2E-001

| Field | Value |
|---|---|
| Test ID | E2E-001 |
| Feature | Actual login, navigation, controlled audit, persisted report, session expiry, responsive viewports |
| Test category | e2e |
| Priority | High |
| Objective | Actual login, navigation, controlled audit, persisted report, session expiry, responsive viewports |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Named test fixtures in `frontend/e2e/workspace.spec.js`; invalid variants where named |
| Steps | Run the mapped test using HOW_TO_TEST.md commands; inspect assertions and evidence |
| Expected output | All mapped assertions pass; no live cloud or paid inference |
| Actual output | 9 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## E2E-002

| Field | Value |
|---|---|
| Test ID | E2E-002 |
| Feature | Terraform workflow absent; cannot test unsupported capability |
| Test category | e2e |
| Priority | High |
| Objective | Terraform workflow absent; cannot test unsupported capability |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Named test fixtures in `manual`; invalid variants where named |
| Steps | Run the mapped test using HOW_TO_TEST.md commands; inspect assertions and evidence |
| Expected output | All mapped assertions pass; no live cloud or paid inference |
| Actual output | Terraform workflow absent; cannot test unsupported capability; unsupported capability / requires independent review |
| Status | Blocked |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Manual: unsupported feature or review requirement |

## E2E-003

| Field | Value |
|---|---|
| Test ID | E2E-003 |
| Feature | Semantic compliance rejection requires independent evidence rubric; not enforced by deterministic code |
| Test category | e2e |
| Priority | High |
| Objective | Semantic compliance rejection requires independent evidence rubric; not enforced by deterministic code |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Named test fixtures in `manual`; invalid variants where named |
| Steps | Run the mapped test using HOW_TO_TEST.md commands; inspect assertions and evidence |
| Expected output | All mapped assertions pass; no live cloud or paid inference |
| Actual output | Semantic compliance rejection requires independent evidence rubric; not enforced by deterministic code; unsupported capability / requires independent review |
| Status | Blocked |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Manual: unsupported feature or review requirement |

