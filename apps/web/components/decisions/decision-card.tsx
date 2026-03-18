import React from "react";

import { DecisionDetail } from "../../lib/api";

export function DecisionCard({ decision }: { decision: DecisionDetail }) {
  return (
    <article className="card">
      <div className="card-head">
        <div>
          <p className="eyebrow">Decision Detail</p>
          <h1>{decision.title}</h1>
        </div>
        <span className="badge">{decision.review_state}</span>
      </div>
      <p><strong>Problem:</strong> {decision.problem}</p>
      <p><strong>Context:</strong> {decision.context ?? "N/A"}</p>
      <p><strong>Constraints:</strong> {decision.constraints ?? "N/A"}</p>
      <p><strong>Chosen option:</strong> {decision.chosen_option}</p>
      <p><strong>Tradeoffs:</strong> {decision.tradeoffs}</p>
      <p><strong>Confidence:</strong> {decision.confidence}</p>
    </article>
  );
}
