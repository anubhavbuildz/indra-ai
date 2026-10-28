# Indraa Test Cases and Function Behavior

This is a hands-on test plan for the current backend and React frontend. It
maps the principal production functions and user-facing operations to their
expected behavior, boundaries, and a test to run. Use the unchecked result
columns during the test session.

## 1. Test-session setup

### Recommended order

1. Run backend unit and API tests with mocked AWS/provider integrations.
2. Run frontend lint and production build.
3. Start the backend and frontend and exercise authentication and UI/API
   integration with local or controlled test data.
4. Run live AWS/inference tests only when explicitly authorized and available.

### Commands

From the repository root:

```bash
python -m pip install -e '.[dev]'
pytest -q
ruff check .
ruff format --check .
```

From `frontend/`:

```bash
npm install
npm run lint
npm run build
npm run dev
```

The backend CI workflow runs Python 3.12. The local environment must have
`pytest` and the project's dependencies installed before backend results can
be recorded.

### Safety and test-data constraints

- Default tests must be offline and must mock AWS, remote inference, and
  external services. Use synthetic account/resource identifiers.
- Never paste AWS credentials, provider keys, passwords, bearer tokens, raw
  production data, or sensitive account identifiers into test cases, logs,
  screenshots, or this file.
- Live cloud checks use read-only AWS operations but can access real account
  configuration. Obtain authorization, use least-privilege credentials, and
  scope the run narrowly.
- A live `/api/v1/chat` request sends the question and audit findings to the
  configured inference provider. Do not run that test unless data transmission
  has been approved and the provider is available.
- Do not upload user-provided FAISS index or pickle files. RAG uses the
  trusted, locally provisioned index/metadata pair.
- Findings are point-in-time signals, not proof of compliance or a complete
  security assessment.

## 2. API and application function tests

| ID | Function / surface | Expected behavior | Constraints and negative cases | Test / pass condition | Result |
|---|---|---|---|---|---|
| API-01 | `login()` — `POST /api/v1/auth/login` | Validates the configured single account and returns an access token and `expires_in=7200`. | Public route. Reject incorrect credentials with 401; missing login configuration or signing key returns 503. JWT signing key must be at least 32 bytes when configured. Never expose password or token in errors/logs. | `pytest tests/test_auth.py -q`; valid login succeeds, invalid/unconfigured cases use expected error shape. | ☐ |
| API-02 | `require_access_token()` and `verify_access_token()` | Protected versioned routes validate the bearer JWT signature, required claims, and expiration. | Only HS256 accepted; claims require `sub`, `iat`, `exp`; absent/invalid/expired token rejected. Login, root, health, readiness, and development docs are public as documented. | `pytest tests/test_auth.py -q`; verify protected endpoints reject missing, malformed, tampered, and expired tokens. | ☐ |
| API-03 | `chat()` — `POST /api/v1/chat` | Validates the request, calls `ChatService.run()`, and returns separate Cloud, Compliance, Senior, sources, assessment ID, and completed status fields. | `message`: 1–8,000 chars. History: at most 20 messages; each role is `user` or `assistant`, content 1–4,000 chars. Requires valid auth, provider, AWS read access, and compatible RAG store for a live run. Non-streaming. | `pytest tests/test_chat_api.py tests/test_chat_workflow.py -q`; response fields remain distinct and validation errors do not echo submitted values. | ☐ |
| API-04 | `list_assessments()` — `GET /api/v1/assessments` | Returns persisted assessments with pagination metadata. | `limit` 1–100, default 50; `offset` >=0, default 0. Requires auth. | `pytest tests/test_assessments.py -q`; check empty list, populated list, paging, and invalid bounds. | ☐ |
| API-05 | `get_assessment()` — `GET /api/v1/assessments/{assessment_id}` | Returns the stored request, Cloud report, Compliance output, Senior output, and timestamps for an existing assessment. | Requires auth. Unknown IDs must use the project's not-found error response; IDs are not authorization tokens. | `pytest tests/test_assessments.py -q`; existing ID round-trips; unknown ID returns not found. | ☐ |
| API-06 | `rag_status()` — `GET /api/v1/rag/status` | Reports embedding model and index/metadata file availability without loading the embedder or exposing filesystem paths. | Requires auth. `available` indicates configured artifact presence, not successful index/metadata compatibility. | `pytest tests/test_rag.py -q`; test both files present, one/both missing, safe fields only. | ☐ |
| API-07 | `rag_query()` — `POST /api/v1/rag/query` | Retrieves up to three locally indexed passages and returns matching source citations. | `question`: 1–8,000 chars. Requires a valid local store and compatible embedding model; does not call AWS or hosted LLM. Retrieval failures return safe error details, not paths or internals. | `pytest tests/test_rag.py -q`; valid query returns passage/source pairs; missing/corrupt/mismatched store fails explicitly. | ☐ |
| API-08 | `aws_identity()` — `GET /api/v1/aws/identity` | Returns the backend's AWS caller identity using STS and the standard credential chain. | Requires auth and usable AWS credentials; must not return secret credentials or claim identity when STS fails. | `pytest tests/test_aws.py -q`; mock success and provider/credential failure. | ☐ |
| API-09 | `health()` — `GET /health` | Reports process health without requiring external integrations. | Must not call AWS, FAISS, embeddings, or inference. Public. | `pytest tests/test_health.py -q`; verify successful health response with integrations unconfigured. | ☐ |
| API-10 | `ready()` — `GET /ready` | Reports basic local database/readiness configuration. | Does not establish AWS, provider, or FAISS availability. Public; response must not expose secrets. | `pytest tests/test_health.py -q`; verify no external calls are triggered. | ☐ |
| API-11 | `RequestContextMiddleware.__call__()` | Adds/propagates request ID and enforces configured request-body size. | Request body maximum configured 1,024–10,485,760 bytes; default 1,048,576. Oversized payload rejected; request ID returned. | `pytest tests/test_health.py -q`; check request ID and oversized-body rejection. | ☐ |
| API-12 | Error handlers: `handle_app_error`, `handle_validation_error`, `handle_unexpected_error` | Return stable JSON error envelopes and avoid leaking exception internals or submitted secrets. | Validation errors must not contain submitted values; unexpected failures must not become success-shaped responses. | `pytest tests/test_errors.py tests/test_health.py -q`; inspect status, shape, and absence of prompt/secret text. | ☐ |

