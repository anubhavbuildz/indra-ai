# Code coverage

Generated: 2026-10-28T19:31:57.928859+05:30

Commit: `41ede85b75df79a7423448468d0d6abec551b2f8` (working tree includes uncommitted QA changes).

| Module | Line coverage | Branch coverage | Target | Result |
|---|---:|---:|---|---|
| Backend | 80.74% | 59.50% | 80% | Met |
| Agent orchestration | 100.00% | N/A | 90% preferred | Met |
| AWS auditing | 72.34% | 61.29% | 90% preferred | Below target |
| Compliance processing | 79.15% | 52.63% | 90% preferred | Below target |
| Frontend | 87.91% | 78.2% | 80% | Met |

Terraform processing is N/A: no implementation exists. Backend line coverage is executable lines, distinct from coverage.py's combined branch+line percentage.

## Backend modules and gaps

| Module | Lines | Branches | Uncovered lines | Uncovered branches |
|---|---:|---:|---|---|
| `app/__init__.py` | N/A | N/A | None | None |
| `app/api/__init__.py` | N/A | N/A | None | None |
| `app/api/dependencies.py` | 100.00% | 100.00% | None | None |
| `app/api/router.py` | 100.00% | N/A | None | None |
| `app/api/routes/__init__.py` | N/A | N/A | None | None |
| `app/api/routes/assessments.py` | 100.00% | N/A | None | None |
| `app/api/routes/auth.py` | 100.00% | N/A | None | None |
| `app/api/routes/aws.py` | 88.89% | N/A | 16 | None |
| `app/api/routes/chat.py` | 100.00% | N/A | None | None |
| `app/api/routes/health.py` | 90.00% | N/A | 21 | None |
| `app/api/routes/rag.py` | 100.00% | N/A | None | None |
| `app/core/__init__.py` | N/A | N/A | None | None |
| `app/core/config.py` | 100.00% | 100.00% | None | None |
| `app/core/errors.py` | 87.50% | N/A | 57, 59, 60 | None |
| `app/core/logging.py` | 100.00% | N/A | None | None |
| `app/core/middleware.py` | 96.15% | 78.57% | 35, 64 | [[34, 35], [56, 32], [63, 64]] |
| `app/core/security.py` | 92.68% | 75.00% | 32, 53, 75 | [[26, 32], [52, 53], [74, 75]] |
| `app/db/__init__.py` | N/A | N/A | None | None |
| `app/db/base.py` | 100.00% | N/A | None | None |
| `app/db/models/__init__.py` | 100.00% | N/A | None | None |
| `app/db/models/assessment.py` | 100.00% | N/A | None | None |
| `app/db/models/operation.py` | 100.00% | N/A | None | None |
| `app/db/session.py` | 97.44% | 50.00% | 30 | [[22, 30], [24, 26], [51, 55], [53, 55]] |
| `app/main.py` | 96.15% | 50.00% | 57 | [[44, 54]] |
| `app/repositories/__init__.py` | N/A | N/A | None | None |
| `app/repositories/assessment_repository.py` | 100.00% | N/A | None | None |
| `app/schemas/__init__.py` | N/A | N/A | None | None |
| `app/schemas/assessment.py` | 100.00% | N/A | None | None |
| `app/schemas/audit_schema.py` | 100.00% | N/A | None | None |
| `app/schemas/auth.py` | 100.00% | N/A | None | None |
| `app/schemas/aws.py` | 100.00% | N/A | None | None |
| `app/schemas/chat.py` | 100.00% | N/A | None | None |
| `app/schemas/common.py` | 0.00% | N/A | 3, 6, 7, 8, 9, 12, 13 | None |
| `app/schemas/rag.py` | 100.00% | N/A | None | None |
| `app/services/__init__.py` | N/A | N/A | None | None |
| `app/services/assessment_service.py` | 100.00% | 100.00% | None | None |
| `app/services/aws/__init__.py` | N/A | N/A | None | None |
| `app/services/aws/aws_service.py` | 66.67% | 0.00% | 28, 29, 30, 31, 38, 39, 40 | [[30, 31], [30, 38]] |
| `app/services/chat_service.py` | 100.00% | N/A | None | None |
| `app/services/llm/__init__.py` | 100.00% | N/A | None | None |
| `app/services/llm/base.py` | 53.38% | 50.00% | 60, 68, 99, 132, 133, 139, 140, 141, 158, 159, 167, 168, 169, 170, 173, 174, 177, 178, 181, 182, 183, 187, 188, 189, 190, 193, 194, 197, 198, 199, 202, 203, 204, 205, 208, 209, 212, 227, 228, 229, 230, 231, 249, 250, 251, 252, 255, 256, 261, 262, 265, 266, 267, 273, 274, 278, 283, 290, 291, 292, 296, 299 | [[59, 60], [98, 99], [193, 194], [193, 197], [198, 199], [198, 202], [208, 209], [208, 212], [224, 226], [226, 227], [229, 230], [229, 231], [277, 278], [282, 283], [290, -288], [290, 291]] |
| `app/services/llm/cloud_agent.py` | 94.12% | 100.00% | 179, 208, 209 | None |
| `app/services/llm/compliance_agent.py` | 100.00% | N/A | None | None |
| `app/services/llm/role_prompts.py` | 47.62% | 25.00% | 20, 21, 22, 23, 24, 25, 27, 31, 32, 33, 34 | [[17, 20], [32, 33], [32, 34]] |
| `app/services/llm/senior_agent.py` | 72.73% | N/A | 20, 31, 43 | None |
| `app/services/llm/workflow.py` | 100.00% | N/A | None | None |
| `app/services/llm_service.py` | 100.00% | N/A | None | None |
| `app/services/rag/__init__.py` | 100.00% | N/A | None | None |
| `app/services/rag/embedding.py` | 54.55% | N/A | 17, 18, 20, 21, 22 | None |
| `app/services/rag/models.py` | 83.33% | 25.00% | 24, 25, 26, 27 | [[18, 20], [25, 26], [25, 27]] |
| `app/services/rag/retrieval.py` | 73.40% | 53.33% | 57, 58, 59, 67, 75, 76, 77, 86, 88, 121, 125, 141, 142, 143, 144, 145, 146, 154, 155, 156, 158, 159, 168, 170, 175 | [[66, 67], [85, 86], [87, 88], [120, 121], [124, 125], [138, 141], [143, 144], [143, 158], [144, 145], [144, 146], [155, 143], [155, 156], [167, 168], [169, 170]] |
| `app/services/rag/service.py` | 100.00% | N/A | None | None |
| `app/services/rag/store.py` | 80.56% | 75.00% | 46, 54, 55, 56, 66, 75, 76 | [[45, 46]] |
| `app/tools/audit/__init__.py` | N/A | N/A | None | None |
| `app/tools/audit/aws/__init__.py` | N/A | N/A | None | None |
| `app/tools/audit/aws/cloudtrail.py` | 64.06% | 58.33% | 36, 37, 53, 54, 63, 75, 81, 101, 113, 114, 119, 134, 142, 156, 170, 171, 179, 180, 185, 201, 206, 207, 214 | [[51, 49], [58, 63], [80, 81], [100, 101], [118, 119], [133, 134], [148, 156], [180, 185], [180, 201], [213, 214]] |
| `app/tools/audit/aws/common.py` | 81.82% | N/A | 9, 14 | None |
| `app/tools/audit/aws/ec2.py` | 72.97% | 61.54% | 42, 56, 87, 88, 98, 99, 100, 101, 115, 116, 140, 141, 146, 158, 159, 175, 176, 177, 193, 194 | [[41, 42], [55, 56], [97, 98], [98, 97], [98, 99], [100, 98], [100, 101], [121, 120], [145, 146], [178, 168]] |
| `app/tools/audit/aws/guardduty.py` | 56.52% | 16.67% | 25, 26, 43, 44, 45, 46, 47, 62, 63, 66 | [[28, 43], [43, 44], [43, 66], [46, 43], [46, 47]] |
| `app/tools/audit/aws/iam.py` | 84.62% | 50.00% | 26, 27 | [[14, 29]] |
| `app/tools/audit/aws/rds.py` | 78.12% | 84.62% | 111, 112, 147, 148, 163, 164, 165, 188, 189, 204, 205, 208, 231, 232 | [[118, 132], [132, 116], [174, 157], [217, 198]] |
| `app/tools/audit/aws/s3.py` | 64.37% | 41.67% | 28, 29, 37, 38, 65, 66, 67, 80, 83, 84, 105, 108, 109, 127, 128, 129, 132, 133, 158, 159, 177, 178, 195, 208, 209, 210, 224, 225, 226, 243, 244 | [[51, 86], [66, 67], [66, 80], [89, 105], [113, 135], [128, 129], [128, 135], [144, 161], [163, 180], [184, 186], [194, 195], [209, 210], [209, 224], [230, 31]] |
| `app/tools/audit/aws/vpc.py` | 89.47% | 66.67% | 65, 66 | [[23, 43], [50, 19]] |
| `app/tools/audit/aws_audit.py` | 57.14% | 0.00% | 40, 42, 46, 47, 50, 51, 52, 55, 58, 59, 60, 61, 62, 63, 65 | [[58, 59], [58, 63]] |

