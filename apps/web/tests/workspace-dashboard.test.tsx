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
});
