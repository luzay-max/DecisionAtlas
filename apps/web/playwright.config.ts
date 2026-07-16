import { defineConfig } from "@playwright/test";
import path from "node:path";

const repoRoot = path.resolve(__dirname, "../..");
const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:3000";
const skipWebServer = process.env.PLAYWRIGHT_SKIP_WEBSERVER === "1";
const reuseExistingServer = process.env.PLAYWRIGHT_REUSE_EXISTING_SERVER === "1";
const browserChannel = process.env.PLAYWRIGHT_BROWSER_CHANNEL || undefined;
const requestedSlowMo = Number.parseInt(process.env.PLAYWRIGHT_SLOW_MO ?? "0", 10);
const slowMo = Number.isFinite(requestedSlowMo) && requestedSlowMo > 0 ? requestedSlowMo : undefined;
const noProxy = Array.from(
  new Set(
    [process.env.NO_PROXY, process.env.no_proxy, "127.0.0.1", "localhost"]
      .flatMap((value) => value?.split(",") ?? [])
      .map((value) => value.trim())
      .filter(Boolean)
  )
).join(",");
process.env.NO_PROXY = noProxy;
process.env.no_proxy = noProxy;

export default defineConfig({
  testDir: "./tests-e2e",
  timeout: 60_000,
  workers: 1,
  use: {
    baseURL,
    channel: browserChannel,
    launchOptions: slowMo ? { slowMo } : undefined
  },
  webServer: skipWebServer ? undefined : [
    {
      command: "powershell -ExecutionPolicy Bypass -File ../../scripts/ci/start-engine-smoke.ps1",
      cwd: __dirname,
      url: "http://127.0.0.1:8000/health",
      reuseExistingServer,
      timeout: 120_000
    },
    {
      command: "powershell -ExecutionPolicy Bypass -File ../../scripts/ci/start-api-smoke.ps1",
      cwd: __dirname,
      url: "http://127.0.0.1:3001/health",
      reuseExistingServer,
      timeout: 120_000
    },
    {
      command: "powershell -ExecutionPolicy Bypass -File ../../scripts/ci/start-web-smoke.ps1",
      cwd: __dirname,
      url: "http://127.0.0.1:3000",
      reuseExistingServer,
      timeout: 120_000,
      env: {
        API_BASE_URL: "http://127.0.0.1:3001",
        PLAYWRIGHT_REPO_ROOT: repoRoot
      }
    }
  ]
});
