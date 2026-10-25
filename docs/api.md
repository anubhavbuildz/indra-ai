# API overview

The versioned API is mounted at `/api/v1`. FastAPI docs are available at
`/docs` only while `APP_ENV=development`.

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/health` | Process health; no external provider calls |
| GET | `/ready` | Local database/index configuration state |
| POST | `/api/v1/chat` | Senior review, repaired Terraform proposal, and compliance assessment in separate fields; never runs proposed actions |
| POST / GET | `/api/v1/projects` | Create and paginate projects |
| GET / PATCH | `/api/v1/projects/{project_id}` | Read or update safe project metadata |
| GET | `/api/v1/rag/status` | Index availability and counts |
| POST | `/api/v1/rag/query` | Return attributed passages or an empty not-indexed response |
| POST | `/api/v1/terraform/generate` | Propose HCL; does not execute it |
| POST | `/api/v1/terraform/repair` | Revise safe HCL from caller-supplied diagnostics; does not run Terraform |
| POST | `/api/v1/terraform/validate` | Fixed init/format/validate operations |
| POST | `/api/v1/terraform/plan` | Fixed init/validate/plan operations; never applies |
| POST | `/api/v1/terraform/apply` | Always returns 501 |
| POST | `/api/v1/terraform/destroy` | Always returns 501 |
| GET | `/api/v1/aws/identity` | Optional STS identity from the standard credential chain |

Expected errors use `{ "error": { "code": "...", "message": "...",
"details": {} } }`. Validation errors include field paths and error types,
not submitted values. Operational response summaries avoid raw Terraform and
provider output.

The chat response includes `assistant_response` (the senior agent's final
assessment of both outputs), `terraform` (the proposed Terraform after
senior-agent repair based on that assessment), and `compliance` as separate
fields. These values are not concatenated. The repaired proposal is not
Terraform-validated, planned, or deployed by the chat workflow. System prompts
are maintained in the packaged Markdown files under
`app/services/llm/roles/`; the senior role separates review and repair prompts.

Terraform repair accepts `project_id`, `code`, and a non-empty `errors` list.
The source and result are checked against the Terraform execution policy. The
repair endpoint calls the configured OpenAI-compatible provider using
`nvidia/nemotron-3-super-120b-a12b`; it does not run `fmt`, `validate`, `plan`,
`apply`, or `destroy`.
