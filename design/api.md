# API overview

The versioned API is mounted at `/api/v1`. FastAPI docs are available at
`/docs` only while `APP_ENV=development`. Every versioned route requires an
`Authorization: Bearer <access_token>` header except
`POST /api/v1/auth/login`. The root, `/health`, `/ready`, and development API
documentation routes remain public.

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/health` | Process health; no external provider calls |
| GET | `/ready` | Local database configuration state |
| POST | `/api/v1/auth/login` | Issue a short-lived JWT for the configured environment account |
| POST | `/api/v1/chat` | Run configured-region AWS checks, retrieve local guidance, and return Compliance/Senior reviews with sources |
| GET | `/api/v1/rag/status` | Report local FAISS and metadata availability without loading the embedder |
| POST | `/api/v1/rag/query` | Retrieve local guidance passages and attributed sources |
| GET | `/api/v1/assessments` | List persisted audit assessments |
| GET | `/api/v1/assessments/{assessment_id}` | Read audit and reviewer output |
| GET | `/api/v1/aws/identity` | Optional STS identity from the standard credential chain |

Chat accepts `message` and bounded `history`. The Cloud
agent uses configured inference to interpret the request and select from a
fixed allowlist of read-only Boto3 audit functions for S3, IAM, EC2/EBS, VPC,
RDS, CloudTrail, and GuardDuty. EC2/EBS, VPC, RDS, and GuardDuty use
`AWS_REGION`; CloudTrail discovers enabled regions. The model cannot supply
arbitrary function names, arguments, or regions. Cloud returns the structured
tool results. The workflow retrieves relevant passages from the configured
local FAISS store, then Compliance summarizes the report using the audit
findings and attributed guidance. Senior reviews both the report and summary.
These steps run sequentially. The response keeps
`cloud_agent_response` (the structured audit report),
`compliance_agent_response`, and `senior_agent_response` in separate fields,
along with the persisted `assessment_id`, `status`, and a `sources` list for
the retrieved guidance. Each successful chat creates an Assessment record that stores the
request, structured audit report, Compliance review, and Senior Reviewer
output. Assessment history can be fetched through the assessment endpoints.
The source citations are returned in chat but are not stored in the Assessment.
AWS credentials are never accepted in request bodies.
The route requires AWS read permissions and configured inference for the Cloud,
Compliance, and Senior steps. Chat also requires the configured local FAISS
index and matching metadata. The AWS identity route independently checks the
process credential chain.

The Compliance and Senior response properties remain plain text strings and
may contain Markdown. Markdown formatting is performed by clients, not by the
API. The React frontend uses `react-markdown` with `remark-gfm` for headings,
lists, emphasis, links, and tables; it does not enable raw HTML. Treat response
text as untrusted and do not inject it as HTML.

`POST /api/v1/rag/query` accepts a JSON `question` from 1 to 8,000 characters:

```json
{"question": "How should AWS storage be encrypted?"}
```

It returns `question`, up to three `passages` (`title`, `content`, `source`,
and optional `uri`), and a matching `sources` citation list. It does not call
AWS or the LLM provider. A missing, corrupt, or mismatched local store returns
a safe HTTP 503 error.

`GET /api/v1/rag/status` reports the configured embedding model and whether
the index and metadata files are present. It does not import FAISS, validate
the index/metadata pair, load the embedding model, or return server filesystem
paths. Pair compatibility is checked during retrieval.

Expected errors use `{ "error": { "code": "...", "message": "...",
"details": {} } }`. Validation errors include field paths and error types,
not submitted values.

### Login

`POST /api/v1/auth/login` accepts the single account configured through
`AUTH_USERNAME`, `AUTH_PASSWORD`, and `JWT_SECRET_KEY`:

```json
{
  "username": "configured-user",
  "password": "configured-password"
}
```

A successful request returns a 2-hour HS256 access token:

```json
{
  "access_token": "signed-jwt",
  "token_type": "bearer",
  "expires_in": 7200
}
```

The signing key must be at least 32 bytes. Protected routes validate the
token's signature and expiration. Send the token to all other versioned routes:

```http
Authorization: Bearer <access_token>
```

Missing, invalid, or expired tokens are rejected with HTTP 401. The login route
is public so clients can obtain tokens.
