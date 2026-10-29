# Indra-AI frontend

React 19 + Vite JavaScript SPA for Indra-AI, a cloud security posture assessment product.
The UI calls the existing authenticated FastAPI routes; it does not simulate
findings or agent progress.

## Run locally

```bash
npm install
cp .env.example .env
npm run dev
```

By default Vite serves at `http://localhost:5173` and the API client connects
to `http://localhost:8000`. Configure `VITE_API_BASE_URL` as a backend origin.
Set the backend's `CORS_ORIGINS` to the frontend origin, and configure
`AUTH_USERNAME`, `AUTH_PASSWORD`, `JWT_SECRET_KEY`, the provider, AWS access,
and matching FAISS artifacts on the backend only.

## Available commands

```bash
npm run dev
npm run lint
npm run build
npm run preview
```

## Backend behavior reflected by the UI

- The login form calls `POST /api/v1/auth/login`; authenticated API calls use
  the returned bearer token. The JWT is saved as `indraa.accessToken` in localStorage and restored on refresh until its two-hour expiry. Sign-out, expiry, or an authenticated API 401 clears it. Passwords are never stored.
- The audit form calls `POST /api/v1/chat` and renders its separate Cloud,
  Compliance, and Senior response fields.
- Agent-level progress is not streamed by the API. The UI shows a single
  workflow-running state and only labels agent results received after the
  completed response.
- Service selection is expressed as natural-language audit scope; the backend
  model selects approved tools. AWS region is controlled by backend
  `AWS_REGION` and cannot be changed per request.
- Findings, report history, RAG status/query, AWS identity, backend health,
  and readiness come from their existing backend endpoints.
- Compliance and Senior responses are rendered with `react-markdown` and
  `remark-gfm`, so headings, emphasis, lists, inline code, links, and tables
  appear as formatted content. Raw HTML in model output is not enabled.
- The structured Cloud Agent report remains formatted JSON rather than being
  interpreted as Markdown.

See [the frontend integration guide](../design/HOW_TO.md) for request and
response examples, Markdown rendering, CORS, token handling, and deployment
notes.

## Validate

```bash
npm run lint
npm run build
```

These checks do not contact AWS or the inference provider. A live audit
workflow requires backend authentication, configured AWS read access, a
matching local FAISS store, and a reachable inference provider.

The renderer smoke check passed, but the latest live workflow attempt timed
out at the inference provider before returning agent text. An earlier
successful live S3 workflow predates Markdown rendering; see the
[testing notes](../design/qa/testing.md).
