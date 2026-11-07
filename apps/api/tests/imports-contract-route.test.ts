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
      expect(response.json()).toEqual(payload);
    } finally {
      await app.close();
    }
  });
});
