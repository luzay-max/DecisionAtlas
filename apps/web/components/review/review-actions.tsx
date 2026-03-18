import React from "react";

export function ReviewActions({ decisionId }: { decisionId: number }) {
  return (
    <div className="action-row" aria-label={`Review actions for decision ${decisionId}`}>
      <button type="button">Accept</button>
      <button type="button">Reject</button>
      <button type="button">Supersede</button>
    </div>
  );
}
