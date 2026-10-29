# Indra-AI Backend

Indra-AI is a cloud security posture assessment product with a FastAPI backend
for read-only AWS security audits and AI-assisted review. It returns a structured Cloud audit report, a separate Compliance
summary informed by local FAISS guidance, and an independent Senior review.
Completed chat assessments are persisted in SQLAlchemy-backed storage.

The [React frontend](frontend/README.md) connects to this API and renders the
Compliance and Senior text responses as Markdown, including GitHub-flavored
tables. The backend response contract remains unchanged.

## Quick start

### Install the full project

Requirements: Python 3.12 or newer, Node.js 20.19+ (or 22.12+), and npm.
From the project root, run:

```bash
./scripts/install.sh
```

The script creates a local `.venv`, installs the backend and development
dependencies, creates `.env` files from the provided examples without
overwriting existing ones, installs frontend dependencies, and applies
database migrations. Configure `.env` before using authenticated or
inference-backed features. Start each application in a separate terminal:

```bash
.venv/bin/uvicorn app.main:app --reload
```

```bash
cd frontend && npm run dev
```

### Manual Python setup

Requirements: Python 3.12 or newer.

If you plan to use AWS features, complete the [AWS CLI and identity setup](AWS_SETUP.md)
first. Use AWS CLI v2 and an approved non-root identity; never use the AWS
account root user or create root access keys. AWS CLI setup is not required
when the backend uses another supported credential source, such as a workload
identity.

Create and activate a Python virtual environment from the project root before
installing dependencies. The full-project installer above creates `.venv`
automatically; these steps are for manual installation.

On macOS or Linux, use Python 3.12 or newer:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If Python is not installed, install Python 3.12 or newer first. On Debian or
Ubuntu, if creating the environment reports that `venv` or `ensurepip` is
missing, install the matching system package (for example,
`sudo apt install python3.12-venv` for Python 3.12), then retry creation.

Keep the environment active while running the dependency installation and
backend commands below. In each new terminal, activate it again. Run
`deactivate` when you are finished.

```bash
python -m pip install -e '.[dev]'
cp .env.example .env
```

Set `AUTH_USERNAME`, `AUTH_PASSWORD`, and a unique `JWT_SECRET_KEY` of at
least 32 bytes to enable login. Set `NVIDIA_API_KEY` for chat inference.
Configure AWS credentials through the standard Boto3 credential chain; do not
send AWS credentials to the API. Chat also requires a matching local FAISS
index and trusted metadata pair.

The optional AWS identity endpoint only verifies the caller identity. The
audit workflow requires read permissions for the AWS services it inspects;
see [AWS setup](AWS_SETUP.md) and the [security notes](design/security.md).

```bash
uvicorn app.main:app --reload
```

The service listens at `http://localhost:8000`. Health is available at
`/health`; development API docs are available at `/docs`.

### Docker Compose: frontend and backend

> **Docker Deployment — Under Development**
>
> The Docker-based deployment version of Indraa is currently under active development and testing. Docker deployment is not yet considered production-ready. The standard installation and deployment method remains available and operational. Docker support will be finalized after testing and validation.

`compose.yml` builds both services and serves the frontend at
`http://localhost:8080`. The frontend proxies API traffic to the backend.
AWS credentials are mounted read-only from your host AWS directory into the
backend; the frontend image contains no credentials.

