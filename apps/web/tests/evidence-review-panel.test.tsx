import React from "react";
import { render, screen } from "@testing-library/react";

import { EvidenceReviewPanel } from "../components/evidence/evidence-review-panel";

const goodRef = {
  id: 9,
  artifact_id: 3,
  span_start: 12,
  span_end: 38,
  quote: "The team chose a cache after measuring latency.",
  url: "https://github.com/org/repo/blob/main/README.md",
  relevance_score: 0.9,
};

describe("EvidenceReviewPanel", () => {
  it("summarizes stored metadata and clearly separates it from verification", () => {
    render(<EvidenceReviewPanel sourceRefs={[goodRef]} />);

    expect(screen.getByRole("heading", { name: "Source References" })).toBeInTheDocument();
    expect(screen.getByText("Quote present")).toBeInTheDocument();
    expect(screen.getByText("Source link available")).toBeInTheDocument();
    expect(screen.getByText("Span recorded")).toBeInTheDocument();
    expect(screen.getByText("The team chose a cache after measuring latency.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Open source/ })).toHaveAttribute("href", goodRef.url);
    expect(screen.getByText(/does not re-fetch or verify current upstream content/i)).toBeInTheDocument();
    expect(screen.getByText(/Independent human review: not recorded/i)).toBeInTheDocument();
  });

  it("flags missing quote, invalid URL and absent span without claiming evidence is verified", () => {
    render(
      <EvidenceReviewPanel
        sourceRefs={[{
          ...goodRef,
          id: 10,
          quote: " ",
          url: "javascript:alert(1)",
          span_start: null,
          span_end: null,
        }]}
      />
    );

    expect(screen.getByText("Quote missing")).toBeInTheDocument();
    expect(screen.getByText("No safe source link")).toBeInTheDocument();
    expect(screen.getByText("No span recorded")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /Open source/ })).not.toBeInTheDocument();
    expect(screen.getByText(/No quote was stored/i)).toBeInTheDocument();
  });

  it("shows the compact queue notice and source preview count", () => {
    render(<EvidenceReviewPanel sourceRefs={[goodRef]} totalSourceCount={3} compact />);

    expect(screen.getByText(/3 source references/)).toBeInTheDocument();
    expect(screen.getByText(/1 refs previewed/)).toBeInTheDocument();
    expect(screen.getByText(/quote and link previews below come from stored import metadata/i)).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /Open source/ })).not.toBeInTheDocument();
  });

  it("renders an empty state without inventing source evidence", () => {
    render(<EvidenceReviewPanel sourceRefs={[]} />);

    expect(screen.getByText("No source references are attached to this decision.")).toBeInTheDocument();
    expect(screen.getAllByText("0 / 0")).toHaveLength(3);
  });
});
