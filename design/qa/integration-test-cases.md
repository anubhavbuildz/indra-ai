# Integration test cases

Designed before new test code. Counts are logical cases; parameterized execution counts may differ. External AWS/model calls must be stubbed.

## INTEGRATION-001

| Field | Value |
|---|---|
| Test ID | INTEGRATION-001 |
| Feature | list and read assessments with senior review |
| Test category | integration |
| Priority | High |
| Objective | list and read assessments with senior review |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: assessment_client; controlled inputs defined in `tests/test_assessments.py::test_list_and_read_assessments_with_senior_review` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_assessments.py::test_list_and_read_assessments_with_senior_review -v`; compare assertions below to execution evidence |
| Expected output | `listed.status_code == 200`; `listed.json()['items'][0]['id'] == assessment_id`; `listed.json()['items'][0]['senior_review'] == 'Senior review output.'`; `listed.json()['items'][0]['created_at'].endswith('Z')`; `listed.json()['items'][0]['updated_at'].endswith('Z')`; `fetched.status_code == 200`; `fetched.json()['question'] == 'Review this AWS account'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-002

| Field | Value |
|---|---|
| Test ID | INTEGRATION-002 |
| Feature | missing assessment has stable error |
| Test category | integration |
| Priority | High |
| Objective | missing assessment has stable error |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: assessment_client; controlled inputs defined in `tests/test_assessments.py::test_missing_assessment_has_stable_error` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_assessments.py::test_missing_assessment_has_stable_error -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 404`; `response.json()['error']['code'] == 'assessment_not_found'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-003

| Field | Value |
|---|---|
| Test ID | INTEGRATION-003 |
| Feature | login issues verifiable access token |
| Test category | integration |
| Priority | High |
| Objective | login issues verifiable access token |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: auth_client; controlled inputs defined in `tests/test_auth.py::test_login_issues_verifiable_access_token` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_auth.py::test_login_issues_verifiable_access_token -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 200`; `result['token_type'] == 'bearer'`; `result['expires_in'] == 2 * 60 * 60`; `verify_access_token(result['access_token'], settings)['sub'] == 'test-user'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-004

| Field | Value |
|---|---|
| Test ID | INTEGRATION-004 |
| Feature | login rejects invalid credentials |
| Test category | integration |
| Priority | High |
| Objective | login rejects invalid credentials |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: auth_client; controlled inputs defined in `tests/test_auth.py::test_login_rejects_invalid_credentials` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_auth.py::test_login_rejects_invalid_credentials -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 401`; `response.json()['error']['code'] == 'invalid_credentials'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-005

| Field | Value |
|---|---|
| Test ID | INTEGRATION-005 |
| Feature | versioned routes reject missing bearer token |
| Test category | integration |
| Priority | High |
| Objective | versioned routes reject missing bearer token |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: auth_client, method, path, payload; controlled inputs defined in `tests/test_auth.py::test_versioned_routes_reject_missing_bearer_token` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_auth.py::test_versioned_routes_reject_missing_bearer_token -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 401`; `response.json()['error']['code'] == 'authentication_required'` |
| Actual output | 4 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-006

| Field | Value |
|---|---|
| Test ID | INTEGRATION-006 |
| Feature | protected route accepts login token |
| Test category | integration |
| Priority | High |
| Objective | protected route accepts login token |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: auth_client; controlled inputs defined in `tests/test_auth.py::test_protected_route_accepts_login_token` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_auth.py::test_protected_route_accepts_login_token -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 200`; `'available' in response.json()` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-007

| Field | Value |
|---|---|
| Test ID | INTEGRATION-007 |
| Feature | protected route rejects invalid bearer token |
| Test category | integration |
| Priority | High |
| Objective | protected route rejects invalid bearer token |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: auth_client; controlled inputs defined in `tests/test_auth.py::test_protected_route_rejects_invalid_bearer_token` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_auth.py::test_protected_route_rejects_invalid_bearer_token -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 401`; `response.json()['error']['code'] == 'invalid_token'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-008

