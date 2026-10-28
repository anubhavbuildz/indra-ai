# INDRAA AI testing and installation manual

This guide uses the existing repository layout. Test inventory: [traceability matrix](test-traceability-matrix.md). Architectural sources and previews: [diagrams](../diagrams/README.md). Evidence is written to `design/qa/evidence/`. Fixtures are synthetic and do not certify AWS security or compliance.

## 1. Prerequisites

| Tool | Supported/tested configuration |
|---|---|
| Git | Git 2.x |
| Python | Application >=3.12; pinned QA lock and QA Dockerfile use 3.13 |
| pip | 26.2.2 in captured QA lock |
| Node | 22.x recommended for QA/CI; local execution used 20.19.2 |
| npm | 10.x recommended; local host 9.2.0 required npm 10 for one dependency update |
| Docker | Engine/Desktop with Compose v2 plugin; unavailable on execution host |
| Lynx | Distribution-supported release; optional HTTP inspection |
| Playwright | npm-locked @playwright/test 1.56.1 with matching Chromium |
| Terraform | Not required: no implemented Terraform generation/execution path |

Python dependency lock is a captured Linux/amd64 environment, including the installed ML stack and its GPU runtime packages. Installation is large. Cross-platform dependency resolution and Docker builds have not been validated; do not represent the lock as a portable application release lock. The application requests CPU embeddings. The original production Dockerfile remains on Python 3.12 and retains its existing dependency installation.

## 2. Docker installation

Docker Engine runs containers. Docker Desktop bundles the engine, GUI and Compose tooling for desktop systems. Compose v2 is the `docker compose` plugin, rather than the older standalone `docker-compose` command.

For Ubuntu, follow Docker's [official Engine installation guide](https://docs.docker.com/engine/install/ubuntu/). Configure its signed apt repository, then install:

```bash
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```

The official guide contains repository setup commands and supported Ubuntu versions; review conflicting packages before installation. These instructions are for Ubuntu, not the Debian host used for this execution.

