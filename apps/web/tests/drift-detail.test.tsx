import React from "react";
import { render, screen } from "@testing-library/react";

import { AlertDetail } from "../components/drift/alert-detail";

describe("AlertDetail", () => {
  it("renders semantic context with confidence, decision, and artifact", () => {
    render(
      <AlertDetail
        alert={{
          id: 1,
          alert_type: "needs_review",
          summary: "Artifact 'Evaluate Redis alternatives' overlaps with accepted decision 'Use Redis Cache' and needs review.",
          status: "open",
          confidence_label: "low",
          created_at: "2026-03-18T10:00:00",
          decision: {
            id: 7,
            title: "Use Redis Cache",
            review_state: "accepted",
            chosen_option: "Use Redis as cache only",
          },
          artifact: {
            id: 12,
            type: "issue",
            title: "Evaluate Redis alternatives",
            url: "https://github.com/org/repo/issues/12",
          },
        }}
      />
    );

    expect(screen.getByText("low confidence")).toBeInTheDocument();
    expect(screen.getByText(/Matched decision:/)).toBeInTheDocument();
    expect(screen.getByText(/Chosen option: Use Redis as cache only/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Evaluate Redis alternatives" })).toBeInTheDocument();
  });
});
