import React from "react";
import { render, screen } from "@testing-library/react";

import { TimelinePageContent } from "../components/timeline/timeline-page-content";

describe("TimelinePageContent", () => {
  it("renders accepted decisions in order", () => {
    render(
      <TimelinePageContent
        workspaceSlug="demo-workspace"
        timeline={{
          workspace_mode: "demo",
          source_summary: "This workspace is using seeded demo data for a guided product walkthrough.",
          items: [
            {
              id: 1,
              title: "Use Redis Cache",
              review_state: "accepted",
              status: "active",
              problem: "Latency too high",
              chosen_option: "Use Redis as cache only",
              tradeoffs: "Extra dependency",
              created_at: "2026-03-18T00:00:00",
            },
            {
              id: 2,
              title: "Keep PostgreSQL Primary",
              review_state: "accepted",
              status: "active",
              problem: "Need transactional consistency",
              chosen_option: "Use PostgreSQL as primary database",
              tradeoffs: "Operational cost",
              created_at: "2026-03-19T00:00:00",
            },
          ],
        }}
      />
    );

    const headings = screen.getAllByRole("heading", { level: 2 }).map((item) => item.textContent);
    expect(headings).toEqual(["Use Redis Cache", "Keep PostgreSQL Primary"]);
    expect(screen.getByText(/Workspace Type/i)).toBeInTheDocument();
    expect(screen.getByText(/Demo Workspace/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Use Redis Cache" })).toHaveAttribute(
      "href",
      "/decisions/1?workspace=demo-workspace"
    );
    expect(screen.getByText(/3\/18\/2026, 12:00/i)).toBeInTheDocument();
    expect(screen.getByText(/3\/19\/2026, 12:00/i)).toBeInTheDocument();
  });

  it("does not crash when a legacy timeline response is still an array", () => {
    render(
      <TimelinePageContent
        workspaceSlug="demo-workspace"
        timeline={[
          {
            id: 1,
            title: "Use Redis Cache",
            review_state: "accepted",
            status: "active",
            problem: "Latency too high",
            chosen_option: "Use Redis as cache only",
            tradeoffs: "Extra dependency",
            created_at: "2026-03-18T00:00:00",
          },
        ]}
      />
    );

    expect(screen.getByText("Use Redis Cache")).toBeInTheDocument();
    expect(screen.queryByText(/Workspace Type/i)).not.toBeInTheDocument();
  });
});
