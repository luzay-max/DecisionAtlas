import { buildServer } from "../src/server";

describe("B02+B03 composed BFF Why contract and cookie/Origin trust", () => {
  const oldFetch = global.fetch;
  const oldAppEnv = process.env.APP_ENV;
  const oldOrigins = process.env.CORS_ALLOWED_ORIGINS;
  const oldEngineBaseUrl = process.env.ENGINE_BASE_URL;

  beforeEach(() => {
    process.env.ENGINE_BASE_URL = "http://localhost:8000";
  });

  afterEach(() => {
    global.fetch = oldFetch;
    if (oldAppEnv === undefined) delete process.env.APP_ENV;
    else process.env.APP_ENV = oldAppEnv;
    if (oldOrigins === undefined) delete process.env.CORS_ALLOWED_ORIGINS;
    else process.env.CORS_ALLOWED_ORIGINS = oldOrigins;
    if (oldEngineBaseUrl === undefined) delete process.env.ENGINE_BASE_URL;
    else process.env.ENGINE_BASE_URL = oldEngineBaseUrl;
  });

  it("forwards a Chinese mixed-language Why request with validated cookie and preserves fallback mode", async () => {
    process.env.APP_ENV = "production";
    process.env.CORS_ALLOWED_ORIGINS = "https://atlas.example";
    const question = "为什么使用 PostgreSQL 主库保证一致性？";
    const payload = {
      status: "evidence_limited",
      question,
      answer: "CI synthetic support only",
      retrieval_mode: "lexical_fallback",
      answer_context: {
        workspace_mode: "demo",
        source_summary: "synthetic",
        retrieval_mode: "lexical_fallback",
      },
      citations: [],
    };
    global.fetch = vi.fn().mockResolvedValue(Response.json(payload));

    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/query/why",
      headers: {
        origin: "https://atlas.example",
        cookie: "decisionatlas_session=valid%2Dcookie",
        "x-decisionatlas-session-token": "forged-browser-header",
      },
      payload: { workspace_slug: "ci-b02-b03-combined", question },
    });
    expect(response.statusCode).toBe(200);
    expect(response.json()).toMatchObject({
      question,
      retrieval_mode: "lexical_fallback",
      answer_context: { retrieval_mode: "lexical_fallback" },
    });
    expect(global.fetch).toHaveBeenCalledTimes(1);
    const upstreamRequest = vi.mocked(global.fetch).mock.calls[0][0] as Request;
    expect(upstreamRequest.url).toBe("http://localhost:8000/query/why");
    expect(upstreamRequest.method).toBe("POST");
    expect(upstreamRequest.headers.get("content-type")).toBe("application/json");
    expect(upstreamRequest.headers.get("x-decisionatlas-session-token")).toBe("valid-cookie");
    expect(await upstreamRequest.json()).toEqual({ workspace_slug: "ci-b02-b03-combined", question });
    await app.close();
  });

  it("blocks a hostile Origin even when the Cookie is valid", async () => {
    process.env.APP_ENV = "production";
    process.env.CORS_ALLOWED_ORIGINS = "https://atlas.example";
    global.fetch = vi.fn();
    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/query/why",
      headers: {
        origin: "https://attacker.example",
        cookie: "decisionatlas_session=valid-cookie",
      },
      payload: {
        workspace_slug: "ci-b02-b03-combined",
        question: "为什么使用 PostgreSQL 主库？",
      },
    });
    expect(response.statusCode).toBe(403);
    expect(global.fetch).not.toHaveBeenCalled();
    await app.close();
  });

  it("does not forward a duplicate session cookie even when the Why mode is supported", async () => {
    process.env.APP_ENV = "test";
    global.fetch = vi.fn().mockResolvedValue(Response.json({ detail: "Authentication required" }, { status: 401 }));
    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/query/why",
      headers: { cookie: "decisionatlas_session=old; decisionatlas_session=new" },
      payload: {
        workspace_slug: "ci-b02-b03-combined",
        question: "PostgreSQL 主库",
      },
    });
    expect(response.statusCode).toBe(401);
    const upstreamRequest = vi.mocked(global.fetch).mock.calls[0][0] as Request;
    expect(upstreamRequest.headers.has("x-decisionatlas-session-token")).toBe(false);
    await app.close();
  });
});