## 3. Backend service and workflow function tests

| ID | Function / surface | Expected behavior | Constraints and negative cases | Test / pass condition | Result |
|---|---|---|---|---|---|
| SVC-01 | `ChatService.run()` | Runs the complete workflow, persists the finished result, and returns all outputs with the persisted assessment ID. | Does not persist incomplete/failed workflow output. Must preserve source citations in the response even though assessment history does not store citations. | `pytest tests/test_chat_workflow.py tests/test_assessments.py -q`; assert call order, persistence, and output separation. | ☐ |
| SVC-02 | `chat_workflow()` | Runs Cloud audit → RAG retrieval → Compliance review → Senior review sequentially; returns the three outputs and citations. | Requires configured inference and matching local FAISS artifacts. Must not report later-agent success if an earlier stage fails. No streaming/progress claims. | `pytest tests/test_chat_workflow.py -q`; stub each dependency and assert exact order and handoffs, including each failure point. | ☐ |
| SVC-03 | `CloudAgent.run_audit()` | Asks the provider to select allowed audit tools, executes selected audit functions, aggregates findings, and validates `AuditReport`. | Only the fixed allowlist; no duplicate tools; arguments must decode to an empty object; AWS region comes from backend settings, not request data. Converts AWS/provider failures to safe application errors. | `pytest tests/test_cloud_agent.py -q`; valid calls execute; unknown, duplicate, malformed, non-empty-argument calls are rejected before AWS call. | ☐ |
| SVC-04 | `ComplianceAgent.review()` | Summarizes audit findings with retrieved guidance while distinguishing observations from general guidance. | Retrieved passages and audit content are untrusted prompt inputs; citations are evidence references, not proof of implementation/compliance. Provider failure must surface. | `pytest tests/test_chat_workflow.py tests/test_llm_service.py -q`; inspect captured prompt and output/error behavior. | ☐ |
| SVC-05 | `SeniorAgent.review()` | Reviews the structured Cloud report and Compliance summary and returns its own independent review string. | Must receive both prior outputs; must not replace or merge them in the API result. No certification claims unless supported. | `pytest tests/test_chat_workflow.py -q`; assert arguments and separate response field. | ☐ |
| SVC-06 | `BaseLLM.complete()` | Sends a completion request through the configured OpenAI-compatible provider and returns validated text. | Requires configured endpoint/key/model; enforce timeout; handle empty/malformed/provider errors safely. Never log credentials or full sensitive prompts. | `pytest tests/test_llm_service.py -q`; mock provider success, timeout, malformed response, and HTTP/provider error. | ☐ |
| SVC-07 | `BaseLLM.request_tool_arguments()` / `request_tool_calls()` | Requests constrained function calls and validates the expected provider response shape. | Tool calls must be within supplied tool schema; invalid/malformed response fails explicitly. Test boundary before any AWS tool executes. | `pytest tests/test_llm_service.py tests/test_cloud_agent.py -q`; assert accepted/rejected response formats. | ☐ |
| SVC-08 | `BaseLLM.ensure_configured()`, `client`, `close()`, async context methods | Validates provider configuration, lazily provides client, and reliably releases client resources. | Missing configuration is explicit; cleanup works on success and exception paths; do not mask original exceptions. | `pytest tests/test_llm_service.py -q`; verify missing config and lifecycle cleanup. | ☐ |
| SVC-09 | `AssessmentService.record_chat()`, `.list()`, `.get()` | Delegates assessment writes/queries to repository and returns persisted records. | Store question, structured audit report, and both reviews; no credentials; sources are not persisted. Pagination constraints enforced by route. | `pytest tests/test_assessments.py -q`; create/list/get and unknown-ID behavior. | ☐ |
| SVC-10 | `AssessmentRepository.create_from_chat()`, `.list()`, `.get()` | Creates, pages, and fetches assessment rows using the DB session. | Persist output atomically/consistently; list ordering/pagination should be stable; `get()` returns missing when ID absent. | `pytest tests/test_assessments.py -q`; verify DB round-trip and page boundaries. | ☐ |
| SVC-11 | `AWSService.identity()` | Calls STS caller identity and shapes account/ARN/user identity fields. | Uses standard credentials; read-only; does not reveal credentials or claim identity on provider failure. | `pytest tests/test_aws.py -q`; mocked STS success and failure. | ☐ |
| SVC-12 | `Settings.validate_jwt_secret_key()` | Accepts unset secret for startup without login; rejects configured secret shorter than 32 UTF-8 bytes. | Validate byte length, not merely character count. | `pytest tests/test_config.py tests/test_auth.py -q`; include multibyte and boundary-length cases. | ☐ |
| SVC-13 | `Settings.cors_origin_list`, `.integrations_ready`, `get_settings()` | Parses comma-separated origins, reports only boolean integration readiness, and caches settings. | Ignore blank origins; never include credential values in repr/readiness output. Cache clear/reload behavior should be controlled in tests. | `pytest tests/test_config.py -q`; verify exact origin trimming and secret-safe representations. | ☐ |
| SVC-14 | `Login.data_validation()`, `Login._encode()` | Constant-time compares configured username/password and issues signed JWT with `sub`, `iat`, `exp`. | 2-hour expiration; unconfigured credentials/signing key yield 503; invalid credentials yield 401; no secret in errors. | `pytest tests/test_auth.py -q`; validate claims, expiration, invalid and unconfigured cases. | ☐ |
| SVC-15 | `verify_access_token()` | Verifies signature/algorithm, required claims, subject, and expiration. | Accept only HS256; reject empty subject, missing claims, wrong key, malformed, or expired token. | `pytest tests/test_auth.py -q`; include tampering and wrong algorithm. | ☐ |
| SVC-16 | `initialize_database()`, `get_db()`, session factory | Initializes migrated DB and yields/closes request-scoped sessions. | Tests must use isolated temporary SQLite DB; no unintended shared production DB writes. | `pytest tests/test_assessments.py tests/test_health.py -q`; verify session cleanup and schema availability. | ☐ |
| SVC-17 | `configure_logging()` | Configures application logging at intended level and format. | Do not emit passwords, tokens, API keys, full prompts, or sensitive audit data. | Inspect test/log output with synthetic sentinel secret and assert it is absent. | ☐ |

