import { expect, test } from "@playwright/test";

test.describe("Homepage onboarding and navigation", () => {
  test("homepage shows onboarding guide and next steps", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("DecisionAtlas", { exact: true }).first()).toBeVisible();
    await expect(page.getByRole("heading", { name: /Engineering decision memory/i })).toBeVisible();
    await expect(page.getByText("Getting Started")).toBeVisible();
    await expect(page.getByText("1. Open the demo workspace")).toBeVisible();
    await expect(page.getByText("2. Review candidate decisions")).toBeVisible();
    await expect(page.getByText("3. Ask why")).toBeVisible();
    await expect(page.getByText("4. Check drift")).toBeVisible();
    await expect(page.getByText("Next Steps")).toBeVisible();
    await expect(page.getByRole("link", { name: /View settings/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /View evidence/i })).toBeVisible();
  });

  test("homepage quick actions navigate correctly", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("link", { name: /Jump to review/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Jump to why search/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Jump to drift/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Start guided demo/i })).toBeVisible();
  });
});

test.describe("Settings page", () => {
  test("settings page renders configuration sections", async ({ page }) => {
    await page.goto("/settings");
    await expect(page.getByRole("heading", { name: "Configuration" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "LLM Provider" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "System Status" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Database" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Cache & Queue" })).toBeVisible();
    await expect(page.getByText("http://localhost:8000")).toBeVisible();
    await expect(page.getByText("http://localhost:3001")).toBeVisible();
  });

  test("sidebar renders on settings page", async ({ page }) => {
    await page.goto("/settings");
    await expect(page.locator(".global-sidebar")).toBeVisible();
    await expect(page.locator(".sidebar-nav-link.active").filter({ hasText: "Settings" })).toBeVisible();
  });
});

test.describe("Evidence page", () => {
  test("evidence page renders with report commands", async ({ page }) => {
    await page.goto("/evidence");
    await expect(page.getByRole("heading", { name: "Evidence Dashboard" })).toBeVisible();
    await expect(page.getByText("Available Reports")).toBeVisible();
    await expect(page.getByText("Self-Hosted Package")).toBeVisible();
    await expect(page.getByText("agent_guardrail.py")).toBeVisible();
    await expect(page.getByText("collect_code_decision_audit_report.py")).toBeVisible();
  });
});

test.describe("Error boundaries", () => {
  test("404 page shows recovery suggestions", async ({ page }) => {
    await page.goto("/nonexistent-page");
    await expect(page.getByText("404")).toBeVisible();
    await expect(page.getByText("Page not found")).toBeVisible();
    await expect(page.getByText("You can try:")).toBeVisible();
    await expect(page.getByRole("link", { name: /Go home/i })).toBeVisible();
  });
});

test.describe("Demo workspace flow", () => {
  test("complete demo walkthrough with sidebar navigation", async ({ page }) => {
    await page.route("**/query/why", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          status: "ok",
          question: "why use redis cache",
          answer: "Use Redis Cache: Use Redis as cache only.",
          answer_context: {
            workspace_mode: "demo",
            source_summary: "This workspace is using seeded demo data for a guided product walkthrough."
          },
          citations: [
            {
              quote: "We decided to use Redis as cache only because latency mattered.",
              url: "https://github.com/org/repo/issues/1"
            }
          ]
        })
      });
    });

    await page.goto("/workspaces/demo-workspace");
    await expect(page.getByRole("heading", { name: "demo-workspace" })).toBeVisible();

    const sidebar = page.locator(".global-sidebar");
    await expect(sidebar).toBeVisible();
    await expect(sidebar.getByRole("link", { name: /Review/i })).toBeVisible();
    await expect(sidebar.getByRole("link", { name: /Why Search/i })).toBeVisible();
    await expect(sidebar.getByRole("link", { name: /Drift/i })).toBeVisible();

    await page.goto("/review?workspace=demo-workspace");
    await expect(page.getByRole("heading", { name: /Candidate decisions waiting for review|All candidates reviewed/i })).toBeVisible();

    await page.goto("/search?workspace=demo-workspace");
    await page.getByRole("button", { name: "Search" }).click();
    await expect(page.getByText("Use Redis Cache: Use Redis as cache only.")).toBeVisible();

    await page.goto("/drift?workspace=demo-workspace");
    await expect(page.getByText(/possible[_ ]drift/i)).toBeVisible();
  });
});

