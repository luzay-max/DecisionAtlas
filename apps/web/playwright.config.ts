import { defineConfig } from "@playwright/test";
import path from "node:path";

const repoRoot = path.resolve(__dirname, "../..");
const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:3000";
const skipWebServer = process.env.PLAYWRIGHT_SKIP_WEBSERVER === "1";

export default defineConfig({
  testDir: "./tests-e2e",
  timeout: 60_000,
  // The CI demo, account/bootstrap and review E2E suites share one SQLite
  // database. Serial execution avoids nondeterministic bootstrap races.
  workers: process.env.CI === "true" ? 1 : undefined,
  use: {
    baseURL,
    // Use the full Chromium binary in the supported new-headless mode.
    // CI installs with --no-shell to avoid downloading the separate headless shell.
    channel: "chromium",
  },
  webServer: skipWebServer ? undefined : [
    {
      command: "powershell -ExecutionPolicy Bypass -File ../../scripts/ci/start-engine-smoke.ps1",
      cwd: __dirname,
      url: "http://127.0.0.1:8000/health",
      reuseExistingServer: true,
      stdout: "pipe",
      stderr: "pipe",
      timeout: 240_000
    },
    {
      command: "powershell -ExecutionPolicy Bypass -File ../../scripts/ci/start-api-smoke.ps1",
      cwd: __dirname,
      url: "http://127.0.0.1:3001/health",
      reuseExistingServer: true,
      stdout: "pipe",
      stderr: "pipe",
      timeout: 240_000
    },
    {
      command: "powershell -ExecutionPolicy Bypass -File ../../scripts/ci/start-web-smoke.ps1",
      cwd: __dirname,
      url: "http://127.0.0.1:3000",
      reuseExistingServer: true,
      stdout: "pipe",
      stderr: "pipe",
      timeout: 240_000,
      env: {
        API_BASE_URL: "http://127.0.0.1:3001",
        PLAYWRIGHT_REPO_ROOT: repoRoot
      }
    }
  ]
});
