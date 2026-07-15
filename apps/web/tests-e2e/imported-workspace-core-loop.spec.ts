import { expect, test } from "@playwright/test";

const REAL_PUBLIC_REPO = process.env.PLAYWRIGHT_REAL_PUBLIC_REPO ?? "pallets/flask";

test("imported workspace core loop browser rehearsal", async ({ page }) => {
  const apiBaseUrl = process.env.API_BASE_URL ?? "http://127.0.0.1:3001";
  const importResponse = await fetch(`${apiBaseUrl}/imports/github`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ repo: REAL_PUBLIC_REPO, mode: "full" })
  });
  const importText = await importResponse.text();
  expect(importResponse.ok, importText).toBeTruthy();
  const importBody = JSON.parse(importText);
  const workspaceSlug = importBody.workspace_slug;
  expect(workspaceSlug).toBeTruthy();

  await page.route("**/query/why", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        status: "review_required",
        question: "why is this imported workspace interesting",
        answer:
          "Imported workspace proof uses a real public GitHub repository reference. Live answer quality remains covered by benchmark evidence.",
        answer_context: {
          workspace_mode: "imported",
          source_summary:
            "Browser rehearsal uses a live workspace shell and mocked why-answer response for deterministic UI validation.",
          workspace_readiness: {
            state: "review_ready",
            next_action: "review_candidates",
            review_state: "review_ready",
            why_state: "review_required",
            drift_state: "unevaluated",
            recommended_actions: ["review_candidates", "evaluate_drift"]
          }
        },
        citations: [
          {
            quote: "Real public repository reference for imported workspace browser rehearsal.",
            url: `https://github.com/${REAL_PUBLIC_REPO}`
          }
        ]
      })
    });
  });

  await page.goto(`/workspaces/${encodeURIComponent(workspaceSlug)}`);
  await expect(page.getByLabel("Active workspace context")).toContainText("Workspace dashboard");
  await expect(page.getByRole("heading", { name: workspaceSlug })).toBeVisible();
  await expect(page.getByText('Repo: ' + REAL_PUBLIC_REPO, { exact: true })).toBeVisible();

  await page.getByRole("link", { name: /Review candidates/i }).first().click();
  await expect(page).toHaveURL(new RegExp(`/review\\?workspace=${workspaceSlug}`));
  await expect(page.getByLabel("Active workspace context")).toContainText("Review queue");

  await page.getByRole("link", { name: "Why Search", exact: true }).click();
  await expect(page).toHaveURL(new RegExp(`/search\\?workspace=${workspaceSlug}`));
  await expect(page.getByLabel("Active workspace context")).toContainText("Why Search");
  await page.getByRole("button", { name: "Search" }).click();
  await expect(page.getByText(/real public GitHub repository reference/i)).toBeVisible();
  const repositoryCitation = page.getByRole("link", {
    name: `https://github.com/${REAL_PUBLIC_REPO}`,
    exact: true
  });
  await expect(repositoryCitation).toBeVisible();
  await expect(repositoryCitation).toHaveAttribute("href", `https://github.com/${REAL_PUBLIC_REPO}`);

  await page.getByRole("link", { name: "Drift", exact: true }).click();
  await expect(page).toHaveURL(new RegExp(`/drift\\?workspace=${workspaceSlug}`));
  await expect(page.getByLabel("Active workspace context")).toContainText("Drift monitoring");

  await page.getByRole("link", { name: /Evidence/i }).first().click();
  await expect(page).toHaveURL(/\/evidence/);
  await expect(page.getByRole("heading", { name: "Evidence Dashboard" })).toBeVisible();
  await expect(page.getByText("Benchmark comparison")).toBeVisible();
});
