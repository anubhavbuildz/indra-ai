# Unit test cases

Designed before new test code. Counts are logical cases; parameterized execution counts may differ. External AWS/model calls must be stubbed.

## UNIT-001

| Field | Value |
|---|---|
| Test ID | UNIT-001 |
| Feature | verify access token rejects expired token |
| Test category | unit |
| Priority | High |
| Objective | verify access token rejects expired token |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_auth.py::test_verify_access_token_rejects_expired_token` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_auth.py::test_verify_access_token_rejects_expired_token -v`; compare assertions below to execution evidence |
| Expected output | `error.value.code == 'invalid_token'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-002

| Field | Value |
|---|---|
| Test ID | UNIT-002 |
| Feature | jwt secret must be at least 32 bytes |
| Test category | unit |
| Priority | High |
| Objective | jwt secret must be at least 32 bytes |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_auth.py::test_jwt_secret_must_be_at_least_32_bytes` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_auth.py::test_jwt_secret_must_be_at_least_32_bytes -v`; compare assertions below to execution evidence |
| Expected output | All mapped assertions pass; no live cloud or paid inference |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-003

| Field | Value |
|---|---|
| Test ID | UNIT-003 |
| Feature | cloud agent selects and executes audit tools |
| Test category | unit |
| Priority | High |
| Objective | cloud agent selects and executes audit tools |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_cloud_agent.py::test_cloud_agent_selects_and_executes_audit_tools` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_cloud_agent.py::test_cloud_agent_selects_and_executes_audit_tools -v`; compare assertions below to execution evidence |
| Expected output | `result.audited_services == ['s3', 'vpc']`; `result.audited_regions == ['eu-west-1']`; `result.total_issues == 1`; `result.high_count == 1`; `result.findings[0].title == 'S3 Public Access Block Disabled'`; `request['tool_choice'] == 'auto'`; `request['parallel_tool_calls'] is False`; `{tool['function']['name'] for tool in request['tools']} == {'audit_s3', 'audit_iam', 'audit_ec2', 'audit_vpc', 'audit_databases', 'audit_cloudtrail', 'audit_guardduty'}` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-004

| Field | Value |
|---|---|
| Test ID | UNIT-004 |
| Feature | cloud agent rejects invalid tool arguments before execution |
| Test category | unit |
| Priority | High |
| Objective | cloud agent rejects invalid tool arguments before execution |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_cloud_agent.py::test_cloud_agent_rejects_invalid_tool_arguments_before_execution` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_cloud_agent.py::test_cloud_agent_rejects_invalid_tool_arguments_before_execution -v`; compare assertions below to execution evidence |
| Expected output | `error.value.code == 'provider_invalid_response'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-005

| Field | Value |
|---|---|
| Test ID | UNIT-005 |
| Feature | cloud agent executes cloudtrail and guardduty with report schema |
| Test category | unit |
| Priority | High |
| Objective | cloud agent executes cloudtrail and guardduty with report schema |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_cloud_agent.py::test_cloud_agent_executes_cloudtrail_and_guardduty_with_report_schema` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_cloud_agent.py::test_cloud_agent_executes_cloudtrail_and_guardduty_with_report_schema -v`; compare assertions below to execution evidence |
| Expected output | `result.audited_services == ['cloudtrail', 'guardduty']`; `result.audited_regions == ['all-enabled-regions', 'eu-west-1']`; `result.findings[0].check_id == 'guardduty.detector_status'`; `result.findings[0].evidence == {'detector_count': 0}` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-006

