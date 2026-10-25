# API overview

The versioned API is mounted at `/api/v1`. FastAPI docs are available at
`/docs` only while `APP_ENV=development`.

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/health` | Process health; no external provider calls |
| GET | `/ready` | Local database/index configuration state |
| POST | `/api/v1/chat` | Run a fresh Prowler scan for the request's optional region/services and summarize findings with the user's question/history |
| POST / GET | `/api/v1/projects` | Create and paginate projects |
| GET / PATCH | `/api/v1/projects/{project_id}` | Read or update safe project metadata |
| GET | `/api/v1/rag/status` | Index availability and counts |
| POST | `/api/v1/rag/query` | Return attributed passages or an empty not-indexed response |
| POST | `/api/v1/prowler/scan` | Run Prowler CLI, parse JSON-OCSF findings, and return findings with an AI summary |
| GET | `/api/v1/aws/identity` | Optional STS identity from the standard credential chain |

Both scan routes accept optional `region`, `services`, and `prowler_args`
fields. Additional Prowler arguments are passed as argv tokens (not through a
shell); arguments that override region, credentials, or report-output settings
are rejected. If `region` and `services` are omitted, the scanner uses
`AWS_REGION` and Prowler's default service scope. Both routes use `PROWLER_BIN` and
the process's standard AWS credential chain. No AWS credentials are accepted
in request bodies. Both routes require a configured Prowler executable, AWS
credentials, and NVIDIA inference. Scan responses include `operation_id`, `status`,
`region`, `findings_count`, `prowler_summary`, `compliance`,
`assistant_response` (the senior agent's cross-check), source references, and
the parsed `findings`. The compliance agent assesses the Prowler summary
against retrieved knowledge-base passages; the senior agent reviews both
assessments and their evidence.

Expected errors use `{ "error": { "code": "...", "message": "...",
"details": {} } }`. Validation errors include field paths and error types,
not submitted values. CLI output and report contents are not included in
operational error messages.

Prowler's output is read from a server-created temporary directory and is not
persisted. JSON reports above 5 MB or 5,000 findings are rejected. Summarizing
findings uses bounded batches and consolidation so every finding is analyzed
without exceeding the per-prompt input limit. A single finding or conversation
that cannot fit that limit is rejected explicitly; no partial summary is
presented as complete. Large scans may require multiple inference calls.
