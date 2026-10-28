import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
export default defineConfig({
  plugins: [react()],
  esbuild: { jsx: "automatic" },
  test: {
    environment: "jsdom",
    include: ["src/**/*.test.{js,jsx}"],
    setupFiles: ["./src/qa-setup.js"],
    reporters: ["default", "junit"],
    outputFile: "../design/qa/evidence/frontend-unit.xml",
    coverage: {
      provider: "v8",
      include: ["src/**/*.{js,jsx}"],
      exclude: ["src/**/*.test.*", "src/qa-setup.js"],
      reporter: ["text", "json", "json-summary", "html", "lcov", "cobertura"],
      reportsDirectory: "../design/qa/evidence/frontend-coverage",
      thresholds: { lines: 80 },
    },
  },
});
