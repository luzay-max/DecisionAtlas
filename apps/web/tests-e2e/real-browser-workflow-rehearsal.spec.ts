import { expect, test } from "@playwright/test";

const REAL_PUBLIC_REPO = "openai/openai-cookbook";
const REAL_PUBLIC_REPO_URL = `https://github.com/${REAL_PUBLIC_REPO}`;

function accountLabel(username: string): RegExp {
  const escaped = username.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`#\\d+ ${escaped}$`);
}

test("real browser human workflow rehearsal with explicit public repo context", async ({ page }) => {
  await page.route("**/imports/lookup?repo=**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        owner_scope: "local",
        repo: REAL_PUBLIC_REPO,
        repo_url: REAL_PUBLIC_REPO_URL,
        workspace_exists: false,
        workspace_slug: null,
        has_successful_import: false,
        can_incremental_sync: false,
        has_running_import: false,
        latest_import: null,
        provider: "github",
        access_mode: "public",
        setup_outcome: "ready",
        next_action: "import",
        access_source_type: "public",
        access_source_label: `Public GitHub rehearsal: ${REAL_PUBLIC_REPO}`,
        access_source_status: "authorized",
        access_requirement: null,
        access_requirement_detail:
          "Browser rehearsal uses a mocked lookup response; live import evidence remains covered by benchmark/readiness artifacts."
      })
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
        primary_decision: {
          decision_id: 1,
          title: "Use Redis Cache"
        },
        answer_context: {
          workspace_mode: "demo",
          source_summary: "This workspace is using seeded demo data for a guided product walkthrough."
        },
        citations: [
          {
            decision_id: 1,
            quote: "We decided to use Redis as cache only because latency mattered.",
            url: "https://github.com/org/repo/issues/1"
          }
        ]
      })
    });
  });

  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Engineering decision memory/i })).toBeVisible();
  await expect(page.getByRole("main").locator("#repository-import-flow").getByText("Repository import flow")).toBeVisible();

  await page.getByRole("link", { name: "Open import controls" }).click();
  await page.getByText("Advanced / Experimental").click();
  await page.locator("#advanced-controls").getByRole("textbox", { name: "Repository" }).first().fill(REAL_PUBLIC_REPO_URL);
  await expect(page.getByText(`Public GitHub rehearsal: ${REAL_PUBLIC_REPO}`)).toBeVisible();
  await expect(page.getByText(REAL_PUBLIC_REPO)).toBeVisible();
  await expect(page.getByText(/mocked lookup response/i)).toBeVisible();

  await page.getByRole("link", { name: /Start guided demo/i }).click();
  await expect(page).toHaveURL(/\/workspaces\/demo-workspace/);
  await expect(page.getByRole("heading", { name: "demo-workspace" })).toBeVisible();
  await expect(page.getByLabel("Active workspace context", { exact: true }).last()).toContainText("Workspace dashboard");
  await expect(page.getByRole("link", { name: /Review candidates/i }).first()).toBeVisible();
  await expect(page.getByRole("link", { name: /Ask why/i }).first()).toBeVisible();
  await expect(page.getByRole("link", { name: /Inspect drift/i }).first()).toBeVisible();
  await expect(page.getByRole("link", { name: /Evidence/i }).first()).toBeVisible();

  await page.locator(".global-sidebar").getByRole("link", { name: /Review$/ }).click();
  await expect(page).toHaveURL(/\/review\?workspace=demo-workspace/);
  await expect(page.getByLabel("Active workspace context", { exact: true }).last()).toContainText("Review queue");
  await expect(page.getByRole("heading", { name: /Candidate decisions waiting for review|All candidates reviewed/i })).toBeVisible();

  await page.getByRole("link", { name: "Why Search", exact: true }).click();
  await expect(page).toHaveURL(/\/search\?workspace=demo-workspace/);
  await expect(page.getByLabel("Active workspace context", { exact: true }).last()).toContainText("Why Search");
  await page.getByRole("button", { name: "Search" }).click();
  await expect(page.getByText("Use Redis Cache: Use Redis as cache only.")).toBeVisible();

  await page.getByRole("link", { name: "Drift", exact: true }).click();
  await expect(page).toHaveURL(/\/drift\?workspace=demo-workspace/);
  await expect(page.getByLabel("Active workspace context", { exact: true }).last()).toContainText("Drift monitoring");
  await expect(page.getByText(/possible[_ ]drift/i).first()).toBeVisible();

  await page.getByRole("link", { name: /Evidence/i }).first().click();
  await expect(page).toHaveURL(/\/evidence/);
  await expect(page.getByRole("heading", { name: "Evidence Dashboard" })).toBeVisible();
  await expect(page.getByText("Release evidence checklist")).toBeVisible();
  await expect(page.getByText("Benchmark comparison")).toBeVisible();

  const suffix = Date.now().toString(36);
  const reviewerUsername = `reviewer-${suffix}`;
  const viewerUsername = `viewer-${suffix}`;
  const password = `Pass-${suffix}-123`;

  await page.goto("/team");
  await expect(page.getByRole("heading", { name: "Accounts and workspace permissions" })).toBeVisible();
  await expect(page.getByText(/Current actor: local-admin/)).toBeVisible();

  await page.getByLabel("Username").fill(reviewerUsername);
  await page.getByLabel("Initial password").fill(password);
  await page.getByLabel("Scope role").selectOption("reviewer");
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page.getByText(accountLabel(reviewerUsername))).toBeVisible();

  await page.getByLabel("Username").fill(viewerUsername);
  await page.getByLabel("Initial password").fill(password);
  await page.getByLabel("Scope role").selectOption("viewer");
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page.getByText(accountLabel(viewerUsername))).toBeVisible();

  await page.goto("/login?next=/team");
  await page.getByLabel("Username").fill(reviewerUsername);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/team$/);
  await expect(page.getByLabel("Current account and owner scope").getByText(/Role: reviewer/)).toBeVisible();
  await expect(page.getByText("Admin role required for team account and workspace permission management.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Create account" })).toHaveCount(0);

  await page.goto("/login?next=/team");
  await page.getByLabel("Username").fill(viewerUsername);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/team$/);
  await expect(page.getByLabel("Current account and owner scope").getByText(/Role: viewer/)).toBeVisible();
  await expect(page.getByText("Admin role required for team account and workspace permission management.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Create account" })).toHaveCount(0);
});
