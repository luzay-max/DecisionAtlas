import React from "react";

import { ReviewDecision } from "../../lib/api";
import { DemoWorkspaceNav } from "../navigation/demo-workspace-nav";
import { ReviewList } from "./review-list";

export function ReviewPageContent({
  decisions,
  workspaceSlug,
}: {
  decisions: ReviewDecision[];
  workspaceSlug: string;
}) {
  return (
    <main className="page-shell">
      <section className="panel">
        <DemoWorkspaceNav workspaceSlug={workspaceSlug} currentPath="/review" />
        <p className="eyebrow">Review Queue</p>
        <h1>Candidate decisions waiting for review</h1>
        <p>Highest-confidence candidates appear first so the demo path stays easy to review.</p>
        <ReviewList decisions={decisions} workspaceSlug={workspaceSlug} />
      </section>
    </main>
  );
}
