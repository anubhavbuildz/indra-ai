# API overview

The versioned API is mounted at `/api/v1`. FastAPI docs are available at
`/docs` only while `APP_ENV=development`.

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/health` | Process health; no external provider calls |
| GET | `/ready` | Local database configuration state |
| POST | `/api/v1/auth/login` | Issue a short-lived JWT for the configured environment account |
| POST | `/api/v1/chat` | Run configured-region AWS checks, summarize findings, and return a senior review |
| GET | `/api/v1/assessments` | List persisted audit assessments |
| GET | `/api/v1/assessments/{assessment_id}` | Read audit and reviewer output |
| GET | `/api/v1/aws/identity` | Optional STS identity from the standard credential chain |

Chat accepts `message` and bounded `history`. The Cloud
agent uses configured inference to interpret the request and select from a
fixed allowlist of read-only Boto3 audit functions for S3, IAM, EC2/EBS, VPC,
RDS, CloudTrail, and GuardDuty. EC2/EBS, VPC, RDS, and GuardDuty use
`AWS_REGION`; CloudTrail discovers enabled regions. The model cannot supply
arbitrary function names, arguments, or regions. Cloud returns the structured
tool results. Next, Compliance summarizes that report, and Senior reviews both
the report and summary. These steps run sequentially; retrieval is not part of
this workflow. The response keeps
`cloud_agent_response` (the structured audit report),
`compliance_agent_response`, and `senior_agent_response` in separate fields,
along with the persisted `assessment_id`, `status`, and an empty `sources`
list. Each successful chat creates an Assessment record that stores the
request, structured audit report, Compliance review, and Senior Reviewer
output. Assessment history can be fetched through the assessment endpoints.
Retrieval is not currently part of the application. AWS credentials are never
accepted in request bodies.
The route requires AWS read permissions and configured inference for the Cloud,
Compliance, and Senior steps. The AWS identity route independently checks the
process credential chain.

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

A successful request returns a 30-minute HS256 access token:

```json
{
  "access_token": "signed-jwt",
  "token_type": "bearer",
  "expires_in": 1800
}
```

The signing key must be at least 32 bytes. The token can be checked with the
`verify_access_token` helper. Existing endpoints do not currently enforce
authentication; issuing a token does not grant route protection.