| Field | Value |
|---|---|
| Test ID | INTEGRATION-008 |
| Feature | openapi documents bearer auth on protected routes |
| Test category | integration |
| Priority | High |
| Objective | openapi documents bearer auth on protected routes |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: auth_client; controlled inputs defined in `tests/test_auth.py::test_openapi_documents_bearer_auth_on_protected_routes` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_auth.py::test_openapi_documents_bearer_auth_on_protected_routes -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 200`; `'security' not in schema['paths']['/api/v1/auth/login']['post']`; `schema['paths']['/api/v1/chat']['post']['security'] == [{'HTTPBearer': []}]` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-009

| Field | Value |
|---|---|
| Test ID | INTEGRATION-009 |
| Feature | login reports missing configuration |
| Test category | integration |
| Priority | High |
| Objective | login reports missing configuration |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_auth.py::test_login_reports_missing_configuration` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_auth.py::test_login_reports_missing_configuration -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 503`; `response.json()['error']['code'] == 'login_not_configured'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-010

| Field | Value |
|---|---|
| Test ID | INTEGRATION-010 |
| Feature | missing credentials return not configured |
| Test category | integration |
| Priority | High |
| Objective | missing credentials return not configured |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_aws.py::test_missing_credentials_return_not_configured` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_aws.py::test_missing_credentials_return_not_configured -v`; compare assertions below to execution evidence |
| Expected output | `response['status'] == 'not_configured'`; `response['account'] is None` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-011

| Field | Value |
|---|---|
| Test ID | INTEGRATION-011 |
| Feature | identity returns only non secret metadata |
| Test category | integration |
| Priority | High |
| Objective | identity returns only non secret metadata |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_aws.py::test_identity_returns_only_non_secret_metadata` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_aws.py::test_identity_returns_only_non_secret_metadata -v`; compare assertions below to execution evidence |
| Expected output | `response['status'] == 'configured'`; `response['account'] == '000000000000'`; `'secret' not in str(response).lower()` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-012

| Field | Value |
|---|---|
| Test ID | INTEGRATION-012 |
| Feature | get enabled regions returns enabled region names |
| Test category | integration |
| Priority | High |
| Objective | get enabled regions returns enabled region names |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_aws_audit.py::test_get_enabled_regions_returns_enabled_region_names` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_aws_audit.py::test_get_enabled_regions_returns_enabled_region_names -v`; compare assertions below to execution evidence |
| Expected output | `auditor.get_enabled_regions() == ['us-east-1', 'eu-west-1']` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-013

| Field | Value |
|---|---|
| Test ID | INTEGRATION-013 |
| Feature | s3 audit reports disabled public access and missing encryption |
| Test category | integration |
| Priority | High |
| Objective | s3 audit reports disabled public access and missing encryption |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_aws_audit.py::test_s3_audit_reports_disabled_public_access_and_missing_encryption` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_aws_audit.py::test_s3_audit_reports_disabled_public_access_and_missing_encryption -v`; compare assertions below to execution evidence |
| Expected output | `{finding['check_id'] for finding in findings} == {'s3.public_access_block', 's3.default_encryption', 's3.public_bucket_policy', 's3.public_bucket_acl', 's3.versioning', 's3.access_logging'}`; `all((finding['resource'] == 'example-bucket' for finding in findings))` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-014