### Application, persistence, and schema helpers

| ID | Function / model | Expected behavior | Constraints and negative cases | Test / pass condition | Result |
|---|---|---|---|---|---|
| INT-01 | `lifespan()` / `initialize_database()` | Applies database migrations before serving application requests. | Startup must fail visibly on database initialization failure; do not silently serve without required schema. | Start app against a temporary DB; verify schema exists and a deliberate DB failure prevents successful startup. | ☐ |
| INT-02 | `root()` | Returns service name and development docs path when docs are enabled. | Production should not advertise disabled docs; public response contains no configuration secrets. | Check response in development and production settings. | ☐ |
| INT-03 | `_engine_for()` / `get_session_factory()` / `get_db()` | Builds/reuses DB engine/session factory and yields a request-scoped session that is closed after use. | Use isolated test DB; no unintended connection/session leaks. | Verify session lifecycle and separate DB URL behavior in service/API tests. | ☐ |
| INT-04 | `utc_now()` / `Assessment` / `Operation` | Supplies UTC timestamps and maps persisted record fields. | Timestamps should be timezone-aware UTC; no credentials or provider secrets stored in records. | Create/read records and inspect timestamp timezone and persisted columns. | ☐ |
| INT-05 | `register_error_handlers()` / `AppError` | Installs application, validation, and unexpected-error handlers with stable JSON envelope. | Preserve correct HTTP status/code; unexpected exceptions are generic to client and logged without secrets. | Exercise known AppError, invalid payload, and unexpected exception through TestClient. | ☐ |
| INT-06 | `load_role_prompt()` / `_normalize_prompt()` | Loads only known packaged role files, normalizes whitespace, and optionally selects a level-two section. | Unknown/missing/empty sections fail explicitly; role file path is constrained by `RoleFile`; prompt changes are reviewed as code. | Test whole prompt, valid section, missing section, and empty section. | ☐ |
| INT-07 | `AuditFinding` / `AuditReport` | Validates finding properties, severity literals, audited services, totals, and severity counts. | `AuditReport` forbids unknown top-level fields; counts cannot be negative; severity must be CRITICAL/HIGH/MEDIUM/LOW or absent. | Test valid report plus invalid severity/service, negative count, and extra top-level field. | ☐ |
| INT-08 | `ChatMessage` / `ChatRequest` / `RagQueryRequest` schemas | Enforces API input lengths, history size/role, and RAG question limits. | Verify exact min/max boundaries and malformed JSON; response errors must not echo submitted secrets. | Parameterize values at limit−1, limit, and limit+1 for each constraint. | ☐ |
| INT-09 | `AssessmentRead` / `AssessmentList` / auth and response schemas | Serializes database rows and API response values to their declared public contracts. | No ORM-only/private fields or secrets; optional fields remain nullable where declared. | Validate model serialization and route response schema. | ☐ |

