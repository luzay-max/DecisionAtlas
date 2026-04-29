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
            candidate_quality: {
              label: "strong",
              summary: "Multiple grounded refs with previewable evidence, provenance, and source URL support.",
              source_ref_count: 2,
              previewable_source_ref_count: 1,
              has_primary_artifact: true,
              has_source_url: true,
              confidence_bucket: "high",
              reasons: [
                "multiple_source_refs",
                "previewable_quote",
                "artifact_provenance",
                "source_url_available",
                "high_confidence",
              ],
            },
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
    expect(screen.getByText("Strong candidate")).toBeInTheDocument();
    expect(screen.getByText(/Multiple grounded refs with previewable evidence/i)).toBeInTheDocument();
    expect(screen.getByText(/Multiple source refs.*Previewable quote.*Artifact provenance.*Source URL available/i)).toBeInTheDocument();
    expect(screen.getByText("Multiple grounded source refs")).toBeInTheDocument();
    expect(
      screen.getByText((_, element) =>
        element?.textContent === "Multiple grounded source refs · 2 source refs · 1 previewable refs"
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

  it("explains partial imported candidates with bounded missing-support reasons", () => {
    render(
      <ReviewPageContent
        workspaceSlug="github-org-repo"
        decisions={[
          {
            id: 9,
            workspace_id: 2,
            title: "Use worker queue",
            status: "active",
            review_state: "candidate",
            problem: "Long-running jobs block requests",
            context: null,
            constraints: null,
            chosen_option: "Move jobs to a queue",
            tradeoffs: "More operational moving parts",
            confidence: 0.9,
            candidate_quality: {
              label: "partial",
              summary: "Some grounding is available, but missing support keeps this below a strong baseline candidate.",
              source_ref_count: 1,
              previewable_source_ref_count: 1,
              has_primary_artifact: true,
              has_source_url: false,
              confidence_bucket: "high",
              reasons: ["single_source_ref", "previewable_quote", "artifact_provenance", "missing_source_url", "high_confidence"],
            },
            review_evidence: {
              state: "thin",
              source_ref_count: 1,
              primary_artifact: {
                id: 4,
                type: "issue",
                title: "Queue rollout",
                repo: "org/repo",
                url: null,
              },
              source_ref_preview: [
                {
                  id: 10,
                  artifact_id: 4,
                  span_start: 0,
                  span_end: 50,
                  quote: "Move long-running jobs to a queue before request handling.",
                  url: null,
                  relevance_score: 0.83,
                },
              ],
            },
          },
        ]}
      />
    );

    expect(screen.getByText("Partial candidate")).toBeInTheDocument();
    expect(screen.getByText(/below a strong baseline candidate/i)).toBeInTheDocument();
    expect(screen.getByText(/Single source ref.*Previewable quote.*Missing source URL.*High confidence/i)).toBeInTheDocument();
    expect(screen.getByText(/usable but incomplete candidate/i)).toBeInTheDocument();
  });

  it("labels thin imported candidates so they are not confused with strong baselines", () => {
    render(
      <ReviewPageContent
        workspaceSlug="github-org-repo"
        decisions={[
          {
            id: 8,
            workspace_id: 2,
            title: "Use background jobs",
            status: "active",
            review_state: "candidate",
            problem: "Async work is unclear",
            context: null,
            constraints: null,
            chosen_option: "Use background jobs",
            tradeoffs: "More moving parts",
            confidence: 0.95,
            candidate_quality: {
              label: "thin",
              summary: "Thin grounding or missing provenance; keep as diagnosable review input, not a strong baseline.",
              source_ref_count: 0,
              previewable_source_ref_count: 0,
              has_primary_artifact: false,
              has_source_url: false,
              confidence_bucket: "high",
              reasons: [
                "missing_source_refs",
                "missing_previewable_quote",
                "missing_artifact_provenance",
                "missing_source_url",
                "high_confidence",
              ],
            },
            review_evidence: {
              state: "missing",
              source_ref_count: 0,
              primary_artifact: null,
              source_ref_preview: [],
            },
          },
        ]}
      />
    );

    expect(screen.getByText("Thin candidate")).toBeInTheDocument();
    expect(screen.getByText(/Missing source refs.*Missing previewable quote.*Missing source URL.*High confidence/i)).toBeInTheDocument();
    expect(screen.getByText(/Treat this as a diagnostic candidate/i)).toBeInTheDocument();
    expect(screen.getByText((_, element) => element?.textContent === "No grounded source refs yet · 0 source refs · 0 previewable refs")).toBeInTheDocument();
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
