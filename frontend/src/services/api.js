const API_PREFIX = "/api/v1";
const BASE_URL_KEY = "indraa.apiBaseUrl";
let accessToken = null;

export function setAccessToken(token) {
  accessToken = token || null;
}

export function getApiBaseUrl() {
  const saved = localStorage.getItem(BASE_URL_KEY);
  const configured = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
  return (saved || configured).replace(/\/+$/, "");
}

export function saveApiBaseUrl(value) {
  const cleaned = value.trim().replace(/\/+$/, "");
  if (cleaned) localStorage.setItem(BASE_URL_KEY, cleaned);
  else localStorage.removeItem(BASE_URL_KEY);
  return getApiBaseUrl();
}

export class ApiError extends Error {
  constructor(message, status, code, details) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details || {};
  }
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (accessToken && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  let response;
  try {
    response = await fetch(`${getApiBaseUrl()}${path}`, {
      ...options,
      headers,
    });
  } catch (error) {
    if (error?.name === "AbortError") throw error;
    throw new ApiError(
      `Could not connect to the backend at ${getApiBaseUrl()}. Check that it is running and CORS is configured.`,
      0,
      "network_error",
    );
  }

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (response.status === 401 && !path.endsWith("/auth/login")) {
    window.dispatchEvent(new Event("indraa:session-expired"));
  }

  if (!response.ok) {
    const body = payload?.error;
    const message = body?.message || `Request failed with status ${response.status}.`;
    throw new ApiError(message, response.status, body?.code, body?.details);
  }
  return payload;
}

export const api = {
  login: (username, password) =>
    request(`${API_PREFIX}/auth/login`, {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),

  chat: (message, history = []) =>
    request(`${API_PREFIX}/chat`, {
      method: "POST",
      body: JSON.stringify({ message, history }),
    }),

  assessments: ({ limit = 50, offset = 0 } = {}) =>
    request(`${API_PREFIX}/assessments?limit=${limit}&offset=${offset}`),

  assessment: (assessmentId) =>
    request(`${API_PREFIX}/assessments/${encodeURIComponent(assessmentId)}`),

  ragStatus: () => request(`${API_PREFIX}/rag/status`),

  awsIdentity: () => request(`${API_PREFIX}/aws/identity`),

  health: () => request("/health"),

  ready: () => request("/ready"),
};
