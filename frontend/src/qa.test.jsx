import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Login from "./pages/Login";
import { api } from "./services/api";

function mount() { return render(<MemoryRouter><AuthProvider><Login /></AuthProvider></MemoryRouter>); }
function fill() {
  fireEvent.change(screen.getByLabelText("Username"), {target: {value: "test-user"}});
  fireEvent.change(screen.getByLabelText("Password"), {target: {value: "test-password"}});
}
describe("UNIT-026 login and auth", () => {
  it("renders labeled required fields and toggles visibility", () => {
    mount(); expect(screen.getByLabelText("Username")).toBeRequired();
    expect(screen.getByLabelText("Password")).toHaveAttribute("type", "password");
    fireEvent.click(screen.getByRole("button", {name: "Toggle password visibility"}));
    expect(screen.getByLabelText("Password")).toHaveAttribute("type", "text");
  });
  it("shows pending state and safe login failure", async () => {
    let reject; vi.spyOn(api, "login").mockImplementation(() => new Promise((_, r) => {reject = r;}));
    mount(); fill(); fireEvent.click(screen.getByRole("button", {name: /Continue securely/}));
    expect(screen.getByRole("button", {name: /Authenticating/})).toBeDisabled();
    reject(new Error("Invalid credentials"));
    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid credentials");
    expect(screen.getByRole("button", {name: /Continue securely/})).toBeEnabled();
  });
  it("sets auth identity then clears token on sign out", async () => {
    vi.spyOn(api, "login").mockResolvedValue({access_token: `${btoa(JSON.stringify({alg: "HS256", typ: "JWT"}))}.${btoa(JSON.stringify({sub: "test-user", exp: Math.floor(Date.now() / 1000) + 7200}))}.fixture-signature`});
    function Harness() {
      const auth = useAuth();
      return <><span>{auth.isAuthenticated ? auth.username : "signed out"}</span>
        <button onClick={() => auth.signIn("test-user", "test-password")}>in</button>
        <button onClick={auth.signOut}>out</button></>;
    }
    render(<AuthProvider><Harness /></AuthProvider>);
    fireEvent.click(screen.getByText("in"));
    await waitFor(() => expect(screen.getByText("test-user")).toBeInTheDocument());
    fireEvent.click(screen.getByText("out")); expect(screen.getByText("signed out")).toBeInTheDocument();
  });
});


function fixtureToken(claims = {}) {
  return `${btoa(JSON.stringify({alg: "HS256", typ: "JWT"}))}.${btoa(JSON.stringify({
    sub: "test-user", exp: Math.floor(Date.now() / 1000) + 7200, ...claims,
  }))}.fixture-signature`;
}
function SessionHarness() {
  const auth = useAuth();
  return <><span>{auth.isAuthenticated ? auth.username : "signed out"}</span>
    <button onClick={() => auth.signIn("test-user", "test-password")}>Sign in fixture</button>
    <button onClick={auth.signOut}>Sign out fixture</button>
    <button onClick={() => api.health()}>Request fixture</button></>;
}
it("UNIT-026 stores JWT, restores identity and bearer on remount, and clears on sign-out", async () => {
  const token = fixtureToken();
  vi.spyOn(api, "login").mockResolvedValue({access_token: token});
  let mounted = render(<AuthProvider><SessionHarness /></AuthProvider>);
  fireEvent.click(screen.getByText("Sign in fixture"));
  expect(await screen.findByText("test-user")).toBeInTheDocument();
  expect(localStorage.getItem("indraa.accessToken")).toBe(token);
  expect(localStorage.getItem("password")).toBeNull();
  mounted.unmount();
  const fetcher = vi.fn().mockResolvedValue(new Response('{}', {status: 200, headers: {"content-type": "application/json"}}));
  vi.stubGlobal("fetch", fetcher);
  mounted = render(<AuthProvider><SessionHarness /></AuthProvider>);
  expect(screen.getByText("test-user")).toBeInTheDocument();
  fireEvent.click(screen.getByText("Request fixture"));
  expect(fetcher.mock.calls[0][1].headers.get("Authorization")).toBe(`Bearer ${token}`);
  fireEvent.click(screen.getByText("Sign out fixture"));
  expect(localStorage.getItem("indraa.accessToken")).toBeNull();
  expect(screen.getByText("signed out")).toBeInTheDocument();
});
it.each(["not-a-jwt", fixtureToken({exp: 1}), fixtureToken({exp: "invalid"}), fixtureToken({sub: ""})])(
  "UNIT-026 discards malformed or expired stored JWT: %s", token => {
    localStorage.setItem("indraa.accessToken", token);
    render(<AuthProvider><SessionHarness /></AuthProvider>);
    expect(screen.getByText("signed out")).toBeInTheDocument();
    expect(localStorage.getItem("indraa.accessToken")).toBeNull();
  },
);
it("UNIT-026 expires a stored JWT without requiring a request or refresh", () => {
  vi.useFakeTimers();
  try {
    localStorage.setItem("indraa.accessToken", fixtureToken({exp: Math.floor(Date.now() / 1000) + 2}));
    render(<AuthProvider><SessionHarness /></AuthProvider>);
    expect(screen.getByText("test-user")).toBeInTheDocument();
    act(() => vi.advanceTimersByTime(2000));
    expect(screen.getByText("signed out")).toBeInTheDocument();
    expect(localStorage.getItem("indraa.accessToken")).toBeNull();
  } finally { vi.useRealTimers(); }
});
it("UNIT-026 synchronizes sign-out from another tab", () => {
  localStorage.setItem("indraa.accessToken", fixtureToken());
  render(<AuthProvider><SessionHarness /></AuthProvider>);
  localStorage.removeItem("indraa.accessToken");
  act(() => window.dispatchEvent(new StorageEvent("storage", {key: "indraa.accessToken", storageArea: localStorage})));
  expect(screen.getByText("signed out")).toBeInTheDocument();
});
