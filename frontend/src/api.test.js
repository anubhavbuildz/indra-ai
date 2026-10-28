import { it, expect, vi, beforeEach } from "vitest";
import { api, setAccessToken, saveApiBaseUrl, getApiBaseUrl, ApiError } from "./services/api";
beforeEach(() => setAccessToken(null));
function response(status, payload) { return new Response(JSON.stringify(payload), {status, headers: {"content-type": "application/json"}}); }
it("UNIT-027 normalizes backend URL", () => {
  expect(saveApiBaseUrl(" http://localhost:8000/// ")).toBe("http://localhost:8000");
  saveApiBaseUrl(""); expect(getApiBaseUrl()).toContain("http");
});
it("UNIT-027 sends bearer and encoded request", async () => {
  const fetcher = vi.fn().mockResolvedValue(response(200, {status: "completed"}));
  vi.stubGlobal("fetch", fetcher); setAccessToken("test-token");
  await api.chat("audit", []);
  const [url, options] = fetcher.mock.calls[0];
  expect(url).toContain("/api/v1/chat"); expect(options.headers.get("Authorization")).toBe("Bearer test-token");
  expect(JSON.parse(options.body)).toEqual({message: "audit", history: []});
});
it("UNIT-027 emits session expiry on protected 401", async () => {
  const expired = vi.fn(); window.addEventListener("indraa:session-expired", expired);
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response(401, {error: {message: "Expired", code: "invalid_token"}})));
  await expect(api.assessments()).rejects.toMatchObject({status: 401, code: "invalid_token"});
  expect(expired).toHaveBeenCalledOnce(); window.removeEventListener("indraa:session-expired", expired);
});
it("UNIT-027 maps network errors and preserves abort", async () => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network")));
  await expect(api.health()).rejects.toBeInstanceOf(ApiError);
  const abort = new DOMException("cancel", "AbortError");
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(abort));
  await expect(api.health()).rejects.toBe(abort);
});
it("UNIT-027 handles text error and encodes report ID", async () => {
  const fetcher = vi.fn().mockResolvedValue(new Response("unavailable", {status: 503}));
  vi.stubGlobal("fetch", fetcher);
  await expect(api.assessment("a/b")).rejects.toMatchObject({status: 503});
  expect(fetcher.mock.calls[0][0]).toContain("a%2Fb");
});

it("UNIT-027 resolves container same-origin configuration to the browser origin", async () => {
  vi.stubEnv("VITE_API_BASE_URL", "/");
  try {
    expect(getApiBaseUrl()).toBe(window.location.origin);
    const fetcher = vi.fn().mockResolvedValue(response(200, {status: "ok"}));
    vi.stubGlobal("fetch", fetcher);
    await api.health();
    expect(fetcher.mock.calls[0][0]).toBe(`${window.location.origin}/health`);
    expect(saveApiBaseUrl("https://custom.example/")).toBe("https://custom.example");
  } finally { vi.unstubAllEnvs(); }
});
