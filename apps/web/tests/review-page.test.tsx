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
    expect(screen.getByText(/0\.88.*High confidence candidate/i)).toBeInTheDocument();
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
    expect(screen.queryByText(/Accept the first well-supported imported candidate/i)).not.toBeInTheDocument();
  });

  it("renders imported review evidence and first-baseline guidance", () => {
    render(
      <ReviewPageContent
        workspaceSlug="github-org-repo"
        decisions={[
          {
            id: 7,
            workspace_id: 2,
            title: "Adopt HTTP downloads for remote browsers",
            status: "active",
            review_state: "candidate",
            problem: "Remote browser state was hard to track",
            context: "Imported PR analysis",
            constraints: null,
            chosen_option: "Use HTTP downloads with status tracking",
            tradeoffs: "More explicit lifecycle handling",
            confidence: 0.91,
            workspace_mode: "imported",
            source_summary: "Imported repository data from GitHub-backed analysis.",
            review_evidence: {
              state: "grounded",
              source_ref_count: 2,
              primary_artifact: {
                id: 3,
                type: "pr",
                title: "Remote browser downloads",
                repo: "org/repo",
                url: "https://github.com/org/repo/pull/3",
              },
              source_ref_preview: [
                {
                  id: 9,
                  artifact_id: 3,
                  span_start: 10,
                  span_end: 80,
                  quote: "Use HTTP downloads to expose active remote browser status.",
                  url: "https://github.com/org/repo/pull/3",
                  relevance_score: 0.92,
                },
              ],
            },
          },
        ]}
      />
    );

    expect(screen.getByText(/Accept the first well-supported imported candidate/i)).toBeInTheDocument();
    expect(screen.getByText("Multiple grounded source refs")).toBeInTheDocument();
    expect(
      screen.getByText((_, element) =>
        element?.textContent === "Multiple grounded source refs · 2 source refs"
      )
    ).toBeInTheDocument();
    expect(screen.getByText(/Use HTTP downloads to expose active remote browser status/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Remote browser downloads" })).toHaveAttribute(
      "href",
      "https://github.com/org/repo/pull/3"
    );
    expect(screen.getByRole("link", { name: "Open full decision detail" })).toHaveAttribute(
      "href",
      "/decisions/7?workspace=github-org-repo"
    );
  });

  it("shows imported downstream entry points after candidates are reviewed", async () => {
    vi.mocked(api.reviewDecision).mockResolvedValue({
      id: 7,
      workspace_id: 2,
      title: "Adopt HTTP downloads for remote browsers",
      status: "active",
      review_state: "accepted",
      problem: "Remote browser state was hard to track",
      context: "Imported PR analysis",
      constraints: null,
      chosen_option: "Use HTTP downloads with status tracking",
      tradeoffs: "More explicit lifecycle handling",
      confidence: 0.91,
    });

    const user = userEvent.setup();
    render(
      <ReviewPageContent
        workspaceSlug="github-org-repo"
        decisions={[
          {
            id: 7,
            workspace_id: 2,
            title: "Adopt HTTP downloads for remote browsers",
            status: "active",
            review_state: "candidate",
            problem: "Remote browser state was hard to track",
            context: null,
            constraints: null,
            chosen_option: "Use HTTP downloads with status tracking",
            tradeoffs: "More explicit lifecycle handling",
            confidence: 0.91,
          },
        ]}
      />
    );

    await user.click(screen.getByRole("button", { name: "Accept" }));

    await waitFor(() => expect(screen.queryByText("Adopt HTTP downloads for remote browsers")).not.toBeInTheDocument());
    expect(screen.getByText("Imported baseline established.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Ask why in this workspace" })).toHaveAttribute(
      "href",
      "/search?workspace=github-org-repo"
    );
    expect(screen.getByRole("link", { name: "Inspect drift" })).toHaveAttribute(
      "href",
      "/drift?workspace=github-org-repo"
    );
  });
});