## Frontend modules

| Module | Lines | Branches |
|---|---:|---:|
| `frontend/src/App.jsx` | 100% | 100% |
| `frontend/src/main.jsx` | 0% | 0% |
| `frontend/src/components/agents/AgentWorkflow.jsx` | 76.47% | 89.36% |
| `frontend/src/components/dashboard/LatestAudits.jsx` | 77.77% | 40.9% |
| `frontend/src/components/dashboard/SeverityChart.jsx` | 100% | 100% |
| `frontend/src/components/dashboard/StatCard.jsx` | 100% | 28.57% |
| `frontend/src/components/findings/FindingsTable.jsx` | 100% | 76.19% |
| `frontend/src/components/layout/AppLayout.jsx` | 100% | 75% |
| `frontend/src/components/layout/ProtectedRoute.jsx` | 100% | 50% |
| `frontend/src/components/layout/Sidebar.jsx` | 100% | 100% |
| `frontend/src/components/layout/Topbar.jsx` | 100% | 83.33% |
| `frontend/src/components/reports/MarkdownView.jsx` | 50% | 100% |
| `frontend/src/components/ui/Primitives.jsx` | 100% | 93.75% |
| `frontend/src/context/AuthContext.jsx` | 97.87% | 88.88% |
| `frontend/src/hooks/useApi.js` | 90% | 100% |
| `frontend/src/lib/utils.js` | 100% | 100% |
| `frontend/src/pages/Agents.jsx` | 100% | 100% |
| `frontend/src/pages/CloudAudit.jsx` | 67.34% | 65% |
| `frontend/src/pages/Dashboard.jsx` | 94.73% | 79.62% |
| `frontend/src/pages/Findings.jsx` | 100% | 80% |
| `frontend/src/pages/Login.jsx` | 95.23% | 78.57% |
| `frontend/src/pages/ReportDetail.jsx` | 30.76% | 46.42% |
| `frontend/src/pages/Settings.jsx` | 100% | 76.92% |
| `frontend/src/services/api.js` | 90.69% | 94.87% |

