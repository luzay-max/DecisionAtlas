import React from "react";

import { ReviewDecision } from "../../lib/api";
import { ReviewActions } from "./review-actions";

export function ReviewList({ decisions }: { decisions: ReviewDecision[] }) {
  return (
    <div className="stack">
      {decisions.map((decision) => (
        <article key={decision.id} className="card">
          <div className="card-head">
            <div>
              <p className="eyebrow">Candidate Decision</p>
              <h2>{decision.title}</h2>
            </div>
            <span className="badge">{decision.review_state}</span>
          </div>
          <p><strong>Confidence:</strong> {decision.confidence.toFixed(2)}</p>
          <p><strong>Problem:</strong> {decision.problem}</p>
          <p><strong>Chosen option:</strong> {decision.chosen_option}</p>
          <p><strong>Tradeoffs:</strong> {decision.tradeoffs}</p>
          <ReviewActions decisionId={decision.id} />
        </article>
      ))}
    </div>
  );
}
