import React from "react";
import { render, screen } from "@testing-library/react";

import { ReviewPageContent } from "../components/review/review-page-content";

describe("ReviewPageContent", () => {
  it("renders candidate review actions", () => {
    render(
      <ReviewPageContent
        decisions={[
          {
            id: 1,
            workspace_id: 1,
            title: "Use Redis Cache",
            status: "active",
            review_state: "candidate",
            problem: "Latency too high",
            context: "Read load increased",
            constraints: "Budget is limited",
            chosen_option: "Use Redis as cache only",
            tradeoffs: "Extra dependency",
            confidence: 0.88,
          },
        ]}
      />
    );

    expect(screen.getByText("Use Redis Cache")).toBeInTheDocument();
    expect(screen.getByText(/highest-confidence candidates appear first/i)).toBeInTheDocument();
    expect(screen.getByText("0.88")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Accept" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Reject" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Supersede" })).toBeInTheDocument();
  });
});
