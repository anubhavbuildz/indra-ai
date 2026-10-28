import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, setAccessToken } from "../services/api";

const AuthContext = createContext(null);
const TOKEN_KEY = "indraa.accessToken";

function sessionFromToken(token) {
  try {
    if (typeof token !== "string") return null;
    const parts = token.split(".");
    if (parts.length !== 3 || parts.some((part) => !part)) return null;
    const encoded = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const bytes = Uint8Array.from(atob(encoded), (character) => character.charCodeAt(0));
    const claims = JSON.parse(new TextDecoder().decode(bytes));
    const expiresAt = claims.exp * 1000;
    // Decoding supports client-side expiry only; the backend verifies the signature.
    if (typeof claims.exp !== "number" || !Number.isFinite(expiresAt) || expiresAt <= Date.now()) return null;
    if (typeof claims.sub !== "string" || !claims.sub.trim()) return null;
    return { token, username: claims.sub, expiresAt };
  } catch {
    return null;
  }
}

function restoreSession() {
  const stored = localStorage.getItem(TOKEN_KEY);
  const session = sessionFromToken(stored);
  if (stored && !session) localStorage.removeItem(TOKEN_KEY);
  // Restore the bearer token before authenticated children issue their first requests.
  setAccessToken(session?.token || null);
  return session;
}

export function AuthProvider({ children }) {
  const [session, setSession] = useState(restoreSession);

  const signIn = useCallback(async (loginName, password) => {
    const result = await api.login(loginName, password);
    const nextSession = sessionFromToken(result.access_token);
    if (!nextSession) throw new Error("The server returned an invalid or expired access token.");
    localStorage.setItem(TOKEN_KEY, nextSession.token);
    setAccessToken(nextSession.token);
    setSession(nextSession);
    return result;
  }, []);

  const signOut = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setAccessToken(null);
    setSession(null);
  }, []);

  useEffect(() => {
    if (!session) return undefined;
    const timer = window.setTimeout(signOut, Math.min(session.expiresAt - Date.now(), 2147483647));
    return () => window.clearTimeout(timer);
  }, [session, signOut]);

  useEffect(() => {
    function syncSession(event) {
      if (event.storageArea === localStorage && (event.key === TOKEN_KEY || event.key === null)) {
        setSession(restoreSession());
      }
    }
    window.addEventListener("storage", syncSession);
    return () => window.removeEventListener("storage", syncSession);
  }, []);

  const value = useMemo(
    () => ({
      token: session?.token || null,
      username: session?.username || "",
      isAuthenticated: Boolean(session),
      signIn,
      signOut,
    }),
    [session, signIn, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used within AuthProvider");
  return value;
}
