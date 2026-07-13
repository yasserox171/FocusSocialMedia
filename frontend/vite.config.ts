import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Dev proxy: API, media and WebSockets go to the Django backend.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
      "/media": "http://localhost:8000",
      "/ws": { target: "ws://localhost:8000", ws: true },
    },
  },
});