| Field | Value |
|---|---|
| Test ID | INTEGRATION-014 |
| Feature | iam audit reports root access keys |
| Test category | integration |
| Priority | High |
| Objective | iam audit reports root access keys |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_aws_audit.py::test_iam_audit_reports_root_access_keys` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_aws_audit.py::test_iam_audit_reports_root_access_keys -v`; compare assertions below to execution evidence |
| Expected output | `len(findings) == 1`; `findings[0]['severity'] == 'CRITICAL'`; `findings[0]['resource'] == 'AWS Root Account'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-015

| Field | Value |
|---|---|
| Test ID | INTEGRATION-015 |
| Feature | regional audits report open management ports and public database |
| Test category | integration |
| Priority | High |
| Objective | regional audits report open management ports and public database |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_aws_audit.py::test_regional_audits_report_open_management_ports_and_public_database` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_aws_audit.py::test_regional_audits_report_open_management_ports_and_public_database -v`; compare assertions below to execution evidence |
| Expected output | `[finding['title'] for finding in ec2_findings] == ['SSH Open to Internet']`; `{finding['title'] for finding in rds_findings} == {'Database Instance Publicly Accessible', 'Database Storage Encryption Disabled', 'Database Multi-AZ Disabled'}` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-016

| Field | Value |
|---|---|
| Test ID | INTEGRATION-016 |
| Feature | ec2 audit reports ipv6 all protocol ingress and public snapshot |
| Test category | integration |
| Priority | High |
| Objective | ec2 audit reports ipv6 all protocol ingress and public snapshot |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_aws_audit.py::test_ec2_audit_reports_ipv6_all_protocol_ingress_and_public_snapshot` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_aws_audit.py::test_ec2_audit_reports_ipv6_all_protocol_ingress_and_public_snapshot -v`; compare assertions below to execution evidence |
| Expected output | `{finding['check_id'] for finding in findings} == {'ec2.security_group.world_ingress', 'ec2.ebs.volume_encryption', 'ec2.ebs.snapshot_public'}`; `ingress['severity'] == 'CRITICAL'`; `ingress['evidence']['public_cidrs'] == ['::/0']`; `volume_finding['resource'] == 'vol-unencrypted'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-017

| Field | Value |
|---|---|
| Test ID | INTEGRATION-017 |
| Feature | rds audit reports disabled backups deletion protection and public snapshots |
| Test category | integration |
| Priority | High |
| Objective | rds audit reports disabled backups deletion protection and public snapshots |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_aws_audit.py::test_rds_audit_reports_disabled_backups_deletion_protection_and_public_snapshots` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_aws_audit.py::test_rds_audit_reports_disabled_backups_deletion_protection_and_public_snapshots -v`; compare assertions below to execution evidence |
| Expected output | `{finding['check_id'] for finding in findings} == {'rds.backup_retention', 'rds.deletion_protection', 'rds.cluster_backup_retention', 'rds.cluster_deletion_protection', 'rds.snapshot_public', 'rds.cluster_snapshot_public'}` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-018

| Field | Value |
|---|---|
| Test ID | INTEGRATION-018 |
| Feature | cloudtrail audit checks multiregion logging and log bucket protection |
| Test category | integration |
| Priority | High |
| Objective | cloudtrail audit checks multiregion logging and log bucket protection |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_aws_audit.py::test_cloudtrail_audit_checks_multiregion_logging_and_log_bucket_protection` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_aws_audit.py::test_cloudtrail_audit_checks_multiregion_logging_and_log_bucket_protection -v`; compare assertions below to execution evidence |
| Expected output | `findings == []`; `cloudtrail.describe_trails.call_count == 2` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-019

| Field | Value |
|---|---|
| Test ID | INTEGRATION-019 |
| Feature | guardduty audit reports missing detector |
| Test category | integration |
| Priority | High |
| Objective | guardduty audit reports missing detector |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_aws_audit.py::test_guardduty_audit_reports_missing_detector` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_aws_audit.py::test_guardduty_audit_reports_missing_detector -v`; compare assertions below to execution evidence |
| Expected output | `len(findings) == 1`; `findings[0]['check_id'] == 'guardduty.detector_status'`; `findings[0]['title'] == 'GuardDuty Detector Not Found'`; `findings[0]['region'] == 'eu-west-1'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-020

| Field | Value |
|---|---|
| Test ID | INTEGRATION-020 |
| Feature | vpc audit reports default vpc without flow logs |
| Test category | integration |
| Priority | High |
| Objective | vpc audit reports default vpc without flow logs |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_aws_audit.py::test_vpc_audit_reports_default_vpc_without_flow_logs` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_aws_audit.py::test_vpc_audit_reports_default_vpc_without_flow_logs -v`; compare assertions below to execution evidence |
| Expected output | `[finding['title'] for finding in findings] == ['Default VPC In Use', 'VPC Flow Logs Disabled']` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-021

| Field | Value |
|---|---|
| Test ID | INTEGRATION-021 |
| Feature | chat sends separate agent responses to frontend |
| Test category | integration |
| Priority | High |
| Objective | chat sends separate agent responses to frontend |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: client, monkeypatch; controlled inputs defined in `tests/test_chat_api.py::test_chat_sends_separate_agent_responses_to_frontend` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_chat_api.py::test_chat_sends_separate_agent_responses_to_frontend -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 200`; `payload['cloud_agent_response']['high_count'] == 1`; `payload['compliance_agent_response'] == 'Compliance summary only.'`; `payload['senior_agent_response'] == 'Independent Senior review only.'`; `payload['assessment_id'] == 'assessment-test-id'`; `'cloud_agent_response' in payload`; `'compliance_agent_response' in payload`; `'senior_agent_response' in payload` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-022

