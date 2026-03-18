import { defineConfig } from "@playwright/test";
import path from "node:path";

const repoRoot = path.resolve(__dirname, "../..");

export default defineConfig({
  testDir: "./tests-e2e",
  timeout: 60_000,
  use: {
    baseURL: "http://127.0.0.1:3000"
  },
  webServer: [
    {
      command: "powershell -ExecutionPolicy Bypass -File ../../scripts/ci/start-engine-smoke.ps1",
      cwd: __dirname,
      url: "http://127.0.0.1:8000/health",
      reuseExistingServer: true,
      timeout: 120_000
    },
    {
      command: "powershell -ExecutionPolicy Bypass -File ../../scripts/ci/start-api-smoke.ps1",
      cwd: __dirname,
      url: "http://127.0.0.1:3001/health",
      reuseExistingServer: true,
      timeout: 120_000
    },
    {
      command: "powershell -ExecutionPolicy Bypass -File ../../scripts/ci/start-web-smoke.ps1",
      cwd: __dirname,
      url: "http://127.0.0.1:3000",
      reuseExistingServer: true,
      timeout: 120_000,
      env: {
        API_BASE_URL: "http://127.0.0.1:3001",
        PLAYWRIGHT_REPO_ROOT: repoRoot
      }
    }
  ]
});
