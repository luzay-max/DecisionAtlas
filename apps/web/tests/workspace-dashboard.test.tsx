import React from "react";
import { render, screen } from "@testing-library/react";

import { WorkspaceDashboardContent } from "../app/workspaces/[slug]/page";

describe("WorkspaceDashboardContent", () => {
  it("renders summary KPIs and alerts", () => {
    render(
      <WorkspaceDashboardContent
        summary={{
          workspace_slug: "demo-workspace",
          import_status: "ready",
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
    expect(screen.getByText("ready")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
    expect(screen.getByText("No alerts yet.")).toBeInTheDocument();
  });
});