## Exclusions and critical gaps

All backend app modules are measured; tests are outside the source scope. Coverage.py excludes type-checking/unreachable annotations according to its defaults; exact excluded lines are retained in backend-coverage.json. Frontend excludes only test sources and qa-setup.js; main.jsx remains measured and uncovered by unit tests. Browser E2E execution is separate and not added to unit coverage. No application module is excluded to raise percentages.

Uncovered branches include AWS exception/partial-response paths, model tool-response variants, retrieval/model-load errors and report export/print behavior. A passing line target does not establish robust branch coverage or semantic correctness. Vitest 4 uses executable-line accounting; earlier Vitest 3 instrumentation numbers in diagnostic logs are superseded.

## Reproduction and artifacts

Run `.venv/bin/python scripts/qa.py unit`, frontend `npm run test:coverage`, then backend `scripts/qa.py integration` and `scripts/qa.py security`. Run `scripts/qa.py gate` and `scripts/qa_reports.py` with the same Python. Backend XML/JSON/HTML: design/qa/evidence/backend-coverage.{xml,json}, backend-html/index.html. Frontend HTML/LCOV/JSON: design/qa/evidence/frontend-coverage/. Full per-statement frontend maps and missing branch counters are in coverage-final.json. Historical preliminary unit artifacts are kept separately.
