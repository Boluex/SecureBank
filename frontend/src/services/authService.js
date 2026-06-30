/**
 * Authentication API calls.
 *
 * Each function returns the parsed response body. Tokens themselves live only
 * in httpOnly cookies set by the backend, so nothing sensitive is returned to
 * or stored by the caller.
 */
import apiClient from "./apiClient.js";

/**
 * Register a new user.
 * @param {{email: string, full_name: string, password: string}} payload
 * @returns {Promise<object>} The created public user record.
 */
export async function register(payload) {
  const response = await apiClient.post("/auth/register", payload);
  return response.data;
}

/**
 * Log in with email and password; auth cookies are set on success.
 * @param {{email: string, password: string}} credentials
 * @returns {Promise<object>} The issued token metadata.
 */
export async function login(credentials) {
  const response = await apiClient.post("/auth/login", credentials);
  return response.data;
}

/** Log out, revoking the refresh token and clearing auth cookies. */
export async function logout() {
  await apiClient.post("/auth/logout", {});
}
