import { expect, test } from "@playwright/test";

// This is a real Web -> Next rewrite -> Fastify BFF -> FastAPI Engine check.
// All records are synthetic and inserted by seed_b02_b03_composition.py.
// Never run real repository capture, private data, or paid embedding providers.
const workspace = "ci-b02-b03-combined";
const chineseQuestion = "为什么使用 PostgreSQL 主库保证一致性？";

test("B02 Chinese Why runs through B03 same-origin HttpOnly cookie transport", async ({ page }) => {
  test.setTimeout(120_000);
  const leakedRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("127.0.0.1:3001")) {
      leakedRequests.push(request.url());
    }
  });

  await page.goto("/");
  const session = await page.request.get("/backend/auth/session");
  expect(session.status()).toBe(200);

  const browserCookies = await page.context().cookies();
  const authCookie = browserCookies.find((cookie) => cookie.name === "decisionatlas_session");
  expect(authCookie, "BFF must establish an HttpOnly session cookie on the Web origin").toBeTruthy();
  expect(authCookie?.httpOnly).toBe(true);
  expect(authCookie?.sameSite).toBe("Lax");

  const accepted = await page.evaluate(async ({ workspace, question }) => {
    const response = await fetch("/backend/query/why", {
      method: "POST",
      credentials: "same-origin",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ workspace_slug: workspace, question }),
    });
    return { status: response.status, body: await response.json() };
  }, { workspace, question: chineseQuestion });

  expect(accepted.status).toBe(200);
  expect(accepted.body.retrieval_mode).toBe("lexical_only");
  expect(accepted.body.answer_context?.retrieval_mode).toBe("lexical_only");
  expect(accepted.body.question).toBe(chineseQuestion);
  expect(JSON.stringify(accepted.body)).toContain("PostgreSQL");
  expect(accepted.body.primary_decision?.title).toBe("使用 PostgreSQL 主库");

  // A candidate-only Chinese term cannot become evidence just because
  // FakeEmbedder, session transport, or a cross-origin request is present.
  const negative = await page.evaluate(async (workspace) => {
    const response = await fetch("/backend/query/why", {
      method: "POST",
      credentials: "same-origin",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ workspace_slug: workspace, question: "火星电梯未审核" }),
    });
    return { status: response.status, body: await response.json() };
  }, workspace);
  expect(negative.status).toBe(200);
  expect(negative.body.retrieval_mode).toBe("lexical_only");
  expect(negative.body.primary_decision).toBeUndefined();
  expect(negative.body.citations).toEqual([]);

  const unsafeOrigin = await page.request.post("/backend/query/why", {
    headers: { origin: "https://attacker.invalid" },
    data: { workspace_slug: workspace, question: chineseQuestion },
  });
  expect(unsafeOrigin.status()).toBe(403);

  expect(await page.evaluate(() => window.localStorage.getItem("decisionatlas-session-token"))).toBeNull();
  expect(leakedRequests).toEqual([]);
});