| Field | Value |
|---|---|
| Test ID | UNIT-006 |
| Feature | chat workflow invokes cloud agent with audit context |
| Test category | unit |
| Priority | High |
| Objective | chat workflow invokes cloud agent with audit context |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: monkeypatch; controlled inputs defined in `tests/test_cloud_agent.py::test_chat_workflow_invokes_cloud_agent_with_audit_context` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_cloud_agent.py::test_chat_workflow_invokes_cloud_agent_with_audit_context -v`; compare assertions below to execution evidence |
| Expected output | `result['cloud_agent_response'] == audit_report.model_dump()`; `result['compliance_agent_response'] == 'Compliance assessment.'`; `result['senior_agent_response'] == 'Senior review.'`; `result['sources'] == [{'title': 'Security guidance', 'source': 'Security guidance', 'uri': 'https://example.invalid/security'}]`; `calls == ['cloud', 'retrieval', 'compliance', 'senior']`; `kwargs['question'] == 'Audit my AWS configuration.'`; `kwargs['history'] == [{'role': 'user', 'content': 'Prioritize urgent risks.'}]`; `kwargs['audit_result'] == audit_report`; `kwargs['retrieved_passages'] == [passage]`; `kwargs['audit_report'] == audit_report`; `kwargs['compliance_assessment'] == 'Compliance assessment.'`; `question == 'Audit my AWS configuration.'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-007

| Field | Value |
|---|---|
| Test ID | UNIT-007 |
| Feature | defaults allow startup without provider credentials |
| Test category | unit |
| Priority | High |
| Objective | defaults allow startup without provider credentials |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: monkeypatch; controlled inputs defined in `tests/test_config.py::test_defaults_allow_startup_without_provider_credentials` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_config.py::test_defaults_allow_startup_without_provider_credentials -v`; compare assertions below to execution evidence |
| Expected output | `settings.app_name == 'Indra API'`; `settings.database_url == 'sqlite:///./data/indra.db'`; `not settings.nvidia_api_key`; `settings.nvidia_base_url == 'https://api.tokenfactory.nebius.com/v1'`; `settings.nvidia_model == 'nvidia/Nemotron-3_5-Lightning'`; `settings.nvidia_api_format == 'openai-chat-completions'`; `settings.inference_timeout_seconds == 120.0`; `not settings.integrations_ready['nvidia']` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-008

| Field | Value |
|---|---|
| Test ID | UNIT-008 |
| Feature | inference timeout is bounded |
| Test category | unit |
| Priority | High |
| Objective | inference timeout is bounded |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_config.py::test_inference_timeout_is_bounded` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_config.py::test_inference_timeout_is_bounded -v`; compare assertions below to execution evidence |
| Expected output | `settings.inference_timeout_seconds == 240` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-009

| Field | Value |
|---|---|
| Test ID | UNIT-009 |
| Feature | inference timeout rejects values above maximum |
| Test category | unit |
| Priority | High |
| Objective | inference timeout rejects values above maximum |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_config.py::test_inference_timeout_rejects_values_above_maximum` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_config.py::test_inference_timeout_rejects_values_above_maximum -v`; compare assertions below to execution evidence |
| Expected output | All mapped assertions pass; no live cloud or paid inference |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-010

| Field | Value |
|---|---|
| Test ID | UNIT-010 |
| Feature | credentials are not in settings repr |
| Test category | unit |
| Priority | High |
| Objective | credentials are not in settings repr |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_config.py::test_credentials_are_not_in_settings_repr` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_config.py::test_credentials_are_not_in_settings_repr -v`; compare assertions below to execution evidence |
| Expected output | `'unit-test-secret' not in repr(settings)` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-011

| Field | Value |
|---|---|
| Test ID | UNIT-011 |
| Feature | missing provider settings fail clearly |
| Test category | unit |
| Priority | High |
| Objective | missing provider settings fail clearly |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_llm_service.py::test_missing_provider_settings_fail_clearly` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_llm_service.py::test_missing_provider_settings_fail_clearly -v`; compare assertions below to execution evidence |
| Expected output | `error.value.code == 'provider_not_configured'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-012

