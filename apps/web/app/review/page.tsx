import React from "react";

import { getReviewQueue, ReviewDecision } from "../../lib/api";
import { ReviewList } from "../../components/review/review-list";

export function ReviewPageContent({ decisions }: { decisions: ReviewDecision[] }) {
  return (
    <main className="page-shell">
      <section className="panel">
        <p className="eyebrow">Review Queue</p>
        <h1>Candidate decisions waiting for review</h1>
        <ReviewList decisions={decisions} />
      </section>
    </main>
  );
}

export default async function ReviewPage() {
  const decisions = await getReviewQueue("demo-workspace");
  return <ReviewPageContent decisions={decisions} />;
}
