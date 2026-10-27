# Indraa frontend

React 19 + Vite JavaScript SPA for the Indraa AWS security review backend.
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
  the returned bearer token. The token stays in application memory.
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

See [the frontend integration guide](../design/HOW_TO.md) for request and
response examples, CORS, token handling, and deployment notes.
