import { defineConfig, devices } from "@playwright/test";
const external = process.env.QA_EXTERNAL_SERVERS === "1";
const backendUrl = process.env.QA_BACKEND_URL || "http://127.0.0.1:18000";
const frontendUrl = process.env.QA_FRONTEND_URL || "http://127.0.0.1:15173";
const backendPort = new URL(backendUrl).port || "18000";
const frontendPort = new URL(frontendUrl).port || "15173";
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 30000,
  reporter: [["list"], ["html", {outputFolder: "../design/qa/evidence/playwright-html", open: "never"}],
    ["junit", {outputFile: "../design/qa/evidence/e2e.xml"}]],
  outputDir: "../design/qa/evidence/playwright-results",
  use: {baseURL: frontendUrl, trace: "retain-on-failure", screenshot: "only-on-failure"},
  projects: [
    {name: "desktop", use: {...devices["Desktop Chrome"]}},
    {name: "tablet", use: {viewport: {width: 768, height: 1024}}},
    {name: "mobile", use: {...devices["iPhone 13"], defaultBrowserType: "chromium"}},
  ],
  webServer: external ? undefined : [
    {command: `${process.env.QA_PYTHON || ".venv/bin/python"} -m uvicorn scripts.qa_server:app --host 127.0.0.1 --port ${backendPort}`,
      cwd: "..", url: `${backendUrl}/health`, reuseExistingServer: false, timeout: 60000},
    {command: `npm run dev -- --host 127.0.0.1 --port ${frontendPort}`, url: frontendUrl, reuseExistingServer: false, timeout: 60000},
  ],
});