| Field | Value |
|---|---|
| Test ID | UNIT-012 |
| Feature | nebius provider defaults |
| Test category | unit |
| Priority | High |
| Objective | nebius provider defaults |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_llm_service.py::test_nebius_provider_defaults` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_llm_service.py::test_nebius_provider_defaults -v`; compare assertions below to execution evidence |
| Expected output | `settings.nvidia_base_url == 'https://api.tokenfactory.nebius.com/v1'`; `settings.nvidia_model == 'nvidia/Nemotron-3_5-Lightning'`; `settings.nvidia_api_format == 'openai-chat-completions'`; `settings.inference_timeout_seconds == 120.0` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-013

| Field | Value |
|---|---|
| Test ID | UNIT-013 |
| Feature | client is created from settings without default endpoint |
| Test category | unit |
| Priority | High |
| Objective | client is created from settings without default endpoint |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_llm_service.py::test_client_is_created_from_settings_without_default_endpoint` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_llm_service.py::test_client_is_created_from_settings_without_default_endpoint -v`; compare assertions below to execution evidence |
| Expected output | `client is openai_client.return_value`; `openai_client.call_args.kwargs == {'api_key': 'test-secret', 'base_url': 'https://provider.invalid/v1', 'timeout': 12.0, 'max_retries': 0}` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-014

| Field | Value |
|---|---|
| Test ID | UNIT-014 |
| Feature | client uses configured inference timeout |
| Test category | unit |
| Priority | High |
| Objective | client uses configured inference timeout |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_llm_service.py::test_client_uses_configured_inference_timeout` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_llm_service.py::test_client_uses_configured_inference_timeout -v`; compare assertions below to execution evidence |
| Expected output | `client is openai_client.return_value`; `openai_client.call_args.kwargs['timeout'] == 180.0` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-015

| Field | Value |
|---|---|
| Test ID | UNIT-015 |
| Feature | completion uses shared client model and conversation |
| Test category | unit |
| Priority | High |
| Objective | completion uses shared client model and conversation |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_llm_service.py::test_completion_uses_shared_client_model_and_conversation` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_llm_service.py::test_completion_uses_shared_client_model_and_conversation -v`; compare assertions below to execution evidence |
| Expected output | `response == 'completion'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-016

| Field | Value |
|---|---|
| Test ID | UNIT-016 |
| Feature | provider errors are mapped without details |
| Test category | unit |
| Priority | High |
| Objective | provider errors are mapped without details |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: provider_error, expected_code; controlled inputs defined in `tests/test_llm_service.py::test_provider_errors_are_mapped_without_details` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_llm_service.py::test_provider_errors_are_mapped_without_details -v`; compare assertions below to execution evidence |
| Expected output | `error.value.code == expected_code`; `'private provider detail' not in error.value.message` |
| Actual output | 4 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-017

| Field | Value |
|---|---|
| Test ID | UNIT-017 |
| Feature | malformed provider response is safe |
| Test category | unit |
| Priority | High |
| Objective | malformed provider response is safe |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_llm_service.py::test_malformed_provider_response_is_safe` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_llm_service.py::test_malformed_provider_response_is_safe -v`; compare assertions below to execution evidence |
| Expected output | `error.value.code == 'provider_invalid_response'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-018

| Field | Value |
|---|---|
| Test ID | UNIT-018 |
| Feature | compliance agent summarizes audit report and history |
| Test category | unit |
| Priority | High |
| Objective | compliance agent summarizes audit report and history |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_llm_service.py::test_compliance_agent_summarizes_audit_report_and_history` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_llm_service.py::test_compliance_agent_summarizes_audit_report_and_history -v`; compare assertions below to execution evidence |
| Expected output | `response == 'Evidence-limited answer'`; `'SSH Open to Internet' in sent_messages[2]['content'][0]['text']`; `'no more than 5 bullets' in sent_messages[2]['content'][0]['text']`; `sent_messages[1] == {'role': 'user', 'content': 'I use AWS.'}`; `'compliance summarizer' in sent_messages[0]['content']`; `'not a certification' in sent_messages[0]['content']` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-019

| Field | Value |
|---|---|
| Test ID | UNIT-019 |
| Feature | compliance role prompt loads from markdown |
| Test category | unit |
| Priority | High |
| Objective | compliance role prompt loads from markdown |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: No fixture arguments; controlled inputs defined in `tests/test_llm_service.py::test_compliance_role_prompt_loads_from_markdown` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_llm_service.py::test_compliance_role_prompt_loads_from_markdown -v`; compare assertions below to execution evidence |
| Expected output | `'compliance summarizer' in load_role_prompt('compliance_role.md')` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-020

