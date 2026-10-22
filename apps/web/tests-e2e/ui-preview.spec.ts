import { expect, test } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

// Only capture the CI's seeded public demo. Never screenshot private workspaces,
// tokens, setup secrets, or individual user account management pages.
const previewDir = path.resolve(__dirname, "../test-results/ui-preview");

test("capture real demo UI screenshots in Chinese (desktop, mobile, dark and light)", async ({ page }) => {
  test.setTimeout(120_000);
  await mkdir(previewDir, { recursive: true });
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.addInitScript(() => {
    window.localStorage.setItem("decisionatlas-language", "zh");
    window.localStorage.setItem("decisionatlas-theme", "dark");
  });

  async function capture(filename: string) {
    // Ensure hydration, locale and fonts have settled before capturing UI.
    await expect(page.locator("html")).toHaveAttribute("lang", "zh");
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({
      path: path.join(previewDir, filename),
      fullPage: true,
      animations: "disabled",
    });
  }

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "带引用的工程决策记忆。" })).toBeVisible();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await capture("01-home-desktop-dark-zh.png");

  await page.goto("/workspaces/demo-workspace");
  await expect(page.getByRole("heading", { name: "demo-workspace", exact: true })).toBeVisible();
  await capture("02-workspace-desktop-dark-zh.png");

  await page.goto("/review?workspace=demo-workspace");
  await expect(page.getByRole("heading", { name: "等待审阅的候选决策" })).toBeVisible();
  await capture("03-review-desktop-dark-zh.png");

  await page.goto("/search?workspace=demo-workspace");
  await expect(page.getByRole("heading", { name: "询问某个决策为什么这样做" })).toBeVisible();
  await capture("04-why-search-desktop-dark-zh.png");

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "带引用的工程决策记忆。" })).toBeVisible();
  await page.getByRole("button", { name: "深色模式" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await capture("05-home-desktop-light-zh.png");

  await page.getByRole("button", { name: "浅色模式" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.getByRole("heading", { name: "带引用的工程决策记忆。" })).toBeVisible();
  const hasOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth + 1
  );
  expect(hasOverflow).toBe(false);
  await capture("06-home-mobile-dark-zh.png");
});