Follow [AWS profile and Compose setup](AWS_SETUP.md#5-aws-credentials-with-docker-compose)
for host login, UID/GID permissions, persistent directories and startup commands.
The regular app can perform real AWS reads and paid inference when you submit
an audit; `compose.qa.yml` remains the separate synthetic test environment.

### Docker

Build and run from the project root:

```bash
docker build -t indra-backend .
docker run --rm --name indra-backend \
  -p 8000:8000 \
  --env-file .env \
  -e APP_ENV=development \
  -v indra-data:/app/data \
  -v "$PWD/faiss_store:/app/faiss_store:ro" \
  indra-backend
```

Create `.env` from `.env.example` and configure the required secrets first.
The host `faiss_store/` directory must contain the matching index and metadata
files for RAG. The named `indra-data` volume preserves the SQLite database.
See the [frontend integration how-to](design/HOW_TO.md) for the frontend CORS,
login, bearer-token, and response-handling walkthrough.

### React frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Set `VITE_API_BASE_URL` to the backend origin when it is not
`http://localhost:8000`, and allow the frontend's exact origin in backend
`CORS_ORIGINS`. Backend credentials and provider secrets must never be placed
in Vite environment variables.

Assessment timestamps are stored in UTC and shown in India Standard Time
(IST, Asia/Kolkata, UTC+05:30) in the frontend.

## API at a glance

The versioned API prefix defaults to `/api/v1`. All versioned routes except
login require `Authorization: Bearer <access_token>`. The root, `/health`,
`/ready`, and development documentation remain public.

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/auth/login` | Issue a 2-hour JWT for the configured environment account |
| `POST` | `/api/v1/chat` | Run AWS audit, RAG, Compliance, and Senior review |
| `GET` | `/api/v1/assessments` | List persisted assessments |
| `GET` | `/api/v1/assessments/{assessment_id}` | Retrieve a saved assessment |
| `GET` | `/api/v1/rag/status` | Check configured RAG artifact presence |
| `POST` | `/api/v1/rag/query` | Query local guidance and return citations |
| `GET` | `/api/v1/aws/identity` | Read AWS caller identity through STS |
| `GET` | `/health` | Process health |
| `GET` | `/ready` | Basic database configuration status |

`POST /api/v1/chat` returns three distinct results:

- `cloud_agent_response`: structured audit report.
- `compliance_agent_response`: Compliance summary text, displayed as Markdown
  by the frontend.
- `senior_agent_response`: Senior review text, displayed as Markdown by the
  frontend.

It also returns retrieved `sources`, an `assessment_id`, and `status`.
Markdown rendering is a frontend presentation concern; these API fields stay
plain strings and are also stored as text in assessment history.

## Documentation

Implementation, API, deployment, and testing references are collected in
[design/](design):

- [Frontend integration how-to](design/HOW_TO.md)
- [Detailed API reference](design/api.md)
- [Architecture](design/diagrams/architecture.md)
- [Low-level design and module interactions](design/diagrams/lld.md)
- [Project overview](design/diagrams/project-overview.md)
- [Security boundaries](design/security.md)
- [Testing strategy](design/qa/testing.md)
- [Function-level test cases and manual checklist](design/qa/test_case.md)

The old Terraform architecture draft is retained as a clearly marked
[historical document](design/diagrams/archive/architecture-legacy.md) and does not
describe the current service.

## Development checks

```bash
pytest
ruff check .
ruff format --check .
python -m compileall -q app tests
```

Routine tests mock AWS and inference calls. Live integration checks require
explicitly configured credentials and may incur costs.

The frontend also has independent lint and production-build checks:

```bash
cd frontend
npm run lint
npm run build
```

The Markdown renderer uses React Markdown with the GFM plugin. Its smoke check
covers headings, emphasis, lists, inline code, and tables; live workflow
testing additionally depends on AWS and inference availability.
The most recent live workflow retry timed out at the remote inference provider,
so real agent output has not been revalidated through the renderer. An earlier
live S3 workflow succeeded before the Markdown integration. See the
[testing notes](design/qa/testing.md) for the distinction.

## Security and limitations

- AWS audit operations are read-only and limited to the configured tool
  allowlist; results are point-in-time decision support, not certification.
- JWTs use the single environment-configured account. User management,
  revocation, refresh tokens, and tenant isolation are not implemented.
- Never commit `.env`, provider credentials, AWS credentials, local database
  files, or trusted FAISS metadata.
- Deploy behind HTTPS and use narrowly scoped AWS workload credentials.

## Hackathon MVP and production roadmap

**Hackathon MVP**

- Working standard installation and deployment using the Quick start instructions.
- IAM user authentication using authorized credentials; see [IAM user setup](AWS_SETUP.md#iam-user-authentication-for-the-hackathon-mvp).
- AWS security posture assessment using read-only permissions.
- AWS STS AssumeRole support through Boto3's standard credential chain and configured role profiles; there is no dedicated application-level AssumeRole onboarding flow. See [AssumeRole prerequisites](AWS_SETUP.md#sts-assumerole-prerequisites-and-credential-flow).
- Docker deployment currently under development.

**Production Roadmap** (planned, not completed)

- Terraform-based AWS onboarding.
- Least-privilege IAM audit roles and policies tailored to assessment checks.
- Cross-account AssumeRole authentication with a managed onboarding flow.
- Temporary credential management beyond the existing SDK credential chain.
- Fully tested Docker deployment and containerized distribution.
