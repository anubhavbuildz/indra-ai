# Indra Backend: Project Overview

## What the project solves

Indra is a backend for AWS security assessment and AI-assisted review. It
provides a single API for selecting a bounded set of read-only AWS checks,
returning structured findings, and producing two sequential model reviews of
those findings. It also offers persisted assessment history, environment-configured JWT login,
and an optional AWS caller-identity check. Retrieval/RAG is not currently
included.

The problem it addresses is the effort required to collect security-relevant
AWS configuration signals and turn them into a clear, reviewable summary.
Indra combines deterministic AWS API checks with model-generated explanation
while keeping the observations and the model's interpretation in separate
response fields.

Indra is a decision-support scaffold, not a cloud control plane or a complete
security product. It does not remediate AWS resources, inspect every AWS
service or control, certify compliance, or guarantee that an account is
secure.

## Main capabilities

- **AWS audit chat:** A model selects from a fixed list of read-only audit
  functions. The backend validates those selections, runs the matching AWS
  checks, validates the structured report, and returns it with separate
  Compliance and Senior reviews.
- **Assessment history:** Each successful chat run creates an assessment
  record containing the question, audit report, Compliance review, and Senior
  Reviewer output.
- **AWS identity:** An optional endpoint calls STS `GetCallerIdentity` using
  the server's standard Boto3 credential chain.
- **Authentication:** A single environment-configured account can obtain
  short-lived JWT access tokens. Existing routes do not yet enforce them.
- **Health and readiness:** Local endpoints report process status and basic
  database configuration without calling AWS or the inference provider.

## Architecture

```mermaid
flowchart TD
    Client[API client] --> Middleware[Request limits and request ID]
    Middleware --> Routes[FastAPI routes and Pydantic schemas]
    Routes --> Chat[Chat workflow]
    Chat --> Cloud[Cloud tool-selection agent]
    Cloud --> LLM[OpenAI-compatible inference API]
    Cloud --> Allowlist[Fixed audit function allowlist]
    Allowlist --> Auditor[AWSAuditor]
    Auditor --> AWS[AWS APIs via Boto3 credential chain]
    Auditor --> Report[Validated AuditReport]
    Report --> Compliance[Compliance summary agent]
    Compliance --> Senior[Senior review agent]
    Report --> Response[Structured chat response]
    Compliance --> Response
    Senior --> Response
    Routes --> Assessments[Assessment service and repository]
    Assessments --> DB[(SQLite by default / PostgreSQL compatible)]
    Routes --> Identity[Optional STS identity service]
```

### Request and application layers

`app/main.py` creates the FastAPI application, registers the error handlers
and middleware, mounts health and versioned API routes, and applies database
migrations during application startup. Routes are deliberately thin: Pydantic
schemas validate input/output, dependency injection provides settings and
database sessions, and services encapsulate the work.

The application is divided into:

| Area | Responsibility |
| --- | --- |
| `app/api/` | HTTP routes and router registration |
| `app/schemas/` | Request, response, and AWS audit report validation |
| `app/core/` | Settings, stable API errors, logging, and bounded request middleware |
| `app/services/` | Chat agents/workflow, AWS identity, and project use cases |
| `app/repositories/` | Database queries and assessment persistence |
| `app/db/` | SQLAlchemy models, engine/session setup, and migration integration |
| `app/tools/audit/aws/` | Service-specific read-only Boto3 audit functions |
| `migrations/` | Alembic environment and versioned schema changes |
| `scripts/` | Local environment checks |
| `tests/` | API, service, workflow, configuration, and audit tests |
| `docs/` | API, architecture, security, and project documentation |

## AWS audit and chat workflow

`POST /api/v1/chat` runs the following steps:

1. The API validates a message (up to 8,000 characters) and optional
   conversation history (up to 20 messages, each up to 4,000 characters).
2. The Cloud agent sends the request, history, and a fixed set of tool
   definitions to the configured OpenAI-compatible inference provider.
3. The provider may select only allowlisted audit tools. Tool arguments must
   be empty; arbitrary AWS operations, resource arguments, and regions are
   rejected.
4. `AWSAuditor` executes selected checks using Boto3. S3 and IAM checks are
   global; EC2/EBS, VPC, RDS, and GuardDuty checks use `AWS_REGION`.
   CloudTrail checks discover enabled regions.
5. Results are validated against the `AuditReport` schema. Findings include
   service, region, check identifiers, severity, details, and any available
   evidence or error.
6. The Compliance agent summarizes the structured report. The Senior agent
   then reviews that report and the Compliance summary for unsupported claims
   and uncertainty.
7. The API returns the report, Compliance summary, Senior review, an operation
   identifier, a completed status, and a `sources` array.

The current audit functions cover:

| Service | Selected checks |
| --- | --- |
| S3 | Public-access block, public bucket policy/ACL, default encryption, versioning, TLS-only policy, and server access logging |
| IAM | Root-account access keys |
| EC2 / EBS | World-open IPv4/IPv6 security-group ingress, public IPs on running instances, unencrypted volumes, EBS default encryption, and public snapshots |
| VPC | Default VPCs and VPC Flow Logs |
| RDS | Public accessibility, storage encryption, Multi-AZ, backup retention, deletion protection, and public manual snapshots |
| CloudTrail | Multi-region coverage, active logging, log-file validation, and log-bucket public-access-block/encryption |
| GuardDuty | Detector presence and enabled state in the configured region |

The model chooses which checks to run; a request does not necessarily run every
check. The AWS process identity must have the read permissions required by
selected checks. Some permission and service errors are returned as findings.
The results are point-in-time observations and should be reviewed before
making operational decisions.

### Inference provider

