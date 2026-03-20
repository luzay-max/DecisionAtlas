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
    expect(screen.getByText("Source References")).toBeInTheDocument();
    expect(screen.getByText("We decided to use Redis as a cache because latency mattered.")).toBeInTheDocument();
  });
});
