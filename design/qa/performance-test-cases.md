# Performance test cases

Designed before new test code. Counts are logical cases; parameterized execution counts may differ. External AWS/model calls must be stubbed.

## PERFORMANCE-001

| Field | Value |
|---|---|
| Test ID | PERFORMANCE-001 |
| Feature | 100 health requests across 8 threads; p95 under 500ms, total under 10s; local fixture-only baseline |
| Test category | performance |
| Priority | High |
| Objective | 100 health requests across 8 threads; p95 under 500ms, total under 10s; local fixture-only baseline |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Named test fixtures in `tests/test_qa_performance.py`; invalid variants where named |
| Steps | Run the mapped test using HOW_TO_TEST.md commands; inspect assertions and evidence |
| Expected output | All mapped assertions pass; no live cloud or paid inference |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