## 4. RAG function tests

| ID | Function / surface | Expected behavior | Constraints and negative cases | Test / pass condition | Result |
|---|---|---|---|---|---|
| RAG-01 | `RagService.status()` | Reports file presence and configured embedding model without loading FAISS/model. | Presence is not proof of compatibility; no filesystem paths in response. | `pytest tests/test_rag.py -q`; assert no embedder/store loader invocation. | ☐ |
| RAG-02 | `RagService.query()` | Runs retrieval off the event loop and returns ranked `RetrievedPassage` objects. | Must propagate safe retrieval errors; no empty-success fallback on unavailable store. | `pytest tests/test_rag.py -q`; success, failure, and async execution behavior. | ☐ |
| RAG-03 | `resolve_store_path()` | Preserves absolute paths and resolves relative paths from project root. | Do not unexpectedly resolve relative paths from arbitrary process working directory. | `pytest tests/test_rag.py -q`; relative and absolute path cases. | ☐ |
| RAG-04 | `is_string_dict()` / `is_document_list()` | Validates dict keys are strings and metadata is a list of documents containing valid `data` maps. | Reject malformed keys, non-list metadata, missing/non-map `data`; do not deserialize user uploads. | `pytest tests/test_rag.py -q`; valid/invalid structures. | ☐ |
| RAG-05 | `load_store()` | Loads local FAISS index and trusted paired pickle metadata; checks non-empty matching document count. | Missing/corrupt/mismatched index or metadata returns safe 503-style AppError; cached store max 4 path pairs; never accept uploaded pickle. | `pytest tests/test_rag.py -q`; missing files, corrupt files, count mismatch, empty index, valid pair. | ☐ |
| RAG-06 | `load_embedding_model()` | Lazily loads and caches configured SentenceTransformer model. | Model must be compatible with index dimension; routine tests mock it and avoid network/model download. | `pytest tests/test_rag.py -q`; mocked model and embedding failure. | ☐ |
| RAG-07 | `RagRetriever.retrieve()` | Embeds query, searches FAISS, and formats the highest-ranked passages with sources. | Top 3 results maximum; index embedding dimension must match; skip negative FAISS indexes; reject out-of-range metadata index. Passage text max 4,000 characters. | `pytest tests/test_rag.py -q`; ranking, top-k, dimensions, metadata mismatch, missing store. | ☐ |
| RAG-08 | `_format_passage()` | Derives title, summary, topics, source name/URI, and relevant practices from metadata. | Reject invalid/empty usable metadata; deduplicate topics; content max 4,000 characters. | `pytest tests/test_rag.py -q`; optional/missing fields, malformed fields, truncation. | ☐ |
| RAG-09 | `_relevant_practices()` / `_tokens()` | Selects up to three practices by query-token overlap, stable order for ties; token matching is case-folded and excludes tokens shorter than 3 chars. | Each practice text max 1,000 characters; no matching practices returns none. | `pytest tests/test_rag.py -q`; relevance ordering, tie order, max count/length, empty inputs. | ☐ |
| RAG-10 | `_string()` / `_strings()` | Normalizes only string values and string lists, trimming blanks. | Ignore non-string values; do not stringify arbitrary metadata objects. | `pytest tests/test_rag.py -q`; whitespace and wrong-type cases. | ☐ |
| RAG-11 | `RetrievedPassage.as_source()` / `.as_prompt_data()` | Produces source citation and prompt-safe passage representations. | Preserve source attribution; include no unrelated metadata or local paths. | `pytest tests/test_rag.py -q`; compare field shapes and citation references. | ☐ |

