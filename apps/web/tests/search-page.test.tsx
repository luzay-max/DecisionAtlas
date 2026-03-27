import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { QueryForm } from "../components/search/query-form";

describe("QueryForm", () => {
  it("submits a question and renders citations", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        status: "ok",
        question: "why use redis cache",
        answer: "Use Redis Cache: Use Redis as cache only.",
        answer_context: {
          workspace_mode: "demo",
          source_summary: "This workspace is using seeded demo data for a guided product walkthrough."
        },
        primary_decision: {
          decision_id: 1,
          title: "Use Redis Cache"
        },
        supporting_context: [],
        citations: [
          {
            quote: "We decided to use Redis as cache",
            url: "https://github.com/org/repo/issues/1"
          }
        ]
      })
    } as Response);

    render(<QueryForm workspaceSlug="demo-workspace" />);
    expect(screen.getByRole("button", { name: "Try the demo question" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() => {
      expect(screen.getByText("Use Redis Cache: Use Redis as cache only.")).toBeInTheDocument();
    });
    expect(screen.getByText(/Workspace Type/i)).toBeInTheDocument();
    expect(screen.getByText(/Demo Workspace/i)).toBeInTheDocument();
    expect(screen.getByText("Status:")).toBeInTheDocument();
    expect(screen.getByText("We decided to use Redis as cache")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Continue to timeline" })).toHaveAttribute(
      "href",
      "/timeline?workspace=demo-workspace"
    );

    global.fetch = originalFetch;
  });

  it("renders a helpful error when why search fails", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      ok: false
    } as Response);

    render(<QueryForm workspaceSlug="demo-workspace" />);
    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() => {
      expect(screen.getByText(/why search is unavailable right now/i)).toBeInTheDocument();
    });

    global.fetch = originalFetch;
  });

  it("shows review-required next action for imported why responses", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        status: "review_required",
        question: "why use queue",
        answer: "Accepted imported decisions are required before why-search is trustworthy. Review candidate decisions first.",
        answer_context: {
          workspace_mode: "imported",
          source_summary: "Imported repository data from GitHub-backed analysis.",
          workspace_readiness: {
            state: "review_ready",
            next_action: "review_candidates",
            why_state: "review_required",
            drift_state: "review_required"
          }
        },
        supporting_context: [],
        citations: []
      })
    } as Response);

    render(<QueryForm workspaceSlug="imported-workspace" />);
    expect(screen.getByText(/imported why-search becomes trustworthy/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() => {
      expect(screen.getByText(/review required/i)).toBeInTheDocument();
    });
    expect(screen.getByRole("link", { name: "Review imported candidates" })).toHaveAttribute(
      "href",
      "/review?workspace=imported-workspace"
    );

    global.fetch = originalFetch;
  });

  it("does not crash when a legacy why response omits provenance context", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        status: "ok",
        question: "why use redis cache",
        answer: "Use Redis Cache: Use Redis as cache only.",
        supporting_context: [],
        citations: [
          {
            quote: "We decided to use Redis as cache",
            url: "https://github.com/org/repo/issues/1"
          }
        ]
      })
    } as Response);

    render(<QueryForm workspaceSlug="demo-workspace" />);
    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() => {
      expect(screen.getByText("Use Redis Cache: Use Redis as cache only.")).toBeInTheDocument();
    });
    expect(screen.queryByText(/Workspace Type/i)).not.toBeInTheDocument();

    global.fetch = originalFetch;
  });

  it("renders supporting context separately from the primary answer", async () => {
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        status: "ok",
        question: "why did we change the release process",
        answer: "Use GitHub App token for release candidate branch operations: Use a GitHub App token for release candidate branch operations. Tradeoffs: Requires separate app identity.",
        answer_context: {
          workspace_mode: "imported",
          source_summary: "Imported repository data from GitHub-backed analysis.",
          workspace_readiness: {
            state: "why_ready",
            next_action: "ask_why",
            why_state: "why_ready",
            drift_state: "clean"
          }
        },
        primary_decision: {
          decision_id: 10,
          title: "Use GitHub App token for release candidate branch operations"
        },
        supporting_context: [
          {
            decision_id: 11,
            title: "Remove prerelease tag manually when promoting GitHub releases to latest",
            answer: "Remove the prerelease tag during release promotion. Tradeoffs: Adds a manual or automated release step."
          }
        ],
        citations: [
          {
            quote: "Use a GitHub App identity when ensuring release candidate branches.",
            url: "https://github.com/org/repo/pull/10"
          },
          {
            quote: "Prerelease tags are not removed automatically when promoting releases to latest.",
            url: "https://github.com/org/repo/pull/11"
          }
        ]
      })
    } as Response);

    render(<QueryForm workspaceSlug="imported-workspace" initialQuestion="why did we change the release process" />);
    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() => {
      expect(screen.getByText(/Use GitHub App token for release candidate branch operations:/)).toBeInTheDocument();
    });
    expect(screen.getByText("Supporting context:")).toBeInTheDocument();
    expect(
      screen.getByText("Remove prerelease tag manually when promoting GitHub releases to latest")
    ).toBeInTheDocument();

    global.fetch = originalFetch;
  });
});
