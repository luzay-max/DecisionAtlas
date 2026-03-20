import { buildServer } from "../src/server";

describe("POST /imports/github", () => {
  it("returns a job id from the engine", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => ({
        job_id: "job-123",
        mode: "full",
        status: "succeeded",
        imported_count: 5,
        summary: {
          artifact_counts: { issue: 1, pr: 1, commit: 2, doc: 1 },
          document_summary: {
            selected: 2,
            imported: 1,
            skipped: { outside_high_signal_paths: 4, non_markdown: 6, generated_or_vendor_path: 1 }
          }
        }
      })
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/imports/github",
      payload: {
        workspace_slug: "demo-workspace",
        repo: "org/repo",
        mode: "full"
      }
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({
      job_id: "job-123",
      mode: "full",
      status: "succeeded",
      imported_count: 5,
      summary: {
        artifact_counts: { issue: 1, pr: 1, commit: 2, doc: 1 },
        document_summary: {
          selected: 2,
          imported: 1,
          skipped: { outside_high_signal_paths: 4, non_markdown: 6, generated_or_vendor_path: 1 }
        }
      }
    });

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

  it("proxies GET /imports/:jobId", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => ({
        job_id: "job-123",
        status: "succeeded",
        imported_count: 8,
        summary: {
          artifact_counts: { issue: 1, pr: 2, commit: 3, doc: 2 },
          document_summary: {
            selected: 3,
            imported: 2,
            skipped: { outside_high_signal_paths: 4, non_markdown: 9, generated_or_vendor_path: 1 }
          }
        }
      })
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "GET",
      url: "/imports/job-123"
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({
      job_id: "job-123",
      status: "succeeded",
      imported_count: 8,
      summary: {
        artifact_counts: { issue: 1, pr: 2, commit: 3, doc: 2 },
        document_summary: {
          selected: 3,
          imported: 2,
          skipped: { outside_high_signal_paths: 4, non_markdown: 9, generated_or_vendor_path: 1 }
        }
      }
    });

    global.fetch = originalFetch;
  });
});
