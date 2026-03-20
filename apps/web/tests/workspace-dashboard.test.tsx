import React from "react";
import { render, screen } from "@testing-library/react";

import { WorkspaceDashboardContent } from "../components/dashboard/workspace-dashboard-content";

describe("WorkspaceDashboardContent", () => {
  it("renders summary KPIs and alerts", () => {
    render(
      <WorkspaceDashboardContent
        summary={{
          workspace_slug: "demo-workspace",
          workspace_mode: "demo",
          source_summary: "This workspace is using seeded demo data for a guided product walkthrough.",
          repo_url: "https://github.com/encode/httpx",
          github_repo: "encode/httpx",
          import_status: "ready",
          latest_import: null,
          artifact_count: 12,
          decision_counts: {
            candidate: 2,
            accepted: 5,
            rejected: 0,
            superseded: 0,
          },
          recent_alerts: [],
        }}
      />
    );

    expect(screen.getByText("demo-workspace")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Run Demo Import" })).toBeInTheDocument();
    expect(screen.getByText("Demo repo: encode/httpx")).toBeInTheDocument();
    expect(screen.getByText(/Workspace Type/i)).toBeInTheDocument();
    expect(screen.getByText(/Demo Workspace/i)).toBeInTheDocument();
    expect(screen.getByText(/Data Source/i)).toBeInTheDocument();
    expect(screen.getByText(/Seeded demo data for a guided product walkthrough\./i)).toBeInTheDocument();
    expect(screen.getByText("ready")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
    expect(screen.getByText("No alerts yet.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Review candidates" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Ask why" })).toBeInTheDocument();
  });

  it("renders import transparency for imported workspaces with low signal", () => {
    render(
      <WorkspaceDashboardContent
        summary={{
          workspace_slug: "imported-workspace",
          workspace_mode: "imported",
          source_summary: "Imported repository data from GitHub-backed analysis.",
          repo_url: "https://github.com/org/repo",
          github_repo: "org/repo",
          import_status: "succeeded",
          latest_import: {
            job_id: "job-123",
            mode: "full",
            status: "succeeded",
            imported_count: 9,
            summary: {
              artifact_counts: { issue: 1, pr: 2, commit: 4, doc: 2 },
              document_summary: {
                selected: 3,
                imported: 2,
                skipped: {
                  outside_high_signal_paths: 4,
                  non_markdown: 8,
                  generated_or_vendor_path: 1,
                },
              },
            },
            error_message: null,
            started_at: null,
            finished_at: null,
          },
          artifact_count: 9,
          decision_counts: {
            candidate: 0,
            accepted: 1,
            rejected: 0,
            superseded: 0,
          },
          recent_alerts: [],
        }}
      />
    );

    expect(
      screen.getByText(/Imported 2 repository docs from 3 high-signal selections and skipped 13 files outside scope\./i)
    ).toBeInTheDocument();
    expect(screen.getByText(/limited high-signal evidence/i)).toBeInTheDocument();
  });
});
