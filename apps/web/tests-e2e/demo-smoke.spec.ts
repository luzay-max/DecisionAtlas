import { expect, test } from "@playwright/test";

test("demo smoke flow", async ({ page }) => {
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
  await expect(page.getByText("Guided Demo", { exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: /Review candidates|Ask why/ }).first()).toBeVisible();

  await page.goto("/review?workspace=demo-workspace");
  await expect(page.getByRole("heading", { name: /Candidate decisions waiting for review|All candidates reviewed/i })).toBeVisible();

  await page.goto("/search?workspace=demo-workspace");
  await page.getByRole("button", { name: "Search" }).click();
  await expect(page.getByText("Use Redis Cache: Use Redis as cache only.")).toBeVisible();

  await page.goto("/drift?workspace=demo-workspace");
  await expect(page.getByText(/possible[_ ]drift/i)).toBeVisible();
});
