/**
 * Vite configuration for the SecureBank frontend.
 *
 * Runs the dev server on port 5173 (whitelisted by the backend CORS policy)
 * and enables the React Fast Refresh plugin. The API base URL is supplied at
 * build time through the `VITE_API_URL` environment variable.
 */
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
  },
});