## 5. AWS audit function tests

All audit methods below must use read-only Boto3 calls. Use mocked clients in
unit tests; avoid executing against a real account unless authorized. Finding
severity/counts must agree with the returned finding list and the
`AuditReport` schema.

| ID | Function | Checks / expected behavior | Constraints / test boundaries | Test / pass condition | Result |
|---|---|---|---|---|---|
| AWS-01 | `AWSAuditor.get_enabled_regions()` | Discovers enabled AWS regions for regional checks. | Uses configured primary region; handles provider/permission errors safely. | `pytest tests/test_aws_audit.py -q`; mocked region list and error case. | ☐ |
| AWS-02 | `AWSAuditor.run_audit()` | Runs selected audit mixins, aggregates findings and region scope. | S3/IAM global; EC2/VPC/RDS/GuardDuty region-specific; CloudTrail discovers enabled regions. Never mutate resources. | Verify service selection, regional scope, aggregation, and no write API calls. | ☐ |
| AWS-03 | `audit_s3()` | Checks bucket region, public access block, default encryption, public policy/ACL, versioning, TLS-only policy, and access logging. | Per-bucket API failures become explicit error findings where handled; do not claim uninspected controls were checked. | `pytest tests/test_aws_audit.py -k s3 -q`; test compliant and insecure bucket cases plus permission failures. | ☐ |
| AWS-04 | `audit_iam()` | Checks root-account access-key condition. | Global account-level check; read-only; permission failure is not a clean result. | `pytest tests/test_aws_audit.py -k iam -q`; keys present/absent and error case. | ☐ |
| AWS-05 | `audit_ec2(region)` | Checks public/world security-group ingress, public IP, EBS volume/default encryption, and public EBS snapshots. | Region supplied by backend configuration; cover IPv4 and IPv6 and all-protocol ingress; read-only. | `pytest tests/test_aws_audit.py -k ec2 -q`; unsafe ingress, public IP/snapshot, encryption states. | ☐ |
| AWS-06 | `audit_vpc(region)` | Checks default VPC and VPC flow-log coverage. | Region supplied by backend; account with no VPCs handled without false finding; read-only. | `pytest tests/test_aws_audit.py -k vpc -q`; default/non-default VPC, flow logs absent/present. | ☐ |
| AWS-07 | `audit_databases(region)` | Checks RDS instance/cluster public access, storage encryption, Multi-AZ, backup retention, deletion protection, and public snapshots. | Region supplied by backend; instance/cluster/snapshot API failures explicit; read-only. | `pytest tests/test_aws_audit.py -k rds -q`; compliant and insecure cases plus denied operations. | ☐ |
| AWS-08 | `audit_cloudtrail()` | Discovers regions and checks trail coverage, multi-region logging, logging status, and log-bucket protections. | Global/multi-region; distinguish absent trail from inability to inspect; read-only. | `pytest tests/test_aws_audit.py -k cloudtrail -q`; region coverage, logging stopped, bucket protection. | ☐ |
| AWS-09 | `audit_guardduty(region)` | Checks detector presence/status and relevant findings state. | Region-specific; missing detector is distinct from access/error condition; read-only. | `pytest tests/test_aws_audit.py -k guardduty -q`; detector present/absent/error cases. | ☐ |
| AWS-10 | `finding()` / `error_finding()` / `is_error()` / `collect_pages()` | Standardizes finding structure, classifies expected AWS errors, and exhausts paginated API results. | Preserve check ID/service/region/severity/evidence; pagination must not silently truncate; avoid secret/error detail disclosure. | `pytest tests/test_aws_audit.py -q`; test standard shape, error classification, multiple pages, terminal page. | ☐ |
| AWS-11 | `AWSAuditor.__init__()` | Initializes auditor clients and configured primary region. | Must use normal Boto3 credential resolution; tests inject/mock clients; no access keys in constructor arguments or logs. | Initialize with test region and fake clients; verify each regional call uses expected region. | ☐ |

