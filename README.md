# Indra AI Backend

Indra is a FastAPI backend for read-only AWS security audits and AI-assisted
review. It returns a structured Cloud audit report, a separate Compliance
summary informed by local FAISS guidance, and an independent Senior review.
Completed chat assessments are persisted in SQLAlchemy-backed storage.

The [React frontend](frontend/README.md) connects to this API and renders the
Compliance and Senior text responses as Markdown, including GitHub-flavored
tables. The backend response contract remains unchanged.

## Quick start

### Local Python

Requirements: Python 3.12 or newer.

```bash
python -m pip install -e '.[dev]'
cp .env.example .env
```

Set `AUTH_USERNAME`, `AUTH_PASSWORD`, and a unique `JWT_SECRET_KEY` of at
least 32 bytes to enable login. Set `NVIDIA_API_KEY` for chat inference.
Configure AWS credentials through the standard Boto3 credential chain; do not
send AWS credentials to the API. Chat also requires a matching local FAISS
index and trusted metadata pair.

```bash
uvicorn app.main:app --reload
```

The service listens at `http://localhost:8000`. Health is available at
`/health`; development API docs are available at `/docs`.

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

## API at a glance

The versioned API prefix defaults to `/api/v1`. All versioned routes except
login require `Authorization: Bearer <access_token>`. The root, `/health`,
`/ready`, and development documentation remain public.

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/auth/login` | Issue a 30-minute JWT for the configured environment account |
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
[design/](design/):

- [Frontend integration how-to](design/HOW_TO.md)
- [Detailed API reference](design/api.md)
- [Architecture](design/architecture.md)
- [Low-level design and module interactions](design/lld.md)
- [Project overview](design/project-overview.md)
- [Security boundaries](design/security.md)
- [Testing strategy](design/testing.md)
- [Function-level test cases and manual checklist](design/test_case.md)

The old Terraform architecture draft is retained as a clearly marked
[historical document](design/archive/architecture-legacy.md) and does not
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
[testing notes](design/testing.md) for the distinction.

## Security and limitations

- AWS audit operations are read-only and limited to the configured tool
  allowlist; results are point-in-time decision support, not certification.
- JWTs use the single environment-configured account. User management,
  revocation, refresh tokens, and tenant isolation are not implemented.
- Never commit `.env`, provider credentials, AWS credentials, local database
  files, or trusted FAISS metadata.
- Deploy behind HTTPS and use narrowly scoped AWS workload credentials.
