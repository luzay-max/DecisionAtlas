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
        mode: "full",
        owner_scope: "local-default",
        access_source_type: "github_app_installation",
        access_source_ref: "12345",
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

  it("proxies POST /imports/github/installations/bind", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      text: async () =>
        JSON.stringify({
          workspace_exists: true,
          workspace_slug: "github-org-repo",
          access_source_type: "github_app_installation",
          access_source_label: "GitHub App installation #12345"
        }),
      json: async () => ({
        workspace_exists: true,
        workspace_slug: "github-org-repo",
        access_source_type: "github_app_installation",
        access_source_label: "GitHub App installation #12345"
      })
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/imports/github/installations/bind",
      payload: {
        repo: "org/repo",
        installation_id: "12345",
        owner_scope: "local-default"
      }
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({
      workspace_exists: true,
      workspace_slug: "github-org-repo",
      access_source_type: "github_app_installation",
      access_source_label: "GitHub App installation #12345"
    });

    global.fetch = originalFetch;
  });

  it("proxies POST /imports/github/private-access/bind", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      text: async () =>
        JSON.stringify({
          workspace_exists: true,
          workspace_slug: "github-org-private-repo",
          access_source_type: "github_token",
          access_source_label: "Private GitHub source team private repo",
          access_source_status: "authorized"
        }),
      json: async () => ({
        workspace_exists: true,
        workspace_slug: "github-org-private-repo",
        access_source_type: "github_token",
        access_source_label: "Private GitHub source team private repo",
        access_source_status: "authorized"
      })
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/imports/github/private-access/bind",
      payload: {
        repo: "org/private-repo",
        token: "ghp-private-token",
        source_ref: "org/private-repo",
        source_label: "team private repo",
      }
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({
      workspace_exists: true,
      workspace_slug: "github-org-private-repo",
      access_source_type: "github_token",
      access_source_label: "Private GitHub source team private repo",
      access_source_status: "authorized"
    });

    global.fetch = originalFetch;
  });

  it("proxies POST /imports/github/webhook", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      text: async () =>
        JSON.stringify({
          status: "queued",
          workspace_slug: "github-org-repo",
          job_id: "job-webhook"
        }),
      json: async () => ({
        status: "queued",
        workspace_slug: "github-org-repo",
        job_id: "job-webhook"
      })
    } as Response);

    const app = buildServer();
    const response = await app.inject({
      method: "POST",
      url: "/imports/github/webhook",
      headers: {
        "x-github-event": "pull_request",
        "x-github-delivery": "delivery-1"
      },
      payload: {
        action: "opened",
        installation: { id: 12345 },
        repository: { full_name: "org/repo" }
      }
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({
      status: "queued",
      workspace_slug: "github-org-repo",
      job_id: "job-webhook"
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
