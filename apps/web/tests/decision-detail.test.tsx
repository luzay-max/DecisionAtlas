import React from "react";
import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { DecisionCard } from "../components/decisions/decision-card";
import { DecisionDetailContent } from "../components/decisions/decision-detail-content";
import { SourceRefList } from "../components/decisions/source-ref-list";

vi.mock("../components/navigation/global-sidebar", () => ({
  GlobalSidebar: () => <nav data-testid="global-sidebar" />,
}));

describe("Decision detail components", () => {
  it("renders decision fields and source refs", () => {
    render(
      <>
        <DecisionCard
          decision={{
            id: 1,
            workspace_id: 1,
            workspace_mode: "demo",
            source_summary: "This workspace is using seeded demo data for a guided product walkthrough.",
            title: "Use Redis Cache",
            status: "active",
            review_state: "candidate",
            problem: "Latency too high",
            context: "Read load increased",
            constraints: "Budget is limited",
            chosen_option: "Use Redis as cache only",
            tradeoffs: "Extra dependency",
            confidence: 0.88,
            review_history: [
              {
                id: 10,
                owner_scope: "team-a",
                workspace_id: 1,
                actor_id: 1,
                actor_username: "reviewer@example.com",
                actor_role: "reviewer",
                target_type: "decision",
                target_id: 1,
                action: "decision_review_accepted",
                previous_state: { review_state: "candidate" },
                new_state: { review_state: "accepted" },
                rationale: "Source refs support this decision.",
                created_at: "2026-06-08T10:00:00",
              },
            ],
            source_refs: [
              {
                id: 1,
                artifact_id: 1,
                span_start: 0,
                span_end: 42,
                quote: "We decided to use Redis as a cache because latency mattered.",
                url: "https://github.com/org/repo/issues/1",
                relevance_score: 0.88,
              },
            ],
          }}
        />
        <SourceRefList
          sourceRefs={[
            {
              id: 1,
              artifact_id: 1,
              span_start: 0,
              span_end: 42,
              quote: "We decided to use Redis as a cache because latency mattered.",
              url: "https://github.com/org/repo/issues/1",
              relevance_score: 0.88,
            },
          ]}
        />
      </>
    );

    expect(screen.getByText("Use Redis Cache")).toBeInTheDocument();
    expect(screen.getByText(/Workspace Type/i)).toBeInTheDocument();
    expect(screen.getByText(/Demo Workspace/i)).toBeInTheDocument();
    expect(screen.getByText(/Latency too high/)).toBeInTheDocument();
    expect(screen.getByText("Review history")).toBeInTheDocument();
    expect(screen.getByText(/reviewer@example.com/)).toBeInTheDocument();
    expect(screen.getByText(/Source refs support this decision/)).toBeInTheDocument();
    expect(screen.getByText("Source References")).toBeInTheDocument();
    expect(screen.getByText("We decided to use Redis as a cache because latency mattered.")).toBeInTheDocument();
  });

  it("renders decision detail as a workspace-centered object hub", () => {
    render(
      <DecisionDetailContent
        workspaceSlug="demo-workspace"
        decision={{
          id: 1,
          workspace_id: 1,
          workspace_mode: "demo",
          source_summary: "This workspace is using seeded demo data for a guided product walkthrough.",
          title: "Use Redis Cache",
          status: "active",
          review_state: "candidate",
          problem: "Latency too high",
          context: "Read load increased",
          constraints: "Budget is limited",
          chosen_option: "Use Redis as cache only",
          tradeoffs: "Extra dependency",
          confidence: 0.88,
          source_refs: [
            {
              id: 1,
              artifact_id: 1,
              span_start: 0,
              span_end: 42,
              quote: "We decided to use Redis as a cache because latency mattered.",
              url: "https://github.com/org/repo/issues/1",
              relevance_score: 0.88,
            },
          ],
        }}
      />
    );

    expect(screen.getByText("Active workspace")).toBeInTheDocument();
    expect(screen.getByText(/Decision detail/)).toBeInTheDocument();
    expect(screen.getByText("Decision next actions")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Back to dashboard" })).toHaveAttribute(
      "href",
      "/workspaces/demo-workspace"
    );
    expect(screen.getByRole("link", { name: "Continue review" })).toHaveAttribute(
      "href",
      "/review?workspace=demo-workspace"
    );
  });
});
