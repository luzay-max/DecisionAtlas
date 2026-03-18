import { expect, test } from "@playwright/test";

test("demo smoke flow", async ({ page }) => {
  await page.route("**/imports/github", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ job_id: "demo-job", imported_count: 2 })
    });
  });

  await page.route("**/query/why", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        status: "ok",
        question: "why use redis cache",
        answer: "Use Redis Cache: Use Redis as cache only.",
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
  await page.getByRole("button", { name: "Run Demo Import" }).click();
  await expect(page.getByText("Imported 2 artifacts")).toBeVisible();

  await page.goto("/review");
  await expect(page.getByText("Adopt Queue for Async Jobs")).toBeVisible();

  await page.goto("/search");
  await page.getByRole("button", { name: "Search" }).click();
  await expect(page.getByText("Use Redis Cache: Use Redis as cache only.")).toBeVisible();

  await page.goto("/drift");
  await expect(page.getByText("possible_drift")).toBeVisible();
});