## 6. Frontend function and interaction tests

| ID | Function / surface | Expected behavior | Constraints and negative cases | Test / pass condition | Result |
|---|---|---|---|---|---|
| UI-01 | `setAccessToken()`, `getApiBaseUrl()`, `saveApiBaseUrl()` | Holds access token in memory; selects configured or saved API origin; trims trailing slashes. | AuthProvider persists the JWT in localStorage; passwords are never stored. Base URL is not a secret. Empty override removes saved value. | Manual/browser: inspect storage; verify JWT and base URL persist until sign-out or expiry and requests target expected origin. | ☐ |
| UI-02 | `request()` / exported `api.*` methods | Sends JSON requests to existing API routes, attaches bearer token, parses JSON/text, converts errors to `ApiError`, and emits session-expired event on protected 401. | No invented routes; preserve abort errors; handle network failure, non-JSON, API error envelope; no secret in user-visible errors. | Mock API/browser: verify login/chat/assessment/RAG/AWS/health route, headers, payload, failure handling. | ☐ |
| UI-03 | `AuthProvider()` / `useAuth()` / `ProtectedRoute()` | Manages login state and restricts application pages to authenticated users. | Restore an unexpired JWT on refresh; unauthenticated users reach login; expired session signs out and removes the stored JWT. | Browser: open private route signed out, login, refresh/session behavior, trigger 401. | ☐ |
| UI-04 | `SessionEvents()` / `App()` | Registers and cleans up 401 session-expiry handler; routes login and protected pages with lazy-loading state. | No duplicate event handler after unmount; unknown route redirects; ensure all declared pages can load. | Browser: navigate each route, unknown route, session expiry, loading fallback. | ☐ |
| UI-05 | `useAssessments()`, `useAssessment()`, `useRagStatus()`, `useBackendHealth()`, `useAwsIdentity()` | Fetches/caches backend data with intended query keys, freshness, enabled and retry behavior. | No fake fixtures in live UI; disabled queries should not call API; errors must remain visible/retryable where supported. | Browser/network panel: confirm expected endpoint, cache behavior, loading/error/empty states. | ☐ |
| UI-06 | `useChatMutation()`, `useRagQueryMutation()` | Sends user-submitted chat/RAG requests and exposes pending/success/error state. | Do not display agent-level streaming progress; outputs only after complete API response. | Browser: pending state, success data, provider/API failure state. | ☐ |
| UI-07 | `MarkdownView()` | Renders Compliance/Senior text with CommonMark and GFM tables. Links open in new tab with `rel=noreferrer`; table wrapper supports horizontal scrolling. | Raw HTML is not enabled. Cloud report JSON is not passed to this renderer. | Manual/smoke: heading, emphasis, list, inline code, table, link, raw HTML input remains inert. | ☐ |
| UI-08 | `AgentWorkflow()` / `outputText()` | Shows Cloud, Compliance, Senior outputs separately, expandable details, and real completion/running status. | Must not fabricate progress or output; Cloud remains JSON; Compliance/Senior rendered Markdown; empty state distinct from empty-string success. | Browser: start audit and compare every displayed output to API response; expand/collapse, failure, empty results. | ☐ |
| UI-09 | `CloudAudit.submit()` / `toggleService()` | Selects one or more services, forms a natural-language request, runs chat, stores actual response, and invalidates assessments/identity queries. | At least one service required; optional context max 1,500 chars; region is backend-controlled, not a per-request override; disabled while request pending. | Browser: toggle services, empty selection validation, context limit, successful run and API error. | ☐ |
| UI-10 | `Login.submit()` | Submits configured username/password, stores access token in app memory, then navigates into protected app. | No credential persistence; wrong credentials show actionable error without echoing password. | Browser: valid and invalid login; inspect storage/network payload; clear token on sign-out. | ☐ |
| UI-11 | `Compliance.submit()` | Sends direct question to existing local RAG query route and displays passages/citations. | This endpoint does not invoke AWS or hosted LLM; validate non-empty question and surface unavailable-index errors. | Browser: query with valid text and missing-index/error response; check cited source output. | ☐ |
| UI-12 | `Dashboard()` | Shows backend-backed security summary, severity chart, latest assessments, and compliance coverage. | Values must derive from API data; no mock or fabricated findings; handle no assessments and failed queries. | Browser with empty and populated assessment history; cross-check counts against source records. | ☐ |
| UI-13 | `Findings()` / `FindingsTable()` / `SeverityPill()` | Lists actual findings with severity, resource, evidence, remediation, and search/filter behavior. | Never invent a finding; handle missing optional fields and no matches; search should not hide error/loading states. | Browser: all severity values, text search, no match, empty data, long resource strings. | ☐ |
| UI-14 | `Reports()` / `getRisk()` | Lists persisted assessments and derives a report risk display from saved report data. | Risk must be derived from actual response; handle missing counts/report and unknown assessment. | Browser: compare derived risk to assessment counts and open a report. | ☐ |
| UI-15 | `ReportDetail()` / `downloadReport()` | Loads a selected saved assessment and provides its report/reviews for viewing/download. | Must use route assessment ID and actual saved response; do not expose another assessment's data; download contents must be user-visible response data only. | Open valid/unknown IDs; verify fetched ID and downloaded output match. | ☐ |
| UI-16 | `Agents()` / `AgentWorkflow()` / `outputText()` | Explains Cloud → Compliance → Senior sequence and expands real output details. | Non-streaming status only; no fabricated per-agent progress. Cloud JSON remains JSON; Compliance/Senior use Markdown. | Compare UI output fields to completed API result; inspect running/failure and expand/collapse states. | ☐ |
| UI-17 | `Settings()` / `saveSettings()` / `refresh()` / `IntegrationRow()` | Saves a validated HTTP(S) backend origin, applies UI preferences, and refreshes integration statuses from API. | Do not allow non-HTTP(S) protocols; do not display credentials; status means backend-reported state only. | Save valid/invalid URLs; refresh failing integrations; reload saved preferences. | ☐ |
| UI-18 | `Login()` / `submit()` | Sends credentials to login API and surfaces authentication errors. | Password not echoed or persisted; successful JWT persists in localStorage until expiry or sign-out. | Try valid/invalid credentials and inspect local/session storage. | ☐ |
| UI-19 | `Compliance()` / `submit()` / `SourceList()` | Queries local RAG endpoint and displays attributed passages and source references. | This is retrieval only, not a full Cloud/LLM audit; unavailable index must show error instead of empty success. | Query known prompt and unavailable-store response; verify no AWS/chat request is made. | ☐ |
| UI-20 | `StatCard()` / `SeverityChart()` / `LatestAudits()` / `reportSeverity()` | Renders numeric status cards, severity distribution and latest audit severity summary. | Counts must match source report; zero values should render as zero, not missing; unknown severities handled clearly. | Compare synthetic report totals with chart/card values and zero-finding report. | ☐ |
| UI-21 | `Button()`, `Card()`, `Badge()`, `Input()`, `PageHeading()`, `LoadingState()`, `ErrorState()`, `EmptyState()` | Reusable visual and interaction primitives with loading, error, empty, and action states. | Preserve keyboard focus/labels and disabled state; error/retry state must not claim success. | Keyboard-only navigation and visual checks for loading/error/empty variants. | ☐ |
| UI-22 | `AppLayout()` / `Sidebar()` / `Topbar()` / `ProtectedRoute()` | Provides responsive navigation, page shell, and authenticated route guard. | Mobile menu opens/closes; compact nav persists only intended preference; protected pages redirect when signed out. | Desktop/mobile navigation, keyboard controls, direct-route auth check. | ☐ |
| UI-23 | `RouteLoading()` / `SessionEvents()` / `App()` | Loads route chunks, provides suspense indicator, and returns expired sessions to login. | Event listener cleanup on unmount; unknown route redirects; no duplicate listener side effects. | Navigate all routes, unknown route, and trigger session-expired event. | ☐ |
| UI-24 | `AuthProvider()` / `signIn()` / `signOut()` / `useAuth()` | Exposes authenticated state and methods to the React tree. | Hook outside provider throws explicit error; sign-out clears the API token, stored JWT, and username. | Test app provider lifecycle and sign-in/sign-out; verify stored JWT survives refresh and is removed on sign-out or expiry. | ☐ |
| UI-25 | `useLatestAudit()` | Currently returns `null` from a disabled query and makes no API call. | It is not a source for live audit data; verify the UI uses the chat mutation result or persisted assessment instead. | Confirm no request is issued and no page labels null as a completed audit. | ☐ |

