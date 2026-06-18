import { expect, test } from "@playwright/test";

function accountLabel(username: string): RegExp {
  const escaped = username.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`#\\d+ ${escaped}$`);
}

test("self-hosted team workflow rehearsal", async ({ page }) => {
  const suffix = Date.now().toString(36);
  const reviewerUsername = `reviewer-${suffix}`;
  const viewerUsername = `viewer-${suffix}`;
  const password = `Pass-${suffix}-123`;

  await page.goto("/team");
  await expect(page.getByRole("heading", { name: "Accounts and workspace permissions" })).toBeVisible();
  await expect(page.getByText(/Current actor: local-admin/)).toBeVisible();
  await expect(page.getByRole("button", { name: "Create account" })).toBeVisible();

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
