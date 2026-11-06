import { expect, test } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

// The data comes exclusively from scripts/ci/seed_smoke_demo.py. This suite
// must never exercise an actual private/public repo import or user review.
const workspaceSlug = "ci-evidence-preview";
const candidateTitle = "CI SYNTHETIC: Cache proposal (NOT VERIFIED)";
const previewDir = path.resolve(__dirname, "../test-results/ui-preview");

test("synthetic imported-style evidence renders via real API on desktop and mobile", async ({ page }) => {
  test.setTimeout(120_000);
  await mkdir(previewDir, { recursive: true });
  await page.addInitScript(() => {
    window.localStorage.setItem("decisionatlas-language", "zh");
    window.localStorage.setItem("decisionatlas-theme", "dark");
  });

  const reviewUrl = "/review?workspace=" + encodeURIComponent(workspaceSlug);

  async function ensureNoHorizontalOverflow(label: string) {
    const hasOverflow = await page.evaluate(
      () => document.documentElement.scrollWidth > window.innerWidth + 1
    );
    expect(hasOverflow, "Unexpected horizontal overflow on " + label).toBe(false);
  }

  async function screenshot(fileName: string) {
    await expect(page.locator("html")).toHaveAttribute("lang", "zh");
    await page.evaluate(async () => { await document.fonts.ready; });
    await page.screenshot({
      path: path.join(previewDir, fileName),
      fullPage: true,
      animations: "disabled",
    });
  }

  async function inspectReviewQueue() {
    await page.goto(reviewUrl);
    try {
      // The server first renders in English; the language provider then reads
      // the synthetic test's localStorage preference during hydration. Wait
      // for that separate readiness condition before asserting Chinese copy.
      await expect(page.locator("html")).toHaveAttribute("lang", "zh", { timeout: 10_000 });
      await expect(page.getByRole("heading", { name: "等待审阅的候选决策" })).toBeVisible();
    } catch (error) {
      // Diagnostic metadata only: never dump the full DOM, cookies, tokens,
      // response bodies, or any imported source text into CI logs/artifacts.
      const readiness = await page.evaluate(() => {
        const headings = Array.from(document.querySelectorAll("h1, h2"));
        return {
          htmlLanguage: document.documentElement.lang,
          storedLanguage: localStorage.getItem("decisionatlas-language"),
          chineseReviewHeading: headings.some(
            (heading) => heading.textContent?.trim() === "等待审阅的候选决策"
          ),
          englishReviewHeading: headings.some(
            (heading) => heading.textContent?.trim() === "Candidate decisions waiting for review"
          ),
          scopedUnavailable: Array.from(document.querySelectorAll("p.eyebrow")).some(
            (element) => element.textContent?.trim() === "Workspace unavailable in current scope"
          ),
          headingCount: headings.length,
          candidateLinkPresent: Array.from(document.querySelectorAll("a")).some(
            (link) => link.textContent?.trim() === "CI SYNTHETIC: Cache proposal (NOT VERIFIED)"
          ),
        };
      }).catch(() => ({ browserEvaluationFailed: true }));
      const diagnostics = { route: new URL(page.url()).pathname, ...readiness };
      await test.info().attach("synthetic-review-readiness", {
        body: JSON.stringify(diagnostics, null, 2),
        contentType: "application/json",
      });
      console.warn("Synthetic review readiness failure:", JSON.stringify(diagnostics));
      throw error;
    }
    await expect(page.getByRole("link", { name: candidateTitle })).toBeVisible();
    const evidence = page.locator(".evidence-review-panel-compact");
    await expect(evidence).toBeVisible();
    await expect(evidence.getByText("仅检查已存元数据")).toBeVisible();
    await expect(evidence.getByText("下方引用和链接预览来自已导入的元数据，本页面尚未对它们进行独立核验。")).toBeVisible();
    await expect(evidence.getByText("本界面尚未记录独立人工审核。")).toBeVisible();
    await expect(evidence.getByText("2 条来源引用")).toBeVisible();
    await expect(page.getByRole("button", { name: "接受" })).toBeVisible();
    return page.getByRole("link", { name: candidateTitle }).getAttribute("href");
  }

  async function inspectDecisionDetail(href: string) {
    await page.goto(href);
    await expect(page.getByRole("heading", { name: candidateTitle })).toBeVisible();
    const evidence = page.locator(".evidence-review-panel");
    await expect(evidence).toBeVisible();
    await expect(evidence.getByRole("heading", { name: "引用来源" })).toBeVisible();
    await expect(evidence.getByText("已保存引用")).toBeVisible();
    await expect(evidence.getByText("缺少引用原文")).toBeVisible();
    await expect(evidence.getByText("未记录区间")).toBeVisible();
    await expect(evidence.getByText("We propose caching repeated reads to reduce latency.")).toBeVisible();
    await expect(evidence.getByRole("link", { name: /打开原始来源/ })).toHaveAttribute(
      "href",
      "https://github.com/example/ci-evidence-preview/blob/main/docs/fictional-adr.md"
    );
    await expect(evidence.getByText(/本页面不会重新获取或核验上游原文/)).toBeVisible();
  }

  await page.setViewportSize({ width: 1440, height: 900 });
  const detailHref = await inspectReviewQueue();
  expect(detailHref).toMatch(/^\/decisions\/\d+\?workspace=ci-evidence-preview$/);
  await screenshot("09-synthetic-import-review-desktop-dark-zh.png");
  await inspectDecisionDetail(detailHref!);
  await screenshot("10-synthetic-import-detail-desktop-dark-zh.png");

  await page.setViewportSize({ width: 390, height: 844 });
  await inspectReviewQueue();
  await ensureNoHorizontalOverflow("synthetic import review on mobile");
  await screenshot("11-synthetic-import-review-mobile-dark-zh.png");
  await inspectDecisionDetail(detailHref!);
  await ensureNoHorizontalOverflow("synthetic import detail on mobile");
  await screenshot("12-synthetic-import-detail-mobile-dark-zh.png");
});