| Field | Value |
|---|---|
| Test ID | INTEGRATION-022 |
| Feature | chat returns review and forwards history |
| Test category | integration |
| Priority | High |
| Objective | chat returns review and forwards history |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: monkeypatch; controlled inputs defined in `tests/test_chat_workflow.py::test_chat_returns_review_and_forwards_history` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_chat_workflow.py::test_chat_returns_review_and_forwards_history -v`; compare assertions below to execution evidence |
| Expected output | `result.cloud_agent_response.total_issues == 0`; `result.compliance_agent_response == 'Compliance assessment.'`; `result.senior_agent_response == 'Senior review.'`; `result.sources == []`; `result.assessment_id`; `assessment is not None`; `assessment.question == 'How should I review storage configuration?'`; `assessment.senior_review == 'Senior review.'`; `assessment.compliance_review == 'Compliance assessment.'`; `assessment.audit_report is not None` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-023

| Field | Value |
|---|---|
| Test ID | INTEGRATION-023 |
| Feature | unconfigured chat does not echo prompt or credentials |
| Test category | integration |
| Priority | High |
| Objective | unconfigured chat does not echo prompt or credentials |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: client, test_auth_settings; controlled inputs defined in `tests/test_errors.py::test_unconfigured_chat_does_not_echo_prompt_or_credentials` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_errors.py::test_unconfigured_chat_does_not_echo_prompt_or_credentials -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 503`; `response.json()['error']['code'] == 'provider_not_configured'`; `secret_prompt not in response.text` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-024

| Field | Value |
|---|---|
| Test ID | INTEGRATION-024 |
| Feature | health reports service without credentials |
| Test category | integration |
| Priority | High |
| Objective | health reports service without credentials |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: client; controlled inputs defined in `tests/test_health.py::test_health_reports_service_without_credentials` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_health.py::test_health_reports_service_without_credentials -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 200`; `response.json() == {'status': 'ok', 'service': 'Indra API', 'version': '0.1.0'}` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-025

| Field | Value |
|---|---|
| Test ID | INTEGRATION-025 |
| Feature | docs are available in development |
| Test category | integration |
| Priority | High |
| Objective | docs are available in development |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: client; controlled inputs defined in `tests/test_health.py::test_docs_are_available_in_development` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_health.py::test_docs_are_available_in_development -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 200` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-026

| Field | Value |
|---|---|
| Test ID | INTEGRATION-026 |
| Feature | request id is returned and oversized body is rejected |
| Test category | integration |
| Priority | High |
| Objective | request id is returned and oversized body is rejected |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: client; controlled inputs defined in `tests/test_health.py::test_request_id_is_returned_and_oversized_body_is_rejected` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_health.py::test_request_id_is_returned_and_oversized_body_is_rejected -v`; compare assertions below to execution evidence |
| Expected output | `response.headers['X-Request-ID'] == 'test-request-id'`; `oversized.status_code == 413`; `oversized.json()['error']['code'] == 'request_too_large'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-027

