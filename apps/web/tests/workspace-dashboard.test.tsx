import React from "react";
import { render, screen } from "@testing-library/react";

import { WorkspaceDashboardContent } from "../components/dashboard/workspace-dashboard-content";

describe("WorkspaceDashboardContent", () => {
  it("renders summary KPIs and alerts", () => {
    render(
      <WorkspaceDashboardContent
        summary={{
          workspace_slug: "demo-workspace",
          repo_url: "https://github.com/openai/openai-cookbook",
          github_repo: "openai/openai-cookbook",
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
    expect(screen.getByText("Demo repo: openai/openai-cookbook")).toBeInTheDocument();
    expect(screen.getByText("ready")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
    expect(screen.getByText("No alerts yet.")).toBeInTheDocument();
  });
});
