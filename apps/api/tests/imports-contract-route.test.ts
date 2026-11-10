import { buildServer } from "../src/server";

describe("Imports generated Engine contract client", () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("preserves nullable lookup fields and uses the generated query operation", async () => {
    const target = {
      owner_scope: "local-default",
      provider: "github",
      access_mode: "public",
      repo: "org/repo",
      repo_url: "https://github.com/org/repo",
      workspace_exists: false,
      workspace_slug: null,
      has_successful_import: false,
      can_incremental_sync: false,
      has_running_import: false,
      latest_import: null,
      active_import: null,
      access_source_type: "public",
      access_source_label: "Public GitHub access",
      access_source_status: null,
      access_source_status_detail: null,
      access_requirement: null,
      access_requirement_detail: null,
    };
    global.fetch = vi.fn().mockResolvedValue(Response.json(target));
    const app = buildServer();
    try {
      const response = await app.inject({
        method: "GET",
        url: "/imports/lookup?repo=org/repo",
        headers: { cookie: "decisionatlas_session=admin-token" },
      });
      expect(response.statusCode).toBe(200);
      expect(response.json()).toEqual(target);
      expect(global.fetch).toHaveBeenCalledExactlyOnceWith(
        "http://localhost:8000/imports/lookup?repo=org%2Frepo",
        { headers: { "x-decisionatlas-session-token": "admin-token" } },
      );
    } finally {
      await app.close();
    }
  });

  it("keeps token binding request-only and preserves upstream status/body", async () => {
    const safeResponse = {
      owner_scope: "local-default",
      provider: "github",
      access_mode: "token",
      repo: "org/private-repo",
      repo_url: "https://github.com/org/private-repo",
      workspace_exists: true,
      workspace_slug: "github-org-private-repo",
      has_successful_import: false,
      can_incremental_sync: false,
      has_running_import: false,
      latest_import: null,
      active_import: null,
      access_source_type: "github_token",
      access_source_label: "Private GitHub source team private repo",
      access_source_status: "authorized",
      repo_private: true,
    };
    global.fetch = vi.fn().mockResolvedValue(Response.json(safeResponse));
    const app = buildServer();
    const secret = "ghp-contract-test-secret";
    try {
      const response = await app.inject({
        method: "POST",
        url: "/imports/github/private-access/bind",
        headers: { cookie: "decisionatlas_session=admin-token" },
        payload: { repo: "org/private-repo", token: secret },
      });
      expect(response.statusCode).toBe(200);
      expect(response.json()).toEqual(safeResponse);
      expect(JSON.stringify(response.json())).not.toContain(secret);
      expect(global.fetch).toHaveBeenCalledExactlyOnceWith(
        "http://localhost:8000/imports/github/private-access/bind",
        {
          method: "POST",
          headers: {
            "content-type": "application/json",
            "x-decisionatlas-session-token": "admin-token",
          },
          body: JSON.stringify({ repo: "org/private-repo", token: secret }),
        },
      );
    } finally {
      await app.close();
    }
  });

  it("keeps the default-disabled pause/resume response as an upstream 503", async () => {
    const payload = { detail: "Import pause/resume is disabled pending worker lifecycle validation" };
    global.fetch = vi.fn().mockResolvedValue(Response.json(payload, { status: 503 }));
    const app = buildServer();
    try {
      const response = await app.inject({
        method: "POST",
        url: "/imports/job-123/pause",
        headers: { cookie: "decisionatlas_session=admin-token" },
      });
      expect(response.statusCode).toBe(503);
      expect(response.json()).toEqual({ ...payload, code: "service_unavailable", message: payload.detail });
    } finally {
      await app.close();
    }
  });

  it.each([
    {
      name: "plain-text 200",
      status: 200,
      makeResponse: () => new Response("plain ok", { status: 200, headers: { "content-type": "text/plain" } }),
      expected: { message: "plain ok" },
    },
    {
      name: "empty 200",
      status: 200,
      makeResponse: () => new Response(null, { status: 200 }),
      expected: null,
    },
    {
      name: "JSON string 200",
      status: 200,
      makeResponse: () => Response.json("hello"),
      expected: "hello",
    },
    {
      name: "JSON object 200",
      status: 200,
      makeResponse: () => Response.json({ pause_resume: { enabled: false, reason_code: "worker_lifecycle_unverified" } }),
      expected: { pause_resume: { enabled: false, reason_code: "worker_lifecycle_unverified" } },
    },
    {
      name: "plain-text 403",
      status: 403,
      makeResponse: () => new Response("Forbidden", { status: 403, headers: { "content-type": "text/plain" } }),
      expected: { error: "Forbidden" },
    },
    {
      name: "empty 403",
      status: 403,
      makeResponse: () => new Response(null, { status: 403 }),
      expected: null,
    },
    {
      name: "JSON object 403",
      status: 403,
      makeResponse: () => Response.json({ detail: "Forbidden" }, { status: 403 }),
      expected: { detail: "Forbidden" },
    },
    {
      name: "JSON string 403",
      status: 403,
      makeResponse: () => Response.json("hello", { status: 403 }),
      expected: "hello",
    },
    {
      name: "JSON numeric-looking string 403",
      status: 403,
      makeResponse: () => Response.json("123", { status: 403 }),
      expected: "123",
    },
    {
      name: "JSON boolean-looking string 403",
      status: 403,
      makeResponse: () => Response.json("false", { status: 403 }),
      expected: "false",
    },
    {
      name: "JSON null-looking string 403",
      status: 403,
      makeResponse: () => Response.json("null", { status: 403 }),
      expected: "null",
    },
    {
      name: "JSON number 403",
      status: 403,
      makeResponse: () => Response.json(123, { status: 403 }),
      expected: 123,
    },
    {
      name: "JSON boolean 403",
      status: 403,
      makeResponse: () => Response.json(false, { status: 403 }),
      expected: false,
    },
    {
      name: "JSON null 403",
      status: 403,
      makeResponse: () => Response.json(null, { status: 403 }),
      expected: null,
    },
  ])("preserves upstream $name response semantics", async ({ status, makeResponse, expected }) => {
    global.fetch = vi.fn().mockResolvedValue(makeResponse());
    const app = buildServer();
    try {
      const response = await app.inject({
        method: "GET",
        url: "/imports/capabilities",
        headers: { cookie: "decisionatlas_session=admin-token" },
      });

      expect(response.statusCode).toBe(status);
      if (status < 400) {
        if (typeof expected === "string") {
          expect(response.body).toBe(expected);
        } else {
          expect(response.json()).toEqual(expected);
        }
      } else {
        const normalized = response.json();
        expect(normalized.code).toBe("forbidden");
        expect(typeof normalized.message).toBe("string");
        if (expected !== null && typeof expected === "object") {
          expect(normalized).toMatchObject(expected);
        } else if (expected !== null) {
          expect(normalized.detail).toEqual(expected);
        }
      }
    } finally {
      await app.close();
    }
  });


  it.each([200, 403])(
    "returns 502 without an unhandled rejection when an upstream %s body stream is interrupted",
    async (status) => {
      const unhandledRejections: unknown[] = [];
      const onUnhandledRejection = (reason: unknown) => {
        unhandledRejections.push(reason);
      };
      process.on("unhandledRejection", onUnhandledRejection);

      const interruptedResponse = new Response(
        new ReadableStream<Uint8Array>({
          start(controller) {
            controller.enqueue(new TextEncoder().encode('{"detail":'));
            controller.error(new Error("synthetic body interrupted"));
          },
        }),
        { status, headers: { "content-type": "application/json" } },
      );
      const healthyPayload = { capabilities: [] };
      global.fetch = vi.fn()
        .mockResolvedValueOnce(interruptedResponse)
        .mockResolvedValue(Response.json(healthyPayload));

      const app = buildServer();
      try {
        const failedResponse = await app.inject({
          method: "GET",
          url: "/imports/capabilities",
          headers: { cookie: "decisionatlas_session=admin-token" },
        });

        expect(failedResponse.statusCode).toBe(502);
        await new Promise<void>((resolve) => setImmediate(resolve));
        expect(unhandledRejections).toEqual([]);

        // A failed upstream stream must not take down the API process/server.
        const recoveredResponse = await app.inject({
          method: "GET",
          url: "/imports/capabilities",
          headers: { cookie: "decisionatlas_session=admin-token" },
        });
        expect(recoveredResponse.statusCode).toBe(200);
        expect(recoveredResponse.json()).toEqual(healthyPayload);
        expect(global.fetch).toHaveBeenCalledTimes(2);

        await new Promise<void>((resolve) => setImmediate(resolve));
        expect(unhandledRejections).toEqual([]);
      } finally {
        process.off("unhandledRejection", onUnhandledRejection);
        await app.close();
      }
    },
  );

});