| Field | Value |
|---|---|
| Test ID | INTEGRATION-027 |
| Feature | rag query route returns passages and citations |
| Test category | integration |
| Priority | High |
| Objective | rag query route returns passages and citations |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: client, monkeypatch; controlled inputs defined in `tests/test_rag.py::test_rag_query_route_returns_passages_and_citations` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_rag.py::test_rag_query_route_returns_passages_and_citations -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 200`; `response.json() == {'question': 'How do I encrypt data?', 'passages': [{'title': 'Encryption', 'content': 'Enable encryption at rest.', 'source': 'Security guide', 'uri': 'https://example.test/encryption'}], 'sources': [{'title': 'Encryption', 'source': 'Security guide', 'uri': 'https://example.test/encryption'}]}` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-028

| Field | Value |
|---|---|
| Test ID | INTEGRATION-028 |
| Feature | rag status route reports missing files |
| Test category | integration |
| Priority | High |
| Objective | rag status route reports missing files |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: client, test_auth_settings, tmp_path; controlled inputs defined in `tests/test_rag.py::test_rag_status_route_reports_missing_files` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_rag.py::test_rag_status_route_reports_missing_files -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 200`; `response.json()['available'] is False`; `response.json()['index_available'] is False`; `response.json()['metadata_available'] is False` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-029

| Field | Value |
|---|---|
| Test ID | INTEGRATION-029 |
| Feature | rag query returns safe error when store is missing |
| Test category | integration |
| Priority | High |
| Objective | rag query returns safe error when store is missing |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: client, test_auth_settings, tmp_path; controlled inputs defined in `tests/test_rag.py::test_rag_query_returns_safe_error_when_store_is_missing` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_rag.py::test_rag_query_returns_safe_error_when_store_is_missing -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 503`; `response.json()['error']['code'] == 'rag_store_unavailable'`; `str(tmp_path) not in response.text` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-030

| Field | Value |
|---|---|
| Test ID | INTEGRATION-030 |
| Feature | rag query validates question length |
| Test category | integration |
| Priority | High |
| Objective | rag query validates question length |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: client; controlled inputs defined in `tests/test_rag.py::test_rag_query_validates_question_length` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_rag.py::test_rag_query_validates_question_length -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 422`; `response.json()['error']['code'] == 'validation_error'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-031

| Field | Value |
|---|---|
| Test ID | INTEGRATION-031 |
| Feature | HTTP chat → workflow fixture → SQLite → report endpoint |
| Test category | integration |
| Priority | High |
| Objective | HTTP chat → workflow fixture → SQLite → report endpoint |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: isolated_client, monkeypatch; controlled inputs defined in `tests/test_qa_integration.py::test_chat_persists_and_reads` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_qa_integration.py::test_chat_persists_and_reads -v`; compare assertions below to execution evidence |
| Expected output | `response.status_code == 200`; `saved.status_code == 200`; `saved.json()['senior_review'] == 'Synthetic review; no real audit evidence.'`; `isolated_client.get('/api/v1/assessments').json()['items'][0]['id'] == assessment_id` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## INTEGRATION-032

| Field | Value |
|---|---|
| Test ID | INTEGRATION-032 |
| Feature | Reject invalid assessment pagination |
| Test category | integration |
| Priority | High |
| Objective | Reject invalid assessment pagination |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: isolated_client, query; controlled inputs defined in `tests/test_qa_integration.py::test_invalid_pagination` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_qa_integration.py::test_invalid_pagination -v`; compare assertions below to execution evidence |
| Expected output | `isolated_client.get(f'/api/v1/assessments?{query}').status_code == 422` |
| Actual output | 3 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |


## INTEGRATION-033

| Field | Value |
|---|---|
| Test ID | INTEGRATION-033 |
| Feature | CORS and settings |
| Test category | integration |
| Priority | High |
| Objective | Allow local frontend JSON/bearer preflight and reject unknown origins |
| Preconditions | No external services; mocked dotenv source or local ASGI client |
| Test input | Child launch directory; local and untrusted origins; POST and authorization/content-type headers |
| Steps | Run mapped pytest node with QA plugin |
| Expected output | Root environment loaded; local origins accepted with exact allow-origin; unknown origin rejected |
| Actual output | 3 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | evidence/cors-fix.xml |
| Automation | Automated: tests/test_cors.py::test_cors_preflight_for_local_frontend |
