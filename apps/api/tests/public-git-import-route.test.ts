import { buildServer } from "../src/server";

describe("POST /imports/git-sources/import", () => {
  it("only proxies strict public GitLab/Gitee import requests", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      text: async () => JSON.stringify({
        job_id: "import-123", repo: "group/project",
        workspace_slug: "gitlab-group-project", status: "queued"
      })
    } as Response);

    try {
      const app = buildServer();
      const response = await app.inject({
        method: "POST",
        url: "/imports/git-sources/import",
        payload: { provider: "gitlab", repo: "group/project", mode: "full" },
      });
      expect(response.statusCode).toBe(200);
      expect(response.json().job_id).toBe("import-123");
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/imports/git-sources/import",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ provider: "gitlab", repo: "group/project", mode: "full" }),
        })
      );
      const rejected = await app.inject({
        method: "POST",
        url: "/imports/git-sources/import",
        payload: { provider: "gitee", repo: "group/project", token: "should-not-pass" },
      });
      expect(rejected.statusCode).toBe(400);
      expect(global.fetch).toHaveBeenCalledTimes(1);
      await app.close();
    } finally {
      global.fetch = originalFetch;
    }
  });

  it("does not accept an unrecognized provider", async () => {
    const app = buildServer();
    try {
      const response = await app.inject({
        method: "POST",
        url: "/imports/git-sources/import",
        payload: { provider: "local", repo: "group/project" },
      });
      expect(response.statusCode).toBe(400);
    } finally {
      await app.close();
    }
  });
});
