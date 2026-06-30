/**
 * Configured Axios instance with automatic JWT refresh.
 *
 * The backend issues access/refresh tokens as httpOnly cookies, so the browser
 * attaches them automatically when `withCredentials` is enabled — the tokens
 * are never read by or stored in JavaScript. When a request fails with 401 the
 * response interceptor transparently calls `/auth/refresh` once and retries the
 * original request, rotating the token pair behind the scenes.
 */
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

// Endpoints that must never trigger the refresh-and-retry loop.
const AUTH_PATHS = ["/auth/login", "/auth/refresh", "/auth/logout"];

let refreshPromise = null;

/** Invoked when refreshing fails so the app can reset to a logged-out state. */
let onAuthFailure = () => {};

/**
 * Register a callback fired when token refresh ultimately fails.
 * @param {() => void} handler - Called after an unrecoverable 401.
 */
export function setAuthFailureHandler(handler) {
  onAuthFailure = handler;
}

/** Refresh the token pair, de-duplicating concurrent refresh attempts. */
function refreshTokens() {
  if (refreshPromise === null) {
    refreshPromise = apiClient
      .post("/auth/refresh", {})
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const isAuthPath = AUTH_PATHS.some((path) => originalRequest?.url?.includes(path));
    const shouldRetry =
      error.response?.status === 401 && !originalRequest?._retry && !isAuthPath;

    if (!shouldRetry) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;
    try {
      await refreshTokens();
      return apiClient(originalRequest);
    } catch (refreshError) {
      onAuthFailure();
      return Promise.reject(refreshError);
    }
  },
);

export default apiClient;
