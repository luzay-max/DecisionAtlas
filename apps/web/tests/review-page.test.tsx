import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { ReviewPageContent } from "../components/review/review-page-content";
import * as api from "../lib/api";

vi.mock("../lib/api", async () => {
  const actual = await vi.importActual<typeof import("../lib/api")>("../lib/api");
  return {
    ...actual,
    reviewDecision: vi.fn(),
  };
});

describe("ReviewPageContent", () => {
  it("renders candidate review actions", () => {
    render(
      <ReviewPageContent
        workspaceSlug="demo-workspace"
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
    expect(screen.getByText(/This review queue is using seeded walkthrough decisions/i)).toBeInTheDocument();
    expect(screen.getByText(/Review the seeded candidate decisions/i)).toBeInTheDocument();
    expect(screen.getByText("0.88")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Accept" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Reject" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Supersede" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Use Redis Cache" })).toHaveAttribute(
      "href",
      "/decisions/1?workspace=demo-workspace"
    );
  });

  it("submits a review action and removes the candidate from the list", async () => {
    vi.mocked(api.reviewDecision).mockResolvedValue({
      id: 1,
      workspace_id: 1,
      title: "Use Redis Cache",
      status: "active",
      review_state: "accepted",
      problem: "Latency too high",
      context: "Read load increased",
      constraints: "Budget is limited",
      chosen_option: "Use Redis as cache only",
      tradeoffs: "Extra dependency",
      confidence: 0.88,
    });

    const user = userEvent.setup();
    render(
      <ReviewPageContent
        workspaceSlug="demo-workspace"
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

    await user.click(screen.getByRole("button", { name: "Accept" }));

    await waitFor(() =>
      expect(api.reviewDecision).toHaveBeenCalledWith(1, "accepted")
    );
    await waitFor(() => expect(screen.queryByText("Use Redis Cache")).not.toBeInTheDocument());
    expect(screen.getByText(/The seeded review step is complete/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /continue to why-search/i })).toHaveAttribute(
      "href",
      "/search?workspace=demo-workspace"
    );
  });

  it("explains sparse imported workspaces when no candidates exist", () => {
    render(<ReviewPageContent workspaceSlug="imported-workspace" decisions={[]} />);

    expect(
      screen.getByText(/imported repository did not contain enough high-signal decision evidence/i)
    ).toBeInTheDocument();
  });
});
