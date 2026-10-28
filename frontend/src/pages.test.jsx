import { beforeEach, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./App";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { api } from "./services/api";

const report = {audited_regions: ["us-east-1"], audited_services: ["s3"], total_issues: 1,
  critical_count: 0, high_count: 1, medium_count: 0, low_count: 0,
  findings: [{service: "s3", region: "us-east-1", resource: "fixture-bucket", check_id: "s3.public",
    severity: "HIGH", title: "Synthetic public bucket", issue: "Public fixture", evidence: {public: true}, remediation: "Block access"}]};
const assessment = {id: "fixture-id", name: "Fixture assessment", created_at: "2026-01-01T00:00:00Z",
  audit_report: report, senior_review: "Fixture senior review", compliance_review: "Fixture compliance"};
beforeEach(() => {
  vi.spyOn(api, "login").mockResolvedValue({access_token: "fixture-token"});
  vi.spyOn(api, "assessments").mockResolvedValue({items: [assessment]});
  vi.spyOn(api, "assessment").mockResolvedValue(assessment);
  vi.spyOn(api, "health").mockResolvedValue({status: "ok", service: "Fixture API", version: "0.1.0"});
  vi.spyOn(api, "ready").mockResolvedValue({database_configured: true});
  vi.spyOn(api, "ragStatus").mockResolvedValue({available: true, index_available: true, metadata_available: true});
  vi.spyOn(api, "awsIdentity").mockResolvedValue({status: "configured", account: "000000000000", region: "us-east-1"});
  vi.spyOn(api, "chat").mockResolvedValue({cloud_agent_response: report, compliance_agent_response: "Fixture compliance",
    senior_agent_response: "Fixture senior", assessment_id: "fixture-id", sources: []});
});
async function mount(path) {
  const client = new QueryClient({defaultOptions: {queries: {retry: false}, mutations: {retry: false}}});
  function SignedApp() {
    const auth = useAuth();
    if (!auth.isAuthenticated) return <button onClick={() => auth.signIn("test-user", "test-password")}>Fixture sign in</button>;
    return <App />;
  }
  render(<MemoryRouter initialEntries={[path]}><QueryClientProvider client={client}><AuthProvider><SignedApp /></AuthProvider></QueryClientProvider></MemoryRouter>);
  fireEvent.click(screen.getByRole("button", {name: "Fixture sign in"}));
  return client;
}
it("UNIT-029 dashboard renders saved evidence and navigation controls", async () => {
  await mount("/"); await screen.findByText("Security overview");
  expect(await screen.findByText("Fixture assessment")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", {name: "Toggle sidebar"}));
  fireEvent.click(screen.getByRole("button", {name: "Toggle sidebar"}));
  fireEvent.click(screen.getByRole("button", {name: "Open navigation"}));
  fireEvent.click(screen.getByRole("button", {name: "Close navigation"}));
  fireEvent.click(screen.getByRole("button", {name: "Sign out"}));
  expect(await screen.findByRole("button", {name: "Fixture sign in"})).toBeInTheDocument();
});
it("UNIT-029 findings filters and expands evidence", async () => {
  await mount("/findings"); await screen.findByText("Synthetic public bucket");
  fireEvent.click(screen.getByRole("button", {name: "Expand finding details"}));
  expect(screen.getByText("Block access")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", {name: "Collapse finding details"}));
  fireEvent.change(screen.getByPlaceholderText("Search finding, resource, service…"), {target: {value: "missing"}});
  expect(screen.getByText("No findings match these filters.")).toBeInTheDocument();
  fireEvent.change(screen.getByPlaceholderText("Search finding, resource, service…"), {target: {value: ""}});
  fireEvent.change(screen.getByRole("combobox"), {target: {value: "LOW"}});
  expect(screen.getByText("No findings match these filters.")).toBeInTheDocument();
});
it("UNIT-029 saved report displays both reviews", async () => {
  await mount("/reports/fixture-id");
  expect(await screen.findByText("Fixture senior review")).toBeInTheDocument();
  expect(screen.getByText("Fixture compliance")).toBeInTheDocument();
});
it("UNIT-029 agent page explains workflow and expiry redirects", async () => {
  await mount("/agents"); await screen.findByText("Three specialists. One evidence trail.");
  window.dispatchEvent(new Event("indraa:session-expired"));
  expect(await screen.findByRole("button", {name: "Fixture sign in"})).toBeInTheDocument();
});
it("UNIT-029 settings validates URL and saves safe origin", async () => {
  await mount("/settings"); const input = await screen.findByLabelText("API base URL");
  fireEvent.change(input, {target: {value: "file:///etc/passwd"}});
  fireEvent.click(screen.getByRole("button", {name: "Save URL"}));
  expect(screen.getByText("Use an http or https URL.")).toBeInTheDocument();
  fireEvent.change(input, {target: {value: "http://localhost:8000/path"}});
  fireEvent.click(screen.getByRole("button", {name: "Save URL"}));
  expect(await screen.findByText("Saved")).toBeInTheDocument();
  expect(input).toHaveValue("http://localhost:8000");
  fireEvent.click(screen.getByRole("button", {name: "Refresh"}));
});
it("UNIT-029 audit requires region confirmation then renders result", async () => {
  await mount("/audit"); await screen.findByRole("button", {name: "Accept us-east-1 for this audit"});
  fireEvent.click(screen.getByRole("button", {name: "Run audit"}));
  expect(await screen.findByRole("alert")).toHaveTextContent("Confirm the backend-configured AWS region");
  fireEvent.click(screen.getByRole("button", {name: "Accept us-east-1 for this audit"}));
  fireEvent.change(screen.getByRole("textbox"), {target: {value: "Fixture scope"}});
  fireEvent.click(screen.getByRole("button", {name: "Run audit"}));
  expect(await screen.findByRole("link", {name: "View assessment"})).toHaveAttribute("href", "/reports/fixture-id");
  expect(api.chat).toHaveBeenCalledWith(expect.stringContaining("Fixture scope"), []);
  fireEvent.click(screen.getByRole("button", {name: /Compliance Agent Reviewed/}));
  expect(await screen.findByText("Fixture compliance")).toBeInTheDocument();
});
it("UNIT-029 empty findings and API failure are visible", async () => {
  api.assessments.mockResolvedValue({items: []}); await mount("/findings");
  expect(await screen.findByText("No assessment findings yet")).toBeInTheDocument();
});
it("UNIT-029 API error supports retry", async () => {
  api.assessments.mockRejectedValueOnce(new Error("Fixture unavailable"));
  await mount("/findings"); expect(await screen.findByText("Fixture unavailable")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", {name: /Try again/i}));
  expect(await screen.findByText("Synthetic public bucket")).toBeInTheDocument();
});
