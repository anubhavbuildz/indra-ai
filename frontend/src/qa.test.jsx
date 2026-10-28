import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
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
    vi.spyOn(api, "login").mockResolvedValue({access_token: "test-token"});
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
