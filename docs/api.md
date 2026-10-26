# API overview

The versioned API is mounted at `/api/v1`. FastAPI docs are available at
`/docs` only while `APP_ENV=development`.

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/health` | Process health; no external provider calls |
| GET | `/ready` | Local database/index configuration state |
| POST | `/api/v1/chat` | Run configured-region AWS checks, summarize findings, and return a senior review |
| POST / GET | `/api/v1/projects` | Create and paginate projects |
| GET / PATCH | `/api/v1/projects/{project_id}` | Read or update safe project metadata |
| GET | `/api/v1/rag/status` | Index availability and counts |
| POST | `/api/v1/rag/query` | Return attributed passages or an empty not-indexed response |
| GET | `/api/v1/aws/identity` | Optional STS identity from the standard credential chain |

Chat accepts `message`, optional `project_id`, and bounded `history`. The Cloud
agent uses configured inference to interpret the request and select from a
fixed allowlist of read-only Boto3 audit functions for S3, IAM, EC2/EBS, VPC,
RDS, CloudTrail, and GuardDuty. EC2/EBS, VPC, RDS, and GuardDuty use
`AWS_REGION`; CloudTrail discovers enabled regions. The model cannot supply
arbitrary function names, arguments, or regions. Cloud returns the structured
tool results. Next, Compliance summarizes that report, and Senior reviews both
the report and summary. These steps run sequentially; RAG is not yet part of
the Compliance step. The response keeps
`cloud_agent_response` (the structured audit report),
`compliance_agent_response`, and `senior_agent_response` in separate fields,
along with `operation_id`, `status`, and an empty `sources` list reserved for
future RAG integration. AWS credentials are never accepted in request bodies.
The route requires AWS read permissions and configured inference for the Cloud,
Compliance, and Senior steps. The AWS identity route independently checks the
process credential chain.

Expected errors use `{ "error": { "code": "...", "message": "...",
"details": {} } }`. Validation errors include field paths and error types,
not submitted values.
