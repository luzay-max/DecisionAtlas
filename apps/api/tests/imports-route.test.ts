import { buildServer } from "../src/server";

describe("POST /imports/github", () => {
  it("proxies GET /imports/lookup", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      text: async () =>
        JSON.stringify({
          repo: "org/repo",
          repo_url: "https://github.com/org/repo",
          workspace_exists: true,
          workspace_slug: "github-org-repo",
          has_successful_import: true,
          can_incremental_sync: true,
          has_running_import: false,
          latest_import: {
            job_id: "job-old",
            workspace_slug: "github-org-repo",
            repo: "org/repo",
            mode: "full",
            status: "succeeded",
            imported_count: 5
          }
        }),
      json: async () => ({
        repo: "org/repo",
        repo_url: "https://github.com/org/repo",
        workspace_exists: true,
        workspace_slug: "github-org-repo",
        has_successful_import: true,
        can_incremental_sync: true,
        has_running_import: false,
        latest_import: {
          job_id: "job-old",
          workspace_slug: "github-org-repo",
          repo: "org/repo",
          mode: "full",
          status: "succeeded",
          imported_count: 5
        }
      })
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "GET",
      url: "/imports/lookup?repo=org%2Frepo"
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({
      repo: "org/repo",
      repo_url: "https://github.com/org/repo",
      workspace_exists: true,
      workspace_slug: "github-org-repo",
      has_successful_import: true,
      can_incremental_sync: true,
      has_running_import: false,
      latest_import: {
        job_id: "job-old",
        workspace_slug: "github-org-repo",
        repo: "org/repo",
        mode: "full",
        status: "succeeded",
        imported_count: 5
      }
    });

    global.fetch = originalFetch;
  });

  it("returns a job id from the engine", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      text: async () =>
        JSON.stringify({
          job_id: "job-123",
          workspace_slug: "demo-workspace",
          mode: "full",
          status: "succeeded",
          imported_count: 5,
          summary: {
            stage: "completed",
            outcome: "ok",
            artifact_counts: { issue: 1, pr: 1, commit: 2, doc: 1 },
            document_summary: {
              selected: 2,
              imported: 1,
              skipped: { outside_high_signal_paths: 4, non_markdown: 6, generated_or_vendor_path: 1 }
            }
          }
        }),
      json: async () => ({
        job_id: "job-123",
        workspace_slug: "demo-workspace",
        mode: "full",
        status: "succeeded",
        imported_count: 5,
        summary: {
          stage: "completed",
          outcome: "ok",
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
      workspace_slug: "demo-workspace",
      mode: "full",
      status: "succeeded",
      imported_count: 5,
      summary: {
        stage: "completed",
        outcome: "ok",
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
      ok: true,
      text: async () =>
        JSON.stringify({
          job_id: "job-123",
          workspace_slug: "imported-workspace",
          status: "succeeded",
          imported_count: 8,
          summary: {
            stage: "completed",
            outcome: "insufficient_evidence",
            artifact_counts: { issue: 1, pr: 2, commit: 3, doc: 2 },
            document_summary: {
              selected: 3,
              imported: 2,
              skipped: { outside_high_signal_paths: 4, non_markdown: 9, generated_or_vendor_path: 1 }
            }
          }
        }),
      json: async () => ({
        job_id: "job-123",
        workspace_slug: "imported-workspace",
        status: "succeeded",
        imported_count: 8,
        summary: {
          stage: "completed",
          outcome: "insufficient_evidence",
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
      workspace_slug: "imported-workspace",
      status: "succeeded",
      imported_count: 8,
      summary: {
        stage: "completed",
        outcome: "insufficient_evidence",
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

  it("returns 502 when the engine request itself fails", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockRejectedValue(new Error("connect ECONNREFUSED"));

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

    expect(response.statusCode).toBe(502);
    expect(response.json()).toEqual({
      error: "Upstream engine request failed",
      detail: "connect ECONNREFUSED"
    });

    global.fetch = originalFetch;
  });
});