| Field | Value |
|---|---|
| Test ID | UNIT-020 |
| Feature | retriever returns faiss ranked passages and sources |
| Test category | unit |
| Priority | High |
| Objective | retriever returns faiss ranked passages and sources |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: tmp_path, monkeypatch; controlled inputs defined in `tests/test_rag.py::test_retriever_returns_faiss_ranked_passages_and_sources` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_rag.py::test_retriever_returns_faiss_ranked_passages_and_sources -v`; compare assertions below to execution evidence |
| Expected output | `passages[0].title == 'Logging'`; `{passage.title for passage in passages} == {'Logging', 'Encryption', 'Identity'}`; `passages[0].source_uri == 'https://example.test/1'`; `passages[0].as_source() == {'title': 'Logging', 'source': 'Logging', 'uri': 'https://example.test/1'}` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-021

| Field | Value |
|---|---|
| Test ID | UNIT-021 |
| Feature | store loader rejects document count mismatch |
| Test category | unit |
| Priority | High |
| Objective | store loader rejects document count mismatch |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: tmp_path; controlled inputs defined in `tests/test_rag.py::test_store_loader_rejects_document_count_mismatch` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_rag.py::test_store_loader_rejects_document_count_mismatch -v`; compare assertions below to execution evidence |
| Expected output | `error.value.code == 'rag_metadata_mismatch'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-022

| Field | Value |
|---|---|
| Test ID | UNIT-022 |
| Feature | resolve store path preserves absolute paths |
| Test category | unit |
| Priority | High |
| Objective | resolve store path preserves absolute paths |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: tmp_path; controlled inputs defined in `tests/test_rag.py::test_resolve_store_path_preserves_absolute_paths` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_rag.py::test_resolve_store_path_preserves_absolute_paths -v`; compare assertions below to execution evidence |
| Expected output | `resolve_store_path(tmp_path / 'store.index') == tmp_path / 'store.index'` |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-023

| Field | Value |
|---|---|
| Test ID | UNIT-023 |
| Feature | Reject missing claims and wrong signatures |
| Test category | unit |
| Priority | High |
| Objective | Reject missing claims and wrong signatures |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: test_auth_settings, variant; controlled inputs defined in `tests/test_qa_unit.py::test_jwt_rejects_invalid_claims` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_qa_unit.py::test_jwt_rejects_invalid_claims -v`; compare assertions below to execution evidence |
| Expected output | `exc.value.code == 'invalid_token'` |
| Actual output | 4 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-024

| Field | Value |
|---|---|
| Test ID | UNIT-024 |
| Feature | Reject unusable guidance |
| Test category | unit |
| Priority | High |
| Objective | Reject unusable guidance |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: document; controlled inputs defined in `tests/test_qa_unit.py::test_rag_rejects_invalid_metadata` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_qa_unit.py::test_rag_rejects_invalid_metadata -v`; compare assertions below to execution evidence |
| Expected output | `exc.value.code == 'rag_metadata_invalid'` |
| Actual output | 3 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-025

| Field | Value |
|---|---|
| Test ID | UNIT-025 |
| Feature | Validate chat boundaries |
| Test category | unit |
| Priority | High |
| Objective | Validate chat boundaries |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Fixture dependencies: payload; controlled inputs defined in `tests/test_qa_unit.py::test_chat_schema_boundaries` |
| Steps | Run `.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_qa_unit.py::test_chat_schema_boundaries -v`; compare assertions below to execution evidence |
| Expected output | `len(ChatRequest(message='x' * 8000).message) == 8000` |
| Actual output | 4 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-026

