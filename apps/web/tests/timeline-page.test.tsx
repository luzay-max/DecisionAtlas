import React from "react";
import { render, screen } from "@testing-library/react";

import { TimelinePageContent } from "../components/timeline/timeline-page-content";

describe("TimelinePageContent", () => {
  it("renders accepted decisions in order", () => {
    render(
      <TimelinePageContent
        workspaceSlug="demo-workspace"
        items={[
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
        ]}
      />
    );

    const headings = screen.getAllByRole("heading", { level: 2 }).map((item) => item.textContent);
    expect(headings).toEqual(["Use Redis Cache", "Keep PostgreSQL Primary"]);
    expect(screen.getByRole("link", { name: "Use Redis Cache" })).toHaveAttribute(
      "href",
      "/decisions/1?workspace=demo-workspace"
    );
  });
});
