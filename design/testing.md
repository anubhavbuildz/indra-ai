# Testing strategy

This project uses three levels of verification: unit tests for isolated
behavior, integration tests for service/API boundaries, and optional live
checks for explicitly configured AWS, inference, and local retrieval
integrations. Routine tests must not require AWS credentials, inference API
keys, network access, or a downloaded embedding model.

## Run checks

From the `indra-ai/` directory, install the development dependencies and run:

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
ruff format --check .
python -m compileall -q app tests
```

Run one layer or feature at a time:

```bash
pytest tests/test_rag.py -q
pytest tests/test_cloud_agent.py tests/test_llm_service.py -q
pytest tests/test_chat_workflow.py tests/test_assessments.py tests/test_aws.py -q
```

`tests/test_rag.py` uses a small temporary FAISS index and local metadata to
exercise actual vector ranking without loading a neural embedding model. It
also verifies source attribution, mismatched store detection, and the RAG
HTTP routes. Workflow tests inject fake agents and passages so the order and
handoff between Cloud, retrieval, Compliance, and Senior are deterministic.
API tests use FastAPI's test client and the project's SQLite fixtures.

## Unit-test coverage

Unit tests should cover a single function or service boundary at a time:

- **Configuration:** defaults, environment aliases, and configured index paths.
- **FAISS store:** index loading, trusted metadata shape, document-count and
  embedding-dimension mismatches, and missing/corrupt local files.
- **Retrieval:** query embedding inputs, top-k ranking, passage formatting,
  character limits, and citations; mock the embedding model where only search
  behavior is under test.
- **Compliance:** audit findings and retrieved passages are included as
  separate prompt evidence, with instructions to treat both as untrusted.
- **Chat service:** workflow output is persisted and returned with citations.
- **Agents/providers:** validate tool allowlists, provider request shape,
  malformed responses, and safe provider errors using mocks.
- **AWS tools:** mock Boto3 clients and assert that checks are read-only.
- **Schemas:** invalid lengths, history limits, and malformed request bodies.
- **Authentication:** correct and incorrect login credentials, missing,
  malformed, invalid, and expired bearer tokens, public login, and protected
  versioned route access.
- **Chat response contract:** the HTTP response exposes the Cloud audit report,
  Compliance summary, and Senior review in separate response fields.

Unit tests must not call live AWS, a hosted LLM, or download a Hugging Face
model. Keep test data synthetic; never put credentials or real account data
in fixtures.

For a function-by-function behavior/constraint matrix and a test-session
checklist, use [test_case.md](./test_case.md).

## Integration-test coverage

Integration tests should verify that actual application components work
together while replacing external systems at their edges:

- Mount the FastAPI application and verify every route's HTTP status,
  validation behavior, and response schema.
- Verify all versioned routes except login reject missing/invalid bearer
  tokens, while login and health endpoints remain public.
- Use a temporary SQLite database to verify chat assessment persistence and
  assessment list/read behavior.
- Exercise the RAG status/query routes through `TestClient`; use a temporary
  FAISS index and trusted metadata pair.
- Run the chat workflow with stubbed AWS and inference providers while using
  a deterministic local embedding model or controlled retriever.
- Verify RAG store failures return the standard safe 503 error shape and do
  not return filesystem paths or exception internals.
- Verify health and readiness do not trigger AWS, embedding, or LLM calls.

These tests should be repeatable and offline. They must not depend on the
ignored developer `faiss_store/` files or an individual's local credentials.

## Frontend verification

Run the frontend checks from `frontend/`:

```bash
npm run lint
npm run build
```

The shared Markdown view should be smoke-tested with headings, emphasis,
lists, inline code, links, and GFM tables. Verify that raw HTML is not
rendered as trusted markup, that Cloud report JSON stays JSON, and that empty
and loading/error states do not present fabricated agent outputs. The
frontend's API workflow is non-streaming; agent completion must not be
simulated independently of the completed chat response.

## Latest recorded frontend/live check

After adding Markdown rendering, frontend lint, production build, and the
renderer smoke check passed. The most recent live workflow retry completed
backend readiness, login, and AWS identity checks, but the remote inference
provider timed out during chat; that retry produced no agent results. An
earlier real S3-only workflow did complete and produced three findings with
separate Compliance and Senior reviews, but it predates the Markdown renderer.
Therefore that earlier run validates the backend workflow, not live rendering
of real agent output through the updated frontend. Keep these results
distinct; do not report the post-renderer live end-to-end attempt as passed.

## Optional live integration checks

Live checks are manual and may incur AWS or provider costs. Before running:

1. Use a disposable or explicitly authorized AWS account with read-only
   permissions for the requested audit checks.
2. Confirm `NVIDIA_API_KEY`, endpoint, and model are configured for the
   intended provider. Do not print or share environment values.
3. Ensure `FAISS_INDEX_PATH` and `FAISS_METADATA_PATH` point to the matching,
   trusted local artifacts; set `EMBEDDING_MODEL` to the exact index model.
4. Run only a narrow service-specific prompt when validating end-to-end chat.
5. Review the audit report, retrieved citations, Compliance output, Senior
   output, and any persisted assessment.

The following command invokes the real local retriever and prints citations;
the first run may download model files:

```bash
python - <<'PY'
import asyncio

from app.core.config import Settings
from app.services.rag import RagService

async def main():
    passages = await RagService(Settings()).query(
        "How should AWS storage be encrypted?"
    )
    for passage in passages:
        print(passage.title, passage.as_source())

asyncio.run(main())
PY
```

To test the full live chat workflow, call `chat_workflow` with a focused
question and configured AWS/provider credentials. This performs real
AWS read calls and real LLM requests; keep output private if it contains
resource identifiers. Do not add live checks to the default CI suite.

## Failure and safety expectations

- Missing or incompatible local RAG artifacts fail explicitly; do not silently
  return a success-shaped empty result.
- Secrets, submitted credentials, full prompts, and exception internals must
  not appear in logs or API errors.
- Retrieved passages are untrusted evidence. Tests should ensure agent
  instructions distinguish guidance from observed AWS findings.
- AWS checks must remain read-only.
- Live responses are evidence from a particular run, not proof of complete
  compliance or security.
