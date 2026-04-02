import React from "react";
import { render, screen } from "@testing-library/react";

import { AlertDetail } from "../components/drift/alert-detail";

describe("AlertDetail", () => {
  it("renders semantic context with confidence, decision, and artifact", () => {
    render(
      <AlertDetail
        workspaceSlug="demo-workspace"
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

    expect(screen.getByText("needs review")).toBeInTheDocument();
    expect(
      screen.getByText(/the system is not claiming the accepted decision was replaced/i)
    ).toBeInTheDocument();
    expect(screen.getByText("low confidence")).toBeInTheDocument();
    expect(screen.getByText(/Matched decision:/)).toBeInTheDocument();
    expect(screen.getByText(/Chosen option: Use Redis as cache only/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Evaluate Redis alternatives" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Use Redis Cache" })).toHaveAttribute(
      "href",
      "/decisions/7?workspace=demo-workspace"
    );
  });

  it("renders grouped follow-up hint for condensed weak alerts", () => {
    render(
      <AlertDetail
        workspaceSlug="demo-workspace"
        alert={{
          id: 2,
          alert_type: "needs_review",
          summary:
            "Artifact 'Evaluate remote browser cookie transfer for HTTP downloads' and 2 related follow-up artifacts appear connected to accepted decision 'Enable HTTP-based downloads for remote browsers with agent status tracking'. Review whether this newer work only continues the prior choice or introduces a real decision change. Closest prior choice: Use HTTP-based downloads with remote browser status tracking.",
          status: "open",
          confidence_label: "low",
          created_at: "2026-03-18T10:00:00",
          decision: {
            id: 9,
            title: "Enable HTTP-based downloads for remote browsers with agent status tracking",
            review_state: "accepted",
            chosen_option: "Use HTTP-based downloads with remote browser status tracking.",
          },
          artifact: {
            id: 21,
            type: "pull_request",
            title: "Evaluate remote browser cookie transfer for HTTP downloads",
            url: "https://github.com/browser-use/browser-use/pull/3901",
          },
        }}
      />
    );

    expect(
      screen.getByText(/condenses several related implementation follow-ups into one review thread/i)
    ).toBeInTheDocument();
    expect(screen.getByText(/related follow-up artifacts/i)).toBeInTheDocument();
  });
});
