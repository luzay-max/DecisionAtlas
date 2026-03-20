"use client";

import React, { useState } from "react";

import { useI18n } from "../i18n/language-provider";

export function ReviewActions({
  decisionId,
  onReview,
}: {
  decisionId: number;
  onReview: (reviewState: "accepted" | "rejected" | "superseded") => Promise<void>;
}) {
  const { messages } = useI18n();
  const [loadingState, setLoadingState] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleReview(reviewState: "accepted" | "rejected" | "superseded") {
    setLoadingState(reviewState);
    setError(null);
    try {
      await onReview(reviewState);
    } catch {
      setError(messages.review.actionFailed);
    } finally {
      setLoadingState(null);
    }
  }

  return (
    <div className="stack">
      <div className="action-row" aria-label={messages.review.actionsLabel.replace("{id}", String(decisionId))}>
        <button type="button" disabled={loadingState !== null} onClick={() => handleReview("accepted")}>
          {loadingState === "accepted" ? messages.review.updating : messages.review.actions.accept}
        </button>
        <button type="button" disabled={loadingState !== null} onClick={() => handleReview("rejected")}>
          {loadingState === "rejected" ? messages.review.updating : messages.review.actions.reject}
        </button>
        <button type="button" disabled={loadingState !== null} onClick={() => handleReview("superseded")}>
          {loadingState === "superseded" ? messages.review.updating : messages.review.actions.supersede}
        </button>
      </div>
      {error ? <p>{error}</p> : null}
    </div>
  );
}