## 7. Manual end-to-end checklist

Only run the live audit portion after confirming the AWS account and inference
data-transmission approval.

| ID | Action | Expected result | Result / notes |
|---|---|---|---|
| E2E-01 | Start backend with local DB and valid test auth configuration; do not print environment values. | `/health` responds; `/ready` reports local status; backend starts without AWS/provider credentials for non-integrated routes. | ☐ |
| E2E-02 | Start frontend and open `/login`. | Login page loads; API origin points to intended backend; no browser-visible AWS/provider credentials. | ☐ |
| E2E-03 | Submit invalid login. | Clear error shown; protected pages remain unavailable; password/token not persisted. | ☐ |
| E2E-04 | Login with approved test account and visit Dashboard, Findings, Reports, Compliance, Agents, Settings. | Protected routing works; loading/empty/error states are truthful; no fabricated audit results. | ☐ |
| E2E-05 | Run direct Compliance/RAG query using approved local index. | Returned passages and sources match API data; no AWS/LLM operation is invoked by direct RAG query. | ☐ |
| E2E-06 | Run authorized narrow Cloud audit in live account. | Read-only checks return structured Cloud findings, severity counts align, and assessment is persisted. Record only non-sensitive summary. | ☐ |
| E2E-07 | Inspect Compliance and Senior outputs from that same completed chat. | Responses are separate; Markdown headings/tables render; raw HTML does not execute; source citations remain attributable. | ☐ |
| E2E-08 | Open saved assessment detail/history. | Persisted report and reviews match the completed response. Citations are expected in chat response but not necessarily stored in assessment history. | ☐ |
| E2E-09 | Simulate unavailable inference provider or force a controlled request failure. | UI reports failure; no completed/fabricated agent outputs; no false successful assessment. | ☐ |
| E2E-10 | Sign out or expire token and retry protected request. | Session is cleared and user returns to login. | ☐ |