The default provider is Nebius Token Factory through the OpenAI Chat
Completions-compatible adapter. Configuration includes a base URL, API key,
model, and adapter format. A valid `NVIDIA_API_KEY` is required for chat
inference. Provider credentials are server-side and are not accepted in API
request bodies.

## Other API workflows

The versioned API is mounted at `/api/v1`; `/health` and `/ready` are mounted
at the root.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Process health; no AWS or model call |
| `GET` | `/ready` | Basic database configuration status |
| `POST` | `/api/v1/auth/login` | Issue a short-lived JWT for the configured environment account |
| `POST` | `/api/v1/chat` | AWS audit and sequential model review |
| `GET` | `/api/v1/assessments` | List persisted audit assessments |
| `GET` | `/api/v1/assessments/{assessment_id}` | Read audit and reviewer output |
| `GET` | `/api/v1/aws/identity` | Optional STS caller identity lookup |

Expected application errors use a stable JSON envelope:

```json
{
  "error": {
    "code": "error_code",
    "message": "Safe explanation.",
    "details": {}
  }
}
```

Request validation errors report field locations and error types rather than
echoing submitted values. The request middleware enforces a configurable body
size limit and attaches an `X-Request-ID` response header.

## Retrieval status

Retrieval/RAG is intentionally removed from the current application and will
be designed and implemented separately. Chat returns an empty `sources`
array; no RAG endpoints, index loader, embedding service, or ingestion command
are available at this stage.

## Persistence and database migrations

SQLAlchemy models currently include:

- **Assessment:** question, audit report, Compliance review, Senior Reviewer
  output, status, and timestamps.
- **Operation:** assessment reference, operation type/status, timestamps, and
  optional safe summary.

SQLite is the default database. PostgreSQL-compatible URLs are supported when
the optional PostgreSQL driver is installed. Alembic migrations are located in
`migrations/` and can be applied with `alembic upgrade head`; application
startup also upgrades the configured database to the current migration head.
Migrations remove the database `users` table, rename projects to assessments,
and add fields for persisted audit and reviewer results. Login credentials are
environment configuration and are not persisted as user records. Every
successful chat creates an assessment row and returns its `assessment_id`.
Assessment records can be listed or fetched by ID.

## Configuration

Settings are loaded from environment variables or an optional `.env` file.
`.env.example` is the placeholder template. See `app/core/config.py` for the
source of defaults.

For the single-account login endpoint, set `AUTH_USERNAME`,
`AUTH_PASSWORD`, and a unique `JWT_SECRET_KEY` of at least 32 bytes.
`POST /api/v1/auth/login` accepts a JSON username/password pair and returns a
30-minute HS256 access token. The app does not currently enforce these tokens
on the other API routes; login is not authorization or route protection.

| Variable | Default | Use |
| --- | --- | --- |
| `APP_NAME` | `Indra API` | Service name |
| `APP_ENV` | `development` | Development enables `/docs` and `/redoc` |
| `DEBUG` | `false` | FastAPI debug mode |
| `API_V1_PREFIX` | `/api/v1` | Versioned route prefix |
| `DATABASE_URL` | `sqlite:///./data/indra.db` | Database connection |
| `AUTH_USERNAME` | empty | Configured login account name |
| `AUTH_PASSWORD` | empty | Configured login account password |
| `JWT_SECRET_KEY` | empty | JWT signing key; minimum 32 bytes when configured |
| `NVIDIA_BASE_URL` | `https://api.tokenfactory.nebius.com/v1` | Inference endpoint |
| `NVIDIA_API_KEY` | empty | Server-side inference credential |
| `NVIDIA_MODEL` | `nvidia/Nemotron-3_5-Lightning` | Inference model |
| `NVIDIA_API_FORMAT` | `openai-chat-completions` | Provider adapter format |
| `AWS_REGION` | `us-east-1` | Regional audits and STS identity |
| `CORS_ORIGINS` | empty | Comma-separated allowed origins |
| `MAX_REQUEST_BYTES` | `1048576` | Request-body limit, bounded by settings validation |

AWS credentials use the standard Boto3 credential chain and are checked only
when AWS functionality is called. The application can start without AWS or
inference credentials; chat and identity functionality require their
respective integrations.

## Run and develop

From the `indra-ai/` project directory:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
cp .env.example .env
```

Set `NVIDIA_API_KEY` in `.env` to enable model calls. Configure AWS access
through a suitably scoped role/profile or another standard Boto3 credential
source. Do not use privileged credentials for routine operation.

Start the API:

```bash
uvicorn app.main:app --reload
```

Development API docs are available at `http://127.0.0.1:8000/docs` when
`APP_ENV=development`.

Useful validation commands:

```bash
pytest
ruff check .
ruff format --check .
python -m compileall -q app tests
```

Tests use mocks for external AWS/provider dependencies and should not require
live credentials. Live calls can incur AWS or provider usage.

## Security boundaries and limitations

- There is no API authorization, tenant isolation, or complete audit trail.
  Assessment IDs are references, not access controls.
- AWS chat uses a fixed allowlist of read-only audit calls. It does not modify
  AWS resources and does not cover every service or control.
- AWS identity calls STS only; it does not inspect account resources or IAM
  policies.
- Model-generated Compliance and Senior reviews are decision support, not
  formal compliance mappings, legal advice, certification, or guarantees.
- Retrieval/RAG is currently out of scope; chat cannot cite local knowledge
  base passages.
- Do not store credentials in assessments, operations, prompts, documents, logs,
  or source control. Keep `.env` private and use least-privilege cloud access.

## Further reading

- [API overview](./api.md)
- [Architecture notes](./architecture.md)
- [Security notes](./security.md)
- [Contribution guide](../CONTRIBUTING.md)