For macOS, download the matching Apple silicon or Intel Docker Desktop installer from [Docker's official Mac guide](https://docs.docker.com/desktop/setup/install/mac-install/), open the DMG, drag Docker to Applications and start it. Wait until the engine is running.

For Windows, use [Docker's official Windows guide](https://docs.docker.com/desktop/setup/install/windows-install/) to install Docker Desktop with WSL 2. Enable WSL integration for the Linux distribution used for this repository. Run the Linux commands in that WSL distribution.

Verify on each platform:

```bash
docker --version
docker compose version
docker run --rm hello-world
```

## 3. Lynx installation and HTTP inspection

Ubuntu / Debian:

```bash
sudo apt update
sudo apt install -y lynx
lynx --version
```

macOS with Homebrew:

```bash
brew install lynx
lynx --version
```

Windows: use Ubuntu through WSL and the Ubuntu commands above. With QA services running:

```bash
lynx http://127.0.0.1:8000/health
lynx -dump http://127.0.0.1:8000/ready
lynx http://127.0.0.1:5173
```

Lynx can inspect HTTP/text and the frontend HTML shell. It does not run modern React JavaScript and cannot replace Playwright. Lynx was not installed or executed in the recorded run.

## 4. Clone and local setup

```bash
git clone https://github.com/anubhavbuildz/indra-ai.git
cd indra-ai
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-qa.lock
.venv/bin/python -m pip install --no-deps -e .
npm ci --prefix frontend
.venv/bin/python -m pip check
```

On Windows use WSL for these commands. Keep `.env` private. `.env.example` and `frontend/.env.example` describe application configuration, but no real AWS/inference credentials are needed for QA. Do not copy production credentials into the testing environment.

`tests/qa_plugin.py` overrides host login/provider secrets and invalid host DEBUG values before importing the app. It selects a temporary SQLite database and blocks outbound sockets. Existing tests supply test-only credentials through fixtures. Always use the provided runner or `-c pytest-qa.ini -p tests.qa_plugin`.

For an interactive deterministic QA workspace, start these in separate terminals:

```bash
.venv/bin/python -m uvicorn scripts.qa_server:app --host 127.0.0.1 --port 8000
npm --prefix frontend run dev -- --host 127.0.0.1
```

Visit `http://127.0.0.1:5173`; use `test-user` / `test-password`. If necessary set the browser-local API origin in Settings to `http://127.0.0.1:8000`. The explicit QA entry point replaces AWS audit, model completion and retrieval boundaries; real HTTP routing, authorization, orchestration order, migrations and persistence still execute. It never modifies runtime production entry points. It blocks outbound external sockets and creates a new temporary database per process. Stop services with Ctrl-C. Never deploy `scripts.qa_server:app`.

## 5. Unit tests — first

```bash
.venv/bin/python scripts/qa.py unit
npm --prefix frontend run test:coverage
```

Backend coverage is preliminary at unit stage; its line gate runs after integration and security. Vitest enforces 80% line coverage across source files, including unimported modules. Test files and the test setup module are excluded. Branches are measured and reported, without pretending the 90% preferred security target is met.

Individual module examples:

```bash
.venv/bin/python -m pytest -c pytest-qa.ini -p tests.qa_plugin tests/test_qa_unit.py -v
npm --prefix frontend run test -- src/api.test.js
```

## 6. Integration tests — second

```bash
.venv/bin/python scripts/qa.py integration
```

Run after unit tests to append coverage. AWS tests use Boto3 Stubber and dummy credentials. SQLite tests use in-memory/temporary databases. Chat persistence replaces the workflow boundary with controlled data. Existing orchestration coverage asserts Cloud → retrieval → Compliance → Senior order. No paid model calls or AWS resources are required.

Stubber fixtures assert expected operations/parameters. They are API simulations, never actual AWS account evidence. IAM checks cover root access keys, not a nonexistent comprehensive IAM policy analyzer.

## 7. Browser E2E — third

```bash
cd frontend
npx playwright install --with-deps chromium
npm run test:e2e
npx playwright show-report ../design/qa/evidence/playwright-html
cd ..
```

Playwright starts fresh backend/frontend services and refuses to reuse unknown running servers. Dedicated browser-test ports 18000 and 15173 must be available. Interactive development services on 8000/5173 are left alone. Nine executions cover three scenarios at desktop, tablet and mobile sizes. Tests use state-based waits and actual local HTTP requests. On failure, screenshots/traces are under `design/qa/evidence/playwright-results/`; JUnit is `e2e.xml`. Inspect a trace with `npx playwright show-trace PATH_TO_TRACE.zip` from `frontend/`.

To use already isolated services (including Compose), set `QA_EXTERNAL_SERVERS=1`, `QA_FRONTEND_URL` and `QA_BACKEND_URL`. These must resolve from the browser process. `QA_PYTHON` overrides the backend Python executable for local managed-service startup. Do not point tests at production endpoints. Browser results establish fixture-backed behavior, not model semantics or real AWS correctness.

## 8. Docker QA

The original Dockerfile is unchanged. `Dockerfile.qa` has independent build-context exclusions so test files are included while `.env`, caches and local data are excluded. No production credentials or host cloud directories are mounted.

```bash
mkdir -p design/qa/evidence
# Give the test-only non-root containers access to this generated artifact directory.
chmod -R a+rwX design/qa/evidence
docker compose -f compose.qa.yml config --quiet
docker compose -f compose.qa.yml build backend frontend
docker compose -f compose.qa.yml up -d --wait backend frontend
docker compose -f compose.qa.yml logs --no-color backend frontend
curl --fail http://127.0.0.1:8000/health
curl --fail http://127.0.0.1:5173
```

Execute each test level in order:

```bash
docker compose -f compose.qa.yml run --rm backend python scripts/qa.py unit
docker compose -f compose.qa.yml run --rm frontend npm run test:coverage
docker compose -f compose.qa.yml run --rm backend python scripts/qa.py integration
docker compose -f compose.qa.yml --profile browser run --build --rm e2e
```

Unit coverage is stored inside each ephemeral backend container; for combined coverage run unit then integration within one container:

```bash
docker compose -f compose.qa.yml run --rm backend sh -c 'python scripts/qa.py unit && python scripts/qa.py integration && python scripts/qa.py security && python scripts/qa.py gate'
```

Collect mounted reports in `design/qa/evidence`. Inspect and safely stop only the QA project:

```bash
docker compose -f compose.qa.yml ps
docker compose -f compose.qa.yml down --remove-orphans
```

No volume deletion or production cleanup commands are needed. Docker build/startup/test/cleanup verification is blocked locally because Docker is absent. These commands are provided for reproduction, not claimed as executed successfully.

## 9. Security and performance

```bash
.venv/bin/python scripts/qa.py security
.venv/bin/python scripts/qa.py performance
.venv/bin/python scripts/install_qa_tools.py
.venv/bin/python scripts/qa_security.py
.venv/bin/ruff check app tests scripts
.venv/bin/ruff format --check app tests scripts
npm --prefix frontend run lint
npm --prefix frontend run build
```

The installer supports Linux/amd64 and checks published SHA256 checksums before extracting pinned CLIs into `/tmp/indra-qa-bin`. It requires release-host access. macOS/Windows users can run this step under a Linux/amd64 development environment or install matching native CLI releases and adapt paths.

Individual scanners:

```bash
.venv/bin/bandit -r app -f json -o design/qa/evidence/bandit.json
.venv/bin/pip-audit --format json --output design/qa/evidence/pip-audit.json
npm --prefix frontend audit --json
/tmp/indra-qa-bin/gitleaks git --config .gitleaks.toml --redact
/tmp/indra-qa-bin/trivy fs --scanners vuln,misconfig --severity HIGH,CRITICAL --skip-dirs .venv --skip-dirs frontend/node_modules --skip-dirs design/qa/evidence .
```

Policy: test failures, Bandit HIGH findings, known Python dependency vulnerabilities, npm HIGH/CRITICAL advisories, unallowlisted secret findings, and Trivy HIGH/CRITICAL filesystem/configuration findings fail the configured gate. Medium/low Bandit warnings remain visible in the full report. Gitleaks exceptions are limited to the exact public test JWT fixture and the stable `s3.default_encryption` check identifier, which generated a false positive in assertion documentation; no entire source folder is exempted. Scanner outages fail the gate as environmental blockers, rather than passing silently. No claim of formal compliance follows from scanner success.

Checkov is N/A for Terraform because there is no Terraform source. Container-image vulnerability scanning remains unexecuted until an image can be built; `trivy fs` is not an image scan. Once Docker is available:

```bash
docker build -t indraa-backend:qa .
/tmp/indra-qa-bin/trivy image --severity HIGH,CRITICAL --exit-code 1 indraa-backend:qa
```

Performance conditions were defined in PERFORMANCE-001 before execution: 100 in-process `/health` requests, eight threads, p95 <500 ms and elapsed <10 seconds. `performance.json` records measured values. No load reaches AWS/inference. FAISS throughput, model latency, browser performance and memory baselines are not established by this check.

## 10. Coverage and diagrams

```bash
.venv/bin/python scripts/qa.py gate
.venv/bin/python scripts/qa_reports.py
.venv/bin/python scripts/qa_verify.py
```

Backend artifacts: `backend-coverage.json`, `backend-coverage.xml` (Cobertura), `backend-html/index.html`. Frontend: `frontend-coverage/index.html`, `coverage-summary.json`, `coverage-final.json`, `lcov.info`, and `cobertura-coverage.xml`. Markdown is generated into `design/qa/CODE_COVERAGE.md`; consolidated results into `design/qa/FINAL_TEST_REPORT.md`. Run stages in order before generating reports; unavailable evidence is shown as N/A rather than fabricated. The backend gate calculates executable line coverage explicitly; coverage.py's combined line+branch percentage is a different metric.

Render Mermaid sources (all diagram outputs stay in design/diagrams):

```bash
PUPPETEER_SKIP_DOWNLOAD=1 npm install --prefix /tmp/indra-mermaid --save-exact @mermaid-js/mermaid-cli@11.12.0
.venv/bin/python scripts/qa_diagrams.py
```

Install Chromium first. `CHROMIUM_PATH` and `MERMAID_CLI` override browser and renderer paths. The renderer uses `--no-sandbox` for this isolated local tooling process; do not use it to browse arbitrary sites.

## 11. CI/CD

Existing `.github/workflows/ci.yml` is preserved. `qa.yml` triggers on PRs, pushes to main/master/develop, and manual runs. It installs locked QA dependencies, lints, runs unit → integration → Docker builds → E2E → security/performance → coverage/report gates. Permissions are read-only; no AWS credentials or inference secrets are supplied. Checkout/setup/upload actions use immutable commit references. Test evidence uploads even if an earlier step fails and expires after 14 days.

Validate locally:

```bash
/tmp/indra-qa-bin/actionlint
```

Local actionlint success does not prove a GitHub-hosted workflow passed. CI builds QA images but its browser suite runs directly on the runner; Compose runtime checks still need execution on a Docker-capable host. The manually triggered `delivery-review.yml` only produces a commit and source checksum manifest; it performs no deployment. Configure required reviewers and branch restrictions on the `production-review` GitHub environment before delivery use. Hosting, image registry, artifact-signing and post-deploy endpoint details are unknown.

Before implementing actual CD, select a target, verify approved build checksums and QA evidence, use short-lived OIDC credentials with scoped permissions, and define a deployment-specific health check. Rollback must restore the previous approved immutable artifact and configuration; database migration rollback needs a tested backup/restore plan. None of those operations runs from the current template.

## 12. Troubleshooting

| Symptom | Diagnosis / correction |
|---|---|
| Python install fails | Use Python 3.13 for captured lock; verify Linux wheel support, network and disk. ML dependencies are large. Run pip check. |
| Node install fails | Use Node 22 and npm 10; npm ci from committed lock. The local npm 9 edgesOut failure was resolved using npm 10, without changing package manager. |
| Invalid DEBUG / credential bleed | Use scripts/qa.py; plugin overrides host values before import. Do not run production services with test credentials. |
| Docker daemon unavailable | Start Docker Desktop or Linux docker service; verify docker info; do not report builds as passed. |
| Container networking | Use service DNS from containers and localhost from host. Compose's browser uses frontend:5173/backend:8000. Confirm allowed Vite host and backend CORS origin. |
| Ports in use | Stop your earlier QA servers with Ctrl-C or change both service/test URLs. Playwright intentionally refuses server reuse and defaults to dedicated ports 18000/15173. |
| Chromium missing libraries | Run npx playwright install --with-deps chromium; Linux package installation may require administrator permission. |
| FAISS fixtures fail | Use paired temporary index/metadata and stub embedding model; clear caches after changing paths. Do not download an embedding model in unit tests. |
| AWS credential resolution | Use test adapter or dummy Stubber credentials; no AWS_PROFILE is required. Metadata is disabled. Do not troubleshoot by injecting production keys. |
| Provider timeout | Reproduce using mocked OpenAI exceptions. Do not increase real paid inference timeouts for CI. |
| CI-only errors | Download qa-evidence; compare Python/Node and lock versions, actionlint output, service startup logs, traces, and gate exit codes. |
| Coverage changed after tool upgrade | Check instrumentation version. Vitest 4 uses different executable-line accounting; use the latest generated JSON, not old percentages. |

Reports list unexecuted semantic compliance review, tenant isolation, Docker runtime/image checks and non-health performance work separately from passing automated tests.
