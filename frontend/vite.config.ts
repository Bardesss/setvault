/// <reference types="vitest" />
import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    proxy: { "/api": "http://localhost:1970", "/uploads": "http://localhost:1080" },
  },
  test: { environment: "node", exclude: ["tests/**", "node_modules/**"] },
});
