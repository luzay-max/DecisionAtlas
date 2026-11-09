import { buildServer } from "../src/server";
import { normalizeApiErrorPayload } from "../src/errors";

describe("normalized BFF API error contract", () => {
  it.each([
    [400, "invalid_request"],
    [401, "unauthenticated"],
    [403, "forbidden"],
    [404, "not_found"],
    [409, "conflict"],
    [422, "invalid_request"],
    [429, "request_rejected"],
    [500, "internal_error"],
    [502, "upstream_unavailable"],
    [503, "service_unavailable"],
    [504, "upstream_unavailable"],
  ] as const)("maps HTTP %s to %s without changing the status source", (status, code) => {
    const normalized = normalizeApiErrorPayload(status, { detail: "synthetic failure" });
    expect(normalized.code).toBe(code);
  });

  it("preserves legacy 4xx fields and derives a message from detail", () => {
    expect(normalizeApiErrorPayload(401, { detail: "Authentication required" })).toEqual({
      detail: "Authentication required",
      code: "unauthenticated",
      message: "Authentication required",
    });
  });

  it("preserves the explicit #36 disabled response as HTTP 503 with its safe reason", () => {
    const normalized = normalizeApiErrorPayload(503, {
      detail: "Import pause/resume is disabled pending worker lifecycle validation",
    });
    expect(normalized).toMatchObject({
      code: "service_unavailable",
      message: "Import pause/resume is disabled pending worker lifecycle validation",
      detail: "Import pause/resume is disabled pending worker lifecycle validation",
    });
  });

  it("wraps scalar error bodies in detail without double-parsing JSON strings", () => {
    expect(normalizeApiErrorPayload(403, '"123"')).toEqual({
      detail: "123",
      code: "forbidden",
      message: "123",
    });
  });

  it("redacts validation input and credential-shaped fields", () => {
    const normalized = normalizeApiErrorPayload(422, {
      detail: [
        { loc: ["body", "password"], msg: "invalid", type: "value_error", input: "plain-password" },
        { loc: ["header", "authorization"], msg: "invalid", token: "secret-token" },
      ],
    });
    expect(JSON.stringify(normalized)).not.toContain("plain-password");
    expect(JSON.stringify(normalized)).not.toContain("secret-token");
    expect(normalized.code).toBe("invalid_request");
    expect(normalized.detail).toEqual([
      { loc: ["body", "password"], msg: "invalid", type: "value_error" },
      { loc: ["header", "authorization"], msg: "invalid" },
    ]);
  });

  it.each([500, 502, 504])("does not expose internal exception details for HTTP %s", (status) => {
    const normalized = normalizeApiErrorPayload(status, {
      error: "Internal Error",
      detail: "database password=secret and stack trace",
    });
    expect(normalized.code).toBe(status === 500 ? "internal_error" : "upstream_unavailable");
    expect(JSON.stringify(normalized)).not.toContain("database password");
    expect(JSON.stringify(normalized)).not.toContain("stack trace");
    expect(typeof normalized.message).toBe("string");
  });

  it("adds a consistent error envelope to BFF-owned validation errors", async () => {
    const app = buildServer();
    try {
      const response = await app.inject({
        method: "POST",
        url: "/auth/login",
        payload: { username: "", password: "" },
      });
      expect(response.statusCode).toBe(400);
      expect(response.json()).toMatchObject({
        code: "invalid_request",
        message: "Invalid login payload",
        error: "Invalid login payload",
      });
      expect(response.json().issues).toBeDefined();
    } finally {
      await app.close();
    }
  });

  it("adds a consistent error envelope to unauthenticated Engine responses", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue(Response.json(
      { detail: "User account is disabled" },
      { status: 401 },
    ));
    const app = buildServer();
    try {
      const response = await app.inject({
        method: "GET",
        url: "/team/accounts",
        headers: { cookie: "decisionatlas_session=disabled-token" },
      });
      expect(response.statusCode).toBe(401);
      expect(response.json()).toMatchObject({
        code: "unauthenticated",
        message: "User account is disabled",
        detail: "User account is disabled",
      });
    } finally {
      global.fetch = originalFetch;
      await app.close();
    }
  });

  it("returns generic public transport errors while retaining the HTTP 502 status", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockRejectedValue(new Error("private socket path /secret"));
    const app = buildServer();
    try {
      const response = await app.inject({
        method: "GET",
        url: "/team/accounts",
        headers: { cookie: "decisionatlas_session=admin-token" },
      });
      expect(response.statusCode).toBe(502);
      expect(response.json()).toMatchObject({
        code: "upstream_unavailable",
        message: "Upstream engine unavailable",
        error: "Upstream engine request failed",
      });
      expect(response.body).not.toContain("/secret");
    } finally {
      global.fetch = originalFetch;
      await app.close();
    }
  });
});
