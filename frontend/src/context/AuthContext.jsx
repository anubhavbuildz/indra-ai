import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { api, setAccessToken } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [username, setUsername] = useState("");

  const signIn = useCallback(async (loginName, password) => {
    const result = await api.login(loginName, password);
    setAccessToken(result.access_token);
    setToken(result.access_token);
    setUsername(loginName);
    return result;
  }, []);

  const signOut = useCallback(() => {
    setAccessToken(null);
    setToken(null);
    setUsername("");
  }, []);

  const value = useMemo(
    () => ({ token, username, isAuthenticated: Boolean(token), signIn, signOut }),
    [token, username, signIn, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used within AuthProvider");
  return value;
}
