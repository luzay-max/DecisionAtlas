import React from "react";
import { render, screen } from "@testing-library/react";

import { DriftPageContent } from "../app/drift/page";

describe("DriftPageContent", () => {
  it("renders persisted alerts with decision and artifact context", () => {
    render(
      <DriftPageContent
        alerts={[
          {
            id: 1,
            alert_type: "possible_drift",
            summary: "Accepted decision 'Use Redis Cache' keeps Redis cache-only.",
            status: "open",
            created_at: "2026-03-18T10:00:00",
            decision: {
              id: 7,
              title: "Use Redis Cache",
              review_state: "accepted",
            },
            artifact: {
              id: 12,
              type: "pull_request",
              title: "Persist sessions in Redis",
              url: "https://github.com/org/repo/pull/2",
            },
          },
        ]}
      />
    );

    expect(screen.getByText("Possible decision drift")).toBeInTheDocument();
    expect(screen.getByText("Use Redis Cache")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Persist sessions in Redis" })).toBeInTheDocument();
  });
});
