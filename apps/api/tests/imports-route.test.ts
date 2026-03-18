import { buildServer } from "../src/server";

describe("POST /imports/github", () => {
  it("returns a job id from the engine", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => ({ job_id: "job-123", imported_count: 5 })
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/imports/github",
      payload: {
        workspace_slug: "demo-workspace",
        repo: "org/repo"
      }
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({ job_id: "job-123", imported_count: 5 });

    global.fetch = originalFetch;
  });

  it("rejects an invalid payload", async () => {
    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/imports/github",
      payload: {
        workspace_slug: "",
        repo: ""
      }
    });

    expect(response.statusCode).toBe(400);
    expect(response.json()).toHaveProperty("error", "Invalid request payload");
  });
});
