# Repository inventory

Discovery completed before new test implementation. Baseline: qa-baseline.json. Existing working-tree edits are user-owned and preserved.

| Boundary | Verified implementation |
|---|---|
| React | frontend/src/main.jsx; App.jsx lazy routes; AuthContext JWT persisted in localStorage with expiry handling; TanStack Query |
| Pages | Login, Dashboard, CloudAudit, Agents, Findings, ReportDetail, Settings |
| HTTP | services/api.js; configurable localStorage backend URL; bearer header; session-expiry event |
| FastAPI | app/main.py; /health, /ready, /; /api/v1/auth/login, chat, assessments, aws/identity, rag/status, rag/query |
| Auth | One environment-configured account, HS256 signed exp/iat/sub JWT; protected versioned routes |
| Orchestration | ChatService → sequential CloudAgent → RagService → ComplianceAgent → SeniorAgent → persistence |
| AWS | Boto3 read-only S3/IAM/EC2/EBS/VPC/RDS/CloudTrail/GuardDuty tools selected from an allowlist |
| Inference | AsyncOpenAI compatible client, bounded timeout, no SDK retries, configurable endpoint; defaults reference Nebius |
| Retrieval | CPU sentence-transformers, FAISS, trusted-local pickle metadata; ranked top-three passages |
| Storage | SQLAlchemy Assessment and Operation; SQLite default, optional PostgreSQL; Alembic migrations |
| Terraform | No generation, validation or execution implementation found; no Terraform test claims |
| Delivery | Backend Dockerfile and Backend CI workflow; no confirmed hosting platform |
| Dependencies | Python pyproject.toml ranges (no lock); frontend npm package-lock.json; existing pytest/Ruff |
| Documentation | Existing design/ and root README/security/setup guides; preserve old diagrams |

## Gaps and risks

No frontend test framework or browser suite initially. Existing backend tests mix units, API integration and AWS Stubber checks. No proven semantic enforcement of senior-agent claims; text reviews are model output. Pickle requires trusted local artifacts. Single-account authentication offers no tenant ownership model; multi-user isolation is unsupported. Readiness reports configuration, not live dependency health. No real cloud audit or paid inference is authorized for QA. Python ranges reduce reproducibility until a lock is captured. No production deployment will run.

## Structure

```text
.dockerignore
.editorconfig
.env.example
.gitattributes
.github/ISSUE_TEMPLATE/bug_report.md
.github/ISSUE_TEMPLATE/feature_request.md
.github/workflows/ci.yml
.gitignore
.pre-commit-config.yaml
.python-version
ATTRIBUTES.md
AWS_SETUP.md
CHANGELOG.md
CODE_OF_CONDUCT.md
CONTRIBUTING.md
Dockerfile
LICENSE
Makefile
README.md
SECURITY.md
SUPPORT.md
alembic.ini
app/__init__.py
app/api/__init__.py
app/api/dependencies.py
app/api/router.py
app/api/routes/__init__.py
app/api/routes/assessments.py
app/api/routes/auth.py
app/api/routes/aws.py
app/api/routes/chat.py
app/api/routes/health.py
app/api/routes/rag.py
app/core/__init__.py
app/core/config.py
app/core/errors.py
app/core/logging.py
app/core/middleware.py
app/core/security.py
app/db/__init__.py
app/db/base.py
app/db/models/__init__.py
app/db/models/assessment.py
app/db/models/operation.py
app/db/session.py
app/main.py
app/repositories/__init__.py
app/repositories/assessment_repository.py
app/schemas/__init__.py
app/schemas/assessment.py
app/schemas/audit_schema.py
app/schemas/auth.py
app/schemas/aws.py
app/schemas/chat.py
app/schemas/common.py
app/schemas/rag.py
app/services/__init__.py
app/services/assessment_service.py
app/services/aws/__init__.py
app/services/aws/aws_service.py
app/services/chat_service.py
app/services/llm/__init__.py
app/services/llm/base.py
app/services/llm/cloud_agent.py
app/services/llm/compliance_agent.py
app/services/llm/role_prompts.py
app/services/llm/roles/cloud_role.md
app/services/llm/roles/compliance_role.md
app/services/llm/roles/senior_role.md
app/services/llm/senior_agent.py
app/services/llm/workflow.py
app/services/llm_service.py
app/services/rag/__init__.py
app/services/rag/embedding.py
app/services/rag/models.py
app/services/rag/retrieval.py
app/services/rag/service.py
app/services/rag/store.py
app/tools/audit/__init__.py
app/tools/audit/aws/__init__.py
app/tools/audit/aws/cloudtrail.py
app/tools/audit/aws/common.py
app/tools/audit/aws/ec2.py
app/tools/audit/aws/guardduty.py
app/tools/audit/aws/iam.py
app/tools/audit/aws/rds.py
app/tools/audit/aws/s3.py
app/tools/audit/aws/vpc.py
app/tools/audit/aws_audit.py
data/.gitkeep
design/HOW_TO.md
design/api.md
design/diagrams/architecture.md
design/diagrams/archive/architecture-legacy.md
design/diagrams/frontend-state-machine.md
design/diagrams/lld.md
design/diagrams/project-overview.md
design/security.md
design/qa/test_case.md
design/qa/testing.md
faiss_store/.gitkeep
faiss_store/security.index
faiss_store/security.pkl
frontend/.env.example
frontend/README.md
frontend/components.json
frontend/eslint.config.js
frontend/index.html
frontend/package-lock.json
frontend/package.json
frontend/postcss.config.js
frontend/src/App.jsx
frontend/src/assets/indraa-mark.svg
frontend/src/assets/three-specialist-agents.svg
frontend/src/components/agents/AgentWorkflow.jsx
frontend/src/components/dashboard/LatestAudits.jsx
frontend/src/components/dashboard/SeverityChart.jsx
frontend/src/components/dashboard/StatCard.jsx
frontend/src/components/findings/FindingsTable.jsx
frontend/src/components/layout/AppLayout.jsx
frontend/src/components/layout/ProtectedRoute.jsx
frontend/src/components/layout/Sidebar.jsx
frontend/src/components/layout/Topbar.jsx
frontend/src/components/reports/MarkdownView.jsx
frontend/src/components/ui/Primitives.jsx
frontend/src/context/AuthContext.jsx
frontend/src/hooks/useApi.js
frontend/src/index.css
frontend/src/lib/utils.js
frontend/src/main.jsx
frontend/src/pages/Agents.jsx
frontend/src/pages/CloudAudit.jsx
frontend/src/pages/Dashboard.jsx
frontend/src/pages/Findings.jsx
frontend/src/pages/Login.jsx
frontend/src/pages/ReportDetail.jsx
frontend/src/pages/Settings.jsx
frontend/src/services/api.js
frontend/tailwind.config.js
frontend/vite.config.js
migrations/env.py
migrations/script.py.mako
migrations/versions/0001_initial_schema.py
migrations/versions/0002_project_owners.py
migrations/versions/0003_remove_database_users.py
migrations/versions/0004_assessments.py
pyproject.toml
reference/senior-review-c73fb872-7357-4c7d-9c9a-45bf3a22c09d.md
requirements.txt
scripts/check_environment.py
tests/conftest.py
tests/test_assessments.py
tests/test_auth.py
tests/test_aws.py
tests/test_aws_audit.py
tests/test_chat_api.py
tests/test_chat_workflow.py
tests/test_cloud_agent.py
tests/test_config.py
tests/test_errors.py
tests/test_health.py
tests/test_llm_service.py
tests/test_rag.py
```