| Field | Value |
|---|---|
| Test ID | UNIT-026 |
| Feature | React login accessibility, loading, failure, token state and API failures |
| Test category | unit |
| Priority | High |
| Objective | React login accessibility, loading, failure, token state and API failures |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Named test fixtures in `frontend/src/qa.test.jsx`; invalid variants where named |
| Steps | Run the mapped test using HOW_TO_TEST.md commands; inspect assertions and evidence |
| Expected output | All mapped assertions pass; no live cloud or paid inference |
| Actual output | 3 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-027

| Field | Value |
|---|---|
| Test ID | UNIT-027 |
| Feature | HTTP bearer, expiry, abort, malformed payload and network handling |
| Test category | unit |
| Priority | High |
| Objective | HTTP bearer, expiry, abort, malformed payload and network handling |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Named test fixtures in `frontend/src/api.test.js`; invalid variants where named |
| Steps | Run the mapped test using HOW_TO_TEST.md commands; inspect assertions and evidence |
| Expected output | All mapped assertions pass; no live cloud or paid inference |
| Actual output | 5 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |

## UNIT-028

| Field | Value |
|---|---|
| Test ID | UNIT-028 |
| Feature | Severity, empty findings, dates and formatting boundaries |
| Test category | unit |
| Priority | High |
| Objective | Severity, empty findings, dates and formatting boundaries |
| Preconditions | Isolated database, test credentials, external service fixtures; dependencies installed |
| Test input | Named test fixtures in `frontend/src/utils.test.js`; invalid variants where named |
| Steps | Run the mapped test using HOW_TO_TEST.md commands; inspect assertions and evidence |
| Expected output | All mapped assertions pass; no live cloud or paid inference |
| Actual output | 2 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | design/qa/evidence/ generated logs and JUnit |
| Automation | Automated |


## UNIT-029

| Field | Value |
|---|---|
| Test ID | UNIT-029 |
| Feature | All implemented React routes |
| Test category | Unit |
| Priority | High |
| Objective | Verify route rendering, findings filtering, settings validation, audit submission and session expiry |
| Preconditions | jsdom, memory router, query client with retries disabled, stubbed API |
| Test input | One synthetic S3 HIGH finding; empty/error variants |
| Steps | Render routes; sign in; exercise controls; assert observable output |
| Expected output | Correct page, validation, report and login redirect |
| Actual output | 8 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | evidence/frontend-unit.xml |
| Automation | Automated: frontend/src/pages.test.jsx |

## UNIT-030

| Field | Value |
|---|---|
| Test ID | UNIT-030 |
| Feature | CORS and settings |
| Test category | unit |
| Priority | High |
| Objective | Load repository .env independently of launch directory |
| Preconditions | No external services; mocked dotenv source or local ASGI client |
| Test input | Child launch directory; local and untrusted origins; POST and authorization/content-type headers |
| Steps | Run mapped pytest node with QA plugin |
| Expected output | Root environment loaded; local origins accepted with exact allow-origin; unknown origin rejected |
| Actual output | 1 mapped executions; Passed. See raw evidence. |
| Status | Passed |
| Evidence | evidence/cors-fix.xml |
| Automation | Automated: tests/test_config.py::test_env_file_is_loaded_from_project_root |

### UNIT-026 persistent-session regression scenarios

Persist the login JWT under `indraa.accessToken`; restore username and bearer header on remount; reject expired/malformed tokens; clear storage on sign-out, server 401 and JWT expiry. Passwords must never be stored. Use valid two-hour fixture JWTs and fake timers for expiration. Evidence: frontend-unit.xml and frontend-auth-persistence.log.
