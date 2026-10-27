# Architecture

```mermaid
flowchart LR
    Client --> FastAPI
    FastAPI --> Chat[Sequential chat workflow]
    Chat --> Cloud[Cloud tool-selection agent]
    Cloud --> Nebius[Nebius Token Factory]
    Nebius -->|allowlisted function calls| Cloud
    Cloud --> Auditor[Read-only Boto3 audit functions]
    Auditor --> AWS[AWS APIs via standard credential chain]
    Auditor --> Report[Validated AuditReport]
    Chat --> RAG[Local FAISS retrieval]
    Report --> Compliance[Compliance summary with guidance]
    RAG --> Compliance
    Compliance --> Nebius
    Report --> Senior[Senior review]
    Compliance --> Senior
    Senior --> Nebius
    Report --> ChatResponse[Separate chat response fields]
    Compliance --> ChatResponse
    Senior --> ChatResponse
    FastAPI --> Assessments[Assessment persistence]
    Assessments --> DB[(SQLite or PostgreSQL)]
    FastAPI --> STS[Optional AWS identity lookup]
```

The application is a FastAPI service. Routes validate input and inject
settings; service modules own provider, AWS, and persistence boundaries.
SQLAlchemy uses SQLite by default and supports PostgreSQL-compatible
URLs. Alembic migrations are available for managed deployments.

## Chat workflow

`POST /api/v1/chat` runs these stages sequentially:

1. **CloudAgent** sends the user's request and a fixed allowlist of read-only
   audit functions to the configured OpenAI-compatible model. It accepts only
   function calls from that allowlist with empty arguments.
2. The application executes the selected functions through `AWSAuditor`.
   S3 and IAM checks are global; EC2, VPC, RDS, and GuardDuty checks use
   `AWS_REGION`; CloudTrail checks discover enabled regions. AWS credentials
   come from the standard Boto3 credential chain.
3. Results are validated against the Pydantic `AuditReport` schema.
4. The workflow embeds the request with the configured sentence-transformers
   model and retrieves up to three matching local documents from FAISS.
5. **ComplianceAgent** creates a short summary using the report, request, and
   retrieved guidance, distinguishing account findings from general guidance.
6. **SeniorAgent** reviews the same report and Compliance summary.
7. The API returns the structured report, Compliance summary, Senior review,
   and attributed `sources`.

Checks include S3 public policy/ACL, TLS, versioning, and logging; IPv4/IPv6
public security-group ingress; CloudTrail logging and log-bucket protection;
GuardDuty detector status; EBS volume/default encryption and public snapshots;
and RDS instance/cluster backup, deletion-protection, and public snapshot checks.
They do not modify resources and are not a comprehensive assessment of every
AWS service or control.

## Other services

- **AWS identity:** `GET /api/v1/aws/identity` calls STS
  `GetCallerIdentity` using the standard credential chain.
- **Assessments:** Each successful chat persists its audit report and reviewer
  outputs through SQLAlchemy; read endpoints expose assessment history.
- **Health:** `/health` reports process status. `/ready` reports basic
  database configuration and does not test live AWS or model access.

The chat workflow requires a matching local FAISS index and trusted metadata
file. The configured embedding model must match the one used to create the
index. Retrieval is limited to the Compliance review; it does not initiate
additional AWS checks.

## Provider configuration

Inference defaults to Nebius Token Factory at
`https://api.tokenfactory.nebius.com/v1` using model
`nvidia/Nemotron-3_5-Lightning` and the OpenAI Chat Completions adapter. A
configured `NVIDIA_API_KEY` is required for the Cloud, Compliance, and Senior
LLM calls.