## 8. Test record

| Field | Record |
|---|---|
| Test date / tester | |
| Branch / revision | |
| Python version | |
| Node.js / npm versions | |
| Backend test result | |
| Ruff result | |
| Frontend lint result | |
| Frontend build result | |
| Live AWS test authorized? | |
| Live inference test authorized? | |
| Failed test IDs and details (no secrets/account identifiers) | |
| Follow-up owner / action | |

## 9. Existing automated test files

Use the test files below for the related backend coverage; do not replace
mocked automated tests with live credentials:

| File | Primary coverage |
|---|---|
| `tests/test_auth.py` | Login, token validation, route protection |
| `tests/test_chat_api.py` | Separate chat API response fields |
| `tests/test_chat_workflow.py` | Workflow sequence and hand-offs |
| `tests/test_cloud_agent.py` | Allowlisted audit tool selection and validation |
| `tests/test_llm_service.py` | Provider client behavior and errors |
| `tests/test_rag.py` | FAISS retrieval, metadata, RAG endpoints and errors |
| `tests/test_aws_audit.py` | Service-specific AWS audit findings |
| `tests/test_aws.py` | AWS identity endpoint/service |
| `tests/test_assessments.py` | Assessment persistence and history |
| `tests/test_health.py` | Health/readiness and request middleware |
| `tests/test_config.py` | Configuration defaults and secret handling |
| `tests/test_errors.py` | Safe API error behavior |
