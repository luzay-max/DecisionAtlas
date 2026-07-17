import { expect, test } from "@playwright/test";

test("offline package shell stays local and exposes the core evidence flow", async ({ page }) => {
  const externalRequests: string[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (!['127.0.0.1', 'localhost'].includes(url.hostname)) {
      externalRequests.push(request.url());
    }
  });

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
          source_summary: "Offline shell proof uses only local seeded evidence."
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

  await page.goto("/review?workspace=demo-workspace");
  await expect(
    page.getByRole("heading", { name: /Candidate decisions waiting for review|All candidates reviewed/i })
  ).toBeVisible();

  await page.goto("/search?workspace=demo-workspace");
  await page.getByRole("button", { name: "Search" }).click();
  await expect(page.getByText("Use Redis Cache: Use Redis as cache only.")).toBeVisible();

  await page.goto("/drift?workspace=demo-workspace");
  await expect(page.getByText(/possible[_ ]drift/i).first()).toBeVisible();

  await page.getByRole("link", { name: /Evidence/i }).first().click();
  await expect(page.getByRole("heading", { name: "Evidence Dashboard" })).toBeVisible();
  expect(externalRequests).toEqual([]);
});
