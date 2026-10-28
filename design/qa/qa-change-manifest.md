# QA change manifest

No existing files moved, renamed or deleted. All 163 baseline tracked paths remain.

## Existing files modified by QA

| File | Explanation |
|---|---|
| `frontend/package.json` | Added npm test scripts and dev-only test dependencies. |
| `frontend/package-lock.json` | Locked Vitest, Testing Library, jsdom and Playwright dependencies; removed vulnerable initial test versions. |
| `pyproject.toml` | Added async/security QA dependencies, upgraded pytest development range, enabled measured branch coverage. The explicit runner enforces 80% executable line coverage. |
| `tests/test_config.py` | Isolated default-setting assertion from the test database environment variable; Ruff formatting. |
| `tests/test_llm_service.py` | Aligned token-limit expectation with the pre-existing 8192-token user change. |

## Added source, configuration and documentation

- `.github/workflows/delivery-review.yml`
- `.github/workflows/qa.yml`
- `.gitleaks.toml`
- `Dockerfile.qa`
- `Dockerfile.qa.dockerignore`
- `compose.qa.yml`
- `design/qa/CODE_COVERAGE.md`
- `design/qa/FINAL_TEST_REPORT.md`
- `design/qa/HOW_TO_TEST.md`
- `design/qa/e2e-test-cases.md`
- `design/qa/integration-test-cases.md`
- `design/qa/performance-test-cases.md`
- `design/qa/qa-baseline.json`
- `design/qa/qa-cases.json`
- `design/qa/qa-change-manifest.json`
- `design/qa/qa-change-manifest.md`
- `design/qa/repository-inventory.md`
- `design/qa/security-test-cases.md`
- `design/qa/test-traceability-matrix.md`
- `design/qa/unit-test-cases.md`
- `frontend/e2e/workspace.spec.js`
- `frontend/playwright.config.js`
- `frontend/src/api.test.js`
- `frontend/src/pages.test.jsx`
- `frontend/src/qa-setup.js`
- `frontend/src/qa.test.jsx`
- `frontend/src/utils.test.js`
- `frontend/vitest.config.js`
- `pytest-qa.ini`
- `requirements-qa.lock`
- `design/diagrams/README.md`
- `design/diagrams/aws-audit-sequence.mmd`
- `design/diagrams/aws-audit-sequence.svg`
- `design/diagrams/ci-cd-pipeline.mmd`
- `design/diagrams/ci-cd-pipeline.svg`
- `design/diagrams/data-model.mmd`
- `design/diagrams/data-model.svg`
- `design/diagrams/deployment-architecture.mmd`
- `design/diagrams/deployment-architecture.svg`
- `design/diagrams/frontend-data-flow.mmd`
- `design/diagrams/frontend-data-flow.svg`
- `design/diagrams/frontend-state-machine.mmd`
- `design/diagrams/frontend-state-machine.svg`
- `design/diagrams/multi-agent-workflow.mmd`
- `design/diagrams/multi-agent-workflow.svg`
- `design/diagrams/system-architecture.mmd`
- `design/diagrams/system-architecture.svg`
- `design/diagrams/system-data-flow.mmd`
- `design/diagrams/system-data-flow.svg`
- `scripts/install_qa_tools.py`
- `scripts/qa.py`
- `scripts/qa_diagrams.py`
- `scripts/qa_reports.py`
- `scripts/qa_security.py`
- `scripts/qa_server.py`
- `scripts/qa_verify.py`
- `tests/qa_plugin.py`
- `tests/test_qa_integration.py`
- `tests/test_qa_performance.py`
- `tests/test_qa_security.py`
- `tests/test_qa_unit.py`

## Existing user edits preserved

- `README.md`
- `app/core/config.py`
- `app/schemas/assessment.py`
- `app/services/llm/base.py`
- `design/diagrams/frontend-state-machine.md`
- `frontend/src/App.jsx`
- `frontend/src/components/agents/AgentWorkflow.jsx`
- `frontend/src/components/dashboard/LatestAudits.jsx`
- `frontend/src/index.css`
- `frontend/src/lib/utils.js`
- `frontend/src/pages/CloudAudit.jsx`
- `frontend/src/services/api.js`
- `tests/test_assessments.py`

Pre-existing untracked scripts/install.sh was preserved. A concurrent frontend API default-origin edit was observed and later reverted externally; QA did not edit that application file.

Generated evidence files: 122. Full names are listed in qa-change-manifest.json. No application source was changed by QA.

## Documentation consolidation

The original path inventory above is historical. QA documentation and evidence now live in `design/qa/`; architecture documents and Mermaid/SVG files live in `design/diagrams/`. See `relocations.json` for all approved source-to-destination mappings. The emptied `resin/` directory was removed.
