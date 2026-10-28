# How to integrate a frontend

This guide connects a browser-based frontend to the Indra FastAPI backend. It
covers login, authenticated API requests, displaying the three independent
agent outputs, CORS, and local Docker development.

## 1. Start the backend

Use the native development setup or Docker. See [the project overview](./project-overview.md)
for dependencies and environment variables and [the API reference](./api.md)
for complete request and response contracts.

For browser development, configure `CORS_ORIGINS` on the backend to include
the exact frontend origin, including its scheme and port. For example:

```env
CORS_ORIGINS=http://localhost:5173
```

Restart the backend after changing the setting. Do not use `*` as a production
origin. The backend accepts the `Authorization`, `Content-Type`, and
`X-Request-ID` headers and allows `GET`, `POST`, and `PATCH`.

## 2. Configure the frontend API base URL

Use a frontend environment setting rather than hardcoding deployment-specific
hostnames. For Vite, for example:

```env
VITE_API_BASE_URL=http://localhost:8000
```

The base URL is the backend origin; append `/api/v1` to call versioned
endpoints. Do not put backend secrets, AWS credentials, or the inference API
key in frontend environment variables. Frontend variables are visible to
users.

## 3. Sign in

The login route is public. It accepts the credentials configured on the
backend through `AUTH_USERNAME` and `AUTH_PASSWORD`:

```http
POST /api/v1/auth/login
Content-Type: application/json

{"username":"configured-user","password":"configured-password"}
```

On success, the response contains an HS256 access token valid for 2 hours:

```json
{
  "access_token": "signed-jwt",
  "token_type": "bearer",
  "expires_in": 7200
}
```

Keep the access token in application memory where practical. Avoid
`localStorage` for bearer tokens because JavaScript executing on the origin
can read it. This backend does not currently provide refresh tokens, logout
revocation, user registration, or multiple user accounts. When a token
expires, request a new one through the login route.

## 4. Call protected endpoints

Every `/api/v1` endpoint except `/api/v1/auth/login` requires:

```http
Authorization: Bearer <access_token>
```

`/`, `/health`, `/ready`, and development API documentation are public.

Vite JavaScript example:

```js
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function login(username, password) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) {
    throw new Error(`Login failed (${response.status})`);
  }
  const result = await response.json();
  return result.access_token;
}

async function runAudit(token, message) {
  const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ message, history: [] }),
  });
  if (response.status === 401) {
    throw new Error("Your session expired. Please sign in again.");
  }
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message ?? `Audit request failed (${response.status})`);
  }
  return response.json();
}
```

Production frontends should validate API responses at runtime (for example
with a schema library), handle network errors, and avoid displaying raw error
details as trusted HTML.

## 5. Display agent results separately

The backend returns all three results from the same chat request, in separate
fields. Render them as separate panels or tabs; do not merge the Compliance
or Senior prose into the structured Cloud report.

```js
const result = await runAudit(accessToken, prompt);

renderCloudReport(result.cloud_agent_response);
renderComplianceSummary(result.compliance_agent_response);
renderSeniorReview(result.senior_agent_response);
renderSources(result.sources);
```

The supplied React frontend displays Compliance and Senior responses with its
shared `MarkdownView` component, backed by `react-markdown` and `remark-gfm`.
This handles common Markdown and GFM tables without enabling raw HTML. Keep
the Cloud report as structured data (for example, formatted JSON) rather than
passing it through the Markdown renderer.

- `cloud_agent_response` is the structured AWS audit report, including counts
  and findings.
- `compliance_agent_response` is the Compliance agent's text summary, informed
  by the report and retrieved local guidance.
- `senior_agent_response` is the Senior agent's separate review of the report
  and Compliance summary.
- `sources` contains the retrieved guidance citations. These source records
  are returned by chat but are not stored in assessment history.
- `assessment_id` can be used to retrieve the persisted report and reviews
  from the assessment endpoints.

The workflow is not streamed. The frontend receives these fields together
when the chat request completes. Show a loading state while the request runs
and preserve each field independently in application state.

## 6. Other useful endpoints

Use the same bearer token for:

- `GET /api/v1/assessments` and
  `GET /api/v1/assessments/{assessment_id}` for persisted history.
- `GET /api/v1/rag/status` to show whether local index and metadata files are
  present. This checks file presence only, not retrieval compatibility.
- `POST /api/v1/rag/query` with `{"question":"..."}` for direct attributed
  guidance retrieval.
- `GET /api/v1/aws/identity` for the backend's AWS caller identity.

The RAG query and status endpoints do not invoke the LLM provider or AWS
resource audits. See the [API reference](./api.md) for all parameters,
schemas, and error codes.

## 7. Local Docker connection

Build and run the backend from the repository root:

```bash
docker build -t indra-backend .
docker run --rm --name indra-backend \
  -p 8000:8000 \
  --env-file .env \
  -e APP_ENV=development \
  -e CORS_ORIGINS=http://localhost:5173 \
  -v indra-data:/app/data \
  -v "$PWD/faiss_store:/app/faiss_store:ro" \
  indra-backend
```

The host FAISS index and its trusted metadata file must both exist in
`faiss_store/`. The named database volume preserves SQLite data between
restarts. The bind-mounted retrieval artifacts are read-only to the container.
Configure `DATABASE_URL`, login/JWT values, provider settings, and embedding
model in the backend environment only. Provide AWS access through the
standard Boto3 credential chain or the platform's workload identity; do not
add AWS credentials to frontend configuration.

For deployments, use HTTPS, a narrowly scoped AWS workload identity, a
production frontend origin, and a persistent database. SQLite in a single
container is suitable for development or a single-instance setup, not
concurrent multi-replica deployments.
