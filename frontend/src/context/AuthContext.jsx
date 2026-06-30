/**
 * Authentication state shared across the application.
 *
 * The JWTs themselves live only in httpOnly cookies and are never accessible
 * here. To survive a page reload we persist a single non-sensitive flag (the
 * logged-in user's email) in localStorage — never a token. The axios refresh
 * interceptor keeps the cookies fresh; if it ultimately fails it calls
 * `handleAuthFailure` to reset this context to a logged-out state.
 */
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { setAuthFailureHandler } from "../services/apiClient.js";
import { login as loginRequest, logout as logoutRequest } from "../services/authService.js";

const STORAGE_KEY = "securebank.user.email";
const AuthContext = createContext(null);

/** Provider that exposes auth state and actions to descendant components. */
export function AuthProvider({ children }) {
  const [email, setEmail] = useState(() => localStorage.getItem(STORAGE_KEY));

  const clearSession = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setEmail(null);
  }, []);

  useEffect(() => {
    setAuthFailureHandler(clearSession);
  }, [clearSession]);

  const signIn = useCallback(async (credentials) => {
    await loginRequest(credentials);
    localStorage.setItem(STORAGE_KEY, credentials.email);
    setEmail(credentials.email);
  }, []);

  const signOut = useCallback(async () => {
    try {
      await logoutRequest();
    } finally {
      clearSession();
    }
  }, [clearSession]);

  const value = useMemo(
    () => ({ email, isAuthenticated: Boolean(email), signIn, signOut }),
    [email, signIn, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Access the authentication context.
 * @returns {{email: string|null, isAuthenticated: boolean, signIn: Function, signOut: Function}}
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
