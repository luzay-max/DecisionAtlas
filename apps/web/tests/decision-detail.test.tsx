import React from "react";
import { render, screen } from "@testing-library/react";

import { DecisionCard } from "../components/decisions/decision-card";
import { SourceRefList } from "../components/decisions/source-ref-list";

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
            candidate_quality: {
              label: "partial", summary: "Grounded but based on one source ref.", source_ref_count: 1,
              previewable_source_ref_count: 1, has_primary_artifact: true,
              has_source_url: true, confidence_bucket: "high", reasons: ["previewable_quote"],
            },
            review_evidence: {
              state: "thin", source_ref_count: 1,
              source_ref_preview: [{
                id: 1, artifact_id: 1, span_start: 0, span_end: 42,
                quote: "We decided to use Redis as a cache because latency mattered.",
                url: "https://github.com/org/repo/issues/1", relevance_score: 0.88,
                current_quote_match: true,
              }],
              primary_artifact: { id: 1, type: "issue", title: "Cache decision", repo: "org/repo", url: "https://github.com/org/repo/issues/1" },
              current_quote_integrity: { status: "current_quotes_found", found_count: 1, missing_count: 0, unverifiable_count: 0 },
            },
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
                metadata: null,
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
                current_quote_match: true,
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
              current_quote_match: true,
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
});
