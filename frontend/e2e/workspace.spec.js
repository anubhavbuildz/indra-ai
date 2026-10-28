import { test, expect } from "@playwright/test";
const backend = process.env.QA_BACKEND_URL || "http://127.0.0.1:18000";
test.beforeEach(async ({page}) => {
  await page.addInitScript((url) => localStorage.setItem("indraa.apiBaseUrl", url), backend);
});
async function login(page) {
  await page.goto("/login");
  await page.getByLabel("Username").fill("test-user");
  await page.getByLabel("Password", {exact: true}).fill("test-password");
  await page.getByRole("button", {name: "Continue securely"}).click();
  await expect(page.getByRole("heading", {name: "Security overview"})).toBeVisible();
}
async function navigate(page, name) {
  const menu = page.getByRole("button", {name: "Open navigation"});
  if (await menu.isVisible()) await menu.click();
  await page.getByRole("link", {name, exact: true}).click();
}
test("E2E-001 startup, real login, synthetic audit and saved report", async ({page, request}) => {
  const errors = []; page.on("pageerror", error => errors.push(error.message));
  expect((await request.get(`${backend}/health`)).ok()).toBeTruthy();
  await login(page);
  await page.reload();
  await expect(page.getByRole("heading", {name: "Security overview"})).toBeVisible();
  await expect.poll(() => page.evaluate(() => localStorage.getItem("indraa.accessToken"))).toBeTruthy();
  await navigate(page, "Cloud audit");
  await page.getByRole("button", {name: "Accept us-east-1 for this audit"}).click();
  const completed = page.waitForResponse(r => r.url().endsWith("/api/v1/chat") && r.request().method() === "POST");
  await page.getByRole("button", {name: "Run audit", exact: true}).click();
  const response = await completed; expect(response.status()).toBe(200);
  const payload = await response.json(); expect(payload.cloud_agent_response.findings[0].evidence.fixture).toBe(true);
  await expect(page.getByRole("link", {name: "View assessment"})).toBeVisible();
  await navigate(page, "Findings");
  await expect(page.getByText("Synthetic public bucket")).toBeVisible();
  await page.getByRole("button", {name: "Expand finding details"}).click();
  await expect(page.getByText('"fixture": true', {exact: false})).toBeVisible();
  await page.goto(`/reports/${payload.assessment_id}`);
  await expect(page.getByText("Senior agent assessment", {exact: true})).toBeVisible();
  await expect(page.getByText("Synthetic fixture review.", {exact: false}).first()).toBeVisible();
  expect(errors).toEqual([]);
  await expect(page.getByRole("button", {name: "Sign out"})).toBeVisible();
});
test("E2E-001 invalid login and network failure remain visible", async ({page}) => {
  await page.goto("/login"); await page.getByLabel("Username").fill("test-user");
  await page.getByLabel("Password", {exact: true}).fill("wrong");
  await page.getByRole("button", {name: "Continue securely"}).click();
  await expect(page.getByRole("alert")).toContainText("incorrect");
  await page.route("**/api/v1/auth/login", route => route.abort("failed"));
  await page.getByRole("button", {name: "Continue securely"}).click();
  await expect(page.getByRole("alert")).toContainText("Could not connect");
});
test("E2E-001 protected route and session expiry", async ({page}) => {
  await page.goto("/audit"); await expect(page.getByLabel("Username")).toBeVisible();
  await login(page);
  await page.route("**/api/v1/aws/identity", route => route.fulfill({status: 401, contentType: "application/json", body: JSON.stringify({error: {code: "invalid_token", message: "Expired"}})}));
  await navigate(page, "Cloud audit");
  // Force an actual protected request rather than depending on query staleness.
  await page.evaluate(async () => {
    const {api} = await import("/src/services/api.js");
    await api.awsIdentity().catch(() => {});
  });
  await expect(page.getByLabel("Username")).toBeVisible();
  expect(await page.evaluate(() => localStorage.getItem("indraa.accessToken"))).toBeNull();
});
