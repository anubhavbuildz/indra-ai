# Verified design index

Architecture documentation, Mermaid sources and SVG previews are consolidated here.

- [system-architecture source](system-architecture.mmd) · [SVG preview](system-architecture.svg)
- [frontend-state-machine source](frontend-state-machine.mmd) · [SVG preview](frontend-state-machine.svg)
- [frontend-data-flow source](frontend-data-flow.mmd) · [SVG preview](frontend-data-flow.svg)
- [system-data-flow source](system-data-flow.mmd) · [SVG preview](system-data-flow.svg)
- [multi-agent-workflow source](multi-agent-workflow.mmd) · [SVG preview](multi-agent-workflow.svg)
- [aws-audit-sequence source](aws-audit-sequence.mmd) · [SVG preview](aws-audit-sequence.svg)
- [ci-cd-pipeline source](ci-cd-pipeline.mmd) · [SVG preview](ci-cd-pipeline.svg)
- [deployment-architecture source](deployment-architecture.mmd) · [SVG preview](deployment-architecture.svg)
- [data-model source](data-model.mmd) · [SVG preview](data-model.svg)

## Source correspondence and limits

System architecture/data flow: app/main.py, api/router.py, services/chat_service.py, llm/workflow.py, rag/*.py, frontend/src/services/api.js. Frontend states: App.jsx, AuthContext.jsx, CloudAudit.jsx, hooks/useApi.js. AWS sequence: CloudAgent.run_audit and AWSAuditor mixins. Data model: app/db/models/assessment.py and operation.py; migrations 0001–0004. Operation is persisted schema without an exposed operation execution API. CI: qa.yml and delivery-review.yml; original ci.yml retained. Deployment: original Dockerfile and Vite configuration; QA compose is added but not runtime-verified locally.

No Terraform generation/execution module is implemented. No tenant model or externally hosted production environment is inferred. Model responses remain untrusted; senior review is prompt-guided. Framework content is retrieved from local metadata rather than a newly invented document service. Historical assessment storage omits live RAG citations. QA external boundaries are fixtures, not real audit evidence. The production container uses Python 3.12; the separately pinned QA environment uses Python 3.13.

Validation results are in ../qa/evidence/diagram-validation.json. Render using the commands in ../qa/HOW_TO_TEST.md.

## Existing architecture documents

- [Architecture](architecture.md)
- [Frontend state machine](frontend-state-machine.md)
- [Low-level design](lld.md)
- [Project overview](project-overview.md)
- [Archived architecture draft](archive/architecture-legacy.md)
